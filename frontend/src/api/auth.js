import api from './index.js'

export const verifyAuth = (initData) =>
  api.post('/auth/verify', { init_data: initData })
