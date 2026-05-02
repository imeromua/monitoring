import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { verifyAuth } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(sessionStorage.getItem('access_token') || null)
  const role = ref(sessionStorage.getItem('user_role') || null)
  const isInitialized = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => role.value === 'admin')

  async function init() {
    const tg = window.Telegram?.WebApp
    if (!tg?.initData) {
      isInitialized.value = true
      return
    }

    try {
      const { data } = await verifyAuth(tg.initData)
      token.value = data.access_token
      role.value = data.role
      sessionStorage.setItem('access_token', data.access_token)
      sessionStorage.setItem('user_role', data.role)
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
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('user_role')
  }

  return { token, role, isAuthenticated, isAdmin, isInitialized, init, logout }
})
