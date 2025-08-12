# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\tests\test_momentum_tab.py
import pytest
import tkinter as tk
from tkinter import ttk
from unittest.mock import Mock
from src.gui.momentum_tab import MomentumTab
from src.core.company_data import CompanyData
from src.core.logging_config import setup_logging
from unittest.mock import patch


@pytest.fixture
def setup_logging_fixture():
    setup_logging()

@pytest.fixture
def company_data():
    company = CompanyData()
    company.companies = [
        {
            "ticker": "TEST",
            "sektor": "Technology",
            "faza": "Wzrost",
            "cena": "100.00",
            "punkty": "50.00"
        }
    ]
    return company

@pytest.fixture
def momentum_tab(company_data):
    root = tk.Tk()
    parent = ttk.Frame(root)
    update_table_callback = Mock()
    momentum_tab = MomentumTab(parent, company_data, update_table_callback)
    yield momentum_tab
    root.destroy()

def test_calculate_momentum_success(setup_logging_fixture, momentum_tab, company_data):
    """Testuje obliczanie momentum dla spółki z historią cen."""
    with patch.object(company_data, "load_company_history") as mock_history, \
         patch.object(company_data, "save_company_data") as mock_save:
        mock_history.return_value = [
            {"ticker": "TEST", "cena": "90.00", "date": "2025-08-01"},
            {"ticker": "TEST", "cena": "100.00", "date": "2025-08-02"}
        ]
        momentum_tab.calculate_momentum()
        assert company_data.companies[0]["momentum"] == "11.11"
        mock_save.assert_called_once()
        momentum_tab.update_table_callback.assert_called_once()

def test_calculate_momentum_no_history(setup_logging_fixture, momentum_tab, company_data):
    """Testuje obliczanie momentum dla spółki bez wystarczającej historii."""
    with patch.object(company_data, "load_company_history") as mock_history:
        mock_history.return_value = [{"ticker": "TEST", "cena": "100.00", "date": "2025-08-02"}]
        momentum_tab.calculate_momentum()
        assert "momentum" not in company_data.companies[0]
        momentum_tab.update_table_callback.assert_called_once()

def test_calculate_momentum_no_sector(setup_logging_fixture, momentum_tab, company_data):
    """Testuje obliczanie momentum dla spółki bez sektora."""
    company_data.companies[0]["sektor"] = None
    with patch.object(company_data, "load_company_history") as mock_history:
        mock_history.return_value = [
            {"ticker": "TEST", "cena": "90.00", "date": "2025-08-01"},
            {"ticker": "TEST", "cena": "100.00", "date": "2025-08-02"}
        ]
        momentum_tab.calculate_momentum()
        assert "momentum" not in company_data.companies[0]
        momentum_tab.update_table_callback.assert_called_once()