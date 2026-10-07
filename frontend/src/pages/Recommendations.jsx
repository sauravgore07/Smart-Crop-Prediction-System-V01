import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Brain } from 'lucide-react'
import CropCard from '../components/CropCard'
import { useRecommendations } from '../hooks/useRecommendations'
import { useStore } from '../store/useStore'
import { getAllCrops } from '../services/api'

function normalize(str) {
  return (str || '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ')
}

function normalizeCropName(name) {
  return name
    .toLowerCase()
    .replace(/\(.*?\)/g, '') // remove brackets
    .trim()
}

function findCropByName(allCrops, name) {

  const normalized = normalizeCropName(name)

  return allCrops.find(crop => {

    const cropName = normalizeCropName(crop.name)

    // direct match
    if (cropName === normalized) {
      return true
    }

    // regional aliases
    const aliases = {
      'jowar': 'sorghum',
      'bajra': 'pearl millet',
      'makka': 'maize',
      'paddy': 'rice',
    }

    if (
      aliases[normalized] &&
      cropName === aliases[normalized]
    ) {
      return true
    }

    return false
  }) || null
}

const FALLBACK_CROP = {
  scientificName: '',
  category: 'Unknown',
  image: '🌱',
  duration: '—',
  yield: '—',
  investment: '—',
  season: [],
  requirements: {},
  profitability: { costPerHectare: 0, revenuePerHectare: 0, profitPerHectare: 0, riskLevel: 'Unknown', marketDemand: 'Unknown', priceTrend: 'Unknown' },
  description: 'Detailed crop information is not available yet.',
  tips: [],
  rotation: {},
}

export default function Recommendations() {
  const navigate  = useNavigate()
  const { envData, farmParams } = useStore()
  const { crops, loading, error, fetchCrops } = useRecommendations()

  const [allCrops, setAllCrops]     = useState([])
  const [useML,    setUseML]        = useState(true)
  const [category, setCategory]     = useState('')
  const [season,   setSeason]       = useState('')
  const [risk,     setRisk]         = useState('')
  const [sortBy,   setSortBy]       = useState('suitability')

  // Load full crop list for filter labels
  useEffect(() => {
    getAllCrops().then(r => setAllCrops(r.data)).catch(() => {})
  }, [])

  // Fetch recommendations on mount and when ML toggle changes
  useEffect(() => { fetchCrops() }, [useML])

  // Apply filters + sort client-side to avoid extra API calls
  const displayed = crops
  .map(c => {
    const full = findCropByName(allCrops, c.crop)
    return {
      ...FALLBACK_CROP,
      ...full,
      ...c,
      name: c.crop,
      suitability: c.suitability
    }
  })
  .filter(c => {
    if (category && c.category !== category) return false

    if (season) {
      const s = c.season || []
      if (!s.includes(season) && !s.includes('Year-round')) return false
    }

    if (risk && c.profitability?.riskLevel !== risk) return false

    return true
  })
  .sort((a, b) => {
    if (sortBy === 'profitability') {
      return (
        (b.profitability?.profitPerHectare || 0) -
        (a.profitability?.profitPerHectare || 0)
      )
    }

    if (sortBy === 'duration') {
      return (a.duration || '').localeCompare(b.duration || '')
    }

    return b.suitability - a.suitability
  })
  .slice(0, 5)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-forest text-white p-6 rounded-2xl">
        <h2 className="font-display text-2xl font-semibold mb-1">Crop recommendations</h2>
        <p className="text-forest-soft">
          Based on {Math.round(envData.currentTemp)}°C · {envData.annualRainfall} mm/yr · {farmParams.soilType} soil · {farmParams.season}
        </p>
      </div>

      {/* Current conditions summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
        {[
          [`${Math.round(envData.currentTemp)}°C`,   'Temperature',  'bg-monsoon-soft'],
          [`${envData.annualRainfall} mm`,             'Annual rain',  'bg-forest-soft'],
          [envData.soilType || farmParams.soilType,   'Soil type',    'bg-primary-soft'],
          [farmParams.season,                          'Season',       'bg-clay-soft'],
        ].map(([val, label, bg]) => (
          <div key={label} className={`${bg} rounded-xl p-3`}>
            <div className="text-lg font-display font-semibold text-ink">{val}</div>
            <div className="text-xs text-ink-soft">{label}</div>
          </div>
        ))}
      </div>

      {/* Filters row */}
      <div className="bg-surface rounded-xl border border-sand p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-xs font-medium mb-1 text-ink-soft">Category</label>
          <select value={category} onChange={e => setCategory(e.target.value)}
            className="w-full px-3 py-2 border border-sand rounded-lg text-sm focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white">
            <option value="">All</option>
            {['Cereals','Pulses','Oilseeds','Cash Crops'].map(c => <option key={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium mb-1 text-ink-soft">Season</label>
          <select value={season} onChange={e => setSeason(e.target.value)}
            className="w-full px-3 py-2 border border-sand rounded-lg text-sm focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white">
            <option value="">All</option>
            {['Kharif','Rabi','Summer'].map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium mb-1 text-ink-soft">Risk</label>
          <select value={risk} onChange={e => setRisk(e.target.value)}
            className="w-full px-3 py-2 border border-sand rounded-lg text-sm focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white">
            <option value="">All</option>
            {['Low','Medium','High'].map(r => <option key={r}>{r}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium mb-1 text-ink-soft">Sort by</label>
          <select value={sortBy} onChange={e => setSortBy(e.target.value)}
            className="w-full px-3 py-2 border border-sand rounded-lg text-sm focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white">
            <option value="suitability">Suitability</option>
            <option value="profitability">Profitability</option>
            <option value="duration">Duration</option>
          </select>
        </div>
      </div>


      {/* Loading */}
      {loading && (
        <div className="text-center py-16 text-ink-soft">
          <div className="text-4xl mb-3 animate-pulse">🌱</div>
          <p>Analysing your farm conditions…</p>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="bg-clay-soft border border-clay/30 rounded-xl p-4 text-clay text-sm">
          Could not fetch recommendations: {error}. <button onClick={fetchCrops} className="underline">Retry</button>
        </div>
      )}

      {/* Results grid */}
      {!loading && displayed.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayed.map((crop, i) => (
            <CropCard key={crop.name} crop={crop} rank={i + 1} isML={useML} />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && displayed.length === 0 && !error && (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">🌱</div>
          <h3 className="text-lg font-semibold mb-2 text-ink">No crops match your filters</h3>
          <p className="text-ink-soft mb-4">Try clearing some filters or changing your location.</p>
          <button onClick={() => navigate('/location')} className="px-6 py-2 bg-forest text-white rounded-xl">
            Change location
          </button>
        </div>
      )}
    </div>
  )
}
