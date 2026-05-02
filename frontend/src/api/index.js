import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// Додаємо JWT токен до кожного запиту (читаємо з sessionStorage — туди зберігає auth.js)
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('access_token')
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
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('user_role')
      window.location.href = '/unauthorized'
    }
    return Promise.reject(err)
  }
)

export default api
