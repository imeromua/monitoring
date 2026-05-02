import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Обробка 403/401 — очищаємо токен і перенаправляємо
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 403 || err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_role')
      localStorage.removeItem('init_data')
      window.location.href = '/unauthorized'
    }
    return Promise.reject(err)
  }
)

export default api
