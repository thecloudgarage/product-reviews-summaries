import React, { useEffect, useState } from 'react'
import { api } from './api'

const styles = {
  page: { fontFamily: 'Arial, sans-serif', padding: 24, color: '#1f2937' },
  grid: { display: 'grid', gridTemplateColumns: '320px 1fr 1fr', gap: 24, alignItems: 'start' },
  card: { border: '1px solid #e5e7eb', borderRadius: 10, padding: 16, background: '#fff' },
  heading: { marginTop: 0 },
  list: { paddingLeft: 18 },
  link: { color: '#2563eb', cursor: 'pointer', textDecoration: 'underline' },
  pre: { background: '#111827', color: '#f9fafb', padding: 12, borderRadius: 8, overflowX: 'auto', whiteSpace: 'pre-wrap' },
  badge: { display: 'inline-block', padding: '4px 8px', background: '#eff6ff', color: '#1d4ed8', borderRadius: 999, fontSize: 12, marginLeft: 8 },
}

export default function App() {
  const [top3, setTop3] = useState({})
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [products, setProducts] = useState([])
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [productDetails, setProductDetails] = useState(null)
  const [reviews, setReviews] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadTop3()
  }, [])

  async function loadTop3() {
    try {
      setLoading(true)
      const data = await api.getTop3()
      setTop3(data)
      const firstCategory = Object.keys(data)[0]
      if (firstCategory) {
        await selectCategory(firstCategory)
      }
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  async function selectCategory(category) {
    try {
      setSelectedCategory(category)
      setSelectedProduct(null)
      setProductDetails(null)
      setReviews([])
      setSummary(null)
      const items = await api.getProducts(category)
      setProducts(items)
    } catch (e) {
      setError(String(e))
    }
  }

  async function selectProduct(productId) {
    try {
      setSelectedProduct(productId)
      const [product, reviewRows, summaryRow] = await Promise.all([
        api.getProduct(productId),
        api.getReviews(productId),
        api.getSummary(productId)
      ])
      setProductDetails(product)
      setReviews(reviewRows)
      setSummary(summaryRow)
    } catch (e) {
      setError(String(e))
    }
  }

  return (
    <div style={styles.page}>
      <h1 style={styles.heading}>Product Review Dashboard</h1>
      {loading && <div>Loading…</div>}
      {error && <div style={{ color: 'red', marginBottom: 12 }}>{error}</div>}

      <div style={styles.grid}>
        <section style={styles.card}>
          <h2 style={styles.heading}>Top 3 by Category</h2>
          {Object.entries(top3).map(([category, items]) => (
            <div key={category} style={{ marginBottom: 16 }}>
              <div>
                <span
                  style={styles.link}
                  onClick={() => selectCategory(category)}
                >
                  {category}
                </span>
                {selectedCategory === category && <span style={styles.badge}>selected</span>}
              </div>
              <ul style={styles.list}>
                {items.map(item => (
                  <li key={item.product_id}>
                    {item.product_id} — score {Number(item.score).toFixed(2)}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </section>

        <section style={styles.card}>
          <h2 style={styles.heading}>Products {selectedCategory ? `in ${selectedCategory}` : ''}</h2>
          <ul style={styles.list}>
            {products.map(product => (
              <li key={product.product_id}>
                <span style={styles.link} onClick={() => selectProduct(product.product_id)}>
                  {product.product_id}
                </span>
                {' '}— {product.name} — avg {Number(product.avg_rating || 0).toFixed(2)} — count {product.rating_count || 0}
              </li>
            ))}
          </ul>
        </section>

        <section style={styles.card}>
          <h2 style={styles.heading}>Product Detail {selectedProduct ? `for ${selectedProduct}` : ''}</h2>
          {productDetails && (
            <>
              <h3>Product</h3>
              <pre style={styles.pre}>{JSON.stringify(productDetails, null, 2)}</pre>
            </>
          )}

          {summary && (
            <>
              <h3>Summary</h3>
              <pre style={styles.pre}>{JSON.stringify(summary, null, 2)}</pre>
            </>
          )}

          {reviews.length > 0 && (
            <>
              <h3>Raw Reviews</h3>
              <pre style={styles.pre}>{JSON.stringify(reviews, null, 2)}</pre>
            </>
          )}
        </section>
      </div>
    </div>
  )
}
