# Methodology

## 1. Data Preparation

The workflow extracts Brazil-level soybean fertilizer application rates from annual GeoTIFF rasters for N, P2O5, and K2O. It then filters FAOSTAT crop production records to soybean yield and merges fertilizer and yield data by country, crop, and year. The paper reports 59 complete Brazil-soybean records for 1961-2019 after harmonization.

The main modeling table is `data/processed/merged_modeling_data_wide.csv`.

## 2. Yield Modeling

Three supervised learning models are trained to predict yield from fertilizer inputs:

- Linear Regression as a baseline.
- Random Forest Regressor as the primary non-linear model.
- XGBoost Regressor as a boosted-tree comparison.

Features are standardized before training. The paper uses an 80/20 train-test split and five-fold cross-validation during training. Models are compared using R2, RMSE, and MAE.

## 3. Fertilizer Optimization

The best-performing Random Forest model is used as a surrogate objective function for fertilizer optimization. The experiments include:

- Single-objective optimization to minimize total fertilizer input.
- Wider-bound exploratory optimization.
- NSGA-II multi-objective optimization to minimize fertilizer input while maximizing predicted yield.

The paper describes NSGA-II with population size 100, 200 generations, crossover probability 0.9, mutation probability 0.05, and random seed 42.

## 4. Scenario Analysis

The scenario experiments simulate N and P2O5 reductions from baseline median fertilizer levels. Predicted yield is compared with the baseline to estimate sensitivity under reduced input levels.

## 5. Strategy Categorization

NSGA-II Pareto-front solutions are grouped into three strategy categories:

- Sustainable: lowest total fertilizer input.
- Balanced: moderate input and moderate predicted yield.
- High-Yield: higher input with higher predicted yield.

