#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 31 13:27:33 2025

@author: vivian
"""

import os
from astropy.io import fits

# Map each filename list to its paired "type" list
_RESULT_PAIRS = {
    "names": ("names", "Obj_type"),
    "recta": ("recta", "recta_type"),
    "Edge_Survey": ("Edge_Survey", "Edge_SuType"),
}

def _resolve_lists(results, category):
    if category not in _RESULT_PAIRS:
        raise KeyError(
            "Unknown category '{}'. Use one of: {}"
            .format(category, ", ".join(_RESULT_PAIRS.keys()))
        )
    name_key, type_key = _RESULT_PAIRS[category]
    if name_key not in results or type_key not in results:
        raise KeyError(
            "Results dict missing required keys '{}'/'{}' for category '{}'"
            .format(name_key, type_key, category)
        )
    return results[name_key], results[type_key]

def get_result_path(base_path, results, category, index):
    """
    Build absolute path for a given results category and index.
    """
    names_list, types_list = _resolve_lists(results, category)
    if not (0 <= index < len(names_list)):
        raise IndexError(
            "Index {} out of range for category '{}' (size={})"
            .format(index, category, len(names_list))
        )
    return os.path.join(base_path, types_list[index], names_list[index])

def load_fits_from_results(base_path, results, category, index=0,
                           memmap=True, return_header=False, return_path=False):
    """
    Load a FITS cutout by category and index from `results`.

    Parameters
    ----------
    base_path : str
        Root folder (e.g., SorceF).
    results : dict
        Output from preprocess_fits(...).
    category : {"names","recta","Edge_Survey"}
        Which list to index into.
    index : int, default 0
        Item index within the chosen category.
    memmap : bool, default True
        Passed to astropy.io.fits.open.
    return_header : bool, default False
        If True, also return the primary header.
    return_path : bool, default False
        If True, also return the file path used.

    Returns
    -------
    data  (and optionally header, path)
    """
    path = get_result_path(base_path, results, category, index)
    with fits.open(path, memmap=memmap) as hdul:
        data = hdul[0].data
        header = hdul[0].header if return_header else None

    if return_header and return_path:
        return data, header, path
    if return_header:
        return data, header
    if return_path:
        return data, path
    return data
