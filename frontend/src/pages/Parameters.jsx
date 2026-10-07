import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Satellite, RefreshCw, Sprout } from 'lucide-react'
import WeatherPanel from '../components/WeatherPanel'
import { useStore } from '../store/useStore'
import { useWeather } from '../hooks/useWeather'

function safeParseFloat(value, fallback) {
  const parsed = parseFloat(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

export default function Parameters() {
  const navigate = useNavigate()
  const { location, envData, farmParams, setFarmParams } = useStore()
  const { fetchAll, loading }  = useWeather()
  const [fetched, setFetched]  = useState(false)

  useEffect(() => {
    if (location && !fetched) {
      fetchAll(location.lat, location.lng).then(() => setFetched(true)).catch(() => setFetched(true))
    }
  }, [location])

  if (!location) {
    return (
      <div className="text-center py-20">
        <p className="text-ink-soft mb-4">No location selected yet.</p>
        <button onClick={() => navigate('/location')} className="px-6 py-2 bg-forest text-white rounded-xl">
          Select a location
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-forest text-white p-6 rounded-2xl">
        <h2 className="font-display text-2xl font-semibold mb-1">Farm parameters</h2>
        <p className="text-forest-soft">Environmental data fetched for {location.name}</p>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="bg-monsoon-soft border border-monsoon/20 rounded-xl p-6 flex items-center gap-3">
          <Satellite className="w-6 h-6 text-monsoon animate-spin" />
          <span className="text-monsoon font-medium">Fetching weather and climate data…</span>
        </div>
      )}

      {/* Weather cards */}
      {!loading && <WeatherPanel />}

      {/* Rainfall seasonality */}
      {!loading && (
        <div className="bg-primary-soft border border-primary/20 rounded-xl p-4">
          <div className="font-semibold text-primary-dark mb-1">Peak rainfall months</div>
          <div className="flex gap-2">
            {envData.rainyMonths?.map(m => (
              <span key={m} className="px-3 py-1 bg-primary/15 text-primary-dark rounded-full text-sm font-medium">
                {m}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Farm parameter form */}
      <div className="bg-surface rounded-xl border border-sand p-6">
        <h3 className="font-semibold text-lg mb-4 text-ink">Farm details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Soil type */}
          <div>
            <label className="block text-sm font-medium mb-1 text-ink">Soil type</label>
            <select
              value={farmParams.soilType}
              onChange={e => setFarmParams({ soilType: e.target.value })}
              className="w-full px-3 py-2 border border-sand rounded-xl focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white"
            >
              {['Loamy', 'Clay', 'Sandy', 'Black Soil', 'Sandy Loam', 'Clay Loam'].map(t => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </div>

          {/* Soil pH */}
          <div>
            <label className="block text-sm font-medium mb-1 text-ink">
              Soil pH <span className="text-ink-soft font-normal">(5.0 – 8.5)</span>
            </label>
            <input
              type="number"
              step="0.1" min="5.0" max="8.5"
              value={farmParams.soilPh}
              onChange={e => setFarmParams({ soilPh: safeParseFloat(e.target.value, farmParams.soilPh) })}
              className="w-full px-3 py-2 border border-sand rounded-xl focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white"
            />
          </div>

          {/* Land area */}
          <div>
            <label className="block text-sm font-medium mb-1 text-ink">Land area (hectares)</label>
            <input
              type="number"
              step="0.1" min="0.1"
              value={farmParams.landArea}
              onChange={e => setFarmParams({ landArea: safeParseFloat(e.target.value, farmParams.landArea) })}
              className="w-full px-3 py-2 border border-sand rounded-xl focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white"
            />
          </div>

          {/* Season */}
          <div>
            <label className="block text-sm font-medium mb-1 text-ink">Growing season</label>
            <select
              value={farmParams.season}
              onChange={e => setFarmParams({ season: e.target.value })}
              className="w-full px-3 py-2 border border-sand rounded-xl focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white"
            >
              <option value="Kharif">Kharif (Jun – Oct)</option>
              <option value="Rabi">Rabi (Nov – Mar)</option>
              <option value="Summer">Summer (Apr – Jun)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col md:flex-row gap-3">
        <button
          onClick={() => fetchAll(location.lat, location.lng)}
          className="flex items-center justify-center gap-2 px-5 py-3 bg-monsoon text-white rounded-xl hover:opacity-90 font-medium transition-opacity"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh data
        </button>
        <button
          onClick={() => navigate('/recommendations')}
          className="flex-1 flex items-center justify-center gap-2 py-4 bg-primary text-white rounded-xl hover:bg-primary-dark font-bold text-lg transition-colors"
        >
          <Sprout className="w-5 h-5" />
          Get crop recommendations →
        </button>
      </div>
    </div>
  )
}
