#!/usr/bin/env python3
"""Shared deterministic ink-analysis helpers for `image2ppt page snap` and `image2ppt page diff`.

All functions operate on grayscale numpy arrays (float or uint8, 0..255).
"Ink" means the minority pixel class inside a local crop after Otsu
thresholding — dark text on a light background or light text on a dark
background are handled symmetrically.
"""

from __future__ import annotations

import numpy as np
from PIL import Image


# Minimum gray-level separation between the ink and background classes for a
# crop to be considered measurable. Below this the crop is likely a photo or
# gradient region where binarization is meaningless.
MIN_CLASS_SEPARATION = 25.0
# Ink must be a minority class: more than this fraction means the threshold
# split a texture, not text.
MAX_INK_FRACTION = 0.45
MIN_INK_PIXELS = 8


def load_gray(path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("L"), dtype=np.float32)


def load_rgb(path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)


def otsu_threshold(gray: np.ndarray) -> tuple[float, float]:
    """Return (threshold, class_separation) for a grayscale crop."""
    hist, _ = np.histogram(gray, bins=256, range=(0.0, 256.0))
    total = float(gray.size)
    if total == 0:
        return 127.5, 0.0
    levels = np.arange(256, dtype=np.float64)
    weight_bg = np.cumsum(hist).astype(np.float64)
    weight_fg = total - weight_bg
    sum_bg = np.cumsum(levels * hist)
    sum_all = sum_bg[-1]
    mean_bg = sum_bg / np.maximum(weight_bg, 1.0)
    mean_fg = (sum_all - sum_bg) / np.maximum(weight_fg, 1.0)
    between = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
    index = int(np.argmax(between))
    separation = abs(float(mean_fg[index]) - float(mean_bg[index]))
    if weight_bg[index] == 0 or weight_fg[index] == 0:
        separation = 0.0
    return float(index), separation


def crop_ink_mask(gray_crop: np.ndarray) -> dict:
    """Binarize a crop and return the ink mask plus reliability metadata.

    Returns dict with keys: mask (bool ndarray), polarity ("dark"|"light"),
    reliable (bool), separation (float), ink_fraction (float).
    """
    threshold, separation = otsu_threshold(gray_crop)
    dark = gray_crop <= threshold
    dark_fraction = float(dark.mean()) if dark.size else 0.0
    if dark_fraction <= 0.5:
        mask, polarity, fraction = dark, "dark", dark_fraction
    else:
        mask, polarity, fraction = ~dark, "light", 1.0 - dark_fraction
    reliable = (
        separation >= MIN_CLASS_SEPARATION
        and fraction <= MAX_INK_FRACTION
        and int(mask.sum()) >= MIN_INK_PIXELS
    )
    return {
        "mask": mask,
        "polarity": polarity,
        "reliable": reliable,
        "separation": separation,
        "ink_fraction": fraction,
    }


def _dilate(mask: np.ndarray) -> np.ndarray:
    out = mask.copy()
    out[1:, :] |= mask[:-1, :]
    out[:-1, :] |= mask[1:, :]
    out[:, 1:] |= mask[:, :-1]
    out[:, :-1] |= mask[:, 1:]
    return out


def despeckle(mask: np.ndarray) -> np.ndarray:
    """Drop ink pixels that have no 8-connected ink neighbor (binarization noise)."""
    if not mask.any():
        return mask
    padded = np.pad(mask, 1, mode="constant")
    neighbors = np.zeros_like(padded, dtype=np.uint8)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            neighbors += np.roll(np.roll(padded, dy, axis=0), dx, axis=1).astype(np.uint8)
    return mask & (neighbors[1:-1, 1:-1] > 0)


def remove_border_components(mask: np.ndarray) -> np.ndarray:
    """Remove ink components that touch the crop boundary.

    Structures crossing the crop edge (card borders, dividers, neighboring
    text) belong to objects outside the rough box and must not pollute the
    measured text bounds.
    """
    if not mask.any():
        return mask
    reach = np.zeros_like(mask)
    reach[0, :] = mask[0, :]
    reach[-1, :] = mask[-1, :]
    reach[:, 0] = mask[:, 0]
    reach[:, -1] = mask[:, -1]
    if not reach.any():
        return mask
    for _ in range(2 * max(mask.shape)):
        grown = _dilate(reach) & mask
        if np.array_equal(grown, reach):
            break
        reach = grown
    return mask & ~reach


def tight_bbox(mask: np.ndarray):
    """Return (x, y, w, h) of the ink bounding box, or None when empty."""
    if not mask.any():
        return None
    rows = np.flatnonzero(mask.any(axis=1))
    cols = np.flatnonzero(mask.any(axis=0))
    top, bottom = int(rows[0]), int(rows[-1])
    left, right = int(cols[0]), int(cols[-1])
    return (left, top, right - left + 1, bottom - top + 1)


def line_bands(mask: np.ndarray, min_ink_px: int = 2, merge_gap: int = 2) -> list[tuple[int, int]]:
    """Segment ink rows into text-line bands [(top, bottom_exclusive), ...].

    Bands separated by gaps of at most merge_gap rows are merged so
    antialiasing breaks do not split a line.
    """
    row_ink = mask.sum(axis=1)
    inky = row_ink >= min_ink_px
    bands: list[list[int]] = []
    start = None
    for y, on in enumerate(inky):
        if on and start is None:
            start = y
        elif not on and start is not None:
            bands.append([start, y])
            start = None
    if start is not None:
        bands.append([start, len(inky)])
    merged: list[list[int]] = []
    for band in bands:
        if merged and band[0] - merged[-1][1] <= merge_gap:
            merged[-1][1] = band[1]
        else:
            merged.append(band)
    return [(top, bottom) for top, bottom in merged if bottom - top >= 2]


def glyph_height_px(bands: list[tuple[int, int]]) -> float:
    if not bands:
        return 0.0
    return float(np.median([bottom - top for top, bottom in bands]))


# A band this thin next to a much taller band is a horizontal rule, divider,
# or underline — not a glyph row. Container borders running through a crop
# without touching its edges are the most common real-slide pollution.
RULE_BAND_MAX_PX = 4
RULE_BAND_RATIO = 0.35


def filter_rule_bands(bands: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Drop line-like bands so dividers do not skew the glyph median or bbox.

    Only fires when a clearly taller band exists; a crop whose text is itself
    tiny (all bands thin) is left untouched.
    """
    if len(bands) <= 1:
        return bands
    heights = [bottom - top for top, bottom in bands]
    tallest = max(heights)
    if tallest <= RULE_BAND_MAX_PX:
        return bands
    kept = [
        (top, bottom)
        for (top, bottom), height in zip(bands, heights)
        if not (height <= RULE_BAND_MAX_PX and height < RULE_BAND_RATIO * tallest)
    ]
    return kept or bands


def ink_centroid(mask: np.ndarray):
    """Return (cx, cy) of ink pixels, or None when empty."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return float(xs.mean()), float(ys.mean())


_CJK_RANGES = (
    (0x3000, 0x30FF),  # CJK punctuation, kana
    (0x4E00, 0x9FFF),  # CJK unified ideographs
    (0xFF00, 0xFFEF),  # full-width forms
)
_DESCENDER_CHARS = set("gjpqy")
_ASCENDER_CHARS = set("bdfhklt")


def contains_cjk(text: str) -> bool:
    return any(any(low <= ord(ch) <= high for low, high in _CJK_RANGES) for ch in text)


def glyph_em_ratio(text: str) -> float:
    """Estimated ratio of measured ink-band height to the font em size.

    These are calibration constants: CJK glyphs nearly fill the em box, Latin
    cap height is ~0.72 em, descenders extend the band to ~0.92 em, and
    lowercase-only words without ascenders sit near the x-height (~0.50 em).
    The deterministic builder's fit_text clamp and `page diff` absorb the
    residual error.
    """
    if not text:
        return 0.72
    if contains_cjk(text):
        return 0.95
    has_descender = any(ch in _DESCENDER_CHARS for ch in text)
    has_ascender = any(ch.isupper() or ch.isdigit() or ch in _ASCENDER_CHARS for ch in text)
    if has_descender and has_ascender:
        return 0.95
    if has_descender:
        return 0.78
    if has_ascender:
        return 0.72
    return 0.50


def segment_mask(mask: np.ndarray):
    """Bands → row restriction → bbox → glyph metrics for a cleaned ink mask.

    Returns None when no glyph bands remain.
    """
    if not mask.any():
        return None
    bands = filter_rule_bands(line_bands(mask))
    if not bands:
        return None
    row_selector = np.zeros(mask.shape[0], dtype=bool)
    for top, bottom in bands:
        row_selector[top:bottom] = True
    restricted = mask & row_selector[:, None]
    bbox = tight_bbox(restricted)
    if bbox is None:
        return None
    return {
        "mask": restricted,
        "bbox": bbox,
        "bands": bands,
        "glyph_height_px": glyph_height_px(bands),
        "line_count": len(bands),
    }


def keep_anchored_columns(mask: np.ndarray, anchor_left: int, anchor_right: int, glyph: float) -> np.ndarray:
    """Keep only column clusters that horizontally overlap the anchor range.

    Ink columns are clustered with a gap threshold of ~0.8 glyph heights:
    characters and word spaces within one text block sit closer than that,
    while neighboring elements (icons, page numbers, other blocks) are
    separated by wider gaps. The anchor is the worker's rough box — its
    placement is the semantic signal for which cluster is the target text.
    Clusters that never reach the anchor range are foreign objects pulled in
    by the crop margin or auto-expansion, and are dropped.
    """
    column_ink = mask.any(axis=0)
    columns = np.flatnonzero(column_ink)
    if columns.size == 0:
        return mask
    gap_limit = max(6, int(0.8 * glyph))
    clusters: list[tuple[int, int]] = []
    start = previous = int(columns[0])
    for column in columns[1:]:
        column = int(column)
        if column - previous > gap_limit:
            clusters.append((start, previous))
            start = column
        previous = column
    clusters.append((start, previous))
    kept = [cluster for cluster in clusters if cluster[1] >= anchor_left and cluster[0] <= anchor_right]
    if not kept:
        center = (anchor_left + anchor_right) / 2
        kept = [min(clusters, key=lambda cluster: abs((cluster[0] + cluster[1]) / 2 - center))]
    selector = np.zeros(mask.shape[1], dtype=bool)
    for start, end in kept:
        selector[start : end + 1] = True
    return mask & selector[None, :]


def measure_crop(gray_crop: np.ndarray, clean_border: bool = True) -> dict:
    """Full measurement for one crop: mask, bbox, bands, glyph height.

    Returns dict with keys: ok (bool), reason (str), mask, polarity,
    bbox (x, y, w, h in crop coordinates), bands, glyph_height_px,
    line_count, ink_fraction.
    """
    ink = crop_ink_mask(gray_crop)
    if not ink["reliable"]:
        return {"ok": False, "reason": "low-contrast", **ink, "bbox": None, "bands": [], "glyph_height_px": 0.0, "line_count": 0}
    mask = despeckle(ink["mask"])
    if clean_border:
        cleaned = remove_border_components(mask)
        # If border cleanup wiped almost everything, the text itself likely
        # touches the crop edge (rough box too tight); fall back to the
        # uncleaned mask rather than reporting an empty measurement.
        if int(cleaned.sum()) >= max(MIN_INK_PIXELS, int(0.1 * mask.sum())):
            mask = cleaned
    segmented = segment_mask(mask)
    if segmented is None:
        return {"ok": False, "reason": "no-ink", **ink, "mask": mask, "bbox": None, "bands": [], "glyph_height_px": 0.0, "line_count": 0}
    return {
        "ok": True,
        "reason": "",
        "polarity": ink["polarity"],
        "separation": ink["separation"],
        "ink_fraction": float(segmented["mask"].mean()),
        **segmented,
    }
