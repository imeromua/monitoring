import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import { verifyAuth } from '@/api/auth'

vi.mock('@/api/auth', () => ({
  verifyAuth: vi.fn()
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('initializes with default values', () => {
    const auth = useAuthStore()
    expect(auth.token).toBeNull()
    expect(auth.role).toBeNull()
    expect(auth.isAuthenticated).toBe(false)
  })

  it('logs out correctly', () => {
    const auth = useAuthStore()
    auth.token = 'fake_token'
    auth.role = 'admin'
    
    auth.logout()
    
    expect(auth.token).toBeNull()
    expect(auth.role).toBeNull()
    expect(localStorage.getItem('access_token')).toBeNull()
  })

  it('authenticates successfully on init', async () => {
    // Mock Telegram WebApp
    global.window.Telegram = {
      WebApp: { initData: 'valid_data' }
    }
    
    verifyAuth.mockResolvedValue({
      data: { access_token: 'new_token', role: 'user' }
    })

    const auth = useAuthStore()
    await auth.init()

    expect(auth.token).toBe('new_token')
    expect(auth.role).toBe('user')
    expect(localStorage.getItem('access_token')).toBe('new_token')
  })
})
