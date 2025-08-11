# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\src\api\api_fetcher.py
import logging
import os
import time
from datetime import datetime

import requests
import yfinance as yf
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.api.api_field_mapping import map_api_fields
from src.api.api_keys import get_api_key
import src.api.scraper as scraper  # ważne: import modułu (łatwy patch w testach)
from src.core.logging_config import setup_logging

# --- Importy opcjonalne (bez twardej zależności w czasie importu modułu) ---
try:
    # Alpha Vantage – jeżeli brak biblioteki, wyłączamy tylko ten fetcher
    from alpha_vantage.fundamentaldata import FundamentalData  # type: ignore
except Exception:
    logging.warning(
        "Biblioteka 'alpha_vantage' nie jest zainstalowana – fetch_from_alpha_vantage zostanie pominięty."
    )
    FundamentalData = None  # type: ignore[misc]

try:
    # yahooquery – jeżeli brak biblioteki, wyłączamy tylko ten fetcher
    from yahooquery import Ticker as YahooQueryTicker  # type: ignore
except Exception:
    logging.warning(
        "Biblioteka 'yahooquery' nie jest zainstalowana – fetch_from_yahooquery zostanie pominięty."
    )
    YahooQueryTicker = None  # type: ignore[misc]

# Inicjalizacja logowania
setup_logging()

# Konfiguracja retry dla żądań HTTP
session = requests.Session()
retries = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))


def fetch_from_yfinance(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z Yahoo Finance dla podanego tickera.
    """
    try:
        if data_type not in ["company", "etf"]:
            logging.info(f"Pomijam yfinance dla {data_type}, używane tylko dla spółek i ETF")
            return {}
        time.sleep(1)  # Opóźnienie dla uniknięcia błędu 429
        ticker_obj = yf.Ticker(ticker.upper())
        data = ticker_obj.info or {}

        # Dodatkowe klucze
        data["market_cap"] = data.get("marketCap")
        data["ebitda_margin"] = data.get("ebitdaMargins")
        data["roic"] = data.get("returnOnAssets")  # przybliżenie
        data["user_growth"] = None
        data["interest_coverage"] = data.get("interestCoverage")
        data["net_debt_ebitda"] = None
        data["inventory_turnover"] = data.get("inventoryTurnover")
        data["asset_turnover"] = data.get("assetTurnover")
        data["operating_cash_flow"] = data.get("operatingCashflow")
        data["free_cash_flow"] = data.get("freeCashflow")
        data["ffo"] = None
        data["ltv"] = None
        data["rnd_sales"] = None
        data["cac_ltv"] = None

        hist = ticker_obj.history(period="1d", raise_errors=False)
        if hist is not None and hasattr(hist, "empty") and not hist.empty:
            try:
                data["cena"] = float(hist["Close"].iloc[-1])
            except Exception:
                pass

        quarterly_income = getattr(ticker_obj, "quarterly_financials", None)
        if quarterly_income is not None and hasattr(quarterly_income, "iterrows") and not quarterly_income.empty:
            data["quarterly_revenue"] = [
                {
                    "date": str(index),
                    "revenue": float(row.get("Total Revenue", None)) if row.get("Total Revenue") else None,
                }
                for index, row in quarterly_income.iterrows()
                if row.get("Total Revenue") is not None
            ][:4]

        yearly_income = getattr(ticker_obj, "financials", None)
        if yearly_income is not None and hasattr(yearly_income, "iterrows") and not yearly_income.empty:
            data["yearly_revenue"] = [
                {
                    "date": str(index),
                    "revenue": float(row.get("Total Revenue", None)) if row.get("Total Revenue") else None,
                }
                for index, row in yearly_income.iterrows()
                if row.get("Total Revenue") is not None
            ][:5]
            try:
                data["revenue"] = (
                    float(yearly_income["Total Revenue"].iloc[0])
                    if "Total Revenue" in yearly_income.columns and not yearly_income.empty
                    else None
                )
            except Exception:
                data["revenue"] = None

        logging.debug(f"Surowe dane z yfinance dla {ticker}: {list(data.keys())}")
        return map_api_fields("yfinance", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z yfinance dla {ticker}: {str(e)}")
        return {}


def fetch_from_alpha_vantage(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z Alpha Vantage dla podanego tickera.
    UWAGA: dla testów funkcja działa nawet bez klucza – używa 'DUMMY' (mocki przejmują wywołania).
    """
    try:
        if data_type != "company":
            logging.info(f"Pomijam Alpha Vantage dla {data_type}, używane tylko dla spółek")
            return {}
        if FundamentalData is None:
            logging.warning("Pomijam Alpha Vantage: brak biblioteki 'alpha_vantage'")
            return {}

        api_key = get_api_key("ALPHA_VANTAGE_API_KEY") or os.getenv("ALPHA_VANTAGE_API_KEY_TEST", "DUMMY")

        # Limit 5 żądań/min – w testach mocki przejmą wywołania
        time.sleep(0 if api_key == "DUMMY" else 12)
        fd = FundamentalData(key=api_key)
        overview, _ = fd.get_company_overview(symbol=ticker.upper())

        data: dict = {}
        if overview:
            data.update(overview)
            data["market_cap"] = overview.get("MarketCapitalization")
            data["ebitda_margin"] = overview.get("EBITDAMargin")
            data["roic"] = overview.get("ReturnOnCapitalEmployed")
            data["interest_coverage"] = overview.get("InterestCoverage")

        # Dodatkowe endpointy REST (quote/income/balance/cashflow)
        quote = session.get(
            f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker.upper()}&apikey={api_key}",
            timeout=15,
        )
        if quote.status_code == 200:
            qj = quote.json() or {}
            gq = qj.get("Global Quote") or {}
            try:
                data["cena"] = float(gq.get("05. price")) if gq.get("05. price") else None
            except Exception:
                pass

        income = session.get(
            f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker.upper()}&apikey={api_key}",
            timeout=15,
        )
        if income.status_code == 200:
            ij = income.json() or {}
            q_reports = (ij.get("quarterlyReports") or [])[:4]
            data["quarterly_revenue"] = [
                {
                    "date": r.get("fiscalDateEnding"),
                    "revenue": float(r.get("totalRevenue")) if r.get("totalRevenue") not in [None, "", "None"] else None,
                }
                for r in q_reports
            ]
            y_reports = (ij.get("annualReports") or [])[:5]
            data["yearly_revenue"] = [
                {
                    "date": r.get("fiscalDateEnding"),
                    "revenue": float(r.get("totalRevenue")) if r.get("totalRevenue") not in [None, "", "None"] else None,
                }
                for r in y_reports
            ]
            try:
                data["revenue"] = (
                    float(y_reports[0]["totalRevenue"]) if y_reports and y_reports[0].get("totalRevenue") else None
                )
            except Exception:
                data["revenue"] = None

        balance = session.get(
            f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker.upper()}&apikey={api_key}",
            timeout=15,
        )
        if balance.status_code == 200:
            bj = balance.json() or {}
            q = (bj.get("quarterlyReports") or [])
            if q:
                b0 = q[0]
                try:
                    total_liab = float(b0.get("totalLiabilities", 0))
                    total_eq = float(b0.get("totalShareholderEquity", 0))
                    data["debt_equity"] = (total_liab / total_eq) if total_eq else None
                except Exception:
                    data["debt_equity"] = None
                try:
                    cash = float(b0.get("cashAndCashEquivalentsAtCarryingValue", 0))
                    curr_liab = float(b0.get("totalCurrentLiabilities", 0))
                    data["cash_ratio"] = (cash / curr_liab) if curr_liab else None
                except Exception:
                    data["cash_ratio"] = None

        cash_flow = session.get(
            f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker.upper()}&apikey={api_key}",
            timeout=15,
        )
        if cash_flow.status_code == 200:
            cfj = cash_flow.json() or {}
            q = (cfj.get("quarterlyReports") or [])
            if q:
                c0 = q[0]
                try:
                    ocf = float(c0.get("operatingCashflow", 0))
                    capex = float(c0.get("capitalExpenditures", 0))
                    data["free_cash_flow"] = ocf - capex
                except Exception:
                    data["free_cash_flow"] = None
                try:
                    data["operating_cash_flow"] = float(c0.get("operatingCashflow", 0))
                except Exception:
                    data["operating_cash_flow"] = None

        # Ustawienia domyślne braków
        data.setdefault("user_growth", None)
        data.setdefault("net_debt_ebitda", None)
        data.setdefault("inventory_turnover", None)
        data.setdefault("asset_turnover", None)
        data.setdefault("ffo", None)
        data.setdefault("ltv", None)
        data.setdefault("rnd_sales", None)
        data.setdefault("cac_ltv", None)

        logging.debug(f"Surowe dane z Alpha Vantage dla {ticker}: {list(data.keys())}")
        return map_api_fields("Alpha Vantage", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z Alpha Vantage dla {ticker}: {str(e)}")
        return {}


def fetch_from_fmp(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z Financial Modeling Prep dla podanego tickera.
    UWAGA: dla testów funkcja działa nawet bez klucza – używa 'DUMMY' (mocki przejmują wywołania).
    """
    try:
        if data_type != "company":
            logging.info(f"Pomijam FMP dla {data_type}, używane tylko dla spółek")
            return {}
        fmp_key = get_api_key("FMP_API_KEY") or os.getenv("FMP_API_KEY_TEST", "DUMMY")

        profile = session.get(
            f"https://financialmodelingprep.com/api/v3/profile/{ticker.upper()}?apikey={fmp_key}", timeout=15
        )
        quote = session.get(
            f"https://financialmodelingprep.com/api/v3/quote/{ticker.upper()}?apikey={fmp_key}", timeout=15
        )
        ratios = session.get(
            f"https://financialmodelingprep.com/api/v3/ratios/{ticker.upper()}?limit=1&apikey={fmp_key}", timeout=15
        )
        income = session.get(
            f"https://financialmodelingprep.com/api/v3/income-statement/{ticker.upper()}?limit=5&apikey={fmp_key}",
            timeout=15,
        )
        balance = session.get(
            f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker.upper()}?limit=5&apikey={fmp_key}",
            timeout=15,
        )
        cash_flow = session.get(
            f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker.upper()}?limit=5&apikey={fmp_key}",
            timeout=15,
        )
        income_quarterly = session.get(
            f"https://financialmodelingprep.com/api/v3/income-statement/{ticker.upper()}?period=quarter&limit=4&apikey={fmp_key}",
            timeout=15,
        )
        analyst = session.get(
            f"https://financialmodelingprep.com/api/v4/analyst-estimates/{ticker.upper()}?apikey={fmp_key}", timeout=15
        )

        data: dict = {}
        if profile.status_code == 200 and profile.json():
            pj = profile.json()[0]
            data.update(pj)
            data["market_cap"] = pj.get("mktCap")
        if quote.status_code == 200 and quote.json():
            data.update(quote.json()[0])
        if ratios.status_code == 200 and ratios.json():
            r = ratios.json()[0]
            data.update(r)
            data["ebitda_margin"] = r.get("ebitdaMargin")
            data["roic"] = r.get("returnOnInvestedCapital")
            data["interest_coverage"] = r.get("interestCoverage")
            data["net_debt_ebitda"] = r.get("netDebtToEBITDA")
            data["inventory_turnover"] = r.get("inventoryTurnover")
            data["asset_turnover"] = r.get("assetTurnover")
        if income.status_code == 200 and income.json():
            ij = income.json()
            data["revenue"] = ij[0].get("revenue")
            data["operating_margin"] = ij[0].get("operatingMargin")
            data["profit_margin"] = ij[0].get("netProfitMargin")
            data["yearly_revenue"] = [
                {"date": entry["date"], "revenue": float(entry["revenue"]) if entry["revenue"] else None}
                for entry in ij[:5]
            ]
        if balance.status_code == 200 and balance.json():
            bj = balance.json()[0]
            data["total_debt"] = bj.get("totalDebt")
            data["total_equity"] = bj.get("totalEquity")
            data["current_ratio"] = bj.get("currentRatio", data.get("currentRatio"))
            data["roe"] = bj.get("returnOnEquity", data.get("returnOnEquity"))
            data["quick_ratio"] = bj.get("quickRatio")
            data["cash_ratio"] = bj.get("cashRatio")
            try:
                td = float(bj.get("totalDebt", 0))
                te = float(bj.get("totalEquity", 0))
                data["debt_equity"] = (td / te) if te else None
            except Exception:
                data["debt_equity"] = None
        if cash_flow.status_code == 200 and cash_flow.json():
            cf = cash_flow.json()[0]
            data["free_cash_flow"] = cf.get("freeCashFlow")
            data["operating_cash_flow"] = cf.get("operatingCashFlow")
            data["cash_flow_to_debt_ratio"] = cf.get("cashFlowToDebtRatio")
        if income_quarterly.status_code == 200 and income_quarterly.json():
            iq = income_quarterly.json()
            data["quarterly_revenue"] = [
                {"date": entry["date"], "revenue": float(entry["revenue"]) if entry["revenue"] else None}
                for entry in iq[:4]
            ]
        if analyst.status_code == 200 and analyst.json():
            a = analyst.json()[0]
            data["average_price_target"] = a.get("averagePriceTarget")
            data["recommendation_mean"] = a.get("recommendationMean")
            data["earnings_growth"] = a.get("earningsGrowth")

        # Braki – ustaw jednoznacznie
        data.setdefault("user_growth", None)
        data.setdefault("ffo", None)
        data.setdefault("ltv", None)
        data.setdefault("rnd_sales", None)
        data.setdefault("cac_ltv", None)

        logging.debug(f"Surowe dane z FMP dla {ticker}: {list(data.keys())}")
        return map_api_fields("FMP", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z FMP dla {ticker}: {str(e)}")
        return {}


def fetch_from_finnhub(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z Finnhub dla podanego tickera.
    UWAGA: dla testów funkcja działa nawet bez klucza – używa 'TEST' (mocki przejmują wywołania).
    """
    try:
        if data_type != "company":
            logging.info(f"Pomijam Finnhub dla {data_type}, używane tylko dla spółek")
            return {}
        # wybierz pierwszy prawidłowy klucz (albo DUMMY na potrzeby testów)
        from src.api.api_keys import FINNHUB_API_KEYS

        valid_key = next((k for k in FINNHUB_API_KEYS if k and not str(k).startswith("your_")), None)
        if not valid_key:
            valid_key = os.getenv("FINNHUB_API_KEY_TEST", "TEST")

        profile = session.get(
            f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker.upper()}&token={valid_key}", timeout=15
        )
        quote = session.get(f"https://finnhub.io/api/v1/quote?symbol={ticker.upper()}&token={valid_key}", timeout=15)
        recommendation = session.get(
            f"https://finnhub.io/api/v1/stock/recommendation?symbol={ticker.upper()}&token={valid_key}", timeout=15
        )
        financials = session.get(
            f"https://finnhub.io/api/v1/stock/metric?symbol={ticker.upper()}&metric=all&token={valid_key}", timeout=15
        )

        data: dict = {}
        if profile.status_code == 200 and profile.json():
            pj = profile.json()
            data.update(pj)
            data["market_cap"] = pj.get("marketCapitalization")
        if quote.status_code == 200 and quote.json():
            data.update(quote.json())
        if recommendation.status_code == 200 and recommendation.json():
            rj = recommendation.json()[0]
            data["targetMeanPrice"] = rj.get("targetPrice")
            data["recommendationMean"] = rj.get("rating")
        if financials.status_code == 200 and financials.json():
            j = financials.json().get("metric", {}) or {}
            data["ebitda_margin"] = j.get("ebitdaMarginTTM")
            data["roic"] = j.get("roicTTM")
            data["revenue_growth"] = j.get("revenueGrowthTTM")
            data["gross_margin"] = j.get("grossMarginTTM")
            data["operating_margin"] = j.get("operatingMarginTTM")
            data["profit_margin"] = j.get("netMarginTTM")
            data["free_cash_flow"] = j.get("freeCashFlowTTM")
            data["eps_ttm"] = j.get("epsTTM")

        data.setdefault("user_growth", None)
        data.setdefault("interest_coverage", None)
        data.setdefault("net_debt_ebitda", None)
        data.setdefault("inventory_turnover", None)
        data.setdefault("asset_turnover", None)
        data.setdefault("operating_cash_flow", None)
        data.setdefault("ffo", None)
        data.setdefault("ltv", None)
        data.setdefault("rnd_sales", None)
        data.setdefault("cac_ltv", None)

        logging.debug(f"Surowe dane z Finnhub dla {ticker}: {list(data.keys())}")
        return map_api_fields("Finnhub", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z Finnhub dla {ticker}: {str(e)}")
        return {}


def fetch_from_yahooquery(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z YahooQuery dla podanego tickera.
    """
    try:
        if data_type not in ["company", "etf"]:
            logging.info(f"Pomijam yahooquery dla {data_type}, używane tylko dla spółek i ETF")
            return {}
        if YahooQueryTicker is None:
            logging.warning("Pomijam yahooquery: moduł nie jest dostępny")
            return {}

        ticker_obj = YahooQueryTicker(ticker.upper())
        data: dict = {}

        summary = getattr(ticker_obj, "summary_profile", None)
        if summary and ticker.upper() in summary and isinstance(summary[ticker.upper()], dict):
            data.update(summary[ticker.upper()])

        financials = getattr(ticker_obj, "financial_data", None)
        if financials and ticker.upper() in financials and isinstance(financials[ticker.upper()], dict):
            f = financials[ticker.upper()]
            data.update(f)
            data["market_cap"] = f.get("marketCap")
            data["ebitda_margin"] = f.get("ebitdaMargin")
            data["roic"] = f.get("returnOnInvestedCapital")
            data["interest_coverage"] = f.get("interestCoverage")
            data["net_debt_ebitda"] = f.get("netDebtToEBITDA")

        key_stats = getattr(ticker_obj, "key_stats", None)
        if key_stats and ticker.upper() in key_stats and isinstance(key_stats[ticker.upper()], dict):
            data.update(key_stats[ticker.upper()])

        income = ticker_obj.income_statement(frequency="q")
        if hasattr(income, "empty") and not income.empty:
            data["quarterly_revenue"] = [
                {
                    "date": str(index[1]) if isinstance(index, tuple) else str(index),
                    "revenue": float(row.get("TotalRevenue", None)) if row.get("TotalRevenue") else None,
                }
                for index, row in income.head(4).iterrows()
                if row.get("TotalRevenue") is not None
            ]

        yearly_income = ticker_obj.income_statement(frequency="a")
        if hasattr(yearly_income, "empty") and not yearly_income.empty:
            data["yearly_revenue"] = [
                {
                    "date": str(index[1]) if isinstance(index, tuple) else str(index),
                    "revenue": float(row.get("TotalRevenue", None)) if row.get("TotalRevenue") else None,
                }
                for index, row in yearly_income.head(5).iterrows()
                if row.get("TotalRevenue") is not None
            ]
            try:
                data["revenue"] = (
                    float(yearly_income["TotalRevenue"].iloc[0])
                    if "TotalRevenue" in yearly_income.columns and not yearly_income.empty
                    else None
                )
            except Exception:
                data["revenue"] = None

        data.setdefault("user_growth", None)
        data.setdefault("inventory_turnover", None)
        data.setdefault("asset_turnover", None)
        data.setdefault("operating_cash_flow", None)
        data.setdefault("ffo", None)
        data.setdefault("ltv", None)
        data.setdefault("rnd_sales", None)
        data.setdefault("cac_ltv", None)

        logging.debug(f"Surowe dane z yahooquery dla {ticker}: {list(data.keys())}")
        return map_api_fields("yahooquery", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z yahooquery dla {ticker}: {str(e)}")
        return {}


def fetch_from_marketwatch(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z MarketWatch za pomocą scrapera.
    Gdy scraping rzuci wyjątek albo zwróci pusty dict – zwracamy {} (bez mapowania),
    aby testy mogły asertywnie sprawdzić błąd.
    """
    try:
        if data_type != "company":
            logging.info(f"Pomijam MarketWatch dla {data_type}, używane tylko dla spółek")
            return {}
        time.sleep(1)
        data = scraper.scrape_marketwatch(ticker)
        if not isinstance(data, dict) or not data:
            return {}
        logging.debug(f"Surowe dane z MarketWatch dla {ticker}: {list(data.keys())}")
        return map_api_fields("MarketWatch", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z MarketWatch dla {ticker}: {str(e)}")
        return {}


def fetch_from_investing(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z Investing.com za pomocą scrapera.
    Gdy scraping rzuci wyjątek albo zwróci pusty dict – zwracamy {} (bez mapowania),
    aby testy mogły asertywnie sprawdzić błąd.
    """
    try:
        if data_type != "company":
            logging.info(f"Pomijam Investing.com dla {data_type}, używane tylko dla spółek")
            return {}
        time.sleep(1)
        data = scraper.scrape_investing(ticker)
        if not isinstance(data, dict) or not data:
            return {}
        logging.debug(f"Surowe dane z Investing.com dla {ticker}: {list(data.keys())}")
        return map_api_fields("Investing", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z Investing.com dla {ticker}: {str(e)}")
        return {}


def fetch_data(tickers, parent=None, data_type="company"):
    """
    Pobiera dane z wielu API dla listy tickerów, uzupełniając brakujące pola.
    Zwraca (wyniki, brakujące_ticker->klucze)
    """
    try:
        logging.info(f"Rozpoczęto pobieranie danych dla tickerów: {tickers}, typ: {data_type}")
        results = {}
        missing_tickers = {}
        required_keys = (
            [
                "nazwa",
                "sektor",
                "cena",
                "pe_ratio",
                "forward_pe",
                "peg_ratio",
                "revenue_growth",
                "gross_margin",
                "debt_equity",
                "current_ratio",
                "roe",
                "free_cash_flow_margin",
                "eps_ttm",
                "price_to_book_ratio",
                "price_to_sales_ratio",
                "operating_margin",
                "profit_margin",
                "quick_ratio",
                "cash_ratio",
                "cash_flow_to_debt_ratio",
                "earnings_growth",
                "analyst_target_price",
                "analyst_rating",
                "quarterly_revenue",
                "yearly_revenue",
                "market_cap",
                "revenue",
                "ebitda_margin",
                "roic",
                "user_growth",
                "interest_coverage",
                "net_debt_ebitda",
                "inventory_turnover",
                "asset_turnover",
                "operating_cash_flow",
                "free_cash_flow",
                "ffo",
                "ltv",
                "rnd_sales",
                "cac_ltv",
            ]
            if data_type != "macro"
            else ["nazwa", "value"]
        )

        for ticker in tickers:
            t = ticker.upper()
            results[t] = (
                {
                    "ticker": t,
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
                    "cac_ltv": None,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                }
                if data_type != "macro"
                else {"ticker": t, "nazwa": t, "value": None, "date": datetime.now().strftime("%Y-%m-%d")}
            )
            missing_tickers[t] = required_keys.copy()

        api_methods = [
            ("yfinance", fetch_from_yfinance),
            ("FMP", fetch_from_fmp),
            ("Alpha Vantage", fetch_from_alpha_vantage),
            ("Finnhub", fetch_from_finnhub),
            ("yahooquery", fetch_from_yahooquery),
            ("MarketWatch", fetch_from_marketwatch),
            ("Investing", fetch_from_investing),
        ]

        for api_name, method in api_methods:
            for ticker in list(tickers):
                t = ticker.upper()
                try:
                    if t in missing_tickers and missing_tickers[t]:
                        data = method(t, data_type)
                        if data:
                            for key in missing_tickers[t][:]:
                                if key in data and data[key] is not None:
                                    results[t][key] = data[key]
                                    missing_tickers[t].remove(key)
                            logging.info(f"Pobrano dane z {api_name} dla {t}: pola={list(data.keys())}")
                        if not missing_tickers[t]:
                            del missing_tickers[t]
                        else:
                            logging.info(f"Brakujące klucze dla {t} po {api_name}: {missing_tickers[t]}")
                except Exception as e:
                    logging.error(f"Błąd pobierania danych z {api_name} dla {t}: {str(e)}")
                    continue

        logging.info(f"Zakończono pobieranie danych, brakujące tickery: {missing_tickers}")
        return results, missing_tickers
    except Exception as e:
        logging.error(f"Błąd podczas pobierania danych z API dla {tickers}: {str(e)}")
        return {}, {t.upper(): ['all'] for t in tickers}
