<template>
  <div class="min-h-screen bg-gray-900 text-gray-100">
    <nav class="fixed top-0 left-0 h-screen w-16 bg-gray-800 flex flex-col items-center py-4 space-y-4">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="p-2 rounded-lg hover:bg-gray-700 transition-colors"
        :class="{ 'bg-gray-700': currentRoute === item.path }"
      >
        <component :is="item.icon" class="w-6 h-6" />
      </router-link>
    </nav>

    <div class="ml-16">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  HomeIcon,
  FolderIcon,
  StarIcon,
  Cog6ToothIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const currentRoute = computed(() => route.path)

const navItems = [
  { path: '/', icon: HomeIcon },
  { path: '/libraries', icon: FolderIcon },
  { path: '/favorites', icon: StarIcon },
  { path: '/settings', icon: Cog6ToothIcon }
]
</script>
