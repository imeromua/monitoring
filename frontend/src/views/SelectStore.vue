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
        class="w-full py-5 px-4 rounded-2xl bg-tg-secondary text-tg-text text-lg font-medium active:opacity-70 transition-opacity"
      >
        🏪 {{ store.name }}
        <span v-if="store.address" class="block text-sm text-tg-hint font-normal mt-1">
          {{ store.address }}
        </span>
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
