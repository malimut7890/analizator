# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\tests\test_api_field_mapping.py
import pytest
from src.api.api_field_mapping import map_api_fields
from src.core.logging_config import setup_logging

@pytest.fixture
def setup_logging_fixture():
    setup_logging()

def test_map_api_fields_yfinance(setup_logging_fixture):
    """Testuje mapowanie pól z Yahoo Finance."""
    data = {
        "longName": "Apple Inc.",
        "sector": "Information Technology",
        "currentPrice": 150.0,
        "revenueGrowth": 0.2,
        "grossMargins": 0.4,
        "debtToEquity": 150.0,
        "ebitdaMargins": 0.3,
        "returnOnAssets": 0.15
    }
    result = map_api_fields("yfinance", data)
    assert result["nazwa"] == "Apple Inc."
    assert result["sektor"] == "Technology"
    assert result["cena"] == "150.00"
    assert result["revenue_growth"] == "20.00"
    assert result["gross_margin"] == "40.00"
    assert result["debt_equity"] == "1.50"
    assert result["ebitda_margin"] == "30.00"
    assert result["roic"] == "15.00"

def test_map_api_fields_alpha_vantage(setup_logging_fixture):
    """Testuje mapowanie pól z Alpha Vantage."""
    data = {
        "Name": "Apple Inc.",
        "Sector": "Information Technology",
        "Price": "150.00",
        "EBITDAMargin": "0.3",
        "ReturnOnCapitalEmployed": "0.15"
    }
    result = map_api_fields("Alpha Vantage", data)
    assert result["nazwa"] == "Apple Inc."
    assert result["sektor"] == "Technology"
    assert result["cena"] == "150.00"
    assert result["ebitda_margin"] == "30.00"
    assert result["roic"] == "15.00"

def test_map_api_fields_fmp(setup_logging_fixture):
    """Testuje mapowanie pól z FMP."""
    data = {
        "companyName": "Apple Inc.",
        "sector": "Information Technology",
        "price": 150.0,
        "ebitdaMargin": 0.3,
        "returnOnInvestedCapital": 0.15
    }
    result = map_api_fields("FMP", data)
    assert result["nazwa"] == "Apple Inc."
    assert result["sektor"] == "Technology"
    assert result["cena"] == "150.00"
    assert result["ebitda_margin"] == "30.00"
    assert result["roic"] == "15.00"

def test_map_api_fields_invalid_data(setup_logging_fixture):
    """Testuje mapowanie z nieprawidłowymi danymi."""
    data = {"invalid_field": "value"}
    result = map_api_fields("yfinance", data)
    assert result["nazwa"] is None
    assert result["sektor"] is None
    assert result["cena"] is None