#!/usr/bin/env python3
"""Read a Sentinel-3 SRAL Level-2 SAFE product and summarize measurement data.

This example reads the standard measurement NetCDF inside an SRAL L2 product
(SL_2_WAT___, SL_2_LAN___, or SL_2_SI___ variants) and prints statistics for
the 20 Hz Ku-band geolocation, range, backscatter, and 1 Hz wind variables.

Usage:
    python3 sral_l2_example.py /path/to/S3?_SR_2_*.SEN3

The path may be the extracted `.SEN3` directory or the original `.zip` file.
"""

import argparse
import zipfile
from pathlib import Path

import netCDF4
import numpy as np


def open_safe(path: str) -> Path:
    """Return the path to the extracted SAFE directory."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input not found: {path}")
    if p.is_dir():
        return p
    if p.suffix == ".zip":
        extract_dir = Path("/tmp/sral_extract")
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(p, "r") as z:
            z.extractall(extract_dir)
        dirs = [d for d in extract_dir.iterdir() if d.is_dir() and d.suffix == ".SEN3"]
        if not dirs:
            raise RuntimeError("No .SEN3 directory found in zip")
        return dirs[0]
    raise ValueError(f"Unsupported input: {path}")


def valid_mask(data):
    """Return a boolean mask of non-masked values."""
    if np.ma.is_masked(data):
        return ~np.ma.getmaskarray(data)
    return np.ones(data.shape, dtype=bool)


def summarize(name, data):
    """Print summary statistics for one variable."""
    mask = valid_mask(data)
    vals = np.array(data[mask])
    print(f"  {name}: valid={len(vals)}", end="")
    if len(vals) > 0:
        print(f", min={np.min(vals):.4f}, max={np.max(vals):.4f}, mean={np.mean(vals):.4f}")
    else:
        print()


def main():
    parser = argparse.ArgumentParser(description="Summarize SRAL L2 measurement data")
    parser.add_argument("safe_path", help="Path to SR_2_* SAFE directory or zip")
    args = parser.parse_args()

    safe_dir = open_safe(args.safe_path)
    meas_file = safe_dir / "standard_measurement.nc"
    if not meas_file.exists():
        raise FileNotFoundError(f"standard_measurement.nc not found in {safe_dir}")

    ds = netCDF4.Dataset(meas_file)

    print("File:", safe_dir.name)
    print("Title:", getattr(ds, "title", "N/A"))
    print("Mission:", getattr(ds, "mission_name", "N/A"))
    print("Product:", getattr(ds, "product_name", "N/A"))
    print("Processing baseline:", getattr(ds, "processing_baseline", "N/A"))
    print()

    # Time and location
    lat = ds["lat_20_ku"][:]
    lon = ds["lon_20_ku"][:]
    time = ds["time_20_ku"][:]
    mask = valid_mask(lat)

    print(f"20 Hz Ku records: {lat.shape[0]}")
    print(f"Valid geolocation records: {np.sum(mask)}")
    if np.sum(mask) > 0:
        print("  Latitude:", np.min(lat[mask]), "to", np.max(lat[mask]))
        print("  Longitude:", np.min(lon[mask]), "to", np.max(lon[mask]))
        print("  Time (sec since 2000-01-01):", np.min(time[mask]), "to", np.max(time[mask]))
    print()

    # Surface classification
    surf_class = ds["surf_class_20_ku"][:]
    valid_sc = valid_mask(surf_class)
    print("Surface class counts (surf_class_20_ku):")
    for val, count in zip(*np.unique(surf_class[valid_sc], return_counts=True)):
        print(f"  {val}: {count}")
    print()

    # Key measurement variables
    print("Key measurement summaries:")
    for vname in [
        "alt_20_ku",
        "range_water_20_ku",
        "sig0_water_20_ku",
        "range_sea_ice_20_ku",
        "sig0_sea_ice_sheet_20_ku",
        "elevation_ocog_20_ku",
    ]:
        if vname in ds.variables:
            summarize(vname, ds[vname][:])

    print("\n1 Hz auxiliary summaries:")
    for vname in ["wind_speed_alt_01_ku", "wind_speed_alt_01_plrm_ku"]:
        if vname in ds.variables:
            summarize(vname, ds[vname][:])

    ds.close()


if __name__ == "__main__":
    main()
