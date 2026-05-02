<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4 border-b border-tg-hint/10">
      <h1 class="text-xl font-bold">🗄️ Архів звітів</h1>
    </div>

    <!-- Список -->
    <div class="p-4 space-y-2">
      <div v-if="files.length === 0" class="text-center text-tg-hint py-8">
        Архів порожній
      </div>
      
      <div v-for="file in files" :key="file.filename" class="bg-tg-secondary rounded-xl p-4 flex justify-between items-center">
        <div class="overflow-hidden mr-2">
          <p class="font-medium text-sm truncate" :title="file.filename">{{ file.filename }}</p>
          <p class="text-xs text-tg-hint">
            {{ formatDate(file.created_at) }} · {{ formatSize(file.size) }}
          </p>
        </div>
        <button @click="downloadFile(file.filename)" class="px-4 py-2 bg-tg-button text-tg-button-text rounded-lg text-xs font-medium shrink-0">
          Завантажити
        </button>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAdminReportsArchive, downloadAdminReport } from '@/api/reports'
import TabBar from '@/components/TabBar.vue'

const files = ref([])

onMounted(async () => {
  const { data } = await getAdminReportsArchive()
  files.value = data
})

function formatSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatDate(dateString) {
  const d = new Date(dateString)
  return d.toLocaleString('uk-UA', { 
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

async function downloadFile(filename) {
  try {
    const { data } = await downloadAdminReport(filename)
    
    // Створення посилання для завантаження Blob
    const url = window.URL.createObjectURL(new Blob([data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    alert('Помилка при завантаженні файлу')
    console.error(err)
  }
}
</script>
