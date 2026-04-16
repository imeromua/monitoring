<template>
  <transition name="slide">
    <div
      v-if="!isOnline"
      class="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-2 py-2 bg-red-500 text-white text-xs font-medium"
    >
      <span class="w-2 h-2 rounded-full bg-white animate-pulse"></span>
      Офлайн — дані зберігаються локально
    </div>
    <div
      v-else-if="justRestored"
      class="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-2 py-2 bg-green-500 text-white text-xs font-medium"
    >
      <span class="w-2 h-2 rounded-full bg-white"></span>
      Онлайн — синхронізація...
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useSessionStore } from '@/stores/session'

const isOnline = ref(navigator.onLine)
const justRestored = ref(false)
const session = useSessionStore()
let restoreTimer = null

async function handleOnline() {
  isOnline.value = true
  justRestored.value = true
  await session.syncOfflineQueue()
  restoreTimer = setTimeout(() => {
    justRestored.value = false
  }, 3000)
}

function handleOffline() {
  isOnline.value = false
  justRestored.value = false
}

onMounted(() => {
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
  clearTimeout(restoreTimer)
})
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
