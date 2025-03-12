import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Libraries from '../views/Libraries.vue'
import Favorites from '../views/Favorites.vue'
import Settings from '../views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/libraries',
    name: 'Libraries',
    component: Libraries
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: Favorites
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
