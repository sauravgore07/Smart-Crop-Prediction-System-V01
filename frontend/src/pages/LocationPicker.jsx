import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Navigation, MapPin, CheckCircle, Info } from 'lucide-react'
import MapView from '../components/MapView'
import { useStore } from '../store/useStore'

export default function LocationPicker() {
  const navigate   = useNavigate()
  const { location, setLocation } = useStore()

  const [query,    setQuery]    = useState('')
  const [searching,setSearching]= useState('')
  const [selected, setSelected] = useState(location)

  function handleSelect(loc) {
    setSelected(loc)
    setLocation(loc)
  }

  async function searchLocation() {
    if (!query.trim()) return
    setSearching(true)
    try {
      const res  = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
      )
      const data = await res.json()
      if (data.length) {
        handleSelect({
          lat:  parseFloat(data[0].lat),
          lng:  parseFloat(data[0].lon),
          name: data[0].display_name,
        })
      } else {
        alert('Location not found. Try a different search term.')
      }
    } catch {
      alert('Search failed. Check your connection.')
    } finally {
      setSearching(false)
    }
  }

  function useGPS() {
    if (!navigator.geolocation) return alert('Geolocation not supported.')
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude: lat, longitude: lng } = pos.coords
        const res  = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
        const data = await res.json().catch(() => ({}))
        handleSelect({ lat, lng, name: data.display_name || `${lat.toFixed(4)}, ${lng.toFixed(4)}` })
      },
      () => alert('Unable to get your location.')
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-forest text-white p-6 rounded-2xl">
        <h2 className="font-display text-2xl font-semibold mb-1">Select your farm location</h2>
        <p className="text-forest-soft">Click on the map or search for a city or village.</p>
      </div>

      {/* Search bar */}
      <div className="flex gap-2">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && searchLocation()}
          placeholder="Search city, village or address..."
          className="flex-1 px-4 py-3 border border-sand rounded-xl focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white"
        />
        <button
          onClick={searchLocation}
          disabled={searching}
          className="px-5 py-3 bg-forest text-white rounded-xl hover:bg-forest-dark font-medium flex items-center gap-2 transition-colors disabled:opacity-60"
        >
          <Search className="w-4 h-4" />
          {searching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Quick location buttons */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <button
          onClick={useGPS}
          className="flex items-center justify-center gap-2 py-3 bg-monsoon text-white rounded-xl hover:opacity-90 font-medium transition-opacity"
        >
          <Navigation className="w-5 h-5" />
          Use my current location
        </button>
        <button
          onClick={() => handleSelect({ lat: 31.1471, lng: 75.3412, name: 'Punjab, India (demo)' })}
          className="flex items-center justify-center gap-2 py-3 bg-primary text-white rounded-xl hover:bg-primary-dark font-medium transition-colors"
        >
          <MapPin className="w-5 h-5" />
          Demo location (Punjab)
        </button>
      </div>

      {/* Map */}
      <MapView onLocationSelect={handleSelect} selectedLocation={selected} />

      {/* Hint */}
      <div className="bg-monsoon-soft border border-monsoon/20 rounded-xl p-4 flex gap-3">
        <Info className="w-5 h-5 text-monsoon shrink-0 mt-0.5" />
        <p className="text-sm text-monsoon">
          Click anywhere on the map to place a pin. Zoom in for more precision. The marker position is used to fetch live weather and rainfall data for your farm.
        </p>
      </div>

      {/* Selected location banner */}
      {selected && (
        <div className="bg-forest-soft border border-forest/20 rounded-xl p-4 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-forest shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-forest">Location selected</div>
            <div className="text-forest text-sm mt-0.5 line-clamp-2 opacity-90">{selected.name}</div>
            <div className="text-forest text-xs mt-0.5 opacity-70">
              {selected.lat.toFixed(4)}, {selected.lng.toFixed(4)}
            </div>
          </div>
        </div>
      )}

      {/* Continue */}
      {selected && (
        <button
          onClick={() => navigate('/parameters')}
          className="w-full py-4 bg-primary text-white rounded-xl hover:bg-primary-dark font-bold text-lg flex items-center justify-center gap-2 transition-colors"
        >
          <Navigation className="w-5 h-5" />
          Fetch climate data →
        </button>
      )}
    </div>
  )
}
