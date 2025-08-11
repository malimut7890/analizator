# ŚCIEŻKA: tests/test_api_field_mapping.py
import pytest

from src.api.api_field_mapping import map_api_fields


@pytest.fixture
def setup_logging_fixture():
    # placeholder (zostawiamy jak w repo — testy logowania są osobno)
    return None


def test_map_api_fields_yfinance(setup_logging_fixture):
    data = {
        "longName": "Apple Inc.",
        "sector": "Information Technology",
        "currentPrice": 150.0,
        "revenueGrowth": 0.2,
        "grossMargins": 0.4,
        "debtToEquity": 150.0,
        "ebitdaMargins": 0.3,
        "returnOnAssets": 0.15,
    }
    result = map_api_fields("yfinance", data)
    assert result["nazwa"] == "Apple Inc."
    # KLUCZOWA ZMIANA: zachowujemy odrębną nazwę sektora
    assert result["sektor"] == "Information Technology"


def test_map_api_fields_alpha_vantage(setup_logging_fixture):
    data = {
        "Name": "Apple Inc.",
        "Sector": "Information Technology",
        "Price": "150.00",
        "EBITDAMargin": "0.3",
        "ReturnOnCapitalEmployed": "0.15",
    }
    result = map_api_fields("Alpha Vantage", data)
    assert result["nazwa"] == "Apple Inc."
    assert result["sektor"] == "Information Technology"


def test_map_api_fields_fmp(setup_logging_fixture):
    data = {
        "companyName": "Apple Inc.",
        "sector": "Information Technology",
        "price": 150.0,
        "ebitdaMargin": 0.3,
        "returnOnInvestedCapital": 0.15,
        "currentRatio": 1.2,
    }
    result = map_api_fields("FMP", data)
    assert result["nazwa"] == "Apple Inc."
    assert result["sektor"] == "Information Technology"
    assert result["current_ratio"] == 1.2


def test_map_api_fields_invalid_data(setup_logging_fixture):
    data = {"invalid_field": "value"}
    result = map_api_fields("yfinance", data)
    # Zwracamy podstawowe klucze zawsze
    assert "nazwa" in result and result["nazwa"] is None
    assert "sektor" in result and result["sektor"] is None
    assert "cena" in result and result["cena"] is None
