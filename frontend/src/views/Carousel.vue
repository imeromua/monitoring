<template>
  <div class="flex flex-col min-h-screen pb-6">
    <!-- Header -->
    <div class="flex items-center gap-3 p-4 border-b border-tg-hint/10">
      <button @click="router.back()" class="text-tg-link text-sm">← Назад</button>
      <div class="flex-1">
        <div class="text-sm font-medium">{{ categoryName }}</div>
        <ProgressBar :current="currentIndex + 1" :total="visibleProducts.length" />
      </div>
    </div>

    <!-- Картка товару -->
    <div v-if="currentProduct" class="flex-1 p-4 flex flex-col gap-4">
      <ProductCard :product="currentProduct" />

      <!-- Перемикач типу ціни -->
      <div class="flex rounded-xl overflow-hidden border border-tg-hint/20">
        <button
          @click="isPromo = false"
          :class="['flex-1 py-3 text-sm font-medium transition-colors',
            !isPromo ? 'bg-tg-button text-tg-button-text' : 'bg-tg-secondary text-tg-text']"
        >
          Звичайна
        </button>
        <button
          @click="isPromo = true"
          :class="['flex-1 py-3 text-sm font-medium transition-colors',
            isPromo ? 'bg-tg-button text-tg-button-text' : 'bg-tg-secondary text-tg-text']"
        >
          🔥 Акція
        </button>
      </div>

      <!-- Numpad -->
      <Numpad v-model="priceInput" />

      <!-- Кнопки дій -->
      <div class="flex gap-3 mt-2">
        <button
          @click="markMissing"
          class="flex-1 py-4 rounded-2xl bg-tg-secondary text-tg-hint font-medium active:opacity-70"
        >
          Відсутнє
        </button>
        <button
          @click="savePrice"
          :disabled="!priceInput || saving"
          class="flex-1 py-4 rounded-2xl bg-tg-button text-tg-button-text font-bold active:opacity-70 disabled:opacity-40"
        >
          {{ saving ? '...' : 'Зберегти' }}
        </button>
      </div>
    </div>

    <!-- Цвинтар товарів -->
    <div v-if="showGraveyard" class="p-4">
      <h2 class="font-bold mb-3">⚰️ Відсутні товари</h2>
      <div v-if="hiddenProducts.length" class="space-y-2 mb-4">
        <div
          v-for="p in hiddenProducts"
          :key="p.id"
          class="flex items-center justify-between bg-tg-secondary rounded-xl p-3"
        >
          <span class="text-sm">{{ p.name }}</span>
          <button @click="resurrect(p)" class="text-tg-link text-sm">З'явився</button>
        </div>
      </div>
      <button
        @click="confirmAllMissing"
        class="w-full py-4 rounded-2xl bg-tg-secondary text-tg-hint font-medium active:opacity-70"
      >
        Нічого з цього немає
      </button>
    </div>

    <!-- Завершення категорії -->
    <div v-if="isDone && !showGraveyard" class="p-4 flex flex-col gap-3">
      <div class="text-center text-tg-hint py-4">✅ Категорію завершено</div>
      <button
        @click="finishVisit"
        class="w-full py-4 rounded-2xl bg-tg-button text-tg-button-text font-bold active:opacity-70"
      >
        Завершити візит
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import { useSessionStore } from '@/stores/session'
import ProductCard from '@/components/ProductCard.vue'
import Numpad from '@/components/Numpad.vue'
import ProgressBar from '@/components/ProgressBar.vue'

const route = useRoute()
const router = useRouter()
const catalog = useCatalogStore()
const session = useSessionStore()

const categoryId = Number(route.params.categoryId)
const priceInput = ref('')
const isPromo = ref(false)
const saving = ref(false)
const currentIndex = ref(0)
const showGraveyard = ref(false)

const categoryName = computed(() =>
  catalog.categories.find((c) => c.id === categoryId)?.name || ''
)

const allProducts = computed(() =>
  catalog.productsByCategory[categoryId] || []
)

// Фільтруємо приховані (Smart Hide)
const visibleProducts = computed(() =>
  allProducts.value.filter((p) => !p.is_hidden)
)

const hiddenProducts = computed(() =>
  allProducts.value.filter((p) => p.is_hidden)
)

const currentProduct = computed(() =>
  visibleProducts.value[currentIndex.value] || null
)

const isDone = computed(() =>
  currentIndex.value >= visibleProducts.value.length
)

async function savePrice() {
  if (!priceInput.value || saving.value) return
  saving.value = true
  await session.saveResult({
    product_id: currentProduct.value.id,
    price: parseFloat(priceInput.value),
    is_promo: isPromo.value,
    is_missing: false,
    result_type: 'standard',
  })
  next()
  saving.value = false
}

async function markMissing() {
  await session.saveResult({
    product_id: currentProduct.value.id,
    price: null,
    is_promo: false,
    is_missing: true,
    result_type: 'standard',
  })
  next()
}

function next() {
  priceInput.value = ''
  isPromo.value = false
  currentIndex.value++
  if (isDone.value && hiddenProducts.value.length) {
    showGraveyard.value = true
  }
}

function resurrect(product) {
  product.is_hidden = false
}

async function confirmAllMissing() {
  for (const p of hiddenProducts.value) {
    await session.saveResult({
      product_id: p.id,
      price: null,
      is_promo: false,
      is_missing: true,
      result_type: 'standard',
    })
  }
  showGraveyard.value = false
}

async function finishVisit() {
  await session.finish()
  router.push({ name: 'SelectStore' })
}
</script>
