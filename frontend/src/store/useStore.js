import { create } from 'zustand'

export const useStore = create((set, get) => ({

  // ── Location ──────────────────────────────────────────
  // Shape: { lat: number, lng: number, name?: string }
  location: null,
  setLocation: (loc) => set({ location: loc }),

  // ── Environmental data (from weather + NASA APIs) ─────
  envData: {
    currentTemp:     25,
    currentRain:     0,
    currentHumidity: 65,
    annualRainfall:  800,
    rainyMonths:     ['JUN', 'JUL', 'AUG'],
  },
  setEnvData: (data) => set({ envData: { ...get().envData, ...data } }),

  // ── Farm parameters (form inputs on Parameters page) ──
  farmParams: {
    soilType:   'Loamy',
    soilPh:     6.5,
    landArea:   2,
    season:     'Kharif',
    // Soil nutrients (mg/kg) — shown and edited on the Parameters page
    nitrogen:   50,
    phosphorus: 50,
    potassium:  150,
  },
  setFarmParams: (params) => set({ farmParams: { ...get().farmParams, ...params } }),

  // ── Crop rotation history ──────────────────────────────
  rotationHistory: [],
  addToRotation: (cropName) => set(s => ({
    rotationHistory: [
      ...s.rotationHistory,
      { crop: cropName, season: s.farmParams.season, addedAt: new Date().toISOString() }
    ]
  })),
  clearRotation: () => set({ rotationHistory: [] }),

  // ── Auth ───────────────────────────────────────────────
  user:  null,
  token: localStorage.getItem('token') || null,
  setAuth: (user, token) => {
    localStorage.setItem('token', token)
    set({ user, token })
  },
  setUser:  (user)  => set({ user }),
  logout:   ()      => {
    localStorage.removeItem('token')
    set({ user: null, token: null })
  },
  isLoggedIn: () => !!get().token,
}))