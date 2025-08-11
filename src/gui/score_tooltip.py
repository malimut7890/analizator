# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\src\gui\score_tooltip.py
from __future__ import annotations
import json, os
from typing import Optional
from src.core.revenue_trend_scoring import (
    compute_quarterly_revenue_trend_points,
    compute_yearly_revenue_trend_points,
)

def _load_latest_snapshot(path: str) -> Optional[dict]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            hist = json.load(f)
        return hist[-1] if isinstance(hist, list) and hist else None
    except Exception:
        return None

def build_score_tooltip_for_ticker(ticker: str, data_dir: str) -> str:
    path = os.path.join(data_dir, f"{ticker}.json")
    snap = _load_latest_snapshot(path)
    if not snap:
        return "Brak danych o przychodach – tooltip punktów za przychody niedostępny."

    q = compute_quarterly_revenue_trend_points(
        snap.get("quarterly_revenue") or snap.get("przychody_kwartalne") or []
    )
    y = compute_yearly_revenue_trend_points(
        snap.get("yearly_revenue") or snap.get("przychody_roczne") or []
    )

    def fmt_dir(ts):
        if ts.direction == "up": return f"wzrosty (seria {ts.streak})"
        if ts.direction == "down": return f"spadki (seria {ts.streak})"
        return "brak serii"

    q_text = f"Kwartalne: {q.points:+d} pkt, {fmt_dir(q)}" if q.periods_used >= 2 else "Kwartalne: brak danych"
    y_text = f"Roczne: {y.points:+d} pkt, {fmt_dir(y)}" if y.periods_used >= 2 else "Roczne: brak danych"
    return f"Trend przychodów — {q_text}; {y_text}"
