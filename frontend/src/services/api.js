import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// Attach JWT if present — skip if no token exists
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401 from a protected endpoint: clear token, redirect once.
// Auth endpoints (login/register) legitimately return 401 for bad credentials —
// those must NOT trigger a redirect or token wipe.
const AUTH_PATHS = ['/api/auth/login', '/api/auth/register']

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      const url = err.config?.url || ''
      const isAuthEndpoint = AUTH_PATHS.some(p => url.includes(p))
      if (!isAuthEndpoint) {
        localStorage.removeItem('token')
        window.location.replace('/login')
      }
    }
    return Promise.reject(err)
  }
)

// --- Auth ---
export const register = (data) => api.post('/api/auth/register', data)
export const login    = (data) => api.post('/api/auth/login', data)
export const getMe    = ()     => api.get('/api/auth/me')

// --- Crops ---
export const getRecommendations = (data) => api.post('/api/crops/recommend', data)
export const getAllCrops         = ()     => api.get('/api/crops/all')

// --- Farms (requires login) ---
export const getFarms   = ()       => api.get('/api/farms/')
export const saveFarm   = (data)   => api.post('/api/farms/', data)
export const updateFarm = (id, d)  => api.patch(`/api/farms/${id}`, d)
export const deleteFarm = (id)     => api.delete(`/api/farms/${id}`)

// --- Weather ---
export const getWeather = (lat, lng) => api.get(`/api/weather?lat=${lat}&lng=${lng}`)
export const getNASA    = (lat, lng) => api.get(`/api/weather/nasa?lat=${lat}&lng=${lng}`)

// --- Market prices ---
export const getMarketPrices = (crops) =>
  api.get(`/api/market/prices?crops=${crops.join(',')}`)
