<template>
  <div class="flex flex-col min-h-screen pb-20">
    <div class="p-4 border-b border-tg-hint/10">
      <h1 class="text-xl font-bold">👥 Персонал</h1>
    </div>

    <!-- Адмін-меню -->
    <div class="p-4 grid grid-cols-2 gap-3 border-b border-tg-hint/10">
      <button
        v-for="item in adminMenu"
        :key="item.route"
        @click="router.push({ name: item.route })"
        class="flex flex-col items-center gap-1 py-4 rounded-2xl bg-tg-secondary text-sm font-medium active:opacity-70 transition-opacity"
        :class="{ 'ring-2 ring-tg-button': route.name === item.route }"
      >
        <span class="text-2xl">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </button>
    </div>

    <div class="p-4 space-y-3">
      <!-- Форма додавання -->
      <div class="bg-tg-secondary rounded-2xl p-4 space-y-2">
        <p class="text-sm font-medium">Додати співробітника</p>
        <input
          v-model="newUser.telegram_id"
          type="number"
          placeholder="Telegram ID"
          class="w-full bg-tg-bg rounded-xl px-4 py-3 text-sm outline-none"
        />
        <input
          v-model="newUser.full_name"
          type="text"
          placeholder="Повне ім'я"
          class="w-full bg-tg-bg rounded-xl px-4 py-3 text-sm outline-none"
        />
        <button
          @click="addUser"
          :disabled="!newUser.telegram_id || !newUser.full_name"
          class="w-full py-3 rounded-xl bg-tg-button text-tg-button-text text-sm font-bold disabled:opacity-40"
        >
          Додати
        </button>
      </div>

      <!-- Список -->
      <div
        v-for="user in users"
        :key="user.id"
        class="bg-tg-secondary rounded-2xl p-4 flex items-center justify-between"
      >
        <div>
          <p class="font-medium text-sm">{{ user.full_name }}</p>
          <p class="text-xs text-tg-hint">ID: {{ user.telegram_id }} · {{ user.role }}</p>
        </div>
        <button
          @click="toggleUser(user)"
          class="px-3 py-1.5 rounded-xl text-xs font-medium transition-colors"
          :class="user.is_active ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'"
        >
          {{ user.is_active ? 'Заблокувати' : 'Розблокувати' }}
        </button>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api/index.js'
import TabBar from '@/components/TabBar.vue'

const router = useRouter()
const route = useRoute()

const adminMenu = [
  { route: 'Admin',         icon: '👥', label: 'Персонал' },
  { route: 'AdminStores',   icon: '🏪', label: 'Магазини' },
  { route: 'AdminReports',  icon: '📊', label: 'Звіти' },
  { route: 'AdminCatalog',  icon: '📦', label: 'Каталог' },
]

const users = ref([])
const newUser = ref({ telegram_id: '', full_name: '' })

onMounted(async () => {
  const { data } = await api.get('/admin/users')
  users.value = data
})

async function addUser() {
  await api.post('/admin/users', newUser.value)
  newUser.value = { telegram_id: '', full_name: '' }
  const { data } = await api.get('/admin/users')
  users.value = data
}

async function toggleUser(user) {
  await api.patch(`/admin/users/${user.id}`, { is_active: !user.is_active })
  user.is_active = !user.is_active
}
</script>
