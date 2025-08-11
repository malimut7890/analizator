# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\gui\main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.gui.edit_window import EditWindow
from src.gui.momentum_tab import MomentumTab
from src.gui.macro_tab import MacroTab
from src.gui.settings_tab import SettingsTab
from src.core.company_data import CompanyData
from src.core.phase_classifier import classify_phase
from src.core.scoring_calculator import calculate_score
from src.core.utils import load_sector_config, format_number, parse_number
from src.core.sector_mapping import normalize_sector
import logging
import json
import os
from typing import Optional, Dict, List, Tuple
from src.core.logging_config import setup_logging
from datetime import datetime
import re

setup_logging()


class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        """
        Inicjalizuje główne okno aplikacji.
        Args:
            root: Główny obiekt Tkinter.
        """
        self.root = root
        self.root.title("Analizator Spółek Giełdowych")
        self.company_data = CompanyData()

        self.column_widths_file = "column_widths.json"
        self.col_to_json = {
            "price_target": "analyst_target_price",
            "analyst_consensus": "analyst_rating",
            "debt_fcf_ratio": "cash_flow_to_debt_ratio",
            "pb_ratio": "price_to_book_ratio",
            "ps_ratio": "price_to_sales_ratio",
            "ebitda_margin": "ebitda_margin",
            "roic": "roic",
            "user_growth": "user_growth",
            "interest_coverage": "interest_coverage",
            "net_debt_ebitda": "net_debt_ebitda",
            "inventory_turnover": "inventory_turnover",
            "asset_turnover": "asset_turnover",
            "operating_cash_flow": "operating_cash_flow",
            "free_cash_flow": "free_cash_flow",
            "ffo": "ffo",
            "ltv": "ltv",
            "rnd_sales": "rnd_sales",
            "cac_ltv": "cac_ltv"
        }

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Główna")

        self.ticker_entry = ttk.Entry(self.main_frame, width=50)
        self.ticker_entry.pack(pady=10)

        self.add_button = ttk.Button(self.main_frame, text="Dodaj", command=self.add_tickers)
        self.add_button.pack(pady=5)

        # DODANE: kolumny na punkty za przychody kwartalne/roczne
        self.columns = (
            "ticker",
            "nazwa",
            "sektor",
            "faza",
            "punkty",
            "pkt_przych_kw",
            "pkt_przych_roczne",
            "więcej",
        )

        self.tree = ttk.Treeview(self.main_frame, columns=self.columns, show="headings", selectmode="extended")
        for col in self.columns:
            if col == "faza":
                self.tree.heading(col, text="Faza")
            elif col == "punkty":
                self.tree.heading(col, text="Punkty")
            elif col == "pkt_przych_kw":
                self.tree.heading(col, text="Pkt. przych. (Q)")
            elif col == "pkt_przych_roczne":
                self.tree.heading(col, text="Pkt. przych. (Y)")
            elif col == "więcej":
                self.tree.heading(col, text="Więcej")
            else:
                self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=120 if col in ("pkt_przych_kw", "pkt_przych_roczne") else 100,
                             anchor="center", stretch=tk.YES)

        self.tree.pack(pady=10, padx=10, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Motion>", self.on_tree_motion)
        self.tree.bind("<Leave>", self.hide_tooltip)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        style = ttk.Style()
        style.configure("Treeview", background="white", fieldbackground="white")
        style.configure("red_row.Treeview", background="red")
        style.configure("orange_row.Treeview", background="orange")
        style.configure("green_row.Treeview", background="lightgreen")

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=5)

        self.edit_button = ttk.Button(button_frame, text="Edytuj dane", command=self.open_edit_window)
        self.edit_button.pack(side="left", padx=5)

        self.fetch_button = ttk.Button(button_frame, text="Pobierz dane", command=self.fetch_data)
        self.fetch_button.pack(side="left", padx=5)

        self.delete_button = ttk.Button(button_frame, text="Usuń", command=self.delete_company)
        self.delete_button.pack(side="left", padx=5)

        self.show_price_plot_button = ttk.Button(button_frame, text="Pokaż wykres cenowy",
                                                 command=self.show_price_plot_window, style="Blue.TButton")
        self.show_price_plot_button.pack(side="left", padx=5)

        self.show_score_plot_button = ttk.Button(button_frame, text="Pokaż punkty",
                                                 command=self.show_score_plot_window, style="Blue.TButton")
        self.show_score_plot_button.pack(side="left", padx=5)

        # ZOSTAWIAMY stare „Dane finansowe” (wykresy linii wskaźników historycznych)
        self.show_financial_button = ttk.Button(button_frame, text="Dane finansowe",
                                                command=self.show_financial_plots, style="Blue.TButton")
        self.show_financial_button.pack(side="left", padx=5)

        # NOWY przycisk: słupki przychodów kwart./rocznych
        self.show_revenue_bars_button = ttk.Button(button_frame, text="Przychody (słupki)",
                                                   command=self.show_revenue_bars, style="Blue.TButton")
        self.show_revenue_bars_button.pack(side="left", padx=5)

        style.configure("Blue.TButton", background="#0000CD", foreground="black", font=("Arial", 10))

        # Zakładka "Dane finansowe" (formularze)
        self.financial_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.financial_frame, text="Dane finansowe")

        self.ticker_combobox = ttk.Combobox(self.financial_frame, state="readonly")
        self.ticker_combobox.pack(pady=10)
        self.ticker_combobox.bind("<<ComboboxSelected>>", self.on_ticker_select)

        self.financial_inputs = {}
        financial_fields = [
            "revenue", "market_cap", "free_cash_flow_margin", "roe",
            "debt_equity", "profit_margin", "cash_ratio"
        ]
        for field in financial_fields:
            frame = ttk.Frame(self.financial_frame)
            frame.pack(fill="x", padx=5, pady=2)
            ttk.Label(frame, text=field.replace("_", " ").title()).pack(side="left")
            entry = ttk.Entry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.financial_inputs[field] = entry

        self.save_financial_button = ttk.Button(self.financial_frame, text="Zapisz dane",
                                                command=self.save_financial_data)
        self.save_financial_button.pack(pady=10)

        self.fig: Optional[plt.Figure] = None
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.current_ticker: Optional[str] = None
        self.tooltip: Optional[tk.Toplevel] = None
        self.price_plot_window: Optional[tk.Toplevel] = None
        self.score_plot_window: Optional[tk.Toplevel] = None
        self.financial_plot_window: Optional[tk.Toplevel] = None
        self.revenue_plot_window: Optional[tk.Toplevel] = None
        self.details_window: Optional[tk.Toplevel] = None
        self.tooltips: Dict[str, Dict[str, str]] = {}

        self.load_column_widths()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Pozostałe zakładki
        self.momentum_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.momentum_frame, text="Momentum")
        self.momentum_tab = MomentumTab(self.momentum_frame, self.company_data, self)

        self.macro_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.macro_frame, text="Macro")
        self.macro_tab = MacroTab(self.macro_frame, self.company_data)

        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Ustawienia")
        self.settings_tab = SettingsTab(self.settings_frame)

        self.update_table()

    # ---------- Pomocnicze do punktów przychodowych ----------

    @staticmethod
    def _safe_float(val) -> Optional[float]:
        if val in [None, "", "-", "NA", "N/A", "None", "nan"]:
            return None
        try:
            # parse_number rozumie przecinki/kropki; jeśli nie, fallback na float
            return float(parse_number(val)) if isinstance(val, str) else float(val)
        except Exception:
            try:
                return float(str(val).replace(",", "."))
            except Exception:
                return None

    @staticmethod
    def _parse_quarter_key(key: str) -> Optional[Tuple[int, int]]:
        """
        Oczekuje formatu 'YYYY-Q1'..'YYYY-Q4'. Zwraca (rok, nr_kwartału).
        """
        try:
            m = re.match(r"^(\d{4})-Q([1-4])$", key.strip())
            if not m:
                return None
            return int(m.group(1)), int(m.group(2))
        except Exception:
            return None

    def _compute_quarterly_revenue_points(self, company: dict) -> Tuple[Optional[float], str]:
        """
        Liczy punkty na bazie sumy ostatnich 4 kwartałów vs poprzednie 4 (prosty % wzrostu),
        następnie skaluje do zakresu punktów (0..max). Zwraca (punkty, opis do tooltipa).
        """
        q = company.get("quarterly_revenue") or []
        # mapa { "YYYY-Qn": value }
        series = {}
        for item in q:
            date_key = str(item.get("date") or "").strip()
            val = self._safe_float(item.get("revenue"))
            if not date_key or val is None:
                continue
            if self._parse_quarter_key(date_key) is None:
                # pomiń niepoprawne wpisy
                continue
            series[date_key] = val

        if len(series) < 8:
            return None, "Za mało danych: potrzeba min. 8 kwartałów (4+4)."

        # posortowane po (rok, kwartal)
        sorted_keys = sorted(series.keys(), key=lambda k: self._parse_quarter_key(k))
        last4 = sorted_keys[-4:]
        prev4 = sorted_keys[-8:-4]

        sum_last4 = sum(series[k] for k in last4)
        sum_prev4 = sum(series[k] for k in prev4)

        if sum_prev4 == 0:
            return None, "Poprzednie 4 kwartały sumują się do 0 – brak możliwości policzenia dynamiki."

        growth = (sum_last4 - sum_prev4) / sum_prev4  # np. 0.25 = +25%
        # Skala punktowa – możesz zgrać z kalkulatorem; na razie sensowny clamp:
        # +50% lub więcej = 10 pkt, 0% = 5 pkt, -50% lub mniej = 0 pkt (liniowo)
        if growth >= 0.5:
            points = 10.0
        elif growth <= -0.5:
            points = 0.0
        else:
            points = 5.0 + (growth * 10.0)  # growth=0.0 -> 5 pkt; +/-0.5 -> +/-5 pkt

        tooltip = (
            f"Ostatnie 4Q: {sum_last4:,.2f}\n"
            f"Poprzednie 4Q: {sum_prev4:,.2f}\n"
            f"Dynamika: {growth*100:.2f}%\n"
            f"Punkty (Q): {points:.2f}"
        )
        return round(points, 2), tooltip

    def _compute_yearly_revenue_points(self, company: dict) -> Tuple[Optional[float], str]:
        """
        Liczy punkty na bazie rocznych przychodów: ostatni rok vs poprzedni rok.
        Zwraca (punkty, opis do tooltipa).
        """
        y = company.get("yearly_revenue") or []
        series = {}
        for item in y:
            key = str(item.get("date") or "").strip()
            val = self._safe_float(item.get("revenue"))
            if not key or val is None:
                continue
            if not re.match(r"^\d{4}$", key):
                continue
            series[int(key)] = val

        if len(series) < 2:
            return None, "Za mało danych rocznych: potrzeba min. 2 lata."

        years_sorted = sorted(series.keys())
        last_year = years_sorted[-1]
        prev_year = years_sorted[-2]
        v_last = series[last_year]
        v_prev = series[prev_year]

        if v_prev == 0:
            return None, "Poprzedni rok = 0 – brak możliwości policzenia dynamiki."

        growth = (v_last - v_prev) / v_prev

        # Skala punktowa spójna z kwartalną:
        if growth >= 0.5:
            points = 10.0
        elif growth <= -0.5:
            points = 0.0
        else:
            points = 5.0 + (growth * 10.0)

        tooltip = (
            f"Ostatni rok ({last_year}): {v_last:,.2f}\n"
            f"Poprzedni rok ({prev_year}): {v_prev:,.2f}\n"
            f"Dynamika: {growth*100:.2f}%\n"
            f"Punkty (Y): {points:.2f}"
        )
        return round(points, 2), tooltip

    # ---------------------------------------------------------

    def load_column_widths(self) -> None:
        try:
            if os.path.exists(self.column_widths_file):
                with open(self.column_widths_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        logging.warning(f"Plik {self.column_widths_file} jest pusty, używam domyślnych szerokości")
                        return
                    col_widths = json.load(f)
                    for col, width in col_widths.items():
                        if col in self.columns:
                            self.tree.column(col, width=int(width))
                    logging.info(f"Wczytano szerokości kolumn z {self.column_widths_file}")
        except json.JSONDecodeError as e:
            logging.error(f"Błąd dekodowania pliku {self.column_widths_file}: {str(e)}")
        except PermissionError as e:
            logging.error(f"Brak uprawnień do odczytu pliku {self.column_widths_file}: {str(e)}")
        except Exception as e:
            logging.error(f"Błąd wczytywania szerokości kolumn: {str(e)}")

    def save_column_widths(self) -> None:
        try:
            col_widths = {col: self.tree.column(col, "width") for col in self.columns}
            with open(self.column_widths_file, "w", encoding="utf-8") as f:
                json.dump(col_widths, f, indent=4)
            logging.info(f"Zapisano szerokości kolumn do {self.column_widths_file}")
        except PermissionError as e:
            logging.error(f"Brak uprawnień do zapisu pliku {self.column_widths_file}: {str(e)}")
            messagebox.showerror("Błąd", f"Brak uprawnień do zapisu pliku {self.column_widths_file}. Uruchom aplikację jako administrator.")
        except Exception as e:
            logging.error(f"Błąd zapisywania szerokości kolumn: {str(e)}")
            messagebox.showerror("Błąd", f"Nie udało się zapisać szerokości kolumn: {str(e)}")

    def on_closing(self) -> None:
        self.save_column_widths()
        self.hide_price_plot_window()
        self.hide_score_plot_window()
        self.hide_financial_plots()
        self.hide_revenue_plots()
        self.hide_details_window()
        self.hide_tooltip()
        self.root.destroy()

    def add_tickers(self) -> None:
        try:
            tickers = self.ticker_entry.get().replace(" ", "").split(",")
            valid_tickers = []
            for ticker in tickers:
                ticker = ticker.strip().upper()
                if not ticker:
                    continue
                if not ticker.isalnum():
                    logging.warning(f"Nieprawidłowy ticker: {ticker}, pomijanie")
                    messagebox.showwarning("Błąd", f"Nieprawidłowy ticker: {ticker}")
                    continue
                if any(c["ticker"] == ticker for c in self.company_data.companies):
                    logging.warning(f"Spółka {ticker} już istnieje, pomijanie")
                    messagebox.showinfo("Informacja", f"Spółka {ticker} już istnieje")
                    continue
                valid_tickers.append(ticker)
            if not valid_tickers:
                logging.warning("Brak prawidłowych tickerów do dodania")
                messagebox.showwarning("Błąd", "Nie podano prawidłowych tickerów!")
                return
            for ticker in valid_tickers:
                try:
                    self.company_data.add_company(ticker)
                    logging.info(f"Dodano ticker: {ticker}")
                    file_path = os.path.join("data", f"{ticker}.json")
                    if os.path.exists(file_path):
                        logging.info(f"Plik JSON dla {ticker} utworzony poprawnie: {file_path}")
                    else:
                        logging.error(f"Nie udało się utworzyć pliku JSON dla {ticker}")
                        messagebox.showerror("Błąd", f"Nie udało się utworzyć pliku danych dla {ticker}")
                except Exception as e:
                    logging.error(f"Błąd podczas dodawania tickera {ticker}: {str(e)}")
                    messagebox.showerror("Błąd", f"Błąd podczas dodawania {ticker}: {str(e)}")
            self.update_table()
            self.ticker_entry.delete(0, tk.END)
            self.update_ticker_combobox()
            if valid_tickers:
                messagebox.showinfo("Sukces", f"Dodano tickery: {', '.join(valid_tickers)}")
        except Exception as e:
            logging.error(f"Błąd podczas dodawania tickerów: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się dodać tickerów!")

    def update_ticker_combobox(self) -> None:
        tickers = [company["ticker"] for company in self.company_data.companies]
        self.ticker_combobox["values"] = tickers
        if tickers:
            self.ticker_combobox.set(tickers[0])
            self.on_ticker_select(None)

    def on_ticker_select(self, event: tk.Event) -> None:
        try:
            ticker = self.ticker_combobox.get()
            company = self.company_data.get_company(ticker)
            if company:
                for field, entry in self.financial_inputs.items():
                    value = company.get(field, "")
                    entry.delete(0, tk.END)
                    entry.insert(0, format_number(value) if value not in [None, "", "-", "NA", "N/A", "None", "nan"] else "")
        except Exception as e:
            logging.error(f"Błąd podczas wyboru tickera: {str(e)}")

    def save_financial_data(self) -> None:
        try:
            ticker = self.ticker_combobox.get()
            if not ticker:
                messagebox.showwarning("Błąd", "Wybierz spółkę!")
                return
            company = self.company_data.get_company(ticker)
            if not company:
                messagebox.showerror("Błąd", f"Spółka {ticker} nie istnieje!")
                return
            for field, entry in self.financial_inputs.items():
                value = entry.get().strip()
                if value:
                    try:
                        company[field] = str(round(parse_number(value), 2))
                        company[f"is_manual_{field}"] = True
                        company[f"indicator_color_{field}"] = "blue"
                    except ValueError as e:
                        logging.warning(f"Nieprawidłowa wartość dla {field}: {value}")
                        messagebox.showwarning("Błąd", f"Nieprawidłowa wartość dla {field}: {str(e)}")
                        return
                else:
                    company[field] = None
                    company[f"is_manual_{field}"] = False
                    company[f"indicator_color_{field}"] = "black"
            self.company_data.save_company_data(ticker, company)
            self.recalculate_score(ticker)
            self.update_table()
            messagebox.showinfo("Sukces", f"Dane dla {ticker} zapisane!")
        except Exception as e:
            logging.error(f"Błąd podczas zapisywania danych finansowych: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się zapisać danych!")

    def recalculate_score(self, ticker: str) -> None:
        """
        Przelicza punktację dla danej spółki.
        Args:
            ticker: Symbol tickera (np. 'AAPL').
        """
        try:
            company = self.company_data.get_company(ticker)
            if not company:
                logging.error(f"Nie znaleziono spółki {ticker} do przeliczenia punktacji")
                return
            sector = company.get("sektor")
            if not sector:
                logging.warning(f"Brak sektora dla {ticker}, pomijam przeliczenie punktacji")
                company["faza"] = "None"
                company["punkty"] = "None"
                self.company_data.save_company_data(ticker, company)
                return
            faza = classify_phase(sector, company)
            company["faza"] = faza if faza is not None else "None"
            if faza != "None":
                score_result = calculate_score(sector, faza, company, self.company_data)
                if score_result:
                    score, _ = score_result
                    company["punkty"] = str(round(float(score), 2)) if score is not None else "None"
                else:
                    company["punkty"] = "None"
            else:
                company["punkty"] = "None"
            self.company_data.save_company_data(ticker, company)
            logging.info(f"Przeliczono punktację dla {ticker}: {company.get('punkty')}")
            self.update_table()
        except Exception as e:
            logging.error(f"Błąd podczas przeliczania punktacji dla {ticker}: {str(e)}")

    def update_table(self) -> None:
        """
        Aktualizuje tabelkę z danymi spółek, respektując ręczne zmiany sektora i fazy.
        """
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            col_widths = {col: self.tree.column(col, "width") for col in self.columns}
            if os.path.exists(self.column_widths_file):
                with open(self.column_widths_file, "r", encoding="utf-8") as f:
                    try:
                        stored = json.load(f)
                        col_widths.update({k: v for k, v in stored.items() if k in self.columns})
                    except Exception:
                        pass

            self.tooltips.clear()
            valid_sectors = {f.replace(".json", "").lower()
                             for f in os.listdir(os.path.join("src", "core", "sectors"))
                             if f.endswith(".json")}
            companies = sorted(
                self.company_data.companies,
                key=lambda c: c.get("is_in_portfolio", False),
                reverse=True
            )
            for company in companies:
                score_details = {"used_fallbacks": {}, "bonuses": {}, "indicators": {}, "sector_phase_avg": 0.0,
                                 "sector_avg": 0.0, "trend_details": {}}
                sector = company.get("sektor", None)
                faza = company.get("faza", None)
                is_manual_sektor = company.get("is_manual_sektor", False)
                is_manual_faza = company.get("is_manual_faza", False)

                if not is_manual_sektor and sector:
                    try:
                        normalized_sector = normalize_sector(sector)
                        if normalized_sector.lower() in valid_sectors:
                            company["sektor"] = normalized_sector
                        else:
                            logging.warning(f"Nieprawidłowy sektor {sector} dla {company['ticker']}, ustawiono None")
                            company["sektor"] = None
                            company["faza"] = "None"
                            company["punkty"] = "None"
                    except AttributeError as e:
                        logging.error(f"Błąd normalizacji sektora dla {company['ticker']}: {str(e)}")
                        company["sektor"] = None
                        company["faza"] = "None"
                        company["punkty"] = "None"

                if not is_manual_faza and company["sektor"]:
                    faza = classify_phase(company["sektor"], company)
                    company["faza"] = faza if faza is not None else "None"
                    if faza != "None":
                        score_result = calculate_score(company["sektor"], faza, company, self.company_data)
                        if score_result:
                            score, score_details = score_result
                            company["punkty"] = str(round(float(score), 2)) if score is not None else "None"
                        else:
                            company["punkty"] = "None"
                    else:
                        company["punkty"] = "None"

                if not is_manual_sektor or not is_manual_faza:
                    try:
                        self.company_data.save_company_data(company["ticker"], company)
                    except Exception as e:
                        logging.error(f"Błąd zapisywania danych dla {company['ticker']}: {str(e)}")
                        continue

                row_tag = "green_row"
                missing_main: List[str] = []
                missing_fallback: List[str] = []
                sector_config = load_sector_config(company["sektor"]) if company["sektor"] else None
                main_indicators = []
                fallback_indicators = []
                phase_config = None
                if sector_config and company["faza"] in sector_config["indicators"]:
                    phase_config = sector_config["indicators"][company["faza"]]
                    main_indicators = phase_config["main"]
                    for ind in phase_config["fallback"]:
                        fallback_indicators.extend(fb["indicator"] for fb in phase_config["fallback"][ind])

                for ind in main_indicators:
                    if company.get(ind) in [None, "", "-", "NA", "N/A", "None", "nan"]:
                        missing_main.append(ind)

                if phase_config:
                    for main_ind in missing_main:
                        has_fallback = False
                        for fb in phase_config["fallback"].get(main_ind, []):
                            fb_ind = fb["indicator"]
                            if company.get(fb_ind) not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                                has_fallback = True
                                break
                        if not has_fallback:
                            missing_fallback.append(main_ind)

                if missing_fallback:
                    row_tag = "red_row"
                elif missing_main:
                    row_tag = "orange_row"

                values = []
                ticker = company["ticker"]
                self.tooltips[ticker] = {}

                # wstępnie policz punkty przychodowe (na potrzeby kolumn i tooltipów)
                q_points, q_tip = self._compute_quarterly_revenue_points(company)
                y_points, y_tip = self._compute_yearly_revenue_points(company)

                for col in self.columns:
                    if col == "więcej":
                        display_value = "Pokaż"
                        self.tooltips[ticker][col] = "Kliknij, aby zobaczyć szczegóły i edycję przychodów."
                    elif col == "pkt_przych_kw":
                        if q_points is None:
                            display_value = "-"
                            self.tooltips[ticker][col] = q_tip or "Brak danych kwartalnych."
                        else:
                            display_value = f"{q_points:.2f}"
                            self.tooltips[ticker][col] = q_tip
                    elif col == "pkt_przych_roczne":
                        if y_points is None:
                            display_value = "-"
                            self.tooltips[ticker][col] = y_tip or "Brak danych rocznych."
                        else:
                            display_value = f"{y_points:.2f}"
                            self.tooltips[ticker][col] = y_tip
                    else:
                        json_key = self.col_to_json.get(col, col)
                        value = company.get(json_key)
                        if col in ["ticker", "nazwa", "sektor", "faza"]:
                            display_value = str(value) if value not in [None, "-", "NA", "N/A", "None", "nan"] else ""
                        elif col == "punkty" and value not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                            display_value = f"{float(value):.2f}"
                            tooltip_lines = [f"Punkty: {display_value}"]
                            base_score = min(float(value) - sum(score_details["bonuses"].values()), 91.0)
                            tooltip_lines.append(f"Bazowa punktacja: {base_score:.2f}/91")
                            for indicator, info in score_details["indicators"].items():
                                if info["points"] != 0:
                                    penalty = " (kara za ujemną wartość)" if info.get("penalty") else ""
                                    tooltip_lines.append(
                                        f"{indicator.replace('_', ' ').title()}: {info['points']:.2f} pkt "
                                        f"(wartość: {info['value']}, waga: {info['weight']}){penalty}"
                                    )
                            for bonus, points in score_details["bonuses"].items():
                                bonus_name = "Sektor" if bonus == "sector" else "Ogólna średnia" if bonus == "overall" else "Trendy"
                                tooltip_lines.append(f"Bonus za {bonus_name}: {'+' if points > 0 else ''}{points} pkt")
                            if score_details["sector_phase_avg"] == 0.0:
                                tooltip_lines.append("Ostrzeżenie: Niewystarczająca liczba spółek dla średniej sektorowej")
                            for indicator, info in score_details["indicators"].items():
                                if info.get("dynamic_thresholds"):
                                    tooltip_lines.append(f"Użyto dynamicznych progów dla {indicator.replace('_', ' ').title()}")

                            # DODANE: pokaż też syntetycznie punkty przychodowe
                            tooltip_lines.append("--- Przychody ---")
                            if q_points is not None:
                                tooltip_lines.append(f"Kwartalne: {q_points:.2f} pkt")
                            if y_points is not None:
                                tooltip_lines.append(f"Roczne: {y_points:.2f} pkt")

                            tooltip_lines.append(
                                f"Podsumowanie: {base_score:.2f}/91 + {sum(score_details['bonuses'].values())} bonusy = {display_value}"
                            )
                            self.tooltips[ticker][col] = "\n".join(tooltip_lines)
                        else:
                            display_value = ""
                            self.tooltips[ticker][col] = f"Brak danych dla {col.replace('_', ' ').title()}"

                    values.append(display_value)

                item_id = self.tree.insert("", tk.END, values=values, tags=row_tag)
                logging.debug(f"Wstawiono dane do tabelki dla {company.get('ticker')}: {values}, tag: {row_tag}")

                for col in self.columns:
                    self.tree.column(col, width=col_widths.get(col, self.tree.column(col, "width")))

            self.update_ticker_combobox()
            logging.info(f"Zaktualizowano tabelkę z {len(self.company_data.companies)} spółkami")
        except Exception as e:
            logging.error(f"Błąd podczas aktualizacji tabelki: {str(e)}")
            if self.tree.get_children():
                logging.info("Tabelka została zaktualizowana mimo błędu, pomijam komunikat")
            else:
                messagebox.showerror("Błąd", "Nie udało się zaktualizować tabelki!")

    def on_tab_change(self, event: tk.Event) -> None:
        """Ukrywa tooltip i okna wykresów przy zmianie zakładki."""
        self.hide_tooltip()
        self.hide_price_plot_window()
        self.hide_score_plot_window()
        self.hide_financial_plots()
        self.hide_revenue_plots()
        self.hide_details_window()

    def on_tree_motion(self, event: tk.Event) -> None:
        try:
            item = self.tree.identify_row(event.y)
            col = self.tree.identify_column(event.x)
            if item and col:
                values = self.tree.item(item)["values"]
                if not values:
                    return
                ticker = values[0]
                col_index = int(col.replace("#", "")) - 1
                col_name = self.columns[col_index]
                if ticker in self.tooltips and col_name in self.tooltips[ticker]:
                    self.show_tooltip(event, self.tooltips[ticker][col_name], col_name)
                else:
                    self.hide_tooltip()
        except Exception as e:
            logging.error(f"Błąd podczas obsługi ruchu myszy: {str(e)}")

    def show_tooltip(self, event: tk.Event, text: str, col_name: str) -> None:
        if self.tooltip:
            self.hide_tooltip()
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        lines = text.split("\n")
        tooltip_width = max(len(line) for line in lines) * 6 + 10
        tooltip_height = len(lines) * 15 + 6
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        cell_bbox = self.tree.bbox(self.tree.identify_row(event.y), col_name)
        if not cell_bbox:
            self.hide_tooltip()
            return
        cell_x, cell_y, cell_width, cell_height = cell_bbox
        cell_x_root = self.root.winfo_rootx() + cell_x
        cell_y_root = self.root.winfo_rooty() + cell_y
        if col_name == "punkty" or (cell_x_root + cell_width + tooltip_width) > screen_width - 20:
            x_pos = max(cell_x_root - tooltip_width - 10, 10)
        else:
            x_pos = cell_x_root + cell_width + 10
        if (cell_y_root + tooltip_height) > screen_height - 20:
            y_pos = max(cell_y_root - tooltip_height - 10, 10)
        else:
            y_pos = cell_y_root + cell_height + 10
        self.tooltip.wm_geometry(f"{tooltip_width}x{tooltip_height}+{x_pos}+{y_pos}")
        label = tk.Label(
            self.tooltip,
            text=text,
            background="#FFFFE0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 10),
            justify="left",
            padx=3,
            pady=3
        )
        label.pack()

    def hide_tooltip(self, event: Optional[tk.Event] = None) -> None:
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def show_details_window(self, ticker: str) -> None:
        """
        Otwiera okno szczegółów dla wybranej spółki z polami dla przychodów kwartalnych i rocznych.
        Args:
            ticker: Symbol tickera (np. 'AAPL').
        """
        try:
            if not ticker:
                messagebox.showwarning("Błąd", "Wybierz spółkę!")
                return
            if self.details_window:
                self.hide_details_window()
            company = self.company_data.get_company(ticker)
            if not company:
                messagebox.showerror("Błąd", f"Spółka {ticker} nie istnieje!")
                return
            self.details_window = tk.Toplevel(self.root)
            self.details_window.title(f"Szczegóły: {ticker}")
            self.details_window.wm_geometry("800x800+100+100")
            self.details_window.bind("<Button-1>", lambda e: None)

            detail_fields = [
                "cena", "analyst_target_price", "pe_ratio", "forward_pe", "peg_ratio",
                "revenue_growth", "gross_margin", "debt_equity", "current_ratio", "roe",
                "free_cash_flow_margin", "eps_ttm", "price_to_book_ratio", "price_to_sales_ratio",
                "operating_margin", "profit_margin", "quick_ratio", "cash_ratio",
                "cash_flow_to_debt_ratio", "analyst_rating", "earnings_growth",
                "ebitda_margin", "roic", "user_growth", "interest_coverage",
                "net_debt_ebitda", "inventory_turnover", "asset_turnover",
                "operating_cash_flow", "free_cash_flow", "ffo", "ltv", "rnd_sales", "cac_ltv"
            ]
            detail_labels = {
                "cena": "Price", "analyst_target_price": "Price Target", "pe_ratio": "PE Ratio",
                "forward_pe": "Forward PE", "peg_ratio": "PEG Ratio", "revenue_growth": "Revenue Growth YoY",
                "gross_margin": "Gross Margin", "debt_equity": "Debt Equity Ratio",
                "current_ratio": "Current Ratio", "roe": "ROE", "free_cash_flow_margin": "Free Cash Flow Margin",
                "eps_ttm": "EPS TTM", "price_to_book_ratio": "PB Ratio", "price_to_sales_ratio": "PS Ratio",
                "operating_margin": "Operating Margin", "profit_margin": "Profit Margin",
                "quick_ratio": "Quick Ratio", "cash_ratio": "Cash Ratio",
                "cash_flow_to_debt_ratio": "Debt FCF Ratio", "analyst_rating": "Analyst Consensus",
                "earnings_growth": "Earnings Growth", "ebitda_margin": "EBITDA Margin",
                "roic": "Return on Invested Capital (ROIC)", "user_growth": "User Growth",
                "interest_coverage": "Interest Coverage", "net_debt_ebitda": "Debt / EBITDA Ratio",
                "inventory_turnover": "Inventory Turnover", "asset_turnover": "Asset Turnover",
                "operating_cash_flow": "Operating Cash Flow", "free_cash_flow": "Free Cash Flow",
                "ffo": "Funds from Operations (FFO)", "ltv": "Lifetime Value (LTV)",
                "rnd_sales": "R&D to Sales Ratio", "cac_ltv": "CAC to LTV Ratio"
            }

            canvas = tk.Canvas(self.details_window)
            scrollbar = ttk.Scrollbar(self.details_window, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            row = 0
            for field in detail_fields:
                frame = ttk.Frame(scrollable_frame)
                frame.grid(row=row, column=0, padx=5, pady=2, sticky="w")
                label = ttk.Label(frame, text=detail_labels.get(field, field.replace("_", " ").title()))
                label.pack(side="left")
                value = company.get(field, "")
                display_value = format_number(value) if value and value not in [None, "", "-", "NA", "N/A", "None", "nan"] and field != "analyst_rating" else str(value) if value not in [None, "", "-", "NA", "N/A", "None", "nan"] else ""
                entry = ttk.Entry(frame)
                entry.insert(0, display_value)
                entry.config(state="readonly")
                entry.pack(side="left", fill="x", expand=True)
                row += 1

            # Dodanie pól dla przychodów kwartalnych (Q1-Q4)
            ttk.Label(scrollable_frame, text="Przychody kwartalne", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=5, pady=5, sticky="w")
            row += 1
            quarters = ["Q1", "Q2", "Q3", "Q4"]
            self.quarterly_entries = {}
            current_year = datetime.now().year
            for quarter in quarters:
                frame = ttk.Frame(scrollable_frame)
                frame.grid(row=row, column=0, padx=5, pady=2, sticky="w")
                label = ttk.Label(frame, text=f"{quarter} {current_year}")
                label.pack(side="left")
                entry = ttk.Entry(frame)
                entry.pack(side="left", fill="x", expand=True)
                quarterly_data = next((item for item in company.get("quarterly_revenue", []) if item.get("date") == f"{current_year}-{quarter}"), {})
                entry.insert(0, format_number(quarterly_data.get("revenue")) if quarterly_data.get("revenue") else "")
                self.quarterly_entries[f"{quarter}_{current_year}"] = entry
                row += 1

            # Dodanie pól dla przychodów rocznych
            ttk.Label(scrollable_frame, text="Przychody roczne", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=5, pady=5, sticky="w")
            row += 1
            years = [current_year, current_year - 1, current_year - 2, current_year - 4]
            self.yearly_entries = {}
            for year in years:
                frame = ttk.Frame(scrollable_frame)
                frame.grid(row=row, column=0, padx=5, pady=2, sticky="w")
                label = ttk.Label(frame, text=f"Rok {year}")
                label.pack(side="left")
                entry = ttk.Entry(frame)
                entry.pack(side="left", fill="x", expand=True)
                yearly_data = next((item for item in company.get("yearly_revenue", []) if item.get("date") == str(year)), {})
                entry.insert(0, format_number(yearly_data.get("revenue")) if yearly_data.get("revenue") else "")
                self.yearly_entries[str(year)] = entry
                row += 1

            # Przyciski
            button_frame = ttk.Frame(scrollable_frame)
            button_frame.grid(row=row, column=0, pady=10)
            ttk.Button(button_frame, text="Zapisz", command=lambda: self.save_revenue_data(ticker)).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Edytuj dane", command=lambda: self.open_edit_window(ticker=ticker)).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Zamknij", command=self.hide_details_window).pack(side="left", padx=5)
        except Exception as e:
            logging.error(f"Błąd podczas wyświetlania okna szczegółów dla {ticker}: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się wyświetlić okna szczegółów!")

    def save_revenue_data(self, ticker: str) -> None:
        """
        Zapisuje dane przychodów kwartalnych i rocznych dla spółki.
        Args:
            ticker: Symbol tickera (np. 'AAPL').
        """
        try:
            company = self.company_data.get_company(ticker)
            if not company:
                messagebox.showerror("Błąd", f"Spółka {ticker} nie istnieje!")
                return
            current_year = datetime.now().year

            # Zapis przychodów kwartalnych
            company["quarterly_revenue"] = company.get("quarterly_revenue", [])
            for quarter in ["Q1", "Q2", "Q3", "Q4"]:
                value = self.quarterly_entries[f"{quarter}_{current_year}"].get().strip()
                if value:
                    try:
                        revenue = parse_number(value)
                        company["quarterly_revenue"] = [
                            item for item in company["quarterly_revenue"] if item.get("date") != f"{current_year}-{quarter}"
                        ]
                        company["quarterly_revenue"].append({
                            "date": f"{current_year}-{quarter}",
                            "revenue": f"{revenue:.2f}",
                            "is_manual": True
                        })
                    except ValueError as e:
                        logging.warning(f"Nieprawidłowa wartość przychodu dla {quarter}_{current_year}: {value}")
                        messagebox.showwarning("Błąd", f"Nieprawidłowa wartość dla {quarter} {current_year}: {str(e)}")
                        return

            # Zapis przychodów rocznych
            company["yearly_revenue"] = company.get("yearly_revenue", [])
            for year in [current_year, current_year - 1, current_year - 2, current_year - 4]:
                value = self.yearly_entries[str(year)].get().strip()
                if value:
                    try:
                        revenue = parse_number(value)
                        company["yearly_revenue"] = [
                            item for item in company["yearly_revenue"] if item.get("date") != str(year)
                        ]
                        company["yearly_revenue"].append({
                            "date": str(year),
                            "revenue": f"{revenue:.2f}",
                            "is_manual": True
                        })
                    except ValueError as e:
                        logging.warning(f"Nieprawidłowa wartość przychodu dla roku {year}: {value}")
                        messagebox.showwarning("Błąd", f"Nieprawidłowa wartość dla roku {year}: {str(e)}")
                        return

            self.company_data.save_company_data(ticker, company)
            self.recalculate_score(ticker)
            self.update_table()
            messagebox.showinfo("Sukces", f"Dane przychodów dla {ticker} zapisane!")
            self.hide_details_window()
        except Exception as e:
            logging.error(f"Błąd podczas zapisywania danych przychodów dla {ticker}: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się zapisać danych przychodów!")

    def hide_details_window(self, event: Optional[tk.Event] = None) -> None:
        if self.details_window:
            self.details_window.destroy()
            self.details_window = None

    def on_tree_double_click(self, event: tk.Event) -> None:
        try:
            item = self.tree.identify_row(event.y)
            col = self.tree.identify_column(event.x)
            if item and col:
                col_index = int(col.replace("#", "")) - 1
                if 0 <= col_index < len(self.columns):
                    if self.columns[col_index] == "więcej":
                        ticker = self.tree.item(item)["values"][0]
                        self.show_details_window(ticker)
        except Exception as e:
            logging.error(f"Błąd podczas obsługi podwójnego kliknięcia: {str(e)}")

    def show_price_plot_window(self) -> None:
        try:
            if not self.current_ticker:
                messagebox.showwarning("Błąd", "Wybierz spółkę!")
                return
            if self.price_plot_window:
                self.hide_price_plot_window()
            self.price_plot_window = tk.Toplevel(self.root)
            self.price_plot_window.wm_geometry("600x200+100+100")
            self.price_plot_window.title(f"Wykres cenowy: {self.current_ticker}")
            self.price_plot_window.bind("<Button-1>", self.hide_price_plot_window)

            self.fig, self.ax = plt.subplots(figsize=(6, 2))
            history = self.company_data.load_company_history(self.current_ticker)
            dates = [entry["date"] for entry in history]
            prices = [float(entry.get("cena", 0) or 0) if entry.get("cena") not in ["None", "-", "NA", "N/A", "nan"] else 0 for entry in history]
            self.ax.plot(dates, prices, marker="o", label="Cena")
            for i, price in enumerate(prices):
                self.ax.axhline(y=price, xmin=(i/len(dates)), xmax=((i+1)/len(dates)), linestyle="--", alpha=0.5)
            self.ax.set_title(f"Historia ceny: {self.current_ticker}")
            self.ax.set_xlabel("Data")
            self.ax.set_ylabel("Cena")
            self.ax.legend()
            self.ax.tick_params(axis="x", rotation=45)
            self.fig.tight_layout()
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.price_plot_window)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            self.canvas.draw()
        except Exception as e:
            logging.error(f"Błąd podczas wyświetlania okna wykresu cenowego dla {self.current_ticker}: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się wyświetlić wykresu cenowego!")

    def hide_price_plot_window(self, event: Optional[tk.Event] = None) -> None:
        if self.price_plot_window:
            self.price_plot_window.destroy()
            self.price_plot_window = None
            self.canvas = None
            self.fig = None

    def show_score_plot_window(self) -> None:
        try:
            if not self.current_ticker:
                messagebox.showwarning("Błąd", "Wybierz spółkę!")
                return
            if self.score_plot_window:
                self.hide_score_plot_window()
            self.score_plot_window = tk.Toplevel(self.root)
            self.score_plot_window.wm_geometry("600x200+100+100")
            self.score_plot_window.title(f"Wykres punktacji: {self.current_ticker}")
            self.score_plot_window.bind("<Button-1>", self.hide_score_plot_window)

            self.fig, self.ax = plt.subplots(figsize=(6, 2))
            history = self.company_data.load_company_history(self.current_ticker)
            dates = [entry["date"] for entry in history]
            points = [float(entry.get("punkty", 0) or 0) if entry.get("punkty") not in ["None", "-", "NA", "N/A", "nan"] else 0 for entry in history]
            self.ax.plot(dates, points, marker="o", label="Punkty")
            for i, point in enumerate(points):
                self.ax.axhline(y=point, xmin=(i/len(dates)), xmax=((i+1)/len(dates)), linestyle="--", alpha=0.5)
            self.ax.set_title(f"Historia punktacji: {self.current_ticker}")
            self.ax.set_xlabel("Data")
            self.ax.set_ylabel("Punkty (0-100)")
            self.ax.set_ylim(0, 100)
            self.ax.legend()
            self.ax.tick_params(axis="x", rotation=45)
            self.fig.tight_layout()
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.score_plot_window)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            self.canvas.draw()
        except Exception as e:
            logging.error(f"Błąd podczas wyświetlania okna punktacji dla {self.current_ticker}: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się wyświetlić wykresu punktacji!")

    def hide_score_plot_window(self, event: Optional[tk.Event] = None) -> None:
        if self.score_plot_window:
            self.score_plot_window.destroy()
            self.score_plot_window = None
            self.canvas = None
            self.fig = None

    def show_financial_plots(self) -> None:
        """
        ZOSTAWIONE: wykresy linii wybranych wskaźników na bazie historycznych zapisów (jak w Twojej wersji).
        """
        try:
            if not self.current_ticker:
                messagebox.showwarning("Błąd", "Wybierz spółkę!")
                return
            if self.financial_plot_window:
                self.hide_financial_plots()
            self.financial_plot_window = tk.Toplevel(self.root)
            self.financial_plot_window.wm_geometry("800x600+100+100")
            self.financial_plot_window.title(f"Dane finansowe (linie): {self.current_ticker}")
            self.financial_plot_window.bind("<Button-1>", self.hide_financial_plots)

            history = self.company_data.load_company_history(self.current_ticker)
            if not history:
                messagebox.showwarning("Błąd", "Brak danych historycznych!")
                return

            indicators = [
                "revenue", "market_cap", "free_cash_flow_margin", "roe",
                "debt_equity", "profit_margin", "cash_ratio"
            ]
            fig, axes = plt.subplots(len(indicators), 1, figsize=(8, len(indicators) * 2))
            if len(indicators) == 1:
                axes = [axes]
            dates = [entry["date"] for entry in history]
            for idx, indicator in enumerate(indicators):
                values = [
                    float(entry.get(indicator, 0) or 0)
                    if entry.get(indicator) not in [None, "", "-", "NA", "N/A", "None", "nan"]
                    else 0
                    for entry in history
                ]
                axes[idx].plot(dates, values, marker="o", label=indicator.replace("_", " ").title())
                for i, value in enumerate(values):
                    axes[idx].axhline(y=value, xmin=(i/len(dates)), xmax=((i+1)/len(dates)), linestyle="--", alpha=0.5)
                axes[idx].set_title(f"{indicator.replace('_', ' ').title()}")
                axes[idx].set_xlabel("Data")
                axes[idx].set_ylabel(indicator.replace("_", " ").title())
                axes[idx].legend()
                axes[idx].tick_params(axis="x", rotation=45)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.financial_plot_window)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()
        except Exception as e:
            logging.error(f"Błąd podczas wyświetlania wykresów finansowych dla {self.current_ticker}: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się wyświetlić wykresów finansowych!")

    def hide_financial_plots(self, event: Optional[tk.Event] = None) -> None:
        if self.financial_plot_window:
            self.financial_plot_window.destroy()
            self.financial_plot_window = None
            self.canvas = None
            self.fig = None

    def show_revenue_bars(self) -> None:
        """
        NOWE: okno z wykresami słupkowymi przychodów kwartalnych i rocznych (z plików JSON).
        """
        try:
            if not self.current_ticker:
                messagebox.showwarning("Błąd", "Wybierz spółkę!")
                return
            if self.revenue_plot_window:
                self.hide_revenue_plots()
            self.revenue_plot_window = tk.Toplevel(self.root)
            self.revenue_plot_window.wm_geometry("900x600+120+120")
            self.revenue_plot_window.title(f"Przychody (słupki): {self.current_ticker}")
            self.revenue_plot_window.bind("<Button-1>", self.hide_revenue_plots)

            company = self.company_data.get_company(self.current_ticker)
            if not company:
                messagebox.showwarning("Błąd", "Brak danych spółki!")
                return

            q = company.get("quarterly_revenue") or []
            y = company.get("yearly_revenue") or []

            # Przygotuj dane kwartalne: sort po (rok, kwartał)
            def q_key(item):
                key = str(item.get("date", ""))
                parsed = self._parse_quarter_key(key)
                return parsed if parsed else (0, 0)

            q_sorted = sorted(
                [i for i in q if self._parse_quarter_key(str(i.get("date", ""))) is not None],
                key=q_key
            )
            q_labels = [str(i["date"]) for i in q_sorted]
            q_vals = [self._safe_float(i.get("revenue")) or 0.0 for i in q_sorted]

            # Przygotuj dane roczne: sort po roku
            y_sorted = sorted(
                [i for i in y if re.match(r"^\d{4}$", str(i.get("date", "")) or "")],
                key=lambda i: int(i["date"])
            )
            y_labels = [str(i["date"]) for i in y_sorted]
            y_vals = [self._safe_float(i.get("revenue")) or 0.0 for i in y_sorted]

            fig, axes = plt.subplots(2, 1, figsize=(10, 6))

            # Słupki kwartalne
            axes[0].bar(q_labels, q_vals, label="Przychody kwartalne")
            axes[0].set_title("Przychody kwartalne")
            axes[0].set_xlabel("Kwartał")
            axes[0].set_ylabel("Przychody")
            axes[0].tick_params(axis="x", rotation=45)
            axes[0].legend()

            # Słupki roczne
            axes[1].bar(y_labels, y_vals, label="Przychody roczne")
            axes[1].set_title("Przychody roczne")
            axes[1].set_xlabel("Rok")
            axes[1].set_ylabel("Przychody")
            axes[1].tick_params(axis="x", rotation=45)
            axes[1].legend()

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.revenue_plot_window)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()

        except Exception as e:
            logging.error(f"Błąd podczas wyświetlania słupków przychodów dla {self.current_ticker}: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się wyświetlić wykresów przychodów!")

    def hide_revenue_plots(self, event: Optional[tk.Event] = None) -> None:
        if self.revenue_plot_window:
            self.revenue_plot_window.destroy()
            self.revenue_plot_window = None

    def on_tree_select(self, event: tk.Event) -> None:
        try:
            selected = self.tree.selection()
            if selected:
                ticker = self.tree.item(selected[0])["values"][0]
                if ticker != self.current_ticker:
                    self.current_ticker = ticker
                    self.hide_price_plot_window()
                    self.hide_score_plot_window()
                    self.hide_financial_plots()
                    self.hide_revenue_plots()
                    self.hide_details_window()
            else:
                self.current_ticker = None
                self.hide_price_plot_window()
                self.hide_score_plot_window()
                self.hide_financial_plots()
                self.hide_revenue_plots()
                self.hide_details_window()
        except Exception as e:
            logging.error(f"Błąd podczas wyboru: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się wybrać spółki!")

    def fetch_data(self) -> None:
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Błąd", "Wybierz co najmniej jedną spółkę!")
                return
            tickers = [self.tree.item(item)["values"][0] for item in selected]
            results, missing = self.company_data.fetch_data(tickers, parent=self.root)
            for ticker in results:
                self.company_data.save_company_data(ticker, results[ticker])
                self.recalculate_score(ticker)
                self.update_table()
                if ticker == self.current_ticker:
                    self.hide_price_plot_window()
                    self.hide_score_plot_window()
                    self.hide_financial_plots()
                    self.hide_revenue_plots()
                    self.hide_details_window()
            if missing:
                messagebox.showwarning("Ostrzeżenie", f"Brakujące dane dla tickerów: {', '.join(missing.keys())}")
        except Exception as e:
            logging.error(f"Błąd podczas pobierania danych z API: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się pobrać danych z API!")

    def open_edit_window(self, ticker: Optional[str] = None) -> None:
        try:
            if not ticker:
                selected = self.tree.selection()
                if not selected:
                    messagebox.showwarning("Błąd", "Wybierz spółkę do edycji!")
                    return
                ticker = self.tree.item(selected[0])["values"][0]
            company = self.company_data.get_company(ticker)
            if company:
                EditWindow(self.root, company, self.company_data, self.update_table, lambda: None)
            else:
                logging.error(f"Nie znaleziono spółki {ticker} w pamięci")
                messagebox.showerror("Błąd", f"Spółka {ticker} nie istnieje!")
        except Exception as e:
            logging.error(f"Błąd podczas otwierania okna edycji: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się otworzyć okna edycji!")

    def delete_company(self) -> None:
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Błąd", "Wybierz spółkę do usunięcia!")
                return
            ticker = self.tree.item(selected[0])["values"][0]
            self.company_data.delete_company(ticker)
            self.update_table()
            if self.current_ticker == ticker:
                self.current_ticker = None
                self.hide_price_plot_window()
                self.hide_score_plot_window()
                self.hide_financial_plots()
                self.hide_revenue_plots()
                self.hide_details_window()
            logging.info(f"Usunięto spółkę {ticker} z tabelki")
        except Exception as e:
            logging.error(f"Błąd podczas usuwania spółki {ticker}: {str(e)}")
            messagebox.showerror("Błąd", "Nie udało się usunąć spółki!")
