#!/usr/bin/env python3
"""Small numerical/layout safety helpers for Python publication figures."""

from __future__ import annotations

from typing import Any

import numpy as np


def interp_monotone(target: Any, xp: Any, fp: Any) -> Any:
    """Interpolate on a strictly monotone grid without silent direction errors.

    ``numpy.interp`` requires increasing ``xp``. This helper accepts a strictly
    increasing or decreasing grid, reverses decreasing ``xp`` and ``fp``
    together, and rejects duplicate/non-monotone coordinates.
    """
    xp_array = np.asarray(xp, dtype=float)
    fp_array = np.asarray(fp, dtype=float)
    if xp_array.ndim != 1 or fp_array.ndim != 1 or xp_array.size != fp_array.size:
        raise ValueError("xp and fp must be one-dimensional arrays of equal length")
    if xp_array.size < 2:
        raise ValueError("at least two interpolation points are required")
    if not np.all(np.isfinite(xp_array)) or not np.all(np.isfinite(fp_array)):
        raise ValueError("xp and fp must contain only finite values")
    differences = np.diff(xp_array)
    if np.all(differences > 0):
        ordered_xp, ordered_fp = xp_array, fp_array
    elif np.all(differences < 0):
        ordered_xp, ordered_fp = xp_array[::-1], fp_array[::-1]
    else:
        raise ValueError("xp must be strictly monotone; duplicates or direction changes are unsafe")
    return np.interp(target, ordered_xp, ordered_fp)


def label_y_above(values: Any, spread: Any | None = None, pad_fraction: float = 0.04) -> float:
    """Return a data-driven label y-position above values and optional spread."""
    centers = np.asarray(values, dtype=float)
    if centers.size == 0 or not np.all(np.isfinite(centers)):
        raise ValueError("values must contain at least one finite value")
    upper = centers if spread is None else centers + np.asarray(spread, dtype=float)
    if not np.all(np.isfinite(upper)):
        raise ValueError("spread must contain only finite values")
    data_min = float(np.min(centers))
    data_max = float(np.max(upper))
    scale = max(data_max - data_min, abs(data_max), 1.0)
    return data_max + max(0.0, pad_fraction) * scale


__all__ = ["interp_monotone", "label_y_above"]
