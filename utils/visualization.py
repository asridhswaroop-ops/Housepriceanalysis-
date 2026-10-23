"""
Interactive Plotly visualizations for House Price Prediction & Analysis Dashboard.
Styled cleanly for modern BI analytics.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CHART_THEME = "plotly_white"
PRIMARY_COLOR = "#2563EB"
ACCENT_COLOR = "#0D9488"
PALETTE = ["#2563EB", "#0D9488", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#10B981"]

def style_figure_layout(fig: go.Figure, height: int = 380):
    """
    Applies unified clean layout styling to Plotly figures.
    """
    fig.update_layout(
        template=CHART_THEME,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=20, t=50, b=30),
        height=height,
        font=dict(family="Inter, sans-serif", size=12, color="#334155"),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", linecolor="#e2e8f0"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", linecolor="#e2e8f0")
    )
    return fig

def plot_price_distribution(df: pd.DataFrame, price_col: str, is_per_sqft: bool = False) -> go.Figure:
    """
    Price Distribution histogram with clean marginal boxplot and professional labels.
    Supports switching between total price and price per sqft.
    """
    if price_col not in df.columns or df[price_col].dropna().empty:
        fig = go.Figure()
        fig.add_annotation(text="Price data not available", showarrow=False, font=dict(size=14))
        return style_figure_layout(fig)

    chart_title = (
        "<b>Price per Sqft Distribution</b><br><span style='font-size:12px;color:#64748b;'>Distribution of property rates per square foot</span>"
        if is_per_sqft
        else "<b>Price Distribution</b><br><span style='font-size:12px;color:#64748b;'>Distribution of property prices</span>"
    )
    unit_label = "₹/sqft" if is_per_sqft else "₹"
    x_axis_title = "Price per Sqft (₹/sqft)" if is_per_sqft else "Price (₹)"

    fig = px.histogram(
        df,
        x=price_col,
        nbins=35,
        marginal="box",
        title=chart_title,
        color_discrete_sequence=[PRIMARY_COLOR],
        opacity=0.88,
        template=CHART_THEME
    )
    fig.update_traces(
        hovertemplate=f"Rate: {unit_label}%{{x:,.0f}}<br>Count: %{{y}}<extra></extra>" if is_per_sqft else "Price: ₹%{x:,.0f}<br>Count: %{y}<extra></extra>"
    )
    fig.update_layout(
        xaxis_title=x_axis_title,
        yaxis_title="Number of Properties",
        hovermode="x unified",
        bargap=0.05
    )
    return style_figure_layout(fig, height=390)

def plot_price_by_location(df: pd.DataFrame, loc_col: str, price_col: str, is_per_sqft: bool = False) -> go.Figure:
    """
    Average Price by Location bar chart, sorted by average price.
    Supports switching between total price and price per sqft.
    """
    if loc_col not in df.columns or price_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Location or Price data missing", showarrow=False, font=dict(size=14))
        return style_figure_layout(fig)

    summary = df.groupby(loc_col)[price_col].agg(["mean", "count"]).reset_index()
    summary = summary.sort_values(by="mean", ascending=True)

    chart_title = (
        "<b>Average Price per Sqft by Location</b><br><span style='font-size:12px;color:#64748b;'>Top locations ranked by mean rate per sqft</span>"
        if is_per_sqft
        else "<b>Average Price by Location</b><br><span style='font-size:12px;color:#64748b;'>Top locations ranked by mean price</span>"
    )
    x_axis_title = "Average Price per Sqft (₹/sqft)" if is_per_sqft else "Average Price (₹)"
    unit_str = "/sqft" if is_per_sqft else ""

    fig = px.bar(
        summary,
        x="mean",
        y=loc_col,
        orientation="h",
        title=chart_title,
        color="mean",
        color_continuous_scale="Blues",
        template=CHART_THEME,
        custom_data=["count"]
    )
    fig.update_traces(
        hovertemplate=f"<b>%{{y}}</b><br>Average Rate: ₹%{{x:,.0f}}{unit_str}<br>Listings: %{{customdata[0]}}<extra></extra>"
    )
    fig.update_layout(
        xaxis_title=x_axis_title,
        yaxis_title="Location",
        coloraxis_showscale=False
    )
    return style_figure_layout(fig, height=390)

def plot_area_vs_price(df: pd.DataFrame, area_col: str, price_col: str, loc_col: str = None, bed_col: str = None, bath_col: str = None) -> go.Figure:
    """
    Area vs Price scatter plot with complete hover details:
    Location, Bedrooms, Bathrooms, Area, Price.
    """
    if area_col not in df.columns or price_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Area or Price data missing", showarrow=False, font=dict(size=14))
        return style_figure_layout(fig)

    # Hover data setup
    hover_cols = {}
    if loc_col and loc_col in df.columns:
        hover_cols[loc_col] = True
    if bed_col and bed_col in df.columns:
        hover_cols[bed_col] = True
    if bath_col and bath_col in df.columns:
        hover_cols[bath_col] = True

    color_col = bed_col if (bed_col and bed_col in df.columns) else None

    fig = px.scatter(
        df,
        x=area_col,
        y=price_col,
        color=color_col,
        hover_data=hover_cols,
        title="<b>Area vs Price</b><br><span style='font-size:12px;color:#64748b;'>Property area (sqft) compared to valuation</span>",
        color_discrete_sequence=PALETTE,
        template=CHART_THEME,
        opacity=0.75
    )
    fig.update_traces(
        marker=dict(size=7, line=dict(width=0.5, color="rgba(0,0,0,0.2)"))
    )
    fig.update_layout(
        xaxis_title="Area (Square Feet)",
        yaxis_title="Price (₹)"
    )
    return style_figure_layout(fig, height=390)

def plot_bedrooms_vs_price(df: pd.DataFrame, bed_col: str, price_col: str) -> go.Figure:
    """
    Bedroom Analysis: Bedrooms -> Average Price.
    """
    if bed_col not in df.columns or price_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Bedrooms or Price data missing", showarrow=False, font=dict(size=14))
        return style_figure_layout(fig)

    summary = df.groupby(bed_col)[price_col].agg(["mean", "median", "count"]).reset_index()
    summary = summary.sort_values(by=bed_col)
    summary["BHK_label"] = summary[bed_col].astype(str) + " BHK"

    fig = px.bar(
        summary,
        x="BHK_label",
        y="mean",
        title="<b>Bedroom Analysis</b><br><span style='font-size:12px;color:#64748b;'>Bedrooms configuration vs Average Price</span>",
        color="mean",
        color_continuous_scale="Teal",
        template=CHART_THEME,
        custom_data=["count", "median"]
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Average Price: ₹%{y:,.0f}<br>Median Price: ₹%{customdata[1]:,.0f}<br>Listings: %{customdata[0]}<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="Bedroom Configuration",
        yaxis_title="Average Price (₹)",
        coloraxis_showscale=False
    )
    return style_figure_layout(fig, height=390)

def plot_price_per_sqft_by_location(df: pd.DataFrame, loc_col: str, sqft_col: str) -> go.Figure:
    """
    Location-wise price per sqft.
    """
    if loc_col not in df.columns or sqft_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Location or Price/Sqft missing", showarrow=False, font=dict(size=14))
        return style_figure_layout(fig)

    summary = df.groupby(loc_col)[sqft_col].mean().reset_index()
    summary = summary.sort_values(by=sqft_col, ascending=True)

    fig = px.bar(
        summary,
        x=sqft_col,
        y=loc_col,
        orientation="h",
        title="<b>Price per Sqft by Location</b><br><span style='font-size:12px;color:#64748b;'>Mean rate per square foot across localities</span>",
        color=sqft_col,
        color_continuous_scale="Purples",
        template=CHART_THEME
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Rate: ₹%{x:,.0f}/sqft<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="Rate (₹/sqft)",
        yaxis_title="Location",
        coloraxis_showscale=False
    )
    return style_figure_layout(fig, height=360)

def plot_category_distribution(df: pd.DataFrame, col: str, title: str, x_label: str) -> go.Figure:
    """
    Frequency distribution bar chart.
    """
    if col not in df.columns or df[col].dropna().empty:
        fig = go.Figure()
        fig.add_annotation(text=f"{col} data missing", showarrow=False, font=dict(size=14))
        return style_figure_layout(fig)

    counts = df[col].value_counts().reset_index()
    counts.columns = [col, "Count"]
    counts = counts.sort_values(by=col)
    counts[col] = counts[col].astype(str)

    fig = px.bar(
        counts,
        x=col,
        y="Count",
        title=f"<b>{title}</b>",
        color="Count",
        color_continuous_scale="Blues",
        template=CHART_THEME
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Count: %{y} properties<extra></extra>"
    )
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title="Property Count",
        coloraxis_showscale=False
    )
    return style_figure_layout(fig, height=340)

def plot_year_built_trend(df: pd.DataFrame, year_col: str, price_col: str) -> go.Figure:
    """
    Year Built vs Average Price trend line.
    """
    if year_col not in df.columns or price_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Year Built data not available", showarrow=False, font=dict(size=14))
        return style_figure_layout(fig)

    yearly = df.groupby(year_col)[price_col].agg(["mean", "count"]).reset_index()
    yearly = yearly.sort_values(by=year_col)

    fig = px.line(
        yearly,
        x=year_col,
        y="mean",
        markers=True,
        title="<b>Year Built vs Average Price</b><br><span style='font-size:12px;color:#64748b;'>Historical construction year trends</span>",
        template=CHART_THEME,
        custom_data=["count"]
    )
    fig.update_traces(
        line=dict(color="#2563EB", width=2.5),
        marker=dict(size=7, color="#1D4ED8"),
        hovertemplate="Year Built: %{x}<br>Average Price: ₹%{y:,.0f}<br>Listings: %{customdata[0]}<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="Year Built",
        yaxis_title="Average Price (₹)"
    )
    return style_figure_layout(fig, height=360)

def plot_correlation_heatmap(df: pd.DataFrame, numeric_cols: list) -> go.Figure:
    """
    Feature Analysis: Correlation Heatmap.
    """
    valid_cols = [c for c in numeric_cols if c in df.columns and df[c].nunique() > 1]
    if len(valid_cols) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Not enough numerical columns for correlation analysis", showarrow=False, font=dict(size=14))
        return style_figure_layout(fig)

    corr = df[valid_cols].corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="<b>Correlation Heatmap</b><br><span style='font-size:12px;color:#64748b;'>Collinearity analysis across numerical housing variables</span>",
        template=CHART_THEME
    )
    fig.update_traces(
        hovertemplate="Feature 1: %{y}<br>Feature 2: %{x}<br>Correlation: %{z:.3f}<extra></extra>"
    )
    return style_figure_layout(fig, height=420)

def plot_feature_importance(feature_names: list, importances: np.ndarray) -> go.Figure:
    """
    Horizontal bar chart of top model factors driving valuation.
    """
    if len(feature_names) == 0 or len(importances) == 0:
        fig = go.Figure()
        fig.add_annotation(text="Feature importances not available", showarrow=False, font=dict(size=14))
        return style_figure_layout(fig)

    fi_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances
    }).sort_values(by="Importance", ascending=True)

    if len(fi_df) > 10:
        fi_df = fi_df.tail(10)

    fig = px.bar(
        fi_df,
        x="Importance",
        y="Feature",
        orientation="h",
        title="<b>Key Factors Driving Valuation (Feature Importance)</b>",
        color="Importance",
        color_continuous_scale="Blues",
        template=CHART_THEME
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Importance: %{x:.3f}<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="Importance Score",
        yaxis_title="Feature",
        coloraxis_showscale=False
    )
    return style_figure_layout(fig, height=360)
