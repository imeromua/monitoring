import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { verifyAuth } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const role = ref(localStorage.getItem('user_role') || null)
  const isInitialized = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => role.value === 'admin')

  async function init() {
    const tg = window.Telegram?.WebApp
    let initData = tg?.initData
    if (initData) {
      localStorage.setItem('init_data', initData)
    } else {
      initData = localStorage.getItem('init_data')
    }

    if (!initData) {
      isInitialized.value = true
      return
    }

    try {
      const { data } = await verifyAuth(initData)
      token.value = data.access_token
      role.value = data.role
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('user_role', data.role)
    } catch {
      token.value = null
      role.value = null
    } finally {
      isInitialized.value = true
    }
  }

  function logout() {
    token.value = null
    role.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_role')
    localStorage.removeItem('init_data')
  }

  return { token, role, isAuthenticated, isAdmin, isInitialized, init, logout }
})
