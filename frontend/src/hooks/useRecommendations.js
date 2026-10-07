import { useState, useCallback } from 'react'
import { getRecommendations } from '../services/api'
import { useStore } from '../store/useStore'

export function useRecommendations() {
  const [crops, setCrops]     = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const location   = useStore(s => s.location)
  const envData    = useStore(s => s.envData)
  const farmParams = useStore(s => s.farmParams)

  const fetchCrops = useCallback(async () => {
    // Guard: location must be set before we can call the model
    if (!location?.lat || !location?.lng) {
      setError('Location not set. Please allow location access and try again.')
      setCrops([])
      return []
    }

    setLoading(true)
    setError(null)

    try {
      const payload = {
        // Required by model — from location store
        latitude:   location.lat,
        longitude:  location.lng,

        // Soil nutrients — from farmParams (NOT hardcoded)
        nitrogen:   farmParams.nitrogen,
        phosphorus: farmParams.phosphorus,
        potassium:  farmParams.potassium,

        // Soil pH — single source of truth: farmParams.soilPh
        ph: farmParams.soilPh,

        // Environment — from weather/NASA API data
        temperature: envData.currentTemp,
        humidity:    envData.currentHumidity,
        rainfall:    envData.annualRainfall,

        // Optional context
        soil_type: farmParams.soilType,
        season:    farmParams.season,
        land_area: farmParams.landArea,
      }

      // Required fields — must be finite numbers before sending
      const required = { latitude: payload.latitude, longitude: payload.longitude, ph: payload.ph }
      for (const [field, val] of Object.entries(required)) {
        if (!Number.isFinite(val)) {
          setError(`Missing required field: "${field}". Check your location and farm settings.`)
          setCrops([])
          return []
        }
      }

      // Optional numeric fields — only validate if present
      const optional = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'rainfall', 'land_area']
      for (const field of optional) {
        const val = payload[field]
        if (val != null && !Number.isFinite(val)) {
          setError(`Invalid value for "${field}". Please check your farm parameters.`)
          setCrops([])
          return []
        }
      }

      const res = await getRecommendations(payload)

      // res.data is already the array returned by the backend — don't wrap in []
      setCrops(res.data)
      return res.data

    } catch (err) {
      const detail = err.response?.data?.detail
      // Pydantic 422 returns detail as an array of error objects
      const message = Array.isArray(detail)
        ? detail.map(e => `${e.loc?.join('.')}: ${e.msg}`).join(', ')
        : detail || err.message
      setError(message)
      setCrops([])
      return []
    } finally {
      setLoading(false)
    }
  }, [location, envData, farmParams])

  return { crops, loading, error, fetchCrops }
}