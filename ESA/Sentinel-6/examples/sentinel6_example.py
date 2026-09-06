#!/usr/bin/env python3
"""Read a Sentinel-6 Poseidon-4 Level-2 HR altimetry NetCDF-4 file.

The script opens the file with the standard netCDF4 Python API, applies the
scale_factor/add_offset attributes automatically, masks the _FillValue, and
prints a short summary of the sea-surface height, wave height, backscatter,
and wind-speed records that are flagged as valid open-ocean measurements.
"""

import argparse
import sys
from pathlib import Path

import netCDF4
import numpy as np


def read_var(group, name, as_flag=False):
    """Return a variable's data as a NumPy array.

    Geophysical variables are auto-scaled and any _FillValue is replaced by
    NaN. Flag variables are left as raw integers so equality tests work.
    """
    var = group[name]
    if as_flag:
        var.set_auto_maskandscale(False)
        return np.array(var[:])
    var.set_auto_maskandscale(True)
    data = var[:]
    return np.ma.filled(data, np.nan)


def main():
    parser = argparse.ArgumentParser(
        description="Summarise a Sentinel-6 L2 HR altimetry NetCDF-4 file."
    )
    parser.add_argument("file", type=Path, help="Path to the Sentinel-6 .nc file.")
    args = parser.parse_args()

    nc = netCDF4.Dataset(args.file, "r")
    print(f"File: {args.file}")
    print(f"Format: {nc.file_format}")
    print(f"Title: {nc.title}")
    print(f"Mission: {nc.mission_name}")
    print(f"Product: {nc.product_name}")
    print(f"Processing baseline: {nc.source}")
    print(f"Cycle / Pass: {nc.cycle_number} / {nc.pass_number}")
    print(f"First measurement: {nc.first_measurement_time}")
    print(f"Last measurement:  {nc.last_measurement_time}")
    print()

    # The 1 Hz data group holds geolocation, radiometer, and quality flags.
    g1 = nc.groups["data_01"]
    # The nested ku group holds the Ku-band altimeter geophysical variables.
    g1ku = g1.groups["ku"]

    print(f"data_01 time dimension: {g1.dimensions['time'].size}")
    if "time" in g1ku.dimensions:
        print(f"data_01/ku time dimension: {g1ku.dimensions['time'].size}")
    else:
        # Dimensions are inherited from the parent group.
        print(f"data_01/ku time dimension: {g1.dimensions['time'].size} (inherited)")

    # Read coordinate and time arrays.
    lat = read_var(g1, "latitude")
    lon = read_var(g1, "longitude")
    time = read_var(g1, "time")

    # Convert time to datetime objects for display.
    time_unit = g1["time"].units
    time_cal = getattr(g1["time"], "calendar", "standard")
    dates = netCDF4.num2date(time, units=time_unit, calendar=time_cal)

    # Read geophysical variables from the 1 Hz altimeter group.
    ssha = read_var(g1ku, "ssha")
    swh = read_var(g1ku, "swh_ocean")
    sig0 = read_var(g1ku, "sig0_ocean")
    wind = read_var(g1, "wind_speed_alt")
    range_ocean = read_var(g1ku, "range_ocean")

    # Read quality and surface-type flags.
    surface = read_var(g1, "surface_classification_flag", as_flag=True)
    range_qual = read_var(g1ku, "range_ocean_qual", as_flag=True)
    swh_qual = read_var(g1ku, "swh_ocean_qual", as_flag=True)
    sig0_qual = read_var(g1ku, "sig0_ocean_qual", as_flag=True)

    # Build an ocean/quality mask.
    # surface_classification_flag: 0 = open_ocean, 1 = land, 2 = continental_water, ...
    # *_qual flags: 0 = good, 1 = bad
    valid = (
        (surface == 0)
        & (range_qual == 0)
        & (swh_qual == 0)
        & (sig0_qual == 0)
        & np.isfinite(ssha)
        & np.isfinite(swh)
        & np.isfinite(sig0)
        & np.isfinite(wind)
    )

    n_total = len(lat)
    n_valid = int(np.sum(valid))
    print(f"\nTotal 1 Hz records: {n_total}")
    print(f"Open-ocean, good-quality records: {n_valid}")

    if n_valid == 0:
        print("No valid ocean records found.")
        return

    print(f"\nGeographic extent (all records):")
    print(f"  latitude: {lat.min():.4f} to {lat.max():.4f}")
    print(f"  longitude: {lon.min():.4f} to {lon.max():.4f}")
    print(f"  time: {dates[0]} to {dates[-1]}")

    print(f"\nValid open-ocean summary:")
    for label, arr, unit in [
        ("SSHA", ssha[valid], "m"),
        ("Significant wave height", swh[valid], "m"),
        ("Backscatter (sig0)", sig0[valid], "dB"),
        ("Wind speed", wind[valid], "m/s"),
        ("Range", range_ocean[valid], "m"),
    ]:
        print(
            f"  {label}: count={arr.size}, mean={arr.mean():.4f} {unit}, "
            f"min={arr.min():.4f} {unit}, max={arr.max():.4f} {unit}"
        )

    nc.close()


if __name__ == "__main__":
    main()
