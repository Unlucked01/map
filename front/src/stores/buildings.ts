import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export interface Building {
  id: string
  name: string
  type: 'academic' | 'living' | 'sports' | 'dining' | 'administrative' | 'other'
  description?: string
  image_url?: string
  coordinates?: { x: number; y: number }
  floor_count?: number
  year_built?: number
  departments?: string[]
  amenities?: string[]
  rooms?: Room[]
  accessible?: boolean
  has_elevator?: boolean
  has_parking?: boolean
}

export interface Room {
  number: string
  floor: number
  type: 'classroom' | 'lab' | 'office' | 'toilet' | 'cafe' | 'library' | 'auditorium' | 'other'
  capacity?: number
  equipment?: string[]
  accessible?: boolean
}

export interface SearchResult {
  type: 'building' | 'room' | 'amenity'
  building: Building
  room?: Room
  amenity?: string
  matchText: string
  priority: number
}

export const useBuildingsStore = defineStore('buildings', () => {
  // State
  const buildings = ref<Building[]>([])
  const selectedBuilding = ref<Building | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')
  const selectedType = ref<string>('all')
  
  // Cache для оптимизации
  const buildingsCache = new Map<string, Building>()
  const lastFetchTime = ref<number>(0)
  const CACHE_DURATION = 5 * 60 * 1000 // 5 минут

  // State для результатов поиска
  const searchResults = ref<SearchResult[]>([])
  const isSearching = ref(false)
  
  // Подсказки для поиска
  const searchSuggestions = computed(() => [
    'столовая', 'библиотека', 'аудитория 101', 'туалет', 'кафе', 'спортзал'
  ])

  // Метод для загрузки подсказок с сервера
  const loadSearchSuggestions = async () => {
    try {
      const response = await axios.get('/api/suggestions')
      return response.data
    } catch (error) {
      console.error('Ошибка загрузки подсказок:', error)
      return [
        'столовая', 'библиотека', 'аудитория 101', 'туалет', 
        'кафе', 'спортзал', 'главный корпус', 'общежитие'
      ]
    }
  }

  // Computed
  const filteredSearchResults = computed(() => searchResults.value)
  
  const filteredBuildings = computed(() => {
    let filtered = buildings.value

    // Фильтр по типу
    if (selectedType.value !== 'all') {
      filtered = filtered.filter(building => building.type === selectedType.value)
    }

    // Простой поиск по названию (для обратной совместимости)
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase().trim()
      filtered = filtered.filter(building => 
        building.name.toLowerCase().includes(query) ||
        (building.description && building.description.toLowerCase().includes(query))
      )
    }

    return filtered
  })

  // Улучшенный поиск с поддержкой аудиторий
  const performAdvancedSearch = (query: string): SearchResult[] => {
    if (!query.trim()) return []
    
    const results: SearchResult[] = []
    const searchTerm = query.toLowerCase().trim()
    
    buildings.value.forEach(building => {
      // Поиск по названию здания
      if (building.name.toLowerCase().includes(searchTerm)) {
        results.push({
          type: 'building',
          building,
          matchText: building.name,
          priority: 1
        })
      }
      
      // Поиск по описанию здания
      if (building.description?.toLowerCase().includes(searchTerm)) {
        results.push({
          type: 'building',
          building,
          matchText: building.description,
          priority: 2
        })
      }
      
      // Поиск по аудиториям
      if (building.rooms) {
        building.rooms.forEach(room => {
          if (room.number.toLowerCase().includes(searchTerm)) {
            results.push({
              type: 'room',
              building,
              room,
              matchText: `Аудитория ${room.number}`,
              priority: 1
            })
          }
        })
      }
      
      // Поиск по удобствам/услугам
      if (building.amenities) {
        building.amenities.forEach(amenity => {
          if (amenity.toLowerCase().includes(searchTerm)) {
            results.push({
              type: 'amenity',
              building,
              amenity,
              matchText: amenity,
              priority: 3
            })
          }
        })
      }
    })
    
    // Сортировка по приоритету и релевантности
    return results.sort((a, b) => {
      if (a.priority !== b.priority) return a.priority - b.priority
      return a.matchText.localeCompare(b.matchText)
    }).slice(0, 10) // Ограничиваем до 10 результатов
  }

  const buildingTypes = computed(() => [
    { key: 'all', label: 'Все здания', count: buildings.value.length },
    { key: 'academic', label: 'Учебные', count: buildings.value.filter(b => b.type === 'academic').length },
    { key: 'living', label: 'Общежития', count: buildings.value.filter(b => b.type === 'living').length },
    { key: 'sports', label: 'Спортивные', count: buildings.value.filter(b => b.type === 'sports').length },
    { key: 'dining', label: 'Питание', count: buildings.value.filter(b => b.type === 'dining').length },
    { key: 'administrative', label: 'Административные', count: buildings.value.filter(b => b.type === 'administrative').length }
  ])

  // Actions
  const fetchBuildings = async (force = false) => {
    const now = Date.now()
    
    // Проверка кэша
    if (!force && buildings.value.length > 0 && (now - lastFetchTime.value) < CACHE_DURATION) {
      console.log('Используем кэшированные данные зданий')
      return
    }

    loading.value = true
    error.value = null
    console.log('Загружаем здания с сервера...')

    try {
      const response = await axios.get('/api/buildings', {
        params: {
          query: searchQuery.value || undefined,
          type: selectedType.value !== 'all' ? selectedType.value : undefined
        }
      })

      buildings.value = response.data
      lastFetchTime.value = now

      // Обновление кэша
      response.data.forEach((building: Building) => {
        buildingsCache.set(building.id, building)
      })

      console.log(`Загружено ${buildings.value.length} зданий`)

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Ошибка загрузки зданий'
      console.error('Error fetching buildings:', err)
      
      // Fallback данные если сервер не доступен
      if (!buildings.value.length) {
        buildings.value = getFallbackBuildings()
        console.log('Используем fallback данные')
      }
    } finally {
      loading.value = false
    }
  }

  const fetchBuilding = async (id: string) => {
    console.log('Загружаем здание:', id)
    
    // Проверка кэша
    if (buildingsCache.has(id)) {
      selectedBuilding.value = buildingsCache.get(id)!
      console.log('Здание найдено в кэше:', selectedBuilding.value?.name)
      return
    }

    // Проверяем в текущем списке
    const existingBuilding = buildings.value.find(b => b.id === id)
    if (existingBuilding) {
      selectedBuilding.value = existingBuilding
      buildingsCache.set(id, existingBuilding)
      console.log('Здание найдено в списке:', selectedBuilding.value?.name)
      return
    }

    loading.value = true
    error.value = null

    try {
      const response = await axios.get(`/api/buildings/${id}`)
      selectedBuilding.value = response.data
      
      // Обновление кэша
      buildingsCache.set(id, response.data)
      console.log('Здание загружено с сервера:', selectedBuilding.value?.name)

    } catch (err: any) {
      error.value = err.response?.data?.message || 'Ошибка загрузки информации о здании'
      console.error('Error fetching building:', err)
      
      // Fallback - ищем в fallback данных
      const fallbackBuilding = getFallbackBuildings().find(b => b.id === id)
      if (fallbackBuilding) {
        selectedBuilding.value = fallbackBuilding
        console.log('Используем fallback данные для здания:', fallbackBuilding.name)
      }
    } finally {
      loading.value = false
    }
  }

  const selectBuilding = (building: Building | null) => {
    selectedBuilding.value = building
    if (building) {
      console.log('Выбрано здание:', building.name)
    }
  }

  const setSearchQuery = (query: string) => {
    searchQuery.value = query
    console.log('Поиск:', query)
  }

  const setSelectedType = (type: string) => {
    selectedType.value = type
    console.log('Выбран тип:', type)
  }

  // Новые методы для расширенного поиска
  const performSearchWithResults = async (query: string) => {
    if (!query.trim()) {
      clearSearchResults()
      return
    }

    isSearching.value = true
    
    try {
      // Убеждаемся что данные загружены
      if (buildings.value.length === 0) {
        console.log('Загружаем здания для поиска...')
        await fetchBuildings()
      }
      
      // Используем локальный поиск как основной
      const localResults = performAdvancedSearch(query)
      searchResults.value = localResults
      
      console.log(`Найдено ${localResults.length} результатов для запроса "${query}"`)
      
      // Попытка получить дополнительные результаты с сервера (если доступен)
      try {
        const response = await axios.get(`/api/search?q=${encodeURIComponent(query)}&limit=10`, {
          timeout: 2000 // 2 секунды таймаут
        })
        
        if (response.data?.results && Array.isArray(response.data.results)) {
          // Объединяем результаты, избегая дублирования
          const serverResults = response.data.results
          const combinedResults = [...localResults]
          
          serverResults.forEach((serverResult: SearchResult) => {
            const exists = combinedResults.some(local => 
              local.building.id === serverResult.building.id && 
              local.type === serverResult.type
            )
            if (!exists) {
              combinedResults.push(serverResult)
            }
          })
          
          searchResults.value = combinedResults.slice(0, 10)
        }
      } catch (serverError) {
        console.log('Сервер поиска недоступен, используем локальный поиск:', serverError)
      }
      
    } catch (error) {
      console.error('Ошибка поиска:', error)
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }

  const clearSearchResults = () => {
    searchResults.value = []
    isSearching.value = false
  }

  const clearCache = () => {
    buildingsCache.clear()
    lastFetchTime.value = 0
    console.log('Кэш очищен')
  }

  // Дебаунс для поиска
  let searchTimeout: ReturnType<typeof setTimeout> | null = null
  const debouncedSearch = (query: string, delay = 300) => {
    if (searchTimeout) clearTimeout(searchTimeout)
    
    searchTimeout = setTimeout(() => {
      setSearchQuery(query)
      fetchBuildings()
    }, delay)
  }

  // Fallback данные на случай если сервер недоступен
  const getFallbackBuildings = (): Building[] => {
    return [
      {
        id: "1",
        name: "Главный корпус",
        type: "academic",
        description: "Главный учебный корпус университета с административными службами",
        floor_count: 4,
        year_built: 1916,
        departments: ["Ректорат", "Приемная комиссия", "Деканаты"],
        amenities: ["Wi-Fi", "Кафе", "Банкомат", "Медпункт", "Библиотека"],
        accessible: true,
        has_elevator: true,
        has_parking: true,
        rooms: [
          { number: "101", floor: 1, type: "office", capacity: 10, equipment: ["Компьютер", "Проектор"], accessible: true },
          { number: "102", floor: 1, type: "classroom", capacity: 30, equipment: ["Доска", "Проектор"], accessible: true },
          { number: "103", floor: 1, type: "toilet", accessible: true },
          { number: "201", floor: 2, type: "auditorium", capacity: 100, equipment: ["Микрофоны", "Проектор", "Звуковая система"], accessible: false },
          { number: "202", floor: 2, type: "library", capacity: 50, equipment: ["Wi-Fi", "Компьютеры"], accessible: true }
        ]
      },
      {
        id: "3",
        name: "Корпус 3", 
        type: "academic",
        description: "Учебный корпус с аудиториями и лабораториями",
        floor_count: 4,
        year_built: 1975,
        departments: ["Физический факультет", "Математический факультет"],
        amenities: ["Лаборатории", "Компьютерные классы", "Wi-Fi"]
      },
      {
        id: "4",
        name: "Корпус 4",
        type: "academic", 
        description: "Современный учебный корпус",
        floor_count: 5,
        year_built: 1985,
        departments: ["Химический факультет", "Биологический факультет"],
        amenities: ["Лаборатории", "Аудитории", "Библиотека"]
      },
      {
        id: "6",
        name: "Корпус 6",
        type: "academic",
        description: "Гуманитарный корпус",
        floor_count: 3,
        year_built: 1980,
        departments: ["Филологический факультет", "Исторический факультет"],
        amenities: ["Аудитории", "Конференц-залы", "Wi-Fi"]
      },
      {
        id: "7",
        name: "Корпус 7",
        type: "academic",
        description: "Корпус факультета вычислительной техники",
        floor_count: 4,
        year_built: 1990,
        departments: ["Экономический факультет", "Юридический факультет"],
        amenities: ["Аудитории", "Компьютерные классы", "Мультимедиа"]
      },
      {
        id: "8", 
        name: "Корпус 8",
        type: "academic",
        description: "Новый учебный корпус",
        floor_count: 6,
        year_built: 2005,
        departments: ["IT факультет", "Инженерный факультет"],
        amenities: ["Современные аудитории", "IT лаборатории", "Коворкинг"]
      },
      {
        id: "О-1",
        name: "Общежитие №1",
        type: "living",
        description: "Студенческое общежитие для первокурсников",
        floor_count: 9,
        year_built: 1970,
        amenities: ["Прачечная", "Кухня", "Комната отдыха", "Интернет", "Охрана"]
      },
      {
        id: "О-2",
        name: "Общежитие №2", 
        type: "living",
        description: "Общежитие для студентов старших курсов",
        floor_count: 9,
        year_built: 1975,
        amenities: ["Прачечная", "Кухня", "Спортзал", "Интернет"]
      },
      {
        id: "О-4",
        name: "Общежитие №4",
        type: "living", 
        description: "Общежитие семейного типа",
        floor_count: 5,
        year_built: 1985,
        amenities: ["Детская площадка", "Прачечная", "Кухня", "Парковка"]
      },
      {
        id: "О-5",
        name: "Общежитие №5",
        type: "living",
        description: "Современное общежитие",
        floor_count: 12,
        year_built: 2000,
        amenities: ["Фитнес-зал", "Кафе", "Прачечная", "Wi-Fi", "Лифты"]
      },
      {
        id: "C",
        name: "Стадион",
        type: "sports", 
        description: "Университетский стадион для занятий спортом",
        floor_count: 1,
        year_built: 1965,
        amenities: ["Футбольное поле", "Беговые дорожки", "Трибуны", "Раздевалки"]
      },
      {
        id: "СК",
        name: "Спорт Кафедра",
        type: "academic",
        description: "Кафедра физической культуры и спорта",
        floor_count: 2,
        year_built: 1980,
        departments: ["Кафедра физической культуры"],
        amenities: ["Спортзалы", "Тренажеры", "Медкабинет"]
      },
      {
        id: "D",
        name: "Столовая",
        type: "dining",
        description: "Главная столовая университета",
        floor_count: 2,
        year_built: 1960,
        amenities: ["Горячее питание", "Буфет", "Кафе", "Летняя терраса"]
      }
    ]
  }

  return {
    // State
    buildings,
    selectedBuilding,
    loading,
    error,
    searchQuery,
    selectedType,
    searchResults,
    isSearching,
    
    // Computed
    filteredBuildings,
    filteredSearchResults,
    buildingTypes,
    searchSuggestions,
    
    // Actions
    fetchBuildings,
    fetchBuilding,
    selectBuilding,
    setSearchQuery,
    setSelectedType,
    clearCache,
    debouncedSearch,
    performSearchWithResults,
    clearSearchResults,
    performAdvancedSearch,
    loadSearchSuggestions
  }
}) 