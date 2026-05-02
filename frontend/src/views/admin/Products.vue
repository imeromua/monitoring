<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4 border-b border-tg-hint/10 flex justify-between items-center">
      <h1 class="text-xl font-bold">🏷️ Товари</h1>
      <button @click="openModal()" class="px-4 py-2 bg-tg-button text-tg-button-text rounded-lg text-sm font-medium">
        + Додати
      </button>
    </div>

    <!-- Список -->
    <div class="p-4 space-y-2">
      <div v-for="product in products" :key="product.id" class="bg-tg-secondary rounded-xl p-4 flex justify-between items-center">
        <div>
          <p class="font-medium text-sm">{{ product.name }}</p>
          <p class="text-xs text-tg-hint">Артикул: {{ product.article_id }} · Категорія ID: {{ product.category_id }}</p>
        </div>
        <div class="flex gap-2">
          <button @click="openModal(product)" class="p-2 text-tg-button bg-tg-button/10 rounded-lg">✏️</button>
          <button @click="deleteProduct(product.id)" class="p-2 text-red-500 bg-red-500/10 rounded-lg">🗑️</button>
        </div>
      </div>
    </div>

    <!-- Модалка створення/редагування -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-tg-bg rounded-2xl w-full max-w-sm overflow-hidden flex flex-col">
        <div class="p-4 border-b border-tg-hint/10">
          <h2 class="text-lg font-bold">{{ isEditing ? 'Редагувати товар' : 'Новий товар' }}</h2>
        </div>
        <div class="p-4 space-y-3">
          <input v-model="form.article_id" placeholder="Артикул (8 цифр)" maxlength="8" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none" />
          <input v-model="form.name" placeholder="Назва товару" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none" />
          <select v-model="form.category_id" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none">
            <option value="" disabled>Оберіть категорію</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }} (ID: {{ cat.id }})</option>
          </select>
        </div>
        <div class="p-4 grid grid-cols-2 gap-3 mt-auto">
          <button @click="closeModal" class="py-3 rounded-xl bg-tg-secondary text-tg-text font-medium text-sm">Скасувати</button>
          <button @click="saveProduct" :disabled="!isValid" class="py-3 rounded-xl bg-tg-button text-tg-button-text font-medium text-sm disabled:opacity-50">Зберегти</button>
        </div>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getAdminProducts, createAdminProduct, updateAdminProduct, deleteAdminProduct, getAdminCategories } from '@/api/catalog'
import TabBar from '@/components/TabBar.vue'

const products = ref([])
const categories = ref([])

const isModalOpen = ref(false)
const isEditing = ref(false)
const form = ref({ id: null, article_id: '', name: '', category_id: '' })

const isValid = computed(() => form.value.article_id?.length === 8 && form.value.name && form.value.category_id)

async function loadData() {
  const [prodRes, catRes] = await Promise.all([
    getAdminProducts(),
    getAdminCategories()
  ])
  products.value = prodRes.data
  categories.value = catRes.data
}

onMounted(() => {
  loadData()
})

function openModal(product = null) {
  if (product) {
    isEditing.value = true
    form.value = { ...product }
  } else {
    isEditing.value = false
    form.value = { id: null, article_id: '', name: '', category_id: '' }
  }
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function saveProduct() {
  if (!isValid.value) return
  if (isEditing.value) {
    await updateAdminProduct(form.value.id, {
      article_id: form.value.article_id,
      name: form.value.name,
      category_id: form.value.category_id
    })
  } else {
    await createAdminProduct({
      article_id: form.value.article_id,
      name: form.value.name,
      category_id: form.value.category_id
    })
  }
  closeModal()
  await loadData()
}

async function deleteProduct(id) {
  if (confirm('Ви впевнені, що хочете видалити цей товар?')) {
    await deleteAdminProduct(id)
    await loadData()
  }
}
</script>
