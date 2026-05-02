import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCatalog, getStores } from '@/api/catalog'

const DB_NAME = 'store-check-db'
const STORE_NAME = 'catalog'

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1)
    req.onupgradeneeded = (e) => {
      e.target.result.createObjectStore(STORE_NAME)
    }
    req.onsuccess = (e) => resolve(e.target.result)
    req.onerror = reject
  })
}

async function saveToIDB(key, value) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    tx.objectStore(STORE_NAME).put(value, key)
    tx.oncomplete = resolve
    tx.onerror = reject
  })
}

async function loadFromIDB(key) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly')
    const req = tx.objectStore(STORE_NAME).get(key)
    req.onsuccess = (e) => resolve(e.target.result)
    req.onerror = reject
  })
}

export const useCatalogStore = defineStore('catalog', () => {
  const categories = ref([])
  const products = ref([])
  const stores = ref([])
  const loaded = ref(false)

  const productsByCategory = computed(() => {
    const map = {}
    for (const p of products.value) {
      if (!map[p.category_id]) map[p.category_id] = []
      map[p.category_id].push(p)
    }
    return map
  })

  function getSubcategoryIds(catId) {
    let ids = [catId]
    const children = categories.value.filter(c => c.parent_id === catId).map(c => c.id)
    for (const childId of children) {
      ids = ids.concat(getSubcategoryIds(childId))
    }
    return ids
  }

  function getTotalProductsCount(catId) {
    const ids = getSubcategoryIds(catId)
    let count = 0
    for (const id of ids) {
      count += (productsByCategory.value[id] || []).length
    }
    return count
  }

  async function load(force = false) {
    if (loaded.value && !force) return
    try {
      const [catalogRes, storesRes] = await Promise.all([getCatalog(), getStores()])
      categories.value = catalogRes.data.categories
      products.value = catalogRes.data.products
      stores.value = storesRes.data
      loaded.value = true
      // Зберігаємо в IndexedDB для офлайн-режиму
      await saveToIDB('catalog', { categories: categories.value, products: products.value })
      await saveToIDB('stores', stores.value)
    } catch {
      // Немає зв’язку — завантажуємо з IndexedDB
      const cached = await loadFromIDB('catalog')
      const cachedStores = await loadFromIDB('stores')
      if (cached) {
        categories.value = cached.categories
        products.value = cached.products
      }
      if (cachedStores) stores.value = cachedStores
    }
  }

  return { categories, products, stores, productsByCategory, getTotalProductsCount, load }
})
