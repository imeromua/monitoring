import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createSession, addResult, completeSession } from '@/api/sessions'

const OFFLINE_KEY = 'offline_queue'

export const useSessionStore = defineStore('session', () => {
  const currentSession = ref(null)
  const offlineQueue = ref(JSON.parse(localStorage.getItem(OFFLINE_KEY) || '[]'))

  async function startSession(storeId) {
    const { data } = await createSession(storeId)
    currentSession.value = data
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
  }

  return { currentSession, offlineQueue, startSession, saveResult, syncOfflineQueue, finish }
})
