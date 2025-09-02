#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 31 12:35:07 2025

@author: vivian
"""

import os
import numpy as np
from astropy.io import fits

def sort_fits_files(df, source_folder, ext, na, nan_threshold=0.1):
    """
    Preprocess FITS files by checking existence, NaN ratios, and shape.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with at least 'sourceType' and 'sourceName' columns.
    source_folder : str
        Path to the root directory containing subdirectories for each source type.
    ext : str
        Extension string to append to each sourceName (e.g. '_CORNISH_5GHz.fits').
    na: list
        List of allowed object types (filtering condition).
    nan_threshold : float, default=0.10 (10%)
        **Edge cutout detector.** If the fraction of NaNs in the image exceeds
        this threshold, the cutout is classified as an *edge-of-survey* image.
        Edge cutouts typically arise where survey tiles don’t fully cover the
        cutout window, leaving missing pixels recorded as NaNs.
   

    Returns
    -------
    results : dict
        Dictionary with categorized results:
            - 'names'       : valid square FITS file names
            - 'Obj_type'    : object types for valid square FITS
            - 'recta'       : rectangular FITS file names
            - 'recta_type'  : object types for rectangular FITS
            - 'Edge_Survey' : file names of fits flagged as edge (NaN ratio > threshold)
            - 'Edge_SuType' : matching source types for 'Edge_Survey'
    """

    names, Obj_type = [], []
    recta, recta_type = [], []
    Edge_Survey, Edge_SuType = [], []

    # Cache top-level directory
    source_dirs = set(os.listdir(source_folder))

    for i in range(len(df)):
        obj = df.sourceType[i]

        # ✅ Only process if the object type is in na
        if obj in na and obj in source_dirs:
            name = df.sourceName[i] + ext
            subdir_path = os.path.join(source_folder, obj)

            try:
                subdir_files = set(os.listdir(subdir_path))
            except FileNotFoundError:
                continue

            if name in subdir_files:
                file_path = os.path.join(subdir_path, name)

                try:
                    sh = fits.open(file_path, memmap=True)[0].data
                    nan_ratio = np.isnan(sh).sum() / sh.size

                    if nan_ratio <= nan_threshold:
                        Length, width = np.shape(sh)

                        if Length == width:
                            Obj_type.append(obj)
                            names.append(name)
                        else:
                            recta.append(name)
                            recta_type.append(obj)
                    else:
                        Edge_Survey.append(name)
                        Edge_SuType.append(obj)

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue

    return {
        "names": names,
        "Obj_type": Obj_type,
        "recta": recta,
        "recta_type": recta_type,
        "Edge_Survey": Edge_Survey,
        "Edge_SuType": Edge_SuType,
    }
