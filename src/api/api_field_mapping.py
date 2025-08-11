# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\src\api\api_field_mapping.py
import logging
from src.core.sector_mapping import normalize_sector
from src.core.logging_config import setup_logging
from src.core.utils import format_number  # używany do formatowania market_cap na 'B/m'

setup_logging()


def map_api_fields(api_name: str, data: dict) -> dict:
    """
    Mapuje pola z różnych API na ujednolicony format aplikacji.
    Zasady normalizacji:
    - wartości procentowe: 0..100 (bez %), zaokrąglone do 2 miejsc, zwracane jako string (np. '54.32')
    - wartości liczbowe: zwracane jako string z dwoma miejscami po kropce (spójność formatu zapisu)
    - DUŻE liczby: 'market_cap' formatujemy jako 'XX.XXB' / 'XX.XXm' (zgodnie z testami),
      natomiast pozostałe (revenue, OCF, FCF...) jako liczby bez sufiksów (edytor formatuje do '130,497,000').
    - quarterly/yearly revenue: lista słowników {"date": ..., "revenue": <float>}
    """
    try:
        result = {
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
        }

        field_mappings = {
            "yfinance": {
                "longName": "nazwa",
                "sector": "sektor",
                "currentPrice": "cena",
                "trailingPE": "pe_ratio",
                "forwardPE": "forward_pe",
                "pegRatio": "peg_ratio",
                "revenueGrowth": "revenue_growth",
                "grossMargins": "gross_margin",
                "debtToEquity": "debt_equity",
                "currentRatio": "current_ratio",
                "returnOnEquity": "roe",
                "freeCashflow": "free_cash_flow",
                "trailingEps": "eps_ttm",
                "priceToBook": "price_to_book_ratio",
                "priceToSalesTrailing12Months": "price_to_sales_ratio",
                "operatingMargins": "operating_margin",
                "profitMargins": "profit_margin",
                "quickRatio": "quick_ratio",
                "cashRatio": "cash_ratio",
                "cashFlowToDebtRatio": "cash_flow_to_debt_ratio",
                "earningsGrowth": "earnings_growth",
                "targetMeanPrice": "analyst_target_price",
                "recommendationMean": "analyst_rating",
                "marketCap": "market_cap",
                "revenue": "revenue",
                "ebitdaMargins": "ebitda_margin",
                "returnOnAssets": "roic",
                "interestCoverage": "interest_coverage",
                "inventoryTurnover": "inventory_turnover",
                "assetTurnover": "asset_turnover",
                "operatingCashflow": "operating_cash_flow",
                "quarterly_revenue": "quarterly_revenue",
                "yearly_revenue": "yearly_revenue",
            },
            "Alpha Vantage": {
                "Name": "nazwa",
                "Sector": "sektor",
                "Price": "cena",
                "PERatio": "pe_ratio",
                "ForwardPE": "forward_pe",
                "PEGRatio": "peg_ratio",
                "EPS": "eps_ttm",
                "PriceToBookRatio": "price_to_book_ratio",
                "PriceToSalesRatioTTM": "price_to_sales_ratio",
                "OperatingMarginTTM": "operating_margin",
                "ProfitMargin": "profit_margin",
                "QuickRatio": "quick_ratio",
                "CashRatio": "cash_ratio",
                "CashFlowToDebtRatio": "cash_flow_to_debt_ratio",
                "AnalystTargetPrice": "analyst_target_price",
                "AnalystRating": "analyst_rating",
                "MarketCapitalization": "market_cap",
                "revenue": "revenue",
                "EBITDAMargin": "ebitda_margin",
                "ReturnOnCapitalEmployed": "roic",
                "InterestCoverage": "interest_coverage",
                "inventoryTurnover": "inventory_turnover",
                "assetTurnover": "asset_turnover",
                "operatingCashflow": "operating_cash_flow",
                "quarterly_revenue": "quarterly_revenue",
                "yearly_revenue": "yearly_revenue",
            },
            "FMP": {
                "companyName": "nazwa",
                "sector": "sektor",
                "price": "cena",
                "priceEarningsRatio": "pe_ratio",
                "forwardPE": "forward_pe",
                "priceEarningsToGrowthRatio": "peg_ratio",
                "earningsPerShare": "eps_ttm",
                "priceToBookRatio": "price_to_book_ratio",
                "priceToSalesRatio": "price_to_sales_ratio",
                "operatingMargin": "operating_margin",
                "netProfitMargin": "profit_margin",
                "quickRatio": "quick_ratio",
                "cashRatio": "cash_ratio",
                "cashFlowToDebtRatio": "cash_flow_to_debt_ratio",
                "earningsGrowth": "earnings_growth",
                "averagePriceTarget": "analyst_target_price",
                "recommendationMean": "analyst_rating",
                "mktCap": "market_cap",
                "revenue": "revenue",
                "ebitdaMargin": "ebitda_margin",
                "returnOnInvestedCapital": "roic",
                "interestCoverage": "interest_coverage",
                "inventoryTurnover": "inventory_turnover",
                "assetTurnover": "asset_turnover",
                "operatingCashFlow": "operating_cash_flow",
                "freeCashFlow": "free_cash_flow",
                "quarterly_revenue": "quarterly_revenue",
                "yearly_revenue": "yearly_revenue",
            },
            "Finnhub": {
                "name": "nazwa",
                "finnhubIndustry": "sektor",
                "c": "cena",
                "epsTTM": "eps_ttm",
                "revenueGrowthTTM": "revenue_growth",
                "grossMarginTTM": "gross_margin",
                "operatingMarginTTM": "operating_margin",
                "netMarginTTM": "profit_margin",
                "freeCashFlowTTM": "free_cash_flow",
                "targetPrice": "analyst_target_price",
                "rating": "analyst_rating",
                "marketCapitalization": "market_cap",
                "ebitdaMarginTTM": "ebitda_margin",
                "roicTTM": "roic",
                "quarterly_revenue": "quarterly_revenue",
                "yearly_revenue": "yearly_revenue",
            },
            "yahooquery": {
                "longName": "nazwa",
                "sector": "sektor",
                "currentPrice": "cena",
                "trailingPE": "pe_ratio",
                "forwardPE": "forward_pe",
                "quickRatio": "quick_ratio",
                "cashRatio": "cash_ratio",
                "cashFlowToDebtRatio": "cash_flow_to_debt_ratio",
                "earningsGrowth": "earnings_growth",
                "trailingEps": "eps_ttm",
                "priceToBook": "price_to_book_ratio",
                "priceToSales": "price_to_sales_ratio",
                "marketCap": "market_cap",
                "revenue": "revenue",
                "ebitdaMargin": "ebitda_margin",
                "returnOnInvestedCapital": "roic",
                "interestCoverage": "interest_coverage",
                "quarterly_revenue": "quarterly_revenue",
                "yearly_revenue": "yearly_revenue",
            },
            "MarketWatch": {
                "company_name": "nazwa",
                "sector": "sektor",
                "current_price": "cena",
                "pe_ratio": "pe_ratio",
                "forwardPE": "forward_pe",
                "pegRatio": "peg_ratio",
                "eps": "eps_ttm",
                "priceToBook": "price_to_book_ratio",
                "priceToSales": "price_to_sales_ratio",
                "operatingMargin": "operating_margin",
                "profitMargin": "profit_margin",
                "quickRatio": "quick_ratio",
                "cashRatio": "cash_ratio",
                "cashFlowToDebtRatio": "cash_flow_to_debt_ratio",
                "earningsGrowth": "earnings_growth",
                "analystTargetPrice": "analyst_target_price",
                "analystRating": "analyst_rating",
                "marketCap": "market_cap",
                "revenue": "revenue",
                "ebitdaMargin": "ebitda_margin",
                "returnOnInvestedCapital": "roic",
                "quarterly_revenue": "quarterly_revenue",
                "yearly_revenue": "yearly_revenue",
            },
            "Investing": {
                "company_name": "nazwa",
                "sector": "sektor",
                "current_price": "cena",
                "pe_ratio": "pe_ratio",
                "forwardPE": "forward_pe",
                "pegRatio": "peg_ratio",
                "eps": "eps_ttm",
                "priceToBook": "price_to_book_ratio",
                "priceToSales": "price_to_sales_ratio",
                "operatingMargin": "operating_margin",
                "profitMargin": "profit_margin",
                "quickRatio": "quick_ratio",
                "cashRatio": "cash_ratio",
                "cashFlowToDebtRatio": "cash_flow_to_debt_ratio",
                "earningsGrowth": "earnings_growth",
                "analystTargetPrice": "analyst_target_price",
                "analystRating": "analyst_rating",
                "marketCap": "market_cap",
                "revenue": "revenue",
                "ebitdaMargin": "ebitda_margin",
                "returnOnInvestedCapital": "roic",
                "quarterly_revenue": "quarterly_revenue",
                "yearly_revenue": "yearly_revenue",
            },
        }

        mapping = field_mappings.get(api_name, {})
        for api_key, internal_key in mapping.items():
            if api_key in data and data[api_key] not in [None, "", "-", "NA", "N/A", "nan"]:
                result[internal_key] = data[api_key]

        # Normalizacja sektora
        if result["sektor"]:
            try:
                result["sektor"] = normalize_sector(result["sektor"])
            except Exception as e:
                logging.error(f"Błąd normalizacji sektora dla {result.get('nazwa', 'nieznana spółka')}: {str(e)}")
                result["sektor"] = None

        # Procenty → 0..100, bez znaku '%'
        percent_fields = [
            "revenue_growth", "gross_margin", "ebitda_margin", "operating_margin",
            "profit_margin", "roe", "free_cash_flow_margin", "roic",
            "earnings_growth"
        ]
        for field in percent_fields:
            if result[field] is not None:
                try:
                    value = float(result[field])
                    if value <= 1.0:
                        value *= 100.0
                    result[field] = f"{value:.2f}"
                except (ValueError, TypeError):
                    result[field] = None

        # Liczbowe zwykłe (bez znaków)
        numeric_fields = [
            "cena", "pe_ratio", "forward_pe", "peg_ratio", "eps_ttm",
            "price_to_book_ratio", "price_to_sales_ratio", "current_ratio",
            "quick_ratio", "cash_ratio", "cash_flow_to_debt_ratio",
            "analyst_target_price", "interest_coverage", "net_debt_ebitda",
            "inventory_turnover", "asset_turnover"
        ]
        for field in numeric_fields:
            if result[field] is not None:
                try:
                    result[field] = f"{float(result[field]):.2f}"
                except (ValueError, TypeError):
                    result[field] = None

        # debt_equity – ujednolicenie (ratio)
        if result["debt_equity"] is not None:
            try:
                value = float(result["debt_equity"])
                # jeśli wygląda na % (np. 120) a powinno być ratio ~1.2
                if value > 10.0:
                    value = value / 100.0
                result["debt_equity"] = f"{value:.2f}"
            except (ValueError, TypeError):
                result["debt_equity"] = None

        # market_cap – FORMAT z sufiksem (zgodnie z testami)
        if result["market_cap"] is not None:
            try:
                result["market_cap"] = format_number(float(result["market_cap"]))
            except Exception:
                result["market_cap"] = None

        # Pozostałe DUŻE wartości – bez sufiksów; zapis jako liczby (string z kropką)
        for field in ["revenue", "operating_cash_flow", "free_cash_flow", "ffo", "ltv"]:
            if result[field] is not None:
                try:
                    result[field] = f"{float(result[field]):.2f}"
                except (ValueError, TypeError):
                    result[field] = None

        # quarterly/yearly revenue listy
        for field in ["quarterly_revenue", "yearly_revenue"]:
            if isinstance(result[field], list):
                cleaned = []
                for item in result[field]:
                    if isinstance(item, dict) and "date" in item and "revenue" in item:
                        try:
                            rev = float(item["revenue"]) if item["revenue"] not in [None, "", "-", "NA", "N/A", "nan"] else None
                        except (ValueError, TypeError):
                            rev = None
                        cleaned.append({"date": item["date"], "revenue": rev, "is_manual": bool(item.get("is_manual", False))})
                result[field] = cleaned

        # Wyprowadź free_cash_flow_margin gdy możliwe
        if result["revenue"] is not None and result["free_cash_flow"] is not None:
            try:
                revenue = float(result["revenue"])
                fcf = float(result["free_cash_flow"])
                if revenue != 0:
                    result["free_cash_flow_margin"] = f"{(fcf / revenue * 100):.2f}"
            except Exception:
                pass

        return result
    except Exception as e:
        logging.error(f"Błąd mapowania danych z {api_name}: {str(e)}")
        return {}
