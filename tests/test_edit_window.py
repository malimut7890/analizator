# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\tests\test_edit_window.py
import pytest
from unittest.mock import Mock, patch
from src.gui.edit_window import EditWindow
from src.core.company_data import CompanyData
from src.core.logging_config import setup_logging
import pyperclip

@pytest.fixture
def setup_logging_fixture():
    setup_logging()

@pytest.fixture
def company_data():
    company = CompanyData()
    company.companies = [
        {
            "ticker": "TEST",
            "nazwa": "Test Company",
            "sektor": "Technology",
            "faza": "Wzrost",
            "cena": "100.00",
            "is_manual_cena": False,
            "indicator_color_cena": "black"
        }
    ]
    return company

@pytest.fixture
def edit_window(company_data):
    parent = Mock()
    company = company_data.get_company("TEST")
    update_callback = Mock()
    update_plots_callback = Mock()
    with patch("tkinter.Tk"), patch("tkinter.Toplevel"), patch("tkinter.ttk.Frame"), \
         patch("tkinter.ttk.Label"), patch("tkinter.ttk.Entry"), patch("tkinter.ttk.Combobox"), \
         patch("tkinter.ttk.Button"), patch("tkinter.ttk.Checkbutton"), patch("tkinter.BooleanVar") as mock_var:
        mock_var.return_value.get.side_effect = [False, False]  # is_in_portfolio, is_manual_faza
        window = EditWindow(parent, company, company_data, update_callback, update_plots_callback)
        window.entries = {
            "Price": Mock(get=lambda: "100.00"),
            "Sector": Mock(get=lambda: "Technology"),
            "Phase": Mock(get=lambda: "Wzrost"),
            "EBITDA Margin": Mock(get=lambda: "30.00")
        }
        window.var_checkboxes = {
            "Price": Mock(get=lambda: False),
            "Sector": Mock(get=lambda: False),
            "Phase": Mock(get=lambda: False),
            "EBITDA Margin": Mock(get=lambda: False)
        }
        window.copy_buttons = {"Price": Mock(), "EBITDA Margin": Mock()}
        return window

def test_copy_button_copies_field_name(setup_logging_fixture, edit_window):
    """Testuje, czy przycisk 'Kopiuj' kopiuje nazwę pola."""
    pyperclip.copy("")  # Wyczyść schowek
    edit_window.copy_buttons["EBITDA Margin"].invoke()
    assert pyperclip.paste() == "EBITDA Margin"

def test_save_data_valid(setup_logging_fixture, edit_window, company_data):
    """Testuje zapis poprawnych danych."""
    edit_window.entries["Price"].get = lambda: "150.00"
    edit_window.var_checkboxes["Price"].get = lambda: True
    with patch.object(company_data, "save_company_data") as mock_save:
        edit_window.save_data()
        mock_save.assert_called_once()
        assert company_data.get_company("TEST")["cena"] == "150.00"
        assert company_data.get_company("TEST")["is_manual_cena"] is True
        assert company_data.get_company("TEST")["indicator_color_cena"] == "black"

def test_save_data_invalid_numeric(setup_logging_fixture, edit_window, company_data):
    """Testuje zapis z nieprawidłową wartością liczbową."""
    edit_window.entries["Price"].get = lambda: "invalid"
    with patch("tkinter.messagebox.showerror") as mock_messagebox:
        edit_window.save_data()
        mock_messagebox.assert_called_with("Błąd", "Nieprawidłowa wartość dla Price: 'invalid' musi być liczbą")