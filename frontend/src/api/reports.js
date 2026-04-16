import api from './index.js'

export const exportReport = (payload) =>
  api.post('/reports/export', payload, { responseType: 'blob' })
