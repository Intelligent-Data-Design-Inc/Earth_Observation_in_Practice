# Sentinel-3 SRAL L2 Example

`sral_l2_example.py` reads a Sentinel-3 SRAL Level-2 measurement SAFE product
(`SR_2_WAT___`, `SR_2_LAN___`, or `SR_2_SI___` variants) and prints summary
statistics for the 20 Hz Ku-band geolocation, altimeter range, backscatter, and
1 Hz auxiliary variables.

## Dependencies

- Python 3
- `netCDF4`
- `numpy`

Install with:

```bash
pip install netCDF4 numpy
```

## Data

Download an `SR_2_*` granule from one of these sources:

- Copernicus Data Space Ecosystem: <https://dataspace.copernicus.eu/>
- EUMETSAT Data Store: <https://data.eumetsat.int/>

A free Copernicus / EUMETSAT account is required. The example accepts either the
extracted `.SEN3` directory or the original `.zip` file.

## Run

```bash
python3 sral_l2_example.py /path/to/S3A_SR_2_*.SEN3.zip
```

The script extracts the archive to `/tmp/sral_extract` if a `.zip` is given,
then reads `standard_measurement.nc` and reports the number of valid records,
geographic extent, surface-class counts, and key measurement summaries.
