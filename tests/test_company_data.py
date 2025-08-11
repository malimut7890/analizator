# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\tests\test_company_data.py
import pytest
import os
import json
from unittest.mock import patch
from src.core.company_data import CompanyData
from src.core.logging_config import setup_logging

@pytest.fixture
def setup_logging_fixture():
    setup_logging()

@pytest.fixture
def company_data(tmp_path):
    """Tworzy tymczasowy folder data/ dla testów."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    company = CompanyData()
    original_data_dir = company.data_dir
    company.data_dir = str(data_dir)
    yield company
    company.data_dir = original_data_dir

def test_add_company_success(setup_logging_fixture, company_data, tmp_path):
    """Testuje dodawanie nowej spółki."""
    ticker = "TEST"
    company_data.add_company(ticker)
    assert any(c["ticker"] == ticker for c in company_data.companies)
    file_path = tmp_path / "data" / f"{ticker}.json"
    assert os.path.exists(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        history = json.load(f)
        assert len(history) == 1
        assert history[0]["ticker"] == ticker
        assert history[0]["nazwa"] is None
        assert history[0]["is_in_portfolio"] is False

def test_add_company_duplicate(setup_logging_fixture, company_data):
    """Testuje dodawanie zduplikowanej spółki."""
    ticker = "TEST"
    company_data.add_company(ticker)
    initial_count = len(company_data.companies)
    company_data.add_company(ticker)
    assert len(company_data.companies) == initial_count

def test_save_company_data(setup_logging_fixture, company_data, tmp_path):
    """Testuje zapis danych spółki."""
    ticker = "TEST"
    data = {
        "ticker": ticker,
        "nazwa": "Test Company",
        "sektor": "Technology",
        "cena": "100.00",
        "ebitda_margin": "30.00",
        "is_manual_ebitda_margin": True,
        "indicator_color_ebitda_margin": "blue"
    }
    company_data.save_company_data(ticker, data)
    file_path = tmp_path / "data" / f"{ticker}.json"
    assert os.path.exists(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        history = json.load(f)
        assert len(history) == 1
        assert history[0]["nazwa"] == "Test Company"
        assert history[0]["sektor"] == "Technology"
        assert history[0]["cena"] == "100.00"
        assert history[0]["ebitda_margin"] == "30.00"
        assert history[0]["is_manual_ebitda_margin"] is True
        assert history[0]["indicator_color_ebitda_margin"] == "blue"

def test_load_company_history(setup_logging_fixture, company_data, tmp_path):
    """Testuje wczytywanie historii spółki."""
    ticker = "TEST"
    data = {
        "ticker": ticker,
        "date": "2025-08-03",
        "nazwa": "Test Company",
        "sektor": "Technology",
        "cena": "100.00"
    }
    file_path = tmp_path / "data" / f"{ticker}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([data], f)
    history = company_data.load_company_history(ticker)
    assert len(history) == 1
    assert history[0]["ticker"] == ticker
    assert history[0]["nazwa"] == "Test Company"
    assert history[0]["sektor"] == "Technology"
    assert history[0]["cena"] == "100.00"

def test_delete_company(setup_logging_fixture, company_data, tmp_path):
    """Testuje usuwanie spółki."""
    ticker = "TEST"
    company_data.add_company(ticker)
    file_path = tmp_path / "data" / f"{ticker}.json"
    assert os.path.exists(file_path)
    company_data.delete_company(ticker)
    assert not any(c["ticker"] == ticker for c in company_data.companies)
    assert not os.path.exists(file_path)