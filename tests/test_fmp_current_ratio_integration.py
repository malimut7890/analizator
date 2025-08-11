# ŚCIEŻKA: tests/test_fmp_current_ratio_integration.py
from src.api.api_field_mapping import map_api_fields


def test_fmp_current_ratio_is_mapped_when_source_uses_currentRatio():
    raw = {
        "companyName": "Apple Inc.",
        "sector": "Technology",
        "price": 150.0,
        "currentRatio": 1.23,  # tak zwraca FMP
    }
    out = map_api_fields("FMP", raw)
    assert out["nazwa"] == "Apple Inc."
    assert out["current_ratio"] == 1.23
