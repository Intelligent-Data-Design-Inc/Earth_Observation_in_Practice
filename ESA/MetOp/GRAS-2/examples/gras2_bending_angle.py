#!/usr/bin/env python3
"""Plot a MetOp-SG GRAS-2 Level-1B neutral bending-angle profile."""

import argparse
import io
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import netCDF4
import numpy as np


def open_product(path: Path) -> netCDF4.Dataset:
    """Open a GRAS-2 NetCDF file or the EUMETSAT ZIP archive containing it."""
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.endswith(".nc")]
            if len(names) != 1:
                raise ValueError(f"Expected one NetCDF file in {path}, found {len(names)}")
            data = archive.read(names[0])
        return netCDF4.Dataset(names[0], memory=data)
    return netCDF4.Dataset(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("product", type=Path, help="GRAS-2 Level-1B .nc or .zip product")
    parser.add_argument("--output", type=Path, default=Path("gras2_bending_angle.png"))
    args = parser.parse_args()

    with open_product(args.product) as dataset:
        occultation = dataset["data/occultation"]
        profile = dataset["data/level_1b/high_resolution"]
        height_km = np.ma.filled(profile["impact_height"][:] / 1000.0, np.nan)
        bending_urad = np.ma.filled(profile["bangle"][:] * 1.0e6, np.nan)
        uncertainty_urad = np.ma.filled(profile["bangle_sdev"][:] * 1.0e6, np.nan)
        latitude = float(occultation["latitude"][...])
        longitude = float(occultation["longitude"][...])
        gnss = str(occultation["gnss_system"][...])
        prn = str(occultation["occultation_prn"][...])
        event_type = str(occultation["occultation_type"][...])
        product_name = dataset.getncattr("product_name")

    valid = np.isfinite(height_km) & np.isfinite(bending_urad) & (bending_urad > 0)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.5, 8))
    ax.plot(bending_urad[valid], height_km[valid], color="tab:blue", linewidth=1.2)
    finite_uncertainty = valid & np.isfinite(uncertainty_urad)
    ax.fill_betweenx(
        height_km[finite_uncertainty],
        np.maximum(bending_urad[finite_uncertainty] - uncertainty_urad[finite_uncertainty], 1.0e-4),
        bending_urad[finite_uncertainty] + uncertainty_urad[finite_uncertainty],
        color="tab:blue",
        alpha=0.2,
        linewidth=0,
    )
    ax.set_xscale("log")
    ax.set_xlabel("Neutral bending angle (microradians)")
    ax.set_ylabel("Impact height above WGS 84 ellipsoid (km)")
    ax.set_title(f"MetOp-SG-A1 GRAS-2 {gnss} {prn} {event_type} occultation")
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(args.output, dpi=180)
    plt.close(fig)

    print(f"Product: {product_name}")
    print(f"Occultation: {gnss} {prn}, {event_type}")
    print(f"Reference location: {latitude:.3f} degrees north, {longitude:.3f} degrees east")
    print(f"Profile samples: {height_km.size}; plotted positive samples: {valid.sum()}")
    print(f"Impact-height range: {np.nanmin(height_km[valid]):.3f} to {np.nanmax(height_km[valid]):.3f} km")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
