# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\tests\test_edit_window.py
import os
import json
import tkinter as tk
import types

import pytest

from src.core.company_data import CompanyData
from src.gui.edit_window import EditWindow


@pytest.fixture
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    try:
        root.destroy()
    except Exception:
        pass


def test_sector_raw_preserved_and_normalized_saved(tmp_path, tk_root, monkeypatch):
    # Przygotowanie CompanyData w katalogu tymczasowym
    cd = CompanyData()
    cd.data_dir = str(tmp_path)

    # Dodaj spółkę
    ticker = "EDITX"
    cd.add_company(ticker)
    company = {"ticker": ticker, "sektor": None}

    # Podmień messageboxy, żeby nie wyskakiwały okna
    monkeypatch.setattr("src.gui.edit_window.messagebox.showwarning", lambda *a, **k: None)
    monkeypatch.setattr("src.gui.edit_window.messagebox.showinfo", lambda *a, **k: None)
    monkeypatch.setattr("src.gui.edit_window.messagebox.showerror", lambda *a, **k: None)

    # Uprość get_phases, aby nie wymagał plików konfiguracyjnych
    monkeypatch.setattr("src.gui.edit_window.get_phases", lambda sector: ["Growth", "Mature"])

    # Otwórz edytor, wpisz niekanoniczny sektor oraz cenę w formacie "1,2"
    ew = EditWindow(tk_root, company, cd, update_callback=lambda: None, update_plots_callback=lambda: None)
    ew.entries["Sector"].delete(0, "end")
    ew.entries["Sector"].insert(0, " technology")  # leading space + różny case

    ew.entries["Price"].delete(0, "end")
    ew.entries["Price"].insert(0, "1,2")  # przecinek zamiast kropki

    # Zapisz
    ew.save_data()

    # Weryfikacja: w JSON sektor znormalizowany, a w cache zachowany surowy tekst
    file_path = os.path.join(cd.data_dir, f"{ticker}.json")
    with open(file_path, "r", encoding="utf-8") as f:
        hist = json.load(f)
    latest = hist[-1]

    assert latest["sektor"] == "Technology"  # znormalizowany zapis w JSON
    # Cena zapisana w JSON jako liczba z kropką i 2 miejscami
    assert latest["cena"] == "1.20"

    # Ponowne otwarcie edytora – w polu Sector i Price powinny być SUROWE wpisy
    ew2 = EditWindow(tk_root, latest, cd, update_callback=lambda: None, update_plots_callback=lambda: None)
    assert ew2.entries["Sector"].get() == " technology"
    assert ew2.entries["Price"].get() == "1,2"