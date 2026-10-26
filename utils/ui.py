"""
UI components and reusable rendering utilities for House Price Analytics Dashboard.
"""
import streamlit as st

def inject_custom_css():
    """
    Injects professional CSS matching the reference design:
    - Clean off-white background
    - Deep royal navy sidebar with compact, styled inputs
    - Subtle pastel KPI cards with rounded corners
    - Clean white cards with light borders and soft shadows
    - High-contrast typography
    """
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Hide Streamlit Deploy button and 3-dots menu, keeping Header & Toolbar intact for Sidebar controls */
        #MainMenu,
        [data-testid="stDeployButton"],
        [data-testid="stToolbarActions"],
        [data-testid="stDecoration"],
        header [data-testid="stDeployButton"],
        header #MainMenu,
        header [data-testid="stToolbarActions"] {
            visibility: hidden !important;
            display: none !important;
            height: 0 !important;
            width: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* Header and Toolbar: Keep transparent, allow interactions */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* Allow interactions on toolbar */
        [data-testid="stToolbar"] {
            visibility: visible !important;
            display: flex !important;
            opacity: 1 !important;
        }

        /* Expand sidebar button (floating at top-left when sidebar is collapsed) */
        [data-testid="stExpandSidebarButton"],
        [data-testid="stSidebarCollapsedControl"] {
            visibility: visible !important;
            display: flex !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            z-index: 999999 !important;
            position: fixed !important;
            top: 14px !important;
            left: 14px !important;
        }

        [data-testid="stExpandSidebarButton"] button,
        [data-testid="stSidebarCollapsedControl"] button {
            color: #1e3a8a !important;
            background: #ffffff !important;
            border: 1.5px solid #3b82f6 !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
            padding: 6px 10px !important;
            min-height: 36px !important;
            min-width: 36px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stExpandSidebarButton"] button:hover,
        [data-testid="stSidebarCollapsedControl"] button:hover {
            background: #eff6ff !important;
            border-color: #1d4ed8 !important;
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35) !important;
            transform: scale(1.05) !important;
        }
        [data-testid="stExpandSidebarButton"] button svg,
        [data-testid="stExpandSidebarButton"] button span,
        [data-testid="stSidebarCollapsedControl"] button svg,
        [data-testid="stSidebarCollapsedControl"] button span {
            color: #1d4ed8 !important;
            fill: #1d4ed8 !important;
        }

        /* Collapse sidebar button (shown inside sidebar header when sidebar is open) */
        [data-testid="stSidebarCollapseButton"] {
            visibility: visible !important;
            display: flex !important;
            opacity: 1 !important;
            pointer-events: auto !important;
        }
        [data-testid="stSidebarCollapseButton"] button {
            color: #cbd5e1 !important;
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebarCollapseButton"] button:hover {
            background: rgba(37, 99, 235, 0.4) !important;
            color: #ffffff !important;
            border-color: #3b82f6 !important;
        }

        /* App Background & Base Contrast */
        .stApp {
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }

        /* Force high contrast dark headings across main dashboard */
        .main [data-testid="stMarkdownContainer"] h1,
        .main [data-testid="stMarkdownContainer"] h2,
        .main [data-testid="stMarkdownContainer"] h3,
        .main [data-testid="stMarkdownContainer"] h4,
        .main [data-testid="stMarkdownContainer"] h5,
        .main [data-testid="stMarkdownContainer"] h6,
        .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
            color: #0f172a !important;
        }

        /* Remove default Streamlit top padding */
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 3rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            max-width: 100%;
        }

        /* Dark Navy Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1528 0%, #112240 50%, #192d52 100%) !important;
            border-right: 1px solid #1e293b;
        }

        /* Sidebar File Uploader Dropzone Styling */
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
            background: transparent !important;
            margin-bottom: 8px !important;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
            background-color: rgba(255, 255, 255, 0.08) !important;
            border: 1px dashed rgba(255, 255, 255, 0.35) !important;
            border-radius: 10px !important;
            padding: 14px 10px !important;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] section:hover {
            border-color: #3b82f6 !important;
            background-color: rgba(37, 99, 235, 0.16) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"],
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
            background: #2563eb !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            border-radius: 6px !important;
            padding: 4px 12px !important;
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"]:hover,
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] button:hover {
            background: #1d4ed8 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] div,
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] p {
            color: #cbd5e1 !important;
        }

        /* Bordered Streamlit Containers (Cards) */
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 14px !important;
            padding: 20px 22px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
            margin-bottom: 20px !important;
        }

        /* Force light text in sidebar */
        section[data-testid="stSidebar"] div, 
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] span, 
        section[data-testid="stSidebar"] label {
            color: #f1f5f9 !important;
        }

        /* Sidebar Brand */
        .sidebar-brand-box {
            text-align: center;
            padding: 12px 10px 18px 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.12);
            margin-bottom: 16px;
        }
        .sidebar-brand-icon {
            font-size: 2.4rem;
            display: inline-block;
            background: rgba(37, 99, 235, 0.25);
            border: 1px solid rgba(59, 130, 246, 0.4);
            border-radius: 14px;
            padding: 6px 12px;
            margin-bottom: 6px;
        }
        .sidebar-brand-title {
            font-size: 1.2rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            color: #ffffff !important;
            line-height: 1.2;
            text-transform: uppercase;
        }
        .sidebar-brand-subtitle {
            font-size: 0.78rem;
            color: #94a3b8 !important;
            margin-top: 4px;
            font-weight: 500;
        }

        /* Sidebar Nav Links */
        .sidebar-nav-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            border-radius: 8px;
            color: #cbd5e1 !important;
            font-size: 0.88rem;
            font-weight: 600;
            margin-bottom: 4px;
            transition: all 0.2s;
            text-decoration: none;
            background: rgba(255, 255, 255, 0.04);
        }
        .sidebar-nav-item:hover {
            background: rgba(37, 99, 235, 0.25);
            color: #ffffff !important;
        }

        /* Sidebar Status Card */
        .sidebar-status-card {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 10px;
            padding: 10px 12px;
            margin: 10px 0 16px 0;
            font-size: 0.8rem;
        }
        .status-dot {
            height: 8px;
            width: 8px;
            background-color: #22c55e;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
            box-shadow: 0 0 8px #22c55e;
        }

        /* Sidebar Reset Button */
        .sidebar-reset-btn button {
            background: #ef4444 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 8px 12px !important;
            width: 100% !important;
            transition: all 0.2s;
        }
        .sidebar-reset-btn button:hover {
            background: #dc2626 !important;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important;
        }

        /* Modern Executive Header Banner */
        .modern-header-banner {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 16px !important;
            padding: 22px 28px !important;
            margin-bottom: 22px !important;
            box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04) !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            position: relative !important;
            overflow: hidden !important;
            flex-wrap: wrap !important;
            gap: 16px !important;
        }
        .modern-header-banner::before {
            content: "" !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            height: 4px !important;
            background: linear-gradient(90deg, #2563eb, #3b82f6, #60a5fa, #38bdf8) !important;
        }
        .header-brand-pill {
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            background: #eff6ff !important;
            border: 1px solid #bfdbfe !important;
            border-radius: 20px !important;
            padding: 4px 12px !important;
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            color: #1d4ed8 !important;
            margin-bottom: 8px !important;
        }
        .header-title-box h1 {
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: #0f172a !important;
            margin: 0 !important;
            letter-spacing: -0.025em !important;
            line-height: 1.25 !important;
        }
        .header-title-box p {
            font-size: 0.92rem !important;
            color: #475569 !important;
            margin: 4px 0 0 0 !important;
        }
        .header-meta-group {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            flex-wrap: wrap !important;
        }
        .header-meta-pill {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 10px !important;
            padding: 8px 14px !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 8px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            color: #1e293b !important;
        }
        .live-status-dot {
            height: 8px !important;
            width: 8px !important;
            background-color: #10b981 !important;
            border-radius: 50% !important;
            display: inline-block !important;
            box-shadow: 0 0 8px #10b981 !important;
        }

        /* Pastel KPI Cards */
        .kpi-card {
            border-radius: 14px;
            padding: 16px 18px;
            border-width: 1px;
            border-style: solid;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
            transition: all 0.2s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 14px rgba(0, 0, 0, 0.05);
        }
        .kpi-card-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }
        .kpi-card-icon {
            font-size: 1.25rem;
        }
        .kpi-card-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #475569;
        }
        .kpi-card-val {
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            line-height: 1.1;
        }

        /* White Analytics Card Container */
        .analytics-card {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 14px !important;
            padding: 20px 22px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
            margin-bottom: 20px !important;
            color: #0f172a !important;
        }
        .analytics-card-header {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            margin-bottom: 14px !important;
            border-bottom: 1px solid #f1f5f9 !important;
            padding-bottom: 10px !important;
        }
        .analytics-card-title,
        .analytics-card-header h3,
        .analytics-card-header h2,
        .analytics-card-header h1,
        .analytics-card h1,
        .analytics-card h2,
        .analytics-card h3,
        .analytics-card h4,
        .analytics-card h5,
        .analytics-card h6 {
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            color: #0f172a !important;
            margin: 0 !important;
            line-height: 1.3 !important;
        }
        .analytics-card-subtitle,
        .analytics-card-header p {
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            color: #475569 !important;
            margin: 3px 0 0 0 !important;
        }
        .analytics-card [data-testid="stMarkdownContainer"] h5,
        .analytics-card h5 {
            color: #0f172a !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
        }
        .analytics-card label,
        .analytics-card [data-testid="stWidgetLabel"] p {
            color: #1e293b !important;
            font-weight: 600 !important;
        }
        [data-testid="stExpander"] summary span {
            color: #0f172a !important;
            font-weight: 600 !important;
        }

        /* Dynamic Insights Callout */
        .insight-pill {
            background-color: #f0fdf4;
            border-left: 4px solid #16a34a;
            padding: 10px 14px;
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 0.92rem;
            color: #166534;
            font-weight: 500;
        }

        /* Prediction Result Box */
        .prediction-hero-card {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border: 2px solid #3b82f6;
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.12);
            margin: 20px 0;
        }
        .pred-label {
            font-size: 0.95rem;
            font-weight: 700;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        .pred-value {
            font-size: 2.6rem;
            font-weight: 800;
            color: #1d4ed8;
            margin: 8px 0;
            letter-spacing: -0.02em;
        }
        .pred-sub {
            font-size: 0.88rem;
            color: #64748b;
        }

        /* Primary Form Submit Button */
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 12px 24px !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
            transition: all 0.2s !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header(title="House Price Prediction & Analysis", subtitle="Interactive Housing Market Analytics Dashboard"):
    """
    Renders an attractive, modern executive dashboard header banner with status indicators.
    """
    st.markdown(f"""
    <div class="modern-header-banner">
        <div class="header-title-box">
            <div class="header-brand-pill">
                <span>🏠</span>
                <span>Real Estate Intelligence Suite</span>
            </div>
            <h1 style="color: #0f172a !important; font-weight: 800; margin: 0;">{title}</h1>
            <p style="color: #475569 !important; font-size: 0.92rem; margin: 5px 0 0 0;">{subtitle}</p>
        </div>
        <div class="header-meta-group">
            <div class="header-meta-pill">
                <span class="live-status-dot"></span>
                <span style="color: #1e293b !important;">Live Market Analytics</span>
            </div>
            <div class="header-meta-pill">
                <span style="font-size: 0.85rem;">⚡</span>
                <span style="color: #1e293b !important;">ML Valuation Engine</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(label, value, icon, bg_color, border_color, text_color, delta=None):
    """
    Renders a single pastel KPI card with optional delta comparison.
    """
    delta_html = ""
    if delta:
        delta_html = f'<div style="font-size: 0.76rem; font-weight: 700; color: {text_color}; margin-top: 6px; opacity: 0.95;">{delta}</div>'

    st.markdown(f"""
    <div class="kpi-card" style="background-color: {bg_color}; border-color: {border_color};">
        <div class="kpi-card-header">
            <span class="kpi-card-icon">{icon}</span>
            <span class="kpi-card-label">{label}</span>
        </div>
        <div class="kpi-card-val" style="color: {text_color};">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_kpi_row(kpis: dict, full_kpis: dict | None = None, is_filtered: bool = False):
    """
    Renders the 5 pastel KPI cards in 5 equal columns:
    1. Total Properties (Soft Blue)
    2. Average Price (Soft Green)
    3. Highest Price (Soft Yellow)
    4. Lowest Price (Soft Pink)
    5. Average Area (Soft Purple)
    When filters are active, displays dynamic deltas vs the full dataset.
    When no filters are active, shows no delta.
    """
    c1, c2, c3, c4, c5 = st.columns(5)
    
    total_props = f"{kpis.get('total_properties', 0):,}"
    avg_price = kpis.get("avg_price_fmt", "N/A")
    max_price = kpis.get("max_price_fmt", "N/A")
    min_price = kpis.get("min_price_fmt", "N/A")
    avg_area = kpis.get("avg_area_fmt", "N/A")

    # Compute comparison deltas only when filters are active
    total_delta = None
    avg_price_delta = None
    max_price_delta = None
    min_price_delta = None
    avg_area_delta = None

    if is_filtered and full_kpis:
        full_total = full_kpis.get("total_properties", 0)
        curr_total = kpis.get("total_properties", 0)
        if full_total > 0:
            total_delta = f"{curr_total:,} of {full_total:,} listings"

        if kpis.get("avg_price") and full_kpis.get("avg_price") and full_kpis["avg_price"] > 0:
            diff_p = ((kpis["avg_price"] - full_kpis["avg_price"]) / full_kpis["avg_price"]) * 100
            arrow = "▲" if diff_p > 0 else ("▼" if diff_p < 0 else "•")
            sign = "+" if diff_p > 0 else ""
            avg_price_delta = f"{arrow} {sign}{diff_p:.1f}% vs all listings"

        if full_kpis.get("max_price_fmt") and full_kpis["max_price_fmt"] != "N/A":
            max_price_delta = f"vs {full_kpis['max_price_fmt']} overall"

        if full_kpis.get("min_price_fmt") and full_kpis["min_price_fmt"] != "N/A":
            min_price_delta = f"vs {full_kpis['min_price_fmt']} overall"

        if kpis.get("avg_area") and full_kpis.get("avg_area") and full_kpis["avg_area"] > 0:
            diff_a = ((kpis["avg_area"] - full_kpis["avg_area"]) / full_kpis["avg_area"]) * 100
            arrow_a = "▲" if diff_a > 0 else ("▼" if diff_a < 0 else "•")
            sign_a = "+" if diff_a > 0 else ""
            avg_area_delta = f"{arrow_a} {sign_a}{diff_a:.1f}% vs all listings"

    with c1:
        render_kpi_card(
            label="TOTAL PROPERTIES",
            value=total_props,
            icon="🏘️",
            bg_color="#eff6ff",
            border_color="#bfdbfe",
            text_color="#1e3a8a",
            delta=total_delta
        )
    with c2:
        render_kpi_card(
            label="AVERAGE PRICE",
            value=avg_price,
            icon="💰",
            bg_color="#f0fdf4",
            border_color="#bbf7d0",
            text_color="#14532d",
            delta=avg_price_delta
        )
    with c3:
        render_kpi_card(
            label="HIGHEST PRICE",
            value=max_price,
            icon="📈",
            bg_color="#fefce8",
            border_color="#fef08a",
            text_color="#713f12",
            delta=max_price_delta
        )
    with c4:
        render_kpi_card(
            label="LOWEST PRICE",
            value=min_price,
            icon="📉",
            bg_color="#fef2f2",
            border_color="#fecaca",
            text_color="#7f1d1d",
            delta=min_price_delta
        )
    with c5:
        render_kpi_card(
            label="AVERAGE AREA",
            value=avg_area,
            icon="📐",
            bg_color="#f5f3ff",
            border_color="#ddd6fe",
            text_color="#4c1d95",
            delta=avg_area_delta
        )
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
