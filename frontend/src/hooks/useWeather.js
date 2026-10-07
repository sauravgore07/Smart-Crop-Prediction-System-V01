import { useState, useCallback } from 'react'
import { getWeather, getNASA } from '../services/api'
import { useStore } from '../store/useStore'

export function useWeather() {
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
  const setEnvData            = useStore(s => s.setEnvData)

  const fetchAll = useCallback(async (lat, lng) => {
    setLoading(true)
    setError(null)
    try {
      const [weatherRes, nasaRes] = await Promise.all([
        getWeather(lat, lng),
        getNASA(lat, lng),
      ])
      setEnvData({
        currentTemp:     weatherRes.data.temperature,
        currentRain:     weatherRes.data.precipitation,
        currentHumidity: weatherRes.data.humidity,
        annualRainfall:  nasaRes.data.annualRainfall,
        rainyMonths:     nasaRes.data.rainyMonths,
      })
      return { weather: weatherRes.data, nasa: nasaRes.data }
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [setEnvData])

  return { fetchAll, loading, error }
}
