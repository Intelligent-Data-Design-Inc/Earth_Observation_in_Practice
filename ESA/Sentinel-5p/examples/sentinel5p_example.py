#!/usr/bin/env python3
"""Read a Sentinel-5P TROPOMI Level-2 NO2 NetCDF-4 file.

The script opens the file with the standard netCDF4 Python API, applies
scale_factor and _FillValue attributes automatically, filters the
nitrogen-dioxide tropospheric column on the qa_value quality field, and
prints a short summary of valid measurements.
"""

import argparse
import sys
from pathlib import Path

import netCDF4
import numpy as np

QA_THRESHOLD = 0.5


def read_var(group, name):
    """Return a variable's data as a NumPy array with the time dimension removed.

    Auto-scaling and _FillValue masking are applied by the netCDF4
    library; the result is converted from a masked array to a NumPy array
    with NaN for missing values.  Singleton dimensions are squeezed out.
    """
    var = group[name]
    var.set_auto_maskandscale(True)
    data = var[:]
    return np.ma.filled(np.squeeze(data), np.nan)


def main():
    parser = argparse.ArgumentParser(
        description="Summarise a Sentinel-5P TROPOMI L2 NO2 NetCDF-4 file."
    )
    parser.add_argument("file", type=Path, help="Path to the Sentinel-5P .nc file.")
    args = parser.parse_args()

    nc = netCDF4.Dataset(args.file, "r")
    print(f"File: {args.file}")
    print(f"Format: {nc.file_format}")
    print(f"Title: {nc.title}")
    print(f"Platform: {nc.platform}")
    print(f"Sensor: {nc.sensor}")
    print(f"Product: {nc.id}")
    print(f"Orbit: {nc.orbit}")
    print(f"Time coverage: {nc.time_coverage_start} to {nc.time_coverage_end}")
    print(f"Spatial resolution: {nc.spatial_resolution}")
    print()

    product = nc.groups["PRODUCT"]
    print(
        f"PRODUCT dimensions: "
        f"scanline={product.dimensions['scanline'].size}, "
        f"ground_pixel={product.dimensions['ground_pixel'].size}"
    )

    lat = read_var(product, "latitude")
    lon = read_var(product, "longitude")
    no2 = read_var(product, "nitrogendioxide_tropospheric_column")
    qa = read_var(product, "qa_value")

    valid = (
        (qa >= QA_THRESHOLD)
        & np.isfinite(lat)
        & np.isfinite(lon)
        & np.isfinite(no2)
    )

    n_total = lat.size
    n_valid = int(np.sum(valid))
    print(f"\nTotal pixels: {n_total}")
    print(f"Valid NO2 pixels (qa_value >= {QA_THRESHOLD}): {n_valid}")

    if n_valid == 0:
        print("No valid NO2 pixels found.")
        return

    print(f"\nGeographic extent (all records):")
    print(f"  latitude: {np.nanmin(lat):.4f} to {np.nanmax(lat):.4f}")
    print(f"  longitude: {np.nanmin(lon):.4f} to {np.nanmax(lon):.4f}")

    no2_valid = no2[valid]
    print(f"\nNO2 tropospheric column summary:")
    print(
        f"  count={no2_valid.size}, "
        f"mean={np.nanmean(no2_valid):.4e} mol m-2, "
        f"min={np.nanmin(no2_valid):.4e} mol m-2, "
        f"max={np.nanmax(no2_valid):.4e} mol m-2"
    )

    nc.close()


if __name__ == "__main__":
    main()
