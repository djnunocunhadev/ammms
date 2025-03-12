&lt;template&gt;
  &lt;div class="relative h-64 bg-gray-900"&gt;
    &lt;!-- Main waveform container --&gt;
    &lt;div ref="waveformRef" class="absolute inset-0"&gt;&lt;/div&gt;

    &lt;!-- Comparison waveform container --&gt;
    &lt;div
      v-if="comparisonMode"
      ref="comparisonWaveformRef"
      class="absolute inset-0 opacity-50"
    &gt;&lt;/div&gt;

    &lt;!-- Loading overlay --&gt;
    &lt;div
      v-if="loading"
      class="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75"
    &gt;
      &lt;div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"&gt;&lt;/div&gt;
    &lt;/div&gt;

    &lt;!-- Error overlay --&gt;
    &lt;div
      v-if="error"
      class="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75"
    &gt;
      &lt;div class="text-red-500 text-center"&gt;
        &lt;svg
          class="w-12 h-12 mx-auto mb-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        &gt;
          &lt;path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          /&gt;
        &lt;/svg&gt;
        &lt;p&gt;{{ error }}&lt;/p&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/template&gt;

&lt;script setup&gt;
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
  playing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['timeupdate', 'ready', 'finish', 'error'])

const waveformRef = ref(null)
const comparisonWaveformRef = ref(null)
const wavesurfer = ref(null)
const comparisonWavesurfer = ref(null)
const loading = ref(true)
const error = ref(null)

// Initialize main waveform
const initWaveform = async () => {
  if (!waveformRef.value) return

  try {
    wavesurfer.value = WaveSurfer.create({
      container: waveformRef.value,
      waveColor: '#4B5563',
      progressColor: '#3B82F6',
      cursorColor: '#60A5FA',
      barWidth: 2,
      barGap: 1,
      responsive: true,
      height: 256,
      normalize: true,
      partialRender: true
    })

    wavesurfer.value.on('ready', () => {
      loading.value = false
      emit('ready', wavesurfer.value.getDuration())
    })

    wavesurfer.value.on('audioprocess', () => {
      emit('timeupdate', wavesurfer.value.getCurrentTime())
    })

    wavesurfer.value.on('finish', () => {
      emit('finish')
    })

    wavesurfer.value.on('error', (err) => {
      error.value = 'Error loading audio file'
      emit('error', err)
    })

    await wavesurfer.value.load(props.audioUrl)
  } catch (err) {
    error.value = 'Error initializing waveform'
    emit('error', err)
  }
}

// Initialize comparison waveform
const initComparisonWaveform = async () => {
  if (!comparisonWaveformRef.value || !props.comparisonUrl) return

  try {
    comparisonWavesurfer.value = WaveSurfer.create({
      container: comparisonWaveformRef.value,
      waveColor: '#9CA3AF',
      progressColor: '#60A5FA',
      cursorColor: '#60A5FA',
      barWidth: 2,
      barGap: 1,
      responsive: true,
      height: 256,
      normalize: true,
      partialRender: true
    })

    comparisonWavesurfer.value.on('ready', () => {
      if (wavesurfer.value.isPlaying()) {
        comparisonWavesurfer.value.play()
      }
    })

    await comparisonWavesurfer.value.load(props.comparisonUrl)
  } catch (err) {
    error.value = 'Error initializing comparison waveform'
    emit('error', err)
  }
}

// Watch for changes in playing state
watch(() => props.playing, (newVal) => {
  if (!wavesurfer.value) return

  if (newVal) {
    wavesurfer.value.play()
    if (props.comparisonMode && comparisonWavesurfer.value) {
      comparisonWavesurfer.value.play()
    }
  } else {
    wavesurfer.value.pause()
    if (props.comparisonMode && comparisonWavesurfer.value) {
      comparisonWavesurfer.value.pause()
    }
  }
})

// Watch for changes in comparison mode and URL
watch([() => props.comparisonMode, () => props.comparisonUrl], async ([newMode, newUrl]) => {
  if (newMode && newUrl) {
    if (!comparisonWavesurfer.value) {
      await initComparisonWaveform()
    } else if (comparisonWavesurfer.value.backend.source.url !== newUrl) {
      await comparisonWavesurfer.value.load(newUrl)
    }
  }
})

// Watch for changes in audio URL
watch(() => props.audioUrl, async (newUrl) => {
  if (wavesurfer.value && newUrl) {
    loading.value = true
    error.value = null
    try {
      await wavesurfer.value.load(newUrl)
    } catch (err) {
      error.value = 'Error loading audio file'
      emit('error', err)
    }
  }
})

// Lifecycle hooks
onMounted(async () => {
  await initWaveform()
  if (props.comparisonMode && props.comparisonUrl) {
    await initComparisonWaveform()
  }
})

onBeforeUnmount(() => {
  if (wavesurfer.value) {
    wavesurfer.value.destroy()
  }
  if (comparisonWavesurfer.value) {
    comparisonWavesurfer.value.destroy()
  }
})

// Expose methods for parent component
defineExpose({
  seek: (time) => {
    if (wavesurfer.value) {
      wavesurfer.value.seekTo(time / wavesurfer.value.getDuration())
      if (props.comparisonMode && comparisonWavesurfer.value) {
        comparisonWavesurfer.value.seekTo(time / comparisonWavesurfer.value.getDuration())
      }
    }
  },
  setVolume: (volume) => {
    if (wavesurfer.value) {
      wavesurfer.value.setVolume(volume)
      if (props.comparisonMode && comparisonWavesurfer.value) {
        comparisonWavesurfer.value.setVolume(volume)
      }
    }
  }
})
&lt;/script&gt;