# Sentinel-3 SLSTR L2 LST Example

`slstr_lst_example.py` reads a Sentinel-3 SLSTR Level-2 Land Surface
Temperature (`SL_2_LST____`) SAFE product and prints a summary of the nadir-view
LST data, coordinates, and quality flags.

## Dependencies

- Python 3
- `netCDF4`
- `numpy`

Install with:

```bash
pip install netCDF4 numpy
```

## Data

Download an `SL_2_LST____` granule from one of these sources:

- Copernicus Data Space Ecosystem: <https://dataspace.copernicus.eu/>
- EUMETSAT Data Store: <https://data.eumetsat.int/>

A free Copernicus / EUMETSAT account is required. The example accepts either the
extracted `.SEN3` directory or the original `.zip` file.

## Run

```bash
python3 slstr_lst_example.py /path/to/S3B_SL_2_LST____*.SEN3.zip
```

The script extracts the archive to `/tmp/slstr_extract` if a `.zip` is given,
reads `geodetic_in.nc`, `LST_in.nc`, and `flags_in.nc`, and reports the count of
valid LST pixels, geographic extent, LST statistics, and the number of pixels
that pass a strict clear-sky / no-exception mask.
