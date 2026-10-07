from pathlib import Path
import pandas as pd

# =====================================================
# FILE PATH
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MANDI_CSV = (
    BASE_DIR
    / "data"
    / "mandis_with_coordinates.csv"
)

# =====================================================
# LOAD DATA
# =====================================================

try:

    _mandi_df = pd.read_csv(MANDI_CSV)

    print("\n=== MANDI COLUMNS ===")
    print(_mandi_df.columns.tolist())

    print("\n=== FIRST ROW ===")
    print(_mandi_df.head(1))

    print("\n=== TOTAL ROWS ===")
    print(len(_mandi_df))

except Exception as e:

    print(f"\nERROR LOADING CSV: {e}")

    _mandi_df = pd.DataFrame()

# =====================================================
# GET MARKETS
# =====================================================

def get_markets_by_district(
    district: str,
    limit: int = 5
):

    if not district:
        return []

    if _mandi_df.empty:
        return []

    matches = _mandi_df[
        _mandi_df["District"]
        .astype(str)
        .str.strip()
        .str.upper()
        ==
        district.strip().upper()
    ]

    markets = (
        matches["Market"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return markets[:limit]