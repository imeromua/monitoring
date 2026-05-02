<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4">
      <h1 class="text-xl font-bold mb-1">Головна</h1>
      <p class="text-sm text-tg-hint">{{ storeName }}</p>
    </div>

    <!-- Магазини -->
    <div class="px-4 mb-4">
      <p class="text-xs text-tg-hint uppercase tracking-wide mb-2">Магазини</p>
      <div class="space-y-2">
        <button
          v-for="store in catalog.stores"
          :key="store.id"
          class="w-full text-left py-3 px-4 rounded-xl bg-tg-secondary text-sm active:opacity-70 transition-opacity"
          :class="store.id === session.currentSession?.store_id ? 'ring-2 ring-tg-button' : ''"
        >
          <span class="font-medium">{{ store.name }}</span>
          <span v-if="store.id === session.currentSession?.store_id" class="text-tg-hint text-xs ml-2">• поточний</span>
        </button>
      </div>
    </div>

    <!-- Категорії -->
    <div class="px-4">
      <p class="text-xs text-tg-hint uppercase tracking-wide mb-2">Категорії</p>
      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="cat in allCategories"
          :key="cat.id"
          @click="goToCarousel(cat.id)"
          class="rounded-2xl bg-tg-secondary p-4 text-left active:opacity-70 transition-opacity"
        >
          <div class="text-2xl mb-2">📦</div>
          <div class="font-medium text-sm">{{ cat.name }}</div>
          <div class="text-xs text-tg-hint mt-1">{{ catalog.getTotalProductsCount(cat.id) }} товарів</div>
        </button>
      </div>
      <p v-if="allCategories.length === 0" class="text-center text-tg-hint text-sm py-6">
        Каталог порожній
      </p>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import { useSessionStore } from '@/stores/session'
import TabBar from '@/components/TabBar.vue'

const router = useRouter()
const catalog = useCatalogStore()
const session = useSessionStore()

// Усі категорії без батьківських, сортовані
const allCategories = computed(() =>
  catalog.categories
    .filter((c) => c.parent_id === null || c.parent_id === undefined)
    .sort((a, b) => a.sort_order - b.sort_order || a.name.localeCompare(b.name, 'uk'))
)

const storeName = computed(() => {
  const s = catalog.stores.find((s) => s.id === session.currentSession?.store_id)
  return s ? s.name : ''
})

function goToCarousel(catId) {
  router.push({ name: 'Carousel', params: { categoryId: catId } })
}
</script>
