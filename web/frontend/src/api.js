const API_BASE = import.meta.env.VITE_API_BASE || ''

async function getJson(path) {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  return response.json()
}

export const api = {
  getTop3: () => getJson('/api/categories/top3'),
  getProducts: (category) => getJson(`/api/categories/${encodeURIComponent(category)}/products`),
  getProduct: (productId) => getJson(`/api/products/${productId}`),
  getReviews: (productId) => getJson(`/api/products/${productId}/reviews`),
  getSummary: (productId) => getJson(`/api/products/${productId}/summary`)
}
