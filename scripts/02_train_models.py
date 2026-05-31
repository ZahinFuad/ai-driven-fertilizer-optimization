"""Train yield prediction models from the processed fertilizer dataset."""

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from _paths import ARTIFACT_MODELS, ARTIFACT_TABLES, PROCESSED_DATA, ensure_artifact_dirs, require_file


FEATURE_COLUMNS = ["N_kg_ha", "P2O5_kg_ha", "K2O_kg_ha"]
TARGET_COLUMN = "Yield_kg_ha"


def evaluate(name: str, y_true, y_pred) -> dict:
    return {
        "Model": name,
        "R2": r2_score(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "MAE": mean_absolute_error(y_true, y_pred),
    }


def main() -> None:
    ensure_artifact_dirs()
    data_path = require_file(
        PROCESSED_DATA / "merged_modeling_data_wide.csv",
        "Missing processed modeling dataset. Run scripts/01_prepare_data.py or restore data/processed.",
    )
    data = pd.read_csv(data_path)
    features = data[FEATURE_COLUMNS]
    target = data[TARGET_COLUMN]

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    x_train, x_test, y_train, y_test = train_test_split(
        features_scaled, target, test_size=0.2, random_state=42
    )

    lr_model = LinearRegression()
    lr_model.fit(x_train, y_train)

    rf_grid = GridSearchCV(
        RandomForestRegressor(random_state=42),
        {"n_estimators": [100, 200], "max_depth": [5, 10, None]},
        cv=5,
        scoring="r2",
        n_jobs=1,
    )
    rf_grid.fit(x_train, y_train)

    xgb_grid = GridSearchCV(
        XGBRegressor(random_state=42, verbosity=0),
        {"n_estimators": [100, 200], "max_depth": [3, 5, 10]},
        cv=5,
        scoring="r2",
        n_jobs=1,
    )
    xgb_grid.fit(x_train, y_train)

    summary = pd.DataFrame(
        [
            evaluate("Linear Regression", y_test, lr_model.predict(x_test)),
            evaluate("Random Forest", y_test, rf_grid.best_estimator_.predict(x_test)),
            evaluate("XGBoost", y_test, xgb_grid.best_estimator_.predict(x_test)),
        ]
    )

    joblib.dump(lr_model, ARTIFACT_MODELS / "linear_regression_model.pkl")
    joblib.dump(rf_grid.best_estimator_, ARTIFACT_MODELS / "random_forest_model.pkl")
    joblib.dump(xgb_grid.best_estimator_, ARTIFACT_MODELS / "xgboost_model.pkl")
    joblib.dump(scaler, ARTIFACT_MODELS / "feature_scaler.pkl")
    summary.to_csv(ARTIFACT_TABLES / "model_evaluation_summary.csv", index=False)

    print(summary.round(3).to_string(index=False))
    print(f"Models written to {ARTIFACT_MODELS}")


if __name__ == "__main__":
    main()
