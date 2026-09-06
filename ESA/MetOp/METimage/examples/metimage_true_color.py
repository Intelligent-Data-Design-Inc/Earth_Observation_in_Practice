#!/usr/bin/env python3
"""Create a true-color image from a MetOp-SG METimage Level-1B product."""

import argparse
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import netCDF4
import numpy as np


def open_product(path: Path) -> netCDF4.Dataset:
    """Open a METimage NetCDF file or the EUMETSAT ZIP archive containing it."""
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.endswith(".nc")]
            if len(names) != 1:
                raise ValueError(f"Expected one NetCDF file in {path}, found {len(names)}")
            data = archive.read(names[0])
        return netCDF4.Dataset(names[0], memory=data)
    return netCDF4.Dataset(path)


def stretch(channel: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Apply a percentile stretch and gamma correction to one visible channel."""
    low, high = np.nanpercentile(channel[valid], (1, 99.5))
    scaled = np.clip((channel - low) / (high - low), 0, 1)
    return np.sqrt(scaled)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("product", type=Path, help="METimage Level-1B .nc or .zip product")
    parser.add_argument("--output", type=Path, default=Path("metimage_true_color.png"))
    args = parser.parse_args()

    with open_product(args.product) as dataset:
        measurements = dataset["data/measurement_data"]
        red = np.ma.filled(measurements["vii_668"][:], np.nan)
        green = np.ma.filled(measurements["vii_555"][:], np.nan)
        blue = np.ma.filled(measurements["vii_443"][:], np.nan)
        latitude = np.ma.filled(measurements["latitude"][:], np.nan)
        longitude = np.ma.filled(measurements["longitude"][:], np.nan)
        product_name = dataset.getncattr("product_name")
        sensing_start = dataset.getncattr("sensing_start_time_utc")

    valid = np.isfinite(red) & np.isfinite(green) & np.isfinite(blue)
    rgb = np.dstack((stretch(red, valid), stretch(green, valid), stretch(blue, valid)))
    rgb[~valid] = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.imshow(rgb, origin="upper")
    ax.set_title(f"MetOp-SG-A1 METimage true color, {sensing_start}")
    ax.set_xlabel("Across-track pixel")
    ax.set_ylabel("Along-track line")
    fig.tight_layout()
    fig.savefig(args.output, dpi=180)
    plt.close(fig)

    geo_valid = np.isfinite(latitude) & np.isfinite(longitude)
    print(f"Product: {product_name}")
    print(f"Image size: {red.shape[0]} lines x {red.shape[1]} pixels")
    print(f"Valid three-channel pixels: {valid.sum()} of {valid.size}")
    print(f"Tie-point latitude: {np.nanmin(latitude[geo_valid]):.3f} to {np.nanmax(latitude[geo_valid]):.3f} degrees north")
    print(f"Tie-point longitude: {np.nanmin(longitude[geo_valid]):.3f} to {np.nanmax(longitude[geo_valid]):.3f} degrees east")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
