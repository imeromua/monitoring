import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createSession, addResult, completeSession } from '@/api/sessions'

const OFFLINE_KEY = 'offline_queue'
const SESSION_KEY = 'current_session'

export const useSessionStore = defineStore('session', () => {
  const currentSession = ref(JSON.parse(localStorage.getItem(SESSION_KEY) || 'null'))
  const offlineQueue = ref(JSON.parse(localStorage.getItem(OFFLINE_KEY) || '[]'))

  async function startSession(storeId) {
    const { data } = await createSession(storeId)
    currentSession.value = data
    localStorage.setItem(SESSION_KEY, JSON.stringify(data))
    return data
  }

  async function saveResult(payload) {
    if (!currentSession.value) return
    try {
      await addResult(currentSession.value.id, payload)
    } catch {
      // Офлайн: додаємо в чергу
      offlineQueue.value.push({ sessionId: currentSession.value.id, payload })
      localStorage.setItem(OFFLINE_KEY, JSON.stringify(offlineQueue.value))
    }
  }

  async function syncOfflineQueue() {
    if (!offlineQueue.value.length) return
    const remaining = []
    for (const item of offlineQueue.value) {
      try {
        await addResult(item.sessionId, item.payload)
      } catch {
        remaining.push(item)
      }
    }
    offlineQueue.value = remaining
    localStorage.setItem(OFFLINE_KEY, JSON.stringify(remaining))
  }

  async function finish() {
    if (!currentSession.value) return
    await syncOfflineQueue()
    await completeSession(currentSession.value.id)
    currentSession.value = null
    localStorage.removeItem(SESSION_KEY)
  }

  return { currentSession, offlineQueue, startSession, saveResult, syncOfflineQueue, finish }
})
