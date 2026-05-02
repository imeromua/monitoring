<template>
  <div class="flex flex-col min-h-screen p-4">
    <h1 class="text-xl font-bold mb-6 text-center">Оберіть магазин</h1>

    <div v-if="loading" class="flex justify-center mt-10">
      <span class="text-tg-hint">Завантаження...</span>
    </div>

    <div v-else class="flex flex-col gap-3">
      <button
        v-for="store in stores"
        :key="store.id"
        @click="selectStore(store)"
        class="w-full flex items-center gap-4 py-4 px-4 rounded-2xl bg-tg-secondary text-tg-text active:opacity-70 transition-opacity"
      >
        <!-- Аватар -->
        <div class="w-14 h-14 rounded-full overflow-hidden flex-shrink-0 bg-tg-hint/20 flex items-center justify-center">
          <img v-if="store.logo_url" :src="store.logo_url" :alt="store.name" class="w-full h-full object-cover" />
          <span v-else class="text-3xl">🏪</span>
        </div>
        <!-- Текст -->
        <div class="text-left flex-1 min-w-0">
          <div class="font-semibold text-base truncate">{{ store.name }}</div>
          <div v-if="store.address" class="text-sm text-tg-hint truncate mt-0.5">{{ store.address }}</div>
        </div>
        <span class="text-tg-hint text-xl flex-shrink-0">›</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import { useSessionStore } from '@/stores/session'

const router = useRouter()
const catalog = useCatalogStore()
const session = useSessionStore()
const loading = ref(true)

const stores = ref([])

onMounted(async () => {
  await catalog.load(true)
  stores.value = catalog.stores
  loading.value = false
})

async function selectStore(store) {
  await session.startSession(store.id)
  router.push({ name: 'Home' })
}
</script>
