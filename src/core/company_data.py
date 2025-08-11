# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\core\company_data.py
import json
import os
import logging
from datetime import datetime
from src.api.api_fetcher import fetch_data
from src.core.logging_config import setup_logging
from src.core.sector_mapping import normalize_sector
from typing import Dict, List, Tuple, Optional

setup_logging()

class CompanyData:
    def __init__(self):
        """
        Inicjalizuje obiekt przechowujący dane spółek.
        """
        self.companies = []
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            try:
                os.makedirs(self.data_dir)
                logging.info(f"Utworzono katalog danych: {self.data_dir}")
            except Exception as e:
                logging.error(f"Błąd tworzenia katalogu danych {self.data_dir}: {str(e)}")
                raise
        self.load_all_companies()

    def load_all_companies(self):
        """
        Wczytuje wszystkie dane spółek z folderu data/.
        """
        try:
            self.companies = []
            valid_sectors = {f.replace(".json", "").lower() for f in os.listdir(os.path.join("src", "core", "sectors")) if f.endswith(".json")}
            for file_name in os.listdir(self.data_dir):
                if file_name.endswith(".json") and not file_name.lower().startswith(("technology", "financials", "biotechnology", "test-sector")):
                    ticker = file_name[:-5].upper()
                    file_path = os.path.join(self.data_dir, f"{ticker}.json")
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            history = json.load(f)
                            if history and isinstance(history, list) and len(history) > 0:
                                latest = history[-1]
                                if isinstance(latest, dict) and "ticker" in latest:
                                    company = {
                                        "ticker": ticker,
                                        "nazwa": None,
                                        "sektor": None,
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
                                        "faza": None,
                                        "is_in_portfolio": False,
                                        "date": latest.get("date", datetime.now().strftime("%Y-%m-%d")),
                                        "is_manual_cena": False,
                                        "is_manual_analyst_target_price": False,
                                        "is_manual_pe_ratio": False,
                                        "is_manual_forward_pe": False,
                                        "is_manual_peg_ratio": False,
                                        "is_manual_revenue_growth": False,
                                        "is_manual_gross_margin": False,
                                        "is_manual_debt_equity": False,
                                        "is_manual_current_ratio": False,
                                        "is_manual_roe": False,
                                        "is_manual_free_cash_flow_margin": False,
                                        "is_manual_eps_ttm": False,
                                        "is_manual_price_to_book_ratio": False,
                                        "is_manual_price_to_sales_ratio": False,
                                        "is_manual_operating_margin": False,
                                        "is_manual_profit_margin": False,
                                        "is_manual_quick_ratio": False,
                                        "is_manual_cash_ratio": False,
                                        "is_manual_cash_flow_to_debt_ratio": False,
                                        "is_manual_earnings_growth": False,
                                        "is_manual_sektor": False,
                                        "is_manual_faza": False,
                                        "is_manual_ebitda_margin": False,
                                        "is_manual_roic": False,
                                        "is_manual_user_growth": False,
                                        "is_manual_interest_coverage": False,
                                        "is_manual_net_debt_ebitda": False,
                                        "is_manual_inventory_turnover": False,
                                        "is_manual_asset_turnover": False,
                                        "is_manual_operating_cash_flow": False,
                                        "is_manual_free_cash_flow": False,
                                        "is_manual_ffo": False,
                                        "is_manual_ltv": False,
                                        "is_manual_rnd_sales": False,
                                        "is_manual_cac_ltv": False,
                                        "indicator_color_nazwa": "black",
                                        "indicator_color_sektor": "black",
                                        "indicator_color_cena": "black",
                                        "indicator_color_analyst_target_price": "black",
                                        "indicator_color_pe_ratio": "black",
                                        "indicator_color_forward_pe": "black",
                                        "indicator_color_peg_ratio": "black",
                                        "indicator_color_revenue_growth": "black",
                                        "indicator_color_gross_margin": "black",
                                        "indicator_color_debt_equity": "black",
                                        "indicator_color_current_ratio": "black",
                                        "indicator_color_roe": "black",
                                        "indicator_color_free_cash_flow_margin": "black",
                                        "indicator_color_eps_ttm": "black",
                                        "indicator_color_price_to_book_ratio": "black",
                                        "indicator_color_price_to_sales_ratio": "black",
                                        "indicator_color_operating_margin": "black",
                                        "indicator_color_profit_margin": "black",
                                        "indicator_color_quick_ratio": "black",
                                        "indicator_color_cash_ratio": "black",
                                        "indicator_color_cash_flow_to_debt_ratio": "black",
                                        "indicator_color_analyst_rating": "black",
                                        "indicator_color_earnings_growth": "black",
                                        "indicator_color_faza": "black",
                                        "indicator_color_ebitda_margin": "black",
                                        "indicator_color_roic": "black",
                                        "indicator_color_user_growth": "black",
                                        "indicator_color_interest_coverage": "black",
                                        "indicator_color_net_debt_ebitda": "black",
                                        "indicator_color_inventory_turnover": "black",
                                        "indicator_color_asset_turnover": "black",
                                        "indicator_color_operating_cash_flow": "black",
                                        "indicator_color_free_cash_flow": "black",
                                        "indicator_color_ffo": "black",
                                        "indicator_color_ltv": "black",
                                        "indicator_color_rnd_sales": "black",
                                        "indicator_color_cac_ltv": "black",
                                        "quarterly_revenue": latest.get("quarterly_revenue", []),
                                        "yearly_revenue": latest.get("yearly_revenue", []),
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
                                        "cac_ltv": None
                                    }
                                    for key, value in latest.items():
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
                                                value = float(value)
                                                if key == "debt_equity" and value > 10.0:
                                                    value /= 100
                                                latest[key] = f"{value:.2f}"
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
                                    logging.info(f"Wczytano spółkę {ticker} z {file_path}")
                                else:
                                    logging.warning(f"Nieprawidłowy format pliku JSON dla {ticker}: brak pola 'ticker'")
                            else:
                                logging.warning(f"Nieprawidłowy format pliku JSON dla {ticker}: pusty lub nieprawidłowy")
                    except json.JSONDecodeError as e:
                        logging.error(f"Błąd dekodowania JSON dla {ticker}: {str(e)}")
            logging.info(f"Wczytano {len(self.companies)} spółek z folderu data/")
        except Exception as e:
            logging.error(f"Błąd podczas wczytywania wszystkich spółek: {str(e)}")

    def add_company(self, ticker: str):
        """
        Dodaje nową spółkę do listy.
        Args:
            ticker: Symbol giełdowy spółki.
        """
        try:
            ticker = ticker.upper()
            if any(c["ticker"] == ticker for c in self.companies):
                logging.warning(f"Spółka {ticker} już istnieje, pomijanie dodawania")
                return
            if not ticker.isalnum():
                logging.error(f"Nieprawidłowy ticker {ticker}: tylko znaki alfanumeryczne są dozwolone")
                raise ValueError(f"Nieprawidłowy ticker {ticker}")
            company = {
                "ticker": ticker,
                "nazwa": None,
                "sektor": None,
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
                "faza": None,
                "is_in_portfolio": False,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "is_manual_cena": False,
                "is_manual_analyst_target_price": False,
                "is_manual_pe_ratio": False,
                "is_manual_forward_pe": False,
                "is_manual_peg_ratio": False,
                "is_manual_revenue_growth": False,
                "is_manual_gross_margin": False,
                "is_manual_debt_equity": False,
                "is_manual_current_ratio": False,
                "is_manual_roe": False,
                "is_manual_free_cash_flow_margin": False,
                "is_manual_eps_ttm": False,
                "is_manual_price_to_book_ratio": False,
                "is_manual_price_to_sales_ratio": False,
                "is_manual_operating_margin": False,
                "is_manual_profit_margin": False,
                "is_manual_quick_ratio": False,
                "is_manual_cash_ratio": False,
                "is_manual_cash_flow_to_debt_ratio": False,
                "is_manual_earnings_growth": False,
                "is_manual_sektor": False,
                "is_manual_faza": False,
                "is_manual_ebitda_margin": False,
                "is_manual_roic": False,
                "is_manual_user_growth": False,
                "is_manual_interest_coverage": False,
                "is_manual_net_debt_ebitda": False,
                "is_manual_inventory_turnover": False,
                "is_manual_asset_turnover": False,
                "is_manual_operating_cash_flow": False,
                "is_manual_free_cash_flow": False,
                "is_manual_ffo": False,
                "is_manual_ltv": False,
                "is_manual_rnd_sales": False,
                "is_manual_cac_ltv": False,
                "indicator_color_nazwa": "black",
                "indicator_color_sektor": "black",
                "indicator_color_cena": "black",
                "indicator_color_analyst_target_price": "black",
                "indicator_color_pe_ratio": "black",
                "indicator_color_forward_pe": "black",
                "indicator_color_peg_ratio": "black",
                "indicator_color_revenue_growth": "black",
                "indicator_color_gross_margin": "black",
                "indicator_color_debt_equity": "black",
                "indicator_color_current_ratio": "black",
                "indicator_color_roe": "black",
                "indicator_color_free_cash_flow_margin": "black",
                "indicator_color_eps_ttm": "black",
                "indicator_color_price_to_book_ratio": "black",
                "indicator_color_price_to_sales_ratio": "black",
                "indicator_color_operating_margin": "black",
                "indicator_color_profit_margin": "black",
                "indicator_color_quick_ratio": "black",
                "indicator_color_cash_ratio": "black",
                "indicator_color_cash_flow_to_debt_ratio": "black",
                "indicator_color_analyst_rating": "black",
                "indicator_color_earnings_growth": "black",
                "indicator_color_faza": "black",
                "indicator_color_ebitda_margin": "black",
                "indicator_color_roic": "black",
                "indicator_color_user_growth": "black",
                "indicator_color_interest_coverage": "black",
                "indicator_color_net_debt_ebitda": "black",
                "indicator_color_inventory_turnover": "black",
                "indicator_color_asset_turnover": "black",
                "indicator_color_operating_cash_flow": "black",
                "indicator_color_free_cash_flow": "black",
                "indicator_color_ffo": "black",
                "indicator_color_ltv": "black",
                "indicator_color_rnd_sales": "black",
                "indicator_color_cac_ltv": "black",
                "quarterly_revenue": [],
                "yearly_revenue": [],
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
                "cac_ltv": None
            }
            self.companies.append(company)
            self.save_company_data(ticker, company)
            logging.info(f"Dodano nową spółkę: {ticker}")
        except ValueError as e:
            logging.error(f"Błąd podczas dodawania spółki {ticker}: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Nieoczekiwany błąd podczas dodawania spółki {ticker}: {str(e)}")
            raise

    def get_company(self, ticker: str) -> dict | None:
        """
        Zwraca dane spółki dla podanego tickera.
        Args:
            ticker: Symbol giełdowy spółki.
        Returns:
            Słownik z danymi spółki lub None.
        """
        try:
            ticker = ticker.upper()
            return next((c for c in self.companies if c["ticker"] == ticker), None)
        except Exception as e:
            logging.error(f"Błąd podczas pobierania danych dla {ticker}: {str(e)}")
            return None

    def save_company_data(self, ticker: str, data: dict):
        """
        Zapisuje dane spółki do pliku JSON z walidacją formatu i nadpisywaniem danych dla tego samego dnia.
        Args:
            ticker: Symbol giełdowy spółki.
            data: Słownik z danymi spółki.
        """
        try:
            ticker = ticker.upper()
            file_path = os.path.join(self.data_dir, f"{ticker}.json")
            today = data.get("date", datetime.now().strftime("%Y-%m-%d"))
            if not today:
                logging.error(f"Brak daty dla {ticker}, używam bieżącej daty")
                today = datetime.now().strftime("%Y-%m-%d")
            valid_sectors = {f.replace(".json", "").lower() for f in os.listdir(os.path.join("src", "core", "sectors")) if f.endswith(".json")}
            sector = data.get("sektor")
            if sector:
                normalized_sector = normalize_sector(sector)
                if normalized_sector and normalized_sector.lower() in valid_sectors:
                    data["sektor"] = normalized_sector
                else:
                    logging.warning(f"Nieprawidłowy sektor {sector} dla {ticker}, ustawiono None")
                    data["sektor"] = None
            else:
                data["sektor"] = None
            # Walidacja formatu danych
            percent_fields = [
                "revenue_growth", "gross_margin", "ebitda_margin", "operating_margin",
                "profit_margin", "roe", "free_cash_flow_margin", "roic",
                "interest_coverage", "net_debt_ebitda", "inventory_turnover",
                "asset_turnover", "cac_ltv", "rnd_sales"
            ]
            numeric_fields = [
                "cena", "pe_ratio", "forward_pe", "peg_ratio", "eps_ttm",
                "price_to_book_ratio", "price_to_sales_ratio", "current_ratio",
                "quick_ratio", "cash_ratio", "cash_flow_to_debt_ratio",
                "earnings_growth", "analyst_target_price", "market_cap",
                "revenue", "operating_cash_flow", "free_cash_flow", "ffo", "ltv"
            ]
            for field in percent_fields:
                if field in data and data[field] not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                    try:
                        value = float(data[field])
                        if value <= 1.0:  # Konwersja ułamków dziesiętnych na procenty
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
                            value /= 100
                        data[field] = f"{value:.2f}"
                    except (ValueError, TypeError):
                        logging.warning(f"Nieprawidłowa wartość liczbowa {field}={data[field]} dla {ticker}, ustawiono None")
                        data[field] = None
            # Walidacja przychodów kwartalnych i rocznych
            if "quarterly_revenue" in data and isinstance(data["quarterly_revenue"], list):
                data["quarterly_revenue"] = [
                    {
                        "date": item["date"],
                        "revenue": f"{float(item['revenue']):.2f}" if item["revenue"] not in [None, "", "-", "NA", "N/A", "None", "nan"] else None,
                        "is_manual": item.get("is_manual", False)
                    }
                    for item in data["quarterly_revenue"]
                    if isinstance(item, dict) and "date" in item and "revenue" in item
                ]
            if "yearly_revenue" in data and isinstance(data["yearly_revenue"], list):
                data["yearly_revenue"] = [
                    {
                        "date": item["date"],
                        "revenue": f"{float(item['revenue']):.2f}" if item["revenue"] not in [None, "", "-", "NA", "N/A", "None", "nan"] else None,
                        "is_manual": item.get("is_manual", False)
                    }
                    for item in data["yearly_revenue"]
                    if isinstance(item, dict) and "date" in item and "revenue" in item
                ]
            # Dynamiczne kopiowanie wszystkich kluczy z danymi
            data_copy = {
                "ticker": ticker,
                "date": today,
                "is_in_portfolio": data.get("is_in_portfolio", False)
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
                data_copy[f"is_manual_{key}"] = data.get(f"is_manual_{key}", False)
                data_copy[f"indicator_color_{key}"] = data.get(f"indicator_color_{key}", "black")
            # Zapisz do pliku JSON
            history = []
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        history = json.load(f)
                        if not isinstance(history, list):
                            logging.warning(f"Nieprawidłowy format pliku JSON dla {ticker}: {history}")
                            history = []
                except json.JSONDecodeError as e:
                    logging.error(f"Błąd dekodowania JSON dla {ticker}: {str(e)}")
                    history = []
            history = [entry for entry in history if entry.get("date") != today]
            history.append(data_copy)
            history = sorted(history, key=lambda x: x.get("date", ""))
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(history, f, indent=4)
                logging.info(f"Zapisano dane dla {ticker} do {file_path}")
                logging.debug(f"Zapisane dane: {data_copy}")
            except PermissionError as e:
                logging.error(f"Brak uprawnień do zapisu pliku {file_path}: {str(e)}")
                raise
            except Exception as e:
                logging.error(f"Błąd zapisu pliku JSON dla {ticker}: {str(e)}")
                raise
            # Aktualizuj dane w pamięci
            company = self.get_company(ticker)
            if company:
                company.update(data_copy)
            else:
                self.companies.append(data_copy)
        except Exception as e:
            logging.error(f"Błąd podczas zapisywania danych dla {ticker}: {str(e)}")
            raise

    def delete_company(self, ticker: str):
        """
        Usuwa spółkę z listy i jej plik JSON.
        Args:
            ticker: Symbol giełdowy spółki.
        """
        try:
            ticker = ticker.upper()
            self.companies = [c for c in self.companies if c["ticker"] != ticker]
            file_path = os.path.join(self.data_dir, f"{ticker}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Usunięto spółkę {ticker} i plik {file_path}")
            else:
                logging.warning(f"Plik JSON dla {ticker} nie istnieje")
        except Exception as e:
            logging.error(f"Błąd podczas usuwania spółki {ticker}: {str(e)}")
            raise

    def load_company_history(self, ticker: str) -> list:
        """
        Wczytuje historię danych dla danej spółki.
        Args:
            ticker: Symbol giełdowy spółki.
        Returns:
            Lista danych historycznych posortowana według daty.
        """
        try:
            ticker = ticker.upper()
            file_path = os.path.join(self.data_dir, f"{ticker}.json")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    if isinstance(history, list):
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
                    else:
                        logging.warning(f"Nieprawidłowy format pliku historycznego dla {ticker}: {history}")
                        return []
            return []
        except Exception as e:
            logging.error(f"Błąd podczas wczytywania historii dla {ticker}: {str(e)}")
            return []

    def fetch_data(self, tickers: List[str], parent=None, data_type: str = "company") -> Tuple[Dict, Dict]:
        """
        Pobiera dane z API dla listy tickerów, respektując flagi 'is_manual_*' i uzupełniając sektor z historii.
        Args:
            tickers: Lista tickerów (np. ['AAPL', 'MSFT']).
            parent: Rodzic dla GUI (opcjonalne).
            data_type: Typ danych ('company' lub 'macro').
        Returns:
            Krotka (wyniki, brakujące tickery).
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
            logging.info(f"Pobrano dane dla {tickers}, brakujące: {missing_tickers.keys()}")
            return results, missing_tickers
        except Exception as e:
            logging.error(f"Błąd podczas pobierania danych z API dla {tickers}: {str(e)}")
            return {}, {ticker: ["all"] for ticker in tickers}