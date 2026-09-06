# Sentinel-6 Poseidon-4 Python Example

`sentinel6_example.py` reads a Sentinel-6 Level-2 HR (high-resolution) altimetry NetCDF-4 file and prints a summary of the geophysical variables in the 1 Hz `data_01` group.

## Dependencies

- Python 3.10 or later
- `netCDF4` (Python bindings for netCDF-C; this also brings the NumPy dependency)

Install with pip:

```bash
python3 -m pip install netCDF4 numpy
```

The NetCDF-4/HDF5 runtime libraries must be available on the system. On the reference machine they are in `/usr/local/netcdf-c` and `/usr/local/hdf5-2.1.1`:

```bash
export LD_LIBRARY_PATH=/usr/local/netcdf-c/lib:/usr/local/hdf5-2.1.1/lib:$LD_LIBRARY_PATH
```

## Data source

The example works with any Sentinel-6 Poseidon-4 Level-2 HR NetCDF-4 measurement file. The file used for the manuscript is:

```text
S6A_P4_2__HR_STD__ST_214_110_20260903T230449_20260904T000102_G01.nc
```

Public archives include:

- EUMETSAT User Portal: <https://user.eumetsat.int/catalogue/>
- NASA PO.DAAC: <https://podaac.jpl.nasa.gov/Sentinel-6>
- ESA Copernicus Data Space: <https://dataspace.copernicus.eu/>

## Run the example

```bash
python3 sentinel6_example.py /path/to/S6A_P4_2__HR_*_*.nc
```

## What it does

The script opens the file, locates the `data_01` 1 Hz group and its `ku` subgroup, reads latitude, longitude, time, surface-classification flags, and the altimeter/radiometer geophysical variables (`ssha`, `swh_ocean`, `sig0_ocean`, `wind_speed_alt`, `range_ocean`), applies the `scale_factor` and `_FillValue` metadata, and reports statistics for records that are classified as open ocean with good quality flags.
