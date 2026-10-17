"""Outreach-capacity metrics (operational primary metric for later evaluation)."""

from __future__ import annotations

import math

import numpy as np


def capacity_recall(y_true, score, capacity_fraction: float, weights=None) -> dict:
    """Flag the top ceil(capacity_fraction * n) dyads by score; report capture.

    Ties are broken by original order (stable sort) so results are deterministic.
    Optional survey weights give weighted recall/precision; the number flagged
    is always a count of dyads, as outreach capacity is a count of contacts.
    Rows with missing outcome must be removed before calling.
    """
    y = np.asarray(y_true, dtype=float)
    s = np.asarray(score, dtype=float)
    w = np.ones_like(y) if weights is None else np.asarray(weights, dtype=float)
    if not (y.shape == s.shape == w.shape) or y.ndim != 1:
        raise ValueError("y_true, score and weights must be 1-D and equal length")
    if np.isnan(y).any() or np.isnan(s).any():
        raise ValueError("missing outcome or score; handle explicitly before scoring")
    if not set(np.unique(y)) <= {0.0, 1.0}:
        raise ValueError("y_true must be binary 0/1")
    if not 0 < capacity_fraction <= 1:
        raise ValueError("capacity_fraction must be in (0, 1]")
    k = math.ceil(capacity_fraction * len(y))
    order = np.argsort(-s, kind="stable")
    flagged = np.zeros(len(y), dtype=bool)
    flagged[order[:k]] = True
    positives = float((w * y).sum())
    captured = float((w * y * flagged).sum())
    return {
        "n": int(len(y)),
        "flagged": int(k),
        "captured_weighted": captured,
        "recall": captured / positives if positives else float("nan"),
        "precision": captured / float(w[flagged].sum()),
        "false_alarms_weighted": float((w * (1 - y) * flagged).sum()),
    }
