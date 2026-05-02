<template>
  <div class="min-h-screen bg-tg-bg text-tg-text">
    <ConnectionStatus />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCatalogStore } from '@/stores/catalog'
import ConnectionStatus from '@/components/ConnectionStatus.vue'

const auth = useAuthStore()
const catalog = useCatalogStore()

onMounted(async () => {
  const tg = window.Telegram?.WebApp
  if (tg) {
    tg.ready()
    tg.expand()
    const theme = tg.themeParams
    if (theme) {
      document.documentElement.style.setProperty('--tg-theme-bg-color', theme.bg_color || '#ffffff')
      document.documentElement.style.setProperty('--tg-theme-text-color', theme.text_color || '#000000')
      document.documentElement.style.setProperty('--tg-theme-hint-color', theme.hint_color || '#999999')
      document.documentElement.style.setProperty('--tg-theme-button-color', theme.button_color || '#2481cc')
      document.documentElement.style.setProperty('--tg-theme-button-text-color', theme.button_text_color || '#ffffff')
      document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', theme.secondary_bg_color || '#f1f1f1')
    }
  }
  await auth.init()
  if (auth.isAuthenticated) {
    await catalog.load()
  }
})
</script>
