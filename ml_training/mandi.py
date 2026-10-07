import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "final_data.csv"
# =====================================================
# FILES
# =====================================================

#INPUT_FILE = "final_data.csv"
OUTPUT_FILE = BASE_DIR /"clean_mandis2.csv"

# =====================================================
# CLEAN MARKET NAME
# =====================================================

def clean_market_name(name):

    if pd.isna(name):
        return ""

    name = str(name).strip()

    patterns = [

        r',?\s*RBZ$',
        r'\(RBZ\)',
        r'\(Rythu\s*Bazar\)',
        r'\(MGH\)',
        r'APMC',
        r'Market\s*Yard',
        r'Sub\s*Yard',
        r'Regulated\s*Market',
        r'Principal\s*Market',
        r'Satellite\s*Market'
    ]

    for pattern in patterns:

        name = re.sub(
            pattern,
            '',
            name,
            flags=re.IGNORECASE
        )

    name = re.sub(r'\(\)', '', name)
    name = re.sub(r',$', '', name)
    name = re.sub(r'\s+', ' ', name)

    return name.strip()

# =====================================================
# LOAD CSV
# =====================================================

print("Loading CSV...")

df = pd.read_csv(INPUT_FILE)

print(f"Original Rows: {len(df)}")

# =====================================================
# VERIFY REQUIRED COLUMNS
# =====================================================

required_cols = [
    "State",
    "District",
    "Market",
    "Market_code"
]

missing = [
    col for col in required_cols
    if col not in df.columns
]

if missing:

    raise ValueError(
        f"Missing columns: {missing}"
    )

# =====================================================
# KEEP ONLY REQUIRED COLUMNS
# =====================================================

df = df[
    [
        "State",
        "District",
        "Market",
        "Market_code"
    ]
].copy()

# =====================================================
# CLEAN STATE / DISTRICT
# =====================================================

for col in ["State", "District"]:

    df[col] = (

        df[col]
        .astype(str)
        .str.strip()
        .str.replace(
            r"\s+",
            " ",
            regex=True
        )
    )

# =====================================================
# CLEAN MARKET NAMES
# =====================================================

df["Market"] = df["Market"].apply(
    clean_market_name
)

# =====================================================
# REMOVE EMPTY ROWS
# =====================================================

df = df.dropna(
    subset=[
        "State",
        "District",
        "Market"
    ]
)

df = df[
    df["Market"] != ""
]

# =====================================================
# REMOVE DUPLICATES
# =====================================================

before = len(df)

df = df.drop_duplicates(

    subset=[
        "State",
        "District",
        "Market"
    ]
)

after = len(df)

print(
    f"Duplicates Removed: {before-after}"
)

# =====================================================
# CLEAN MARKET CODE
# =====================================================

df["Market_code"] = (

    pd.to_numeric(
        df["Market_code"],
        errors="coerce"
    )

    .fillna(0)

    .astype(int)
)

# =====================================================
# SORT
# =====================================================

df = df.sort_values(

    by=[
        "State",
        "District",
        "Market"
    ]
)

# =====================================================
# SAVE
# =====================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# =====================================================
# SUMMARY
# =====================================================

print("\n===================================")
print("MANDI CLEANING COMPLETE")
print("===================================")

print(
    f"Final Rows: {len(df)}"
)

print(
    f"Unique Districts: {df['District'].nunique()}"
)

print(
    f"Unique Markets: {df['Market'].nunique()}"
)

print(
    f"\nSaved File: {OUTPUT_FILE}"
)

print("\nSample Data:\n")

print(df.head(20))