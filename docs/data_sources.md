# Data Sources

## Fertilizer Application Maps

The fertilizer inputs come from crop-specific global fertilizer application maps in GeoTIFF format. The analysis uses soybean maps for nitrogen (N), phosphorus (P2O5), and potassium (K2O) from 1961-2019.

These raw GeoTIFFs are excluded from Git because the folder is several gigabytes.

## FAOSTAT Yield Data

Soybean yield data comes from the FAOSTAT crop production domain. The original FAOSTAT item name `Soya beans` is mapped to `Soybean` for alignment with fertilizer map filenames.

The full FAOSTAT CSV is excluded from Git. The filtered and modeling-ready derived files are included in `data/processed/`.

## Country Boundaries

Country-level extraction uses Natural Earth Admin-0 boundaries to mask fertilizer rasters to Brazil.

Natural Earth files are kept locally under `data/raw/` but ignored by Git.

