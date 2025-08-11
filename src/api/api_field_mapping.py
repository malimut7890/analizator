# ŚCIEŻKA: src/api/api_field_mapping.py
"""
Ujednolicone mapowanie pól z różnych dostawców API/scraperów → nasz standard.

Zmiany:
- Usunięto automatyczną normalizację sektora (zostawiamy oryginalne brzmienie,
  np. "Information Technology" ≠ "Technology").
- Wspólna struktura SCRAPER_MAPPING dla 'MarketWatch' i 'Investing'.
- Zwracamy zawsze bazowe klucze: 'nazwa', 'sektor', 'cena' (gdy brak → None).
- Mapowanie 'currentRatio' → 'current_ratio' we wszystkich providerach, gdzie występuje.
"""

from __future__ import annotations
from typing import Dict, Any

# Wspólna mapa dla scraperów – jeden słownik, dwie nazwy źródeł
SCRAPER_MAPPING: Dict[str, str] = {
    "name": "nazwa",
    "sector": "sektor",
    "price": "cena",
    "ebitdaMargin": "ebitda_margin",
    "operatingMargin": "operating_margin",
    "netProfitMargin": "net_margin",
    "currentRatio": "current_ratio",
    "quickRatio": "quick_ratio",
    "cashRatio": "cash_ratio",
    "cashFlowToDebtRatio": "cash_flow_to_debt_ratio",
    "returnOnEquity": "roe",
    "returnOnAssets": "roa",
    "returnOnInvestedCapital": "roic",
    "inventoryTurnover": "inventory_turnover",
    "assetTurnover": "asset_turnover",
    "marketCap": "market_cap",
    "targetMeanPrice": "analyst_target_price",
    "recommendationMean": "analyst_rating",
}

MAPPINGS: Dict[str, Dict[str, str]] = {
    # yfinance.info
    "yfinance": {
        "longName": "nazwa",
        "sector": "sektor",
        "currentPrice": "cena",
        "trailingPE": "pe_ttm",
        "forwardPE": "pe_forward",
        "pegRatio": "peg",
        "revenueGrowth": "revenue_growth",
        "grossMargins": "gross_margin",
        "debtToEquity": "debt_to_equity",
        "currentRatio": "current_ratio",
        "returnOnEquity": "roe",
        "freeCashflow": "free_cash_flow",
        "trailingEps": "eps_ttm",
        "priceToBook": "pb",
        "priceToSalesTrailing12Months": "ps_ttm",
        "operatingMargins": "operating_margin",
        "profitMargins": "net_margin",
        "quickRatio": "quick_ratio",
        "cashRatio": "cash_ratio",
        "cashFlowToDebtRatio": "cash_flow_to_debt_ratio",
        "earningsGrowth": "earnings_growth",
        "targetMeanPrice": "analyst_target_price",
        "recommendationMean": "analyst_rating",
        "marketCap": "market_cap",
        "ebitdaMargins": "ebitda_margin",
        "returnOnAssets": "roa",
        "interestCoverage": "interest_coverage",
        "inventoryTurnover": "inventory_turnover",
        "assetTurnover": "asset_turnover",
        "operatingCashflow": "operating_cash_flow",
    },

    # Alpha Vantage – Company Overview
    "Alpha Vantage": {
        "Name": "nazwa",
        "Sector": "sektor",
        "Price": "cena",
        "PERatio": "pe_ttm",
        "ForwardPE": "pe_forward",
        "PEGRatio": "peg",
        "EBITDAMargin": "ebitda_margin",
        "ReturnOnCapitalEmployed": "roce",
        "EPS": "eps_ttm",
        "PriceToBookRatio": "pb",
        "PriceToSalesRatioTTM": "ps_ttm",
        "OperatingMarginTTM": "operating_margin",
        "ProfitMargin": "net_margin",
        "QuickRatio": "quick_ratio",
        "CashRatio": "cash_ratio",
        "CashFlowToDebtRatio": "cash_flow_to_debt_ratio",
        "AnalystTargetPrice": "analyst_target_price",
        "AnalystRating": "analyst_rating",
        "InterestCoverage": "interest_coverage",
        "inventoryTurnover": "inventory_turnover",
        "assetTurnover": "asset_turnover",
        "operatingCashflow": "operating_cash_flow",
        "MarketCapitalization": "market_cap",
        "ReturnOnEquityTTM": "roe",
        "ReturnOnAssetsTTM": "roa",
        "CurrentRatio": "current_ratio",
    },

    # Financial Modeling Prep (FMP)
    "FMP": {
        "companyName": "nazwa",
        "sector": "sektor",
        "price": "cena",
        "priceEarningsRatio": "pe_ttm",
        "forwardPE": "pe_forward",
        "priceEarningsToGrowthRatio": "peg",
        "earningsPerShare": "eps_ttm",
        "priceToBookRatio": "pb",
        "priceToSalesRatio": "ps_ttm",
        "ebitdaMargin": "ebitda_margin",
        "returnOnInvestedCapital": "roic",
        "operatingMargin": "operating_margin",
        "netProfitMargin": "net_margin",
        "quickRatio": "quick_ratio",
        "cashRatio": "cash_ratio",
        "cashFlowToDebtRatio": "cash_flow_to_debt_ratio",
        "earningsGrowth": "earnings_growth",
        "interestCoverage": "interest_coverage",
        "inventoryTurnover": "inventory_turnover",
        "assetTurnover": "asset_turnover",
        "mktCap": "market_cap",
        "currentRatio": "current_ratio",
        "returnOnEquity": "roe",
        "returnOnAssets": "roa",
        "operatingCashFlow": "operating_cash_flow",
        "freeCashFlow": "free_cash_flow",
    },

    # Finnhub
    "Finnhub": {
        "name": "nazwa",
        "finnhubIndustry": "sektor",
        "c": "cena",
        "ebitdaMarginTTM": "ebitda_margin",
        "roicTTM": "roic",
        "revenueGrowthTTM": "revenue_growth",
        "grossMarginTTM": "gross_margin",
        "operatingMarginTTM": "operating_margin",
        "netMarginTTM": "net_margin",
        "freeCashFlowTTM": "free_cash_flow",
        "epsTTM": "eps_ttm",
        "marketCapitalization": "market_cap",
        "currentRatioTTM": "current_ratio",
    },

    # YahooQuery
    "YahooQuery": {
        "longName": "nazwa",
        "sector": "sektor",
        "regularMarketPrice": "cena",
        "currentRatio": "current_ratio",
        "ebitdaMargins": "ebitda_margin",
        "returnOnAssets": "roa",
        "returnOnEquity": "roe",
        "marketCap": "market_cap",
    },

    # Scraperzy – wspólna mapa
    "MarketWatch": SCRAPER_MAPPING,
    "Investing": SCRAPER_MAPPING,
}


def map_api_fields(provider: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Przekształca dane z 'provider' na nasz kanoniczny słownik.
    Nie rzuca wyjątków – brakujące pola są ignorowane.

    Zwracane *zawsze* zawiera klucze: 'nazwa', 'sektor', 'cena' (gdy brak danych → None).
    """
    out: Dict[str, Any] = {"nazwa": None, "sektor": None, "cena": None}
    if not isinstance(data, dict):
        return out

    mapping = MAPPINGS.get(provider)
    if not mapping:
        return out

    for k_src, k_dst in mapping.items():
        if k_src in data:
            out[k_dst] = data[k_src]

    # Brak automatycznej normalizacji sektora — zachowujemy oryginał
    return out
