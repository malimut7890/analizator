# ŚCIEŻKA: tests/test_sector_mapping.py
import pytest

from src.core.sector_mapping import normalize_sector


def test_normalize_known_variants():
    assert normalize_sector("technology") == "Technology"
    assert normalize_sector("Tech") == "Technology"
    assert normalize_sector("Information Technology") == "Technology"
    assert normalize_sector("Health Care") == "Healthcare"
    assert normalize_sector("communication services") == "Communication Services"


def test_normalize_unknown_preserve_original():
    assert normalize_sector("TECH") == "TECH"               # brak .title()
    assert normalize_sector("AI/ML STARTUPS") == "AI/ML STARTUPS"
    assert normalize_sector("Semi-Conductors") == "Semi-Conductors"  # nie zmieniamy myślników
