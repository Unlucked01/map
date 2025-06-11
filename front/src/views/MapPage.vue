<template>
  <div class="map-page h-screen flex flex-col bg-gray-50">
    <!-- Хэдер -->
    <header class="relative bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 shadow-2xl z-30">
      <!-- Декоративная обводка -->
      <div class="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-blue-700/20 backdrop-blur-sm"></div>
      <div class="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent"></div>
      
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Десктопная версия -->
        <div class="hidden md:flex items-center justify-between h-16">
          <!-- Логотип -->
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <h1 class="text-xl font-bold text-white drop-shadow-lg">ПГУ</h1>
              <p class="text-sm text-blue-100 font-medium">Интерактивная карта</p>
            </div>
          </div>

          <!-- Поиск -->
          <div class="flex-1 max-w-md mx-8">
            <SearchBar @building-select="onBuildingSelect" />
          </div>
        </div>
        
        <!-- Мобильная версия -->
        <div class="md:hidden">
          <!-- Первая строка: логотип -->
          <div class="flex items-center justify-center h-14 border-b border-white/20">
            <div class="text-center">
              <h1 class="text-lg font-bold text-white drop-shadow-lg">ПГУ</h1>
              <p class="text-xs text-blue-100 font-medium">Интерактивная карта</p>
            </div>
          </div>
          
          <!-- Вторая строка: поиск на всю ширину -->
          <div class="py-3">
            <SearchBar @building-select="onBuildingSelect" />
          </div>
        </div>
      </div>
    </header>

    <!-- Фильтры -->
    <div class="bg-white shadow-sm border-b border-gray-200 z-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <FilterControls />
      </div>
    </div>

    <!-- Основной контент -->
    <main class="flex-1 relative overflow-hidden">
      <!-- Карта -->
      <div class="absolute inset-0">
        <MapViewer
          :show-minimap="showMinimap"
          @building-click="onBuildingClick"
          ref="mapViewer"
        />
      </div>

      <!-- Боковая панель с информацией о здании (только для десктопа) -->
      <div
        v-if="selectedBuilding && !isMobile"
        class="absolute top-4 left-4 z-20 w-96 max-w-[calc(100vw-2rem)]"
      >
        <BuildingCard
          :building="selectedBuilding"
          @close="closeBuilding"
        />
      </div>

      <!-- Мобильная карточка (снизу) -->
      <div
        v-if="selectedBuilding && isMobile"
        class="absolute bottom-0 left-0 right-0 z-20 bg-white rounded-t-xl shadow-2xl transform transition-transform duration-300"
        :class="showMobileCard ? 'translate-y-0' : 'translate-y-full'"
      >
        <div class="p-4">
          <!-- Ручка для перетаскивания -->
          <div class="w-10 h-1 bg-gray-300 rounded-full mx-auto mb-4"></div>
          
          <BuildingCard
            :building="selectedBuilding"
            @close="closeBuilding"
          />
        </div>
      </div>

      <!-- Индикатор загрузки -->
      <div
        v-if="loading"
        class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-30"
      >
        <div class="bg-white rounded-lg shadow-lg p-6 flex items-center gap-4">
          <div class="loading-spinner"></div>
          <span class="text-gray-700">Загрузка данных...</span>
        </div>
      </div>

      <!-- Уведомления об ошибках -->
      <div
        v-if="error"
        class="absolute top-4 right-4 z-30 max-w-md"
      >
        <div class="bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg">
          <div class="flex">
            <ExclamationTriangleIcon class="w-5 h-5 text-red-400 flex-shrink-0" />
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Ошибка</h3>
              <p class="text-sm text-red-700 mt-1">{{ error }}</p>
            </div>
            <button
              @click="clearError"
              class="ml-auto -mx-1.5 -my-1.5 p-1.5 text-red-500 hover:text-red-700"
            >
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Мобильная навигация (если нужна) -->
    <nav
      v-if="isMobile"
      class="bg-white border-t border-gray-200 px-4 py-2 safe-area-bottom"
    >
      <div class="flex justify-center gap-6">
        <button
          @click="toggleMinimap"
          class="flex flex-col items-center gap-1 text-gray-500 hover:text-gray-700"
        >
          <MapIcon class="w-5 h-5" />
          <span class="text-xs">Миникарта</span>
        </button>
        <button
          @click="resetMapView"
          class="flex flex-col items-center gap-1 text-gray-500 hover:text-gray-700"
        >
          <HomeIcon class="w-5 h-5" />
          <span class="text-xs">Центр</span>
        </button>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  ExclamationTriangleIcon,
  XMarkIcon,
  MapIcon,
  HomeIcon
} from '@heroicons/vue/24/outline'
import { useBuildingsStore } from '@/stores/buildings'
import type { Building } from '@/stores/buildings'

// Components
import MapViewer from '@/components/MapViewer.vue'
import BuildingCard from '@/components/BuildingCard.vue'
import SearchBar from '@/components/SearchBar.vue'
import FilterControls from '@/components/FilterControls.vue'

// Store
const buildingsStore = useBuildingsStore()

// Refs
const showMinimap = ref(false)
const showMobileCard = ref(false)
const isMobile = ref(false)
const mapViewer = ref<InstanceType<typeof MapViewer> | null>(null)

// Computed
const selectedBuilding = computed(() => buildingsStore.selectedBuilding)
const loading = computed(() => buildingsStore.loading)
const error = computed(() => buildingsStore.error)

// Methods
const onBuildingClick = async (buildingId: string) => {
  // Предотвращаем двойной клик
  if (buildingsStore.loading) {
    return
  }
  
  // Если уже выбрано это здание, не делаем ничего
  if (selectedBuilding.value && selectedBuilding.value.id === buildingId) {
    return
  }
  
  await buildingsStore.fetchBuilding(buildingId)
  
  if (isMobile.value) {
    showMobileCard.value = true
  }
}

const onBuildingSelect = (building: Building) => {
  console.log('🔍 Поиск здания:', building.name, building.id)
  
  // Используем новый метод навигации к зданию с анимацией
  if (mapViewer.value) {
    mapViewer.value.navigateToBuilding(building.id)
  }
  
  // Устанавливаем выбранное здание в store для подсветки
  buildingsStore.selectBuilding(building)
  
  // На мобильных устройствах показываем карточку
  if (isMobile.value) {
    showMobileCard.value = true
  }
}

const closeBuilding = () => {
  buildingsStore.selectBuilding(null)
  showMobileCard.value = false
}

const clearError = () => {
  buildingsStore.error = null
}

const toggleMinimap = () => {
  showMinimap.value = !showMinimap.value
}

const resetMapView = () => {
  // Эмитим событие для сброса вида карты
  window.dispatchEvent(new CustomEvent('resetMapView'))
}

// Определение мобильного устройства
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const handleResize = () => {
  checkMobile()
  
  // Закрываем мобильную карточку при переходе в десктоп режим
  if (!isMobile.value) {
    showMobileCard.value = false
  }
}

// Обработка свайпов для мобильной карточки
const handleTouchStart = (event: TouchEvent) => {
  if (isMobile.value && selectedBuilding.value) {
    const startY = event.touches[0].clientY
    
    const handleTouchMove = (moveEvent: TouchEvent) => {
      const currentY = moveEvent.touches[0].clientY
      const deltaY = currentY - startY
      
      if (deltaY > 50) {
        showMobileCard.value = false
        document.removeEventListener('touchmove', handleTouchMove)
      }
    }
    
    document.addEventListener('touchmove', handleTouchMove, { passive: true })
    
    setTimeout(() => {
      document.removeEventListener('touchmove', handleTouchMove)
    }, 1000)
  }
}

// Lifecycle
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', handleResize)
  document.addEventListener('touchstart', handleTouchStart, { passive: true })
  
  // Загружаем данные
  buildingsStore.fetchBuildings()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('touchstart', handleTouchStart)
})
</script>

<style scoped>
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}

/* Анимации для мобильной карточки */
.mobile-card-enter-active,
.mobile-card-leave-active {
  transition: transform 0.3s ease-out;
}

.mobile-card-enter-from,
.mobile-card-leave-to {
  transform: translateY(100%);
}

/* Адаптивность */
@media (max-width: 768px) {
  .map-page header {
    padding: 0 1rem;
  }
  
  .map-page header h1 {
    font-size: 1.125rem;
  }
}
</style> 