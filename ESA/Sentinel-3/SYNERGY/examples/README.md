# Sentinel-3 SYNERGY VGP Python Example

`sentinel3_synergy_example.py` reads an unzipped Sentinel-3 SYNERGY Level-2
`SY_2_VGP` SAFE package and prints a summary of the aerosol optical
thickness (`ag.nc`) and VGT B0 top-of-atmosphere reflectance (`B0.nc`) files.

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

The example works with any Sentinel-3 SYNERGY `SY_2_VGP___` `.SEN3` package.
The file used for the manuscript is:

```text
S3A_SY_2_VGP____20260905T092449_20260905T100901_20260905T140636_2652_143_307______PS1_O_ST_003.SEN3.zip
```

Unzip it first:

```bash
unzip S3A_SY_2_VGP____*.SEN3.zip -d /path/to/data/
```

Public archives include:

- ESA Copernicus Data Space: <https://dataspace.copernicus.eu/>
- EUMETSAT Data Store: <https://data.eumetsat.int/>
- CREODIAS: <https://creodias.eu/>

## Run the example

```bash
python3 sentinel3_synergy_example.py /path/to/S3A_SY_2_VGP____*.SEN3
```

## What it does

The script opens the `.SEN3` directory, reads package-level metadata from
one of the NetCDF files, then summarises `ag.nc` (aerosol optical thickness
at 550 nm) and `B0.nc` (TOA reflectance for the VGT B0 channel). It applies
the `scale_factor` and `_FillValue` attributes and reports the count, mean,
minimum, and maximum of the valid pixels.
