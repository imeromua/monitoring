import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { watch } from 'vue'

const routes = [
  {
    path: '/',
    redirect: '/select-store',
  },
  {
    path: '/select-store',
    name: 'SelectStore',
    component: () => import('@/views/SelectStore.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/catalog',
    name: 'Catalog',
    component: () => import('@/views/Catalog.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/carousel/:categoryId',
    name: 'Carousel',
    component: () => import('@/views/Carousel.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/admin/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/unauthorized',
    name: 'Unauthorized',
    component: () => import('@/views/Unauthorized.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  
  // Чекаємо ініціалізації авторизації (Telegram API)
  if (!auth.isInitialized) {
    await new Promise((resolve) => {
      const unwatch = watch(() => auth.isInitialized, (val) => {
        if (val) {
          unwatch()
          resolve()
        }
      })
    })
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'Unauthorized' }
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: 'Home' }
  }
})

export default router
