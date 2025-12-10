import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowLeft, ExternalLink } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts'
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart'

function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [priceHistory, setPriceHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const chartConfig = {
    price: {
      label: "Price",
      color: "hsl(var(--chart-1))",
    },
  }

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)

      try {
        // Fetch product details
        const productResponse = await fetch(`http://localhost:8000/api/v1/products/${id}`)
        if (!productResponse.ok) {
          throw new Error(`Error: ${productResponse.status}`)
        }
        const productData = await productResponse.json()
        console.log('Product data:', productData)
        setProduct(productData)

        // Fetch price history
        const historyResponse = await fetch(`http://localhost:8000/api/v1/products/${id}/history?limit=100`)
        if (historyResponse.ok) {
          const historyData = await historyResponse.json()
          console.log('Price history:', historyData)
          // Reverse the array so oldest is on the left, newest on the right
          setPriceHistory((historyData.history || []).reverse())
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen w-full p-8">
        <div className="w-full mx-auto px-4">
          <p className="text-center text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen w-full p-8">
        <div className="w-full mx-auto px-4">
          <Button variant="outline" onClick={() => navigate(-1)} className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Search
          </Button>
          <div className="p-4 text-destructive border border-destructive rounded-md bg-destructive/10">
            Error: {error}
          </div>
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="min-h-screen w-full p-8">
        <div className="w-full mx-auto px-4">
          <Button variant="outline" onClick={() => navigate(-1)} className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Search
          </Button>
          <p className="text-center text-muted-foreground">Product not found</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen w-full p-8">
      <div className="max-w-4xl mx-auto px-4">
        <Button variant="outline" onClick={() => navigate(-1)} className="mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Search
        </Button>

        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">{product.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-6">
              {product.image && (
                <div className="flex-shrink-0">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-80 h-auto rounded-lg border"
                  />
                </div>
              )}

              <div className="flex-1 space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Current Price</p>
                    <p className="font-medium text-lg">
                      {product.current_price ? (
                        <>
                          <span>{new Intl.NumberFormat('mk-MK', { minimumFractionDigits: 0 }).format(product.current_price)}</span> <span className="text-sm">ден</span>
                        </>
                      ) : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Store</p>
                    <p className="font-medium">{product.store_name || product.store_id}</p>
                  </div>
                  {product.category && (
                    <div>
                      <p className="text-sm text-muted-foreground">Category</p>
                      <p className="font-medium">{product.category}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm text-muted-foreground">Last Scraped</p>
                    <p className="font-medium">
                      {product.last_price_update ? new Date(product.last_price_update).toLocaleString() : 'N/A'}
                    </p>
                  </div>
                </div>

                <div className="pt-4">
                  <a
                    href={product.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-primary hover:underline font-medium"
                  >
                    View Product <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {priceHistory.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Price History</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="min-h-[400px] w-full">
                <LineChart
                  data={priceHistory}
                  margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="scraped_at"
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    tickLine={false}
                    axisLine={false}
                    tickMargin={8}
                  />
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    tickMargin={8}
                    tickFormatter={(value) => `${value.toFixed(2)}`}
                  />
                  <ChartTooltip
                    content={<ChartTooltipContent />}
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                  />
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke="var(--color-price)"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ChartContainer>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default ProductDetail
