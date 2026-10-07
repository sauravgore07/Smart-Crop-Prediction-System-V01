import { useEffect, useState } from 'react'
import RotationPlanner from '../components/RotationPlanner'
import { getAllCrops } from '../services/api'

export default function CropRotation() {

  const [allCrops, setAllCrops] = useState([])
  const [nearestMarkets, setNearestMarkets] = useState([])

  useEffect(() => {

    getAllCrops()
      .then(r => setAllCrops(r.data))
      .catch(() => {})

  }, [])

  return (

    <div className="space-y-6">

      {/* Header */}

      <div className="bg-forest text-white p-6 rounded-2xl">

        <h2 className="font-display text-2xl font-semibold mb-1">
          Crop rotation planner
        </h2>

        <p className="text-forest-soft">
          Plan multi-season rotations for better soil health and higher yields.
        </p>

      </div>

      {/* Main Layout */}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left Side - Rotation Planner */}

        <div className="lg:col-span-2 bg-surface rounded-xl border border-sand p-6">

          <RotationPlanner
            allCrops={allCrops}
            setNearestMarkets={setNearestMarkets}
          />

        </div>

        {/* Right Side - Nearest Markets */}

        <div className="bg-surface rounded-xl border border-sand p-6 h-fit">

          <h3 className="font-semibold text-lg mb-4 text-ink">

            Nearest markets

          </h3>

          {nearestMarkets.length === 0 ? (

            <div className="text-sm text-ink-soft">

              Generate a rotation plan to view nearby markets.

            </div>

          ) : (

            <div className="space-y-3">

              {nearestMarkets.map((market, index) => (

                <div
                  key={index}
                  className="bg-monsoon-soft border border-monsoon/20 rounded-xl p-3"
                >

                  <div className="font-semibold text-ink">

                    {market.market}

                  </div>

                  <div className="text-sm text-ink-soft">

                    {market.district}, {market.state}

                  </div>

                  <div className="text-monsoon font-semibold mt-1">

                    {market.distance} km

                  </div>

                </div>

              ))}

            </div>

          )}

        </div>

      </div>

    </div>

  )
}
