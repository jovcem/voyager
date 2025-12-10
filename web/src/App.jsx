import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Search, ExternalLink, Sun, Moon, X } from 'lucide-react'

function App() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [searchTerm, setSearchTerm] = useState(searchParams.get('q') || '')
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isDark, setIsDark] = useState(false)
  const [selectedProductId, setSelectedProductId] = useState(
    sessionStorage.getItem('lastViewedProduct')
  )

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

  const performSearch = async (query) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/products/search?q=${encodeURIComponent(query)}&limit=50`
      )

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`)
      }

      const data = await response.json()
      setProducts(data.products || [])
    } catch (err) {
      setError(err.message)
      setProducts([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const query = searchParams.get('q')
    if (query) {
      setSearchTerm(query)
      performSearch(query)
    }
  }, [searchParams])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchTerm.trim()) return

    // Clear selection when doing a new search
    setSelectedProductId(null)
    sessionStorage.removeItem('lastViewedProduct')
    setSearchParams({ q: searchTerm })
  }

  const handleProductClick = (productId) => {
    sessionStorage.setItem('lastViewedProduct', productId)
    setSelectedProductId(productId)
    navigate(`/product/${productId}`)
  }

  const handleClear = () => {
    setSearchTerm('')
    setProducts([])
    setSelectedProductId(null)
    sessionStorage.removeItem('lastViewedProduct')
    setSearchParams({})
  }

  return (
    <div className="min-h-screen w-full p-8">
      <div className="w-full mx-auto px-4">
        <div className="flex justify-end mb-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsDark(!isDark)}
            className="gap-1"
          >
            {isDark ? (
              <Sun className="h-3 w-3" />
            ) : (
              <Moon className="h-3 w-3" />
            )}
          </Button>
        </div>

        <form onSubmit={handleSearch} className="flex gap-3 max-w-2xl mx-auto mb-8">
          <Input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search products (e.g., RAM)"
            className="flex-1"
          />
          <Button type="submit" disabled={loading} className="gap-2 h-10">
            <Search className="h-4 w-4" />
            {loading ? 'Searching...' : 'Search'}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={handleClear}
            className="gap-2 h-10"
          >
            <X className="h-4 w-4" />
            Clear
          </Button>
        </form>

        {error && (
          <div className="max-w-2xl mx-auto mb-8 p-4 text-destructive border border-destructive rounded-md bg-destructive/10">
            Error: {error}
          </div>
        )}

        {!loading && products.length === 0 && searchParams.get('q') && (
          <div className="max-w-2xl mx-auto mb-8 p-8 text-center text-muted-foreground border border-muted rounded-md">
            <p className="text-lg">No products found for "{searchParams.get('q')}"</p>
            <p className="text-sm mt-2">Try a different search term</p>
          </div>
        )}

        {products.length > 0 && (
          <div>
            <p className="text-center text-muted-foreground mb-6">
              Found {products.length} products
            </p>
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-muted">
                  <tr className="border-b">
                    <th className="text-left p-4 font-semibold">Product</th>
                    <th className="text-left p-4 font-semibold">Store</th>
                    <th className="text-right p-4 font-semibold">Price</th>
                    <th className="text-center p-4 font-semibold">Link</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((product) => {
                    const isSelected = selectedProductId === String(product.id)
                    return (
                      <tr
                        key={product.id}
                        onClick={() => handleProductClick(product.id)}
                        className={`border-b hover:bg-muted/50 transition-colors cursor-pointer ${
                          isSelected ? 'bg-accent/30 border-l-4 border-l-primary' : ''
                        }`}
                      >
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <div className="font-medium">{product.name}</div>
                          {product.category && (
                            <Badge variant="outline">{product.category}</Badge>
                          )}
                        </div>
                      </td>
                      <td className="p-4 text-muted-foreground">{product.store}</td>
                      <td className="p-4 text-right">
                        <span className="font-mono">{new Intl.NumberFormat('mk-MK', { minimumFractionDigits: 0 }).format(product.price)}</span> <span className="text-sm">ден</span>
                      </td>
                      <td className="p-4 text-center">
                        <a
                          href={product.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="inline-flex items-center gap-2 text-primary hover:underline"
                        >
                          View <ExternalLink className="h-4 w-4" />
                        </a>
                      </td>
                    </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
