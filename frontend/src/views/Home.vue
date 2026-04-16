<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4">
      <h1 class="text-xl font-bold mb-1">Головна</h1>
      <p class="text-sm text-tg-hint">{{ storeName }}</p>
    </div>

    <!-- Популярні категорії (верхній рівень) -->
    <div class="grid grid-cols-2 gap-3 px-4">
      <button
        v-for="cat in topCategories"
        :key="cat.id"
        @click="goToCarousel(cat.id)"
        class="rounded-2xl bg-tg-secondary p-4 text-left active:opacity-70 transition-opacity"
      >
        <div class="text-2xl mb-2">📦</div>
        <div class="font-medium text-sm">{{ cat.name }}</div>
        <div class="text-xs text-tg-hint mt-1">
          {{ productCount(cat.id) }} товарів
        </div>
      </button>
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

const topCategories = computed(() =>
  catalog.categories.filter((c) => c.level === 'division')
)

const storeName = computed(() => {
  const s = catalog.stores.find((s) => s.id === session.currentSession?.store_id)
  return s ? s.name : ''
})

function productCount(catId) {
  return (catalog.productsByCategory[catId] || []).length
}

function goToCarousel(catId) {
  router.push({ name: 'Carousel', params: { categoryId: catId } })
}
</script>
