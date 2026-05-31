"""Run fertilizer optimization using the trained Random Forest model."""

import joblib
import numpy as np
import os
import pandas as pd
import warnings
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from scipy.optimize import minimize as scipy_minimize

from _paths import ARTIFACT_MODELS, ARTIFACT_TABLES, PROCESSED_DATA, ensure_artifact_dirs, require_file


FEATURE_COLUMNS = ["N_kg_ha", "P2O5_kg_ha", "K2O_kg_ha"]
NSGA2_POPULATION = int(os.getenv("NSGA2_POPULATION", "100"))
NSGA2_GENERATIONS = int(os.getenv("NSGA2_GENERATIONS", "200"))
warnings.filterwarnings("ignore", message="Values in x were outside bounds.*", category=RuntimeWarning)


def load_inputs():
    data = pd.read_csv(
        require_file(PROCESSED_DATA / "merged_modeling_data_wide.csv", "Missing processed modeling dataset.")
    )
    model = joblib.load(
        require_file(ARTIFACT_MODELS / "random_forest_model.pkl", "Missing trained Random Forest model. Run 02_train_models.py.")
    )
    scaler = joblib.load(
        require_file(ARTIFACT_MODELS / "feature_scaler.pkl", "Missing trained feature scaler. Run 02_train_models.py.")
    )
    return data, model, scaler


def predict_yield(model, scaler, values) -> float:
    frame = pd.DataFrame([values], columns=FEATURE_COLUMNS)
    return float(model.predict(scaler.transform(frame))[0])


def main() -> None:
    ensure_artifact_dirs()
    data, model, scaler = load_inputs()

    bounds_5_95 = [(data[col].quantile(0.05), data[col].quantile(0.95)) for col in FEATURE_COLUMNS]
    bounds_1_99 = [(data[col].quantile(0.01), data[col].quantile(0.99)) for col in FEATURE_COLUMNS]
    x0 = [data[col].median() for col in FEATURE_COLUMNS]
    target_yield = data["Yield_kg_ha"].quantile(0.90)

    def objective(x):
        return float(np.sum(x))

    def yield_constraint(x):
        return predict_yield(model, scaler, x) - target_yield

    single = scipy_minimize(
        objective,
        x0,
        bounds=bounds_5_95,
        constraints={"type": "ineq", "fun": yield_constraint},
        method="SLSQP",
    )
    exploratory = scipy_minimize(
        lambda x: -predict_yield(model, scaler, x),
        x0,
        bounds=bounds_1_99,
        method="SLSQP",
    )

    pd.DataFrame(
        [
            {
                "N_kg_ha": single.x[0],
                "P2O5_kg_ha": single.x[1],
                "K2O_kg_ha": single.x[2],
                "Total_Input": np.sum(single.x),
                "Predicted_Yield_kg_ha": predict_yield(model, scaler, single.x),
                "Target_Yield_kg_ha": target_yield,
                "Success": single.success,
            }
        ]
    ).to_csv(ARTIFACT_TABLES / "fertilizer_optimization_result.csv", index=False)

    pd.DataFrame(
        [
            {
                "N_kg_ha": exploratory.x[0],
                "P2O5_kg_ha": exploratory.x[1],
                "K2O_kg_ha": exploratory.x[2],
                "Total_Input": np.sum(exploratory.x),
                "Predicted_Yield_kg_ha": predict_yield(model, scaler, exploratory.x),
                "Success": exploratory.success,
            }
        ]
    ).to_csv(ARTIFACT_TABLES / "exploratory_optimization_result.csv", index=False)

    lower_bounds = [v[0] for v in bounds_1_99]
    upper_bounds = [v[1] for v in bounds_1_99]

    class FertilizerOptimizationProblem(ElementwiseProblem):
        def __init__(self):
            super().__init__(n_var=3, n_obj=2, n_constr=0, xl=lower_bounds, xu=upper_bounds)

        def _evaluate(self, x, out, *args, **kwargs):
            predicted = predict_yield(model, scaler, x)
            out["F"] = [np.sum(x), -predicted]

    res = minimize(
        FertilizerOptimizationProblem(),
        NSGA2(pop_size=NSGA2_POPULATION),
        get_termination("n_gen", NSGA2_GENERATIONS),
        seed=42,
        verbose=False,
    )

    frontier = pd.DataFrame(res.X, columns=FEATURE_COLUMNS)
    frontier["Total_Input"] = frontier[FEATURE_COLUMNS].sum(axis=1)
    frontier["Predicted_Yield_kg_ha"] = -res.F[:, 1]
    frontier.to_csv(ARTIFACT_TABLES / "nsga2_pareto_front.csv", index=False)
    print(f"Optimization outputs written to {ARTIFACT_TABLES}")


if __name__ == "__main__":
    main()
