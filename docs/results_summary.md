# Results Summary

## Model Comparison

| Model | R2 | RMSE | MAE |
|---|---:|---:|---:|
| Linear Regression | 0.807 | 359.08 | 322.27 |
| Random Forest | 0.948 | 186.33 | 166.33 |
| XGBoost | 0.934 | 210.72 | 178.42 |

Random Forest achieved the best overall predictive performance and was used for downstream optimization.

## Optimization Findings

The NSGA-II Pareto frontier shows a clear trade-off between total fertilizer input and predicted soybean yield. It supports a range of decision strategies rather than a single fixed fertilizer recommendation.

The curated frontier and strategy figures are available in `results/figures/`:

- `fig3_pareto_frontier.png`
- `fig6_strategy_map.png`
- `phase_7_strategy_visualization.png`

## Scenario Findings

The N and P2O5 reduction scenarios found limited predicted yield loss in the tested 10-30 percent reduction range. This supports the study's broader conclusion that fertilizer input can be reduced in targeted ways without necessarily sacrificing modeled yield.

## Strategy Groups

The Pareto solutions are grouped into:

- Sustainable: lowest total input.
- Balanced: middle input range.
- High-Yield: high predicted yield at higher input levels.

These categories are intended to make the trade-off surface easier to communicate to farmers, policymakers, or research reviewers.

