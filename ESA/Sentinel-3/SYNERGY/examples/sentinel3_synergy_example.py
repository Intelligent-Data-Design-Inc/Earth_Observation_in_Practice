#!/usr/bin/env python3
"""Read a Sentinel-3 SYNERGY SY_2_VGP SAFE package.

The script expects the path to an unzipped `.SEN3` directory. It opens the
aerosol optical thickness file (`ag.nc`) and the VGT B0 reflectance file
(`B0.nc`), applies `scale_factor` and `_FillValue` masking automatically, and
prints a short summary of each variable.
"""

import argparse
import sys
from pathlib import Path

import netCDF4
import numpy as np


def read_var(nc, name):
    """Return a variable's data as a NumPy array with NaN for missing values."""
    var = nc[name]
    var.set_auto_maskandscale(True)
    return np.ma.filled(var[:], np.nan)


def summarize_file(nc_path, var_name=None):
    """Print a summary of one NetCDF file in the package."""
    nc = netCDF4.Dataset(nc_path, "r")
    try:
        if var_name is None:
            stem = Path(nc_path).stem
            # Data variables are stored in upper case (e.g., "ag.nc" -> "AG").
            var_name = stem.upper()
        if var_name not in nc.variables:
            print(f"Warning: {var_name} not found in {nc_path}", file=sys.stderr)
            return

        data = read_var(nc, var_name)
        lat = read_var(nc, "latitude")
        lon = read_var(nc, "longitude")
        valid = np.isfinite(data)
        n_valid = int(np.sum(valid))

        print(f"\nFile: {nc_path}")
        print(f"Title: {nc.title}")
        print(f"Dimensions: latitude={lat.size}, longitude={lon.size}")
        print(f"Valid pixels: {n_valid} / {data.size}")
        print(
            f"Geographic extent: latitude {np.nanmin(lat):.4f} to "
            f"{np.nanmax(lat):.4f}, longitude {np.nanmin(lon):.4f} to "
            f"{np.nanmax(lon):.4f}"
        )

        if n_valid == 0:
            print(f"  {var_name}: no valid data")
        else:
            units = getattr(nc[var_name], "units", "-")
            print(
                f"  {var_name}: count={n_valid}, "
                f"mean={np.nanmean(data[valid]):.6f} {units}, "
                f"min={np.nanmin(data[valid]):.6f} {units}, "
                f"max={np.nanmax(data[valid]):.6f} {units}"
            )
    finally:
        nc.close()


def main():
    parser = argparse.ArgumentParser(
        description="Summarise a Sentinel-3 SYNERGY SY_2_VGP .SEN3 package."
    )
    parser.add_argument(
        "sen3_dir",
        type=Path,
        help="Path to the unzipped .SEN3 directory containing the .nc files.",
    )
    args = parser.parse_args()

    if not args.sen3_dir.is_dir():
        print(f"Not a directory: {args.sen3_dir}", file=sys.stderr)
        sys.exit(1)

    # Print package-level metadata from one of the files.
    metadata_file = args.sen3_dir / "ag.nc"
    if not metadata_file.is_file():
        metadata_file = next(args.sen3_dir.glob("*.nc"), None)
    if metadata_file is None:
        print(f"No NetCDF files found in {args.sen3_dir}", file=sys.stderr)
        sys.exit(1)

    nc = netCDF4.Dataset(metadata_file, "r")
    print(f"SAFE package: {args.sen3_dir}")
    print(f"Product: {getattr(nc, 'product_name', 'N/A')}")
    print(f"Source: {getattr(nc, 'source', 'N/A')}")
    print(
        f"Time coverage: {getattr(nc, 'start_time', 'N/A')} to "
        f"{getattr(nc, 'stop_time', 'N/A')}"
    )
    print(f"Processing baseline: {getattr(nc, 'processing_baseline', 'N/A')}")
    nc.close()

    # Summarise the aerosol and B0 reflectance files if they exist.
    for filename in ("ag.nc", "B0.nc"):
        nc_path = args.sen3_dir / filename
        if nc_path.is_file():
            summarize_file(nc_path)


if __name__ == "__main__":
    main()
