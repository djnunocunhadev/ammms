<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold mb-8">Settings</h1>

    <div class="max-w-3xl bg-gray-800 rounded-lg p-6">
      <h2 class="text-xl font-semibold mb-6">API Keys</h2>

      <form @submit.prevent="saveApiKeys" class="space-y-6">
        <div v-for="(value, key) in apiKeys" :key="key" class="space-y-2">
          <label :for="key" class="block text-sm font-medium text-gray-300">
            {{ formatKeyName(key) }}
          </label>
          <input
            :id="key"
            v-model="apiKeys[key]"
            type="password"
            class="w-full px-4 py-2 rounded-md bg-gray-700 border border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div class="flex justify-end space-x-4">
          <button
            type="button"
            @click="resetForm"
            class="px-4 py-2 rounded-md bg-gray-700 hover:bg-gray-600 transition-colors"
          >
            Reset
          </button>
          <button
            type="submit"
            class="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-500 transition-colors"
          >
            Save Changes
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const apiKeys = ref({
  acoustid: '',
  musicbrainz_app_name: '',
  discogs_token: '',
  beatport_client_id: '',
  beatport_client_secret: '',
  lastfm_api_key: '',
  lastfm_api_secret: ''
})

const originalKeys = ref({})

onMounted(async () => {
  try {
    const response = await axios.get('/api/v1/settings/api-keys')
    apiKeys.value = response.data
    originalKeys.value = { ...response.data }
  } catch (error) {
    console.error('Failed to load API keys:', error)
  }
})

const saveApiKeys = async () => {
  try {
    await axios.put('/api/v1/settings/api-keys', apiKeys.value)
    originalKeys.value = { ...apiKeys.value }
  } catch (error) {
    console.error('Failed to save API keys:', error)
  }
}

const resetForm = () => {
  apiKeys.value = { ...originalKeys.value }
}

const formatKeyName = (key) => {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
</script>
