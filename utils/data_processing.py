"""
Centralized data processing, column detection, cleaning, and metric calculation utilities.
"""
import re
import numpy as np
import pandas as pd

# Canonical column mapping aliases (lowercase stripped)
CANONICAL_ALIASES = {
    "price": ["price", "saleprice", "sale_price", "target_price", "house_price", "cost", "amount", "value"],
    "area": ["area", "sqft", "square_feet", "squarefeet", "size", "lot_size", "surface_area", "sq_ft"],
    "bedrooms": ["bedrooms", "bedroom", "beds", "bed", "bhk", "rooms", "num_bedrooms"],
    "bathrooms": ["bathrooms", "bathroom", "baths", "bath", "num_bathrooms"],
    "location": ["location", "city", "neighborhood", "locality", "suburb", "address", "area_name", "region", "branch"],
    "year_built": ["year built", "year_built", "yearbuilt", "built_year", "construction_year", "year"],
    "parking": ["parking", "garage", "parking_spaces", "parking_space", "car_parking"],
    "furnishing": ["furnishing", "furnishing_status", "furnished_status", "furnished"],
    "id": ["house id", "house_id", "id", "property_id", "pid", "roll"]
}

def find_column(df: pd.DataFrame, candidates: list) -> str | None:
    """
    Safely finds the first matching column in df from a list of candidates.
    Supports case-insensitive, stripped, and underscore/space variations.
    """
    if df is None or df.empty:
        return None

    normalized_cols = {col.strip().lower().replace("_", " "): col for col in df.columns}
    raw_normalized = {re.sub(r'[^a-zA-Z0-9]', '', col).lower(): col for col in df.columns}

    for candidate in candidates:
        norm_c = candidate.strip().lower().replace("_", " ")
        if norm_c in normalized_cols:
            return normalized_cols[norm_c]
        clean_c = re.sub(r'[^a-zA-Z0-9]', '', candidate).lower()
        if clean_c in raw_normalized:
            return raw_normalized[clean_c]

    return None

def identify_columns(df: pd.DataFrame) -> dict:
    """
    Identifies the canonical mapping for all available columns in the dataframe.
    """
    col_mapping = {}
    for canonical, aliases in CANONICAL_ALIASES.items():
        found = find_column(df, aliases)
        if found:
            col_mapping[canonical] = found
    return col_mapping

def clean_currency_or_number(series: pd.Series) -> pd.Series:
    """
    Cleans strings with currency symbols (₹, $) or commas and converts to numeric.
    """
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors='coerce')
    cleaned = series.astype(str).str.replace(r'[₹$,\s]', '', regex=True)
    return pd.to_numeric(cleaned, errors='coerce')

def clean_and_preprocess_dataset(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict, dict]:
    """
    Cleans and standardizes the dataset:
    - Removes duplicate rows.
    - Resolves canonical column mappings.
    - Converts numerical features to correct dtypes.
    - Imputes missing values safely without crashing.
    - Computes price_per_sqft if area and price are present.
    """
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(), {}, {
            "initial_rows": 0, "clean_rows": 0, "duplicates_removed": 0,
            "total_columns": 0, "total_missing_cells": 0, "numeric_columns": [], "categorical_columns": []
        }

    df = df_raw.copy()
    initial_rows = len(df)
    
    # 1. Remove duplicate rows
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)

    # 2. Identify canonical columns
    col_mapping = identify_columns(df)

    # 3. Clean numeric columns identified as canonical
    numeric_targets = ["price", "area", "bedrooms", "bathrooms", "year_built"]
    for canon in numeric_targets:
        if canon in col_mapping:
            actual_col = col_mapping[canon]
            df[actual_col] = clean_currency_or_number(df[actual_col])

    # 4. Fill missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val if not pd.isna(median_val) else 0)

    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    for col in cat_cols:
        if df[col].isnull().any():
            mode_val = df[col].mode()
            fill_val = mode_val[0] if not mode_val.empty else "Unknown"
            df[col] = df[col].fillna(fill_val)

    # 5. Price per sqft calculation
    if "price" in col_mapping and "area" in col_mapping:
        p_col = col_mapping["price"]
        a_col = col_mapping["area"]
        # avoid division by zero
        df["Price_per_sqft"] = np.where(df[a_col] > 0, df[p_col] / df[a_col], np.nan)
        col_mapping["price_per_sqft"] = "Price_per_sqft"

    quality_report = {
        "initial_rows": initial_rows,
        "clean_rows": len(df),
        "duplicates_removed": duplicates_removed,
        "total_columns": len(df.columns),
        "missing_values_count": df_raw.isnull().sum().to_dict(),
        "total_missing_cells": int(df_raw.isnull().sum().sum()),
        "numeric_columns": numeric_cols,
        "categorical_columns": cat_cols,
        "column_mapping": col_mapping
    }

    return df, col_mapping, quality_report

def format_inr(val) -> str:
    """
    Formats a numeric value into Indian Rupee style (Lakhs / Crores) or standard format.
    Example: 15,000,000 -> ₹ 1.50 Cr, 7,500,000 -> ₹ 75.00 L
    """
    if val is None or pd.isna(val):
        return "N/A"
    try:
        val = float(val)
        if abs(val) >= 10_000_000:
            return f"₹ {val / 10_000_000:.2f} Cr"
        elif abs(val) >= 100_000:
            return f"₹ {val / 100_000:.2f} L"
        else:
            return f"₹ {val:,.0f}"
    except (ValueError, TypeError):
        return str(val)

def compute_kpis(df: pd.DataFrame, col_mapping: dict = None) -> dict:
    """
    Centralized, ultra-robust KPI calculation function.
    Guarantees that every expected key exists with default fallbacks,
    completely preventing KeyError under all circumstances.
    """
    if col_mapping is None:
        col_mapping = identify_columns(df) if df is not None else {}

    kpis = {
        "total_properties": len(df) if df is not None else 0,
        "total_locations": 0,
        "avg_price": None,
        "avg_price_fmt": "N/A",
        "max_price": None,
        "max_price_fmt": "N/A",
        "min_price": None,
        "min_price_fmt": "N/A",
        "avg_area": None,
        "avg_area_fmt": "N/A",
        "total_records": len(df) if df is not None else 0,
        "missing_values": int(df.isnull().sum().sum()) if df is not None else 0,
        "total_columns": len(df.columns) if df is not None else 0
    }

    if df is None or df.empty:
        return kpis

    # 1. Location count
    loc_col = col_mapping.get("location") or find_column(df, ["Location", "location", "City", "Locality"])
    if loc_col and loc_col in df.columns:
        kpis["total_locations"] = int(df[loc_col].nunique())

    # 2. Price metrics
    price_col = col_mapping.get("price") or find_column(df, ["Price", "price", "SalePrice", "Cost"])
    if price_col and price_col in df.columns:
        valid_prices = pd.to_numeric(df[price_col], errors='coerce').dropna()
        if not valid_prices.empty:
            avg_p = float(valid_prices.mean())
            max_p = float(valid_prices.max())
            min_p = float(valid_prices.min())
            kpis["avg_price"] = avg_p
            kpis["avg_price_fmt"] = format_inr(avg_p)
            kpis["max_price"] = max_p
            kpis["max_price_fmt"] = format_inr(max_p)
            kpis["min_price"] = min_p
            kpis["min_price_fmt"] = format_inr(min_p)

    # 3. Area metrics
    area_col = col_mapping.get("area") or find_column(df, ["Area", "area", "Sqft", "Square Feet", "Size"])
    if area_col and area_col in df.columns:
        valid_areas = pd.to_numeric(df[area_col], errors='coerce').dropna()
        if not valid_areas.empty:
            avg_a = float(valid_areas.mean())
            kpis["avg_area"] = avg_a
            kpis["avg_area_fmt"] = f"{avg_a:,.0f} sqft"

    return kpis

# Alias for calculate_kpis as requested in user specification
calculate_kpis = compute_kpis

def compute_insights(df: pd.DataFrame, col_mapping: dict = None) -> list[str]:
    """
    Generates dynamic, data-driven key insights directly from the actual dataset.
    """
    insights = []
    if df is None or df.empty:
        return ["No property data available under current filter selection."]

    if col_mapping is None:
        col_mapping = identify_columns(df)

    p_col = col_mapping.get("price") or find_column(df, ["Price", "price", "SalePrice"])
    a_col = col_mapping.get("area") or find_column(df, ["Area", "area", "Sqft"])
    loc_col = col_mapping.get("location") or find_column(df, ["Location", "location", "City"])
    bed_col = col_mapping.get("bedrooms") or find_column(df, ["Bedrooms", "bedroom", "Beds", "bhk"])
    sqft_col = col_mapping.get("price_per_sqft")

    # 1. Average price
    if p_col and p_col in df.columns:
        valid_p = df[p_col].dropna()
        if not valid_p.empty:
            avg_p = valid_p.mean()
            insights.append(f"Average property price is **{format_inr(avg_p)}**.")

    # 2. Top location
    if loc_col and p_col and loc_col in df.columns and p_col in df.columns:
        loc_avg = df.groupby(loc_col)[p_col].mean()
        if not loc_avg.empty:
            top_loc = loc_avg.idxmax()
            top_price = loc_avg.max()
            insights.append(f"Location **{top_loc}** has the highest average property price ({format_inr(top_price)}).")

    # 3. Bedroom percentage
    if bed_col and bed_col in df.columns:
        bed_counts = df[bed_col].value_counts(normalize=True)
        if not bed_counts.empty:
            most_common_bed = bed_counts.idxmax()
            pct = bed_counts.max() * 100
            insights.append(f"**{int(most_common_bed) if isinstance(most_common_bed, (int, float)) else most_common_bed}-bedroom** properties represent **{pct:.1f}%** of the current dataset.")

    # 4. Average price per sqft
    if sqft_col and sqft_col in df.columns:
        valid_sqft = df[sqft_col].dropna()
        if not valid_sqft.empty:
            avg_sq = valid_sqft.mean()
            insights.append(f"Average price per sqft across listings is **{format_inr(avg_sq)}/sqft**.")
    elif p_col and a_col and p_col in df.columns and a_col in df.columns:
        valid_both = df[(df[a_col] > 0) & (df[p_col] > 0)]
        if not valid_both.empty:
            avg_sq = (valid_both[p_col] / valid_both[a_col]).mean()
            insights.append(f"Average price per sqft across listings is **{format_inr(avg_sq)}/sqft**.")

    # 5. Average area
    if a_col and a_col in df.columns:
        valid_a = df[a_col].dropna()
        if not valid_a.empty:
            avg_area = valid_a.mean()
            insights.append(f"The average property area across listings is **{avg_area:,.0f} sqft**.")

    return insights
