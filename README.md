# 🏠 House Price Prediction & Analysis Dashboard

A complete, professional real-estate market analytics and price prediction web application built **100% in Python** using Streamlit, Plotly, Pandas, and Scikit-Learn.

---

## 📖 Project Description

The **House Price Prediction & Analysis Dashboard** is an interactive analytics application designed to help buyers, real-estate investors, agents, and data analysts explore housing market trends and predict property values.

The application loads housing data, cleans and preprocesses features, computes key housing metrics, provides interactive multi-variable filtering, dynamically generates market insights, and trains a regression model (Random Forest via Scikit-Learn with a pure NumPy fallback) to deliver instant, customized property valuations.

---

## ✨ Features

- **Professional Executive Analytics UI**:
  - **Dark Navy Sidebar**: Modern branding header, quick section links, dataset upload panel, real-time dataset status badge, and filter controls.
  - **Top 5 Pastel KPI Cards**: Color-coded KPI summary displaying Total Properties, Average Price, Highest Price, Lowest Price, and Average Area.
  - **Market Insights Card**: Automatically computes data-driven market takeaways such as average valuations, top-priced localities, and bedroom premiums.
- **Robust Dataset Ingestion & Preprocessing**:
  - Upload custom CSV or Excel files, or load the built-in default housing dataset.
  - Automatic column detection supporting varied schema naming conventions (`Area`, `Bedrooms`, `Bathrooms`, `Location`, `Year Built`, `Parking`, `Furnishing`, `Price`).
  - Cleans currency formatting, converts types, removes duplicate entries, and safely imputes missing values.
- **Interactive Multi-Variable Filters**:
  - Filter by **Location** (multi-select).
  - Range sliders for **Bedrooms**, **Bathrooms**, and **Price Range** (computed across the dataset to avoid out-of-range slider states).
  - One-click **Reset Filters** button.
- **Interactive Visualizations (Plotly)**:
  - **Price Distribution**: Interactive histogram with boxplot marginals.
  - **Average Price by Location**: Sorted horizontal bar chart.
  - **Area vs Price**: Scatter plot highlighting space-to-price relationships.
  - **Bedrooms vs Average Price**: Bar chart comparing valuations across BHK configurations.
  - **Feature Correlation Heatmap**: Matrix examining correlations across all numerical attributes.
- **Machine Learning Price Prediction**:
  - Dynamic training pipeline using Scikit-Learn's `RandomForestRegressor` (with standard scaling, median imputation, and one-hot encoding), plus pure NumPy fallback.
  - Stale cache prevention: model cache updates whenever dataset contents change.
  - Strict target leakage prevention: target and target-derived columns (like `price_per_sqft`) are excluded from model features.
  - Prediction input form with dataset-driven ranges for Area and Year Built.
  - Prominent price estimation output formatted in Indian currency (`₹ Lakh` / `₹ Cr`) alongside exact valuation.
  - Displays validation metrics: **R² Score**, **MAE**, and **RMSE**.
  - Expandable Feature Importance chart showing factors influencing valuations.
- **Dataset Explorer & Export**:
  - Tabular view of the filtered dataset with record, column, missing, and duplicate counts.
  - One-click **Download Processed Dataset** as CSV.
- **Data Quality Diagnostics**:
  - Expandable diagnostics section displaying raw vs clean row counts, duplicates removed, and a full column schema/type verification table.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3** | Core programming language |
| **Streamlit** | Interactive web application framework |
| **Pandas & NumPy** | Data manipulation and numeric operations |
| **Plotly** | Responsive, interactive data charts and heatmaps |
| **Scikit-Learn** | Machine learning preprocessing and regression modeling |
| **Joblib** | Model serialization and parallel processing utility |
| **OpenPyXL** | Excel file reading support |

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/asridhswaroop-ops/Housepriceanalysis-.git
cd Housepriceanalysis-
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
*(Alternatively: `python -m streamlit run app.py`)*

The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```text
Housepriceanalysis-/
│
├── app.py                     # Main Streamlit web application
├── requirements.txt           # Pinned Python dependencies
├── README.md                  # Project documentation
│
├── data/
│   ├── house_prices.csv       # Default housing dataset
│   └── generate_dataset.py    # Synthetic dataset generator script
│
└── utils/
    ├── __init__.py            # Package initializer
    ├── data_processing.py     # Dataset cleaning, column mapping, KPIs & insights
    ├── ui.py                  # Custom styling, header, and KPI components
    ├── visualization.py       # Plotly chart generation utilities
    └── prediction.py          # ML training and prediction pipeline
```

---

## 📊 Dataset Format

The system supports CSV and Excel files. Common expected columns include:

| Column Name | Type | Description | Example |
|---|---|---|---|
| `House ID` | Text / String | Unique identifier | `HSE-1001` |
| `Area` | Numeric | Property area in square feet | `1650` |
| `Bedrooms` | Numeric | Number of bedrooms (BHK) | `3` |
| `Bathrooms` | Numeric | Number of bathrooms | `2` |
| `Location` | Categorical | Neighborhood / City | `Downtown Core` |
| `Year Built` | Numeric | Construction year | `2018` |
| `Parking` | Categorical | Parking availability | `Yes` / `No` |
| `Furnishing` | Categorical | Furnishing state | `Furnished`, `Semi-Furnished`, `Unfurnished` |
| `Price` | Numeric | Property valuation / selling price | `8500000` |

If a dataset uses alternative column naming (such as `sqft`, `beds`, `baths`, `saleprice`), the system's column detection layer automatically maps them to canonical features.
