"""Categorize Pareto-front fertilizer solutions into strategy groups."""

import pandas as pd

from _paths import ARTIFACT_TABLES, PROCESSED_DATA, ensure_artifact_dirs, require_file


def categorize(total_input: float) -> str:
    if total_input <= 3:
        return "Sustainable"
    if total_input <= 10:
        return "Balanced"
    return "High-Yield"


def main() -> None:
    ensure_artifact_dirs()
    frontier_path = ARTIFACT_TABLES / "nsga2_pareto_front.csv"
    if not frontier_path.exists():
        frontier_path = require_file(
            PROCESSED_DATA / "nsga2_pareto_front.csv",
            "Missing Pareto frontier. Run 03_optimize_fertilizer.py or restore data/processed.",
        )

    df = pd.read_csv(frontier_path)
    df["Strategy"] = df["Total_Input"].apply(categorize)
    summary = (
        df.groupby("Strategy")
        .agg({"Total_Input": ["min", "mean", "max"], "Predicted_Yield_kg_ha": ["min", "mean", "max"]})
        .round(2)
    )

    df.to_csv(ARTIFACT_TABLES / "phase_7_tagged_strategies.csv", index=False)
    summary.to_csv(ARTIFACT_TABLES / "phase_7_strategy_summary.csv")
    print(summary)
    print(f"Strategy outputs written to {ARTIFACT_TABLES}")


if __name__ == "__main__":
    main()

