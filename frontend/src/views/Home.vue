<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4">
      <h1 class="text-xl font-bold mb-1">Головна</h1>
      <p class="text-sm text-tg-hint">{{ storeName }}</p>
    </div>

    <!-- Магазини -->
    <div v-if="catalog.stores.length > 1" class="px-4 mb-4">
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
      <p class="text-xs text-tg-hint uppercase tracking-wide mb-3">Категорії</p>
      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="cat in activeCategories"
          :key="cat.id"
          @click="goToCarousel(cat.id)"
          class="relative rounded-2xl bg-tg-secondary p-4 text-left active:scale-95 transition-transform duration-150"
        >
          <!-- Emoji іконка -->
          <div class="text-3xl mb-3">{{ getCategoryEmoji(cat) }}</div>

          <!-- Назва -->
          <div class="font-semibold text-sm leading-tight mb-2">{{ cat.name }}</div>

          <!-- Ярлик з кількістю товарів -->
          <div class="inline-flex items-center gap-1 bg-tg-button/15 rounded-full px-2 py-0.5">
            <span class="text-xs">&#x1f4e6;</span>
            <span class="text-xs font-medium text-tg-button">{{ catalog.getTotalProductsCount(cat.id) }}</span>
          </div>
        </button>
      </div>

      <p v-if="activeCategories.length === 0" class="text-center text-tg-hint text-sm py-10">
        Каталог порожній. Зверніться до адміністратора.
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

// Емодзі за першою літерою назви
const CATEGORY_EMOJIS = {
  'а': '🍎', 'б': '🥐', 'в': '💧', 'г': '🍄', 'д': '🌳',
  'е': '💻', 'ж': '🪼', 'з': '🌟', 'и': '🧸', 'і': '🍨',
  'ї': '📦', 'й': '🌊', 'к': '🎨', 'л': '🛒', 'м': '🍦',
  'н': '📺', 'о': '🎁', 'п': '📖', 'р': '🌹', 'с': '👖',
  'т': '🍕', 'у': '🐑', 'ф': '🥡', 'х': '🌾', 'ц': '🍢',
  'ч': '🐡', 'ш': '🍫', 'щ': '🥞', 'ю': '🎠', 'я': '🍋',
}

function getCategoryEmoji(cat) {
  const firstChar = cat.name?.[0]?.toLowerCase() || ''
  return CATEGORY_EMOJIS[firstChar] || '📦'
}

// Тільки категорії з товарами, сортовані
const activeCategories = computed(() =>
  catalog.categories
    .filter((c) => catalog.getTotalProductsCount(c.id) > 0)
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
