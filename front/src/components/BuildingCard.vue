<template>
  <div class="building-card card p-0 overflow-hidden max-w-md animate-slide-up">
    <!-- Изображение здания -->
    <div class="relative h-48 bg-gradient-to-br from-primary-500 to-primary-600 overflow-hidden">
      <img 
        v-if="building.image_url" 
        :src="building.image_url" 
        :alt="building.name"
        class="w-full h-full object-cover"
        @error="onImageError"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-white">
        <BuildingOfficeIcon class="w-16 h-16 opacity-50" />
      </div>
      
      <!-- Градиент для лучшей читаемости -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent"></div>
      
      <!-- Тип здания -->
      <div class="absolute top-4 left-4">
        <span :class="typeClasses" class="px-3 py-1 rounded-full text-sm font-medium">
          {{ typeLabel }}
        </span>
      </div>

      <!-- Кнопка закрытия -->
      <button 
        @click="$emit('close')"
        class="absolute top-4 right-4 bg-black/20 hover:bg-black/40 text-white p-2 rounded-full transition-colors"
      >
        <XMarkIcon class="w-5 h-5" />
      </button>
    </div>

    <!-- Содержимое карточки -->
    <div class="p-6">
      <!-- Заголовок -->
      <div class="mb-4">
        <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ building.name }}</h2>
        <p v-if="building.description" class="text-gray-600 leading-relaxed">
          {{ building.description }}
        </p>
      </div>

      <!-- Информация о здании -->
      <div class="space-y-3 mb-6">
        <div v-if="building.floor_count" class="flex items-center gap-3">
          <BuildingOffice2Icon class="w-5 h-5 text-gray-400" />
          <span class="text-gray-700">{{ building.floor_count }} этажей</span>
        </div>
        
        <div v-if="building.year_built" class="flex items-center gap-3">
          <CalendarIcon class="w-5 h-5 text-gray-400" />
          <span class="text-gray-700">Построено в {{ building.year_built }} году</span>
        </div>
      </div>

      <!-- Кафедры/отделы -->
      <div v-if="building.departments && building.departments.length" class="mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Кафедры и отделы</h3>
        <div class="flex flex-wrap gap-2">
          <span 
            v-for="dept in building.departments.slice(0, 3)" 
            :key="dept"
            class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
          >
            {{ dept }}
          </span>
          <span 
            v-if="building.departments.length > 3"
            class="bg-gray-100 text-gray-500 px-3 py-1 rounded-full text-sm"
          >
            +{{ building.departments.length - 3 }} еще
          </span>
        </div>
      </div>

      <!-- Удобства -->
      <div v-if="building.amenities && building.amenities.length" class="mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Удобства</h3>
        <div class="grid grid-cols-2 gap-2">
          <div 
            v-for="amenity in building.amenities.slice(0, 6)" 
            :key="amenity"
            class="flex items-center gap-2 text-sm text-gray-600"
          >
            <CheckIcon class="w-4 h-4 text-green-500" />
            {{ amenity }}
          </div>
        </div>
      </div>

      <!-- Действия -->
      <div class="flex gap-3">
        <button 
          @click="openRoute"
          class="btn-primary flex-1 flex items-center justify-center gap-2"
        >
          <MapPinIcon class="w-4 h-4" />
          Маршрут
        </button>
        <button 
          @click="shareBuilding"
          class="btn-secondary flex items-center justify-center gap-2"
        >
          <ShareIcon class="w-4 h-4" />
          Поделиться
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  BuildingOfficeIcon, 
  BuildingOffice2Icon,
  XMarkIcon, 
  CalendarIcon, 
  CheckIcon, 
  MapPinIcon, 
  ShareIcon 
} from '@heroicons/vue/24/outline'
import type { Building } from '@/stores/buildings'

// Props
interface Props {
  building: Building
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  close: []
  route: [buildingId: string]
}>()

// Computed
const typeClasses = computed(() => {
  const baseClasses = 'backdrop-blur-sm'
  
  switch (props.building.type) {
    case 'academic':
      return `${baseClasses} bg-blue-500/80 text-white`
    case 'living':
      return `${baseClasses} bg-green-500/80 text-white`
    case 'sports':
      return `${baseClasses} bg-orange-500/80 text-white`
    case 'dining':
      return `${baseClasses} bg-red-500/80 text-white`
    case 'administrative':
      return `${baseClasses} bg-purple-500/80 text-white`
    default:
      return `${baseClasses} bg-gray-500/80 text-white`
  }
})

const typeLabel = computed(() => {
  const labels = {
    academic: 'Учебное',
    living: 'Общежитие',
    sports: 'Спортивное',
    dining: 'Питание',
    administrative: 'Административное',
    other: 'Другое'
  }
  
  return labels[props.building.type] || labels.other
})

// Methods
const onImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

const openRoute = () => {
  // Координаты ПГУ (примерные)
  const psuLatitude = 58.0105
  const psuLongitude = 56.2502
  
  // Создаем URL для Яндекс.Карт с маршрутом
  const yandexMapsUrl = `https://yandex.ru/maps/?rtext=~${psuLatitude},${psuLongitude}&rtt=auto`
  
  // Создаем URL для Google Maps с маршрутом
  const googleMapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${psuLatitude},${psuLongitude}`
  
  // Определяем мобильное устройство
  const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  
  if (isMobile) {
    // На мобильных устройствах пробуем открыть нативные приложения
    if (navigator.userAgent.includes('Android')) {
      // Для Android пробуем Яндекс.Навигатор или Google Maps
      window.open(`yandexmaps://maps.yandex.ru/?rtext=~${psuLatitude},${psuLongitude}&rtt=auto`, '_blank')
      // Fallback к веб-версии
      setTimeout(() => {
        window.open(yandexMapsUrl, '_blank')
      }, 1000)
    } else if (navigator.userAgent.includes('iPhone') || navigator.userAgent.includes('iPad')) {
      // Для iOS пробуем Apple Maps или Google Maps
      window.open(`maps://maps.apple.com/?daddr=${psuLatitude},${psuLongitude}&dirflg=d`, '_blank')
      // Fallback к Google Maps
      setTimeout(() => {
        window.open(googleMapsUrl, '_blank')
      }, 1000)
    }
  } else {
    // На десктопе открываем в новой вкладке
    // Предлагаем выбор между Яндекс.Картами и Google Maps
    const choice = confirm('Открыть в Яндекс.Картах? (Отмена = Google Maps)')
    if (choice) {
      window.open(yandexMapsUrl, '_blank')
    } else {
      window.open(googleMapsUrl, '_blank')
    }
  }
  
  // Эмитим событие для аналитики
  emit('route', props.building.id)
}

const shareBuilding = async () => {
  const shareData = {
    title: `${props.building.name} - ПГУ`,
    text: `Посмотрите информацию о здании "${props.building.name}" в Пермском государственном университете`,
    url: window.location.href
  }

  try {
    // Проверяем поддержку Web Share API
    if (navigator.share && navigator.canShare(shareData)) {
      await navigator.share(shareData)
    } else {
      // Fallback - копируем ссылку в буфер обмена
      await navigator.clipboard.writeText(window.location.href)
      alert('Ссылка скопирована в буфер обмена!')
    }
  } catch (error) {
    console.error('Ошибка при попытке поделиться:', error)
    // Дополнительный fallback
    try {
      await navigator.clipboard.writeText(window.location.href)
      alert('Ссылка скопирована в буфер обмена!')
    } catch (clipboardError) {
      console.error('Ошибка копирования в буфер обмена:', clipboardError)
      alert('Не удалось поделиться. Скопируйте ссылку вручную: ' + window.location.href)
    }
  }
}
</script>

<style scoped>
.building-card {
  max-height: 80vh;
  overflow-y: auto;
}

/* Кастомная анимация появления */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 