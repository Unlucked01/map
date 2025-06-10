<template>
  <div class="search-bar relative">
    <div class="relative">
      <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
      <input
        ref="searchInput"
        v-model="localQuery"
        type="text"
        placeholder="Поиск зданий..."
        class="input-field pl-10 pr-10"
        @input="handleInput"
        @keydown.escape="clearSearch"
      />
      <button
        v-if="localQuery"
        @click="clearSearch"
        class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
      >
        <XMarkIcon class="w-5 h-5" />
      </button>
    </div>

    <!-- Результаты поиска -->
    <div
      v-if="showResults && (results.length > 0 || loading)"
      class="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-80 overflow-y-auto"
    >
      <!-- Индикатор загрузки -->
      <div v-if="loading" class="p-4 flex items-center justify-center">
        <div class="loading-spinner"></div>
        <span class="ml-2 text-gray-600">Поиск...</span>
      </div>

      <!-- Результаты -->
      <div v-else-if="results.length > 0" class="py-2">
        <button
          v-for="building in results"
          :key="building.id"
          @click="selectBuilding(building)"
          class="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0"
        >
          <div class="flex items-center gap-3">
            <div class="flex-shrink-0">
              <div :class="getTypeColor(building.type)" class="w-3 h-3 rounded-full"></div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900 truncate">{{ building.name }}</p>
              <p class="text-sm text-gray-500">{{ getTypeLabel(building.type) }}</p>
            </div>
          </div>
        </button>
      </div>

      <!-- Пустой результат -->
      <div v-else class="p-4 text-center text-gray-500">
        <MagnifyingGlassIcon class="w-8 h-8 mx-auto mb-2 text-gray-300" />
        <p>Ничего не найдено</p>
        <p class="text-sm">Попробуйте изменить запрос</p>
      </div>
    </div>

    <!-- Overlay для закрытия результатов -->
    <div
      v-if="showResults"
      @click="hideResults"
      class="fixed inset-0 z-40"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useBuildingsStore } from '@/stores/buildings'
import type { Building } from '@/stores/buildings'

// Store
const buildingsStore = useBuildingsStore()

// Emits
const emit = defineEmits<{
  buildingSelect: [building: Building]
}>()

// Refs
const searchInput = ref<HTMLInputElement>()
const localQuery = ref('')
const showResults = ref(false)
const searchTimeout = ref<number | null>(null)

// Computed
const loading = computed(() => buildingsStore.loading)
const results = computed(() => buildingsStore.filteredBuildings.slice(0, 10)) // Ограничиваем до 10 результатов

// Methods
const handleInput = () => {
  showResults.value = true
  
  // Дебаунс для поиска
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  searchTimeout.value = setTimeout(() => {
    buildingsStore.debouncedSearch(localQuery.value)
  }, 300) as unknown as number
}

const clearSearch = () => {
  localQuery.value = ''
  buildingsStore.setSearchQuery('')
  hideResults()
  searchInput.value?.focus()
}

const selectBuilding = (building: Building) => {
  emit('buildingSelect', building)
  hideResults()
}

const hideResults = () => {
  showResults.value = false
}

const getTypeColor = (type: string) => {
  const colors = {
    academic: 'bg-blue-500',
    living: 'bg-green-500',
    sports: 'bg-orange-500',
    dining: 'bg-red-500',
    administrative: 'bg-purple-500',
    other: 'bg-gray-500'
  }
  
  return colors[type as keyof typeof colors] || colors.other
}

const getTypeLabel = (type: string) => {
  const labels = {
    academic: 'Учебное здание',
    living: 'Общежитие',
    sports: 'Спортивное сооружение',
    dining: 'Столовая/Кафе',
    administrative: 'Административное здание',
    other: 'Другое'
  }
  
  return labels[type as keyof typeof labels] || labels.other
}

// Обработка клавиш
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.ctrlKey && event.key === 'k') {
    event.preventDefault()
    searchInput.value?.focus()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
  buildingsStore.fetchBuildings()
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
})

// Watchers
watch(localQuery, (newQuery) => {
  if (!newQuery) {
    buildingsStore.setSearchQuery('')
    hideResults()
  }
})
</script>

<style scoped>
.search-bar {
  position: relative;
  width: 100%;
  max-width: 400px;
}

/* Анимация для результатов поиска */
.search-results-enter-active,
.search-results-leave-active {
  transition: all 0.2s ease;
}

.search-results-enter-from,
.search-results-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style> 