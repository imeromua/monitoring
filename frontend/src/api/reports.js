import api from './index.js'

export const exportReport = (payload) =>
  api.post('/reports/export', payload, { responseType: 'blob' })

// Admin Reports Archive
export const getAdminReportsArchive = () => api.get('/admin/reports/archive')
export const downloadAdminReport = (filename) => 
  api.get(`/admin/reports/archive/${filename}`, { responseType: 'blob' })
