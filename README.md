# Data Curation

**Requirements**

- Python **3.6+**
- `numpy`, `pandas`, `matplotlib`, `astropy`, `pickle`
  
**Expected data layout**
```
project/
├── Fitts/                 # root of FITS data
│   ├── <label_A>/        # e.g., sourceType "PN"
│   │   ├── <file>.fits
│   └── <label_B>/
├── CN2                    # CSV with at least: sourceType, sourceName
└── (code files + notebooks)
```
You’ll also need to include:
~~~
Ext    = ['_MIPS24_maic.fits', '_CORNISH_5GHz.fits', '_MIPS70_filt.fits']
Survey = ['MIPS24','CORNISH','MIPS70','GLIMPSE2','GLIMPSE3','UKIDDS']  # Channel names
# Channel is derived by the index of `ext_used` in Ext → Survey.
~~~
…and a whitelist of labels to include (example)
~~~
na = ['PN','Radio-Galaxy (Lobe)','UCHII','Radio-Star','Dark HII-Region',
      'Radio-Galaxy (Central Source)','Diffuse HII-Region','Galaxy','IR-Quiet']
~~~
---
**API Reference**

**Results dictionary (shared by all functions)**

Many functions below use a `results` dict with these keys:

- `names` / `Obj_type` – valid **square** FITS images (filename + label)

- `recta` / `recta_type` – valid **rectangular** FITS images

- `Edge_Survey` / `Edge_SuType` – **edge** cutouts (NaN ratio > threshold)

---
`sort_data.sort_fits_files(df, source_folder, ext, na, nan_threshold=0.1)`

Build the `results` index by checking file existence, NaN ratio, and shape (square vs rectangular). Edge cutouts are detected by NaN fraction > `nan_threshold`. Returns the `results` dict described above.

**Parameters**

`df: pandas.DataFrame` – must contain `sourceType` and `sourceName`.

`source_folder: str` – root folder containing one subfolder per `sourceType`.

`ext: str` – filename suffix to append to `sourceName` (e.g. `'_CORNISH_5GHz.fits'`).

`na: list` – whitelist of allowed `sourceType`.

`nan_threshold: float` (default `0.10`) – NaN fraction above which a cutout is flagged as edge.

**Returns**
```
{
  "names": [...], "Obj_type": [...],
  "recta": [...], "recta_type": [...],
  "Edge_Survey": [...], "Edge_SuType": [...]
}
```
---
`load_fits_data.get_result_path(base_path, results, category, index)`

Utility to construct the absolute filesystem path for a given `category` and `index`. Raises `IndexError` if `index` is out of range; `KeyError` if `results` is missing the needed keys.


**Parameters**

`base_path: str` – e.g. `SorceF`.

`results: dict` – as returned by `sort_fits_files`.

`category: {"names","recta","Edge_Survey"}`.

`index: int`.


**Returns**

`str` – absolute path to the FITS file.

---
`load_fits_data.load_fits_from_results(base_path, results, category, index=0, memmap=True, return_header=False, return_path=False)`

Open a FITS cutout selected by `category` + `index`. Builds the path internally and returns the primary HDU’s data (and optionally the header and/or path).

**Parameters**

`base_path: str`

`results: dict`

`category: {"names","recta","Edge_Survey"}`

`index: int` (default `0`)

`memmap: bool` (default `True`) – passed to `fits.open`

`return_header: bool` (default `False`)

`return_path: bool` (default `False`)

**Returns**

`If only data: numpy.ndarray` (your FITS data as-is).

If `return_header=True`: `(data, header)`

If `return_path=True`: `(data, path)`

If both True: `(data, header, path)`
```
from load_fits_data import load_fits_from_results
img, hdr, p = load_fits_from_results(SorceF, results, "names", 0,
                                     return_header=True, return_path=True)
```
---
`make_dataframe.build_data_table(base_path, results, ext_used, ext_list, survey_list, categories=None, return_type="dataframe", out_path=None, include_path=False, include_category=False, memmap=True, fill_nans=True)`

Create a **table of samples** as a Pandas DataFrame (or write it to a pickle) with columns:
`Channel`, `name`, `label`, `image` (and optionally `path`, `category`). By default it uses the  categories `["names","recta"]`. The `Channel` string is derived from `ext_used` via its index in `ext_list`→`survey_list`.

**Parameters**

`base_path: str` – root folder (`SorceF`).

`results: dict` – from `sort_fits_files`.

`ext_used: str` – one element from `ext_list` (e.g. `Ext[1]`).

`ext_list: list[str]` – e.g. `Ext`.

`survey_list: list[str]` – e.g. `Survey`.

`categories: list[str] or None` – None ⇒ `["names","recta"].` Provide `["names","recta","Edge_Survey"]` if you want to include edge rows.

`return_type: "dataframe" | "pickle"` (default `"dataframe"`).

`out_path: str or None` – required if `return_type="pickle"`.

`include_path: bool` – add a `path` column.

`include_category: bool` – add a `category` column.

`memmap: bool` – passed to FITS loader.

`fill_nans: bool` – **present in signature but not applied** in this file (images are loaded as-is).

Returns

DataFrame if `return_type="dataframe"`, otherwise writes a pickle and returns `out_path`.

Example (DataFrame)
```
from make_dataframe import build_data_table
df_clean = build_data_table(
    base_path=SorceF, results=results,
    ext_used=Ext[1], ext_list=Ext, survey_list=Survey,  # Channel = Survey[1]
    include_path=True, include_category=True            # optional extras
)  # defaults to names+recta
```
```
build_data_table(
    base_path=SorceF, results=results,
    ext_used=Ext[1], ext_list=Ext, survey_list=Survey,
    include_path=True, include_category=True,
    return_type="pickle", out_path="artifacts/CORNISH_clean.pkl"
)
```
Typical flow
```
from sort_data import sort_fits_files
from load_fits_data import load_fits_from_results
from make_dataframe import build_data_table

# 1) Index the dataset
results = sort_fits_files(df, SorceF, Ext[1], na, nan_threshold=0.10)  # builds categories dict
# -> results["names"], results["recta"], results["Edge_Survey"], etc.  :contentReference[oaicite:11]{index=11}

# 2) Build a clean DataFrame (Edge_Survey excluded by default)
df_clean = build_data_table(SorceF, results, Ext[1], Ext, Survey)      # DataFrame of rows
# columns: Channel, name, label, image [, path, category]              :contentReference[oaicite:12]{index=12}

# 3) Load any single cutout on demand
img = load_fits_from_results(SorceF, results, "Edge_Survey", index=2)  # raw FITS data
# supports return_header / return_path if needed                      :contentReference[oaicite:13]{index=13}

```
---
This project is licensed under the [CC BY-NC-SA 4.0 license](https://creativecommons.org/licenses/by-nc-sa/4.0/)

