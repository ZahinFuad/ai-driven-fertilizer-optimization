"""Prepare Brazil soybean fertilizer and yield data for modeling."""

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping

from _paths import ARTIFACT_TABLES, RAW_DATA, ensure_artifact_dirs, require_file


CROP_NAME_MAPPING = {"Soybean": "Soya beans"}
TARGET_COUNTRIES = ["Brazil"]
TARGET_CROPS = ["Soybean"]
TARGET_NUTRIENTS = ["N", "P2O5", "K2O"]
TARGET_YEARS = range(1961, 2020)


def main() -> None:
    ensure_artifact_dirs()

    tif_folder = RAW_DATA / "Cropland_Maps"
    faostat_file = RAW_DATA / "Production_Crops_Livestock_E_All_Data.csv"
    shapefile_path = RAW_DATA / "ne_110m_admin_0_countries.shp"

    require_file(faostat_file, "Missing raw FAOSTAT data. See data/README.md.")
    require_file(shapefile_path, "Missing Natural Earth shapefile. See data/README.md.")
    if not tif_folder.exists():
        raise FileNotFoundError(f"Missing fertilizer GeoTIFF folder.\nExpected path: {tif_folder}")

    print("Loading country shapefile...")
    world = gpd.read_file(shapefile_path)
    world = world[world["ADMIN"].isin(TARGET_COUNTRIES)].to_crs("EPSG:4326")

    print("Processing fertilizer GeoTIFF files...")
    results = []
    for tif_path in tif_folder.glob("*.tiff"):
        name = tif_path.name
        for crop in TARGET_CROPS:
            for nutrient in TARGET_NUTRIENTS:
                for year in TARGET_YEARS:
                    if crop in name and nutrient in name and str(year) in name:
                        with rasterio.open(tif_path) as src:
                            for _, row in world.iterrows():
                                geometry = [mapping(row["geometry"])]
                                out_image, _ = mask(src, geometry, crop=True)
                                masked_data = out_image[0]
                                positive = masked_data[masked_data > 0]
                                mean_val = np.nan if positive.size == 0 else np.nanmean(positive)
                                results.append(
                                    {
                                        "Country": row["ADMIN"],
                                        "Year": year,
                                        "Crop": crop,
                                        "Nutrient": nutrient,
                                        "Mean_kg_ha": round(float(mean_val), 2),
                                    }
                                )

    fertilizer_df = pd.DataFrame(results)
    print(f"Extracted {len(fertilizer_df)} fertilizer records.")

    print("Loading FAOSTAT yield data...")
    faostat_df = pd.read_csv(faostat_file, low_memory=False)
    value_vars = [col for col in faostat_df.columns if col.startswith("Y")]
    faostat_long = faostat_df.melt(
        id_vars=["Area", "Item", "Element", "Unit"],
        value_vars=value_vars,
        var_name="Year",
        value_name="Value",
    )
    faostat_long["Year"] = faostat_long["Year"].str.extract(r"(\d+)", expand=False).astype(int)

    faostat_filtered = faostat_long[
        (faostat_long["Element"] == "Yield") & (faostat_long["Area"].isin(TARGET_COUNTRIES))
    ].copy()
    faostat_filtered = faostat_filtered.rename(
        columns={"Area": "Country", "Item": "Crop", "Value": "Yield_kg_ha"}
    )
    reverse_mapping = {v: k for k, v in CROP_NAME_MAPPING.items()}
    faostat_filtered["Crop"] = faostat_filtered["Crop"].replace(reverse_mapping)
    faostat_filtered = faostat_filtered[faostat_filtered["Crop"].isin(TARGET_CROPS)]
    faostat_filtered = faostat_filtered[
        pd.to_numeric(faostat_filtered["Yield_kg_ha"], errors="coerce").notnull()
    ]
    faostat_filtered["Yield_kg_ha"] = pd.to_numeric(faostat_filtered["Yield_kg_ha"])

    merged_df = pd.merge(
        fertilizer_df,
        faostat_filtered,
        on=["Country", "Year", "Crop"],
        how="inner",
    )
    pivot_df = merged_df.pivot_table(
        index=["Country", "Year", "Crop", "Yield_kg_ha"],
        columns="Nutrient",
        values="Mean_kg_ha",
    ).reset_index()
    pivot_df = pivot_df.rename(columns={"N": "N_kg_ha", "P2O5": "P2O5_kg_ha", "K2O": "K2O_kg_ha"})

    fertilizer_df.to_csv(ARTIFACT_TABLES / "fertilizer_aggregated.csv", index=False)
    faostat_filtered.to_csv(ARTIFACT_TABLES / "faostat_filtered_yield.csv", index=False)
    pivot_df.to_csv(ARTIFACT_TABLES / "merged_modeling_data_wide.csv", index=False)
    print(f"Prepared data written to {ARTIFACT_TABLES}")


if __name__ == "__main__":
    main()

