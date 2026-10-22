# 🏠 House Price Prediction & Analysis Dashboard

A complete, professional real-estate market analytics and price prediction web application built **100% in Python** using Streamlit, Plotly, Pandas, and Scikit-Learn.

---

## 📖 Project Description

The **House Price Prediction & Analysis System** is an interactive analytics dashboard designed to help buyers, real-estate investors, agents, and data analysts explore housing market trends and predict property values. 

The application loads housing data, cleans and preprocesses features, computes key housing metrics, provides interactive multi-variable filtering, dynamically generates market insights, and runs a Scikit-Learn regression pipeline (Random Forest) to deliver instant, customized property valuations.

---

## ✨ Modern Executive UI & Features

- **Executive Analytics Dashboard Theme**:
  - **Left Sidebar**: Deep royal navy background with branded header, clean active pill navigation tabs, and system info footer.
  - **Header & Badge**: Executive title bar with project tracking badge.
  - **Upload Panel & File Status**: Clean file upload container with real-time success confirmation badge.
  - **8 Pastel KPI Stat Cards**: Color-coded KPI grid for Total Properties, Locations, Average Price, Highest Price, Lowest Price, Total Records, Missing Values, and Columns.
  - **3-Panel Middle Section**:
    - **🗂️ Dataset Preview**: Clean table showing key property attributes.
    - **⚙️ Missing Values**: Real-time missing value count diagnostic table.
    - **🛠️ Data Cleaning**: Interactive action buttons for checking missing values, median/mode imputations, and deduplication.
  - **3-Panel Analytics Section**:
    - **📊 Analysis**: Dynamic analysis selector with localized summary tables.
    - **📈 Visualization**: Interactive chart type selector (Bar, Histogram, Scatter) powered by Plotly.
    - **🥧 Distribution**: Interactive BHK / Price bracket donut chart.
  - **Action Toolbar**: One-click buttons to download processed data, generate markdown/PDF reports, and open the prediction studio.
  - **Multi-View Navigation**: Dedicated workspaces for **Dashboard**, **Load Data**, **Data Preview**, **Data Cleaning**, **Analysis**, **Visualization**, **Prediction**, and **Report**.
- **100% Python Native**: No Node.js, React, Angular, or external web servers required.
- **Robust Dataset Processing**:
  - Automatically detects and maps column names (`Area`, `Bedrooms`, `Bathrooms`, `Location`, `Year Built`, `Parking`, `Furnishing`, `Price`).
  - Cleans currency characters (`₹`, `$`, commas) and typecasts numerical features.
  - Automatically deduplicates records and safely imputes missing values.
  - Graceful degradation: never crashes if specific columns are absent.
- **Dynamic Interactive Filters**:
  - Multi-select filters for Location and Furnishing status.
  - Range sliders for Bedrooms, Bathrooms, Price, Area, and Year Built.
  - One-click **Reset Filters** button.
- **Top KPI Cards**:
  - Total Properties, Average Price, Maximum Price, Minimum Price, and Average Area.
- **📌 Key Insights Engine**:
  - Automatically calculates data-driven insights (e.g., average market prices, top-tier localities, bedroom premiums, and average price per sqft).
- **📊 Interactive Market Overview**:
  - **Price Distribution**: Interactive histogram with boxplot marginals and zoom.
  - **Average Price by Location**: Sorted horizontal bar chart with property count tooltips.
  - **Area vs Price**: Scatter plot highlighting space-to-price correlations.
  - **Bedrooms vs Average Price**: Multi-metric configuration comparison.
- **🏡 Property Analysis**:
  - Price per Square Foot calculation (`Price / Area`) with highest, lowest, and location-wise averages.
  - Bedroom & Bathroom frequency distribution graphs.
  - Historical Year Built vs Price trend visualization.
- **🔗 Feature Correlation Matrix**:
  - Interactive Plotly heatmap assessing collinearity across all numeric features.
- **🤖 Machine Learning Price Prediction**:
  - Trained using Scikit-Learn's `RandomForestRegressor`.
  - Full `ColumnTransformer` preprocessing pipeline with median imputation, standard scaling, and one-hot encoding.
  - Model metrics displayed: **R² Score**, **MAE**, and **RMSE**.
  - Interactive prediction form dynamically tailored to the dataset.
  - Prominent price estimation output formatted in Indian Lakhs/Crores (`₹ XX.XX Lakh / Cr`).
  - Feature Importance bar chart visualizing factors driving property valuations.
- **📋 Dataset Explorer & Export**:
  - Tabular view of filtered listings with search capability.
  - Instant CSV download button for filtered datasets.
- **🔍 Data Quality Report**:
  - Expandable diagnostic view displaying raw vs clean row counts, duplicate removals, schema data types, and column mapping statuses.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3** | Core language |
| **Streamlit** | Interactive web application framework |
| **Pandas & NumPy** | Data manipulation and numeric computing |
| **Plotly** | Responsive, interactive charts and heatmaps |
| **Scikit-Learn** | Machine learning pipeline, regression model, and evaluation |
| **Matplotlib & Seaborn** | Statistical charting support |

---

## 🚀 Installation & Setup

### 1. Clone or Navigate to the Project Directory
```bash
cd "d:\house price analysis"
```

### 2. Install Required Dependencies
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
house-price-analysis/
│
├── app.py                     # Main Streamlit web application
├── requirements.txt           # Python dependency requirements
├── README.md                  # Comprehensive documentation
│
├── data/
│   ├── house_prices.csv       # Default housing dataset (1,500 listings)
│   └── generate_dataset.py    # Synthetic dataset generator script
│
├── models/
│   └── model.pkl              # Saved trained machine learning pipeline
│
└── utils/
    ├── __init__.py            # Package initializer
    ├── data_processing.py     # Dataset cleaning, mapping, KPI & insight logic
    ├── visualization.py       # Plotly chart generation utilities
    └── prediction.py          # Scikit-learn ML training and prediction pipeline
```

---

## 📊 Dataset Format

The system supports CSV files. Expected columns include:

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
| `Price` | Numeric | House valuation / selling price | `8500000` |

> **Note on Flexibility**: If your CSV uses alternative naming (such as `sqft`, `beds`, `baths`, `saleprice`, `city`), the system's column detection layer maps them to canonical features automatically. If a column is missing, the application cleanly adapts without crashing.

---

## 🧠 Machine Learning Workflow

```
Raw CSV / User Input
        │
        ▼
Column Identification & Data Cleaning
        │
        ▼
Feature Extraction (Numerical & Categorical)
        │
        ├── Numerical Pipeline: SimpleImputer(median) -> StandardScaler()
        └── Categorical Pipeline: SimpleImputer(mode) -> OneHotEncoder(handle_unknown='ignore')
        │
        ▼
Random Forest Regressor (n_estimators=100)
        │
        ├── Train / Test Split (80% / 20%)
        ├── Evaluation: R² Score, MAE, RMSE
        └── Feature Importances Calculation
        │
        ▼
Interactive Valuation Generator (User Inputs -> Predicted ₹ Valuation)
```

---

## 💡 Running Tests / Verification

You can verify the backend modules directly from the command line:

```bash
python data/generate_dataset.py
python -c "import app; print('App module loaded successfully!')"
```
