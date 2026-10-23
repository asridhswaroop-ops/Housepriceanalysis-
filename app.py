"""
House Price Prediction & Analysis Dashboard
Completely redesigned with Modern Executive Analytics UI Theme.
"""
import io
import os
import re
import numpy as np
import pandas as pd
import streamlit as st

# Utility imports
from utils.data_processing import (
    clean_and_preprocess_dataset,
    compute_insights,
    compute_kpis,
    format_inr,
)
from utils.prediction import (
    predict_single_house_price,
    train_house_price_model,
)
from utils.ui import (
    inject_custom_css,
    render_kpi_row,
)
from utils.visualization import (
    plot_area_vs_price,
    plot_bedrooms_vs_price,
    plot_correlation_heatmap,
    plot_feature_importance,
    plot_price_by_location,
    plot_price_distribution,
)

def render_header(title="House Price Prediction & Analysis", subtitle="Interactive Housing Market Analytics Dashboard"):
    """
    Renders an attractive, modern executive dashboard header banner without any redundant project badge.
    Defined directly in app.py to eliminate any submodule caching issues.
    """
    st.markdown(f"""
    <div class="modern-header-banner">
        <div class="header-title-box">
            <div class="header-brand-pill">
                <span>🏠</span>
                <span>Real Estate Intelligence Suite</span>
            </div>
            <h1 style="color: #0f172a !important; font-weight: 800; margin: 0; font-size: 1.85rem; letter-spacing: -0.025em;">{title}</h1>
            <p style="color: #475569 !important; font-size: 0.95rem; margin: 5px 0 0 0;">{subtitle}</p>
        </div>
        <div class="header-meta-group">
            <div class="header-meta-pill">
                <span class="live-status-dot"></span>
                <span style="color: #1e293b !important; font-size: 0.82rem; font-weight: 600;">Live Market Analytics</span>
            </div>
            <div class="header-meta-pill">
                <span style="font-size: 0.85rem;">⚡</span>
                <span style="color: #1e293b !important; font-size: 0.82rem; font-weight: 600;">ML Valuation Engine</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def find_column(df, candidates):
    """
    Safely finds the first matching column in df from candidate names.
    Defined directly in app.py to prevent any submodule caching issues.
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

def safe_button(label, width="stretch", **kwargs):
    """
    Renders st.button with modern width parameter, falling back gracefully for older versions.
    """
    try:
        return st.button(label, width=width, **kwargs)
    except TypeError:
        use_cw = (width == "stretch")
        return st.button(label, use_container_width=use_cw, **kwargs)

def safe_form_submit_button(label, width="stretch", **kwargs):
    """
    Renders st.form_submit_button with modern width parameter, falling back gracefully for older versions.
    """
    try:
        return st.form_submit_button(label, width=width, **kwargs)
    except TypeError:
        use_cw = (width == "stretch")
        return st.form_submit_button(label, use_container_width=use_cw, **kwargs)

def render_chart(fig):
    """
    Renders Plotly chart with modern width parameter, suppressing deprecation warnings.
    """
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)

def render_dataframe(df, height=None):
    """
    Renders dataframe with modern width parameter, safely handling height.
    """
    kwargs = {}
    if height is not None:
        kwargs["height"] = height
    try:
        st.dataframe(df, width="stretch", **kwargs)
    except Exception:
        st.dataframe(df, use_container_width=True, **kwargs)

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="House Price Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Clean Professional CSS
inject_custom_css()

# -----------------------------------------------------------------------------
# 2. Cached Data Loading & Model Retrieval
# -----------------------------------------------------------------------------
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "house_prices.csv")

@st.cache_data
def load_and_prepare_data(file_bytes=None, file_name=None):
    if file_bytes is not None:
        try:
            if file_name and file_name.endswith(('.xlsx', '.xls')):
                df_raw = pd.read_excel(io.BytesIO(file_bytes))
            else:
                df_raw = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as e:
            return None, {}, {"error": f"Failed to parse file: {str(e)}"}
    else:
        if not os.path.exists(DEFAULT_DATA_PATH):
            return None, {}, {"error": f"Default dataset not found at {DEFAULT_DATA_PATH}"}
        df_raw = pd.read_csv(DEFAULT_DATA_PATH)

    df_clean, col_mapping, quality_report = clean_and_preprocess_dataset(df_raw)
    return df_clean, col_mapping, quality_report

@st.cache_resource
def get_trained_model(data_hash, _df_clean, col_mapping_tuple):
    col_mapping = dict(col_mapping_tuple)
    return train_house_price_model(_df_clean, col_mapping)

def reset_all_filters():
    for key in list(st.session_state.keys()):
        if key.startswith("filter_"):
            del st.session_state[key]

# -----------------------------------------------------------------------------
# 3. Sidebar Redesign (Dark Navy, Brand, Compact Sections, Filters)
# -----------------------------------------------------------------------------
with st.sidebar:
    # Sidebar Brand Header
    st.markdown("""
    <div class="sidebar-brand-box">
        <div class="sidebar-brand-title">House Price<br>Analyzer</div>
        <div class="sidebar-brand-subtitle">Prediction & Market Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation-style quick anchors
    st.markdown("""
    <div style="margin-bottom: 12px;">
        <a href="#kpi-section" class="sidebar-nav-item">📊 Dashboard</a>
        <a href="#dataset-section" class="sidebar-nav-item">📁 Dataset</a>
        <a href="#market-analysis" class="sidebar-nav-item">📈 Market Analysis</a>
        <a href="#prediction-section" class="sidebar-nav-item">🤖 Price Prediction</a>
        <a href="#explorer-section" class="sidebar-nav-item">🔍 Data Explorer</a>
    </div>
    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.12); margin: 14px 0;">
    """, unsafe_allow_html=True)

    # Dataset Upload Section
    st.markdown("<p style='font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8 !important; margin-bottom: 6px;'>DATASET</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload Housing CSV / Excel",
        type=["csv", "xlsx", "xls"],
        help="Upload custom housing records or use default sample."
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name
        source_label = f"Uploaded: {file_name}"
    else:
        file_bytes = None
        file_name = "house_prices.csv"
        source_label = "house_prices.csv (Default)"

    # Load data
    df_clean, col_mapping, quality_report = load_and_prepare_data(file_bytes, file_name)

    if df_clean is None:
        st.error(quality_report.get("error", "Error loading dataset."))
        st.stop()

    # Small Status Card
    st.markdown(f"""
    <div class="sidebar-status-card">
        <div style="font-weight: 700; color: #ffffff !important; margin-bottom: 4px;">
            <span class="status-dot"></span>Dataset Status: Loaded
        </div>
        <div style="color: #cbd5e1 !important; font-size: 0.78rem;">
            Source: {source_label}
        </div>
        <div style="color: #cbd5e1 !important; font-size: 0.78rem; margin-top: 2px;">
            Records: <b>{len(df_clean):,}</b> &nbsp;|&nbsp; Features: <b>{len(df_clean.columns)}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.12); margin: 12px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8 !important; margin-bottom: 8px;'>FILTERS</p>", unsafe_allow_html=True)

    # Centralized robust column detection
    p_col = col_mapping.get("price") or find_column(df_clean, ["Price", "price", "SalePrice", "Cost"])
    a_col = col_mapping.get("area") or find_column(df_clean, ["Area", "area", "Sqft", "Square Feet"])
    loc_col = col_mapping.get("location") or find_column(df_clean, ["Location", "location", "City", "Locality"])
    bed_col = col_mapping.get("bedrooms") or find_column(df_clean, ["Bedrooms", "bedroom", "Beds", "bhk"])
    bath_col = col_mapping.get("bathrooms") or find_column(df_clean, ["Bathrooms", "bathroom", "Baths"])
    yr_col = col_mapping.get("year_built") or find_column(df_clean, ["Year Built", "year_built", "YearBuilt", "Year"])
    park_col = col_mapping.get("parking") or find_column(df_clean, ["Parking", "parking", "Garage"])
    furn_col = col_mapping.get("furnishing") or find_column(df_clean, ["Furnishing", "furnishing", "Furnished"])

    filtered_df = df_clean.copy()

    # 1. Location Filter
    if loc_col and loc_col in filtered_df.columns:
        loc_options = sorted(filtered_df[loc_col].dropna().unique().tolist())
        selected_locs = st.multiselect(
            "Location",
            options=loc_options,
            key="filter_location"
        )
        if selected_locs:
            filtered_df = filtered_df[filtered_df[loc_col].isin(selected_locs)]

    # 2. Bedrooms Filter (Range Slider computed from full dataset)
    if bed_col and bed_col in filtered_df.columns:
        min_b = int(df_clean[bed_col].min())
        max_b = int(df_clean[bed_col].max())
        if min_b < max_b:
            selected_b = st.slider(
                "Bedrooms",
                min_value=min_b,
                max_value=max_b,
                value=(min_b, max_b),
                key="filter_bedrooms"
            )
            filtered_df = filtered_df[
                (filtered_df[bed_col] >= selected_b[0]) & (filtered_df[bed_col] <= selected_b[1])
            ]

    # 3. Bathrooms Filter (Range Slider computed from full dataset)
    if bath_col and bath_col in filtered_df.columns:
        min_ba = int(df_clean[bath_col].min())
        max_ba = int(df_clean[bath_col].max())
        if min_ba < max_ba:
            selected_ba = st.slider(
                "Bathrooms",
                min_value=min_ba,
                max_value=max_ba,
                value=(min_ba, max_ba),
                key="filter_bathrooms"
            )
            filtered_df = filtered_df[
                (filtered_df[bath_col] >= selected_ba[0]) & (filtered_df[bath_col] <= selected_ba[1])
            ]

    # 4. Price Range Filter (Range Slider)
    if p_col and p_col in filtered_df.columns:
        min_p = float(df_clean[p_col].min())
        max_p = float(df_clean[p_col].max())
        if min_p < max_p:
            selected_p = st.slider(
                "Price Range (₹)",
                min_value=min_p,
                max_value=max_p,
                value=(min_p, max_p),
                step=100000.0,
                format="₹%d",
                key="filter_price"
            )
            filtered_df = filtered_df[
                (filtered_df[p_col] >= selected_p[0]) & (filtered_df[p_col] <= selected_p[1])
            ]

    # Reset Filters Button
    st.markdown('<div class="sidebar-reset-btn" style="margin-top: 12px;">', unsafe_allow_html=True)
    if safe_button("↻ Reset Filters", width="stretch"):
        reset_all_filters()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"<div style='font-size: 0.78rem; color: #94a3b8 !important; text-align: center; margin-top: 10px;'>Showing <b>{len(filtered_df):,}</b> of <b>{len(df_clean):,}</b> listings</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. Main Header Section
# -----------------------------------------------------------------------------
st.markdown("<div id='kpi-section'></div>", unsafe_allow_html=True)
render_header(
    title="House Price Prediction & Analysis",
    subtitle="Interactive Housing Market Analytics Dashboard"
)

# -----------------------------------------------------------------------------
# 5. Top 5 KPI Cards Section (Pastel Colors, Robust Against KeyError)
# -----------------------------------------------------------------------------
kpis = compute_kpis(filtered_df, col_mapping)
render_kpi_row(kpis)

if filtered_df.empty:
    st.warning("⚠️ No properties match the current filter selection. Please reset or loosen your filters in the sidebar.")
    st.stop()

# -----------------------------------------------------------------------------
# 6. Market Insights Card
# -----------------------------------------------------------------------------
insights = compute_insights(filtered_df, col_mapping)
st.markdown("""
<div class="analytics-card">
    <div class="analytics-card-header">
        <h3 class="analytics-card-title" style="color: #0f172a !important; font-weight: 700; margin: 0;">📌 Market Insights</h3>
    </div>
""", unsafe_allow_html=True)

ins_col1, ins_col2 = st.columns(2)
for idx, ins in enumerate(insights):
    target = ins_col1 if idx % 2 == 0 else ins_col2
    with target:
        st.markdown(f'<div class="insight-pill">• {ins}</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 7. Main Analytics Area (Row 1: Price Distribution & Location Analysis)
# -----------------------------------------------------------------------------
st.markdown("<div id='market-analysis'></div>", unsafe_allow_html=True)
st.markdown("""
<div class="analytics-card">
    <div class="analytics-card-header">
        <div>
            <h3 class="analytics-card-title" style="color: #0f172a !important; font-weight: 700; margin: 0;">📊 Market Overview</h3>
            <p class="analytics-card-subtitle" style="color: #475569 !important; margin-top: 3px;">Exploratory distribution and geographic pricing trends</p>
        </div>
    </div>
""", unsafe_allow_html=True)

chart1_col, chart2_col = st.columns(2)

with chart1_col:
    if p_col:
        fig_dist = plot_price_distribution(filtered_df, p_col)
        render_chart(fig_dist)
    else:
        st.info("Price distribution is unavailable because the dataset does not contain a price column.")

with chart2_col:
    if loc_col and p_col:
        fig_loc = plot_price_by_location(filtered_df, loc_col, p_col)
        render_chart(fig_loc)
    else:
        st.info("Location analysis is unavailable because the dataset does not contain a location column.")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. Second Chart Row (Row 2: Area vs Price & Bedroom Analysis)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="analytics-card">
    <div class="analytics-card-header">
        <div>
            <h3 class="analytics-card-title" style="color: #0f172a !important; font-weight: 700; margin: 0;">📐 Property Dimensionality & Configuration</h3>
            <p class="analytics-card-subtitle" style="color: #475569 !important; margin-top: 3px;">Correlation of built-up space and bedroom counts with valuation</p>
        </div>
    </div>
""", unsafe_allow_html=True)

chart3_col, chart4_col = st.columns(2)

with chart3_col:
    if a_col and p_col:
        fig_area = plot_area_vs_price(
            filtered_df,
            area_col=a_col,
            price_col=p_col,
            loc_col=loc_col,
            bed_col=bed_col,
            bath_col=bath_col
        )
        render_chart(fig_area)
    else:
        st.info("Area vs Price analysis is unavailable because area or price columns are missing.")

with chart4_col:
    if bed_col and p_col:
        fig_bed = plot_bedrooms_vs_price(filtered_df, bed_col, p_col)
        render_chart(fig_bed)
    else:
        st.info("Bedroom analysis is unavailable because bedroom or price columns are missing.")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. Correlation & Feature Analysis
# -----------------------------------------------------------------------------
st.markdown("""
<div class="analytics-card">
    <div class="analytics-card-header">
        <div>
            <h3 class="analytics-card-title" style="color: #0f172a !important; font-weight: 700; margin: 0;">📊 Feature Analysis</h3>
            <p class="analytics-card-subtitle" style="color: #475569 !important; margin-top: 3px;">Automated correlation matrix across all numerical housing features</p>
        </div>
    </div>
""", unsafe_allow_html=True)

numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
numeric_feature_cols = [c for c in numeric_cols if not any(x in c.lower() for x in ["id", "index", "unnamed"])]

if len(numeric_feature_cols) >= 2:
    fig_corr = plot_correlation_heatmap(filtered_df, numeric_feature_cols)
    render_chart(fig_corr)
else:
    st.info("Feature analysis is unavailable: Not enough numerical columns detected.")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 10. Machine Learning Price Prediction Section
# -----------------------------------------------------------------------------
st.markdown("<div id='prediction-section'></div>", unsafe_allow_html=True)
st.markdown("""
<div class="analytics-card">
    <div class="analytics-card-header">
        <div>
            <h3 class="analytics-card-title" style="color: #0f172a !important; font-weight: 700; margin: 0;">🤖 House Price Prediction</h3>
            <p class="analytics-card-subtitle" style="color: #475569 !important; margin-top: 3px;">Estimate the expected property price using the trained machine-learning model.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Train or retrieve cached model
data_hash = int(pd.util.hash_pandas_object(df_clean, index=True).sum())
model_tuple = tuple(sorted(col_mapping.items()))
model_res = get_trained_model(data_hash, df_clean, model_tuple)

if model_res["status"] == "error":
    st.warning(f"⚠️ {model_res['message']}")
else:
    pipeline = model_res["pipeline"]
    metrics = model_res["metrics"]
    all_features = model_res["all_features"]
    feature_names = model_res["feature_names"]
    importances = model_res["importances"]
    model_name_disp = model_res.get("model_name", "Random Forest Regression")

    # Clean input form in 2 or 3 columns
    with st.form("clean_prediction_form"):
        st.markdown("<h5 style='color: #0f172a !important; font-weight: 700; margin-bottom: 12px;'>Enter Property Specifications</h5>", unsafe_allow_html=True)
        f_c1, f_c2, f_c3 = st.columns(3)
        input_data = {}

        if a_col:
            col_series_a = df_clean[a_col].dropna()
            if not col_series_a.empty:
                data_min_a = float(col_series_a.min())
                data_max_a = float(col_series_a.max())
                area_min = max(1, int(data_min_a * 0.8))
                area_max = max(area_min + 100, int(data_max_a * 1.2))
                default_a = int(col_series_a.median())
            else:
                area_min, area_max, default_a = 100, 20000, 1500
            default_a = max(area_min, min(area_max, default_a))
            with f_c1:
                input_data[a_col] = st.number_input(
                    "Area (Square Feet)",
                    min_value=area_min,
                    max_value=area_max,
                    value=default_a,
                    step=50,
                    help="Total carpet or super built-up area in sqft"
                )

        if bed_col:
            unique_b = sorted([int(x) for x in df_clean[bed_col].dropna().unique()])
            default_b_idx = min(2, len(unique_b) - 1)
            with f_c2:
                input_data[bed_col] = st.selectbox(
                    "Bedrooms (BHK)",
                    options=unique_b,
                    index=default_b_idx
                )

        if bath_col:
            unique_ba = sorted([int(x) for x in df_clean[bath_col].dropna().unique()])
            with f_c3:
                input_data[bath_col] = st.selectbox(
                    "Bathrooms",
                    options=unique_ba,
                    index=min(1, len(unique_ba) - 1)
                )

        if loc_col:
            unique_l = sorted(df_clean[loc_col].dropna().unique().tolist())
            with f_c1:
                input_data[loc_col] = st.selectbox(
                    "Location",
                    options=unique_l
                )

        if yr_col:
            col_series_y = df_clean[yr_col].dropna()
            if not col_series_y.empty:
                data_min_y = int(col_series_y.min())
                data_max_y = int(col_series_y.max())
                year_min = max(1800, data_min_y - 10)
                year_max = max(year_min + 5, max(data_max_y + 5, 2030))
                default_y = int(col_series_y.median())
            else:
                year_min, year_max, default_y = 1950, 2030, 2018
            default_y = max(year_min, min(year_max, default_y))
            with f_c2:
                input_data[yr_col] = st.number_input(
                    "Year Built",
                    min_value=year_min,
                    max_value=year_max,
                    value=default_y,
                    step=1
                )

        if park_col:
            unique_p = sorted(df_clean[park_col].dropna().unique().tolist())
            with f_c3:
                input_data[park_col] = st.selectbox(
                    "Parking",
                    options=unique_p
                )

        if furn_col:
            unique_f = sorted(df_clean[furn_col].dropna().unique().tolist())
            with f_c1:
                input_data[furn_col] = st.selectbox(
                    "Furnishing",
                    options=unique_f
                )

        # Extra columns if present
        handled_set = {a_col, bed_col, bath_col, loc_col, yr_col, park_col, furn_col}
        extra_cols = [f for f in all_features if f not in handled_set]
        for idx, feat in enumerate(extra_cols):
            target_sub = [f_c1, f_c2, f_c3][(idx + 1) % 3]
            with target_sub:
                if pd.api.types.is_numeric_dtype(df_clean[feat]):
                    input_data[feat] = st.number_input(feat, value=float(df_clean[feat].median()))
                else:
                    input_data[feat] = st.selectbox(feat, options=sorted(df_clean[feat].dropna().unique().tolist()))

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        predict_submit = safe_form_submit_button("🔮 Predict House Price", width="stretch")

    if predict_submit:
        try:
            pred_price = predict_single_house_price(pipeline, input_data, all_features)
            formatted_price = format_inr(pred_price)

            # Premium Prediction Result Card
            st.markdown(f"""
            <div class="prediction-hero-card">
                <div class="pred-label">ESTIMATED HOUSE PRICE</div>
                <div class="pred-value">{formatted_price}</div>
                <div class="pred-sub">Raw Exact Valuation: ₹ {pred_price:,.0f}</div>
                <div style="display: flex; justify-content: center; gap: 24px; margin-top: 14px; flex-wrap: wrap;">
                    <span style="font-size: 0.85rem; color: #475569;"><b>Model:</b> {model_name_disp}</span>
                    <span style="font-size: 0.85rem; color: #475569;"><b>R² Score:</b> {metrics['r2']:.3f}</span>
                    <span style="font-size: 0.85rem; color: #475569;"><b>MAE:</b> {format_inr(metrics['mae'])}</span>
                    <span style="font-size: 0.85rem; color: #475569;"><b>RMSE:</b> {format_inr(metrics['rmse'])}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error computing prediction: {str(e)}")

    # Feature Importance Chart
    if len(feature_names) > 0 and len(importances) > 0:
        with st.expander("📊 View Model Factors Driving House Price", expanded=False):
            fig_fi = plot_feature_importance(feature_names, importances)
            render_chart(fig_fi)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 11. Section: Dataset Explorer
# -----------------------------------------------------------------------------
st.markdown("<div id='explorer-section'></div>", unsafe_allow_html=True)
st.markdown("""
<div class="analytics-card">
    <div class="analytics-card-header">
        <div>
            <h3 class="analytics-card-title" style="color: #0f172a !important; font-weight: 700; margin: 0;">📋 Dataset Explorer</h3>
            <p class="analytics-card-subtitle" style="color: #475569 !important; margin-top: 3px;">Inspect, search, and export the processed dataset</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Summary counts row
e_c1, e_c2, e_c3, e_c4 = st.columns(4)
e_c1.metric("Number of Records", f"{len(filtered_df):,}")
e_c2.metric("Number of Columns", f"{len(filtered_df.columns)}")
e_c3.metric("Missing Values", f"{filtered_df.isnull().sum().sum()}")
e_c4.metric("Duplicate Rows", f"{filtered_df.duplicated().sum()}")

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
render_dataframe(filtered_df, height=360)

csv_out = io.StringIO()
filtered_df.to_csv(csv_out, index=False)
st.download_button(
    label="📥 Download Processed Dataset",
    data=csv_out.getvalue(),
    file_name="processed_house_prices.csv",
    mime="text/csv",
    help="Download active filtered dataset as CSV"
)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 12. Section: Data Quality Report
# -----------------------------------------------------------------------------
st.markdown("""
<div class="analytics-card">
    <div class="analytics-card-header">
        <div>
            <h3 class="analytics-card-title" style="color: #0f172a !important; font-weight: 700; margin: 0;">🔍 Data Quality</h3>
            <p class="analytics-card-subtitle" style="color: #475569 !important; margin-top: 3px;">Comprehensive data health diagnostics and schema verification</p>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.expander("Click to view complete Data Quality Diagnostics", expanded=False):
    dq_1, dq_2, dq_3, dq_4 = st.columns(4)
    dq_1.metric("Total Records Loaded", f"{quality_report.get('initial_rows', len(df_clean)):,}")
    dq_2.metric("Duplicate Rows Removed", f"{quality_report.get('duplicates_removed', 0):,}")
    dq_3.metric("Features Detected", f"{quality_report.get('total_columns', len(df_clean.columns))}")
    dq_4.metric("Imputed Cells", f"{quality_report.get('total_missing_cells', 0)}")

    st.markdown("<h5 style='color: #0f172a !important; font-weight: 700; margin-bottom: 8px;'>Column Schema & Type Verification</h5>", unsafe_allow_html=True)
    schema_df = pd.DataFrame({
        "Column Name": df_clean.columns,
        "Data Type": [str(t) for t in df_clean.dtypes],
        "Missing Values": [df_clean[c].isnull().sum() for c in df_clean.columns],
        "Unique Values": [df_clean[c].nunique() for c in df_clean.columns]
    })
    render_dataframe(schema_df)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.15;'>", unsafe_allow_html=True)
st.caption("House Price Prediction & Analysis Dashboard • Built with Python & Streamlit • 100% Python Native")
