import { useState } from 'react'
import axios from 'axios'
import { RefreshCw } from 'lucide-react'
import { useStore } from '../store/useStore'

// =======================================================
// SEASONS
// =======================================================

const SEASON_ORDER = [

  'Kharif',

  'Rabi',

  'Summer'
]

// =======================================================
// COMPONENT
// =======================================================

export default function RotationPlanner({

  allCrops,
  setNearestMarkets

}) {

  // =====================================================
  // STORE
  // =====================================================

  const {

    rotationHistory,

    location

  } = useStore()

  // =====================================================
  // STATES
  // =====================================================

  const [startSeason, setStartSeason] = useState(

    'Kharif'
  )

  const [plan, setPlan] = useState([])

  const [loading, setLoading] = useState(false)

  // =====================================================
  // GENERATE
  // =====================================================

  async function generate() {

    try {

      setLoading(true)

      // =================================================
      // CURRENT CROP
      // =================================================

      const currentCrop =

        rotationHistory[
          rotationHistory.length - 1
        ]?.crop

      if (!currentCrop) {

        alert(
          'Please add a crop first'
        )

        setLoading(false)

        return
      }

      // =================================================
      // LOCATION
      // =================================================

      const latitude = Number(
        location?.lat
      )

      const longitude = Number(
        location?.lng
      )

      // =================================================
      // VALIDATION
      // =================================================

      if (

        !latitude ||

        !longitude

      ) {

        alert(
          'Please select farm location first'
        )

        setLoading(false)

        return
      }

      // =================================================
      // API REQUEST
      // =================================================

      const response = await axios.post(

        'http://127.0.0.1:8000/rotation/next-season',

        {

          latitude,

          longitude,

          currentSeason: startSeason,

          previousCrop: currentCrop,
        }
      )

      // =================================================
      // RESPONSE
      // =================================================

      const data = response.data

      console.log(
        'Rotation Response:',
        data
      )

      // =================================================
      // ERROR
      // =================================================

      if (data.error) {

        alert(data.error)

        setLoading(false)

        return
      }

      // =================================================
      // ENRICH WITH crops.json
      // =================================================

      const enriched = (

        data.recommendedRotation || []

      ).map(item => {

        const fullCrop = allCrops.find(

          c =>

            c.name?.trim().toLowerCase()

            ===

            item.crop?.trim().toLowerCase()
        )

        // ------------------------------------------------
        // FOUND IN crops.json
        // ------------------------------------------------

        if (fullCrop) {

          return {

            ...item,

            season: data.nextSeason,

            crop: {

              ...fullCrop,

              name: item.crop
            }
          }
        }

        // ------------------------------------------------
        // FALLBACK
        // ------------------------------------------------

        return {

          ...item,

          season: data.nextSeason,

          crop: {

            name: item.crop,

            image: '🌱',

            category: 'Crop',

            duration: '90-120 days',

            season: [data.nextSeason],

            profitability: {

              marketDemand: 'Medium',

              riskLevel: 'Medium',

              profitPerHectare: 50000,
            }
          }
        }
      })

      // =================================================
      // SAVE PLAN
      // =================================================

      setPlan(enriched)

      // =================================================
      // FETCH NEAREST MARKETS
      // =================================================

      if (enriched.length > 0) {

        try {

          const marketResponse = await axios.post(

            'http://127.0.0.1:8000/api/market_info/info',

            {

              crop: enriched[0].crop.name,

              latitude,

              longitude
            }
          )

          setNearestMarkets(

            marketResponse.data.nearest_markets || []

          )

        } catch (err) {

          console.error(

            'Market fetch failed',

            err
          )

          setNearestMarkets([])
        }
      }

    } catch (err) {

      console.error(err)

      alert(
        'Rotation generation failed'
      )

    } finally {

      setLoading(false)
    }
  }

  // =====================================================
  // RENDER
  // =====================================================

  return (

    <div className="space-y-6">

      {/* =============================================== */}
      {/* CONTROLS */}
      {/* =============================================== */}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Current Season */}

        <div>

          <label className="block text-sm font-medium mb-1 text-ink">

            Current season

          </label>

          <select

            value={startSeason}

            onChange={e => setStartSeason(e.target.value)}

            className="w-full px-3 py-2 border border-sand rounded-lg focus:ring-2 focus:ring-primary/40 focus:border-primary outline-none bg-white"
          >

            {SEASON_ORDER.map(s => (

              <option

                key={s}

                value={s}
              >

                {s}

              </option>
            ))}

          </select>

        </div>

        {/* Generate */}

        <div className="flex items-end">

          <button

            onClick={generate}

            disabled={loading}

            className="btn-sky w-full flex items-center justify-center gap-2 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark font-medium transition-colors disabled:opacity-50"
          >

            <RefreshCw

              className={`w-4 h-4 ${loading
                  ? 'animate-spin'
                  : ''
                }`}
            />

            {

              loading

                ? 'Generating...'

                : 'Generate next season plan'
            }

          </button>

        </div>

      </div>

      {/* =============================================== */}
      {/* LOCATION */}
      {/* =============================================== */}

      {location && (

        <div className="bg-monsoon-soft border border-monsoon/20 rounded-xl p-4">

          <div className="font-semibold text-monsoon text-sm mb-1">

            Selected farm location

          </div>

          <div className="text-monsoon text-sm">

            {location.name}
          </div>

          <div className="text-monsoon text-xs mt-1 opacity-70">

            {location.lat?.toFixed(4)},

            {' '}

            {location.lng?.toFixed(4)}
          </div>

        </div>
      )}

      {/* =============================================== */}
      {/* CURRENT CROP */}
      {/* =============================================== */}

      {rotationHistory.length > 0 && (

        <div className="bg-primary-soft border border-primary/20 rounded-xl p-4">

          <div className="text-sm font-semibold text-primary-dark mb-1">

            Current crop

          </div>

          <div className="text-primary-dark">

            {

              rotationHistory[
                rotationHistory.length - 1
              ]?.crop

            }

          </div>

        </div>
      )}

      {/* =============================================== */}
      {/* PLAN */}
      {/* =============================================== */}

      {plan.length > 0 && (

        <div className="space-y-3">

          <div className="font-semibold text-sm text-ink">

            Recommended next season crops

          </div>

          {plan.map((item, i) => (

            <div

              key={i}

              className="flex items-center justify-between p-4 bg-paper rounded-xl border border-sand hover:shadow-sm transition-shadow"
            >

              {/* LEFT */}

              <div className="flex items-center gap-3">

                <div className="text-4xl">

                  {item.crop.image ?? '🌱'}

                </div>

                <div>

                  <div className="font-semibold text-ink">

                    {item.crop.name}

                  </div>

                  <div className="text-sm text-ink-soft">

                    {item.season}

                  </div>

                  <div className="text-xs text-ink-soft/70">

                    {item.crop.category}
                  </div>

                </div>

              </div>

              {/* RIGHT */}

              <div className="text-right">

                <div className="text-lg font-display font-semibold text-forest">

                  {item.score}
                </div>

                <div className="text-xs text-ink-soft">

                  Rotation score
                </div>

                <div className="text-xs text-monsoon mt-1">

                  {

                    item.crop.profitability?.marketDemand

                    ?? 'Medium demand'
                  }

                </div>

              </div>

            </div>
          ))}

        </div>
      )}

      {/* =============================================== */}
      {/* HISTORY */}
      {/* =============================================== */}

      {rotationHistory.length > 0 && (

        <div>

          <h4 className="font-semibold mb-2 text-sm text-ink">

            Previous rotation history

          </h4>

          <div className="flex flex-wrap gap-2">

            {rotationHistory.map((r, i) => (

              <span

                key={i}

                className="px-3 py-1 bg-forest-soft text-forest rounded-full text-sm"
              >

                {r.crop}

              </span>
            ))}

          </div>

        </div>
      )}

    </div>

  )
}
