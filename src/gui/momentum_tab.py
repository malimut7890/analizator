# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\gui\momentum_tab.py
import tkinter as tk
from tkinter import ttk
import logging
from src.core.scoring_calculator import calculate_score
from src.core.logging_config import setup_logging

setup_logging()

class MomentumTab:
    def __init__(self, parent: ttk.Frame, company_data, update_table_callback):
        """
        Inicjalizuje zakładkę Momentum w GUI.
        Args:
            parent: Rodzic dla zakładki (ttk.Frame).
            company_data: Instancja CompanyData z danymi spółek.
            update_table_callback: Funkcja do aktualizacji tabeli w MainWindow.
        """
        self.parent = parent
        self.company_data = company_data
        self.update_table_callback = update_table_callback
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill="both", expand=True)

        ttk.Label(self.frame, text="Momentum Analysis").pack(pady=10)
        self.momentum_button = ttk.Button(self.frame, text="Oblicz Momentum", command=self.calculate_momentum)
        self.momentum_button.pack(pady=5)

    def calculate_momentum(self):
        """
        Oblicza momentum dla każdej spółki i aktualizuje punktację.
        """
        try:
            for company in self.company_data.companies:
                ticker = company["ticker"]
                sector = company.get("sektor")
                if not sector:
                    logging.warning(f"Brak sektora dla {ticker}, pomijam obliczanie momentum")
                    continue
                history = self.company_data.load_company_history(ticker)
                if len(history) < 2:
                    logging.warning(f"Za mało danych historycznych dla {ticker} do obliczenia momentum")
                    continue
                prices = [
                    float(entry.get("cena", 0) or 0)
                    if entry.get("cena") not in [None, "", "-", "NA", "N/A", "None", "nan"]
                    else 0
                    for entry in history
                ]
                if len(prices) >= 2 and prices[-2] != 0:
                    momentum = ((prices[-1] - prices[-2]) / prices[-2]) * 100
                    company["momentum"] = f"{momentum:.2f}"
                    logging.info(f"Obliczono momentum dla {ticker}: {momentum:.2f}%")
                    faza = company.get("faza")
                    if faza and faza != "None":
                        score_result = calculate_score(sector, faza, company, self.company_data)
                        if score_result:
                            score, _ = score_result
                            company["punkty"] = f"{score:.2f}"
                            self.company_data.save_company_data(ticker, company)
                        else:
                            logging.warning(f"Nie udało się przeliczyć punktacji dla {ticker}")
                else:
                    logging.warning(f"Brak wystarczających danych cenowych dla {ticker}")
            self.update_table_callback()
            logging.info("Zaktualizowano tabelę po obliczeniu momentum")
        except Exception as e:
            logging.error(f"Błąd podczas obliczania momentum: {str(e)}")