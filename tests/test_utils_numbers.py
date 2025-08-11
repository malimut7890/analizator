# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\tests\test_utils_numbers.py
import pytest
from src.core.utils import parse_number, format_large_int_grouped, format_float_for_editor

@pytest.mark.parametrize("text,expected", [
    ("130,497,000", 130_497_000.0),
    ("3,2", 3.2),
    ("3.2", 3.2),
    ("1,234,567.89", 1234567.89),
    ("37.68B", 37_680_000_000.0),
    ("12.22m", 12_220_000.0),
    ("-", None),
    ("", None),
])
def test_parse_number(text, expected):
    assert parse_number(text) == expected

def test_format_large_int_grouped():
    assert format_large_int_grouped(130_497_000) == "130,497,000"

def test_format_float_for_editor():
    assert format_float_for_editor(3.2) == "3,2"
    assert format_float_for_editor("3,20") == "3,2"
    assert format_float_for_editor("10") == "10"
