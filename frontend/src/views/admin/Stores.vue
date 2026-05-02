<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4 border-b border-tg-hint/10">
      <h1 class="text-xl font-bold">🏪 Магазини</h1>
    </div>

    <!-- Форма додавання -->
    <div class="p-4 border-b border-tg-hint/10 space-y-2">
      <input v-model="newName" placeholder="Назва магазину" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none" />
      <input v-model="newAddress" placeholder="Адреса (необов'язково)" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none" />
      <button @click="addStore" :disabled="!newName" class="w-full py-3 rounded-xl bg-tg-button text-tg-button-text font-medium text-sm active:opacity-70 disabled:opacity-50">
        + Додати магазин
      </button>
    </div>

    <!-- Список -->
    <div class="p-4 space-y-3">
      <div v-for="store in stores" :key="store.id" class="bg-tg-secondary rounded-2xl overflow-hidden">

        <!-- Основна інформація -->
        <div class="flex items-center gap-3 p-4">
          <!-- Аватар -->
          <div class="w-12 h-12 rounded-full overflow-hidden flex-shrink-0 bg-tg-hint/20 flex items-center justify-center">
            <img v-if="store.logo_url" :src="store.logo_url" :alt="store.name" class="w-full h-full object-cover" />
            <span v-else class="text-2xl">🏪</span>
          </div>

          <!-- Текст -->
          <div class="flex-1 min-w-0">
            <div class="font-semibold text-sm truncate">{{ store.name }}</div>
            <div v-if="store.address" class="text-xs text-tg-hint truncate">{{ store.address }}</div>
            <div v-if="store.logo_url" class="text-xs text-green-500 mt-0.5">✓ Лого завантажено</div>
          </div>
        </div>

        <!-- Дії -->
        <div class="flex border-t border-tg-hint/10">
          <!-- Завантажити лого -->
          <label class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium text-tg-button cursor-pointer active:opacity-60 hover:bg-tg-button/5 transition-colors">
            <span>📷</span>
            <span>{{ store.logo_url ? 'Змінити лого' : 'Завантажити лого' }}</span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              class="hidden"
              @change="(e) => uploadLogo(store.id, e)"
            />
          </label>

          <!-- Розділювач -->
          <div class="w-px bg-tg-hint/10"></div>

          <!-- Архів -->
          <button
            @click="archiveStore(store)"
            class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium text-red-400 active:opacity-60 hover:bg-red-500/5 transition-colors"
          >
            <span>🗑️</span>
            <span>Архівувати</span>
          </button>
        </div>
      </div>

      <p v-if="stores.length === 0" class="text-center text-tg-hint text-sm py-8">Магазинів немає</p>
    </div>

    <!-- Прогрес завантаження -->
    <div v-if="uploading" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-tg-bg rounded-2xl px-8 py-6 text-center">
        <div class="text-3xl mb-2 animate-bounce">📷</div>
        <p class="text-sm font-medium">Завантаження лого...</p>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'
import TabBar from '@/components/TabBar.vue'

const stores = ref([])
const newName = ref('')
const newAddress = ref('')
const uploading = ref(false)

onMounted(async () => {
  await loadStores()
})

async function loadStores() {
  const { data } = await api.get('/stores')
  stores.value = data
}

async function addStore() {
  if (!newName.value) return
  try {
    await api.post('/admin/stores', null, { params: { name: newName.value, address: newAddress.value } })
    newName.value = ''
    newAddress.value = ''
    await loadStores()
  } catch (e) {
    alert(e.response?.data?.detail || 'Помилка при додаванні магазину')
  }
}

async function uploadLogo(storeId, event) {
  const file = event.target.files?.[0]
  if (!file) return

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post(`/admin/stores/${storeId}/logo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    // Оновити лого у локальному стані без повного перезавантаження
    const store = stores.value.find(s => s.id === storeId)
    if (store) store.logo_url = data.logo_url
  } catch (e) {
    alert(e.response?.data?.detail || 'Помилка завантаження лого')
  } finally {
    uploading.value = false
    event.target.value = ''
  }
}

async function archiveStore(store) {
  if (!confirm(`Архівувати магазин "${store.name}"?`)) return
  try {
    await api.patch(`/admin/stores/${store.id}/archive`)
    stores.value = stores.value.filter(s => s.id !== store.id)
  } catch (e) {
    alert(e.response?.data?.detail || 'Помилка')
  }
}
</script>
