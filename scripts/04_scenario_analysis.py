"""Simulate N and P2O5 reduction scenarios using the trained model."""

import joblib
import matplotlib.pyplot as plt
import pandas as pd

from _paths import (
    ARTIFACT_FIGURES,
    ARTIFACT_MODELS,
    ARTIFACT_TABLES,
    PROCESSED_DATA,
    ensure_artifact_dirs,
    require_file,
)


FEATURE_COLUMNS = ["N_kg_ha", "P2O5_kg_ha", "K2O_kg_ha"]


def simulate_reduction(data, model, scaler, nutrient: str, label: str) -> pd.DataFrame:
    baseline = {col: data[col].median() for col in FEATURE_COLUMNS}
    scenarios = []
    for rate in [0, 0.10, 0.20, 0.30]:
        values = baseline.copy()
        values[nutrient] = values[nutrient] * (1 - rate)
        frame = pd.DataFrame([values], columns=FEATURE_COLUMNS)
        predicted = float(model.predict(scaler.transform(frame))[0])
        scenarios.append(
            {
                f"{label}_Reduction_%": int(rate * 100),
                **values,
                "Predicted_Yield_kg_ha": predicted,
            }
        )
    output = pd.DataFrame(scenarios)
    output["Yield_Change_%"] = (
        100
        * (output["Predicted_Yield_kg_ha"] - output["Predicted_Yield_kg_ha"].iloc[0])
        / output["Predicted_Yield_kg_ha"].iloc[0]
    )
    return output


def plot_scenario(df: pd.DataFrame, x_col: str, label: str) -> None:
    plt.figure(figsize=(8, 5))
    plt.plot(df[x_col], df["Predicted_Yield_kg_ha"], marker="o")
    plt.title(f"Yield Impact of {label} Reduction")
    plt.xlabel(f"{label} Reduction (%)")
    plt.ylabel("Predicted Yield (kg/ha)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(ARTIFACT_FIGURES / f"yield_vs_{label}_reduction.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(df[x_col], df["Yield_Change_%"], marker="s", color="green")
    plt.title(f"Yield Change vs {label} Reduction")
    plt.xlabel(f"{label} Reduction (%)")
    plt.ylabel("Yield Change (%)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(ARTIFACT_FIGURES / f"yield_change_vs_{label}_reduction.png", dpi=300)
    plt.close()


def main() -> None:
    ensure_artifact_dirs()
    data = pd.read_csv(require_file(PROCESSED_DATA / "merged_modeling_data_wide.csv", "Missing processed dataset."))
    model = joblib.load(require_file(ARTIFACT_MODELS / "random_forest_model.pkl", "Missing model. Run 02_train_models.py."))
    scaler = joblib.load(require_file(ARTIFACT_MODELS / "feature_scaler.pkl", "Missing scaler. Run 02_train_models.py."))

    n_results = simulate_reduction(data, model, scaler, "N_kg_ha", "N")
    p_results = simulate_reduction(data, model, scaler, "P2O5_kg_ha", "P2O5")

    n_results.to_csv(ARTIFACT_TABLES / "phase_4_1_N_reduction_results.csv", index=False)
    p_results.to_csv(ARTIFACT_TABLES / "phase_4_3_P2O5_reduction_results.csv", index=False)
    plot_scenario(n_results, "N_Reduction_%", "N")
    plot_scenario(p_results, "P2O5_Reduction_%", "P2O5")
    print(f"Scenario outputs written to {ARTIFACT_TABLES} and {ARTIFACT_FIGURES}")


if __name__ == "__main__":
    main()

