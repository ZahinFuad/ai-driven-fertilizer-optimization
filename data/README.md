# Data Notes

This repository tracks small processed datasets that are useful for reviewing and rerunning the public analysis workflow.

## Included

Files in `data/processed/` include:

- `fertilizer_aggregated.csv`: Brazil-level mean N, P2O5, and K2O fertilizer application values.
- `faostat_filtered_yield.csv`: filtered soybean yield records from FAOSTAT.
- `merged_modeling_data_wide.csv`: modeling-ready dataset with fertilizer inputs and yield.
- `model_evaluation_summary.csv`: model comparison metrics.
- `nsga2_pareto_front.csv`: Pareto frontier from NSGA-II optimization.
- Scenario and strategy output tables from later phases.

## Excluded

The following local inputs are intentionally ignored by Git:

- `data/raw/Cropland_Maps/`: crop-specific global fertilizer GeoTIFF maps.
- `data/raw/Production_Crops_Livestock_E_All_Data.csv`: raw FAOSTAT production data.
- `data/raw/ne_110m_admin_0_countries.*`: Natural Earth country boundary files.

These files are external datasets and are too large or source-owned for a lightweight public portfolio repository.

## Regenerating Processed Data

Place the raw inputs under `data/raw/`, then run:

```powershell
python scripts/01_prepare_data.py
```

The script writes regenerated processed CSVs to `artifacts/tables/` so existing curated files in `data/processed/` are not overwritten accidentally.

