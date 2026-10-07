import { Thermometer, CloudRain, Droplets, Cloud } from 'lucide-react'
import { useStore } from '../store/useStore'

export default function WeatherPanel() {
  const envData = useStore(s => s.envData)

  const stats = [
    {
      icon: <Thermometer className="w-5 h-5" />,
      label: 'Temperature',
      value: `${Math.round(envData.currentTemp)}°C`,
      sub: 'Open-Meteo API',
      bg: 'bg-monsoon-soft',
      iconColor: 'text-monsoon',
    },
    {
      icon: <CloudRain className="w-5 h-5" />,
      label: 'Precipitation',
      value: `${envData.currentRain} mm`,
      sub: 'Current',
      bg: 'bg-forest-soft',
      iconColor: 'text-forest',
    },
    {
      icon: <Droplets className="w-5 h-5" />,
      label: 'Humidity',
      value: `${Math.round(envData.currentHumidity)}%`,
      sub: 'Relative',
      bg: 'bg-primary-soft',
      iconColor: 'text-primary-dark',
    },
    {
      icon: <Cloud className="w-5 h-5" />,
      label: 'Annual rainfall',
      value: `${envData.annualRainfall} mm`,
      sub: 'NASA 30-yr avg',
      bg: 'bg-clay-soft',
      iconColor: 'text-clay',
    },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((s) => (
        <div key={s.label} className={`${s.bg} rounded-xl p-4`}>
          <div className={`${s.iconColor} mb-2`}>{s.icon}</div>
          <div className="text-2xl font-display font-semibold text-ink">{s.value}</div>
          <div className="text-sm text-ink-soft">{s.label}</div>
          <div className="text-xs text-ink-soft/70 mt-0.5">{s.sub}</div>
        </div>
      ))}
    </div>
  )
}
