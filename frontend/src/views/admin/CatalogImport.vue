<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4 border-b border-tg-hint/10">
      <h1 class="text-xl font-bold">📦 Імпорт каталогу</h1>
    </div>

    <div class="p-4 space-y-4">
      <p class="text-sm text-tg-hint">
        Завантажте .xlsx файл з колонками: <strong>article_id, name, category_id</strong> (та необов'язково <strong>weight_label</strong>).
        Відсутні позиції будуть архівовані.
      </p>

      <!-- Зона завантаження -->
      <label
        class="flex flex-col items-center justify-center w-full h-32 rounded-2xl border-2 border-dashed border-tg-hint/30 cursor-pointer bg-tg-secondary active:opacity-70 transition-opacity"
      >
        <span class="text-3xl mb-1">📂</span>
        <span class="text-sm text-tg-hint">{{ file ? file.name : 'Оберіть .xlsx файл' }}</span>
        <input type="file" accept=".xlsx" class="hidden" @change="onFileChange" />
      </label>

      <button
        @click="upload"
        :disabled="!file || loading"
        class="w-full py-4 rounded-2xl bg-tg-button text-tg-button-text font-bold active:opacity-70 disabled:opacity-40 transition-opacity"
      >
        {{ loading ? 'Завантаження...' : 'Завантажити каталог' }}
      </button>

      <!-- Результат -->
      <div v-if="result" class="rounded-2xl p-4 text-sm"
        :class="result.success ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'"
      >
        {{ result.message }}
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/index.js'
import TabBar from '@/components/TabBar.vue'

const file = ref(null)
const loading = ref(false)
const result = ref(null)

function onFileChange(e) {
  file.value = e.target.files[0] || null
  result.value = null
}

async function upload() {
  if (!file.value) return
  loading.value = true
  result.value = null
  try {
    const form = new FormData()
    form.append('file', file.value)
    const { data } = await api.post('/admin/catalog/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    result.value = {
      success: true,
      message: `✅ Успішно! Оновлено / додано: ${data.upserted} позицій`,
    }
    file.value = null
  } catch (err) {
    const detail = err.response?.data?.detail || 'Помилка завантаження'
    result.value = { success: false, message: `❌ ${detail}` }
  } finally {
    loading.value = false
  }
}
</script>
