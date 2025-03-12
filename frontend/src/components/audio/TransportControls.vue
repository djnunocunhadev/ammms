<template>
  <div class="flex items-center space-x-4 px-4 py-2 bg-gray-800 border-b border-gray-700">
    <!-- Play/Pause button -->
    <button
      @click="togglePlay"
      class="p-2 rounded-full hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <component
        :is="isPlaying ? PauseIcon : PlayIcon"
        class="w-6 h-6 text-gray-200"
      />
    </button>

    <!-- Stop button -->
    <button
      @click="stop"
      class="p-2 rounded-full hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <StopIcon class="w-6 h-6 text-gray-200" />
    </button>

    <!-- Loop button -->
    <button
      @click="toggleLoop"
      :class="{
        'bg-blue-600': loop,
        'hover:bg-gray-700': !loop
      }"
      class="p-2 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <ArrowPathIcon class="w-6 h-6 text-gray-200" />
    </button>

    <!-- Time display -->
    <div class="text-sm text-gray-400 font-mono">
      {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
    </div>

    <!-- Volume control -->
    <div class="flex items-center space-x-2">
      <button
        @click="toggleMute"
        class="p-2 rounded-full hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <component
          :is="volumeIcon"
          class="w-6 h-6 text-gray-200"
        />
      </button>

      <input
        type="range"
        v-model="localVolume"
        min="0"
        max="1"
        step="0.01"
        class="w-24 accent-blue-500"
      />
    </div>

    <!-- Record button -->
    <button
      @click="toggleRecord"
      :class="{
        'bg-red-600': isRecording,
        'hover:bg-gray-700': !isRecording
      }"
      class="p-2 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <component
        :is="isRecording ? StopIcon : MicrophoneIcon"
        class="w-6 h-6 text-gray-200"
      />
    </button>

    <!-- Spacer -->
    <div class="flex-grow" />

    <!-- Additional controls -->
    <div class="flex items-center space-x-2">
      <!-- Compare mode toggle -->
      <button
        @click="toggleCompareMode"
        :class="{
          'bg-blue-600': compareMode,
          'hover:bg-gray-700': !compareMode
        }"
        class="p-2 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <ViewColumnsIcon class="w-6 h-6 text-gray-200" />
      </button>

      <!-- Settings button -->
      <button
        @click="$emit('settings')"
        class="p-2 rounded-full hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <Cog6ToothIcon class="w-6 h-6 text-gray-200" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  PlayIcon,
  PauseIcon,
  StopIcon,
  ArrowPathIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  MicrophoneIcon,
  ViewColumnsIcon,
  Cog6ToothIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  isPlaying: Boolean,
  currentTime: Number,
  duration: Number,
  volume: Number,
  loop: Boolean,
  isRecording: Boolean,
  compareMode: Boolean
})

const emit = defineEmits([
  'play',
  'pause',
  'stop',
  'loop',
  'volume-change',
  'record',
  'compare-mode',
  'settings'
])

const localVolume = ref(props.volume)
const previousVolume = ref(props.volume)

const volumeIcon = computed(() => {
  return localVolume.value === 0 ? SpeakerXMarkIcon : SpeakerWaveIcon
})

const togglePlay = () => {
  emit(props.isPlaying ? 'pause' : 'play')
}

const stop = () => {
  emit('stop')
}

const toggleLoop = () => {
  emit('loop', !props.loop)
}

const toggleMute = () => {
  if (localVolume.value > 0) {
    previousVolume.value = localVolume.value
    localVolume.value = 0
  } else {
    localVolume.value = previousVolume.value
  }
  emit('volume-change', localVolume.value)
}

const toggleRecord = () => {
  emit('record')
}

const toggleCompareMode = () => {
  emit('compare-mode', !props.compareMode)
}

const formatTime = (time) => {
  if (!time) return '00:00'
  const minutes = Math.floor(time / 60)
  const seconds = Math.floor(time % 60)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

// Watch for volume changes
watch(localVolume, (newValue) => {
  emit('volume-change', newValue)
})
</script>