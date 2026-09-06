#!/usr/bin/env python3
"""Read a Sentinel-3 SLSTR L2 LST SAFE product and summarize the LST variable.

This example reads the nadir-view NetCDF files inside an `SL_2_LST___` SAFE
package and computes statistics for the land-surface temperature (LST) data.

Usage:
    python3 slstr_lst_example.py /path/to/S3?_SL_2_LST____*.SEN3

The path may point to the extracted `.SEN3` directory or to the `.zip` file.
"""

import argparse
import sys
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
        extract_dir = Path("/tmp/slstr_extract")
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(p, "r") as z:
            z.extractall(extract_dir)
        dirs = [d for d in extract_dir.iterdir() if d.is_dir() and d.suffix == ".SEN3"]
        if not dirs:
            raise RuntimeError("No .SEN3 directory found in zip")
        return dirs[0]
    raise ValueError(f"Unsupported input: {path}")


def main():
    parser = argparse.ArgumentParser(description="Summarize SLSTR L2 LST data")
    parser.add_argument("safe_path", help="Path to SL_2_LST___ SAFE directory or zip")
    args = parser.parse_args()

    safe_dir = open_safe(args.safe_path)

    geo_ds = netCDF4.Dataset(safe_dir / "geodetic_in.nc")
    lat = geo_ds["latitude_in"][:]
    lon = geo_ds["longitude_in"][:]

    lst_ds = netCDF4.Dataset(safe_dir / "LST_in.nc")
    lst = lst_ds["LST"][:]
    unc = lst_ds["LST_uncertainty"][:]

    flags_ds = netCDF4.Dataset(safe_dir / "flags_in.nc")
    confidence = flags_ds["confidence_in"][:]
    cloud = flags_ds["cloud_in"][:]
    exception = lst_ds["exception"][:]

    # Mask out fill values (netCDF4 returns masked arrays by default).
    valid = (~lst.mask)

    # Count confidence flag settings among valid pixels.
    land = valid & ((confidence & 8) != 0)
    ocean = valid & ((confidence & 2) != 0)

    print("File:", safe_dir.name)
    print("Total grid:", lst.shape[0], "rows x", lst.shape[1], "columns")
    print("Valid LST pixels:", np.sum(valid))
    print("  Land pixels:", np.sum(land))
    print("  Ocean pixels:", np.sum(ocean))

    if np.sum(valid) > 0:
        print("\nGeographic extent (valid pixels):")
        print("  Latitude:", np.min(lat[valid]), "to", np.max(lat[valid]))
        print("  Longitude:", np.min(lon[valid]), "to", np.max(lon[valid]))

        print("\nLST summary (all valid pixels):")
        print("  Count:", np.sum(valid))
        print("  Mean:", np.mean(lst[valid]), "K")
        print("  Std:", np.std(lst[valid]), "K")
        print("  Min:", np.min(lst[valid]), "K")
        print("  Max:", np.max(lst[valid]), "K")

        print("\nLST uncertainty summary:")
        print("  Mean:", np.mean(unc[valid]), "K")
        print("  Min:", np.min(unc[valid]), "K")
        print("  Max:", np.max(unc[valid]), "K")

        # Example quality mask: keep only pixels with no cloud-test bits set
        # and no exception flags.
        cloud_test_bits = 64 + 128 + 256 + 512  # gross, thin, medium, fog
        clear = (
            valid
            & ((cloud & cloud_test_bits) == 0)
            & (exception == 0)
        )
        print("\nClear-sky, no-exception pixels:", np.sum(clear))
        if np.sum(clear) > 0:
            print("  Mean LST:", np.mean(lst[clear]), "K")
            print("  Min/Max:", np.min(lst[clear]), "K", "/", np.max(lst[clear]), "K")

    geo_ds.close()
    lst_ds.close()
    flags_ds.close()


if __name__ == "__main__":
    main()
