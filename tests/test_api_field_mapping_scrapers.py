# ŚCIEŻKA: tests/test_api_field_mapping_scrapers.py
from src.api.api_field_mapping import map_api_fields


def test_scraper_mapping_shared_structure():
    src = {
        "name": "Acme Inc.",
        "sector": "Technology",
        "price": 123.4,
        "currentRatio": 1.5,
    }
    out_mw = map_api_fields("MarketWatch", src)
    out_inv = map_api_fields("Investing", src)

    assert out_mw == out_inv
    assert out_mw["nazwa"] == "Acme Inc."
    assert out_mw["current_ratio"] == 1.5
