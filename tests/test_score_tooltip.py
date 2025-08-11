# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\tests\test_score_tooltip.py
import json, os
from src.gui.score_tooltip import build_score_tooltip_for_ticker

def test_build_score_tooltip_for_ticker(tmp_path):
    data_dir = tmp_path
    ticker = "TTT"
    path = os.path.join(data_dir, f"{ticker}.json")
    history = [{
        "quarterly_revenue": [
            {"date": "2024-Q3", "revenue": 100},
            {"date": "2024-Q4", "revenue": 110},
            {"date": "2025-Q1", "revenue": 120},
        ],
        "yearly_revenue": [
            {"date": "2023", "revenue": 1000},
            {"date": "2024", "revenue": 1200},
        ],
    }]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    text = build_score_tooltip_for_ticker(ticker, str(data_dir))
    assert "Kwartalne: +3 pkt" in text
    assert "Roczne: +5 pkt" in text

def test_build_score_tooltip_no_data(tmp_path):
    text = build_score_tooltip_for_ticker("XYZ", str(tmp_path))
    assert "Brak danych o przychodach" in text
