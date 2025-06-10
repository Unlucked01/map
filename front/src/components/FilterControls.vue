<template>
  <div class="filter-controls">
    <div class="flex items-center gap-2 overflow-x-auto pb-2">
      <button
        v-for="type in buildingTypes"
        :key="type.key"
        @click="selectType(type.key)"
        :class="[
          'flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 whitespace-nowrap',
          selectedType === type.key
            ? 'bg-primary-600 text-white shadow-lg'
            : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
        ]"
      >
        <span :class="getTypeIcon(type.key)" class="w-4 h-4" />
        <span>{{ type.label }}</span>
        <span 
          v-if="type.count > 0"
          :class="[
            'px-2 py-0.5 rounded-full text-xs',
            selectedType === type.key
              ? 'bg-white/20 text-white'
              : 'bg-gray-100 text-gray-600'
          ]"
        >
          {{ type.count }}
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useBuildingsStore } from '@/stores/buildings'

// Store
const buildingsStore = useBuildingsStore()

// Computed
const buildingTypes = computed(() => buildingsStore.buildingTypes)
const selectedType = computed(() => buildingsStore.selectedType)

// Methods
const selectType = (type: string) => {
  buildingsStore.setSelectedType(type)
  buildingsStore.fetchBuildings()
}

const getTypeIcon = (type: string) => {
  const icons = {
    all: 'building-office',
    academic: 'academic-cap',
    living: 'home',
    sports: 'trophy',
    dining: 'cake',
    administrative: 'clipboard-document-list'
  }
  
  return `heroicon-${icons[type as keyof typeof icons] || icons.all}`
}
</script>

<style scoped>
.filter-controls {
  /* Скрываем скроллбар для горизонтального скролла */
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.filter-controls::-webkit-scrollbar {
  display: none;
}
</style> 