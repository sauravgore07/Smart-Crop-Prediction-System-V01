
import { useState } from 'react'
import { useStore } from '../store/useStore'
import CropDetailModal from './CropDetailModal'

export default function CropCard({

  crop,

  rank,

  isML = false

}) {

  const [showModal, setShowModal] = useState(false)

  const { farmParams, addToRotation } = useStore()

  const landArea = Number(
    farmParams.landArea || 2
  )

  // =====================================================
  // SAFE NUMERIC SUITABILITY
  // =====================================================

  const suitability = Number(

    crop.confidence ??

    crop.suitability ??

    0
  )

  // =====================================================
  // SUITABILITY LABEL
  // =====================================================

  const suitabilityLabel =

    crop.suitabilityLabel ??

    crop.suitability ??

    'Unknown'

  // =====================================================
  // SAFE PROFITABILITY
  // =====================================================

  const profitPerHectare = Number(

    crop.profitability?.profitPerHectare ??

    crop.estimatedProfit ??

    0
  )

  const profit = Math.round(

    profitPerHectare *

    (suitability / 100) *

    landArea
  )

  // =====================================================
  // SAFE VALUES
  // =====================================================

  const cropYield =

    crop.yield ??

    crop.expectedYield ??

    'N/A'

  const duration =

    crop.duration ??

    'N/A'

  const cropSeason = Array.isArray(crop.season)

    ? crop.season.join(', ')

    : crop.season ?? 'N/A'

  const investment =

    crop.investment ??

    'Medium'

  const marketDemand =

    crop.profitability?.marketDemand ??

    'Medium'

  const riskLevel =

    crop.profitability?.riskLevel ??

    'Medium'

  // =====================================================
  // COLORS
  // =====================================================

  const suitabilityColor =

    suitability >= 80

      ? 'text-forest'

      : suitability >= 60

      ? 'text-primary-dark'

      : 'text-clay'

  const riskColor =

    riskLevel === 'High'

      ? 'text-clay'

      : riskLevel === 'Medium'

      ? 'text-primary-dark'

      : 'text-forest'

  const demandColor =

    marketDemand === 'High'

      ? 'text-forest'

      : marketDemand === 'Medium'

      ? 'text-primary-dark'

      : 'text-clay'

  // =====================================================
  // RENDER
  // =====================================================

  return (

    <>

      <div className="crop-card bg-surface rounded-2xl border border-sand p-5 hover:shadow-lg">

        {/* Header */}

        <div className="flex justify-between items-start mb-3">

          <div className="flex gap-2 flex-wrap">

            {rank && (

              <span

                className={`text-xs font-bold px-2 py-1 rounded-full ${
                  isML
                    ? 'bg-monsoon-soft text-monsoon'
                    : 'bg-forest-soft text-forest'
                }`}
              >

                {isML ? '🤖 AI' : `#${rank}`}

              </span>
            )}

            <span className="text-xs px-2 py-1 rounded-full bg-paper text-ink-soft">

              {crop.category ?? 'Crop'}

            </span>

          </div>

          <div className="text-right">

            <div
              className={`text-lg font-display font-semibold ${suitabilityColor}`}
            >

              {Math.round(suitability)}%

            </div>

          </div>

        </div>

        {/* Crop Image */}

        <div className="text-5xl text-center my-3">

          {crop.image ?? '🌱'}

        </div>

        {/* Name */}

        <h3 className="font-display text-lg font-semibold text-center mb-0.5 text-ink">

          {crop.name ?? 'Unknown Crop'}

        </h3>

        <p className="text-xs text-ink-soft text-center italic mb-4">

          {crop.scientificName || 'Agricultural Crop'}

        </p>

        {/* Stats */}

        <div className="space-y-2 text-sm mb-4">

          <div className="flex justify-between">

            <span className="text-ink-soft">

              Profit potential

            </span>

            <span className="font-semibold text-forest">

              ₹{profit.toLocaleString()}

            </span>

          </div>

          <div className="flex justify-between">

            <span className="text-ink-soft">

              Yield

            </span>

            <span className="text-ink">

              {cropYield}

            </span>

          </div>

          <div className="flex justify-between">

            <span className="text-ink-soft">

              Duration

            </span>

            <span className="text-ink">

              {duration}

            </span>

          </div>

          <div className="flex justify-between">

            <span className="text-ink-soft">

              Season

            </span>

            <span className="text-ink">

              {cropSeason}

            </span>

          </div>

          <div className="flex justify-between">

            <span className="text-ink-soft">

              Investment

            </span>

            <span className="text-ink">

              {investment}

            </span>

          </div>

          <div className="flex justify-between">

            <span className="text-ink-soft">

              Risk

            </span>

            <span className={`font-medium ${riskColor}`}>

              {riskLevel}

            </span>

          </div>

          <div className="flex justify-between">

            <span className="text-ink-soft">

              Market demand

            </span>

            <span className={`font-medium ${demandColor}`}>

              {marketDemand}

            </span>

          </div>

        </div>

        {/* Description */}

        <p className="text-xs text-ink-soft bg-paper rounded-lg p-3 mb-4 line-clamp-2">

          {crop.description ??

            'Suitable crop for Indian agriculture.'}

        </p>

        {/* Buttons */}

        <div className="flex gap-2">

          <button

            onClick={() => setShowModal(true)}

            className="btn-sky flex-1 py-2 bg-forest text-white rounded-lg text-sm font-medium hover:bg-forest-dark transition-colors"
          >

            Details

          </button>

          <button

            onClick={() => addToRotation(crop.name)}

            className="btn-sky flex-1 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors"
          >

            + Rotation

          </button>

        </div>

      </div>

      {/* Modal */}

      {showModal && (

        <CropDetailModal

          crop={crop}

          onClose={() => setShowModal(false)}

        />
      )}

    </>
  )
}
