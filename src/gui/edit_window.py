# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\src\gui\edit_window.py
import os
import json
import logging
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import pyperclip

from src.core.company_data import CompanyData
from src.core.utils import load_sector_config, format_number, parse_number
from src.core.phase_classifier import classify_phase
from src.core.logging_config import setup_logging
from src.core.sector_mapping import normalize_sector

setup_logging()


def _last_years(n: int = 5) -> list[int]:
    """Zwraca listę ostatnich n lat (malejąco), bazując na roku bieżącym."""
    year = datetime.now().year
    return [year - i for i in range(n)]


def _get_sectors() -> list[str]:
    """Zwraca listę dostępnych sektorów (tytułowane) na podstawie plików JSON."""
    try:
        sectors_dir = os.path.join("src", "core", "sectors")
        sectors = [
            f.replace(".json", "").title()
            for f in os.listdir(sectors_dir)
            if f.endswith(".json")
        ]
        return sorted(sectors)
    except Exception as e:
        logging.error(f"Błąd wczytywania sektorów: {e}")
        return []


def _get_phases(sector: str) -> list[str]:
    """Zwraca listę faz dla podanego sektora (na bazie konfiguracji sektorów)."""
    try:
        sector_config = load_sector_config(sector)
        if sector_config and "indicators" in sector_config:
            return list(sector_config["indicators"].keys())
        return []
    except Exception as e:
        logging.error(f"Błąd pobierania faz dla sektora {sector}: {e}")
        return []


class EditWindow:
    """
    Okno edycji danych spółki.

    Kluczowe założenia (zgodnie z wymaganiami):
    - Usunięte pojedyncze pole „Revenue” z sekcji głównej.
    - Dodane sekcje: „Przychody kwartalne” (Rok + Kwartał 1..4) i „Przychody roczne” (ostatnie 5 lat – dynamicznie).
    - Tooltipy po POLSKU (etykiety + checkboxy).
    - Przycisk „Kopiuj” przy każdym wskaźniku – kopiuje NAZWĘ wskaźnika (nie wartość).
    - Przycisk „Oblicz” tylko dla wskaźników, które można policzyć; inne nie mają tego przycisku.
    - „To, co wpisujesz, jest święte” – pamiętamy surowe wpisy użytkownika i przy ponownym otwarciu pokazujemy je bez nadpisywania formatowaniem.
    - Rozdzielenie raw_sector (prezentacja) i normalized_sector (zapis/klasyfikacja).
    """

    # Pola, które mają przycisk „Oblicz” (pozostałe – brak przycisku)
    CALCULABLE_FIELDS = {
        "PEG Ratio",              # = PE / Earnings Growth
        "Free Cash Flow Margin",  # = FCF / Revenue * 100
    }

    # Pola liczbowe (nie-procentowe), zapisywane jako string z kropką i 2 miejscami
    NUMERIC_FIELDS = {
        "Price", "Price Target", "PE Ratio", "Forward PE", "PEG Ratio",
        "Revenue Growth", "Gross Margin", "Debt / Equity Ratio",
        "Current Ratio", "ROE", "Free Cash Flow Margin", "EPS TTM",
        "PB Ratio", "PS Ratio", "Operating Margin", "Profit Margin",
        "Quick Ratio", "Cash Ratio", "Debt / FCF Ratio",
        "Earnings Growth", "EBITDA Margin", "ROIC", "User Growth",
        "Interest Coverage", "Net Debt / EBITDA", "Inventory Turnover",
        "Asset Turnover", "Operating Cash Flow", "Free Cash Flow",
        "FFO", "LTV", "R&D / Sales", "CAC / LTV",
    }

    TEXT_FIELDS = {"Company Name", "Sector", "Phase", "Analyst Consensus"}

    # Mapowanie etykieta → klucz JSON + tooltip PL
    FIELD_MAPPING = {
        "Company Name": {"json_key": "nazwa", "tooltip": "Pełna nazwa spółki (np. Apple Inc.)."},
        "Sector": {"json_key": "sektor", "tooltip": "Sektor działalności (np. Technologia)."},
        "Phase": {"json_key": "faza", "tooltip": "Faza rozwoju spółki (np. Wzrost, Dojrzałość)."},
        "Price": {"json_key": "cena", "tooltip": "Aktualna cena akcji."},
        "Price Target": {"json_key": "analyst_target_price", "tooltip": "Średnia cena docelowa wg analityków."},
        "PE Ratio": {"json_key": "pe_ratio", "tooltip": "Cena / Zysk (Price/Earnings)."},
        "Forward PE": {"json_key": "forward_pe", "tooltip": "Prognozowana cena / zysk (Forward P/E)."},
        "PEG Ratio": {"json_key": "peg_ratio", "tooltip": "P/E do wzrostu zysku (PEG)."},
        "Revenue Growth": {"json_key": "revenue_growth", "tooltip": "Roczny wzrost przychodów (%)."},
        "Gross Margin": {"json_key": "gross_margin", "tooltip": "Marża brutto (%)."},
        "Debt / Equity Ratio": {"json_key": "debt_equity", "tooltip": "Zadłużenie / Kapitał własny."},
        "Current Ratio": {"json_key": "current_ratio", "tooltip": "Aktywa bieżące / Zobowiązania bieżące."},
        "ROE": {"json_key": "roe", "tooltip": "Zwrot z kapitału własnego (%)."},
        "Free Cash Flow Margin": {"json_key": "free_cash_flow_margin", "tooltip": "FCF / Przychody * 100 (%)."},
        "EPS TTM": {"json_key": "eps_ttm", "tooltip": "Zysk na akcję (TTM)."},
        "PB Ratio": {"json_key": "price_to_book_ratio", "tooltip": "Cena / Wartość księgowa."},
        "PS Ratio": {"json_key": "price_to_sales_ratio", "tooltip": "Cena / Przychody na akcję."},
        "Operating Margin": {"json_key": "operating_margin", "tooltip": "Zysk operacyjny / Przychody * 100 (%)."},
        "Profit Margin": {"json_key": "profit_margin", "tooltip": "Zysk netto / Przychody * 100 (%)."},
        "Quick Ratio": {"json_key": "quick_ratio", "tooltip": "(Aktywa bieżące - Zapasy) / Zobowiązania bieżące."},
        "Cash Ratio": {"json_key": "cash_ratio", "tooltip": "Gotówka / Zobowiązania bieżące."},
        "Debt / FCF Ratio": {"json_key": "cash_flow_to_debt_ratio", "tooltip": "FCF / Dług (lub odwrotnie – zgodnie ze źródłem)."},
        "Analyst Consensus": {"json_key": "analyst_rating", "tooltip": "Średnia rekomendacja (Buy/Hold/Sell)."},
        "Earnings Growth": {"json_key": "earnings_growth", "tooltip": "Roczny wzrost zysków (%)."},
        "EBITDA Margin": {"json_key": "ebitda_margin", "tooltip": "EBITDA / Przychody * 100 (%)."},
        "ROIC": {"json_key": "roic", "tooltip": "Zwrot z zainwestowanego kapitału (%)."},
        "User Growth": {"json_key": "user_growth", "tooltip": "Wzrost liczby użytkowników (%)."},
        "Interest Coverage": {"json_key": "interest_coverage", "tooltip": "EBIT / Koszty odsetek."},
        "Net Debt / EBITDA": {"json_key": "net_debt_ebitda", "tooltip": "Dług netto / EBITDA."},
        "Inventory Turnover": {"json_key": "inventory_turnover", "tooltip": "Rotacja zapasów."},
        "Asset Turnover": {"json_key": "asset_turnover", "tooltip": "Rotacja aktywów."},
        "Operating Cash Flow": {"json_key": "operating_cash_flow", "tooltip": "Przepływy operacyjne (USD)."},
        "Free Cash Flow": {"json_key": "free_cash_flow", "tooltip": "Wolne przepływy pieniężne."},
        "FFO": {"json_key": "ffo", "tooltip": "Funds From Operations."},
        "LTV": {"json_key": "ltv", "tooltip": "Lifetime Value (wartość klienta)."},
        "R&D / Sales": {"json_key": "rnd_sales", "tooltip": "R&D / Przychody."},
        "CAC / LTV": {"json_key": "cac_ltv", "tooltip": "Koszt pozyskania klienta / Lifetime Value."},
    }

    def __init__(self, parent, company: dict, company_data: CompanyData, update_callback, update_plots_callback):
        self.parent = parent
        self.company = company.copy()
        self.company_data = company_data
        self.update_callback = update_callback
        self.update_plots_callback = update_plots_callback

        self.raw_values: dict[str, str] = {}
        self.entries: dict[str, ttk.Entry | ttk.Combobox] = {}
        self.labels: dict[str, ttk.Label] = {}
        self.copy_buttons: dict[str, ttk.Button] = {}
        self.manual_checkboxes: dict[str, ttk.Checkbutton] = {}
        self.var_checkboxes: dict[str, tk.BooleanVar] = {}
        self.calc_buttons: dict[str, ttk.Button] = {}
        self.quarter_rows: list[dict] = []
        self.year_entries: dict[int, ttk.Entry] = {}
        self.tooltip: tk.Toplevel | None = None

        # surowy sektor (pozycja do wyświetlania)
        ticker = self.company.get("ticker", "")
        self.raw_sector = ""
        try:
            if hasattr(self.company_data, "get_raw_sector"):
                self.raw_sector = self.company_data.get_raw_sector(ticker) or ""
        except Exception:
            self.raw_sector = ""
        if not self.raw_sector:
            self.raw_sector = self.company.get("sektor") or ""

        self.var_in_portfolio = tk.BooleanVar(value=self.company.get("is_in_portfolio", False))

        # --- OKNO I LAYOUT (UWAGA: brak mieszania pack/grid na tym samym kontenerze) ---
        self.window = tk.Toplevel(parent)
        self.window.title(f"Edytuj dane: {self.company.get('ticker', 'Brak tickera')}")
        # Minimalny, przejrzysty rozmiar – zapobiega efektowi „1 cm paska”
        self.window.minsize(980, 720)

        # Główny kontener
        main = ttk.Frame(self.window)
        main.pack(fill=tk.BOTH, expand=True)

        # Canvas + Scrollbar (sprawdzone podejście – unika zapadania się UI)
        canvas = tk.Canvas(main)
        vscroll = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = ttk.Frame(canvas)
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # ustaw szerokość wewnętrznej ramki na szerokość canvasa
            try:
                canvas.itemconfigure(inner_id, width=canvas.winfo_width())
            except Exception:
                pass

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_configure)

        # Checkbox „W portfelu”
        ttk.Checkbutton(inner, text="W portfelu", variable=self.var_in_portfolio).grid(
            row=0, column=0, columnspan=5, padx=8, pady=8, sticky="w"
        )

        # Sekcja pól podstawowych
        basic_frame = ttk.LabelFrame(inner, text="Dane podstawowe")
        basic_frame.grid(row=1, column=0, columnspan=5, padx=8, pady=(4, 10), sticky="ew")
        self._build_basic_fields(basic_frame)

        # Sekcja przychodów kwartalnych
        q_frame = ttk.LabelFrame(inner, text="Przychody kwartalne (Rok + Kwartał 1..4)")
        q_frame.grid(row=2, column=0, columnspan=5, padx=8, pady=(0, 10), sticky="ew")
        self._build_quarterly_section(q_frame)

        # Sekcja przychodów rocznych
        y_frame = ttk.LabelFrame(inner, text="Przychody roczne (ostatnie 5 lat)")
        y_frame.grid(row=3, column=0, columnspan=5, padx=8, pady=(0, 10), sticky="ew")
        self._build_yearly_section(y_frame)

        # Przyciski akcji
        btns = ttk.Frame(inner)
        btns.grid(row=4, column=0, columnspan=5, padx=8, pady=8, sticky="e")
        ttk.Button(btns, text="Zapisz", command=self.save_data).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btns, text="Zamknij", command=self.window.destroy).pack(side=tk.RIGHT)

        # Kolory na podstawie konfiguracji
        self.update_field_colors()

        # Geometria – bezpieczne wczytanie (nie zmniejszamy poniżej minsize)
        self.load_geometry()

        self.window.transient(parent)
        self.window.grab_set()
        self.window.update_idletasks()  # upewnia się, że layout się przeliczył

    # --------------------- Sekcje UI ---------------------

    def _build_basic_fields(self, container: ttk.Frame):
        row = 0
        for field, meta in self.FIELD_MAPPING.items():
            json_key = meta["json_key"]

            # Etykieta z tooltipem i klik do historii (historia wywoływana bezpiecznie)
            lbl = ttk.Label(container, text=field)
            lbl.grid(row=row, column=0, padx=6, pady=3, sticky="w")
            lbl.bind("<Enter>", lambda e, f=field: self._show_tooltip(e, self.FIELD_MAPPING[f]["tooltip"]))
            lbl.bind("<Leave>", lambda _e: self._hide_tooltip())
            lbl.bind("<Button-1>", lambda _e, f=field: self._show_indicator_history_safe(f))
            self.labels[field] = lbl

            # Pole wejściowe
            if field == "Sector":
                entry = ttk.Combobox(container, values=_get_sectors(), width=30, state="normal")
                # Do wyświetlania używamy raw_sector
                display_value = self.raw_sector or ""
                entry.set(display_value)
                entry.bind("<<ComboboxSelected>>", lambda _e: self.update_field_colors())
            elif field == "Phase":
                entry = ttk.Combobox(container, values=_get_phases(self.company.get("sektor") or "Technology"),
                                     width=30, state="normal")
                entry.bind("<<ComboboxSelected>>", lambda _e: self.update_field_colors())
                entry.insert(0, str(self.company.get("faza") or ""))
            else:
                entry = ttk.Entry(container, width=32)
                value = self.company.get(json_key, "")
                # jeżeli mamy surową wartość – pokaż ją
                raw_override = None
                try:
                    if hasattr(self.company_data, "get_raw_value"):
                        raw_override = self.company_data.get_raw_value(self.company.get("ticker", ""), json_key)
                except Exception:
                    raw_override = None

                if raw_override is not None:
                    display_value = raw_override
                elif value not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                    if json_key in {"market_cap", "operating_cash_flow", "free_cash_flow", "ffo", "ltv"}:
                        display_value = format_number(value)
                    else:
                        try:
                            display_value = f"{float(value):.2f}"
                        except Exception:
                            display_value = str(value)
                else:
                    display_value = ""
                entry.insert(0, display_value)

            entry.grid(row=row, column=1, padx=6, pady=3, sticky="w")
            self.entries[field] = entry

            # Checkbox „Ręczne”
            self.var_checkboxes[field] = tk.BooleanVar(value=self.company.get(f"is_manual_{json_key}", False))
            chk = ttk.Checkbutton(container, text="Ręczne", variable=self.var_checkboxes[field])
            chk.grid(row=row, column=2, padx=6, pady=3, sticky="w")
            chk.bind("<Enter>", lambda e, f=field: self._show_tooltip(e, self.FIELD_MAPPING[f]["tooltip"]))
            chk.bind("<Leave>", lambda _e: self._hide_tooltip())
            self.manual_checkboxes[field] = chk

            # Przycisk „Oblicz” tylko dla wybranych wskaźników
            if field in self.CALCULABLE_FIELDS:
                btn = ttk.Button(container, text="Oblicz", command=lambda f=field: self._calculate_and_fill(f))
                btn.grid(row=row, column=3, padx=6, pady=3, sticky="w")
                self.calc_buttons[field] = btn

            # Przycisk „Kopiuj” – kopiuje NAZWĘ wskaźnika
            btnc = ttk.Button(container, text="Kopiuj", command=lambda f=field: pyperclip.copy(f))
            btnc.grid(row=row, column=4, padx=6, pady=3, sticky="w")
            self.copy_buttons[field] = btnc

            row += 1

    def _build_quarterly_section(self, container: ttk.Frame):
        headers = ("Rok", "Kwartał (1..4)", "Przychód", "Kopiuj")
        for c, h in enumerate(headers):
            ttk.Label(container, text=h).grid(row=0, column=c, padx=6, pady=4, sticky="w")

        existing = self.company.get("quarterly_revenue") or []

        def add_row(_year: int | None = None, _q: int | None = None, _rev: str | None = None):
            r = len(self.quarter_rows) + 1
            y_cb = ttk.Combobox(container, values=_last_years(10), width=10, state="normal")
            q_cb = ttk.Combobox(container, values=[1, 2, 3, 4], width=10, state="normal")
            e_rev = ttk.Entry(container, width=20)
            y_cb.grid(row=r, column=0, padx=6, pady=2, sticky="w")
            q_cb.grid(row=r, column=1, padx=6, pady=2, sticky="w")
            e_rev.grid(row=r, column=2, padx=6, pady=2, sticky="w")
            if _year: y_cb.set(str(_year))
            if _q: q_cb.set(str(_q))
            if _rev is not None: e_rev.insert(0, _rev)
            ttk.Button(container, text="Kopiuj", command=lambda: pyperclip.copy("Quarterly Revenue")).grid(
                row=r, column=3, padx=6, pady=2, sticky="w"
            )
            self.quarter_rows.append({"year": y_cb, "quarter": q_cb, "revenue": e_rev})

        # Inicjalizacja z danych
        if existing:
            for item in existing:
                try:
                    date = str(item.get("date") or "")
                    revenue = item.get("revenue")
                    year = None
                    quarter = None
                    if "-" in date:
                        y, rest = date.split("-", 1)
                        year = int(y)
                        rest = rest.upper().replace("Q", "").strip()
                        quarter = int(rest)
                    elif date.isdigit():
                        year = int(date)
                    add_row(year, quarter, (str(revenue) if revenue not in [None, "", "nan"] else ""))
                except Exception:
                    add_row(None, None, "")
        else:
            add_row()

        btns = ttk.Frame(container)
        btns.grid(row=999, column=0, columnspan=4, padx=6, pady=6, sticky="w")
        ttk.Button(btns, text="Dodaj wiersz", command=lambda: add_row()).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Wyczyść", command=self._clear_quarter_rows).pack(side=tk.LEFT, padx=4)

        container.bind(
            "<Enter>",
            lambda e: self._show_tooltip(
                e, "Wpisz przychody dla wybranego roku i kwartału (1..4). Zapis w formacie 'YYYY-Q#'."
            ),
        )
        container.bind("<Leave>", lambda _e: self._hide_tooltip())

    def _build_yearly_section(self, container: ttk.Frame):
        headers = ("Rok", "Przychód", "Kopiuj")
        for c, h in enumerate(headers):
            ttk.Label(container, text=h).grid(row=0, column=c, padx=6, pady=4, sticky="w")

        years = _last_years(5)
        existing = self.company.get("yearly_revenue") or []
        existing_map: dict[int, str] = {}
        for item in existing:
            try:
                d = str(item.get("date") or "")
                if d.isdigit():
                    existing_map[int(d)] = str(item.get("revenue") or "")
            except Exception:
                pass

        for i, yr in enumerate(years, start=1):
            ttk.Label(container, text=str(yr)).grid(row=i, column=0, padx=6, pady=2, sticky="w")
            e = ttk.Entry(container, width=22)
            e.grid(row=i, column=1, padx=6, pady=2, sticky="w")
            if yr in existing_map and existing_map[yr]:
                e.insert(0, existing_map[yr])
            self.year_entries[yr] = e
            ttk.Button(container, text="Kopiuj", command=lambda: pyperclip.copy("Yearly Revenue")).grid(
                row=i, column=2, padx=6, pady=2, sticky="w"
            )

        container.bind(
            "<Enter>",
            lambda e: self._show_tooltip(e, "Wpisz przychody roczne – dynamicznie pokazujemy ostatnie 5 lat."),
        )
        container.bind("<Leave>", lambda _e: self._hide_tooltip())

    # --------------------- Akcje pomocnicze ---------------------

    def _clear_quarter_rows(self):
        for r in self.quarter_rows:
            try:
                r["year"].set("")
                r["quarter"].set("")
                r["revenue"].delete(0, tk.END)
            except Exception:
                pass

    def _show_tooltip(self, event, text: str):
        if self.tooltip:
            self._hide_tooltip()
        self.tooltip = tk.Toplevel(self.window)
        self.tooltip.wm_overrideredirect(True)
        lines = (text or "").split("\n")
        width = max(len(line) for line in lines) * 6 + 14 if lines else 220
        height = len(lines) * 15 + 12
        self.tooltip.wm_geometry(f"{width}x{height}+{event.x_root + 10}+{event.y_root + 10}")
        label = tk.Label(
            self.tooltip, text=text, background="yellow",
            relief="solid", borderwidth=1, font=("Arial", 10), justify="left", padx=5, pady=4
        )
        label.pack()

    def _hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def _show_indicator_history_safe(self, field: str):
        """Bezpieczne wywołanie historii wskaźnika (jeśli CompanyData udostępnia metodę)."""
        try:
            if not hasattr(self.company_data, "load_company_history"):
                messagebox.showwarning("Brak funkcji", "Historia wskaźnika jest niedostępna w tej wersji.")
                return
            # Lazy import matplotlib, aby nie blokować GUI przy starcie
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            json_key = self.FIELD_MAPPING[field]["json_key"]
            hist = self.company_data.load_company_history(self.company["ticker"])
            if not hist:
                messagebox.showwarning("Brak danych", f"Brak danych historycznych dla {field}")
                return

            win = tk.Toplevel(self.window)
            win.title(f"Historia: {field} ({self.company['ticker']})")
            fig, ax = plt.subplots(figsize=(6, 4))
            xs, ys = [], []
            for entry in hist:
                v = entry.get(json_key)
                if v not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                    try:
                        ys.append(float(v))
                        xs.append(entry.get("date"))
                    except Exception:
                        pass
            if not ys:
                messagebox.showwarning("Brak danych", f"Brak ważnych danych historycznych dla {field}")
                win.destroy()
                return
            ax.plot(xs, ys, marker="o", label=field)
            ax.set_title(f"Historia: {field}")
            ax.set_xlabel("Data")
            ax.set_ylabel(field)
            ax.legend()
            ax.tick_params(axis="x", rotation=45)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=win)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()
        except Exception as e:
            logging.error(f"Błąd historii wskaźnika: {e}", exc_info=True)

    def update_field_colors(self):
        """Aktualizuje kolory pól i podkreślenia etykiet w zależności od fazy i konfiguracji sektora."""
        try:
            sector_text = (self.entries["Sector"].get() or "").strip()
            normalized_sector = normalize_sector(sector_text) if sector_text else None

            sectors_dir = os.path.join("src", "core", "sectors")
            valid_sectors = set()
            if os.path.isdir(sectors_dir):
                valid_sectors = {
                    f.replace(".json", "").lower()
                    for f in os.listdir(sectors_dir)
                    if f.endswith(".json")
                }

            if normalized_sector and normalized_sector.lower() not in valid_sectors:
                normalized_sector = None

            temp_company = self.company.copy()
            temp_company["sektor"] = normalized_sector

            # Faza: jeśli nie oznaczono ręcznie – wylicz automatycznie
            manual_phase = self.var_checkboxes.get("Phase")
            manual_phase_flag = bool(manual_phase.get()) if manual_phase else False
            if manual_phase_flag:
                faza = (self.entries["Phase"].get() or "").strip()
            else:
                faza = classify_phase(normalized_sector, temp_company) if normalized_sector else None
                if faza:
                    self.entries["Phase"].delete(0, tk.END)
                    self.entries["Phase"].insert(0, faza)

            main_indicators = []
            fallback_indicators = []
            phase_indicators = []
            if normalized_sector and faza:
                sector_config = load_sector_config(normalized_sector)
                if sector_config and faza in sector_config.get("indicators", {}):
                    phase_cfg = sector_config["indicators"][faza]
                    main_indicators = list(phase_cfg.get("main", []))
                    for ind in phase_cfg.get("fallback", {}):
                        fallback_indicators.extend(fb["indicator"] for fb in phase_cfg["fallback"][ind])
                if sector_config and "phase_classification" in sector_config:
                    for ph in sector_config["phase_classification"]:
                        for cond in sector_config["phase_classification"][ph]:
                            phase_indicators.append(cond["indicator"])

            # Kolory + podkreślenia
            for field, meta in self.FIELD_MAPPING.items():
                json_key = meta["json_key"]
                if json_key in main_indicators:
                    fg = "green"
                elif json_key in fallback_indicators:
                    fg = "orange"
                else:
                    fg = "black"
                try:
                    self.entries[field].configure(foreground=fg)
                except Exception:
                    pass
                try:
                    self.labels[field].configure(foreground=fg)
                except Exception:
                    pass
                # podkreślenie jeśli wskaźnik bierze udział w klasyfikacji faz
                try:
                    self.labels[field].configure(font=("Arial", 10, "underline" if json_key in phase_indicators else "normal"))
                except Exception:
                    pass

        except Exception as e:
            logging.error(f"Błąd update_field_colors: {e}", exc_info=True)

    # --------------------- Geometria okna ---------------------

    def load_geometry(self):
        """Wczytuje geometrię z pliku – łagodnie obsługuje brak/pusty/zepsuty plik."""
        try:
            path = "edit_window_geometry.json"
            if not os.path.isfile(path):
                # Domyślna, ale minsize i tak chroni przed „1 cm”
                self.window.geometry("980x720+80+60")
                return
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    logging.warning("Plik edit_window_geometry.json jest pusty – używam domyślnej geometrii.")
                    self.window.geometry("980x720+80+60")
                    return
                geometry = json.loads(content)
                w = int(geometry.get("width", 980))
                h = int(geometry.get("height", 720))
                x = int(geometry.get("x", 80))
                y = int(geometry.get("y", 60))
                # Nie schodzimy poniżej minsize
                w = max(w, 980)
                h = max(h, 720)
                self.window.geometry(f"{w}x{h}+{x}+{y}")
        except Exception as e:
            logging.error(f"Błąd wczytywania geometrii okna: {e}", exc_info=True)
            self.window.geometry("980x720+80+60")

    def save_geometry(self):
        """Zapisuje geometrię okna do pliku."""
        try:
            geometry = self.window.geometry()
            width, height, x, y = map(int, geometry.replace("x", "+").split("+"))
            with open("edit_window_geometry.json", "w", encoding="utf-8") as f:
                json.dump({"width": width, "height": height, "x": x, "y": y}, f, indent=4)
        except Exception as e:
            logging.error(f"Błąd zapisu geometrii: {e}", exc_info=True)

    # --------------------- Zapis danych ---------------------

    def save_data(self):
        """
        Zapisuje dane z okna edycji:
        - do JSON: wartości przetworzone (liczby jako string z kropką, 2 miejsca),
          sektor – znormalizowany jeśli istnieje w configach; inaczej None.
        - do cache (CompanyData): surowe wpisy użytkownika (dla ponownego wyświetlenia).
        - quarterly_revenue/yearly_revenue: listy obiektów {date, revenue}.
        """
        try:
            ticker = self.company.get("ticker", "")
            payload: dict = {"ticker": ticker}
            manual_flags: dict = {}
            indicator_colors: dict = {}
            raw_map_for_cache: dict[str, str] = {}

            for field, meta in self.FIELD_MAPPING.items():
                json_key = meta["json_key"]
                value = (self.entries[field].get() or "").strip()
                is_manual = bool(self.var_checkboxes[field].get())

                # puste
                if not value or value.lower() in {"none", "-", "na", "n/a", "--", "nan"}:
                    payload[json_key] = None
                    manual_flags[f"is_manual_{json_key}"] = False
                    indicator_colors[f"indicator_color_{json_key}"] = "black"
                    continue

                # teksty
                if field in self.TEXT_FIELDS:
                    if field == "Sector":
                        # zapamiętaj surowy sektor do późniejszego wyświetlania
                        self.raw_sector = value
                        try:
                            if hasattr(self.company_data, "store_raw_sector"):
                                self.company_data.store_raw_sector(ticker, self.raw_sector)
                        except Exception:
                            pass
                        # normalizacja + walidacja
                        norm = normalize_sector(value) if value else None
                        sectors_dir = os.path.join("src", "core", "sectors")
                        valid = set()
                        if os.path.isdir(sectors_dir):
                            valid = {
                                f.replace(".json", "").lower()
                                for f in os.listdir(sectors_dir)
                                if f.endswith(".json")
                            }
                        if norm and norm.lower() in valid:
                            payload[json_key] = norm
                        else:
                            payload[json_key] = None
                            try:
                                messagebox.showwarning("Ostrzeżenie", f"Sektor '{value}' nie jest zdefiniowany – zapisano None.")
                            except Exception:
                                pass
                    else:
                        payload[json_key] = value

                    manual_flags[f"is_manual_{json_key}"] = is_manual
                    indicator_colors[f"indicator_color_{json_key}"] = "blue" if is_manual else "black"
                    continue

                # liczby
                if field in self.NUMERIC_FIELDS:
                    raw_map_for_cache[json_key] = value  # do cache – surowy zapis (np. „1,2”)
                    try:
                        num = parse_number(value)
                    except ValueError:
                        payload[json_key] = None
                        manual_flags[f"is_manual_{json_key}"] = False
                        indicator_colors[f"indicator_color_{json_key}"] = "black"
                        try:
                            messagebox.showerror("Błąd", f"Nieprawidłowa liczba w polu '{field}': '{value}'")
                        except Exception:
                            pass
                        continue

                    # specjalna obsługa Debt/Equity – gdy użytkownik poda np. „1250” zamiast „12.5”
                    if json_key == "debt_equity" and num > 10.0:
                        num /= 100.0

                    payload[json_key] = f"{num:.2f}"
                    manual_flags[f"is_manual_{json_key}"] = is_manual
                    indicator_colors[f"indicator_color_{json_key}"] = "blue" if is_manual else "black"
                    continue

            # Zapis surowych wartości do cache (dla zachowania oryginalnej prezentacji)
            try:
                if hasattr(self.company_data, "store_raw_values"):
                    self.company_data.store_raw_values(ticker, raw_map_for_cache)
            except Exception:
                pass

            # Przychody kwartalne
            q_list = []
            for row in self.quarter_rows:
                year_str = (row["year"].get() or "").strip()
                q_str = (row["quarter"].get() or "").strip()
                rev_str = (row["revenue"].get() or "").strip()
                if not rev_str:
                    continue
                try:
                    rev = parse_number(rev_str)
                except ValueError:
                    continue
                date_str = None
                if year_str and q_str:
                    try:
                        y = int(year_str)
                        q = int(q_str)
                        if 1 <= q <= 4:
                            date_str = f"{y}-Q{q}"
                    except Exception:
                        date_str = None
                elif year_str:
                    date_str = year_str
                if date_str:
                    q_list.append({"date": date_str, "revenue": f"{rev:.2f}", "is_manual": False})
            if q_list:
                payload["quarterly_revenue"] = q_list

            # Przychody roczne (ostatnie 5 lat)
            y_list = []
            for yr, entry in self.year_entries.items():
                val = (entry.get() or "").strip()
                if not val:
                    continue
                try:
                    rev = parse_number(val)
                except ValueError:
                    continue
                y_list.append({"date": str(yr), "revenue": f"{rev:.2f}", "is_manual": False})
            if y_list:
                payload["yearly_revenue"] = y_list

            # flaga portfela
            payload["is_in_portfolio"] = bool(self.company.get("is_in_portfolio", False) or self.var_in_portfolio.get())

            # scal i zapisz
            payload.update(manual_flags)
            payload.update(indicator_colors)

            self.company_data.save_company_data(ticker, payload)

            # odświeżenia i info
            try:
                if callable(self.update_callback):
                    self.update_callback()
                if callable(self.update_plots_callback):
                    self.update_plots_callback()
                messagebox.showinfo("OK", "Dane zapisane.")
            except Exception:
                pass

            # zapisz geometrię (zostawiamy okno otwarte do dalszej edycji)
            self.save_geometry()

        except Exception as e:
            logging.error(f"Błąd zapisu danych w EditWindow: {e}", exc_info=True)
            try:
                messagebox.showerror("Błąd", f"Nie udało się zapisać danych: {e}")
            except Exception:
                pass

    # --------------------- Kalkulacje wskaźników ---------------------

    def _calculate_and_fill(self, field: str):
        """Wywołuje kalkulator wskaźników dla wybranych pól (tylko CALCULABLE_FIELDS)."""
        try:
            # Lazy import aby uniknąć ciężkich zależności przy starcie
            from src.gui.indicator_calculator import calculate_indicator
        except Exception as e:
            logging.error(f"Brak modułu kalkulatora wskaźników: {e}")
            return

        if field not in self.CALCULABLE_FIELDS:
            return

        try:
            value = calculate_indicator(self.window, field, self.entries)
            if value is not None:
                self.entries[field].delete(0, tk.END)
                try:
                    self.entries[field].insert(0, f"{float(value):.2f}")
                except Exception:
                    self.entries[field].insert(0, str(value))
                # oznacz jako ręczne
                self.var_checkboxes[field].set(True)
        except Exception as e:
            logging.error(f"Błąd kalkulacji dla {field}: {e}", exc_info=True)
