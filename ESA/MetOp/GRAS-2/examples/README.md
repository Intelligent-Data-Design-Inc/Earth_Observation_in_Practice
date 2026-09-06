# MetOp-SG GRAS-2 Bending-Angle Example

`gras2_bending_angle.py` reads a GRAS-2 Level-1B bending-angle product and plots the ionosphere-corrected neutral bending angle against impact height. It accepts either the EUMETSAT ZIP archive or its extracted NetCDF-4 file.

## Dependencies

- Python 3.10 or later
- `netCDF4`
- `numpy`
- `matplotlib`

Install them with:

```bash
python3 -m pip install -r requirements.txt
```

## Data

Download the **GRAS-2 Global Level 1B Bending Angle** collection (`EO:EUM:DAT:0452`) from the [EUMETSAT Data Store](https://data.eumetsat.int/). A free EUMETSAT account is required.

The manuscript uses this product:

```text
W_XX-EUMETSAT-Darmstadt,SAT,SGA1-RO_-1B-BND_C_EUMT_20260906100432_G_O_20260906081129_20260906081653_O_N_E09.zip
```

## Run

```bash
python3 gras2_bending_angle.py /path/to/W_XX-EUMETSAT-Darmstadt,SAT,SGA1-RO_-1B-BND_*.zip
```

Use `--output` to select the PNG path:

```bash
python3 gras2_bending_angle.py product.zip --output figures/gras2_bending_angle.png
```

The script opens the `data/occultation` and `data/level_1b/high_resolution` groups. It reads the occultation identity and location, converts `impact_height` from metres to kilometres, converts `bangle` and `bangle_sdev` from radians to microradians, and plots the positive bending-angle samples on a logarithmic horizontal axis.
