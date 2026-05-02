<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4">
      <h1 class="text-xl font-bold">Каталог</h1>
    </div>

    <div class="px-4 space-y-2">
      <button
        v-for="cat in categoriesWithProducts"
        :key="cat.id"
        @click="goToCarousel(cat.id)"
        class="w-full text-left py-3 px-4 rounded-xl bg-tg-secondary active:opacity-70 transition-opacity"
      >
        <span class="font-medium text-sm">{{ cat.name }}</span>
        <span class="text-tg-hint text-xs ml-2">({{ catalog.getTotalProductsCount(cat.id) }})</span>
      </button>

      <p v-if="categoriesWithProducts.length === 0" class="text-center text-tg-hint text-sm py-10">
        Каталог порожній. Завантажте товари через адмін-панель.
      </p>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import TabBar from '@/components/TabBar.vue'

const router = useRouter()
const catalog = useCatalogStore()

// Тільки категорії де є хоча б один товар (включаючи підкатегорії)
const categoriesWithProducts = computed(() =>
  catalog.categories
    .filter((c) => catalog.getTotalProductsCount(c.id) > 0)
    .sort((a, b) => a.sort_order - b.sort_order || a.name.localeCompare(b.name, 'uk'))
)

function goToCarousel(catId) {
  router.push({ name: 'Carousel', params: { categoryId: catId } })
}
</script>
