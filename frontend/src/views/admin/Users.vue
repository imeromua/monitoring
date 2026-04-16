<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4 border-b border-tg-hint/10">
      <h1 class="text-xl font-bold">👥 Персонал</h1>
    </div>

    <!-- Додати співробітника -->
    <div class="p-4 border-b border-tg-hint/10 space-y-2">
      <input
        v-model="newTelegramId"
        type="number"
        placeholder="Telegram ID"
        class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none"
      />
      <input
        v-model="newName"
        type="text"
        placeholder="Ім'я та прізвище"
        class="w-full bg-tg-secondary rounded-xl px-4 py-3 text-sm outline-none"
      />
      <button
        @click="addUser"
        class="w-full py-3 rounded-xl bg-tg-button text-tg-button-text font-medium active:opacity-70"
      >
        + Додати
      </button>
    </div>

    <!-- Список -->
    <div class="p-4 space-y-2">
      <div
        v-for="user in users"
        :key="user.id"
        class="flex items-center justify-between bg-tg-secondary rounded-xl px-4 py-3"
      >
        <div>
          <div class="font-medium text-sm">{{ user.full_name }}</div>
          <div class="text-xs text-tg-hint">{{ user.telegram_id }} · {{ user.role }}</div>
        </div>
        <button
          @click="toggleBlock(user)"
          :class="[
            'text-xs px-3 py-1.5 rounded-lg font-medium active:opacity-70',
            user.is_active ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'
          ]"
        >
          {{ user.is_active ? 'Блок' : 'Розблок' }}
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

const users = ref([])
const newTelegramId = ref('')
const newName = ref('')

onMounted(async () => {
  const { data } = await api.get('/admin/users')
  users.value = data
})

async function addUser() {
  if (!newTelegramId.value || !newName.value) return
  await api.post('/admin/users', null, {
    params: { telegram_id: newTelegramId.value, full_name: newName.value }
  })
  const { data } = await api.get('/admin/users')
  users.value = data
  newTelegramId.value = ''
  newName.value = ''
}

async function toggleBlock(user) {
  await api.patch(`/admin/users/${user.id}`, null, {
    params: { is_active: !user.is_active }
  })
  user.is_active = !user.is_active
}
</script>
