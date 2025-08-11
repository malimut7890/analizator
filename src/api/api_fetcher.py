# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\api\api_fetcher.py
import requests
import yfinance as yf
from alpha_vantage.fundamentaldata import FundamentalData
from src.core.logging_config import setup_logging
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
import time
from src.api.api_field_mapping import map_api_fields
from src.api.api_keys import (
    ALPHA_VANTAGE_API_KEY,
    FMP_API_KEY,
    FINNHUB_API_KEYS,
    get_api_key
)
from src.api.scraper import scrape_marketwatch, scrape_investing
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
try:
    from yahooquery import Ticker as YahooQueryTicker
except ImportError:
    logging.warning("Moduł yahooquery nie jest zainstalowany. Użyj 'pip install yahooquery'.")
    YahooQueryTicker = None

# Inicjalizacja logowania
setup_logging()

# Konfiguracja retry dla żądań HTTP
session = requests.Session()
retries = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

def fetch_from_yfinance(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z Yahoo Finance dla podanego tickera.
    Args:
        ticker: Symbol tickera (np. 'AAPL').
        data_type: Typ danych ('company' lub 'etf').
    Returns:
        Słownik z danymi lub pusty słownik w przypadku błędu.
    """
    try:
        if data_type not in ["company", "etf"]:
            logging.info(f"Pomijam yfinance dla {data_type}, używane tylko dla spółek i ETF")
            return {}
        time.sleep(1)  # Opóźnienie dla uniknięcia błędu 429
        ticker_obj = yf.Ticker(ticker.upper())
        data = ticker_obj.info
        data["market_cap"] = ticker_obj.info.get("marketCap")
        data["ebitda_margin"] = ticker_obj.info.get("ebitdaMargins")
        data["roic"] = ticker_obj.info.get("returnOnAssets")  # Przybliżenie ROIC
        data["user_growth"] = None  # yfinance nie dostarcza danych o wzroście użytkowników
        data["interest_coverage"] = ticker_obj.info.get("interestCoverage")
        data["net_debt_ebitda"] = None  # yfinance nie dostarcza bezpośrednio
        data["inventory_turnover"] = ticker_obj.info.get("inventoryTurnover")
        data["asset_turnover"] = ticker_obj.info.get("assetTurnover")
        data["operating_cash_flow"] = ticker_obj.info.get("operatingCashflow")
        data["free_cash_flow"] = ticker_obj.info.get("freeCashflow")
        data["ffo"] = None  # yfinance nie dostarcza FFO
        data["ltv"] = None
        data["rnd_sales"] = None
        data["cac_ltv"] = None
        hist = ticker_obj.history(period="1d", raise_errors=True)
        if not hist.empty:
            data["cena"] = str(round(hist["Close"].iloc[-1], 2))
        quarterly_income = ticker_obj.quarterly_financials
        if not quarterly_income.empty:
            data["quarterly_revenue"] = [
                {"date": str(index), "revenue": float(row.get("Total Revenue", None)) if row.get("Total Revenue") else None}
                for index, row in quarterly_income.iterrows() if row.get("Total Revenue") is not None
            ][:4]
        yearly_income = ticker_obj.financials
        if not yearly_income.empty:
            data["yearly_revenue"] = [
                {"date": str(index), "revenue": float(row.get("Total Revenue", None)) if row.get("Total Revenue") else None}
                for index, row in yearly_income.iterrows() if row.get("Total Revenue") is not None
            ][:5]
            data["revenue"] = (
                float(yearly_income["Total Revenue"].iloc[0]) if not yearly_income.empty and yearly_income["Total Revenue"].iloc[0]
                else None
            )
        logging.debug(f"Surowe dane z yfinance dla {ticker}: {data}")
        return map_api_fields("yfinance", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z yfinance dla {ticker}: {str(e)}")
        return {}

def fetch_from_alpha_vantage(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z Alpha Vantage dla podanego tickera.
    Args:
        ticker: Symbol tickera (np. 'AAPL').
        data_type: Typ danych ('company').
    Returns:
        Słownik z danymi lub pusty słownik w przypadku błędu.
    """
    try:
        if data_type != "company":
            logging.info(f"Pomijam Alpha Vantage dla {data_type}, używane tylko dla spółek")
            return {}
        api_key = get_api_key("ALPHA_VANTAGE_API_KEY")
        if not api_key or api_key.startswith("your_"):
            logging.warning("Pomijam Alpha Vantage: nieprawidłowy klucz API")
            return {}
        time.sleep(12)  # Limit 5 żądań/min
        fd = FundamentalData(key=api_key)
        overview, _ = fd.get_company_overview(symbol=ticker.upper())
        quote = session.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker.upper()}&apikey={api_key}", timeout=15)
        income = session.get(f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker.upper()}&apikey={api_key}", timeout=15)
        balance = session.get(f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker.upper()}&apikey={api_key}", timeout=15)
        cash_flow = session.get(f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker.upper()}&apikey={api_key}", timeout=15)
        data = {}
        if overview:
            data.update(overview)
            data["market_cap"] = overview.get("MarketCapitalization")
            data["ebitda_margin"] = overview.get("EBITDAMargin")
            data["roic"] = overview.get("ReturnOnCapitalEmployed")
            data["interest_coverage"] = overview.get("InterestCoverage")
        if quote.status_code == 200 and quote.json().get("Global Quote"):
            quote_data = quote.json().get("Global Quote", {})
            data["cena"] = quote_data.get("05. price")
            logging.debug(f"Odpowiedź quote z Alpha Vantage dla {ticker}: status={quote.status_code}, dane={quote.json()}")
        if income.status_code == 200 and income.json().get("quarterlyReports"):
            quarterly_reports = income.json().get("quarterlyReports", [])[:4]
            data["quarterly_revenue"] = [
                {"date": report["fiscalDateEnding"], "revenue": float(report["totalRevenue"]) if report["totalRevenue"] not in ["None", ""] else None}
                for report in quarterly_reports
            ]
            yearly_reports = income.json().get("annualReports", [])[:5]
            data["yearly_revenue"] = [
                {"date": report["fiscalDateEnding"], "revenue": float(report["totalRevenue"]) if report["totalRevenue"] not in ["None", ""] else None}
                for report in yearly_reports
            ]
            data["revenue"] = (
                float(yearly_reports[0]["totalRevenue"]) if yearly_reports and yearly_reports[0]["totalRevenue"] not in ["None", ""]
                else None
            )
            logging.debug(f"Odpowiedź income z Alpha Vantage dla {ticker}: status={income.status_code}, dane={income.json()}")
        if balance.status_code == 200 and balance.json().get("quarterlyReports"):
            balance_data = balance.json().get("quarterlyReports", [])[0]
            data["debt_equity"] = (
                float(balance_data.get("totalLiabilities", 0)) / float(balance_data.get("totalShareholderEquity", 1))
                if balance_data.get("totalShareholderEquity") and float(balance_data.get("totalShareholderEquity")) != 0
                else None
            )
            data["cash_ratio"] = (
                float(balance_data.get("cashAndCashEquivalentsAtCarryingValue", 0)) / float(balance_data.get("totalCurrentLiabilities", 1))
                if balance_data.get("totalCurrentLiabilities") and float(balance_data.get("totalCurrentLiabilities")) != 0
                else None
            )
            data["inventory_turnover"] = balance_data.get("inventoryTurnover")
            data["asset_turnover"] = balance_data.get("assetTurnover")
            logging.debug(f"Odpowiedź balance z Alpha Vantage dla {ticker}: status={balance.status_code}, dane={balance.json()}")
        if cash_flow.status_code == 200 and cash_flow.json().get("quarterlyReports"):
            cash_flow_data = cash_flow.json().get("quarterlyReports", [])[0]
            data["free_cash_flow"] = (
                float(cash_flow_data.get("operatingCashflow", 0)) - float(cash_flow_data.get("capitalExpenditures", 0))
                if cash_flow_data.get("operatingCashflow") and cash_flow_data.get("capitalExpenditures")
                else None
            )
            data["operating_cash_flow"] = cash_flow_data.get("operatingCashflow")
            logging.debug(f"Odpowiedź cash flow z Alpha Vantage dla {ticker}: status={cash_flow.status_code}, dane={cash_flow.json()}")
        data["user_growth"] = None
        data["net_debt_ebitda"] = None
        data["ffo"] = None
        data["ltv"] = None
        data["rnd_sales"] = None
        data["cac_ltv"] = None
        logging.debug(f"Surowe dane z Alpha Vantage dla {ticker}: {data}")
        return map_api_fields("Alpha Vantage", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z Alpha Vantage dla {ticker}: {str(e)}")
        return {}

def fetch_from_fmp(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z Financial Modeling Prep dla podanego tickera.
    Args:
        ticker: Symbol tickera (np. 'AAPL').
        data_type: Typ danych ('company').
    Returns:
        Słownik z danymi lub pusty słownik w przypadku błędu.
    """
    try:
        if data_type != "company":
            logging.info(f"Pomijam FMP dla {data_type}, używane tylko dla spółek")
            return {}
        if not FMP_API_KEY or FMP_API_KEY.startswith("your_"):
            logging.warning("Pomijam FMP: nieprawidłowy klucz API")
            return {}
        profile = session.get(f"https://financialmodelingprep.com/api/v3/profile/{ticker.upper()}?apikey={FMP_API_KEY}", timeout=15)
        quote = session.get(f"https://financialmodelingprep.com/api/v3/quote/{ticker.upper()}?apikey={FMP_API_KEY}", timeout=15)
        ratios = session.get(f"https://financialmodelingprep.com/api/v3/ratios/{ticker.upper()}?limit=1&apikey={FMP_API_KEY}", timeout=15)
        income = session.get(f"https://financialmodelingprep.com/api/v3/income-statement/{ticker.upper()}?limit=5&apikey={FMP_API_KEY}", timeout=15)
        balance = session.get(f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker.upper()}?limit=5&apikey={FMP_API_KEY}", timeout=15)
        cash_flow = session.get(f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker.upper()}?limit=5&apikey={FMP_API_KEY}", timeout=15)
        income_quarterly = session.get(f"https://financialmodelingprep.com/api/v3/income-statement/{ticker.upper()}?period=quarter&limit=4&apikey={FMP_API_KEY}", timeout=15)
        analyst = session.get(f"https://financialmodelingprep.com/api/v4/analyst-estimates/{ticker.upper()}?apikey={FMP_API_KEY}", timeout=15)
        data = {}
        if profile.status_code == 200 and profile.json():
            data.update(profile.json()[0])
            data["market_cap"] = profile.json()[0].get("mktCap")
            logging.debug(f"Odpowiedź profile z FMP dla {ticker}: status={profile.status_code}, dane={profile.json()[0]}")
        if quote.status_code == 200 and quote.json():
            data.update(quote.json()[0])
            logging.debug(f"Odpowiedź quote z FMP dla {ticker}: status={quote.status_code}, dane={quote.json()[0]}")
        if ratios.status_code == 200 and ratios.json():
            data.update(ratios.json()[0])
            data["ebitda_margin"] = ratios.json()[0].get("ebitdaMargin")
            data["roic"] = ratios.json()[0].get("returnOnInvestedCapital")
            data["interest_coverage"] = ratios.json()[0].get("interestCoverage")
            data["net_debt_ebitda"] = ratios.json()[0].get("netDebtToEBITDA")
            data["inventory_turnover"] = ratios.json()[0].get("inventoryTurnover")
            data["asset_turnover"] = ratios.json()[0].get("assetTurnover")
            logging.debug(f"Odpowiedź ratios z FMP dla {ticker}: status={ratios.status_code}, dane={ratios.json()[0]}")
        if income.status_code == 200 and income.json():
            data["revenue"] = income.json()[0].get("revenue")
            data["operating_margin"] = income.json()[0].get("operatingMargin")
            data["profit_margin"] = income.json()[0].get("netProfitMargin")
            data["yearly_revenue"] = [
                {"date": entry["date"], "revenue": float(entry["revenue"]) if entry["revenue"] else None}
                for entry in income.json()[:5]
            ]
            logging.debug(f"Odpowiedź income z FMP dla {ticker}: status={income.status_code}, dane={income.json()}")
        if balance.status_code == 200 and balance.json():
            data["total_debt"] = balance.json()[0].get("totalDebt")
            data["total_equity"] = balance.json()[0].get("totalEquity")
            data["quick_ratio"] = balance.json()[0].get("quickRatio")
            data["cash_ratio"] = balance.json()[0].get("cashRatio")
            data["debt_equity"] = (
                float(balance.json()[0].get("totalDebt", 0)) / float(balance.json()[0].get("totalEquity", 1))
                if balance.json()[0].get("totalEquity") and float(balance.json()[0].get("totalEquity")) != 0
                else None
            )
            logging.debug(f"Odpowiedź balance z FMP dla {ticker}: status={balance.status_code}, dane={balance.json()[0]}")
        if cash_flow.status_code == 200 and cash_flow.json():
            data["free_cash_flow"] = cash_flow.json()[0].get("freeCashFlow")
            data["operating_cash_flow"] = cash_flow.json()[0].get("operatingCashFlow")
            data["cash_flow_to_debt_ratio"] = cash_flow.json()[0].get("cashFlowToDebtRatio")
            logging.debug(f"Odpowiedź cash flow z FMP dla {ticker}: status={cash_flow.status_code}, dane={cash_flow.json()[0]}")
        if income_quarterly.status_code == 200 and income_quarterly.json():
            data["quarterly_revenue"] = [
                {"date": entry["date"], "revenue": float(entry["revenue"]) if entry["revenue"] else None}
                for entry in income_quarterly.json()[:4]
            ]
            logging.debug(f"Odpowiedź income quarterly z FMP dla {ticker}: status={income_quarterly.status_code}, dane={income_quarterly.json()}")
        if analyst.status_code == 200 and analyst.json():
            data["average_price_target"] = analyst.json()[0].get("averagePriceTarget")
            data["recommendation_mean"] = analyst.json()[0].get("recommendationMean")
            data["earnings_growth"] = analyst.json()[0].get("earningsGrowth")
            logging.debug(f"Odpowiedź analyst z FMP dla {ticker}: status={analyst.status_code}, dane={analyst.json()[0]}")
        data["user_growth"] = None
        data["ffo"] = None
        data["ltv"] = None
        data["rnd_sales"] = None
        data["cac_ltv"] = None
        logging.debug(f"Surowe dane z FMP dla {ticker}: {data}")
        return map_api_fields("FMP", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z FMP dla {ticker}: {str(e)}")
        return {}

def fetch_from_finnhub(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z Finnhub dla podanego tickera.
    Args:
        ticker: Symbol tickera (np. 'AAPL').
        data_type: Typ danych ('company').
    Returns:
        Słownik z danymi lub pusty słownik w przypadku błędu.
    """
    try:
        if data_type != "company":
            logging.info(f"Pomijam Finnhub dla {data_type}, używane tylko dla spółek")
            return {}
        valid_key = None
        for key in FINNHUB_API_KEYS:
            if key and not key.startswith("your_"):
                valid_key = key
                break
        if not valid_key:
            logging.warning("Pomijam Finnhub: brak prawidłowego klucza API")
            return {}
        profile = session.get(f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker.upper()}&token={valid_key}", timeout=15)
        quote = session.get(f"https://finnhub.io/api/v1/quote?symbol={ticker.upper()}&token={valid_key}", timeout=15)
        recommendation = session.get(f"https://finnhub.io/api/v1/stock/recommendation?symbol={ticker.upper()}&token={valid_key}", timeout=15)
        financials = session.get(f"https://finnhub.io/api/v1/stock/metric?symbol={ticker.upper()}&metric=all&token={valid_key}", timeout=15)
        data = {}
        if profile.status_code == 200 and profile.json():
            data.update(profile.json())
            data["market_cap"] = profile.json().get("marketCapitalization")
            logging.debug(f"Odpowiedź profile z Finnhub dla {ticker}: status={profile.status_code}, dane={profile.json()}")
        if quote.status_code == 200 and quote.json():
            data.update(quote.json())
            logging.debug(f"Odpowiedź quote z Finnhub dla {ticker}: status={quote.status_code}, dane={quote.json()}")
        if recommendation.status_code == 200 and recommendation.json():
            data["targetMeanPrice"] = recommendation.json()[0].get("targetPrice")
            data["recommendationMean"] = recommendation.json()[0].get("rating")
            logging.debug(f"Odpowiedź recommendation z Finnhub dla {ticker}: status={recommendation.status_code}, dane={recommendation.json()}")
        if financials.status_code == 200 and financials.json():
            data["ebitda_margin"] = financials.json().get("ebitdaMarginTTM")
            data["roic"] = financials.json().get("roicTTM")
            data["revenue_growth"] = financials.json().get("revenueGrowthTTM")
            data["gross_margin"] = financials.json().get("grossMarginTTM")
            data["operating_margin"] = financials.json().get("operatingMarginTTM")
            data["profit_margin"] = financials.json().get("netMarginTTM")
            data["free_cash_flow"] = financials.json().get("freeCashFlowTTM")
            data["eps_ttm"] = financials.json().get("epsTTM")
            logging.debug(f"Odpowiedź financials z Finnhub dla {ticker}: status={financials.status_code}, dane={financials.json()}")
        data["user_growth"] = None
        data["interest_coverage"] = None
        data["net_debt_ebitda"] = None
        data["inventory_turnover"] = None
        data["asset_turnover"] = None
        data["operating_cash_flow"] = None
        data["ffo"] = None
        data["ltv"] = None
        data["rnd_sales"] = None
        data["cac_ltv"] = None
        logging.debug(f"Surowe dane z Finnhub dla {ticker}: {data}")
        return map_api_fields("Finnhub", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z Finnhub dla {ticker}: {str(e)}")
        return {}

def fetch_from_yahooquery(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z YahooQuery dla podanego tickera.
    Args:
        ticker: Symbol tickera (np. 'AAPL').
        data_type: Typ danych ('company' lub 'etf').
    Returns:
        Słownik z danymi lub pusty słownik w przypadku błędu.
    """
    try:
        if data_type not in ["company", "etf"]:
            logging.info(f"Pomijam yahooquery dla {data_type}, używane tylko dla spółek i ETF")
            return {}
        if YahooQueryTicker is None:
            logging.warning("Pomijam yahooquery: moduł nie jest dostępny")
            return {}
        ticker_obj = YahooQueryTicker(ticker.upper())
        data = {}
        summary = ticker_obj.summary_profile
        if summary and ticker.upper() in summary and isinstance(summary[ticker.upper()], dict):
            data.update(summary[ticker.upper()])
            logging.debug(f"Odpowiedź summary z yahooquery dla {ticker}: {summary[ticker.upper()]}")
        financials = ticker_obj.financial_data
        if financials and ticker.upper() in financials and isinstance(financials[ticker.upper()], dict):
            data.update(financials[ticker.upper()])
            data["market_cap"] = financials[ticker.upper()].get("marketCap")
            data["ebitda_margin"] = financials[ticker.upper()].get("ebitdaMargin")
            data["roic"] = financials[ticker.upper()].get("returnOnInvestedCapital")
            data["interest_coverage"] = financials[ticker.upper()].get("interestCoverage")
            data["net_debt_ebitda"] = financials[ticker.upper()].get("netDebtToEBITDA")
            logging.debug(f"Odpowiedź financials z yahooquery dla {ticker}: {financials[ticker.upper()]}")
        key_stats = ticker_obj.key_stats
        if key_stats and ticker.upper() in key_stats and isinstance(key_stats[ticker.upper()], dict):
            data.update(key_stats[ticker.upper()])
            logging.debug(f"Odpowiedź key stats z yahooquery dla {ticker}: {key_stats[ticker.upper()]}")
        income = ticker_obj.income_statement(frequency="q")
        if not income.empty:
            data["quarterly_revenue"] = [
                {"date": str(index[1]), "revenue": float(row.get("TotalRevenue", None)) if row.get("TotalRevenue") else None}
                for index, row in income.head(4).iterrows() if row.get("TotalRevenue") is not None
            ]
            logging.debug(f"Odpowiedź income quarterly z yahooquery dla {ticker}: {income.to_dict()}")
        yearly_income = ticker_obj.income_statement(frequency="a")
        if not yearly_income.empty:
            data["yearly_revenue"] = [
                {"date": str(index[1]), "revenue": float(row.get("TotalRevenue", None)) if row.get("TotalRevenue") else None}
                for index, row in yearly_income.head(5).iterrows() if row.get("TotalRevenue") is not None
            ]
            data["revenue"] = (
                float(yearly_income["TotalRevenue"].iloc[0]) if not yearly_income.empty and yearly_income["TotalRevenue"].iloc[0]
                else None
            )
            logging.debug(f"Odpowiedź income yearly z yahooquery dla {ticker}: {yearly_income.to_dict()}")
        data["user_growth"] = None
        data["inventory_turnover"] = None
        data["asset_turnover"] = None
        data["operating_cash_flow"] = None
        data["ffo"] = None
        data["ltv"] = None
        data["rnd_sales"] = None
        data["cac_ltv"] = None
        logging.debug(f"Surowe dane z yahooquery dla {ticker}: {data}")
        return map_api_fields("yahooquery", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z yahooquery dla {ticker}: {str(e)}")
        return {}

def fetch_from_marketwatch(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z MarketWatch za pomocą scrapera.
    Args:
        ticker: Symbol tickera (np. 'AAPL').
        data_type: Typ danych ('company').
    Returns:
        Słownik z danymi lub pusty słownik w przypadku błędu.
    """
    try:
        if data_type != "company":
            logging.info(f"Pomijam MarketWatch dla {data_type}, używane tylko dla spółek")
            return {}
        time.sleep(1)  # Opóźnienie dla uniknięcia blokady
        data = scrape_marketwatch(ticker)
        logging.debug(f"Surowe dane z MarketWatch dla {ticker}: {data}")
        return map_api_fields("MarketWatch", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z MarketWatch dla {ticker}: {str(e)}")
        return {}

def fetch_from_investing(ticker: str, data_type: str = "company") -> dict:
    """
    Pobiera dane z Investing.com za pomocą scrapera.
    Args:
        ticker: Symbol tickera (np. 'AAPL').
        data_type: Typ danych ('company').
    Returns:
        Słownik z danymi lub pusty słownik w przypadku błędu.
    """
    try:
        if data_type != "company":
            logging.info(f"Pomijam Investing.com dla {data_type}, używane tylko dla spółek")
            return {}
        time.sleep(1)  # Opóźnienie dla uniknięcia blokady
        data = scrape_investing(ticker)
        logging.debug(f"Surowe dane z Investing.com dla {ticker}: {data}")
        return map_api_fields("Investing", data)
    except Exception as e:
        logging.error(f"Błąd pobierania danych z Investing.com dla {ticker}: {str(e)}")
        return {}

def fetch_data(tickers, parent=None, data_type="company"):
    """
    Pobiera dane z wielu API dla listy tickerów, uzupełniając brakujące pola.
    Args:
        tickers: Lista tickerów (np. ['AAPL', 'MSFT']).
        parent: Rodzic okna dla GUI (opcjonalne).
        data_type: Typ danych ('company', 'etf', 'macro').
    Returns:
        Krotka (wyniki, brakujące tickery).
    """
    try:
        logging.info(f"Rozpoczęto pobieranie danych dla tickerów: {tickers}, typ: {data_type}")
        results = {}
        missing_tickers = {}
        required_keys = [
            "nazwa", "sektor", "cena", "pe_ratio", "forward_pe", "peg_ratio",
            "revenue_growth", "gross_margin", "debt_equity", "current_ratio",
            "roe", "free_cash_flow_margin", "eps_ttm", "price_to_book_ratio",
            "price_to_sales_ratio", "operating_margin", "profit_margin",
            "quick_ratio", "cash_ratio", "cash_flow_to_debt_ratio",
            "earnings_growth", "analyst_target_price", "analyst_rating",
            "quarterly_revenue", "yearly_revenue", "market_cap", "revenue",
            "ebitda_margin", "roic", "user_growth", "interest_coverage",
            "net_debt_ebitda", "inventory_turnover", "asset_turnover",
            "operating_cash_flow", "free_cash_flow", "ffo", "ltv", "rnd_sales",
            "cac_ltv"
        ] if data_type != "macro" else ["nazwa", "value"]
        for ticker in tickers:
            ticker = ticker.upper()
            results[ticker] = {
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
                "date": datetime.now().strftime("%Y-%m-%d")
            } if data_type != "macro" else {
                "ticker": ticker,
                "nazwa": ticker,
                "value": None,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            missing_tickers[ticker] = required_keys.copy()
        api_methods = [
            ("yfinance", fetch_from_yfinance),
            ("FMP", fetch_from_fmp),
            ("Alpha Vantage", fetch_from_alpha_vantage),
            ("Finnhub", fetch_from_finnhub),
            ("yahooquery", fetch_from_yahooquery),
            ("MarketWatch", fetch_from_marketwatch),
            ("Investing", fetch_from_investing)
        ]
        for api_name, method in api_methods:
            for ticker in tickers:
                try:
                    if ticker in missing_tickers and missing_tickers[ticker]:
                        data = method(ticker, data_type)
                        if data:
                            for key in missing_tickers[ticker][:]:
                                if key in data and data[key] is not None:
                                    results[ticker][key] = data[key]
                                    missing_tickers[ticker].remove(key)
                            logging.info(f"Pobrano dane z {api_name} dla {ticker}: {data}")
                        if not missing_tickers[ticker]:
                            del missing_tickers[ticker]
                        else:
                            logging.info(f"Brakujące klucze dla {ticker} po {api_name}: {missing_tickers[ticker]}")
                except Exception as e:
                    logging.error(f"Błąd pobierania danych z {api_name} dla {ticker}: {str(e)}")
                    continue
        logging.info(f"Zakończono pobieranie danych, brakujące tickery: {missing_tickers}")
        return results, missing_tickers
    except Exception as e:
        logging.error(f"Błąd podczas pobierania danych z API dla {tickers}: {str(e)}")
        return {}, {ticker: ["all"] for ticker in tickers}