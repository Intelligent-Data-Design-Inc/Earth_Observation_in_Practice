# Sentinel-5P TROPOMI Python Example

`sentinel5p_example.py` reads a Sentinel-5P TROPOMI Level-2 nitrogen-dioxide (NO2) NetCDF-4 file and prints a summary of the `nitrogendioxide_tropospheric_column` data in the `PRODUCT` group.

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

The example works with any Sentinel-5P TROPOMI Level-2 `L2__NO2___` NetCDF-4 product. The file used for the manuscript is:

```text
S5P_NRTI_L2__NO2____20260905T115116_20260905T115616_46096_03_020901_20260905T123301.nc
```

Public archives include:

- ESA Copernicus Data Space: <https://dataspace.copernicus.eu/>
- TROPOMI data products: <https://www.tropomi.eu/data-products/nitrogen-dioxide>

## Run the example

```bash
python3 sentinel5p_example.py /path/to/S5P_NRTI_L2__NO2____*.nc
```

## What it does

The script opens the file, locates the `PRODUCT` group, reads latitude, longitude, `qa_value`, and the `nitrogendioxide_tropospheric_column` geophysical variable, applies the `scale_factor` and `_FillValue` metadata, filters on `qa_value >= 0.5`, and reports the count, mean, minimum, and maximum of the valid NO2 tropospheric-column values.
