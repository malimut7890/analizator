# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\src\gui\edit_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
from src.core.company_data import CompanyData
import logging
import pyperclip
from src.gui.indicator_calculator import calculate_indicator
import os
from src.core.utils import (
    load_sector_config,
    parse_number,
    format_large_int_grouped,
    format_float_for_editor,
)
from src.core.phase_classifier import classify_phase
from src.core.logging_config import setup_logging
from src.core.sector_mapping import normalize_sector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

setup_logging()


def get_sectors():
    try:
        sectors_dir = os.path.join("src", "core", "sectors")
        sectors = [
            f.replace(".json", "").title()
            for f in os.listdir(sectors_dir)
            if f.endswith(".json")
        ]
        return sorted(sectors)
    except Exception as e:
        logging.error(f"Błąd wczytywania sektorów: {str(e)}")
        return []


def get_phases(sector: str) -> list:
    try:
        sector_config = load_sector_config(sector)
        if sector_config and "indicators" in sector_config:
            return list(sector_config["indicators"].keys())
        return []
    except Exception as e:
        logging.error(f"Błąd wczytywania faz dla sektora {sector}: {str(e)}")
        return []


class EditWindow:
    def __init__(self, parent, company: dict, company_data: CompanyData, update_callback, update_plots_callback):
        self.parent = parent
        self.company = company.copy()
        self.company_data = company_data
        self.update_callback = update_callback
        self.update_plots_callback = update_plots_callback

        self.window = tk.Toplevel(parent)
        self.window.title(f"Edytuj dane: {company.get('ticker', 'Brak tickera')}")
        self.window.geometry("800x600+100+100")

        self.entries = {}
        self.labels = {}
        self.copy_buttons = {}
        self.manual_checkboxes = {}
        self.var_checkboxes = {}
        self.calc_buttons = {}
        self.tooltip = None
        self.history_window = None

        self.var_in_portfolio = tk.BooleanVar(value=company.get("is_in_portfolio", False))

        # Mapowanie kluczy GUI na klucze JSON i opis
        self.field_mapping = {
            "Company Name": {"json_key": "nazwa", "tooltip": "Pełna nazwa spółki (np. Apple Inc.)"},
            "Sector": {"json_key": "sektor", "tooltip": "Sektor działalności spółki (np. Technologia)"},
            "Phase": {"json_key": "faza", "tooltip": "Faza rozwoju spółki (np. Wzrost, Dojrzałość)"},
            "Price": {"json_key": "cena", "tooltip": "Aktualna cena akcji (w USD)"},
            "Price Target": {"json_key": "analyst_target_price", "tooltip": "Średnia cena docelowa według analityków (w USD)"},
            "PE Ratio": {"json_key": "pe_ratio", "tooltip": "Wskaźnik cena/zysk (Price/Earnings)"},
            "Forward PE": {"json_key": "forward_pe", "tooltip": "Przyszły wskaźnik cena/zysk (Forward Price/Earnings)"},
            "PEG Ratio": {"json_key": "peg_ratio", "tooltip": "Wskaźnik cena/zysk do wzrostu zysków (Price/Earnings to Growth)"},
            "Revenue Growth": {"json_key": "revenue_growth", "tooltip": "Roczny wzrost przychodów (liczba, bez %)"},
            "Gross Margin": {"json_key": "gross_margin", "tooltip": "Marża brutto (liczba, bez %)"},
            "Debt / Equity Ratio": {"json_key": "debt_equity", "tooltip": "Zadłużenie / Kapitał własny"},
            "Current Ratio": {"json_key": "current_ratio", "tooltip": "Aktywa bieżące / Zobowiązania bieżące"},
            "ROE": {"json_key": "roe", "tooltip": "Zwrot z kapitału własnego (liczba, bez %)"},
            "Free Cash Flow Margin": {"json_key": "free_cash_flow_margin", "tooltip": "FCF / Przychody (liczba, bez %)"},
            "EPS TTM": {"json_key": "eps_ttm", "tooltip": "Zysk na akcję za ostatnie 12 miesięcy"},
            "PB Ratio": {"json_key": "price_to_book_ratio", "tooltip": "Cena/Wartość księgowa"},
            "PS Ratio": {"json_key": "price_to_sales_ratio", "tooltip": "Cena/Przychody"},
            "Operating Margin": {"json_key": "operating_margin", "tooltip": "Zysk operacyjny / Przychody (liczba, bez %)"},
            "Profit Margin": {"json_key": "profit_margin", "tooltip": "Zysk netto / Przychody (liczba, bez %)"},
            "Quick Ratio": {"json_key": "quick_ratio", "tooltip": "Szybki wskaźnik płynności"},
            "Cash Ratio": {"json_key": "cash_ratio", "tooltip": "Gotówka/Zob. bieżące"},
            "Debt / FCF Ratio": {"json_key": "cash_flow_to_debt_ratio", "tooltip": "FCF / Dług"},
            "Analyst Consensus": {"json_key": "analyst_rating", "tooltip": "Średnia ocena analityków"},
            "Earnings Growth": {"json_key": "earnings_growth", "tooltip": "Roczny wzrost zysków (liczba, bez %)"},
            "EBITDA Margin": {"json_key": "ebitda_margin", "tooltip": "EBITDA / Przychody (liczba, bez %)"},
            "ROIC": {"json_key": "roic", "tooltip": "Zwrot z zainwestowanego kapitału (liczba, bez %)"},
            "User Growth": {"json_key": "user_growth", "tooltip": "Roczny wzrost liczby użytkowników (liczba)"},
            "Interest Coverage": {"json_key": "interest_coverage", "tooltip": "EBIT / Koszty odsetek"},
            "Net Debt / EBITDA": {"json_key": "net_debt_ebitda", "tooltip": "Dług netto / EBITDA"},
            "Inventory Turnover": {"json_key": "inventory_turnover", "tooltip": "Rotacja zapasów"},
            "Asset Turnover": {"json_key": "asset_turnover", "tooltip": "Rotacja aktywów"},
            "Operating Cash Flow": {"json_key": "operating_cash_flow", "tooltip": "Przepływy operacyjne (USD)"},
            "Free Cash Flow": {"json_key": "free_cash_flow", "tooltip": "FCF (USD)"},
            "FFO": {"json_key": "ffo", "tooltip": "Funds From Operations (USD)"},
            "LTV": {"json_key": "ltv", "tooltip": "Lifetime Value (USD)"},
            "Market Cap": {"json_key": "market_cap", "tooltip": "Kapitalizacja (USD)"},
            "Revenue": {"json_key": "revenue", "tooltip": "Roczne przychody (USD)"},
        }

        # Scrollable frame
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Checkbox "W portfelu"
        ttk.Checkbutton(scrollable_frame, text="W portfelu", variable=self.var_in_portfolio).grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w"
        )

        row = 1
        for field, field_info in self.field_mapping.items():
            json_key = field_info["json_key"]

            # Label
            label = ttk.Label(scrollable_frame, text=field)
            label.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            label.bind("<Button-1>", lambda e, f=field: self.show_indicator_history(f))
            self.labels[field] = label

            # Entry
            if field == "Sector":
                entry = ttk.Combobox(scrollable_frame, values=get_sectors(), width=27, state="normal")
                entry.bind("<<ComboboxSelected>>", self.update_field_colors)
            elif field == "Phase":
                sector = self.company.get("sektor", "")
                entry = ttk.Combobox(scrollable_frame, values=get_phases(sector), width=27, state="normal")
                entry.bind("<<ComboboxSelected>>", self.update_field_colors)
            else:
                entry = ttk.Entry(scrollable_frame, width=30)

            entry.grid(row=row, column=1, padx=5, pady=2)

            # Wyświetlanie WARTOŚCI – zgodnie z zasadami edytora (użytkownik ma „święty” format)
            raw_val = self.company.get(json_key, "")
            display_value = ""
            if raw_val not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                # Duże wartości → grupowane integre
                if json_key in ["market_cap", "revenue", "operating_cash_flow", "free_cash_flow", "ffo", "ltv"]:
                    display_value = format_large_int_grouped(raw_val)
                # wartości liczbowe „małe” → przecinek jako separator dziesiętny
                elif json_key not in ["nazwa", "sektor", "faza", "analyst_rating"]:
                    display_value = format_float_for_editor(raw_val, decimals=2)
                else:
                    display_value = str(raw_val)

            entry.delete(0, tk.END)
            entry.insert(0, display_value)
            self.entries[field] = entry

            # Checkbox 'Ręczne'
            self.var_checkboxes[field] = tk.BooleanVar(value=self.company.get(f"is_manual_{json_key}", False))
            self.manual_checkboxes[field] = ttk.Checkbutton(scrollable_frame, text="Ręczne", variable=self.var_checkboxes[field])
            self.manual_checkboxes[field].grid(row=row, column=2, padx=5, pady=2)

            # Przyciski 'Oblicz' – dla wskaźników numerycznych
            if field not in ["Company Name", "Sector", "Phase", "Price Target", "Analyst Consensus"]:
                self.calc_buttons[field] = ttk.Button(
                    scrollable_frame, text="Oblicz", command=lambda f=field: calculate_indicator(self.window, f, self.entries)
                )
                self.calc_buttons[field].grid(row=row, column=3, padx=5, pady=2)

            # Kopiuj – zgodnie z testami: kopiujemy NAZWĘ POLA
            self.copy_buttons[field] = ttk.Button(
                scrollable_frame, text="Kopiuj", command=lambda f=field: pyperclip.copy(f)
            )
            self.copy_buttons[field].grid(row=row, column=4, padx=5, pady=2)

            row += 1

        # Przyciski akcji
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=5, pady=10)
        ttk.Button(button_frame, text="Zapisz", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Wyczyść ręczne", command=self.clear_manual_flags).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Anuluj", command=self.window.destroy).pack(side="left", padx=5)

        self.update_field_colors(None)
        self.window.transient(parent)
        self.window.grab_set()
        self.load_geometry()

    def load_geometry(self):
        try:
            geometry_file = "edit_window_geometry.json"
            if not os.path.exists(geometry_file) or os.path.getsize(geometry_file) == 0:
                default_geometry = {"width": 800, "height": 600, "x": 100, "y": 100}
                with open(geometry_file, "w", encoding="utf-8") as f:
                    json.dump(default_geometry, f, indent=4)
                self.window.geometry(f"{default_geometry['width']}x{default_geometry['height']}+{default_geometry['x']}+{default_geometry['y']}")
                return
            with open(geometry_file, "r", encoding="utf-8") as f:
                geometry = json.load(f)
                self.window.geometry(f"{geometry['width']}x{geometry['height']}+{geometry['x']}+{geometry['y']}")
        except Exception as e:
            logging.error(f"Błąd wczytywania geometrii okna: {str(e)}")
            self.window.geometry("800x600+100+100")

    def save_geometry(self):
        try:
            geometry = self.window.geometry()
            width, height, x, y = map(int, geometry.replace("x", "+").split("+"))
            geometry_data = {"width": width, "height": height, "x": x, "y": y}
            with open("edit_window_geometry.json", "w", encoding="utf-8") as f:
                json.dump(geometry_data, f, indent=4)
        except Exception as e:
            logging.error(f"Błąd zapisywania geometrii okna: {str(e)}")

    def update_field_colors(self, event):
        try:
            sector = self.entries["Sector"].get().strip()
            normalized_sector = normalize_sector(sector) if sector else None
            valid_sectors = {
                f.replace(".json", "").lower()
                for f in os.listdir(os.path.join("src", "core", "sectors"))
                if f.endswith(".json")
            }
            if normalized_sector and normalized_sector.lower() not in valid_sectors:
                normalized_sector = None

            temp_company = self.company.copy()
            temp_company["sektor"] = normalized_sector
            faza = self.entries["Phase"].get().strip() if self.var_checkboxes["Phase"].get() else (
                classify_phase(normalized_sector, temp_company) if normalized_sector else None
            )
            if faza and not self.var_checkboxes["Phase"].get():
                self.entries["Phase"].delete(0, tk.END)
                self.entries["Phase"].insert(0, faza)
        except Exception as e:
            logging.error(f"Błąd podczas aktualizacji kolorów pól: {str(e)}")

    def show_indicator_history(self, field: str):
        try:
            json_key = self.field_mapping[field]["json_key"]
            history = self.company_data.load_company_history(self.company["ticker"])
            if not history:
                messagebox.showwarning("Brak danych", f"Brak danych historycznych dla {field}")
                return
            if self.history_window:
                self.history_window.destroy()
            self.history_window = tk.Toplevel(self.window)
            self.history_window.title(f"Historia: {field} ({self.company['ticker']})")
            self.history_window.geometry("600x400")
            fig, ax = plt.subplots(figsize=(6, 4))
            dates = [entry["date"] for entry in history]
            values = []
            for entry in history:
                v = entry.get(json_key, None)
                try:
                    values.append(float(v) if v not in [None, "", "-", "NA", "N/A", "None", "nan"] else None)
                except Exception:
                    values.append(None)
            valid_dates, valid_values = [], []
            for d, v in zip(dates, values):
                if v is not None:
                    valid_dates.append(d)
                    valid_values.append(v)
            if not valid_values:
                messagebox.showwarning("Brak danych", f"Brak ważnych danych historycznych dla {field}")
                self.history_window.destroy()
                return
            ax.plot(valid_dates, valid_values, marker="o", label=field)
            ax.set_title(f"Historia: {field} ({self.company['ticker']})")
            ax.set_xlabel("Data")
            ax.set_ylabel(field)
            ax.legend()
            ax.tick_params(axis="x", rotation=45)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.history_window)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()
        except Exception as e:
            logging.error(f"Błąd podczas wyświetlania historii dla {field}: {str(e)}")
            messagebox.showerror("Błąd", f"Nie udało się wyświetlić historii dla {field}")

    def clear_manual_flags(self):
        try:
            for field, field_info in self.field_mapping.items():
                self.var_checkboxes[field].set(False)
        except Exception as e:
            logging.error(f"Błąd podczas czyszczenia flag 'Ręczne' dla {self.company['ticker']}: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się wyczyścić flag 'Ręczne'!")

    def save_data(self):
        """
        Zasady:
        - To co wpisujesz w okienku edycji jest święte (nie zmieniamy nazwy wskaźników ani formatu wejścia).
        - Zapisy do JSON mogą być w formacie liczbowym standaryzowanym (string z kropką dziesiętną), by kalkulacje były spójne.
        """
        try:
            numeric_fields = [
                "Price", "Price Target", "PE Ratio", "Forward PE", "PEG Ratio",
                "Revenue Growth", "Gross Margin", "Debt / Equity Ratio",
                "Current Ratio", "ROE", "Free Cash Flow Margin", "EPS TTM",
                "PB Ratio", "PS Ratio", "Operating Margin", "Profit Margin",
                "Quick Ratio", "Cash Ratio", "Debt / FCF Ratio",
                "Earnings Growth", "EBITDA Margin", "ROIC", "User Growth",
                "Interest Coverage", "Net Debt / EBITDA", "Inventory Turnover",
                "Asset Turnover"
            ]
            large_numeric_fields = [
                "Market Cap", "Revenue", "Operating Cash Flow", "Free Cash Flow", "FFO", "LTV"
            ]
            text_fields = ["Company Name", "Sector", "Phase", "Analyst Consensus"]

            for field, field_info in self.field_mapping.items():
                json_key = field_info["json_key"]
                entry_widget = self.entries.get(field)
                if entry_widget is None:
                    logging.debug(f"Pominięto brakujące pole edytora: {field}")
                    self.company[json_key] = self.company.get(json_key, None)
                    self.company[f"is_manual_{json_key}"] = self.company.get(f"is_manual_{json_key}", False)
                    continue

                raw_value = entry_widget.get().strip()
                is_manual = self.var_checkboxes.get(field).get() if self.var_checkboxes.get(field) else False

                if not raw_value or raw_value.lower() in ["none", "-", "na", "n/a", "--", "nan"]:
                    self.company[json_key] = None
                    self.company[f"is_manual_{json_key}"] = False
                    continue

                if field in text_fields:
                    processed_value = raw_value
                    if field == "Sector":
                        normalized = normalize_sector(raw_value)
                        valid = {
                            f.replace(".json", "").lower()
                            for f in os.listdir(os.path.join("src", "core", "sectors"))
                            if f.endswith(".json")
                        }
                        if normalized and normalized.lower() not in valid:
                            messagebox.showwarning("Ostrzeżenie", f"Sektor {raw_value} nie jest zdefiniowany, ustawiono None")
                            processed_value = None
                        else:
                            processed_value = normalized
                    self.company[json_key] = processed_value
                    self.company[f"is_manual_{json_key}"] = is_manual
                elif field in large_numeric_fields:
                    try:
                        num = parse_number(raw_value)
                        self.company[json_key] = f"{float(num):.2f}" if num is not None else None
                        self.company[f"is_manual_{json_key}"] = is_manual
                    except ValueError as e:
                        logging.error(f"Nieprawidłowa wartość dla {field}: '{raw_value}'")
                        messagebox.showerror("Błąd", f"Nieprawidłowa wartość dla {field}: {str(e)}")
                        return
                elif field in numeric_fields:
                    try:
                        num = parse_number(raw_value)
                        if json_key == "peg_ratio" and num is not None and num < 0:
                            messagebox.showwarning("Ostrzeżenie", f"Wartość PEG Ratio ({raw_value}) nie może być ujemna, ustawiono None")
                            self.company[json_key] = None
                            self.company[f"is_manual_{json_key}"] = False
                        else:
                            self.company[json_key] = f"{float(num):.2f}" if num is not None else None
                            self.company[f"is_manual_{json_key}"] = is_manual
                    except ValueError:
                        messagebox.showerror("Błąd", f"Nieprawidłowa wartość dla {field}: '{raw_value}' musi być liczbą")
                        return
                else:
                    logging.debug(f"Pominięto pole nieobsługiwane: {field}")

            self.company["is_in_portfolio"] = self.var_in_portfolio.get()
            self.company_data.save_company_data(self.company["ticker"], self.company)
            self.update_callback()
            self.update_plots_callback()
            self.window.destroy()
        except Exception as e:
            logging.error(
                f"Błąd podczas zapisywania danych w oknie edycji dla {self.company.get('ticker','?')}: {str(e)}",
                exc_info=True
            )
            messagebox.showerror("Błąd", f"Nie udało się zapisać danych: {str(e)}")
