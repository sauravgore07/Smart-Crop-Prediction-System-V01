"""
crop.py — Pydantic schemas for CropPredict API

CropRequest accepts user-facing scalar inputs (latitude/longitude + nutrient mg/kg + pH),
then converts them to the 18 features the RandomForest was trained on:
  Latitude, Longitude,
  Nitrogen-High/Medium/Low, Phosphorous-H/M/L, Potassium-H/M/L,
  pH-Acidic/Neutral/Alkaline,
  N_score, P_score, K_score, pH_score

These must exactly match FEATURE_COLS in train_model.py.
"""

import math
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


# ── Agronomic thresholds (Indian soils, mg/kg for N/P/K) ────────────────────
# Nitrogen  : Low < 25, Medium 25–50, High > 50
# Phosphorus: Low < 25, Medium 25–50, High > 50
# Potassium : Low < 100, Medium 100–200, High > 200
# pH        : Acidic < 6.5, Neutral 6.5–7.5, Alkaline > 7.5

_N_LOW, _N_HIGH = 25.0, 50.0
_P_LOW, _P_HIGH = 25.0, 50.0
_K_LOW, _K_HIGH = 100.0, 200.0
_PH_ACID_MAX = 6.5
_PH_ALK_MIN  = 7.5


def _soft_distribution(value: float, low_thresh: float, high_thresh: float) -> tuple[float, float, float]:
    """
    Convert a scalar nutrient value into fuzzy (High%, Medium%, Low%) percentages
    that sum to 100. Avoids hard step-function cutoffs at the boundaries.

    Returns: (high_pct, medium_pct, low_pct)
    """
    if value >= high_thresh:
        return 100.0, 0.0, 0.0
    if value <= low_thresh:
        return 0.0, 0.0, 100.0
    # Linear ramp through the medium zone
    frac = (value - low_thresh) / (high_thresh - low_thresh)
    return 0.0, round(frac * 100.0, 4), round((1.0 - frac) * 100.0, 4)


def _ph_distribution(ph: float) -> tuple[float, float, float]:
    """
    Returns (Acidic%, Neutral%, Alkaline%) for a given pH reading.
    Uses soft boundaries around the neutral zone edges.
    """
    if ph <= _PH_ACID_MAX:
        return 100.0, 0.0, 0.0
    if ph >= _PH_ALK_MIN:
        return 0.0, 0.0, 100.0
    # Smooth linear ramp through neutral zone
    frac = (ph - _PH_ACID_MAX) / (_PH_ALK_MIN - _PH_ACID_MAX)
    # Transition: acidic → neutral → alkaline
    if frac <= 0.5:
        neutral_pct = frac * 2 * 100.0
        acid_pct    = 100.0 - neutral_pct
        return round(acid_pct, 4), round(neutral_pct, 4), 0.0
    else:
        neutral_pct = (1.0 - frac) * 2 * 100.0
        alk_pct     = 100.0 - neutral_pct
        return 0.0, round(neutral_pct, 4), round(alk_pct, 4)


# ── Request / Response models ────────────────────────────────────────────────

class CropRequest(BaseModel):
    """
    User-facing input. Accepts standard agronomic scalars.
    Call `.to_feature_vector()` to get the 18 values the model expects.
    """

    # Location — required; the model weights these heavily
    latitude:  float
    longitude: float

    # Soil nutrients in mg/kg (ppm).  Defaults are rough pan-India averages.
    nitrogen:   float = 50.0   # N  — typical range: 0–140
    phosphorus: float = 50.0   # P  — typical range: 0–100
    potassium:  float = 150.0  # K  — typical range: 0–300

    # Soil pH (0–14)
    ph: float = 6.5
    season: str | None = None
    previous_crop: str | None = None

    # ── Optional context (stored for logging/UI; NOT sent to the ML model) ──
    temperature: Optional[float] = None  # °C
    humidity:    Optional[float] = None  # %
    rainfall:    Optional[float] = None  # mm/year
    soil_type:   Optional[str]   = None
    season:      Optional[str]   = None
    land_area:   Optional[float] = None  # hectares

    # ── Validators ──────────────────────────────────────────────────────────

    @field_validator(
        "latitude", "longitude",
        "nitrogen", "phosphorus", "potassium", "ph",
        "temperature", "humidity", "rainfall", "land_area",
        mode="after",
    )
    @classmethod
    def reject_nan_inf(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (math.isnan(v) or math.isinf(v)):
            raise ValueError("NaN and Inf values are not allowed")
        return v

    @model_validator(mode="after")
    def check_ranges(self) -> "CropRequest":
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"latitude must be in [-90, 90], got {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"longitude must be in [-180, 180], got {self.longitude}")
        if not (0 < self.ph < 14):
            raise ValueError(f"ph must be in (0, 14), got {self.ph}")
        if self.nitrogen < 0:
            raise ValueError("nitrogen cannot be negative")
        if self.phosphorus < 0:
            raise ValueError("phosphorus cannot be negative")
        if self.potassium < 0:
            raise ValueError("potassium cannot be negative")
        return self

    # ── Feature conversion ───────────────────────────────────────────────────

    def to_feature_vector(self) -> list[float]:
        """
        Convert scalar user inputs into the 18-element feature vector the
        RandomForest model expects.  Order MUST match FEATURE_COLS in
        train_model.py:

            Latitude, Longitude,
            Nitrogen - High, Nitrogen - Medium, Nitrogen - Low,
            Phosphorous - High, Phosphorous - Medium, Phosphorous - Low,
            Potassium - High, Potassium - Medium, Potassium - Low,
            pH - Acidic, pH - Neutral, pH - Alkaline,
            N_score, P_score, K_score, pH_score
        """
        n_high, n_med, n_low = _soft_distribution(self.nitrogen,   _N_LOW, _N_HIGH)
        p_high, p_med, p_low = _soft_distribution(self.phosphorus,  _P_LOW, _P_HIGH)
        k_high, k_med, k_low = _soft_distribution(self.potassium,   _K_LOW, _K_HIGH)
        ph_acid, ph_neut, ph_alk = _ph_distribution(self.ph)

        # Engineered scores — must mirror train_model.py exactly:
        #   score = High*2 + Medium*1 + Low*0
        #   pH_score = Alkaline*2 + Neutral - Acidic
        n_score  = n_high  * 2 + n_med
        p_score  = p_high  * 2 + p_med
        k_score  = k_high  * 2 + k_med
        ph_score = ph_alk  * 2 + ph_neut - ph_acid

        return [
            self.latitude,
            self.longitude,
            n_high, n_med, n_low,
            p_high, p_med, p_low,
            k_high, k_med, k_low,
            ph_acid, ph_neut, ph_alk,
            n_score, p_score, k_score, ph_score,
        ]

    def to_feature_dict(self) -> dict[str, float]:
        """Same as to_feature_vector() but keyed by column name — handy for debugging."""
        vec = self.to_feature_vector()
        keys = [
            "Latitude", "Longitude",
            "Nitrogen - High", "Nitrogen - Medium", "Nitrogen - Low",
            "Phosphorous - High", "Phosphorous - Medium", "Phosphorous - Low",
            "Potassium - High", "Potassium - Medium", "Potassium - Low",
            "pH - Acidic", "pH - Neutral", "pH - Alkaline",
            "N_score", "P_score", "K_score", "pH_score",
        ]
        return dict(zip(keys, vec))


class CropResponse(BaseModel):

    crop: str

    confidence: float

    suitability: float

    suitability_label: str

    top_crops: Optional[list[dict]] = None