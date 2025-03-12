&lt;template&gt;
  &lt;div class="flex flex-col h-screen"&gt;
    &lt;!-- Transport controls --&gt;
    &lt;TransportControls
      :is-playing="isPlaying"
      :current-time="currentTime"
      :duration="duration"
      :volume="volume"
      :loop="loop"
      :is-recording="isRecording"
      :compare-mode="compareMode"
      @play="play"
      @pause="pause"
      @stop="stop"
      @loop="setLoop"
      @volume-change="setVolume"
      @record="toggleRecord"
      @compare-mode="setCompareMode"
      @settings="showSettings = true"
    /&gt;

    &lt;div class="flex flex-1 overflow-hidden"&gt;
      &lt;!-- Side panel (file browser/metadata) --&gt;
      &lt;div class="w-64 bg-gray-800 border-r border-gray-700 flex flex-col"&gt;
        &lt;!-- Tab navigation --&gt;
        &lt;div class="flex border-b border-gray-700"&gt;
          &lt;button
            v-for="tab in ['Files', 'Metadata']"
            :key="tab"
            @click="activeTab = tab"
            class="flex-1 px-4 py-2 text-sm font-medium"
            :class="{
              'text-blue-500 border-b-2 border-blue-500': activeTab === tab,
              'text-gray-400 hover:text-gray-300': activeTab !== tab
            }"
          &gt;
            {{ tab }}
          &lt;/button&gt;
        &lt;/div&gt;

        &lt;!-- Tab content --&gt;
        &lt;div class="flex-1 overflow-y-auto"&gt;
          &lt;!-- Files tab --&gt;
          &lt;div v-if="activeTab === 'Files'" class="p-4 space-y-2"&gt;
            &lt;div
              v-for="file in audioFiles"
              :key="file.id"
              @click="selectFile(file)"
              class="p-2 rounded cursor-pointer hover:bg-gray-700"
              :class="{ 'bg-gray-700': selectedFile?.id === file.id }"
            &gt;
              &lt;div class="font-medium truncate"&gt;{{ file.filename }}&lt;/div&gt;
              &lt;div class="text-sm text-gray-400"&gt;
                {{ formatDuration(file.duration) }}
              &lt;/div&gt;
            &lt;/div&gt;
          &lt;/div&gt;

          &lt;!-- Metadata tab --&gt;
          &lt;div v-else-if="activeTab === 'Metadata'" class="p-4 space-y-4"&gt;
            &lt;template v-if="selectedFile"&gt;
              &lt;div v-for="(value, key) in selectedFile.metadata" :key="key"&gt;
                &lt;div class="text-sm text-gray-400"&gt;{{ formatKey(key) }}&lt;/div&gt;
                &lt;div class="font-medium"&gt;{{ value || '-' }}&lt;/div&gt;
              &lt;/div&gt;
              
              &lt;div class="pt-4"&gt;
                &lt;h3 class="text-sm font-medium text-gray-400 mb-2"&gt;Tags&lt;/h3&gt;
                &lt;div class="flex flex-wrap gap-2"&gt;
                  &lt;span
                    v-for="tag in selectedFile.tags"
                    :key="tag.id"
                    class="px-2 py-1 text-sm rounded-full bg-blue-600"
                  &gt;
                    {{ tag.name }}
                  &lt;/span&gt;
                &lt;/div&gt;
              &lt;/div&gt;
            &lt;/template&gt;
          &lt;/div&gt;
        &lt;/div&gt;
      &lt;/div&gt;

      &lt;!-- Main content --&gt;
      &lt;div class="flex-1 flex flex-col bg-gray-900 overflow-hidden"&gt;
        &lt;!-- Waveform display --&gt;
        &lt;WaveformDisplay
          v-if="selectedFile"
          :audio-url="getAudioUrl(selectedFile.id)"
          :comparison-url="comparisonFile ? getAudioUrl(comparisonFile.id) : null"
          :comparison-mode="compareMode"
          :playing="isPlaying"
          @timeupdate="updateTime"
          @ready="handleWaveformReady"
          @finish="handlePlaybackFinish"
          @error="handlePlaybackError"
        /&gt;

        &lt;!-- File list/grid --&gt;
        &lt;div class="flex-1 overflow-y-auto p-4"&gt;
          &lt;div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"&gt;
            &lt;div
              v-for="file in similarFiles"
              :key="file.id"
              @click="selectComparisonFile(file)"
              class="p-4 rounded-lg bg-gray-800 hover:bg-gray-700 cursor-pointer"
              :class="{ 'ring-2 ring-blue-500': comparisonFile?.id === file.id }"
            &gt;
              &lt;div class="font-medium truncate"&gt;{{ file.filename }}&lt;/div&gt;
              &lt;div class="text-sm text-gray-400 mt-1"&gt;
                Similarity: {{ (file.similarity_score * 100).toFixed(1) }}%
              &lt;/div&gt;
              &lt;div class="text-sm text-gray-400"&gt;
                {{ formatDuration(file.duration) }}
              &lt;/div&gt;
            &lt;/div&gt;
          &lt;/div&gt;
        &lt;/div&gt;
      &lt;/div&gt;
    &lt;/div&gt;

    &lt;!-- Settings modal --&gt;
    &lt;SettingsModal
      v-if="showSettings"
      @close="showSettings = false"
    /&gt;
  &lt;/div&gt;
&lt;/template&gt;

&lt;script setup&gt;
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import TransportControls from '../components/audio/TransportControls.vue'
import WaveformDisplay from '../components/audio/WaveformDisplay.vue'
import SettingsModal from '../components/SettingsModal.vue'

// State
const router = useRouter()
const activeTab = ref('Files')
const audioFiles = ref([])
const selectedFile = ref(null)
const comparisonFile = ref(null)
const similarFiles = ref([])
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(0.8)
const loop = ref(false)
const isRecording = ref(false)
const compareMode = ref(false)
const showSettings = ref(false)

// Load audio files
onMounted(async () => {
  try {
    const response = await axios.get('/api/v1/audio/files')
    audioFiles.value = response.data
  } catch (error) {
    console.error('Failed to load audio files:', error)
  }
})

// Watch for file selection
watch(selectedFile, async (file) => {
  if (file) {
    try {
      const response = await axios.get(`/api/v1/audio/similar/${file.id}`)
      similarFiles.value = response.data
    } catch (error) {
      console.error('Failed to load similar files:', error)
    }
  } else {
    similarFiles.value = []
  }
})

// Audio control methods
const play = () => {
  isPlaying.value = true
}

const pause = () => {
  isPlaying.value = false
}

const stop = () => {
  isPlaying.value = false
  currentTime.value = 0
}

const setLoop = (value) => {
  loop.value = value
}

const setVolume = (value) => {
  volume.value = value
}

const toggleRecord = () => {
  isRecording.value = !isRecording.value
}

const setCompareMode = (value) => {
  compareMode.value = value
  if (!value) {
    comparisonFile.value = null
  }
}

// File selection methods
const selectFile = (file) => {
  selectedFile.value = file
  stop()
}

const selectComparisonFile = (file) => {
  if (compareMode.value) {
    comparisonFile.value = file
  }
}

// Waveform event handlers
const handleWaveformReady = (audioDuration) => {
  duration.value = audioDuration
}

const updateTime = (time) => {
  currentTime.value = time
}

const handlePlaybackFinish = () => {
  isPlaying.value = false
  if (loop.value) {
    play()
  }
}

const handlePlaybackError = (error) => {
  console.error('Playback error:', error)
  isPlaying.value = false
}

// Utility methods
const formatDuration = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const formatKey = (key) => {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const getAudioUrl = (fileId) => {
  return `/api/v1/audio/stream/${fileId}`
}
&lt;/script&gt;