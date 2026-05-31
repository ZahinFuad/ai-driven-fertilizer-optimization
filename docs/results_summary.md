# Results Summary

## Model Comparison

Paper-reported model performance:

| Model | R2 | RMSE | MAE |
|---|---:|---:|---:|
| Linear Regression | 0.807 | 359.08 | 322.27 |
| XGBoost Regressor | 0.934 | 210.72 | 178.42 |
| Random Forest | 0.951 | 181.95 | 163.84 |

Random Forest achieved the best overall predictive performance and was used for downstream optimization.

## Optimization Findings

The paper reports that the initial single-objective optimization could not satisfy the 90th percentile yield target of 2932.3 kg/ha, with the best exploratory setup reaching approximately 1701.7 kg/ha. NSGA-II was then used to expose the trade-off between total fertilizer input and predicted soybean yield.

The curated frontier and strategy figures are available in `results/figures/`:

- `fig1_methodology_pipeline.png`
- `yield_response_curve.png`
- `fig3_pareto_frontier.png`
- `fig6_strategy_map.png`
- `correlation_heatmap.png`
- `feature_importance_rf_v2.png`

## Scenario Findings

The paper reports that N and P2O5 reductions of up to 30 percent can be explored with limited predicted yield loss. N showed a near-plateau response, and P2O5 yield response remained largely stable in the tested reduction range.

## Input Variable Analysis

The paper reports that Pearson correlation ranked P2O5 highest in linear association with yield, followed by K2O and N. Random Forest feature importance identified K2O as the strongest nonlinear predictor, supporting the strategy recommendation that K2O should be managed carefully under constrained fertilizer input scenarios.

## Strategy Groups

The Pareto solutions are grouped into:

- Sustainable: lowest total input.
- Balanced: middle input range.
- High-Yield: high predicted yield at higher input levels.

These categories are intended to make the trade-off surface easier to communicate to farmers, policymakers, or research reviewers.

