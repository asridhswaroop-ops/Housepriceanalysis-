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
