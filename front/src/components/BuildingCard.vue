<template>
  <Transition name="card-slide">
    <div v-if="building" class="building-card">
      <!-- Заголовок с градиентом -->
      <div class="card-header">
        <div class="header-content">
          <div class="building-info">
            <h3 class="building-title">{{ building.name }}</h3>
            <div class="building-meta">
              <span :class="getTypeBadgeClass(building.type)" class="type-badge">
                {{ getTypeLabel(building.type) }}
              </span>
              <div class="accessibility-indicators">
                <div v-if="building.accessible" class="indicator accessible" title="Доступно для людей с ограниченными возможностями">
                  <UserIcon class="w-4 h-4" />
                </div>
                <div v-if="building.has_elevator" class="indicator elevator" title="Есть лифт">
                  <ArrowUpIcon class="w-4 h-4" />
                </div>
                <div v-if="building.has_parking" class="indicator parking" title="Есть парковка">
                  <TruckIcon class="w-4 h-4" />
                </div>
              </div>
            </div>
          </div>
        </div>
        <button @click="closeCard" class="close-button">
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <!-- Содержимое карточки -->
      <div class="card-content">
        <!-- Изображение здания -->
        <div v-if="building.image_url" class="building-image">
          <img :src="building.image_url" :alt="building.name" />
          <div class="image-overlay"></div>
        </div>

        <!-- Описание -->
        <div v-if="building.description" class="building-description">
          <p>{{ building.description }}</p>
        </div>

        <!-- Информация о комнатах -->
        <div v-if="building.rooms && building.rooms.length > 0" class="rooms-section">
          <h4 class="section-title">
            <HomeIcon class="w-5 h-5" />
            Помещения ({{ building.rooms.length }})
          </h4>
          <div class="rooms-grid">
            <div 
              v-for="room in building.rooms.slice(0, 6)" 
              :key="room.number"
              class="room-card"
            >
              <div class="room-header">
                <span class="room-number">{{ room.number }}</span>
                <span :class="getRoomTypeBadge(room.type)" class="room-type">
                  {{ getRoomTypeLabel(room.type) }}
                </span>
              </div>
              <div class="room-details">
                <span v-if="room.floor" class="detail">{{ room.floor }} этаж</span>
                <span v-if="room.capacity" class="detail">{{ room.capacity }} мест</span>
                <div v-if="room.accessible" class="accessibility-dot" title="Доступно"></div>
              </div>
            </div>
          </div>
          <button 
            v-if="building.rooms.length > 6" 
            class="show-more-button"
            @click="showAllRooms = !showAllRooms"
          >
            {{ showAllRooms ? 'Скрыть' : `Показать еще ${building.rooms.length - 6}` }}
          </button>
        </div>

        <!-- Дополнительная информация -->
        <div class="building-stats">
          <div class="stat-item">
            <BuildingOfficeIcon class="w-5 h-5" />
            <span>{{ building.floors || 1 }} {{ pluralize(building.floors || 1, 'этаж', 'этажа', 'этажей') }}</span>
          </div>
          <div v-if="building.total_capacity" class="stat-item">
            <UsersIcon class="w-5 h-5" />
            <span>{{ building.total_capacity }} мест</span>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  XMarkIcon,
  HomeIcon,
  BuildingOfficeIcon,
  UsersIcon,
  UserIcon,
  ArrowUpIcon,
  TruckIcon
} from '@heroicons/vue/24/outline'
import type { Building } from '@/stores/buildings'

interface Props {
  building: Building | null
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const showAllRooms = ref(false)

const closeCard = () => {
  emit('close')
}

const getTypeBadgeClass = (type: string) => {
  const classes = {
    'academic': 'bg-blue-100 text-blue-800 border-blue-200',
    'living': 'bg-green-100 text-green-800 border-green-200',
    'sports': 'bg-orange-100 text-orange-800 border-orange-200',
    'dining': 'bg-red-100 text-red-800 border-red-200',
    'administrative': 'bg-purple-100 text-purple-800 border-purple-200',
    'other': 'bg-gray-100 text-gray-800 border-gray-200'
  }
  return classes[type as keyof typeof classes] || classes.other
}

const getTypeLabel = (type: string) => {
  const labels = {
    'academic': 'Учебный',
    'living': 'Жилой',
    'sports': 'Спортивный',
    'dining': 'Столовая',
    'administrative': 'Административный',
    'other': 'Другое'
  }
  return labels[type as keyof typeof labels] || 'Неизвестно'
}

const getRoomTypeBadge = (type: string) => {
  const classes = {
    'classroom': 'bg-blue-50 text-blue-700',
    'lab': 'bg-purple-50 text-purple-700',
    'office': 'bg-gray-50 text-gray-700',
    'toilet': 'bg-cyan-50 text-cyan-700',
    'cafe': 'bg-orange-50 text-orange-700',
    'library': 'bg-green-50 text-green-700',
    'auditorium': 'bg-red-50 text-red-700',
    'other': 'bg-gray-50 text-gray-700'
  }
  return classes[type as keyof typeof classes] || classes.other
}

const getRoomTypeLabel = (type: string) => {
  const labels = {
    'classroom': 'Аудитория',
    'lab': 'Лаборатория',
    'office': 'Офис',
    'toilet': 'Туалет',
    'cafe': 'Кафе',
    'library': 'Библиотека',
    'auditorium': 'Актовый зал',
    'other': 'Другое'
  }
  return labels[type as keyof typeof labels] || 'Неизвестно'
}

const pluralize = (count: number, one: string, few: string, many: string) => {
  if (count % 10 === 1 && count % 100 !== 11) return one
  if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) return few
  return many
}
</script>

<style scoped>
.building-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  max-width: 400px;
  max-height: 80vh;
  overflow-y: auto;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-content {
  flex: 1;
}

.building-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
  line-height: 1.2;
}

.building-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.type-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.accessibility-indicators {
  display: flex;
  gap: 8px;
}

.indicator {
  padding: 6px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  transition: all 0.2s ease;
}

.indicator:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.close-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 12px;
  padding: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.card-content {
  padding: 24px;
}

.building-image {
  position: relative;
  margin-bottom: 20px;
  border-radius: 16px;
  overflow: hidden;
}

.building-image img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.3) 100%);
}

.building-description {
  margin-bottom: 24px;
  padding: 16px;
  background: rgba(99, 102, 241, 0.05);
  border-radius: 12px;
  border-left: 4px solid #6366f1;
}

.building-description p {
  color: #374151;
  line-height: 1.6;
  margin: 0;
}

.rooms-section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 16px;
}

.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.room-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  padding: 12px;
  transition: all 0.2s ease;
}

.room-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.room-number {
  font-weight: 600;
  color: #111827;
  font-size: 16px;
}

.room-type {
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
}

.room-details {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
}

.detail {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
}

.accessibility-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

.show-more-button {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 12px;
  color: #6366f1;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.show-more-button:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
  transform: translateY(-1px);
}

.building-stats {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #374151;
  font-weight: 500;
}

.stat-item svg {
  color: #6366f1;
}

/* Анимации */
.card-slide-enter-active,
.card-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-slide-enter-from {
  opacity: 0;
  transform: translateX(100px) scale(0.9);
}

.card-slide-leave-to {
  opacity: 0;
  transform: translateX(100px) scale(0.9);
}

/* Адаптивность */
@media (max-width: 640px) {
  .building-card {
    max-width: 100%;
    border-radius: 20px 20px 0 0;
  }
  
  .card-header {
    padding: 20px;
  }
  
  .building-title {
    font-size: 20px;
  }
  
  .card-content {
    padding: 20px;
  }
  
  .rooms-grid {
    grid-template-columns: 1fr;
  }
}
</style> 