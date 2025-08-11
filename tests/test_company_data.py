# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\tests\test_company_data.py
import os
import json
import tempfile

from src.core.company_data import CompanyData


def _mk_tmp_company(tmp_path) -> CompanyData:
    cd = CompanyData()
    cd.data_dir = str(tmp_path)
    return cd


def test_numeric_not_scaled_to_percent_and_debt_equity_normalization(tmp_path):
    cd = _mk_tmp_company(tmp_path)
    ticker = "TEST"
    cd.add_company(ticker)

    payload = {
        "ticker": ticker,
        # wartości <1 dla pól liczbowych – NIE powinny być mnożone przez 100
        "interest_coverage": 0.5,
        "net_debt_ebitda": 0.8,
        "inventory_turnover": 0.9,
        "asset_turnover": 0.7,
        "cac_ltv": 0.6,
        "rnd_sales": 0.4,
        # debt_equity z wartością >10 → dzielenie przez 100 (250 → 2.50)
        "debt_equity": 250,
    }

    cd.save_company_data(ticker, payload)

    file_path = os.path.join(cd.data_dir, f"{ticker}.json")
    assert os.path.exists(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        hist = json.load(f)

    latest = hist[-1]
    assert latest["interest_coverage"] == "0.50"
    assert latest["net_debt_ebitda"] == "0.80"
    assert latest["inventory_turnover"] == "0.90"
    assert latest["asset_turnover"] == "0.70"
    assert latest["cac_ltv"] == "0.60"
    assert latest["rnd_sales"] == "0.40"
    assert latest["debt_equity"] == "2.50"
