<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4 border-b border-tg-hint/10">
      <h1 class="text-xl font-bold">🏪 Магазини</h1>
    </div>

    <div class="p-4 border-b border-tg-hint/10 space-y-2">
      <input v-model="newName" placeholder="Назва" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none" />
      <input v-model="newAddress" placeholder="Адреса" class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none" />
      <button @click="addStore" class="w-full py-3 rounded-xl bg-tg-button text-tg-button-text font-medium active:opacity-70">
        + Додати
      </button>
    </div>

    <div class="p-4 space-y-2">
      <div v-for="store in stores" :key="store.id" class="flex items-center justify-between bg-tg-secondary rounded-xl px-4 py-3">
        <div>
          <div class="font-medium text-sm">{{ store.name }}</div>
          <div class="text-xs text-tg-hint">{{ store.address }}</div>
        </div>
        <button @click="archiveStore(store)" class="text-xs px-3 py-1.5 rounded-lg bg-tg-bg text-tg-hint active:opacity-70">
          Архів
        </button>
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

onMounted(async () => {
  const { data } = await api.get('/stores')
  stores.value = data
})

async function addStore() {
  if (!newName.value) return
  await api.post('/admin/stores', null, { params: { name: newName.value, address: newAddress.value } })
  const { data } = await api.get('/stores')
  stores.value = data
  newName.value = ''
  newAddress.value = ''
}

async function archiveStore(store) {
  await api.patch(`/admin/stores/${store.id}/archive`)
  stores.value = stores.value.filter((s) => s.id !== store.id)
}
</script>
