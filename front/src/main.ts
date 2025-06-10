import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import MapPage from './views/MapPage.vue'
import './style.css'

const routes = [
  { path: '/', name: 'map', component: MapPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const pinia = createPinia()

const app = createApp(App)
app.use(pinia)
app.use(router)
app.mount('#app') 