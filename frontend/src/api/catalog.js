import api from './index.js'

export const getCatalog = () => api.get('/catalog')
export const getStores = () => api.get('/stores')

// Admin Catalog (Products)
export const getAdminProducts = () => api.get('/admin/catalog/products')
export const createAdminProduct = (data) => api.post('/admin/catalog/products', data)
export const updateAdminProduct = (id, data) => api.put(`/admin/catalog/products/${id}`, data)
export const deleteAdminProduct = (id) => api.delete(`/admin/catalog/products/${id}`)

// Admin Catalog (Categories)
export const getAdminCategories = () => api.get('/admin/catalog/categories')
export const createAdminCategory = (data) => api.post('/admin/catalog/categories', data)
export const updateAdminCategory = (id, data) => api.put(`/admin/catalog/categories/${id}`, data)
export const deleteAdminCategory = (id) => api.delete(`/admin/catalog/categories/${id}`)
