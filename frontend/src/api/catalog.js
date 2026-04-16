import api from './index.js'

export const getCatalog = () => api.get('/catalog')
export const getStores = () => api.get('/stores')
