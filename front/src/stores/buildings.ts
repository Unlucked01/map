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

  // Computed
  const filteredBuildings = computed(() => {
    let filtered = buildings.value

    // Фильтр по типу
    if (selectedType.value !== 'all') {
      filtered = filtered.filter(building => building.type === selectedType.value)
    }

    // Поиск по названию (оптимизированный)
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase().trim()
      filtered = filtered.filter(building => 
        building.name.toLowerCase().includes(query) ||
        (building.description && building.description.toLowerCase().includes(query))
      )
    }

    return filtered
  })

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
      const response = await axios.get('http://localhost:8000/api/buildings', {
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
      const response = await axios.get(`http://localhost:8000/api/buildings/${id}`)
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
        amenities: ["Wi-Fi", "Кафе", "Банкомат", "Медпункт", "Библиотека"]
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
        description: "Корпус экономического факультета",
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
    
    // Computed
    filteredBuildings,
    buildingTypes,
    
    // Actions
    fetchBuildings,
    fetchBuilding,
    selectBuilding,
    setSearchQuery,
    setSelectedType,
    clearCache,
    debouncedSearch
  }
}) 