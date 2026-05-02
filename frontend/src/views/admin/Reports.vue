<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4 border-b border-tg-hint/10">
      <h1 class="text-xl font-bold">📊 Звіти</h1>
    </div>

    <div class="p-4 space-y-3">
      <div>
        <label class="text-xs text-tg-hint mb-1 block">Дата від</label>
        <input v-model="dateFrom" type="date" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none" />
      </div>
      <div>
        <label class="text-xs text-tg-hint mb-1 block">Дата до</label>
        <input v-model="dateTo" type="date" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none" />
      </div>
      <div>
        <label class="text-xs text-tg-hint mb-1 block">Магазин (необов'язково)</label>
        <select v-model="storeId" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none">
          <option :value="null">Всі магазини</option>
          <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>

      <button
        @click="downloadReport"
        :disabled="!dateFrom || !dateTo || loading"
        class="w-full py-4 rounded-2xl bg-tg-button text-tg-button-text font-bold active:opacity-70 disabled:opacity-40"
      >
        {{ loading ? 'Генерація...' : 'Завантажити .xlsx' }}
      </button>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'
import TabBar from '@/components/TabBar.vue'

const dateFrom = ref('')
const dateTo = ref('')
const storeId = ref(null)
const loading = ref(false)
const stores = ref([])

onMounted(async () => {
  const { data } = await api.get('/stores')
  stores.value = data
})

async function downloadReport() {
  loading.value = true
  try {
    // Спочатку генеруємо звіт на сервері
    const { data } = await api.post('/reports/export', {
      date_from: dateFrom.value,
      date_to: dateTo.value,
      store_id: storeId.value,
    })

    // Бекенд повертає { filename } — відкриваємо завантаження через Telegram
    const filename = data?.filename
    if (!filename) throw new Error('Не вдалось створити звіт')

    const fileUrl = `${window.location.origin}/api/v1/admin/reports/archive/${filename}`
    openFileUrl(fileUrl, filename)
  } catch (e) {
    alert(e.response?.data?.detail || 'Помилка генерації звіту')
  } finally {
    loading.value = false
  }
}

function openFileUrl(url, filename) {
  const tg = window.Telegram?.WebApp
  if (tg?.openLink) {
    // Telegram WebApp: відкриваємо в системному браузері де завантаження працює
    tg.openLink(url)
  } else {
    // Фолбек для браузера
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
  }
}
</script>
