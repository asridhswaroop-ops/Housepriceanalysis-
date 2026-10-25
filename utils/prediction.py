"""
Machine Learning training, evaluation, and prediction pipeline.
Supports Scikit-Learn when available, and includes a high-performance pure NumPy/Pandas
regression engine for environments with OS Application Control / DLL restrictions.
"""
import os
import numpy as np
import pandas as pd

# Check if Scikit-Learn is usable without OS policy / DLL restrictions
SKLEARN_AVAILABLE = False
try:
    from sklearn.model_selection import train_test_split
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
    import joblib
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_FILE = os.path.join(MODEL_DIR, "model.pkl")

def get_feature_and_target_columns(df: pd.DataFrame, col_mapping: dict):
    """
    Identifies target column and separates candidate features into numerical and categorical.
    Strictly excludes target column, identifiers, and any columns derived from price
    (such as price_per_sqft) to prevent target leakage into the regression model.
    """
    if "price" not in col_mapping or col_mapping["price"] not in df.columns:
        return None, [], []

    target_col = col_mapping["price"]

    # Canonical columns to exclude explicitly
    excluded_canonical = ["price", "id", "price_per_sqft"]
    excluded_names = {col_mapping[k] for k in excluded_canonical if k in col_mapping}
    excluded_names.add(target_col)

    # Exclude ID, index, and any price-derived columns (e.g. price_per_sqft, sqft_price)
    for col in df.columns:
        c_lower = col.strip().lower()
        if "id" in c_lower or c_lower in ["index", "unnamed: 0"]:
            excluded_names.add(col)
        elif "price" in c_lower or "cost" in c_lower or "rate_per" in c_lower:
            excluded_names.add(col)

    feature_cols = [c for c in df.columns if c not in excluded_names]

    numeric_features = []
    categorical_features = []

    for c in feature_cols:
        if pd.api.types.is_numeric_dtype(df[c]):
            numeric_features.append(c)
        else:
            categorical_features.append(c)

    return target_col, numeric_features, categorical_features

# --------------------------------------------------------------------------
# Pure NumPy & Pandas Regression Engine (Fast, Robust, Zero DLL Dependencies)
# --------------------------------------------------------------------------
class PureNumpyRegressionPipeline:
    def __init__(self, num_features, cat_features, l2_reg=1.0):
        self.num_features = list(num_features)
        self.cat_features = list(cat_features)
        self.l2_reg = l2_reg
        self.means = {}
        self.stds = {}
        self.medians = {}
        self.cat_categories = {}
        self.encoded_feature_names = []
        self.weights = None
        self.intercept = 0.0

    def fit(self, X: pd.DataFrame, y: pd.Series):
        X = X.copy()
        
        # 1. Numeric statistics for imputation and standardization
        for col in self.num_features:
            med = float(X[col].median()) if not X[col].dropna().empty else 0.0
            self.medians[col] = med
            X[col] = X[col].fillna(med)
            m = float(X[col].mean())
            s = float(X[col].std())
            self.means[col] = m
            self.stds[col] = s if s > 1e-6 else 1.0

        # Standardize numeric features
        X_num = pd.DataFrame(index=X.index)
        for col in self.num_features:
            X_num[col] = (X[col] - self.means[col]) / self.stds[col]

        # 2. Categorical encoding
        X_cat_dummies = []
        for col in self.cat_features:
            cats = sorted(X[col].dropna().astype(str).unique().tolist())
            self.cat_categories[col] = cats
            for c in cats:
                col_name = f"{col}_{c}"
                X_cat_dummies.append(
                    pd.Series((X[col].astype(str) == c).astype(float), name=col_name, index=X.index)
                )

        if X_cat_dummies:
            X_cat_df = pd.concat(X_cat_dummies, axis=1)
            X_all = pd.concat([X_num, X_cat_df], axis=1)
        else:
            X_all = X_num

        self.encoded_feature_names = list(X_all.columns)

        # 3. Ridge Regression with intercept: beta = (X^T X + lambda I)^(-1) X^T y
        X_mat = X_all.values
        y_vec = y.values.astype(float)
        
        # Prepend bias column of 1s
        N = X_mat.shape[0]
        D = X_mat.shape[1]
        X_bias = np.hstack([np.ones((N, 1)), X_mat])
        
        # Regularization matrix (do not regularize intercept)
        reg_matrix = self.l2_reg * np.eye(D + 1)
        reg_matrix[0, 0] = 0.0

        try:
            beta = np.linalg.solve(X_bias.T @ X_bias + reg_matrix, X_bias.T @ y_vec)
        except np.linalg.LinAlgError:
            beta = np.linalg.pinv(X_bias.T @ X_bias + reg_matrix) @ (X_bias.T @ y_vec)

        self.intercept = float(beta[0])
        self.weights = beta[1:]

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X = X.copy()
        X_num = pd.DataFrame(index=X.index)
        for col in self.num_features:
            val = X[col].fillna(self.medians.get(col, 0.0))
            X_num[col] = (val - self.means.get(col, 0.0)) / self.stds.get(col, 1.0)

        X_cat_dummies = []
        for col in self.cat_features:
            cats = self.cat_categories.get(col, [])
            for c in cats:
                col_name = f"{col}_{c}"
                if col in X.columns:
                    series = (X[col].astype(str) == c).astype(float)
                else:
                    series = pd.Series(0.0, index=X.index)
                series.name = col_name
                X_cat_dummies.append(series)

        if X_cat_dummies:
            X_cat_df = pd.concat(X_cat_dummies, axis=1)
            X_all = pd.concat([X_num, X_cat_df], axis=1)
        else:
            X_all = X_num

        # Align with fit features
        for f in self.encoded_feature_names:
            if f not in X_all.columns:
                X_all[f] = 0.0
        X_all = X_all[self.encoded_feature_names]

        preds = self.intercept + X_all.values @ self.weights
        return preds

# --------------------------------------------------------------------------
# Main Model Trainer Function
# --------------------------------------------------------------------------
def train_house_price_model(df: pd.DataFrame, col_mapping: dict):
    """
    Builds and trains the house price regression model.
    Uses Scikit-Learn if available; otherwise uses PureNumpyRegressionPipeline.
    """
    target_col, num_features, cat_features = get_feature_and_target_columns(df, col_mapping)
    
    if not target_col or len(num_features) + len(cat_features) == 0:
        return {
            "status": "error",
            "message": "Cannot train model: Target 'Price' column or feature columns missing."
        }

    valid_df = df.dropna(subset=[target_col]).copy()
    if len(valid_df) < 20:
        return {
            "status": "error",
            "message": f"Dataset too small ({len(valid_df)} rows) to train a reliable model. Need at least 20 records."
        }

    all_features = num_features + cat_features
    X = valid_df[all_features]
    y = valid_df[target_col]

    # Train-test split (80/20) using reproducible random state
    np.random.seed(42)
    indices = np.random.permutation(len(valid_df))
    test_size = int(len(valid_df) * (0.20 if len(valid_df) >= 50 else 0.10))
    test_idx = indices[:test_size]
    train_idx = indices[test_size:]

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    if SKLEARN_AVAILABLE:
        try:
            transformers = []
            if num_features:
                num_pipeline = Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler())
                ])
                transformers.append(("num", num_pipeline, num_features))

            if cat_features:
                cat_pipeline = Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
                ])
                transformers.append(("cat", cat_pipeline, cat_features))

            preprocessor = ColumnTransformer(transformers=transformers)
            regressor = RandomForestRegressor(
                n_estimators=100, random_state=42, max_depth=15, min_samples_split=3, n_jobs=-1
            )
            model_pipeline = Pipeline([
                ("preprocessor", preprocessor),
                ("regressor", regressor)
            ])
            model_pipeline.fit(X_train, y_train)
            y_pred = model_pipeline.predict(X_test)

            r2 = float(r2_score(y_test, y_pred))
            mae = float(mean_absolute_error(y_test, y_pred))
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

            # Feature importances
            feature_names = []
            if num_features:
                feature_names.extend(num_features)
            if cat_features:
                try:
                    ohe = model_pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["encoder"]
                    feature_names.extend(list(ohe.get_feature_names_out(cat_features)))
                except Exception:
                    feature_names.extend(cat_features)
            importances = regressor.feature_importances_

            return {
                "status": "success",
                "model_name": "Random Forest Regressor (Scikit-Learn)",
                "pipeline": model_pipeline,
                "engine": "sklearn",
                "metrics": {"r2": r2, "mae": mae, "rmse": rmse},
                "num_features": num_features,
                "cat_features": cat_features,
                "all_features": all_features,
                "feature_names": feature_names,
                "importances": importances,
                "train_count": len(X_train),
                "test_count": len(X_test),
                "target_col": target_col
            }
        except Exception:
            pass

    # Pure NumPy / Pandas Pipeline fallback
    numpy_pipe = PureNumpyRegressionPipeline(num_features, cat_features, l2_reg=1.0)
    numpy_pipe.fit(X_train, y_train)
    y_pred = numpy_pipe.predict(X_test)
    y_test_vals = y_test.values.astype(float)

    # Compute metrics
    ss_res = np.sum((y_test_vals - y_pred) ** 2)
    ss_tot = np.sum((y_test_vals - np.mean(y_test_vals)) ** 2)
    r2 = float(1.0 - (ss_res / (ss_tot + 1e-9)))
    mae = float(np.mean(np.abs(y_test_vals - y_pred)))
    rmse = float(np.sqrt(np.mean((y_test_vals - y_pred) ** 2)))

    # Compute relative feature importances based on standardized weights
    abs_weights = np.abs(numpy_pipe.weights)
    total_w = np.sum(abs_weights)
    importances = (abs_weights / (total_w + 1e-9)) if total_w > 0 else abs_weights

    return {
        "status": "success",
        "model_name": "Multi-Variable Regression (Pure-Python Native)",
        "pipeline": numpy_pipe,
        "engine": "numpy",
        "metrics": {"r2": r2, "mae": mae, "rmse": rmse},
        "num_features": num_features,
        "cat_features": cat_features,
        "all_features": all_features,
        "feature_names": numpy_pipe.encoded_feature_names,
        "importances": importances,
        "train_count": len(X_train),
        "test_count": len(X_test),
        "target_col": target_col
    }

def predict_single_house_price(pipeline, input_data: dict, feature_cols: list) -> float:
    """
    Predicts house price for a single property configuration dict.
    Supports both Scikit-Learn Pipeline and PureNumpyRegressionPipeline.
    """
    df_input = pd.DataFrame([input_data])
    for col in feature_cols:
        if col not in df_input.columns:
            df_input[col] = np.nan

    prediction = pipeline.predict(df_input[feature_cols])
    return float(prediction[0])

def predict_house_price_with_interval(pipeline, input_data: dict, feature_cols: list) -> tuple[float, float | None, float | None]:
    """
    Predicts house price and calculates the 10th-90th percentile prediction interval
    using individual trees in the fitted RandomForestRegressor when available.
    """
    df_input = pd.DataFrame([input_data])
    for col in feature_cols:
        if col not in df_input.columns:
            df_input[col] = np.nan

    prediction = float(pipeline.predict(df_input[feature_cols])[0])
    range_low, range_high = None, None

    try:
        if hasattr(pipeline, "named_steps") and "regressor" in pipeline.named_steps:
            preprocessor = pipeline.named_steps.get("preprocessor")
            regressor = pipeline.named_steps.get("regressor")
            if preprocessor is not None and hasattr(regressor, "estimators_") and len(regressor.estimators_) > 0:
                X_trans = preprocessor.transform(df_input[feature_cols])
                tree_preds = [float(tree.predict(X_trans)[0]) for tree in regressor.estimators_]
                range_low = float(np.percentile(tree_preds, 10))
                range_high = float(np.percentile(tree_preds, 90))
    except Exception:
        range_low, range_high = None, None

    return prediction, range_low, range_high

# --------------------------------------------------------------------------
# What-If Sensitivity Simulator Functions
# --------------------------------------------------------------------------
def generate_what_if_scenarios(
    pipeline,
    base_input: dict,
    feature_cols: list,
    df_clean: pd.DataFrame,
    col_mapping: dict
) -> tuple[float, pd.DataFrame, pd.DataFrame]:
    """
    Builds What-If sensitivity scenarios by modifying one attribute at a time.
    Re-predicts with the trained machine-learning model.
    Returns:
        base_price: float
        df_scenarios: DataFrame with columns ['Scenario', 'New Price', 'Change (₹)', 'Change (%)']
        df_locations: DataFrame with columns ['Location', 'New Price', 'Change (₹)', 'Change (%)']
    """
    from utils.data_processing import find_column

    base_price = float(predict_single_house_price(pipeline, base_input, feature_cols))
    scenario_inputs = []

    a_col = col_mapping.get("area") or find_column(df_clean, ["Area", "area", "Sqft", "Square Feet"])
    bed_col = col_mapping.get("bedrooms") or find_column(df_clean, ["Bedrooms", "bedroom", "Beds", "bhk"])
    bath_col = col_mapping.get("bathrooms") or find_column(df_clean, ["Bathrooms", "bathroom", "Baths"])
    park_col = col_mapping.get("parking") or find_column(df_clean, ["Parking", "parking", "Garage"])
    furn_col = col_mapping.get("furnishing") or find_column(df_clean, ["Furnishing", "furnishing", "Furnished"])
    yr_col = col_mapping.get("year_built") or find_column(df_clean, ["Year Built", "year_built", "YearBuilt", "Year"])
    loc_col = col_mapping.get("location") or find_column(df_clean, ["Location", "location", "City", "Locality"])

    # 1. +200 sqft area
    if a_col and a_col in base_input and a_col in df_clean.columns:
        try:
            curr_a = float(base_input[a_col])
            max_a = float(df_clean[a_col].dropna().max())
            new_a = min(curr_a + 200, max_a)
            if new_a > curr_a:
                alt = dict(base_input)
                alt[a_col] = new_a
                scenario_inputs.append(("+200 sqft area", alt))
        except Exception:
            pass

    # 2. +1 bedroom
    if bed_col and bed_col in base_input and bed_col in df_clean.columns:
        try:
            curr_b = int(base_input[bed_col])
            max_b = int(df_clean[bed_col].dropna().max())
            new_b = min(curr_b + 1, max_b)
            if new_b > curr_b:
                alt = dict(base_input)
                alt[bed_col] = new_b
                scenario_inputs.append(("+1 bedroom", alt))
        except Exception:
            pass

    # 3. +1 bathroom
    if bath_col and bath_col in base_input and bath_col in df_clean.columns:
        try:
            curr_ba = int(base_input[bath_col])
            max_ba = int(df_clean[bath_col].dropna().max())
            new_ba = min(curr_ba + 1, max_ba)
            if new_ba > curr_ba:
                alt = dict(base_input)
                alt[bath_col] = new_ba
                scenario_inputs.append(("+1 bathroom", alt))
        except Exception:
            pass

    # 4. Add parking (only if currently No or 0)
    if park_col and park_col in base_input and park_col in df_clean.columns:
        try:
            curr_p = str(base_input[park_col]).strip().lower()
            if curr_p in ["no", "0", "none", "false", "without", "n"]:
                unique_p = df_clean[park_col].dropna().unique().tolist()
                pos_vals = [v for v in unique_p if str(v).strip().lower() in ["yes", "1", "true", "available", "y"]]
                target_p = pos_vals[0] if pos_vals else "Yes"
                alt = dict(base_input)
                alt[park_col] = target_p
                scenario_inputs.append(("Add parking", alt))
        except Exception:
            pass

    # 5. Upgrade furnishing one level (Unfurnished -> Semi-Furnished -> Furnished)
    if furn_col and furn_col in base_input and furn_col in df_clean.columns:
        try:
            curr_f = str(base_input[furn_col]).strip().lower()
            unique_f = df_clean[furn_col].dropna().unique().tolist()
            semi_matches = [v for v in unique_f if "semi" in str(v).lower()]
            furn_matches = [v for v in unique_f if "furn" in str(v).lower() and "un" not in str(v).lower() and "semi" not in str(v).lower()]
            target_f = None
            if "unfurn" in curr_f and semi_matches:
                target_f = semi_matches[0]
            elif ("semi" in curr_f or "unfurn" in curr_f) and furn_matches:
                target_f = furn_matches[0]

            if target_f is not None and str(target_f) != str(base_input[furn_col]):
                alt = dict(base_input)
                alt[furn_col] = target_f
                scenario_inputs.append(("Upgrade furnishing one level", alt))
        except Exception:
            pass

    # 6. Newer build (+5 years, max current year)
    if yr_col and yr_col in base_input and yr_col in df_clean.columns:
        try:
            curr_yr = int(base_input[yr_col])
            max_yr = min(int(df_clean[yr_col].dropna().max()), 2026)
            new_yr = min(curr_yr + 5, max_yr)
            if new_yr > curr_yr:
                alt = dict(base_input)
                alt[yr_col] = new_yr
                scenario_inputs.append(("Newer build (+5 years)", alt))
        except Exception:
            pass

    # Predict scenarios
    scenario_rows = []
    for name, alt_data in scenario_inputs:
        try:
            new_p = float(predict_single_house_price(pipeline, alt_data, feature_cols))
            diff = new_p - base_price
            pct = (diff / base_price * 100) if base_price > 0 else 0.0
            scenario_rows.append({
                "Scenario": name,
                "New Price": new_p,
                "Change (₹)": diff,
                "Change (%)": pct
            })
        except Exception:
            continue

    df_scenarios = pd.DataFrame(scenario_rows)
    if not df_scenarios.empty:
        df_scenarios = df_scenarios.sort_values(by="Change (₹)", ascending=False).reset_index(drop=True)

    # 7. Move to another location (one row per other location)
    loc_rows = []
    if loc_col and loc_col in base_input and loc_col in df_clean.columns:
        try:
            curr_loc = str(base_input[loc_col])
            other_locs = sorted([l for l in df_clean[loc_col].dropna().unique() if str(l) != curr_loc])
            for other_l in other_locs:
                alt = dict(base_input)
                alt[loc_col] = other_l
                new_p = float(predict_single_house_price(pipeline, alt, feature_cols))
                diff = new_p - base_price
                pct = (diff / base_price * 100) if base_price > 0 else 0.0
                loc_rows.append({
                    "Location": other_l,
                    "New Price": new_p,
                    "Change (₹)": diff,
                    "Change (%)": pct
                })
        except Exception:
            pass

    df_locations = pd.DataFrame(loc_rows)
    if not df_locations.empty:
        df_locations = df_locations.sort_values(by="Change (₹)", ascending=False).reset_index(drop=True)

    return base_price, df_scenarios, df_locations


def generate_price_vs_area_curve(
    pipeline,
    base_input: dict,
    feature_cols: list,
    df_clean: pd.DataFrame,
    col_mapping: dict
):
    """
    Predicts the price for 15 area values from 5th to 95th percentile,
    keeping other inputs fixed, and marks the user's current area.
    Returns:
        (area_points, curve_preds, curr_area, curr_price) or None
    """
    from utils.data_processing import find_column

    a_col = col_mapping.get("area") or find_column(df_clean, ["Area", "area", "Sqft", "Square Feet"])
    if not a_col or a_col not in df_clean.columns or a_col not in base_input:
        return None

    try:
        series_a = pd.to_numeric(df_clean[a_col], errors='coerce').dropna()
        if series_a.empty:
            return None
        min_p = float(np.percentile(series_a, 5))
        max_p = float(np.percentile(series_a, 95))
        if min_p >= max_p:
            min_p = float(series_a.min())
            max_p = float(series_a.max())
            if min_p >= max_p:
                return None

        area_points = [float(x) for x in np.linspace(min_p, max_p, 15).round(0)]
        df_curve = pd.DataFrame([base_input] * len(area_points))
        df_curve[a_col] = area_points

        curve_preds = [float(p) for p in pipeline.predict(df_curve[feature_cols])]
        curr_a = float(base_input[a_col])
        curr_p = float(predict_single_house_price(pipeline, base_input, feature_cols))
        return area_points, curve_preds, curr_a, curr_p
    except Exception:
        return None


# --------------------------------------------------------------------------
# Batch Valuation Functions
# --------------------------------------------------------------------------
def align_batch_columns(
    df_batch: pd.DataFrame,
    expected_features: list,
    canonical_col_mapping: dict
) -> tuple[pd.DataFrame, list[str], dict]:
    """
    Aligns and detects column names in df_batch to match expected_features.
    Uses canonical alias lookup and normalized string matching.
    Returns:
        df_aligned: DataFrame with standardized column names
        missing_required: list of expected feature names not found
        mapped_dict: dict of {source_col: target_feature}
    """
    from utils.data_processing import CANONICAL_ALIASES, find_column

    df_aligned = df_batch.copy()
    mapped_dict = {}

    expected_to_canon = {actual: canon for canon, actual in canonical_col_mapping.items()}

    for feat in expected_features:
        if feat in df_aligned.columns:
            mapped_dict[feat] = feat
            continue

        found_col = None
        canon_key = expected_to_canon.get(feat)
        if canon_key and canon_key in CANONICAL_ALIASES:
            aliases = CANONICAL_ALIASES[canon_key]
            found_col = find_column(df_aligned, aliases)

        if not found_col:
            found_col = find_column(df_aligned, [feat])

        if found_col and found_col in df_aligned.columns:
            df_aligned[feat] = df_aligned[found_col]
            mapped_dict[found_col] = feat

    missing_required = [f for f in expected_features if f not in df_aligned.columns]
    return df_aligned, missing_required, mapped_dict


def batch_predict_house_prices(
    pipeline,
    df_batch: pd.DataFrame,
    feature_cols: list,
    area_col: str | None = None
) -> pd.DataFrame:
    """
    Vectorized batch prediction for the entire DataFrame.
    Adds Predicted_Price, Low (10th percentile), High (90th percentile), and Rate_per_sqft.
    """
    df_result = df_batch.copy()
    X = df_result[feature_cols]

    # 1. Main Vectorized Prediction
    raw_preds = pipeline.predict(X)
    df_result["Predicted_Price"] = np.round(raw_preds, 0).astype(float)

    # 2. 10th-90th Percentile Intervals from Random Forest Trees
    lows = None
    highs = None
    try:
        if hasattr(pipeline, "named_steps") and "regressor" in pipeline.named_steps:
            preprocessor = pipeline.named_steps.get("preprocessor")
            regressor = pipeline.named_steps.get("regressor")
            if preprocessor is not None and hasattr(regressor, "estimators_") and len(regressor.estimators_) > 0:
                X_trans = preprocessor.transform(X)
                tree_preds = np.array([tree.predict(X_trans) for tree in regressor.estimators_])
                lows = np.percentile(tree_preds, 10, axis=0).round(0)
                highs = np.percentile(tree_preds, 90, axis=0).round(0)
    except Exception:
        lows = None
        highs = None

    if lows is not None and highs is not None:
        df_result["Low"] = lows
        df_result["High"] = highs
    else:
        df_result["Low"] = np.nan
        df_result["High"] = np.nan

    # 3. Implied Rate per Sqft
    if area_col and area_col in df_result.columns:
        numeric_area = pd.to_numeric(df_result[area_col], errors='coerce')
        df_result["Rate_per_sqft"] = np.where(
            numeric_area > 0,
            np.round(df_result["Predicted_Price"] / numeric_area, 0),
            np.nan
        )
    else:
        df_result["Rate_per_sqft"] = np.nan

    return df_result

