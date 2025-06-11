<template>
  <div class="search-container">
    <!-- Поисковая строка -->
    <div class="search-wrapper">
      <div class="search-input-group">
        <MagnifyingGlassIcon class="search-icon" />
        <input
          ref="searchInput"
          v-model="searchQuery"
          type="text"
          placeholder="Поиск зданий, аудиторий, удобств..."
          class="search-input"
          @input="handleInput"
          @focus="isInputFocused = true"
          @blur="handleBlur"
          @keydown="handleKeydown"
        />
        <button
          v-if="searchQuery"
          @click="clearSearch"
          class="clear-button"
          type="button"
        >
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Результаты поиска -->
    <Transition name="search-dropdown">
      <div v-if="showResults" class="search-results">
        <div v-if="buildingsStore.isSearching" class="search-loading">
          <div class="loading-spinner"></div>
          <span>Поиск...</span>
        </div>
        
        <div v-else-if="searchResults.length === 0 && searchQuery" class="no-results">
          <ExclamationCircleIcon class="w-5 h-5 text-gray-400" />
          <span>Ничего не найдено для "<strong>{{ searchQuery }}</strong>"</span>
        </div>
        
        <div v-else class="results-list">
          <div
            v-for="(result, index) in searchResults"
            :key="`${result.type}-${result.building?.id || result.amenity}-${index}`"
            :class="[
              'result-item',
              { 'highlighted': index === highlightedIndex }
            ]"
            @click="selectResult(result)"
            @mouseenter="highlightedIndex = index"
          >
            <!-- Иконка типа результата -->
            <div class="result-icon">
              <BuildingOfficeIcon 
                v-if="result.type === 'building'" 
                :class="getResultIconClass(result)"
              />
              <AcademicCapIcon 
                v-else-if="result.type === 'room'" 
                :class="getResultIconClass(result)"
              />
              <ArchiveBoxIcon 
                v-else 
                :class="getResultIconClass(result)"
              />
            </div>

            <!-- Информация о результате -->
            <div class="result-content">
              <div class="result-main">
                <span class="result-title">{{ getResultTitle(result) }}</span>
                <div class="result-badges">
                  <span :class="getTypeBadgeClass(result.type)">
                    {{ getTypeLabel(result.type) }}
                  </span>
                  <span v-if="result.room?.accessible" class="accessibility-badge">
                    <div class="accessibility-dot"></div>
                  </span>
                </div>
              </div>
              <div class="result-details">
                <span class="building-name">{{ result.building?.name || 'Неизвестное здание' }}</span>
                <span v-if="result.room" class="room-details">
                  {{ result.room.floor ? `${result.room.floor} этаж` : '' }}
                  {{ result.room.capacity ? `• ${result.room.capacity} мест` : '' }}
                </span>
              </div>
            </div>

            <!-- Стрелка -->
            <ChevronRightIcon class="result-arrow" />
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { 
  MagnifyingGlassIcon, 
  XMarkIcon,
  BuildingOfficeIcon,
  HomeIcon,
  AcademicCapIcon,
  ArchiveBoxIcon,
  ExclamationCircleIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'
import { useBuildingsStore } from '@/stores/buildings'
import type { Building, SearchResult } from '@/stores/buildings'

// Store
const buildingsStore = useBuildingsStore()

// Emits
const emit = defineEmits<{
  buildingSelect: [building: Building]
}>()

// Refs
const searchInput = ref<HTMLInputElement>()
const searchQuery = ref('')
const showResults = ref(false)
const searchTimeout = ref<number | null>(null)
const selectedResultIndex = ref(0)
const highlightedIndex = ref(0)
const isInputFocused = ref(false)

// Computed
const loading = computed(() => buildingsStore.loading)
const results = computed(() => buildingsStore.filteredBuildings.slice(0, 10)) // Ограничиваем до 10 результатов
const searchResults = computed(() => buildingsStore.filteredSearchResults)
const isSearching = computed(() => buildingsStore.isSearching)
const searchSuggestions = computed(() => buildingsStore.searchSuggestions)

// Methods
const handleInput = () => {
  selectedResultIndex.value = 0
  highlightedIndex.value = 0
  
  // Дебаунс для поиска
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  const query = searchQuery.value.trim()
  
  if (query.length === 0) {
    buildingsStore.clearSearchResults()
    showResults.value = false
    return
  }
  
  // Показываем результаты только если есть минимум 2 символа
  if (query.length < 2) {
    buildingsStore.clearSearchResults()
    showResults.value = false
    return
  }
  
  showResults.value = true
  
  searchTimeout.value = setTimeout(() => {
    buildingsStore.performSearchWithResults(query)
  }, 200) as unknown as number // Уменьшили дебаунс для лучшей отзывчивости
}

const clearSearch = () => {
  searchQuery.value = ''
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

const getResultIcon = (result: SearchResult) => {
  switch (result.type) {
    case 'building':
      return BuildingOfficeIcon
    case 'room':
      return AcademicCapIcon
    case 'amenity':
      return ArchiveBoxIcon
    default:
      return MagnifyingGlassIcon
  }
}

const getResultIconColor = (result: SearchResult) => {
  const colors = {
    building: 'text-blue-500',
    room: 'text-green-500',
    amenity: 'text-orange-500'
  }
  return colors[result.type] || 'text-gray-400'
}

const getResultBadgeColor = (result: SearchResult) => {
  const colors = {
    building: 'bg-blue-100 text-blue-800',
    room: 'bg-green-100 text-green-800',
    amenity: 'bg-orange-100 text-orange-800'
  }
  return colors[result.type] || 'bg-gray-100 text-gray-800'
}

const getResultTypeLabel = (result: SearchResult) => {
  const labels = {
    building: 'Здание',
    room: 'Аудитория',
    amenity: 'Услуга'
  }
  return labels[result.type] || 'Неизвестно'
}

const getAccessibilityInfo = (result: SearchResult): string | null => {
  if (result.type === 'room' && result.room) {
    return result.room.accessible ? 'Доступно для маломобильных' : null
  }
  if (result.type === 'building') {
    return result.building.accessible ? 'Доступно для маломобильных' : null
  }
  return null
}

const getAccessibilityColor = (result: SearchResult) => {
  const accessible = result.type === 'room' 
    ? result.room?.accessible 
    : result.building.accessible
  return accessible ? 'bg-green-400' : 'bg-gray-300'
}

const selectSearchResult = (result: SearchResult) => {
  emit('buildingSelect', result.building)
  if (result.type === 'room') {
    // Дополнительная логика для выбора конкретной аудитории
    console.log('Selected room:', result.room?.number)
  }
  hideResults()
}

const applySuggestion = (suggestion: string) => {
  searchQuery.value = suggestion
  handleInput()
  searchInput.value?.focus()
}

const navigateResults = (direction: number) => {
  if (searchResults.value.length === 0) return
  
  selectedResultIndex.value += direction
  if (selectedResultIndex.value < 0) {
    selectedResultIndex.value = searchResults.value.length - 1
  } else if (selectedResultIndex.value >= searchResults.value.length) {
    selectedResultIndex.value = 0
  }
}

const handleEnterSearch = () => {
  if (searchResults.value.length > 0 && selectedResultIndex.value >= 0) {
    selectSearchResult(searchResults.value[selectedResultIndex.value])
  }
}

// Обработка глобальных клавиш
const handleKeyDown = (event: KeyboardEvent) => {
  if (!showResults.value || searchResults.value.length === 0) return
  
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, searchResults.value.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0)
      break
    case 'Enter':
      event.preventDefault()
      if (highlightedIndex.value >= 0 && highlightedIndex.value < searchResults.value.length) {
        selectResult(searchResults.value[highlightedIndex.value])
      }
      break
    case 'Escape':
      event.preventDefault()
      hideResults()
      searchInput.value?.blur()
      break
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
watch(searchQuery, (newQuery) => {
  if (!newQuery) {
    buildingsStore.setSearchQuery('')
    hideResults()
  }
})

const getResultTitle = (result: SearchResult) => {
  return result.matchText || result.building?.name || result.amenity || 'Неизвестно'
}

const getResultIconClass = (result: SearchResult) => {
  const baseClasses = 'w-5 h-5'
  switch (result.type) {
    case 'building':
      return `${baseClasses} text-blue-500`
    case 'room':
      return `${baseClasses} text-green-500`
    case 'amenity':
      return `${baseClasses} text-orange-500`
    default:
      return `${baseClasses} text-gray-400`
  }
}

const getTypeBadgeClass = (type: string) => {
  return getTypeColor(type)
}

const handleBlur = () => {
  if (!searchQuery.value) {
    hideResults()
  }
}

const selectResult = (result: SearchResult) => {
  selectSearchResult(result)
}

const handleKeydown = (event: KeyboardEvent) => {
  if (!showResults.value || searchResults.value.length === 0) return
  
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, searchResults.value.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0)
      break
    case 'Enter':
      event.preventDefault()
      if (highlightedIndex.value >= 0 && highlightedIndex.value < searchResults.value.length) {
        selectResult(searchResults.value[highlightedIndex.value])
      }
      break
    case 'Escape':
      event.preventDefault()
      hideResults()
      searchInput.value?.blur()
      break
  }
}
</script>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
  max-width: 600px;
}

/* Поисковая строка с современным дизайном */
.search-wrapper {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-wrapper:hover {
  box-shadow: 0 15px 35px rgba(102, 126, 234, 0.25);
  transform: translateY(-1px);
}

.search-input-group {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  overflow: hidden;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #6366f1;
  transition: color 0.2s ease;
}

.search-input {
  width: 100%;
  padding: 16px 50px 16px 50px;
  border: none;
  background: transparent;
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
  outline: none;
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: #9ca3af;
  font-weight: 400;
}

.search-input:focus {
  color: #111827;
}

.search-input:focus + .search-icon {
  color: #4f46e5;
}

.clear-button {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(239, 68, 68, 0.1);
  border: none;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #ef4444;
}

.clear-button:hover {
  background: rgba(239, 68, 68, 0.2);
  transform: translateY(-50%) scale(1.1);
}

/* Результаты поиска с современным дизайном */
.search-results {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  max-height: 400px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  z-index: 50;
}

.search-loading {
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #6366f1;
  font-weight: 500;
}

.no-results {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #6b7280;
}

.results-list {
  padding: 8px;
  overflow-y: auto;
  max-height: 350px;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 16px;
  margin: 4px 0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.result-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.result-item:hover::before,
.result-item.highlighted::before {
  opacity: 1;
}

.result-item:hover {
  transform: translateX(4px);
}

.result-icon {
  position: relative;
  z-index: 1;
  padding: 8px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin-right: 16px;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.result-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.result-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.result-title {
  font-weight: 600;
  color: #111827;
  font-size: 16px;
}

.result-badges {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-badges span {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.result-details {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  color: #6b7280;
  font-size: 14px;
}

.building-name {
  font-weight: 500;
  color: #374151;
}

.room-details {
  font-size: 12px;
  color: #9ca3af;
}

.result-arrow {
  position: relative;
  z-index: 1;
  width: 20px;
  height: 20px;
  color: #9ca3af;
  margin-left: 16px;
  transition: all 0.2s ease;
}

.result-item:hover .result-arrow {
  color: #6366f1;
  transform: translateX(4px);
}

.accessibility-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 6px;
}

.accessibility-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

/* Анимации */
.search-dropdown-enter-active,
.search-dropdown-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-dropdown-enter-from,
.search-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-16px) scale(0.95);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(99, 102, 241, 0.2);
  border-top: 2px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Адаптивность */
@media (max-width: 640px) {
  .search-wrapper {
    padding: 1px;
  }
  
  .search-input {
    padding: 14px 45px 14px 45px;
    font-size: 16px;
  }
  
  .search-results {
    max-height: 300px;
  }
  
  .result-item {
    padding: 12px;
  }
  
  .result-title {
    font-size: 14px;
  }
}
</style> 