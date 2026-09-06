# MetOp-SG METimage True-Color Example

`metimage_true_color.py` reads a METimage Level-1B spectral-radiance product and combines the 668, 555, and 443 nm channels into a true-color image. It accepts either the EUMETSAT ZIP archive or its extracted NetCDF-4 file.

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

Download the **METimage Global Level 1B Spectral Radiance** collection (`EO:EUM:DAT:0464`) from the [EUMETSAT Data Store](https://data.eumetsat.int/). A free EUMETSAT account is required.

The manuscript uses this product:

```text
W_XX-EUMETSAT-Darmstadt,SAT,SGA1-VII-1B-RAD_C_EUMT_20260906070617_G_O_20260906050358_20260906050459_C_N_T__.zip
```

## Run

```bash
python3 metimage_true_color.py /path/to/W_XX-EUMETSAT-Darmstadt,SAT,SGA1-VII-1B-RAD_*.zip
```

Use `--output` to select the PNG path:

```bash
python3 metimage_true_color.py product.zip --output figures/metimage_true_color.png
```

The `netCDF4` package applies each channel's `scale_factor`, `add_offset`, and `_FillValue` automatically. The script applies a 1st-to-99.5th-percentile stretch and square-root gamma correction independently to the red, green, and blue radiance arrays. The result is an image-grid view rather than a projected map because this product stores geolocation on a coarser tie-point grid.
