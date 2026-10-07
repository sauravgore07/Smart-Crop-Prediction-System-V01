import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { useStore } from '../store/useStore'

export default function CropDetailModal({ crop, onClose }) {
  const { farmParams, location, addToRotation } = useStore()

  const landArea = farmParams.landArea || 2
  const [marketInfo, setMarketInfo] = useState(null)
  const [loadingMarket, setLoadingMarket] = useState(false)

  // Close on Escape key
  useEffect(() => {
    const loadMarketInfo = async () => {
      try {
        if (
          !crop?.name ||
          !location?.lat ||
          !location?.lng
        ) {
          console.log("Location missing:", location)
          return
        }

        setLoadingMarket(true)

        const response = await fetch(
          'http://localhost:8000/api/market_info/info',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              crop: crop.name,
              latitude: location.lat,
              longitude: location.lng
            })
          }
        )

        const data = await response.json()

        setMarketInfo(data)

      } catch (error) {
        console.error('Market info error:', error)
      } finally {
        setLoadingMarket(false)
      }
    }

    loadMarketInfo()
  }, [crop, location]) // FIX #1: Changed from farmParams to location

  const profit = Math.round(
    (crop.profitability?.profitPerHectare ?? 0) * ((crop.suitability ?? 80) / 100) * landArea
  )

  return (
    <div
      className="fixed inset-0 bg-ink/50 flex items-center justify-center z-50 p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-surface rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl border border-sand">
        <div className="p-6">
          {/* Modal header */}
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="font-display text-2xl font-semibold text-ink">{crop.name}</h2>
              <p className="text-ink-soft italic text-sm">{crop.scientificName}</p>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-paper transition-colors"
            >
              <X className="w-6 h-6 text-ink-soft" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left column */}
            <div>
              <div className="text-7xl text-center mb-4">{crop.image}</div>

              <div className="bg-paper p-4 rounded-xl mb-4">
                <h3 className="font-semibold mb-1 text-sm text-ink">Description</h3>
                <p className="text-sm text-ink-soft">{crop.description}</p>
              </div>

              <div className="space-y-2 text-sm">
                {[
                  ['Category', crop.category],
                  ['Season', Array.isArray(crop.season) ? crop.season.join(', ') : crop.season],
                  ['Duration', crop.duration],
                  ['Yield', crop.yield],
                  ['Investment', crop.investment],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between">
                    <span className="text-ink-soft">{label}</span>
                    <span className="font-medium text-ink">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right column */}
            <div>
              <h3 className="font-semibold mb-3 text-ink">Profitability</h3>
              <div className="space-y-2 text-sm mb-4">
                {/* FIX #2: Restored profitability section */}
                {[
                  ['Cost / hectare', `₹${crop.profitability?.costPerHectare?.toLocaleString()}`],
                  ['Revenue / hectare', `₹${crop.profitability?.revenuePerHectare?.toLocaleString()}`],
                  ['Profit / hectare', `₹${crop.profitability?.profitPerHectare?.toLocaleString()}`],
                  [`Total (${landArea} ha)`, `₹${profit.toLocaleString()}`],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between">
                    <span className="text-ink-soft">{label}</span>
                    <span className="font-semibold text-forest">{value}</span>
                  </div>
                ))}
                <div className="flex justify-between pt-1 border-t border-sand">
                  <span className="text-ink-soft">Risk level</span>
                  <span className={`font-semibold ${crop.profitability?.riskLevel === 'High' ? 'text-clay' :
                    crop.profitability?.riskLevel === 'Medium' ? 'text-primary-dark' : 'text-forest'
                    }`}>{crop.profitability?.riskLevel}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-ink-soft">Price trend</span>
                  <span className="font-medium text-ink">{crop.profitability?.priceTrend}</span>
                </div>
              </div>

              {/* Growing tips */}
              <div className="bg-primary-soft rounded-xl p-4 mb-4">
                <h4 className="font-semibold text-sm mb-2 text-primary-dark">Growing tips</h4>
                <ul className="text-sm text-primary-dark list-disc list-inside space-y-1">
                  {crop.tips?.map((tip, i) => <li key={i}>{tip}</li>)}
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-monsoon-soft rounded-xl p-4 mb-4">
            <h4 className="font-semibold text-sm mb-3 text-monsoon">
              Market information
            </h4>

            {loadingMarket ? (
              <p className="text-sm text-monsoon">
                Loading market data...
              </p>
            ) : marketInfo ? (
              <>
                <div className="space-y-2 text-sm mb-4">

                  <div className="flex justify-between">
                    <span className="text-ink-soft">
                      Current price
                    </span>

                    <span className="font-semibold text-forest">
                      ₹{Number(marketInfo.price || 0).toLocaleString()} / quintal
                    </span>
                  </div>

                  {/* FIX #3: Updated district display */}
                  <div className="flex justify-between">
                    <span className="text-ink-soft">
                      Nearest district
                    </span>

                    <span className="font-medium text-ink">
                      {marketInfo.nearest_markets?.[0]?.district || 'N/A'}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-ink-soft">
                      Market trend
                    </span>

                    <span
                      className={`font-medium ${marketInfo.trend === 'up'
                        ? 'text-forest'
                        : marketInfo.trend === 'down'
                          ? 'text-clay'
                          : 'text-primary-dark'
                        }`}
                    >
                      {marketInfo.trend}
                    </span>
                  </div>

                </div>

                {/* FIX #4: Keep nearest markets section */}
                <div>
                  <p className="text-xs font-medium text-ink-soft mb-2">
                    Nearest markets
                  </p>

                  <div className="space-y-2">

                    {marketInfo.nearest_markets?.map((market) => (

                      <div
                        key={`${market.market}-${market.distance}`}
                        className="bg-white border border-sand rounded-lg p-3 flex justify-between items-center"
                      >

                        <div>

                          <div className="font-medium text-sm text-ink">
                            {market.market}
                          </div>

                          <div className="text-xs text-ink-soft">
                            {market.district}, {market.state}
                          </div>

                        </div>

                        <div className="font-semibold text-monsoon">
                          {market.distance} km
                        </div>

                      </div>

                    ))}

                  </div>
                </div>

                <div className="mt-3 text-xs text-ink-soft">
                  Source: {marketInfo.source}
                </div>
              </>
            ) : (
              <p className="text-sm text-ink-soft">
                Market information unavailable
              </p>
            )}
          </div>

          {/* Environmental requirements */}
          <div className="mt-4 pt-4 border-t border-sand">
            <h3 className="font-semibold mb-3 text-sm text-ink">Environmental requirements</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              {[
                ['Temperature', `${crop.requirements?.tempMin}–${crop.requirements?.tempMax}°C`, 'bg-monsoon-soft'],
                ['Rainfall', `${crop.requirements?.rainfallMin}–${crop.requirements?.rainfallMax} mm`, 'bg-forest-soft'],
                ['Soil types', crop.requirements?.soilTypes?.join(', '), 'bg-primary-soft'],
                ['pH range', `${crop.requirements?.phMin}–${crop.requirements?.phMax}`, 'bg-clay-soft'],
              ].map(([label, value, bg]) => (
                <div key={label} className={`${bg} rounded-lg p-3 text-center`}>
                  <div className="font-semibold text-xs text-ink">{value}</div>
                  <div className="text-ink-soft text-xs mt-0.5">{label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex gap-3">
            <button
              onClick={() => { addToRotation(crop.name); onClose() }}
              className="btn-sky flex-1 py-2.5 bg-primary text-white rounded-xl font-semibold hover:bg-primary-dark transition-colors"
            >
              Add to rotation plan
            </button>
            <button
              onClick={onClose}
              className="flex-1 py-2.5 bg-paper text-ink rounded-xl font-semibold hover:bg-sand transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
