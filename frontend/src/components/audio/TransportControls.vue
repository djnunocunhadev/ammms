&lt;template&gt;
  &lt;div class="bg-gray-800 border-b border-gray-700 p-4"&gt;
    &lt;div class="flex items-center justify-between"&gt;
      &lt;!-- Main controls --&gt;
      &lt;div class="flex items-center space-x-4"&gt;
        &lt;button
          @click="$emit(isPlaying ? 'pause' : 'play')"
          class="p-2 rounded-full hover:bg-gray-700"
          :title="isPlaying ? 'Pause' : 'Play'"
        &gt;
          &lt;svg
            v-if="isPlaying"
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          &gt;
            &lt;path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10 9v6m4-6v6"
            /&gt;
          &lt;/svg&gt;
          &lt;svg
            v-else
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          &gt;
            &lt;path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
            /&gt;
            &lt;path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            /&gt;
          &lt;/svg&gt;
        &lt;/button&gt;

        &lt;button
          @click="$emit('stop')"
          class="p-2 rounded-full hover:bg-gray-700"
          title="Stop"
        &gt;
          &lt;svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          &gt;
            &lt;rect
              x="6"
              y="6"
              width="12"
              height="12"
              stroke-width="2"
            /&gt;
          &lt;/svg&gt;
        &lt;/button&gt;

        &lt;button
          @click="$emit('loop', !loop)"
          class="p-2 rounded-full hover:bg-gray-700"
          :class="{ 'text-blue-500': loop }"
          title="Toggle Loop"
        &gt;
          &lt;svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          &gt;
            &lt;path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            /&gt;
          &lt;/svg&gt;
        &lt;/button&gt;
      &lt;/div&gt;

      &lt;!-- Time display and progress --&gt;
      &lt;div class="flex-1 mx-8"&gt;
        &lt;div class="flex items-center justify-between text-sm mb-1"&gt;
          &lt;span&gt;{{ formatTime(currentTime) }}&lt;/span&gt;
          &lt;span&gt;{{ formatTime(duration) }}&lt;/span&gt;
        &lt;/div&gt;
        &lt;input
          type="range"
          :value="currentTime"
          :max="duration"
          @input="handleSeek"
          class="w-full"
        /&gt;
      &lt;/div&gt;

      &lt;!-- Additional controls --&gt;
      &lt;div class="flex items-center space-x-4"&gt;
        &lt;!-- Volume control --&gt;
        &lt;div class="flex items-center space-x-2"&gt;
          &lt;button
            @click="toggleMute"
            class="p-2 rounded-full hover:bg-gray-700"
            :title="isMuted ? 'Unmute' : 'Mute'"
          &gt;
            &lt;svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            &gt;
              &lt;path
                v-if="isMuted"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
              /&gt;
              &lt;path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15.536 8.464a5 5 0 010 7.072M18.364 5.636a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
              /&gt;
            &lt;/svg&gt;
          &lt;/button&gt;
          &lt;input
            type="range"
            :value="volume * 100"
            @input="handleVolumeChange"
            class="w-24"
            min="0"
            max="100"
          /&gt;
        &lt;/div&gt;

        &lt;!-- Record button --&gt;
        &lt;button
          @click="$emit('record')"
          class="p-2 rounded-full hover:bg-gray-700"
          :class="{ 'text-red-500': isRecording }"
          title="Toggle Recording"
        &gt;
          &lt;svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          &gt;
            &lt;circle cx="12" cy="12" r="6" :fill="isRecording ? 'currentColor' : 'none'" stroke-width="2" /&gt;
          &lt;/svg&gt;
        &lt;/button&gt;

        &lt;!-- Compare mode toggle --&gt;
        &lt;button
          @click="$emit('compare-mode', !compareMode)"
          class="p-2 rounded-full hover:bg-gray-700"
          :class="{ 'text-blue-500': compareMode }"
          title="Toggle Compare Mode"
        &gt;
          &lt;svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          &gt;
            &lt;path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
            /&gt;
          &lt;/svg&gt;
        &lt;/button&gt;

        &lt;!-- Settings button --&gt;
        &lt;button
          @click="$emit('settings')"
          class="p-2 rounded-full hover:bg-gray-700"
          title="Settings"
        &gt;
          &lt;svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          &gt;
            &lt;path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            /&gt;
            &lt;path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            /&gt;
          &lt;/svg&gt;
        &lt;/button&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/template&gt;

&lt;script setup&gt;
import { ref, computed } from 'vue'

const props = defineProps({
  isPlaying: {
    type: Boolean,
    default: false
  },
  currentTime: {
    type: Number,
    default: 0
  },
  duration: {
    type: Number,
    default: 0
  },
  volume: {
    type: Number,
    default: 0.8
  },
  loop: {
    type: Boolean,
    default: false
  },
  isRecording: {
    type: Boolean,
    default: false
  },
  compareMode: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'play',
  'pause',
  'stop',
  'loop',
  'volume-change',
  'seek',
  'record',
  'compare-mode',
  'settings'
])

const isMuted = ref(false)
const previousVolume = ref(props.volume)

const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const handleSeek = (event) => {
  emit('seek', parseFloat(event.target.value))
}

const handleVolumeChange = (event) => {
  const newVolume = parseFloat(event.target.value) / 100
  emit('volume-change', newVolume)
  if (isMuted.value && newVolume > 0) {
    isMuted.value = false
  }
}

const toggleMute = () => {
  if (isMuted.value) {
    isMuted.value = false
    emit('volume-change', previousVolume.value)
  } else {
    previousVolume.value = props.volume
    isMuted.value = true
    emit('volume-change', 0)
  }
}
&lt;/script&gt;