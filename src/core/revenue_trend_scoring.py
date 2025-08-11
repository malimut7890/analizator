# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\src\core\revenue_trend_scoring.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple, Dict

# --- Punktacja streaków ---
QUARTERLY_PENALTIES = {1: -3, 2: -5, 3: -15, 4: -30}
QUARTERLY_BONUSES   = {1: +2, 2: +3, 3: +10, 4: +20}

# Roczne — aktywne punktowanie jak w kalkulatorze
YEARLY_PENALTIES = {1: -10, 2: -20, 3: -30, 4: -50}
YEARLY_BONUSES   = {1: +5,  2: +10, 3: +15, 4: +30}

@dataclass
class TrendScore:
    points: int
    direction: Optional[str]  # "up" | "down" | None
    streak: int
    deltas_used: List[float]
    periods_used: int

def _to_float(x) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(" ", "").replace("\u00A0", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None

def _parse_quarter(s: str) -> Optional[Tuple[int, int]]:
    if not s:
        return None
    s = s.strip().upper().replace(" ", "")
    try:
        if "-" in s:
            y, q = s.split("-", 1)
            y = int(y)
            q = int(q.replace("Q", ""))
            return (y, q) if 1 <= q <= 4 else None
        return (int(s), 0)
    except Exception:
        return None

def _parse_year(s: str) -> Optional[int]:
    try:
        return int(str(s).strip())
    except Exception:
        return None

def _sort_quarterly(data: Iterable[dict]) -> List[Tuple[int, int, float]]:
    out: List[Tuple[int, int, float]] = []
    for item in data or []:
        rev = _to_float(item.get("revenue"))
        parsed = _parse_quarter(str(item.get("date") or ""))
        if rev is not None and parsed is not None:
            y, q = parsed
            out.append((y, q, rev))
    out.sort(key=lambda t: (t[0], t[1]))
    return out

def _sort_yearly(data: Iterable[dict]) -> List[Tuple[int, float]]:
    out: List[Tuple[int, float]] = []
    for item in data or []:
        rev = _to_float(item.get("revenue"))
        y = _parse_year(str(item.get("date") or ""))
        if rev is not None and y is not None:
            out.append((y, rev))
    out.sort(key=lambda t: t[0])
    return out

def _build_deltas(values: List[float], max_lookback: int = 4) -> List[float]:
    if len(values) < 2:
        return []
    tail = values[-(max_lookback + 1):]
    return [tail[i + 1] - tail[i] for i in range(len(tail) - 1)]

def _streak_points_from_deltas(
    deltas: List[float],
    penalty_map: Dict[int, int],
    bonus_map: Dict[int, int],
) -> TrendScore:
    if not deltas:
        return TrendScore(0, None, 0, [], 0)

    last = deltas[-1]
    if last == 0:
        return TrendScore(0, None, 0, deltas, len(deltas) + 1)

    sign = 1 if last > 0 else -1
    direction = "up" if sign > 0 else "down"

    streak = 0
    for d in reversed(deltas):
        if d == 0:
            break
        if (d > 0 and sign > 0) or (d < 0 and sign < 0):
            streak += 1
        else:
            break

    streak = max(0, min(4, streak))
    if streak == 0:
        points = 0
        direction = None
    else:
        points = (bonus_map if direction == "up" else penalty_map)[streak]

    return TrendScore(points, direction, streak, deltas, len(deltas) + 1)

def compute_quarterly_revenue_trend_points(quarterly_revenue: Iterable[dict]) -> TrendScore:
    series = _sort_quarterly(quarterly_revenue)
    values = [rev for (_y, _q, rev) in series]
    deltas = _build_deltas(values, max_lookback=4)
    return _streak_points_from_deltas(deltas, QUARTERLY_PENALTIES, QUARTERLY_BONUSES)

def compute_yearly_revenue_trend_points(yearly_revenue: Iterable[dict]) -> TrendScore:
    # TERAZ: roczne też punktują wg kalkulatora
    series = _sort_yearly(yearly_revenue)
    values = [rev for (_y, rev) in series]
    deltas = _build_deltas(values, max_lookback=4)
    return _streak_points_from_deltas(deltas, YEARLY_PENALTIES, YEARLY_BONUSES)

def compute_total_revenue_trend_points(quarterly_revenue: Iterable[dict], yearly_revenue: Iterable[dict]) -> TrendScore:
    q = compute_quarterly_revenue_trend_points(quarterly_revenue)
    y = compute_yearly_revenue_trend_points(yearly_revenue)
    # Jeśli sumujesz do jednej metryki – możesz dodać q.points + y.points; tu zwracam kwartalne jako bazę:
    return TrendScore(q.points + y.points, q.direction, q.streak, q.deltas_used, q.periods_used)

def is_revenue_declining_quarterly(quarterly_revenue: Iterable[dict]) -> bool:
    t = compute_quarterly_revenue_trend_points(quarterly_revenue)
    return t.direction == "down" and t.streak >= 1

def is_revenue_growing_quarterly(quarterly_revenue: Iterable[dict]) -> bool:
    t = compute_quarterly_revenue_trend_points(quarterly_revenue)
    return t.direction == "up" and t.streak >= 1

def is_revenue_declining_yearly(yearly_revenue: Iterable[dict]) -> bool:
    t = compute_yearly_revenue_trend_points(yearly_revenue)
    return t.direction == "down" and t.streak >= 1

def is_revenue_growing_yearly(yearly_revenue: Iterable[dict]) -> bool:
    t = compute_yearly_revenue_trend_points(yearly_revenue)
    return t.direction == "up" and t.streak >= 1
