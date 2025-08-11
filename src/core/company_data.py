# ŚCIEŻKA: src/core/company_data.py (MERGED FULL FEATURE SET)
from __future__ import annotations

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

from src.api.api_fetcher import fetch_data
from src.core.logging_config import setup_logging
from src.core.sector_mapping import normalize_sector

setup_logging()


class CompanyData:
    def __init__(self):
        """
        Inicjalizuje obiekt przechowujący dane spółek.
        - zachowuje wszystkie istniejące funkcjonalności (cache surowych wartości, walidacje, load/save, fetch, itp.)
        - DODANE: metody serii do wykresów: get_price_series / get_score_series / get_financials_series
        """
        # Cache na surowe wpisy użytkownika (tylko w pamięci bieżącej sesji)
        self.raw_values_cache: Dict[str, Dict[str, str]] = {}
        self.raw_sector_cache: Dict[str, str] = {}
        self.data_dir = "data"
        self.companies: List[dict] = []

        if not os.path.exists(self.data_dir):
            try:
                os.makedirs(self.data_dir)
                logging.info(f"Utworzono katalog danych: {self.data_dir}")
            except Exception as e:
                logging.error(f"Błąd tworzenia katalogu danych {self.data_dir}: {str(e)}")
                raise

        # kompatybilnie z Twoimi wcześniejszymi wersjami
        self.load_companies()

    # ---------------------------------------------------------------------
    # POMOCNICZE
    # ---------------------------------------------------------------------
    def _safe_float(self, v: Any) -> Optional[float]:
        try:
            if v in [None, "", "-", "NA", "N/A", "None", "nan"]:
                return None
            return float(v)
        except Exception:
            return None

    def _history_path(self, ticker: str) -> str:
        return os.path.join(self.data_dir, f"{ticker.upper()}.json")

    def _load_history_file(self, ticker: str) -> List[dict]:
        file_path = self._history_path(ticker)
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
                if isinstance(history, list):
                    return history
                logging.warning(f"Nieprawidłowy format pliku historycznego dla {ticker}: {type(history)}")
                return []
        except json.JSONDecodeError:
            logging.error(f"Uszkodzony JSON w {file_path}")
            return []
        except Exception as e:
            logging.error(f"Błąd wczytywania pliku {file_path}: {e}")
            return []

    # ---------------------------------------------------------------------
    # ŁADOWANIE LISTY SPÓŁEK
    # ---------------------------------------------------------------------
    def load_companies(self) -> None:
        """
        Wczytuje listę spółek z folderu data.
        (wersja łączona – zachowuje logikę walidacji, kolorów i flag ręcznych)
        """
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            self.companies = []

            sectors_dir = os.path.join("src", "core", "sectors")
            valid_sectors = set()
            if os.path.isdir(sectors_dir):
                valid_sectors = {f.replace(".json", "").lower() for f in os.listdir(sectors_dir) if f.endswith(".json")}

            for file_name in os.listdir(self.data_dir):
                if file_name.endswith(".json") and not file_name.startswith(("technology", "financials", "biotechnology", "test-sector")):
                    ticker = file_name[:-5].upper()
                    file_path = os.path.join(self.data_dir, f"{ticker}.json")
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            history = json.load(f)
                            if history and isinstance(history, list) and len(history) > 0:
                                latest = history[-1]
                                if isinstance(latest, dict) and "ticker" in latest:
                                    company = {
                                        "ticker": latest.get("ticker", ticker),
                                        "nazwa": latest.get("nazwa"),
                                        "sektor": latest.get("sektor") if (latest.get("sektor") or "").lower() in valid_sectors else None,
                                        "faza": latest.get("faza"),
                                        "cena": latest.get("cena"),
                                        "pe_ratio": latest.get("pe_ratio"),
                                        "forward_pe": latest.get("forward_pe"),
                                        "peg_ratio": latest.get("peg_ratio"),
                                        "revenue_growth": latest.get("revenue_growth"),
                                        "gross_margin": latest.get("gross_margin"),
                                        "debt_equity": latest.get("debt_equity"),
                                        "current_ratio": latest.get("current_ratio"),
                                        "roe": latest.get("roe"),
                                        "free_cash_flow_margin": latest.get("free_cash_flow_margin"),
                                        "eps_ttm": latest.get("eps_ttm"),
                                        "price_to_book_ratio": latest.get("price_to_book_ratio"),
                                        "price_to_sales_ratio": latest.get("price_to_sales_ratio"),
                                        "operating_margin": latest.get("operating_margin"),
                                        "profit_margin": latest.get("profit_margin"),
                                        "quick_ratio": latest.get("quick_ratio"),
                                        "cash_ratio": latest.get("cash_ratio"),
                                        "cash_flow_to_debt_ratio": latest.get("cash_flow_to_debt_ratio"),
                                        "earnings_growth": latest.get("earnings_growth"),
                                        "analyst_target_price": latest.get("analyst_target_price"),
                                        "analyst_rating": latest.get("analyst_rating"),
                                        "punkty": latest.get("punkty"),
                                        "market_cap": latest.get("market_cap"),
                                        "revenue": latest.get("revenue"),
                                        "ebitda_margin": latest.get("ebitda_margin"),
                                        "roic": latest.get("roic"),
                                        "user_growth": latest.get("user_growth"),
                                        "interest_coverage": latest.get("interest_coverage"),
                                        "net_debt_ebitda": latest.get("net_debt_ebitda"),
                                        "inventory_turnover": latest.get("inventory_turnover"),
                                        "asset_turnover": latest.get("asset_turnover"),
                                        "operating_cash_flow": latest.get("operating_cash_flow"),
                                        "free_cash_flow": latest.get("free_cash_flow"),
                                        "ffo": latest.get("ffo"),
                                        "ltv": latest.get("ltv"),
                                        "rnd_sales": latest.get("rnd_sales"),
                                        "cac_ltv": latest.get("cac_ltv"),
                                        "faza_history": latest.get("faza_history", []),
                                        "quarterly_revenue": latest.get("quarterly_revenue", []),
                                        "yearly_revenue": latest.get("yearly_revenue", []),
                                        "is_in_portfolio": latest.get("is_in_portfolio", False),
                                        "date": latest.get("date", datetime.now().strftime("%Y-%m-%d")),
                                        # flagi manualne (domyślnie False, jeśli brak)
                                        **{f"is_manual_{k}": latest.get(f"is_manual_{k}", False) for k in [
                                            "nazwa","sektor","faza","cena","pe_ratio","forward_pe","peg_ratio",
                                            "revenue_growth","gross_margin","debt_equity","current_ratio","roe",
                                            "free_cash_flow_margin","eps_ttm","price_to_book_ratio","price_to_sales_ratio",
                                            "operating_margin","profit_margin","quick_ratio","cash_ratio","cash_flow_to_debt_ratio",
                                            "earnings_growth","analyst_target_price","analyst_rating","market_cap","revenue",
                                            "ebitda_margin","roic","user_growth","interest_coverage","net_debt_ebitda",
                                            "inventory_turnover","asset_turnover","operating_cash_flow","free_cash_flow",
                                            "ffo","ltv","rnd_sales","cac_ltv"
                                        ]}
                                    }
                                    # sanity/normalizacja bieżącego snapshotu
                                    for key, value in list(latest.items()):
                                        if value in ["None", "-", "NA", "nan", None]:
                                            latest[key] = None
                                        elif key == "sektor" and value:
                                            normalized_sector = normalize_sector(value) if value else None
                                            if normalized_sector and normalized_sector.lower() in valid_sectors:
                                                latest[key] = normalized_sector
                                            else:
                                                logging.warning(f"Nieprawidłowy sektor {value} dla {ticker}, ustawiono None")
                                                latest[key] = None
                                        elif key in [
                                            "cena", "pe_ratio", "forward_pe", "peg_ratio",
                                            "revenue_growth", "gross_margin", "debt_equity",
                                            "current_ratio", "roe", "free_cash_flow_margin",
                                            "eps_ttm", "price_to_book_ratio", "price_to_sales_ratio",
                                            "operating_margin", "profit_margin", "quick_ratio",
                                            "cash_ratio", "cash_flow_to_debt_ratio", "earnings_growth",
                                            "analyst_target_price", "market_cap", "revenue",
                                            "ebitda_margin", "roic", "user_growth", "interest_coverage",
                                            "net_debt_ebitda", "inventory_turnover", "asset_turnover",
                                            "operating_cash_flow", "free_cash_flow", "ffo", "ltv",
                                            "rnd_sales", "cac_ltv"
                                        ] and value is not None:
                                            try:
                                                valf = float(value)
                                                if key == "debt_equity" and valf > 10.0:
                                                    valf /= 100.0
                                                latest[key] = f"{valf:.2f}"
                                            except (ValueError, TypeError):
                                                logging.warning(f"Nieprawidłowa wartość {key}={value} dla {ticker}, ustawiono None")
                                                latest[key] = None
                                        elif key in ["quarterly_revenue", "yearly_revenue"] and isinstance(value, list):
                                            for item in value:
                                                if isinstance(item, dict) and "revenue" in item and item["revenue"] not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                                                    try:
                                                        item["revenue"] = f"{float(item['revenue']):.2f}"
                                                        item["is_manual"] = item.get("is_manual", False)
                                                    except (ValueError, TypeError):
                                                        logging.warning(f"Nieprawidłowa wartość przychodu dla {ticker}, data {item.get('date')}")
                                                        item["revenue"] = None
                                            latest[key] = value
                                    company.update(latest)
                                    self.companies.append(company)
                    except Exception as e:
                        logging.error(f"Błąd wczytywania spółki z pliku {file_path}: {str(e)}")
        except PermissionError as e:
            logging.error(f"Brak uprawnień do odczytu folderu {self.data_dir}: {str(e)}")
        except Exception as e:
            logging.error(f"Błąd podczas wczytywania spółek: {str(e)}")

    # alias dla wstecznej kompatybilności
    def load_all_companies(self):
        self.load_companies()

    # ---------------------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------------------
    def add_company(self, ticker: str) -> None:
        """
        Dodaje nową spółkę i tworzy plik JSON z podstawowym wpisem.
        """
        try:
            ticker = ticker.upper()
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            file_path = self._history_path(ticker)
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                self.companies.append({
                    "ticker": ticker,
                    "nazwa": None,
                    "sektor": None,
                    "faza": None,
                    "cena": None,
                    "pe_ratio": None,
                    "forward_pe": None,
                    "peg_ratio": None,
                    "revenue_growth": None,
                    "gross_margin": None,
                    "debt_equity": None,
                    "current_ratio": None,
                    "roe": None,
                    "free_cash_flow_margin": None,
                    "eps_ttm": None,
                    "price_to_book_ratio": None,
                    "price_to_sales_ratio": None,
                    "operating_margin": None,
                    "profit_margin": None,
                    "quick_ratio": None,
                    "cash_ratio": None,
                    "cash_flow_to_debt_ratio": None,
                    "earnings_growth": None,
                    "analyst_target_price": None,
                    "analyst_rating": None,
                    "punkty": None,
                    "market_cap": None,
                    "revenue": None,
                    "ebitda_margin": None,
                    "roic": None,
                    "user_growth": None,
                    "interest_coverage": None,
                    "net_debt_ebitda": None,
                    "inventory_turnover": None,
                    "asset_turnover": None,
                    "operating_cash_flow": None,
                    "free_cash_flow": None,
                    "ffo": None,
                    "ltv": None,
                    "rnd_sales": None,
                    "cac_ltv": None,
                    "faza_history": [],
                    "quarterly_revenue": [],
                    "yearly_revenue": [],
                    "is_in_portfolio": False,
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                logging.info(f"Utworzono nową spółkę {ticker} i plik {file_path}")
            else:
                logging.warning(f"Plik {file_path} już istnieje")
        except PermissionError as e:
            logging.error(f"Brak uprawnień do utworzenia pliku dla {ticker}: {str(e)}")
        except Exception as e:
            logging.error(f"Błąd podczas dodawania spółki {ticker}: {str(e)}")

    def get_company(self, ticker: str) -> Optional[dict]:
        """Zwraca najnowszy rekord danych spółki."""
        try:
            ticker = ticker.upper()
            for c in self.companies:
                if c.get("ticker") == ticker:
                    return c
            return None
        except Exception as e:
            logging.error(f"Błąd get_company({ticker}): {str(e)}")
            return None

    def delete_company(self, ticker: str) -> None:
        """Usuwa spółkę i jej plik JSON."""
        try:
            ticker = ticker.upper()
            file_path = self._history_path(ticker)
            self.companies = [c for c in self.companies if c.get("ticker") != ticker]
            if os.path.exists(file_path):
                os.remove(file_path)
            logging.info(f"Usunięto spółkę {ticker}")
        except PermissionError as e:
            logging.error(f"Brak uprawnień do usunięcia {ticker}: {str(e)}")
        except Exception as e:
            logging.error(f"Błąd podczas usuwania spółki {ticker}: {str(e)}")

    # ---------------------------------------------------------------------
    # ZAPIS / WALIDACJA
    # ---------------------------------------------------------------------
    def save_company_data(self, ticker: str, data: dict):
        """
        Zapisuje dane spółki do pliku JSON z walidacją formatu i nadpisywaniem danych dla tego samego dnia.
        (z Twojej nowszej wersji – uzupełnione o wszelkie pola + flagi)
        """
        try:
            ticker = ticker.upper()
            file_path = self._history_path(ticker)
            today = data.get("date", datetime.now().strftime("%Y-%m-%d")) or datetime.now().strftime("%Y-%m-%d")

            sectors_dir = os.path.join("src", "core", "sectors")
            valid_sectors = set()
            if os.path.isdir(sectors_dir):
                valid_sectors = {f.replace(".json", "").lower() for f in os.listdir(sectors_dir) if f.endswith(".json")}

            # Normalizacja i walidacja sektora (logika zgodna z Twoją implementacją)
            if "sektor" in data and data["sektor"]:
                normalized_sector = normalize_sector(data["sektor"])  # mapowanie wg konfiguracji
                if normalized_sector and normalized_sector.lower() in valid_sectors:
                    data["sektor"] = normalized_sector
                else:
                    data["sektor"] = None
            else:
                data["sektor"] = None

            # Pola procentowe – tylko PRAWDZIWE procenty
            percent_fields = [
                "revenue_growth", "gross_margin", "ebitda_margin",
                "operating_margin", "profit_margin", "roe",
                "free_cash_flow_margin", "roic", "user_growth"
            ]

            # Pola liczbowe (nie mnożymy przez 100)
            numeric_fields = [
                "cena", "pe_ratio", "forward_pe", "peg_ratio", "eps_ttm",
                "price_to_book_ratio", "price_to_sales_ratio", "current_ratio",
                "quick_ratio", "cash_ratio", "cash_flow_to_debt_ratio",
                "earnings_growth", "analyst_target_price", "market_cap",
                "revenue", "operating_cash_flow", "free_cash_flow", "ffo", "ltv",
                # dodatkowe – jak w Twojej wersji
                "interest_coverage", "net_debt_ebitda", "inventory_turnover",
                "asset_turnover", "cac_ltv", "rnd_sales",
                # warunkowa normalizacja
                "debt_equity",
            ]

            for field in percent_fields:
                if field in data and data[field] not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                    try:
                        value = float(data[field])
                        if value <= 1.0:  # jeśli przychodzi ułamek, przeliczamy na %
                            value *= 100
                        data[field] = f"{value:.2f}"
                    except (ValueError, TypeError):
                        logging.warning(f"Nieprawidłowa wartość procentowa {field}={data[field]} dla {ticker}, ustawiono None")
                        data[field] = None

            for field in numeric_fields:
                if field in data and data[field] not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                    try:
                        value = float(data[field])
                        if field == "debt_equity" and value > 10.0:
                            # niektóre API zwracają 250 (=250%), normalizujemy do 2.5
                            value /= 100.0
                        data[field] = f"{value:.2f}"
                    except (ValueError, TypeError):
                        logging.warning(f"Nieprawidłowa wartość liczbowa {field}={data[field]} dla {ticker}, ustawiono None")
                        data[field] = None

            # Obsługa przychodów kwartalnych/rocznych (opcjonalna)
            if isinstance(data.get("quarterly_revenue"), list):
                data["quarterly_revenue"] = [
                    {
                        "date": item.get("date"),
                        "revenue": f"{float(item.get('revenue', 0.0)):.2f}" if item.get("revenue") not in [None, "", "-", "NA", "N/A", "None", "nan"] else None,
                        "is_manual": item.get("is_manual", False)
                    }
                    for item in data["quarterly_revenue"]
                    if isinstance(item, dict) and "date" in item and "revenue" in item
                ]

            if isinstance(data.get("yearly_revenue"), list):
                data["yearly_revenue"] = [
                    {
                        "date": item.get("date"),
                        "revenue": f"{float(item.get('revenue', 0.0)):.2f}" if item.get("revenue") not in [None, "", "-", "NA", "N/A", "None", "nan"] else None,
                        "is_manual": item.get("is_manual", False)
                    }
                    for item in data["yearly_revenue"]
                    if isinstance(item, dict) and "date" in item and "revenue" in item
                ]

            # Dynamiczne kopiowanie wszystkich kluczy z danymi
            data_copy = {
                "ticker": ticker,
                "date": today,
                "is_in_portfolio": data.get("is_in_portfolio", False),
            }
            required_keys = [
                "nazwa", "sektor", "faza", "cena", "pe_ratio", "forward_pe",
                "peg_ratio", "revenue_growth", "gross_margin", "debt_equity",
                "current_ratio", "roe", "free_cash_flow_margin", "eps_ttm",
                "price_to_book_ratio", "price_to_sales_ratio", "operating_margin",
                "profit_margin", "quick_ratio", "cash_ratio",
                "cash_flow_to_debt_ratio", "earnings_growth", "analyst_target_price",
                "analyst_rating", "punkty", "market_cap", "revenue",
                "ebitda_margin", "roic", "user_growth", "interest_coverage",
                "net_debt_ebitda", "inventory_turnover", "asset_turnover",
                "operating_cash_flow", "free_cash_flow", "ffo", "ltv", "rnd_sales",
                "cac_ltv", "quarterly_revenue", "yearly_revenue"
            ]
            for key in required_keys:
                data_copy[key] = data.get(key, None)
                # flaga ręczna dla każdego wskaźnika (domyślnie False)
                data_copy[f"is_manual_{key}"] = data.get(f"is_manual_{key}", False)
                data_copy[f"indicator_color_{key}"] = data.get(f"indicator_color_{key}", "black")

            # Wczytaj historię
            history: List[dict] = []
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        history = json.load(f)
                        if not isinstance(history, list):
                            history = []
                except json.JSONDecodeError:
                    logging.error(f"Uszkodzony JSON w {file_path}, tworzę nowy")
                    history = []

            # Nadpisanie wpisu dla tej samej daty
            replaced = False
            for i, item in enumerate(history):
                if isinstance(item, dict) and item.get("date") == today:
                    history[i] = data_copy
                    replaced = True
                    break
            if not replaced:
                history.append(data_copy)

            # sortuj po dacie (string YYYY-MM-DD jest OK)
            history = sorted(history, key=lambda x: x.get("date", ""))

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=4)

            # Aktualizacja w pamięci
            found = False
            for i, c in enumerate(self.companies):
                if c.get("ticker") == ticker:
                    latest = self.companies[i]
                    for key, value in data_copy.items():
                        if key in [
                            "nazwa", "sektor", "faza", "cena", "pe_ratio", "forward_pe",
                            "peg_ratio", "revenue_growth", "gross_margin", "debt_equity",
                            "current_ratio", "roe", "free_cash_flow_margin", "eps_ttm",
                            "price_to_book_ratio", "price_to_sales_ratio", "operating_margin",
                            "profit_margin", "quick_ratio", "cash_ratio", "cash_flow_to_debt_ratio",
                            "earnings_growth", "analyst_target_price", "analyst_rating",
                            "punkty", "market_cap", "revenue", "ebitda_margin", "roic", "user_growth",
                            "interest_coverage", "net_debt_ebitda", "inventory_turnover",
                            "asset_turnover", "operating_cash_flow", "free_cash_flow",
                            "ffo", "ltv", "rnd_sales", "cac_ltv",
                            "quarterly_revenue", "yearly_revenue"
                        ]:
                            latest[key] = value
                        elif key in ["is_in_portfolio", "date"]:
                            latest[key] = value
                        # flagi i kolory
                        latest[f"is_manual_{key}"] = data_copy.get(f"is_manual_{key}", latest.get(f"is_manual_{key}", False))
                        latest[f"indicator_color_{key}"] = data_copy.get(f"indicator_color_{key}", latest.get(f"indicator_color_{key}", "black"))
                    self.companies[i] = latest
                    found = True
                    break
            if not found:
                self.companies.append(data_copy)
            logging.info(f"Zapisano dane dla {ticker} do {file_path}")
        except PermissionError as e:
            logging.error(f"Brak uprawnień do zapisu danych {ticker}: {str(e)}")
        except Exception as e:
            logging.error(f"Błąd podczas zapisu danych {ticker}: {str(e)}", exc_info=True)

    # ---------------------------------------------------------------------
    # POBIERANIE DANYCH Z API
    # ---------------------------------------------------------------------
    def fetch_and_save(self, ticker: str, api_sources: List[str]) -> None:
        """Pobiera dane z podanych API i zapisuje wynik (pojedynczy ticker)."""
        try:
            data = fetch_data(ticker, api_sources)
            if data:
                self.save_company_data(ticker, data)
        except Exception as e:
            logging.error(f"Błąd fetch_and_save dla {ticker}: {str(e)}")

    # Wersja wielotickerowa – zachowana z Twojej starszej wersji
    def fetch_data(self, tickers: List[str], parent=None, data_type: str = "company") -> Tuple[Dict, Dict]:
        """
        Pobiera dane z API dla listy tickerów, respektując flagi 'is_manual_*' i uzupełniając sektor z historii.
        Zwraca (wyniki, brakujące tickery).
        """
        try:
            valid_sectors = {f.replace(".json", "").lower() for f in os.listdir(os.path.join("src", "core", "sectors")) if f.endswith(".json")}
            required_keys = [
                "nazwa", "sektor", "faza", "cena", "pe_ratio", "forward_pe",
                "peg_ratio", "revenue_growth", "gross_margin", "debt_equity",
                "current_ratio", "roe", "free_cash_flow_margin", "eps_ttm",
                "price_to_book_ratio", "price_to_sales_ratio", "operating_margin",
                "profit_margin", "quick_ratio", "cash_ratio",
                "cash_flow_to_debt_ratio", "earnings_growth", "analyst_target_price",
                "analyst_rating", "punkty", "market_cap", "revenue",
                "ebitda_margin", "roic", "user_growth", "interest_coverage",
                "net_debt_ebitda", "inventory_turnover", "asset_turnover",
                "operating_cash_flow", "free_cash_flow", "ffo", "ltv", "rnd_sales",
                "cac_ltv", "quarterly_revenue", "yearly_revenue"
            ] if data_type != "macro" else ["nazwa", "value"]

            results, missing_tickers = fetch_data(tickers, parent, data_type)

            for ticker in results:
                ticker = ticker.upper()
                existing_company = self.get_company(ticker)
                updated_data = {
                    "ticker": ticker,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "is_in_portfolio": existing_company.get("is_in_portfolio", False) if existing_company else False
                }
                # Dynamicznie kopiuj wszystkie klucze z wyników API
                for key, value in results[ticker].items():
                    updated_data[key] = value
                    updated_data[f"is_manual_{key}"] = existing_company.get(f"is_manual_{key}", False) if existing_company else False
                    updated_data[f"indicator_color_{key}"] = existing_company.get(f"indicator_color_{key}", "black") if existing_company else "black"

                # Zachowaj ręczne dane z istniejącej spółki
                if existing_company:
                    for key in required_keys:
                        if existing_company.get(f"is_manual_{key}", False):
                            updated_data[key] = existing_company.get(key)
                            updated_data[f"is_manual_{key}"] = True
                            updated_data[f"indicator_color_{key}"] = existing_company.get(f"indicator_color_{key}", "black")

                # Uzupełnij sektor z historii, jeśli brak danych z API i nie jest ręczny
                if not updated_data.get("sektor") and not updated_data.get("is_manual_sektor", False):
                    history = self.load_company_history(ticker)
                    if history:
                        last_entry = history[-1]
                        last_sector = last_entry.get("sektor")
                        if last_sector and last_sector.lower() in valid_sectors:
                            updated_data["sektor"] = last_sector
                            logging.info(f"Uzupełniono sektor dla {ticker} z historii: {last_sector}")

                self.save_company_data(ticker, updated_data)

            logging.info(f"Pobrano dane dla {tickers}, brakujące: {list(missing_tickers.keys())}")
            return results, missing_tickers
        except Exception as e:
            logging.error(f"Błąd podczas pobierania danych z API dla {tickers}: {str(e)}")
            return {}, {ticker: ["all"] for ticker in tickers}

    # ---------------------------------------------------------------------
    # HISTORIA / SERIE DO WYKRESÓW
    # ---------------------------------------------------------------------
    def load_company_history(self, ticker: str) -> List[dict]:
        """
        Wczytuje historię danych dla danej spółki i zwraca listę wpisów (słowników) posortowaną po dacie.
        ZACHOWANA identyczna sygnatura i zachowanie jak w Twojej starszej wersji.
        """
        try:
            history = self._load_history_file(ticker)
            if not history:
                return []
            # normalizacja przychodów – tak jak w Twojej implementacji
            for entry in history:
                if "quarterly_revenue" in entry and isinstance(entry["quarterly_revenue"], list):
                    entry["quarterly_revenue"] = [
                        {
                            "date": item["date"],
                            "revenue": f"{float(item['revenue']):.2f}" if item["revenue"] not in [None, "", "-", "NA", "N/A", "None", "nan"] else None,
                            "is_manual": item.get("is_manual", False)
                        }
                        for item in entry["quarterly_revenue"]
                        if isinstance(item, dict) and "date" in item and "revenue" in item
                    ]
                if "yearly_revenue" in entry and isinstance(entry["yearly_revenue"], list):
                    entry["yearly_revenue"] = [
                        {
                            "date": item["date"],
                            "revenue": f"{float(item['revenue']):.2f}" if item["revenue"] not in [None, "", "-", "NA", "N/A", "None", "nan"] else None,
                            "is_manual": item.get("is_manual", False)
                        }
                        for item in entry["yearly_revenue"]
                        if isinstance(item, dict) and "date" in item and "revenue" in item
                    ]
            return sorted(history, key=lambda x: x.get("date", ""))
        except Exception as e:
            logging.error(f"Błąd podczas wczytywania historii dla {ticker}: {str(e)}")
            return []

    # NOWE – lekkie serie gotowe do wykresów (bez ruszania load_company_history)
    def get_price_series(self, ticker: str) -> List[Tuple[datetime, Optional[float]]]:
        """Zwraca listę (data_datetime, cena_float|None) posortowaną po dacie."""
        series: List[Tuple[datetime, Optional[float]]] = []
        for entry in self.load_company_history(ticker):
            ds = entry.get("date")
            if not ds:
                continue
            try:
                dt = datetime.fromisoformat(ds)
            except Exception:
                try:
                    dt = datetime.strptime(ds[:10], "%Y-%m-%d")
                except Exception:
                    continue
            price = self._safe_float(entry.get("cena"))
            series.append((dt, price))
        series.sort(key=lambda x: x[0])
        return series

    def get_score_series(self, ticker: str) -> List[Tuple[datetime, Optional[float]]]:
        """Zwraca listę (data_datetime, punkty_float|None) posortowaną po dacie."""
        out: List[Tuple[datetime, Optional[float]]] = []
        for entry in self.load_company_history(ticker):
            ds = entry.get("date")
            if not ds:
                continue
            try:
                dt = datetime.fromisoformat(ds)
            except Exception:
                try:
                    dt = datetime.strptime(ds[:10], "%Y-%m-%d")
                except Exception:
                    continue
            pts = self._safe_float(entry.get("punkty"))
            out.append((dt, pts))
        out.sort(key=lambda x: x[0])
        return out

    def get_financials_series(self, ticker: str) -> Dict[str, List[Tuple[str, float]]]:
        """
        Zwraca struktury do wykresów słupkowych finansów:
          {
            'quarterly_revenue': [(etykieta, wartość_float), ...],
            'yearly_revenue':    [(etykieta, wartość_float), ...]
          }
        Dane bierzemy z NAJNOWSZEGO wpisu w historii (tak jak w GUI).
        """
        history = self.load_company_history(ticker)
        if not history:
            return {"quarterly_revenue": [], "yearly_revenue": []}
        latest = history[-1]

        def _norm_list(raw) -> List[Tuple[str, float]]:
            rows: List[Tuple[str, float]] = []
            if not raw:
                return rows
            if isinstance(raw, dict):
                for k, v in raw.items():
                    vf = self._safe_float(v)
                    if vf is not None:
                        rows.append((str(k), vf))
            elif isinstance(raw, list):
                for item in raw:
                    if isinstance(item, dict):
                        d = item.get("date") or item.get("data") or item.get("period")
                        v = item.get("revenue") or item.get("value") or item.get("przychody")
                        vf = self._safe_float(v)
                        if d is not None and vf is not None:
                            rows.append((str(d), vf))
            return rows

        q = _norm_list(latest.get("quarterly_revenue"))
        y = _norm_list(latest.get("yearly_revenue"))
        q.sort(key=lambda x: x[0])
        y.sort(key=lambda x: x[0])
        return {"quarterly_revenue": q, "yearly_revenue": y}

    # ---------------------------------------------------------------------
    # CACHE surowych wpisów użytkownika (do prezentacji w GUI)
    # ---------------------------------------------------------------------
    def store_raw_values(self, ticker: str, raw_map: Dict[str, str]) -> None:
        """Przechowuje surowe wartości wpisane przez użytkownika (nie zapisuje do JSON)."""
        try:
            t = ticker.upper()
            self.raw_values_cache[t] = {k: str(v) for k, v in (raw_map or {}).items()}
        except Exception:
            pass

    def get_raw_value(self, ticker: str, json_key: str) -> Optional[str]:
        """Zwraca surową wartość dla pola json_key (jeśli istnieje) dla danego tickera."""
        try:
            return self.raw_values_cache.get(ticker.upper(), {}).get(json_key)
        except Exception:
            return None

    def store_raw_sector(self, ticker: str, raw_sector: str) -> None:
        """Zachowuje surowy tekst sektora wpisany przez użytkownika (tylko w pamięci)."""
        try:
            if raw_sector is not None:
                self.raw_sector_cache[ticker.upper()] = str(raw_sector)
        except Exception:
            pass

    def get_raw_sector(self, ticker: str) -> Optional[str]:
        """Zwraca surowy sektor (jeśli istnieje) dla danego tickera."""
        try:
            return self.raw_sector_cache.get(ticker.upper())
        except Exception:
            return None
