import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { getMarketPrices } from '../services/api'

const TOP_CROPS = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Soybean', 'Mustard', 'Chickpea', 'Groundnut']

export default function MarketPriceBar() {
  const [prices, setPrices] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getMarketPrices(TOP_CROPS)
      .then(res => setPrices(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="bg-forest-dark text-forest-soft py-2 px-4 text-sm overflow-hidden">
        <span className="opacity-70">Loading market prices...</span>
      </div>
    )
  }

  const TrendIcon = ({ trend }) => {
    if (trend === 'up')   return <TrendingUp className="w-3 h-3 text-primary-soft" />
    if (trend === 'down') return <TrendingDown className="w-3 h-3 text-clay-soft" />
    return <Minus className="w-3 h-3 text-forest-soft" />
  }

  const items = Object.entries(prices)
  const row = (suffix) => items.map(([crop, data]) => (
    <div key={crop + suffix} className="flex items-center gap-1.5 shrink-0 mr-8">
      <span className="text-forest-soft text-xs">{crop}</span>
      <span className="font-semibold">₹{data.price?.toLocaleString()}</span>
      <TrendIcon trend={data.trend} />
      <span className="text-forest-soft text-xs">{data.unit}</span>
    </div>
  ))

  return (
    <div className="marquee bg-forest-dark text-white py-2 overflow-hidden text-sm">
      <div className="marquee-track">
        <span className="font-medium text-marigold text-xs shrink-0 mr-8 self-center">Market prices</span>
        {row('a')}
        <span className="font-medium text-marigold text-xs shrink-0 mr-8 self-center">Market prices</span>
        {row('b')}
      </div>
    </div>
  )
}
