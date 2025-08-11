from typing import List, Dict, Tuple

def _clean_series(items: List[Dict]) -> List[Tuple[str, float]]:
    out = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        d = it.get("date")
        rv = it.get("revenue")
        if d is None or rv in (None, "", "-", "NA", "N/A", "None", "nan"):
            continue
        try:
            out.append((d, float(rv)))
        except Exception:
            pass
    out.sort(key=lambda x: x[0])  # YYYY-.. / YYYYQ.. sortuje się leksykograficznie OK
    return out

def quarterly_points(quarterly_revenue: List[Dict]) -> int:
    series = _clean_series(quarterly_revenue)
    if len(series) < 3:
        return 0
    last = series[-5:]  # max 4 zmiany
    ups = 0
    for i in range(1, len(last)):
        if last[i][1] > last[i-1][1]:
            ups += 1
    if ups >= 3:
        return 2
    if ups == 2:
        return 1
    return 0

def yearly_points(yearly_revenue: List[Dict]) -> int:
    series = _clean_series(yearly_revenue)
    if len(series) < 2:
        return 0
    first = series[0][1]
    last = series[-1][1]
    if first <= 0:
        return 0
    try:
        n_years = max(1, int(series[-1][0][:4]) - int(series[0][0][:4]))
    except Exception:
        n_years = max(1, len(series) - 1)
    try:
        cagr = (last / first) ** (1 / n_years) - 1
    except Exception:
        return 0
    cagr_pct = cagr * 100.0
    if cagr_pct > 15.0:
        return 3
    if cagr_pct > 5.0:
        return 2
    if cagr_pct >= 0.0:
        return 1
    return 0

def revenue_points(quarterly_revenue: List[Dict], yearly_revenue: List[Dict]) -> Dict[str, int]:
    return {
        "punkty_quarterly_revenue": quarterly_points(quarterly_revenue),
        "punkty_yearly_revenue": yearly_points(yearly_revenue),
    }
