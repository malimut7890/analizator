# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\tests\test_revenue_trend_scoring.py
import pytest
from src.core.revenue_trend_scoring import (
    compute_quarterly_revenue_trend_points,
    compute_yearly_revenue_trend_points,
    compute_total_revenue_trend_points,
)

def test_quarterly_points_increase_when_adding_higher_q1_after_q4():
    qdata_2 = [
        {"date": "2024-Q3", "revenue": 100},
        {"date": "2024-Q4", "revenue": 110},
    ]
    qdata_3 = qdata_2 + [{"date": "2025-Q1", "revenue": 120}]
    ts2 = compute_quarterly_revenue_trend_points(qdata_2)
    ts3 = compute_quarterly_revenue_trend_points(qdata_3)
    assert ts2.points == 2
    assert ts3.points == 3
    assert ts3.direction == "up" and ts3.streak == 2

def test_quarterly_penalty_on_decline():
    qdata = [
        {"date": "2024-Q3", "revenue": 110},
        {"date": "2024-Q4", "revenue": 120},
        {"date": "2025-Q1", "revenue": 115},
    ]
    ts = compute_quarterly_revenue_trend_points(qdata)
    assert ts.direction == "down"
    assert ts.streak == 1
    assert ts.points == -3

def test_yearly_points_awarded_and_flip_on_decline():
    y2 = [
        {"date": "2023", "revenue": 1000},
        {"date": "2024", "revenue": 1100},  # +5 pkt (1 wzrost)
    ]
    y3 = y2 + [{"date": "2025", "revenue": 1200}]  # +10 pkt (2 wzrosty)
    y4 = y3 + [{"date": "2026", "revenue": 1150}]  # flip: -10 pkt (1 spadek)
    ts2 = compute_yearly_revenue_trend_points(y2)
    ts3 = compute_yearly_revenue_trend_points(y3)
    ts4 = compute_yearly_revenue_trend_points(y4)
    assert ts2.points == 5
    assert ts3.points == 10
    assert ts4.points == -10 and ts4.direction == "down" and ts4.streak == 1

def test_total_sums_quarterly_and_yearly_points():
    qdata = [
        {"date": "2024-Q3", "revenue": 100},
        {"date": "2024-Q4", "revenue": 110},  # +2
        {"date": "2025-Q1", "revenue": 120},  # +3 (2 wzrosty)
    ]
    ydata = [
        {"date": "2023", "revenue": 1000},
        {"date": "2024", "revenue": 1100},  # +5 (1 wzrost)
    ]
    q = compute_quarterly_revenue_trend_points(qdata)
    y = compute_yearly_revenue_trend_points(ydata)
    tot = compute_total_revenue_trend_points(qdata, ydata)
    assert q.points == 3 and y.points == 5
    assert tot.points == 8
