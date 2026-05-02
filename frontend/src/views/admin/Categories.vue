<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4 border-b border-tg-hint/10 flex justify-between items-center">
      <h1 class="text-xl font-bold">📁 Категорії</h1>
      <button @click="openModal()" class="px-4 py-2 bg-tg-button text-tg-button-text rounded-lg text-sm font-medium">
        + Додати
      </button>
    </div>

    <!-- Список -->
    <div class="p-4 space-y-2">
      <div v-for="category in categories" :key="category.id" class="bg-tg-secondary rounded-xl p-4 flex justify-between items-center">
        <div>
          <p class="font-medium text-sm">{{ category.name }}</p>
          <p class="text-xs text-tg-hint">Рівень: {{ category.level }} · ID: {{ category.id }}</p>
        </div>
        <div class="flex gap-2">
          <button @click="openModal(category)" class="p-2 text-tg-button bg-tg-button/10 rounded-lg">✏️</button>
          <button @click="deleteCategory(category.id)" class="p-2 text-red-500 bg-red-500/10 rounded-lg">🗑️</button>
        </div>
      </div>
    </div>

    <!-- Модалка створення/редагування -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-tg-bg rounded-2xl w-full max-w-sm overflow-hidden flex flex-col">
        <div class="p-4 border-b border-tg-hint/10">
          <h2 class="text-lg font-bold">{{ isEditing ? 'Редагувати категорію' : 'Нова категорія' }}</h2>
        </div>
        <div class="p-4 space-y-3">
          <input v-model="form.name" placeholder="Назва категорії" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none" />
          <select v-model="form.level" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none">
            <option value="" disabled>Оберіть рівень</option>
            <option value="division">Відділ (division)</option>
            <option value="department">Департамент (department)</option>
            <option value="group">Група (group)</option>
          </select>
          <input v-model="form.sort_order" type="number" placeholder="Порядок сортування (0 за замовч.)" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none" />
        </div>
        <div class="p-4 grid grid-cols-2 gap-3 mt-auto">
          <button @click="closeModal" class="py-3 rounded-xl bg-tg-secondary text-tg-text font-medium text-sm">Скасувати</button>
          <button @click="saveCategory" :disabled="!isValid" class="py-3 rounded-xl bg-tg-button text-tg-button-text font-medium text-sm disabled:opacity-50">Зберегти</button>
        </div>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getAdminCategories, createAdminCategory, updateAdminCategory, deleteAdminCategory } from '@/api/catalog'
import TabBar from '@/components/TabBar.vue'

const categories = ref([])

const isModalOpen = ref(false)
const isEditing = ref(false)
const form = ref({ id: null, name: '', level: 'group', sort_order: 0, parent_id: null })

const isValid = computed(() => form.value.name && form.value.level)

async function loadData() {
  const { data } = await getAdminCategories()
  categories.value = data
}

onMounted(() => {
  loadData()
})

function openModal(category = null) {
  if (category) {
    isEditing.value = true
    form.value = { ...category }
  } else {
    isEditing.value = false
    form.value = { id: null, name: '', level: 'group', sort_order: 0, parent_id: null }
  }
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

async function saveCategory() {
  if (!isValid.value) return
  try {
    if (isEditing.value) {
      await updateAdminCategory(form.value.id, {
        name: form.value.name,
        level: form.value.level,
        sort_order: form.value.sort_order
      })
    } else {
      await createAdminCategory({
        name: form.value.name,
        level: form.value.level,
        sort_order: form.value.sort_order || 0
      })
    }
    closeModal()
    await loadData()
  } catch (e) {
    alert(e.response?.data?.detail || 'Помилка збереження категорії')
  }
}

async function deleteCategory(id) {
  if (confirm('Ви впевнені, що хочете видалити цю категорію?')) {
    try {
      await deleteAdminCategory(id)
      await loadData()
    } catch (e) {
      alert(e.response?.data?.detail || 'Помилка видалення категорії')
    }
  }
}
</script>
