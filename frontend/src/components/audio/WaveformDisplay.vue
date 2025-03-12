<template>
  <div
    ref="container"
    class="relative w-full bg-gray-800 rounded-lg overflow-hidden"
    :class="{ 'h-48': !comparisonMode, 'h-96': comparisonMode }"
  >
    <!-- Main waveform -->
    <div ref="waveform" class="w-full h-1/2" />

    <!-- Comparison waveform (if in comparison mode) -->
    <div
      v-if="comparisonMode"
      ref="comparisonWaveform"
      class="w-full h-1/2 border-t border-gray-700"
    />

    <!-- Time markers -->
    <div
      class="absolute bottom-0 left-0 right-0 flex justify-between px-2 py-1 text-xs text-gray-400 bg-gray-800 bg-opacity-75"
    >
      <span>{{ formatTime(currentTime) }}</span>
      <span>{{ formatTime(duration) }}</span>
    </div>

    <!-- Loading overlay -->
    <div
      v-if="loading"
      class="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75"
    >
      <svg
        class="animate-spin h-8 w-8 text-blue-500"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import WaveSurfer from 'wavesurfer.js'

const props = defineProps({
  audioUrl: {
    type: String,
    required: true
  },
  comparisonUrl: {
    type: String,
    default: null
  },
  comparisonMode: {
    type: Boolean,
    default: false
  },
  peaks: {
    type: Array,
    default: () => []
  },
  comparisonPeaks: {
    type: Array,
    default: () => []
  },
  playing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['timeupdate', 'ready', 'finish', 'error'])

const container = ref(null)
const waveform = ref(null)
const comparisonWaveform = ref(null)
const wavesurfer = ref(null)
const comparisonWavesurfer = ref(null)
const loading = ref(true)
const currentTime = ref(0)
const duration = ref(0)

// Initialize WaveSurfer instances
onMounted(async () => {
  // Create main waveform
  wavesurfer.value = WaveSurfer.create({
    container: waveform.value,
    waveColor: '#4a9eff',
    progressColor: '#2563eb',
    cursorColor: '#60a5fa',
    cursorWidth: 2,
    height: props.comparisonMode ? 128 : 200,
    normalize: true,
    responsive: true,
    fillParent: true,
    minPxPerSec: 50,
    plugins: []
  })

  // Create comparison waveform if in comparison mode
  if (props.comparisonMode && props.comparisonUrl) {
    comparisonWavesurfer.value = WaveSurfer.create({
      container: comparisonWaveform.value,
      waveColor: '#22c55e',
      progressColor: '#16a34a',
      cursorColor: '#4ade80',
      cursorWidth: 2,
      height: 128,
      normalize: true,
      responsive: true,
      fillParent: true,
      minPxPerSec: 50,
      plugins: []
    })
  }

  // Set up event listeners
  wavesurfer.value.on('ready', () => {
    loading.value = false
    duration.value = wavesurfer.value.getDuration()
    emit('ready')
  })

  wavesurfer.value.on('audioprocess', (time) => {
    currentTime.value = time
    emit('timeupdate', time)
  })

  wavesurfer.value.on('finish', () => {
    emit('finish')
  })

  wavesurfer.value.on('error', (error) => {
    emit('error', error)
  })

  // Load audio
  try {
    if (props.peaks.length > 0) {
      await wavesurfer.value.load(props.audioUrl, props.peaks)
    } else {
      await wavesurfer.value.load(props.audioUrl)
    }

    if (props.comparisonMode && props.comparisonUrl) {
      if (props.comparisonPeaks.length > 0) {
        await comparisonWavesurfer.value.load(props.comparisonUrl, props.comparisonPeaks)
      } else {
        await comparisonWavesurfer.value.load(props.comparisonUrl)
      }
    }
  } catch (error) {
    emit('error', error)
  }
})

// Clean up on component unmount
onBeforeUnmount(() => {
  if (wavesurfer.value) {
    wavesurfer.value.destroy()
  }
  if (comparisonWavesurfer.value) {
    comparisonWavesurfer.value.destroy()
  }
})

// Watch for playing state changes
watch(
  () => props.playing,
  (newVal) => {
    if (newVal) {
      wavesurfer.value?.play()
      if (props.comparisonMode) {
        comparisonWavesurfer.value?.play()
      }
    } else {
      wavesurfer.value?.pause()
      if (props.comparisonMode) {
        comparisonWavesurfer.value?.pause()
      }
    }
  }
)

// Format time in MM:SS format
const formatTime = (time) => {
  if (!time) return '00:00'
  const minutes = Math.floor(time / 60)
  const seconds = Math.floor(time % 60)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}
</script>
