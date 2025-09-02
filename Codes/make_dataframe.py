#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  1 22:29:46 2025

@author: vivian
"""

# samples.py  (Python 3.6+)
import os
import pickle
import numpy as np
import pandas as pd

# expects your existing loader:
from load_fits_data import load_fits_from_results

_RESULT_PAIRS = {
    "names": ("names", "Obj_type"),
    "recta": ("recta", "recta_type"),
    "Edge_Survey": ("Edge_Survey", "Edge_SuType"),
}

def _resolve_channel(ext_used, ext_list, survey_list):
    try:
        return survey_list[ext_list.index(ext_used)]
    except ValueError:
        return str(ext_used)  # fallback

def _save_pickle(obj, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

# -------------------------------------------------------------------
# 1) CLEAN SAMPLES ONLY (default): names + recta   (Edge_Survey excluded)
# -------------------------------------------------------------------
def build_data_table(
    base_path,
    results,
    ext_used,                 # e.g. Ext[1]
    ext_list,                 # e.g. Ext
    survey_list,              # e.g. Survey
    categories=None,          # None -> use both ['names','recta']; or pass a list
    return_type="dataframe",  # "dataframe" | "pickle"
    out_path=None,
    include_path=False,
    include_category=False,
    memmap=True,
    fill_nans=True,
):
    """
    Build rows with: Channel (survey), name, label, image [(+ path), (+ category)]
    DEFAULT: uses only clean categories ['names','recta'] (excludes 'Edge_Survey').
    """
    channel = _resolve_channel(ext_used, ext_list, survey_list)

    if categories is None:
        cats = ["names", "recta"]
    else:
        # ensure Edge_Survey is not silently included
        cats = [c for c in categories]

    rows = []
    for cat in cats:
        name_key, type_key = _RESULT_PAIRS[cat]
        names = results.get(name_key, []) or []
        labels = results.get(type_key, []) or []

        for i in range(min(len(names), len(labels))):
            img = load_fits_from_results(base_path, results, cat, index=i, memmap=memmap)

            row = {
                "Channel": channel,  # survey mapped from ext_used
                "name":    names[i], # filename
                "label":   labels[i],# sourceType
                "image":   img,      # 2D numpy array (native dtype)
            }
            if include_path:
                row["path"] = os.path.join(base_path, labels[i], names[i])
            if include_category:
                row["category"] = cat
            rows.append(row)

    df = pd.DataFrame(rows)

    if return_type == "dataframe":
        return df
    if return_type == "pickle":
        if not out_path:
            raise ValueError("out_path is required when return_type='pickle'")
        _save_pickle(df, out_path)
        return out_path
    raise ValueError("return_type must be 'dataframe' or 'pickle'")
