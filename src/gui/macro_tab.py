# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\gui\macro_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.api.api_fetcher import fetch_data
from src.core.logging_config import setup_logging
import logging

# Inicjalizacja logowania
setup_logging()

class MacroTab:
    def __init__(self, parent, company_data):
        self.parent = parent
        self.company_data = company_data
        
        # Checkbutton do pobierania makro
        self.macro_check = tk.BooleanVar()
        self.check_button = ttk.Checkbutton(self.parent, text="Pobierz dane makro", variable=self.macro_check, command=self.toggle_macro)
        self.check_button.pack(pady=10)
        
        # Tabela dla danych makro
        self.macro_tree = ttk.Treeview(self.parent, columns=("Wskaźnik", "Wartość"), show="headings")
        self.macro_tree.heading("Wskaźnik", text="Wskaźnik")
        self.macro_tree.heading("Wartość", text="Wartość")
        self.macro_tree.pack(pady=10, fill="both", expand=True)
        
    def toggle_macro(self):
        if self.macro_check.get():
            try:
                # Pobierz makro z API jak FRED (przykładowe tickery makro)
                macro_tickers = ["GDP", "UNRATE"]  # Przykład: GDP, bezrobocie
                results, _ = fetch_data(macro_tickers, data_type="macro")
                for key, value in results.items():
                    self.macro_tree.insert("", tk.END, values=(key, value.get("value", "Brak")))
            except Exception as e:
                logging.error(f"Błąd pobierania makro: {str(e)}")
                messagebox.showerror("Błąd", "Nie udało się pobrać danych makro!")
        else:
            for item in self.macro_tree.get_children():
                self.macro_tree.delete(item)