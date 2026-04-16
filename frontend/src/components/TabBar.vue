<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-tg-bg border-t border-tg-hint/10 flex">
    <button
      v-for="tab in tabs"
      :key="tab.name"
      @click="router.push({ name: tab.route })"
      :class="[
        'flex-1 flex flex-col items-center py-3 gap-0.5 text-xs transition-colors',
        isActive(tab.route) ? 'text-tg-button' : 'text-tg-hint'
      ]"
    >
      <span class="text-xl">{{ tab.icon }}</span>
      <span>{{ tab.label }}</span>
    </button>

    <!-- Вкладка адміна -->
    <button
      v-if="auth.isAdmin"
      @click="router.push({ name: 'Admin' })"
      :class="[
        'flex-1 flex flex-col items-center py-3 gap-0.5 text-xs transition-colors',
        isActive('Admin') ? 'text-tg-button' : 'text-tg-hint'
      ]"
    >
      <span class="text-xl">⚙️</span>
      <span>Адмін</span>
    </button>
  </nav>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const tabs = [
  { name: 'home', route: 'Home', icon: '🏠', label: 'Головна' },
  { name: 'catalog', route: 'Catalog', icon: '📂', label: 'Каталог' },
]

function isActive(routeName) {
  return route.name === routeName
}
</script>
