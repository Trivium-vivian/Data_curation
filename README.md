# Data Curation
**Expected data layout**
project/
├── Fitts/                 # root of FITS data
│   ├── <label_A>/        # e.g., sourceType "PN"
│   │   ├── <file>.fits
│   └── <label_B>/
├── CN2                    # CSV with at least: sourceType, sourceName
└── (code files + notebooks)

**Requirements**

- Python 3.6+
- numpy, pandas, matplotlib, astropy, pickle
