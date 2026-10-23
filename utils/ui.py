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

        /* Top Header Styling */
        .main-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 22px;
            flex-wrap: wrap;
            gap: 12px;
        }
        .header-title-box h1 {
            font-size: 1.85rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0;
            letter-spacing: -0.02em;
        }
        .header-title-box p {
            font-size: 0.92rem;
            color: #64748b;
            margin: 4px 0 0 0;
        }
        .header-project-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 10px 18px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .header-project-icon {
            font-size: 1.6rem;
            color: #2563eb;
        }
        .header-project-label {
            font-size: 0.72rem;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        .header-project-value {
            font-size: 0.96rem;
            font-weight: 700;
            color: #0f172a;
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

def render_header(title="House Price Prediction & Analysis", subtitle="Interactive Housing Market Analytics Dashboard", project_name=None):
    """
    Renders the modern top dashboard header.
    If project_name is provided, displays the project badge; otherwise displays a clean, elegant header.
    """
    project_badge_html = ""
    if project_name:
        project_badge_html = f"""
        <div class="header-project-card">
            <div class="header-project-icon">📅</div>
            <div>
                <div class="header-project-label" style="color: #64748b !important;">PROJECT</div>
                <div class="header-project-value" style="color: #0f172a !important;">{project_name}</div>
            </div>
        </div>
        """

    st.markdown(f"""
    <div class="main-header-row">
        <div class="header-title-box">
            <h1 style="color: #0f172a !important; font-weight: 800; margin: 0;">{title}</h1>
            <p style="color: #475569 !important; font-size: 0.95rem; margin: 4px 0 0 0;">{subtitle}</p>
        </div>
        {project_badge_html}
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(label, value, icon, bg_color, border_color, text_color):
    """
    Renders a single pastel KPI card.
    """
    st.markdown(f"""
    <div class="kpi-card" style="background-color: {bg_color}; border-color: {border_color};">
        <div class="kpi-card-header">
            <span class="kpi-card-icon">{icon}</span>
            <span class="kpi-card-label">{label}</span>
        </div>
        <div class="kpi-card-val" style="color: {text_color};">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_row(kpis: dict):
    """
    Renders the 5 pastel KPI cards in 5 equal columns:
    1. Total Properties (Soft Blue)
    2. Average Price (Soft Green)
    3. Highest Price (Soft Yellow)
    4. Lowest Price (Soft Pink)
    5. Average Area (Soft Purple)
    Safe from KeyError using .get() defaults.
    """
    c1, c2, c3, c4, c5 = st.columns(5)
    
    total_props = f"{kpis.get('total_properties', 0):,}"
    avg_price = kpis.get("avg_price_fmt", "N/A")
    max_price = kpis.get("max_price_fmt", "N/A")
    min_price = kpis.get("min_price_fmt", "N/A")
    avg_area = kpis.get("avg_area_fmt", "N/A")

    with c1:
        render_kpi_card(
            label="TOTAL PROPERTIES",
            value=total_props,
            icon="🏘️",
            bg_color="#eff6ff",
            border_color="#bfdbfe",
            text_color="#1e3a8a"
        )
    with c2:
        render_kpi_card(
            label="AVERAGE PRICE",
            value=avg_price,
            icon="💰",
            bg_color="#f0fdf4",
            border_color="#bbf7d0",
            text_color="#14532d"
        )
    with c3:
        render_kpi_card(
            label="HIGHEST PRICE",
            value=max_price,
            icon="📈",
            bg_color="#fefce8",
            border_color="#fef08a",
            text_color="#713f12"
        )
    with c4:
        render_kpi_card(
            label="LOWEST PRICE",
            value=min_price,
            icon="📉",
            bg_color="#fef2f2",
            border_color="#fecaca",
            text_color="#7f1d1d"
        )
    with c5:
        render_kpi_card(
            label="AVERAGE AREA",
            value=avg_area,
            icon="📐",
            bg_color="#f5f3ff",
            border_color="#ddd6fe",
            text_color="#4c1d95"
        )
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
