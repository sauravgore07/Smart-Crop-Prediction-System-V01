"""
CropPredict — ML training pipeline (location-based agricultural dataset)

Dataset: ml_training/crop_dataset.csv
  - 730 rows across 36 Indian states/regions
  - Multi-label crop column (comma-separated)
  - Soil nutrient percentages (N/P/K high/medium/low)
  - pH distribution (acidic/neutral/alkaline)
  - Latitude/Longitude

Output:
  - backend/app/ml/model.pkl         (trained RandomForest)
  - backend/app/ml/label_encoder.pkl (LabelEncoder for target)
  - backend/app/ml/feature_cols.pkl  (ordered feature column names)
"""

import re
import pickle
import pathlib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

CSV_PATH = pathlib.Path(__file__).parent / "crop_dataset.csv"
OUT_DIR  = pathlib.Path(__file__).parent.parent / "backend" / "app" / "ml"

# Minimum number of samples a crop must have after explode to be trainable
MIN_SAMPLES = 10


# ── Step 1: Data loading and cleaning ────────────────────────────────────────

def load_and_clean(path: pathlib.Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Drop the trailing empty column the CSV has
#    df = df.loc[:, ~df.columns.str.strip().eq("")]
    df = df.loc[:, df.columns.str.strip() != ""]
    # Drop rows where soil nutrient data is entirely missing
    soil_cols = [c for c in df.columns if c.startswith(("Nitrogen", "Phosphorous", "Potassium", "pH"))]
    df = df.dropna(subset=soil_cols, how="all").reset_index(drop=True)

    # Drop rows with no crop data
    df = df.dropna(subset=["Crop"]).reset_index(drop=True)

    return df


def split_crop_field(crop_string: str) -> list[str]:
    """
    Split comma-separated crops while preserving commas inside parentheses.
    'Paddy (Aman, Boro), Mustard' → ['Paddy (Aman, Boro)', 'Mustard']
    """
    parts = []
    depth = 0
    current = []
    for char in crop_string:
        if char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current).strip())
    return [p for p in parts if p]


# Canonical name mapping: raw messy label → clean standardized name.
# None = discard this entry (not a real crop or too vague).
CROP_NAME_MAP = {
    # Case normalization + paddy/rice unification
    "rice": "Rice", "paddy": "Rice", "upland rice": "Rice", "basmati rice": "Rice",
    "paddy (aman, boro)": "Rice",
    "wheat": "Wheat",
    "maize": "Maize",
    "sugarcane": "Sugarcane",
    "cotton": "Cotton",
    "soybean": "Soybean", "soyabean": "Soybean",
    "mustard": "Mustard",
    "groundnut": "Groundnut",
    "potato": "Potato", "potatoes": "Potato",
    "onion": "Onion",
    "tomato": "Tomato", "tomatoes": "Tomato",
    "banana": "Banana",
    "mango": "Mango",
    "coconut": "Coconut",
    "coffee": "Coffee",
    "tea": "Tea",
    "rubber": "Rubber",
    "pepper": "Pepper", "black pepper": "Pepper",
    "cashew": "Cashew", "cashewnut": "Cashew",
    "orange": "Orange", "oranges": "Orange",
    "grape": "Grape", "grapes": "Grape",
    "apple": "Apple", "apples": "Apple", "apple (high yield)": "Apple",
    "jute": "Jute",
    "barley": "Barley",
    "sesame": "Sesame",
    "sunflower": "Sunflower",
    "tobacco": "Tobacco",
    "turmeric": "Turmeric",
    "ginger": "Ginger",
    "gram": "Chickpea",
    "lentil": "Lentil", "lentils": "Lentil", "lentil (masoor)": "Lentil",
    "pea": "Pea", "peas": "Pea",
    "millets": "Millet", "millet": "Millet", "minor millets": "Millet",
    "beans": "Beans",
    "cabbage": "Cabbage",
    "capsicum": "Capsicum",
    "cauliflower": "Cauliflower",
    "chilli": "Chilli", "chillies": "Chilli",
    "coriander": "Coriander",
    "cumin": "Cumin",
    "fenugreek": "Fenugreek",
    "garlic": "Garlic",
    "guava": "Guava",
    "jackfruit": "Jackfruit",
    "litchi": "Litchi",
    "niger": "Niger",
    "opium": "Opium",
    "pineapple": "Pineapple",
    "pomegranate": "Pomegranate",
    "brinjal": "Brinjal",
    "saffron": "Saffron",
    "tapioca": "Tapioca",
    "walnut": "Walnut",
    "plums": "Plum", "pears": "Pear", "apricot": "Apricot",
    "bamboo": "Bamboo",
    "arecanut": "Arecanut",
    "castor": "Castor",
    "linseed": "Linseed",
    "breadfruit": "Breadfruit",
    "yam": "Yam",
    "buckwheat": "Buckwheat",
    "mulberry": "Mulberry", "mulberry (sericulture)": "Mulberry",
    "sericulture": "Mulberry",

    # Aliases with parenthetical names
    "bajra": "Pearl Millet", "bajra (pearl millet)": "Pearl Millet",
    "jowar": "Sorghum", "jowar (sorghum)": "Sorghum",
    "ragi": "Finger Millet", "ragi (finger millet)": "Finger Millet",
    "finger millet (ragi)": "Finger Millet",
    "mandua": "Finger Millet", "mandua (finger millet)": "Finger Millet",
    "kodo millet": "Millet", "kodo-kutki": "Millet",
    "tur (pigeon pea)": "Pigeonpea",
    "arhar": "Pigeonpea", "arhar (pigeon pea)": "Pigeonpea",
    "red gram": "Pigeonpea", "red gram (tur)": "Pigeonpea",
    "rajma": "Kidneybeans", "rajma (kidney beans)": "Kidneybeans",
    "bengal gram": "Chickpea",
    "moong": "Mungbean", "green gram": "Mungbean",
    "urad": "Blackgram",
    "mentha (mint)": "Mentha",
    "aonla (gooseberry)": "Gooseberry",
    "large cardamom": "Cardamom", "cardamom": "Cardamom",
    "mango (notably alphonso)": "Mango",

    # Broken fragments from comma-inside-parentheses splits
    "boro)": None,
    "brinjal)": None,
    "spinach)": None,
    "herbs)": None,

    # Fragment entries from "crop1, and crop2" patterns
    "and gram": "Chickpea",
    "and maize": "Maize",
    "and mustard.": "Mustard",
    "and oilseeds": None,
    "and paddy": "Rice",
    "and pulses": None,
    "and soybean": "Soybean",
    "and wheat": "Wheat",

    # Non-crop entries
    "urban area": None,
    "urban area; limited agriculture (terrace farming: vegetables": None,
    "urban area; minimal agricultural activity": None,
    "urban crops: spinach": None,
    "urban farming: vegetables": None,
    "greens (urban/peri-urban)": None,
    "limited cultivation": None,
    "limited vegetables": None,
    "minimal cultivation": None,
    "small farms": None,
    "terrace gardening": None,

    # Generic category entries — too vague to train on
    "fruits": None,
    "pulses": None,
    "oilseeds": None,
    "vegetables": None,
    "tubers": None,
    "tuber crops": None,
    "greens": None,
    "flowers": None,
    "spices": None,
    "seasonal vegetables": None,
    "citrus": None,
    "citrus fruits": None,
}


def normalize_crop_name(raw: str) -> str | None:
    """Returns the canonical crop name, or None if the entry should be discarded."""
    # Strip zero-width spaces, trailing punctuation, extra whitespace
    cleaned = raw.replace("​", "").strip().rstrip(".")
    key = cleaned.lower()

    if key in CROP_NAME_MAP:
        return CROP_NAME_MAP[key]

    # Strip parenthetical qualifiers and try again
    without_parens = re.sub(r"\s*\(.*?\)\s*", "", cleaned).strip()
    key_no_parens = without_parens.lower()
    if key_no_parens in CROP_NAME_MAP:
        return CROP_NAME_MAP[key_no_parens]

    # Compound descriptors like "Fruits like Mango and Cashew" — discard
    if key.startswith(("fruits like", "vegetables (", "seasonal vegetables (")):
        return None

    # If nothing matched, title-case and keep it
    return without_parens.title() if without_parens else None


def explode_crops(df: pd.DataFrame) -> pd.DataFrame:
    """
    Splits multi-crop rows into one-row-per-crop, normalizes names,
    and drops invalid entries.
    """
    df = df.copy()
    df["crop_list"] = df["Crop"].apply(split_crop_field)
    df = df.explode("crop_list").reset_index(drop=True)
    df["crop_clean"] = df["crop_list"].apply(normalize_crop_name)

    # Drop rows where the crop was discarded
    df = df.dropna(subset=["crop_clean"]).reset_index(drop=True)

    # Drop crops with too few samples to train reliably
    counts = df["crop_clean"].value_counts()
    valid_crops = counts[counts >= MIN_SAMPLES].index
    df = df[df["crop_clean"].isin(valid_crops)].reset_index(drop=True)

    return df


# ── Step 2 & 3: Feature engineering ─────────────────────────────────────────

SOIL_PERCENT_COLS = [
    "Nitrogen - High", "Nitrogen - Medium", "Nitrogen - Low",
    "Phosphorous - High", "Phosphorous - Medium", "Phosphorous - Low",
    "Potassium - High", "Potassium - Medium", "Potassium - Low",
    "pH - Acidic", "pH - Neutral", "pH - Alkaline",
]


def pct_to_float(val) -> float:
    if pd.isna(val):
        return 0.0
    s = str(val).strip().rstrip("%")
    try:
        return float(s)
    except ValueError:
        return 0.0


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Convert all percentage columns to numeric
    for col in SOIL_PERCENT_COLS:
        df[col] = df[col].apply(pct_to_float)

    # Weighted nutrient scores: High*2 + Medium*1 + Low*0
    df["N_score"] = df["Nitrogen - High"] * 2 + df["Nitrogen - Medium"]
    df["P_score"] = df["Phosphorous - High"] * 2 + df["Phosphorous - Medium"]
    df["K_score"] = df["Potassium - High"] * 2 + df["Potassium - Medium"]

    # pH composite: higher = more alkaline
    df["pH_score"] = df["pH - Alkaline"] * 2 + df["pH - Neutral"] - df["pH - Acidic"]

    return df


FEATURE_COLS = [
    # Location
    "Latitude", "Longitude",
    # Raw soil distributions
    "Nitrogen - High", "Nitrogen - Medium", "Nitrogen - Low",
    "Phosphorous - High", "Phosphorous - Medium", "Phosphorous - Low",
    "Potassium - High", "Potassium - Medium", "Potassium - Low",
    "pH - Acidic", "pH - Neutral", "pH - Alkaline",
    # Engineered scores
    "N_score", "P_score", "K_score", "pH_score",
]


# ── Step 4-7: Training and saving ───────────────────────────────────────────

def train_and_save():
    if not CSV_PATH.exists():
        print(f"ERROR: Dataset not found at {CSV_PATH}")
        return

    # Step 1: Load and clean
    print("Loading dataset...")
    df_raw = load_and_clean(CSV_PATH)
    print(f"  Raw rows: {len(df_raw)}")

    # Step 1b: Explode multi-crop rows into single-label rows
    print("Splitting multi-crop rows...")
    df = explode_crops(df_raw)
    print(f"  Rows after explode: {len(df)}")
    print(f"  Unique crops: {df['crop_clean'].nunique()}")
    print(f"  Crops: {sorted(df['crop_clean'].unique())}")

    # Step 2-3: Build feature matrix
    print("Engineering features...")
    df = build_features(df)

    X = df[FEATURE_COLS].values
    if np.any(~np.isfinite(X)):
        print("  WARNING: non-finite values in features, replacing with 0")
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    # Step 4: Encode target variable
    le = LabelEncoder()
    y = le.fit_transform(df["crop_clean"])
    print(f"  Features shape: {X.shape}")
    print(f"  Classes: {len(le.classes_)}")

    # Step 5: Train/test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    # Step 5b: Train RandomForest
    print("\nTraining RandomForest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=3,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    # Step 5c: Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0))

    # Feature importance
    importances = sorted(
        zip(FEATURE_COLS, model.feature_importances_),
        key=lambda x: x[1], reverse=True,
    )
    print("Feature importance (top 10):")
    for name, imp in importances[:10]:
        print(f"  {name:25s} {imp:.4f}")

    # Step 7: Save all artifacts
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    model_path = OUT_DIR / "model.pkl"
    le_path    = OUT_DIR / "label_encoder.pkl"
    feat_path  = OUT_DIR / "feature_cols.pkl"

    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    with open(le_path, "wb") as f:
        pickle.dump(le, f)
    with open(feat_path, "wb") as f:
        pickle.dump(FEATURE_COLS, f)

    print(f"\nSaved:")
    print(f"  Model:         {model_path}")
    print(f"  LabelEncoder:  {le_path}")
    print(f"  Feature cols:  {feat_path}")
    print(f"\nDone. {len(le.classes_)} crops, {X.shape[1]} features, {accuracy:.2%} accuracy.")


if __name__ == "__main__":
    train_and_save()
