import api from './index.js'

export const createSession = (storeId) =>
  api.post('/sessions', { store_id: storeId })

export const addResult = (sessionId, payload) =>
  api.post(`/sessions/${sessionId}/results`, payload)

export const completeSession = (sessionId) =>
  api.patch(`/sessions/${sessionId}/complete`)
