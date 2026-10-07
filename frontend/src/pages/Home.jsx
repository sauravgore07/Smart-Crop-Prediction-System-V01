import { useNavigate } from 'react-router-dom'
import { MapPin, Satellite, Cloud, TrendingUp, ShieldCheck, Sprout } from 'lucide-react'
import MarketPriceBar from '../components/MarketPriceBar'
import Reveal from '../components/Reveal'

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
// Indian cropping seasons: Rabi Nov–Mar, Zaid Apr–May, Kharif Jun–Oct
const seasonOf = (m) => (m >= 5 && m <= 9 ? 'Kharif' : m === 3 || m === 4 ? 'Zaid' : 'Rabi')
const SEASON_STYLE = {
  Kharif: 'bg-primary',
  Rabi:   'bg-marigold',
  Zaid:   'bg-clay',
}

function SeasonRuler() {
  const now = new Date().getMonth()
  return (
    <div className="bg-forest-dark/70 border border-white/15 rounded-xl p-5">
      <p className="text-forest-soft text-sm mb-1">Where the farming year stands</p>
      <p className="font-display text-3xl font-bold mb-5">
        {MONTHS[now]} &middot; {seasonOf(now)} season
      </p>
      <div className="grid grid-cols-12 gap-1">
        {MONTHS.map((m, i) => (
          <div key={m} className="text-center">
            <div
              style={{ '--i': i }}
              className={`bar-grow h-16 rounded-sm ${SEASON_STYLE[seasonOf(i)]} ${i === now ? 'opacity-100 ring-2 ring-white now-ring' : 'opacity-40'}`}
            />
            <span className={`block mt-1.5 text-[11px] ${i === now ? 'text-white font-semibold' : 'text-forest-soft'}`}>
              {m}
            </span>
          </div>
        ))}
      </div>
      <div className="flex gap-4 mt-4 text-xs text-forest-soft">
        {Object.entries(SEASON_STYLE).map(([name, cls]) => (
          <span key={name} className="flex items-center gap-1.5">
            <span className={`w-2.5 h-2.5 rounded-sm ${cls}`} /> {name}
          </span>
        ))}
      </div>
    </div>
  )
}

export default function Home() {
  const navigate = useNavigate()

  const features = [
    { icon: <MapPin className="w-5 h-5" />,      title: 'Interactive map',  desc: 'Click anywhere on a live satellite map to select your farm location.' },
    { icon: <Satellite className="w-5 h-5" />,    title: 'Climate data',     desc: '30-year historical rainfall from the NASA POWER API.' },
    { icon: <Cloud className="w-5 h-5" />,        title: 'Live weather',     desc: 'Real-time temperature and humidity from Open-Meteo.' },
    { icon: <TrendingUp className="w-5 h-5" />,   title: 'Market prices',    desc: 'Current MSP-based crop prices, updated daily.' },
    { icon: <ShieldCheck className="w-5 h-5" />,  title: 'ML predictions',   desc: 'A RandomForest model trained on 2,200+ samples.' },
    { icon: <Sprout className="w-5 h-5" />,       title: 'Rotation planner', desc: 'Multi-season crop rotation for better soil health.' },
  ]

  return (
    <div className="space-y-12">
      <div className="-mx-6 -mt-6">
        <MarketPriceBar />
      </div>

      {/* Hero */}
      <div className="field-texture bg-forest text-white rounded-2xl overflow-hidden">
        <div className="px-6 py-12 md:py-16 md:px-12 grid lg:grid-cols-5 gap-10 items-center">
          <div className="lg:col-span-2">
            <h1 style={{ '--i': 0 }} className="rise text-4xl md:text-5xl leading-[1.05] font-bold mb-5">
              Know what to sow, before the season starts.
            </h1>
            <p style={{ '--i': 1 }} className="rise text-forest-soft text-lg mb-8 max-w-md leading-relaxed">
              Live weather, 30 years of rainfall and mandi prices go into a trained model that
              ranks the crops best suited to your land right now.
            </p>
            <button
              style={{ '--i': 2 }}
              onClick={() => navigate('/location')}
              className="rise px-6 py-3.5 bg-marigold text-forest-dark rounded-md hover:opacity-90 font-bold text-base transition-colors"
            >
              Find crops for my farm
            </button>
          </div>
          <div className="lg:col-span-3">
            <SeasonRuler />
          </div>
        </div>
      </div>

      {/* Feature grid */}
      <div>
        <h2 className="text-2xl font-bold text-ink mb-5">What goes into a recommendation</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-sand border border-sand rounded-2xl overflow-hidden">
          {features.map((f, i) => (
            <Reveal key={f.title} index={i % 3} className="bg-surface p-6 hover:bg-forest-soft/10">
              <div className="w-10 h-10 rounded-md bg-forest-soft text-forest flex items-center justify-center mb-4">
                {f.icon}
              </div>
              <h3 className="font-semibold text-lg mb-1 text-ink">{f.title}</h3>
              <p className="text-ink-soft text-sm leading-relaxed">{f.desc}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </div>
  )
}
