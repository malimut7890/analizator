# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\tests\test_api_fetcher.py
import pytest
from unittest.mock import patch, Mock
from src.api.api_fetcher import (
    fetch_from_yfinance,
    fetch_from_alpha_vantage,
    fetch_from_fmp,
    fetch_from_finnhub,
    fetch_from_yahooquery,
    fetch_from_marketwatch,
    fetch_from_investing
)

def test_fetch_from_yfinance_success():
    """Testuje pobieranie danych z Yahoo Finance dla wszystkich pól."""
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.info = {
            "longName": "Apple Inc.",
            "sector": "Technology",
            "currentPrice": 150.0,
            "trailingPE": 25.0,
            "forwardPE": 20.0,
            "pegRatio": 1.5,
            "revenueGrowth": 0.2,
            "grossMargins": 0.4,
            "debtToEquity": 150.0,
            "currentRatio": 1.2,
            "returnOnEquity": 0.3,
            "freeCashflow": 800000000,
            "trailingEps": 5.0,
            "priceToBook": 10.0,
            "priceToSalesTrailing12Months": 5.0,
            "operatingMargins": 0.25,
            "profitMargins": 0.2,
            "quickRatio": 1.0,
            "cashRatio": 0.5,
            "cashFlowToDebtRatio": 0.3,
            "earningsGrowth": 0.15,
            "targetMeanPrice": 160.0,
            "recommendationMean": "Buy",
            "marketCap": 2000000000000,
            "ebitdaMargins": 0.3,
            "returnOnAssets": 0.15,
            "interestCoverage": 10.0,
            "inventoryTurnover": 5.0,
            "assetTurnover": 1.2,
            "operatingCashflow": 1000000000
        }
        mock_ticker.return_value.history.return_value = Mock(empty=False, __getitem__=lambda x, y: {"Close": [150.0]})
        mock_ticker.return_value.quarterly_financials = Mock(empty=False, iterrows=lambda: [(None, {"Total Revenue": 1000000000})])
        mock_ticker.return_value.financials = Mock(empty=False, iterrows=lambda: [(None, {"Total Revenue": 2000000000})])
        result = fetch_from_yfinance("AAPL")
        assert result["nazwa"] == "Apple Inc."
        assert result["sektor"] == "Technology"
        assert result["cena"] == "150.00"
        assert result["revenue_growth"] == "20.00"
        assert result["ebitda_margin"] == "30.00"
        assert result["market_cap"] == "2000.00B"
        assert result["revenue"] == "2000.00B"
        assert result["quarterly_revenue"][0]["revenue"] == "1000.00m"

def test_fetch_from_alpha_vantage_success():
    """Testuje pobieranie danych z Alpha Vantage dla wszystkich pól."""
    with patch("requests.Session.get") as mock_get, patch("alpha_vantage.fundamentaldata.FundamentalData") as mock_fd:
        mock_fd.return_value.get_company_overview.return_value = (
            {
                "Name": "Apple Inc.",
                "Sector": "Technology",
                "MarketCapitalization": "2000000000000",
                "EBITDAMargin": "0.3",
                "ReturnOnCapitalEmployed": "0.15",
                "PERatio": "25.0",
                "ForwardPE": "20.0",
                "PEGRatio": "1.5",
                "EPS": "5.0",
                "PriceToBookRatio": "10.0",
                "PriceToSalesRatioTTM": "5.0",
                "OperatingMarginTTM": "0.25",
                "ProfitMargin": "0.2",
                "QuickRatio": "1.0",
                "CashRatio": "0.5",
                "CashFlowToDebtRatio": "0.3",
                "AnalystTargetPrice": "160.0",
                "AnalystRating": "Buy",
                "InterestCoverage": "10.0",
                "inventoryTurnover": "5.0",
                "assetTurnover": "1.2",
                "operatingCashflow": "1000000000"
            },
            None
        )
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: {"Global Quote": {"05. price": "150.00"}}),
            Mock(status_code=200, json=lambda: {
                "quarterlyReports": [{"fiscalDateEnding": "2023-12-31", "totalRevenue": "1000000000"}],
                "annualReports": [{"fiscalDateEnding": "2023-12-31", "totalRevenue": "2000000000"}]
            }),
            Mock(status_code=200, json=lambda: {
                "quarterlyReports": [{"totalLiabilities": "1000000000", "totalShareholderEquity": "2000000000"}]
            }),
            Mock(status_code=200, json=lambda: {
                "quarterlyReports": [{"operatingCashflow": "1000000000", "capitalExpenditures": "200000000"}]
            })
        ]
        result = fetch_from_alpha_vantage("AAPL")
        assert result["nazwa"] == "Apple Inc."
        assert result["sektor"] == "Technology"
        assert result["cena"] == "150.00"
        assert result["ebitda_margin"] == "30.00"
        assert result["market_cap"] == "2000.00B"
        assert result["revenue"] == "2000.00B"
        assert result["quarterly_revenue"][0]["revenue"] == "1000.00m"

def test_fetch_from_fmp_success():
    """Testuje pobieranie danych z FMP dla wszystkich pól."""
    with patch("requests.Session.get") as mock_get:
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: [{"companyName": "Apple Inc.", "sector": "Technology", "mktCap": 2000000000000}]),
            Mock(status_code=200, json=lambda: [{"price": 150.0}]),
            Mock(status_code=200, json=lambda: [{
                "ebitdaMargin": 0.3,
                "returnOnInvestedCapital": 0.15,
                "inventoryTurnover": 5.0,
                "assetTurnover": 1.2,
                "priceEarningsRatio": 25.0,
                "forwardPE": 20.0,
                "priceEarningsToGrowthRatio": 1.5,
                "earningsPerShare": 5.0,
                "priceToBookRatio": 10.0,
                "priceToSalesRatio": 5.0,
                "operatingMargin": 0.25,
                "netProfitMargin": 0.2,
                "quickRatio": 1.0,
                "cashRatio": 0.5,
                "cashFlowToDebtRatio": 0.3,
                "earningsGrowth": 0.15,
                "interestCoverage": 10.0
            }]),
            Mock(status_code=200, json=lambda: [{"revenue": 2000000000, "operatingMargin": 0.25, "netProfitMargin": 0.2}]),
            Mock(status_code=200, json=lambda: [{"totalDebt": 1000000000, "totalEquity": 2000000000, "currentRatio": 1.2, "returnOnEquity": 0.3}]),
            Mock(status_code=200, json=lambda: [{"freeCashFlow": 800000000, "operatingCashFlow": 1000000000}]),
            Mock(status_code=200, json=lambda: [{"revenue": 1000000000, "date": "2023-12-31"}]),
            Mock(status_code=200, json=lambda: [{"averagePriceTarget": 160.0, "recommendationMean": "Buy"}])
        ]
        result = fetch_from_fmp("AAPL")
        assert result["nazwa"] == "Apple Inc."
        assert result["sektor"] == "Technology"
        assert result["cena"] == "150.00"
        assert result["ebitda_margin"] == "30.00"
        assert result["market_cap"] == "2000.00B"
        assert result["revenue"] == "2000.00B"
        assert result["quarterly_revenue"][0]["revenue"] == "1000.00m"

def test_fetch_from_finnhub_success():
    """Testuje pobieranie danych z Finnhub dla wszystkich pól."""
    with patch("requests.Session.get") as mock_get:
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: {"name": "Apple Inc.", "finnhubIndustry": "Technology", "marketCapitalization": 2000000000000}),
            Mock(status_code=200, json=lambda: {"c": 150.0}),
            Mock(status_code=200, json=lambda: [{"targetPrice": 160.0, "rating": "Buy"}]),
            Mock(status_code=200, json=lambda: {
                "ebitdaMarginTTM": 0.3,
                "roicTTM": 0.15,
                "revenueGrowthTTM": 0.2,
                "grossMarginTTM": 0.4,
                "operatingMarginTTM": 0.25,
                "netMarginTTM": 0.2,
                "freeCashFlowTTM": 800000000,
                "epsTTM": 5.0
            })
        ]
        result = fetch_from_finnhub("AAPL")
        assert result["nazwa"] == "Apple Inc."
        assert result["sektor"] == "Technology"
        assert result["cena"] == "150.00"
        assert result["revenue_growth"] == "20.00"
        assert result["ebitda_margin"] == "30.00"
        assert result["market_cap"] == "2000.00B"

def test_fetch_from_yahooquery_success():
    """Testuje pobieranie danych z YahooQuery dla wszystkich pól."""
    with patch("yahooquery.Ticker") as mock_ticker:
        mock_ticker.return_value.summary_profile = {"AAPL": {"sector": "Technology"}}
        mock_ticker.return_value.financial_data = {"AAPL": {
            "marketCap": 2000000000000,
            "ebitdaMargin": 0.3,
            "returnOnInvestedCapital": 0.15,
            "currentPrice": 150.0,
            "trailingPE": 25.0,
            "forwardPE": 20.0,
            "quickRatio": 1.0,
            "cashRatio": 0.5,
            "cashFlowToDebtRatio": 0.3,
            "earningsGrowth": 0.15,
            "interestCoverage": 10.0
        }}
        mock_ticker.return_value.key_stats = {"AAPL": {
            "priceToBook": 10.0,
            "priceToSales": 5.0,
            "trailingEps": 5.0
        }}
        mock_ticker.return_value.income_statement.return_value = Mock(
            empty=False,
            iterrows=lambda: [(("AAPL", "2023-12-31"), {"TotalRevenue": 1000000000})],
            __getitem__=lambda x, y: [1000000000]
        )
        result = fetch_from_yahooquery("AAPL")
        assert result["nazwa"] is None
        assert result["sektor"] == "Technology"
        assert result["cena"] == "150.00"
        assert result["ebitda_margin"] == "30.00"
        assert result["market_cap"] == "2000.00B"
        assert result["quarterly_revenue"][0]["revenue"] == "1000.00m"

def test_fetch_from_marketwatch_failure():
    """Testuje błąd pobierania danych z MarketWatch."""
    with patch("src.api.scraper.scrape_marketwatch") as mock_scrape:
        mock_scrape.side_effect = Exception("Błąd scrapowania")
        result = fetch_from_marketwatch("AAPL")
        assert result == {}

def test_fetch_from_investing_failure():
    """Testuje błąd pobierania danych z Investing.com."""
    with patch("src.api.scraper.scrape_investing") as mock_scrape:
        mock_scrape.side_effect = Exception("Błąd scrapowania")
        result = fetch_from_investing("AAPL")
        assert result == {}