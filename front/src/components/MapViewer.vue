<template>
  <div class="map-viewer relative w-full h-full overflow-hidden bg-gray-100">
    <!-- Индикатор загрузки -->
    <div v-if="loading" class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-30">
      <div class="flex flex-col items-center gap-4">
        <div class="loading-spinner"></div>
        <p class="text-gray-600">Загрузка карты...</p>
      </div>
    </div>

    <!-- Контейнер карты -->
    <div 
      ref="mapContainer" 
      class="map-container w-full h-full cursor-grab active:cursor-grabbing"
      @wheel.prevent="handleWheel"
      @mousedown="startPan"
      @mousemove="handlePan"
      @mouseup="endPan"
      @mouseleave="endPan"
      @touchstart="startPan"
      @touchmove="handlePan"
      @touchend="endPan"
    >
      <!-- SVG карта -->
      <div 
        ref="mapContent"
        class="map-content"
        :style="{ 
          transform: `translate(${panX}px, ${panY}px) scale(${scale})`,
          transformOrigin: 'center center',
          transition: isAnimating ? 'transform 0.3s ease-out' : 'none'
        }"
      >
        <div 
          v-if="svgContent" 
          v-html="svgContent"
          class="map-svg"
          @click="handleMapClick"
        />
      </div>
    </div>

    <!-- Контролы зума -->
    <div class="absolute bottom-4 left-4 z-20 flex flex-col gap-2">
      <button 
        @click="zoomIn"
        class="bg-white hover:bg-gray-50 border border-gray-300 rounded-lg p-3 shadow-lg transition-colors"
        title="Увеличить"
      >
        <PlusIcon class="w-5 h-5 text-gray-600" />
      </button>
      <button 
        @click="zoomOut"
        class="bg-white hover:bg-gray-50 border border-gray-300 rounded-lg p-3 shadow-lg transition-colors"
        title="Уменьшить"
      >
        <MinusIcon class="w-5 h-5 text-gray-600" />
      </button>
      <button 
        @click="resetZoom"
        class="bg-white hover:bg-gray-50 border border-gray-300 rounded-lg p-3 shadow-lg transition-colors"
        title="Сбросить масштаб"
      >
        <HomeIcon class="w-5 h-5 text-gray-600" />
      </button>
    </div>

    <!-- Миникарта -->
    <div 
      v-if="showMinimap"
      class="absolute bottom-4 right-4 z-20 w-48 h-32 bg-white border border-gray-300 rounded-lg shadow-lg overflow-hidden"
    >
      <div class="h-full relative">
        <!-- Миниатюрная версия SVG -->
        <div 
          ref="minimapContainer"
          class="w-full h-full"
          style="transform-origin: top left;"
        ></div>
        
        <!-- Индикатор текущего вида -->
        <div 
          ref="viewportIndicator"
          class="absolute border-2 border-red-500 bg-red-500/20 pointer-events-none"
          style="min-width: 8px; min-height: 8px;"
        ></div>
        
        <!-- Заголовок миникарты -->
        <div class="absolute top-1 left-1 bg-black/70 text-white text-xs px-2 py-1 rounded">
          Миникарта
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { PlusIcon, MinusIcon, HomeIcon } from '@heroicons/vue/24/outline'
import { useBuildingsStore } from '@/stores/buildings'

// Props
interface Props {
  showMinimap?: boolean
  maxZoom?: number
  minZoom?: number
}

const props = withDefaults(defineProps<Props>(), {
  showMinimap: false,
  maxZoom: 5,
  minZoom: 0.1
})

// Emits
const emit = defineEmits<{
  buildingClick: [buildingId: string]
}>()

// Store
const buildingsStore = useBuildingsStore()

// Refs
const mapContainer = ref<HTMLElement | null>(null)
const mapContent = ref<HTMLElement>()
const svgContent = ref<string>('')
const loading = ref(true)
const minimapContainer = ref<HTMLElement | null>(null)
const viewportIndicator = ref<HTMLElement | null>(null)
let svgElement: SVGSVGElement | null = null
let minimapSvg: SVGSVGElement | null = null
let isMapLoaded = false

// Pan & Zoom state
const scale = ref(1)
const panX = ref(0)
const panY = ref(0)
const isPanning = ref(false)
const lastPanPoint = ref({ x: 0, y: 0 })
const isAnimating = ref(false)

// Отслеживание выбранного типа для подсветки
const selectedType = computed(() => buildingsStore.selectedType)

// Computed
const filteredBuildings = computed(() => buildingsStore.filteredBuildings)

// Загрузка SVG БЕЗ агрессивной оптимизации
const loadSVG = async () => {
  try {
    loading.value = true
    console.log('Загружаем SVG...')
    
    // Загружаем SVG файл
    const response = await fetch('/map.svg')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    let svgText = await response.text()
    console.log('SVG загружен, размер:', svgText.length)
    
    // Минимальная оптимизация - только удаляем комментарии
    svgText = svgText.replace(/<!--[\s\S]*?-->/g, '')
    
    svgContent.value = svgText
    
    await nextTick()
    setupSVGInteractions()
    
    console.log('SVG настроен')
    
  } catch (error) {
    console.error('Ошибка загрузки SVG:', error)
  } finally {
    loading.value = false
  }
}

// Настройка интерактивности SVG
const setupSVGInteractions = () => {
  const svgElement = mapContainer.value?.querySelector('svg')
  if (!svgElement) {
    console.warn('SVG элемент не найден')
    return
  }

  // Сохраняем ссылку на SVG
  (window as any).mapSvgElement = svgElement

  // Отключаем pointer-events для всех элементов по умолчанию
  svgElement.style.pointerEvents = 'all'
  const allElements = svgElement.querySelectorAll('*')
  allElements.forEach(element => {
    const htmlElement = element as HTMLElement
    if (!htmlElement.hasAttribute('data-id')) {
      htmlElement.style.pointerEvents = 'none'
    }
  })

  // Добавляем обработчики для отслеживания трансформаций
  let isDragging = false
  let lastMousePos = { x: 0, y: 0 }
  
  // Убираем дублирующий обработчик wheel - используем основной handleWheel
  
  // Обработчики mouse для пана
  svgElement.addEventListener('mousedown', (event) => {
    const target = event.target as HTMLElement
    if (event.button === 0 && target && !target.hasAttribute('data-id')) {
      isDragging = true
      lastMousePos = { x: event.clientX, y: event.clientY }
      const svgHtml = svgElement as unknown as HTMLElement
      svgHtml.style.cursor = 'grabbing'
    }
  })
  
  document.addEventListener('mousemove', (event) => {
    if (isDragging) {
      const deltaX = event.clientX - lastMousePos.x
      const deltaY = event.clientY - lastMousePos.y
      
      panX.value += deltaX
      panY.value += deltaY
      
      lastMousePos = { x: event.clientX, y: event.clientY }
      
      updateMinimap()
    }
  })
  
  document.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false
      const svgHtml = svgElement as unknown as HTMLElement
      svgHtml.style.cursor = 'default'
    }
  })

  // Находим все интерактивные элементы с data-id
  const buildings = svgElement.querySelectorAll('[data-id]')
  console.log(`Найдено ${buildings.length} интерактивных зданий`)
  
  // Создаем карту всех дочерних элементов к родительским зданиям
  const elementToBuildingMap = new Map<Element, Element>()
  
  buildings.forEach((building, index) => {
    const element = building as HTMLElement
    const buildingId = element.getAttribute('data-id')
    const buildingName = element.getAttribute('data-name')
    const buildingType = element.getAttribute('data-type')
    
    console.log(`Здание ${index + 1}:`, { id: buildingId, name: buildingName, type: buildingType, tagName: element.tagName })
    
    // Добавляем само здание в карту
    elementToBuildingMap.set(element, element)
    
    // Включаем pointer-events для зданий и поднимаем их наверх
    element.style.pointerEvents = 'all'
    element.style.cursor = 'pointer'
    element.style.transition = 'all 0.3s ease'
    
    // Поднимаем элемент наверх в DOM дереве
    element.parentElement?.appendChild(element)
    
    // Hover эффекты
    element.addEventListener('mouseenter', (event) => {
      event.stopPropagation()
      element.classList.add('highlighted')
      console.log('Hover на здание:', buildingName)
    })
    
    element.addEventListener('mouseleave', (event) => {
      event.stopPropagation()
      // Не убираем highlighted если это выбранное здание
      if (!element.classList.contains('selected')) {
        element.classList.remove('highlighted')
      }
    })
    
    // Прямой обработчик клика на здание
    element.addEventListener('click', (event) => {
      event.stopPropagation()
      event.preventDefault()
      
      // Предотвращаем множественные клики
      if (element.dataset.clicking === 'true') {
        return
      }
      
      element.dataset.clicking = 'true'
      setTimeout(() => {
        element.dataset.clicking = 'false'
      }, 300)
      
      console.log('🎯 ПРЯМОЙ КЛИК ПО ЗДАНИЮ:', { id: buildingId, name: buildingName, type: buildingType })
      
      if (buildingId) {
        // Убираем выделение с других зданий
        buildings.forEach(b => {
          b.classList.remove('selected', 'highlighted')
        })
        
        // Выделяем текущее здание
        element.classList.add('selected', 'highlighted')
        
        // Эмитим событие
        console.log('🚀 Эмитим buildingClick для:', buildingId)
        emit('buildingClick', buildingId)
      }
    })
    
    // Дополнительный обработчик для touch событий на мобильных устройствах
    element.addEventListener('touchend', (event) => {
      event.stopPropagation()
      event.preventDefault()
      
      // Предотвращаем обработку, если уже был клик
      if (element.dataset.clicking === 'true') {
        return
      }
      
      // Имитируем клик для touch устройств
      const clickEvent = new MouseEvent('click', {
        bubbles: false,
        cancelable: true,
        view: window
      })
      element.dispatchEvent(clickEvent)
    })
  })
  
  // СОЗДАЕМ ТЕКСТОВЫЕ ЭЛЕМЕНТЫ ДЛЯ НАЗВАНИЙ ЗДАНИЙ
  console.log(`Создаем текстовые элементы для названий ${buildings.length} зданий`)
  
  // Создаем группу для текста в самом конце SVG
  const textLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g')
  textLayer.setAttribute('id', 'text-layer')
  textLayer.style.pointerEvents = 'none'
  textLayer.style.isolation = 'isolate' // Изолируем от stacking context других элементов
  svgElement.appendChild(textLayer)
  
  // Создаем текстовые элементы для каждого здания
  let createdTexts = 0
  buildings.forEach((building, index) => {
    const element = building as SVGElement
    const buildingName = element.getAttribute('data-name')
    const buildingId = element.getAttribute('data-id')
    
    if (!buildingName) {
      console.warn(`Здание ${buildingId} не имеет названия`)
      return
    }
    
    // Получаем bounding box здания для позиционирования текста
    try {
      const bbox = (element as any).getBBox()
      const centerX = bbox.x + bbox.width
      const centerY = bbox.y + bbox.height / 2
      
      // Создаем текстовый элемент
      const textElement = document.createElementNS('http://www.w3.org/2000/svg', 'text')
      textElement.setAttribute('x', centerX.toString())
      textElement.setAttribute('y', centerY.toString())
      textElement.setAttribute('text-anchor', 'middle')
      textElement.setAttribute('dominant-baseline', 'middle')
      textElement.setAttribute('data-building-id', buildingId || '')
      textElement.textContent = buildingName
      
      // Применяем стили для максимальной видимости
      textElement.style.pointerEvents = 'none'
      textElement.style.userSelect = 'none'
      textElement.style.fill = '#000000'
      textElement.style.fontSize = '14px'
      textElement.style.fontWeight = '900'
      textElement.style.fontFamily = 'Arial, sans-serif'
      textElement.style.stroke = '#ffffff'
      textElement.style.strokeWidth = '3px'
      textElement.style.strokeLinejoin = 'round'
      textElement.style.paintOrder = 'stroke fill'
      textElement.style.filter = 'none'
      
      // Добавляем в текстовый слой
      textLayer.appendChild(textElement)
      createdTexts++
      
      console.log(`Создан текст ${createdTexts}: "${buildingName}" в позиции (${Math.round(centerX)}, ${Math.round(centerY)})`)
      
    } catch (error) {
      console.warn(`Не удалось получить позицию для здания ${buildingName}:`, error)
    }
  })

  console.log(`Настроено ${buildings.length} интерактивных зданий`)
  console.log(`Создано ${createdTexts} текстовых элементов для названий зданий`)
  
  // Обновляем подсветку при изменении фильтра
  updateBuildingHighlights()
  
  // Инициализируем миникарту после настройки интерактивности
  nextTick(() => {
    initMinimap()
  })
}

// Обновление подсветки зданий при фильтрации
const updateBuildingHighlights = () => {
  console.log('Обновляем подсветку зданий для типа:', selectedType.value)
  
  const svgElement = mapContainer.value?.querySelector('svg')
  if (!svgElement) {
    console.warn('SVG элемент не найден для обновления подсветки')
    return
  }

  const buildings = svgElement.querySelectorAll('[data-id]')
  console.log(`Обновляем подсветку для ${buildings.length} зданий`)
  
  buildings.forEach((building, index) => {
    const element = building as HTMLElement
    const buildingType = element.getAttribute('data-type')
    const buildingName = element.getAttribute('data-name')
    
    // Убираем предыдущие классы фильтрации
    element.classList.remove('filtered-out', 'filtered-in')
    
    if (selectedType.value === 'all') {
      // Показываем все здания
      element.classList.add('filtered-in')
      console.log(`Здание "${buildingName}" (${buildingType}) - показываем (все)`)
    } else if (buildingType === selectedType.value) {
      // Подсвечиваем здания выбранного типа
      element.classList.add('filtered-in')
      console.log(`Здание "${buildingName}" (${buildingType}) - подсвечиваем (совпадает)`)
    } else {
      // Затемняем остальные здания
      element.classList.add('filtered-out')
      console.log(`Здание "${buildingName}" (${buildingType}) - затемняем (не совпадает)`)
    }
  })
}

// Обработка клика по карте (не по зданию)
const handleMapClick = (event: Event) => {
  // Если клик был по зданию, событие уже обработано
  // Это для кликов по пустым областям карты
  console.log('Клик по карте (пустая область)')
}

// Методы зума и навигации
const zoomIn = () => {
  if (scale.value < props.maxZoom) {
    scale.value = Math.min(props.maxZoom, scale.value * 1.2)
    console.log('Zoom In:', scale.value)
  }
}

const zoomOut = () => {
  if (scale.value > props.minZoom) {
    scale.value = Math.max(props.minZoom, scale.value / 1.2)
    console.log('Zoom Out:', scale.value)
  }
}

const resetZoom = () => {
  scale.value = 1
  panX.value = 0
  panY.value = 0
  console.log('Reset Zoom')
}



// Инициализация миникарты
const initMinimap = () => {
  if (!minimapContainer.value || !svgElement) return

  // Клонируем SVG для миникарты
  minimapSvg = (svgElement as unknown as Node).cloneNode(true) as SVGSVGElement
  const minimapElement = minimapSvg as unknown as HTMLElement
  minimapElement.style.width = '100%'
  minimapElement.style.height = '100%'
  minimapElement.style.pointerEvents = 'none'
  
  // Удаляем интерактивность из миникарты
  const buildings = minimapSvg.querySelectorAll('[data-id]')
  buildings.forEach(building => {
    const element = building as HTMLElement
    element.style.cursor = 'default'
    element.classList.remove('highlighted', 'selected')
  })
  
  minimapContainer.value.innerHTML = ''
  minimapContainer.value.appendChild(minimapSvg)
  
  updateMinimap()
}

// Обновление миникарты
const updateMinimap = () => {
  if (!viewportIndicator.value || !minimapContainer.value || !mapContainer.value) return
  
  console.log('Обновляем миникарту. Зум:', scale.value, 'Пан:', { x: panX.value, y: panY.value })
  
  // Получаем размеры контейнеров
  const mapRect = mapContainer.value.getBoundingClientRect()
  const minimapRect = minimapContainer.value.getBoundingClientRect()
  
  if (!mapRect || !minimapRect) return
  
  // Вычисляем масштаб миникарты относительно основной карты
  const mapWidth = mapRect.width
  const mapHeight = mapRect.height
  const minimapWidth = minimapRect.width
  const minimapHeight = minimapRect.height
  
  // Размер индикатора viewport пропорционален зуму
  const indicatorWidth = Math.max(8, minimapWidth / scale.value)
  const indicatorHeight = Math.max(8, minimapHeight / scale.value)
  
  // Позиция индикатора обратно пропорциональна пану
  const indicatorX = Math.max(0, Math.min(minimapWidth - indicatorWidth, 
    (minimapWidth - indicatorWidth) / 2 - (panX.value / scale.value) * (minimapWidth / mapWidth)))
  const indicatorY = Math.max(0, Math.min(minimapHeight - indicatorHeight,
    (minimapHeight - indicatorHeight) / 2 - (panY.value / scale.value) * (minimapHeight / mapHeight)))
  
  // Применяем стили к индикатору
  viewportIndicator.value.style.width = `${indicatorWidth}px`
  viewportIndicator.value.style.height = `${indicatorHeight}px`
  viewportIndicator.value.style.left = `${indicatorX}px`
  viewportIndicator.value.style.top = `${indicatorY}px`
  
  console.log('Индикатор viewport:', { width: indicatorWidth, height: indicatorHeight, x: indicatorX, y: indicatorY })
}

// Throttle функция для оптимизации
const throttle = (func: Function, limit: number) => {
  let inThrottle: boolean
  return function(this: any, ...args: any[]) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// Обработка колесика мыши
const handleWheel = throttle((event: WheelEvent) => {
  const zoomFactor = event.deltaY > 0 ? 0.95 : 1.05 // Более плавное масштабирование
  const newScale = Math.max(props.minZoom, Math.min(props.maxZoom, scale.value * zoomFactor))
  
  if (newScale !== scale.value) {
    scale.value = newScale
  }
}, 16)

// Управление панорамированием
const startPan = (event: MouseEvent | TouchEvent) => {
  isPanning.value = true
  
  const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
  const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY
  
  lastPanPoint.value = { x: clientX, y: clientY }
}

const handlePan = throttle((event: MouseEvent | TouchEvent) => {
  if (!isPanning.value) return
  
  const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
  const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY
  
  const deltaX = clientX - lastPanPoint.value.x
  const deltaY = clientY - lastPanPoint.value.y
  
  panX.value += deltaX
  panY.value += deltaY
  
  lastPanPoint.value = { x: clientX, y: clientY }
}, 16)

const endPan = () => {
  isPanning.value = false
}

// Watchers для обновления подсветки при изменении фильтров
watch(selectedType, () => {
  updateBuildingHighlights()
})

// Watcher для обновления миникарты при изменении масштаба и позиции
watch([scale, panX, panY], () => {
  updateMinimap()
})

// Функция для подсветки здания при поиске
const highlightSearchedBuilding = (buildingId: string) => {
  console.log('🎯 Подсвечиваем найденное здание:', buildingId)
  
  const svgElement = mapContainer.value?.querySelector('svg')
  if (!svgElement) return
  
  const buildings = svgElement.querySelectorAll('[data-id]')
  
  // Убираем предыдущие выделения
  buildings.forEach(building => {
    building.classList.remove('search-highlighted')
  })
  
  // Находим и подсвечиваем нужное здание
  const targetBuilding = svgElement.querySelector(`[data-id="${buildingId}"]`)
  if (targetBuilding) {
    targetBuilding.classList.add('search-highlighted')
    console.log('✨ Здание подсвечено:', targetBuilding.getAttribute('data-name'))
    
    // Автоматически убираем подсветку через 5 секунд
    setTimeout(() => {
      targetBuilding.classList.remove('search-highlighted')
    }, 5000)
  } else {
    console.warn('Здание не найдено на карте:', buildingId)
  }
}

// Lifecycle
onMounted(() => {
  loadSVG()
  
  // Предотвращаем контекстное меню
  mapContainer.value?.addEventListener('contextmenu', (e) => e.preventDefault())
  
  // Слушатель для подсветки зданий при поиске
  const handleHighlightBuilding = (event: CustomEvent) => {
    highlightSearchedBuilding(event.detail.buildingId)
  }
  
  window.addEventListener('highlightBuilding', handleHighlightBuilding as EventListener)
  
  // Очистка слушателя при размонтировании
  onUnmounted(() => {
    window.removeEventListener('highlightBuilding', handleHighlightBuilding as EventListener)
  })
})

onUnmounted(() => {
  // Очистка
})
</script>

<style scoped>
.map-content {
  will-change: transform;
  backface-visibility: hidden;
  perspective: 1000px;
}

/* Стили для интерактивных зданий */
:deep(.map-svg [data-id]) {
  cursor: pointer;
  transition: all 0.3s ease;
}

:deep(.map-svg [data-id]:hover),
:deep(.map-svg [data-id].highlighted) {
  filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.8));
  stroke: #3b82f6 !important;
  stroke-width: 5 !important;
  stroke-opacity: 1 !important;
}

:deep(.map-svg [data-id].selected) {
  filter: drop-shadow(0 0 25px rgba(29, 78, 216, 1));
  stroke: #1d4ed8 !important;
  stroke-width: 6 !important;
  stroke-opacity: 1 !important;
}

:deep(.map-svg [data-id].search-highlighted) {
  filter: drop-shadow(0 0 30px rgba(255, 215, 0, 1));
  stroke: #ffd700 !important;
  stroke-width: 8 !important;
  stroke-opacity: 1 !important;
  animation: search-pulse 2s ease-in-out infinite;
}

/* Стили для фильтрации - СПЛОШНАЯ ПОДСВЕТКА */
:deep(.map-svg [data-id].filtered-in) {
  opacity: 1 !important;
  stroke-width: 6 !important;
  stroke-opacity: 1 !important;
}

:deep(.map-svg [data-id].filtered-out) {
  opacity: 0.2 !important;
  stroke: #9ca3af !important;
  stroke-width: 1 !important;
  stroke-opacity: 0.4 !important;
  filter: grayscale(0.7);
}

/* Сплошная подсветка для разных типов зданий при фильтрации */
:deep(.map-svg [data-type="academic"].filtered-in) {
  stroke: #2563eb !important;
  filter: drop-shadow(0 0 20px rgba(37, 99, 235, 0.8)) !important;
}

:deep(.map-svg [data-type="living"].filtered-in) {
  stroke: #059669 !important;
  filter: drop-shadow(0 0 20px rgba(5, 150, 105, 0.8)) !important;
}

:deep(.map-svg [data-type="sports"].filtered-in) {
  stroke: #d97706 !important;
  filter: drop-shadow(0 0 20px rgba(217, 119, 6, 0.8)) !important;
}

:deep(.map-svg [data-type="dining"].filtered-in) {
  stroke: #dc2626 !important;
  filter: drop-shadow(0 0 20px rgba(220, 38, 38, 0.8)) !important;
}

:deep(.map-svg [data-type="administrative"].filtered-in) {
  stroke: #7c3aed !important;
  filter: drop-shadow(0 0 20px rgba(124, 58, 237, 0.8)) !important;
}

/* Стили для hover разных типов зданий */
:deep(.map-svg [data-type="academic"].highlighted) {
  stroke: #3b82f6; /* blue */
  stroke-width: 4;
}

:deep(.map-svg [data-type="living"].highlighted) {
  stroke: #10b981; /* green */
  stroke-width: 4;
}

:deep(.map-svg [data-type="sports"].highlighted) {
  stroke: #f59e0b; /* orange */
  stroke-width: 4;
}

:deep(.map-svg [data-type="dining"].highlighted) {
  stroke: #ef4444; /* red */
  stroke-width: 4;
}

:deep(.map-svg [data-type="administrative"].highlighted) {
  stroke: #8b5cf6; /* purple */
  stroke-width: 4;
}

/* Оптимизация для мобильных устройств */
@media (max-width: 768px) {
  .map-viewer {
    touch-action: none;
  }
}

/* Стили для зданий */
.building {
  cursor: pointer;
  transition: outline 0.3s ease, outline-offset 0.3s ease;
}

.building.highlighted {
  outline: 4px solid #3b82f6;
  outline-offset: 2px;
}

.building.selected {
  outline: 5px solid #1d4ed8;
  outline-offset: 3px;
}

/* Специальные стили для разных типов зданий */
.building[data-type="academic"].highlighted {
  outline-color: #3b82f6;
}

.building[data-type="living"].highlighted {
  outline-color: #10b981;
}

.building[data-type="sports"].highlighted {
  outline-color: #f59e0b;
}

.building[data-type="dining"].highlighted {
  outline-color: #ef4444;
}

.building[data-type="administrative"].highlighted {
  outline-color: #8b5cf6;
}

/* Обеспечиваем максимальную видимость текста */
svg text {
  pointer-events: none !important;
  user-select: none !important;
  fill: #000000 !important;
  font-weight: 900 !important;
  font-size: 16px !important;
  font-family: Arial, sans-serif !important;
  paint-order: stroke fill !important;
  stroke: #ffffff !important;
  stroke-width: 4px !important;
  stroke-linejoin: round !important;
  stroke-linecap: round !important;
  filter: none !important;
}

/* Специальный текстовый слой всегда поверх */
:deep(.map-svg #text-layer) {
  isolation: isolate !important;
  z-index: 9999 !important;
  pointer-events: none !important;
}

:deep(.map-svg #text-layer text) {
  pointer-events: none !important;
  user-select: none !important;
  fill: #000000 !important;
  font-weight: 900 !important;
  font-size: 16px !important;
  font-family: Arial, sans-serif !important;
  paint-order: stroke fill !important;
  stroke: #ffffff !important;
  stroke-width: 4px !important;
  stroke-linejoin: round !important;
  stroke-linecap: round !important;
  filter: none !important;
    opacity: 1 !important;
}

/* Анимация для найденного здания */
@keyframes search-pulse {
  0%, 100% {
    filter: drop-shadow(0 0 30px rgba(255, 215, 0, 1));
    stroke-width: 8;
  }
  50% {
    filter: drop-shadow(0 0 40px rgba(255, 215, 0, 1));
    stroke-width: 10;
  }
}
</style> 