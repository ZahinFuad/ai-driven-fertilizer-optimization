"""Generate final Pareto and strategy figures from processed outputs."""

import matplotlib.pyplot as plt
import pandas as pd

from _paths import ARTIFACT_FIGURES, ARTIFACT_TABLES, PROCESSED_DATA, ensure_artifact_dirs, require_file


def load_frontier() -> pd.DataFrame:
    path = ARTIFACT_TABLES / "phase_7_tagged_strategies.csv"
    if not path.exists():
        path = PROCESSED_DATA / "phase_7_tagged_strategies.csv"
    if not path.exists():
        path = ARTIFACT_TABLES / "nsga2_pareto_front.csv"
    if not path.exists():
        path = PROCESSED_DATA / "nsga2_pareto_front.csv"
    df = pd.read_csv(require_file(path, "Missing Pareto frontier data."))
    if "Strategy" not in df.columns:
        df["Strategy"] = pd.cut(
            df["Total_Input"],
            bins=[-float("inf"), 3, 10, float("inf")],
            labels=["Sustainable", "Balanced", "High-Yield"],
        )
    return df.sort_values("Total_Input")


def main() -> None:
    ensure_artifact_dirs()
    df = load_frontier()

    plt.figure(figsize=(7.5, 5.5))
    plt.scatter(
        df["Total_Input"],
        df["Predicted_Yield_kg_ha"],
        s=40,
        color="crimson",
        alpha=0.75,
        edgecolor="black",
        linewidth=0.3,
    )
    plt.xlabel("Total Fertilizer Input (kg/ha)")
    plt.ylabel("Predicted Yield (kg/ha)")
    plt.title("Pareto Frontier: Fertilizer Input vs. Predicted Yield")
    plt.grid(True, linestyle="--", linewidth=0.6, alpha=0.6)
    plt.tight_layout()
    plt.savefig(ARTIFACT_FIGURES / "fig3_pareto_frontier.png", dpi=300)
    plt.close()

    colors = {"Sustainable": "seagreen", "Balanced": "royalblue", "High-Yield": "darkorange"}
    plt.figure(figsize=(8, 5.5))
    for strategy, group in df.groupby("Strategy"):
        plt.scatter(
            group["Total_Input"],
            group["Predicted_Yield_kg_ha"],
            label=strategy,
            s=45,
            color=colors.get(str(strategy), "gray"),
            alpha=0.8,
            edgecolor="black",
            linewidth=0.25,
        )
    plt.xlabel("Total Fertilizer Input (kg/ha)")
    plt.ylabel("Predicted Yield (kg/ha)")
    plt.title("Fertilizer Strategy Map")
    plt.grid(True, linestyle="--", linewidth=0.6, alpha=0.6)
    plt.legend(title="Strategy")
    plt.tight_layout()
    plt.savefig(ARTIFACT_FIGURES / "fig6_strategy_map.png", dpi=300)
    plt.close()

    print(f"Figures written to {ARTIFACT_FIGURES}")


if __name__ == "__main__":
    main()

