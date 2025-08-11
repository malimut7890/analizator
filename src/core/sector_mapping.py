# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\core\sector_mapping.py
from typing import Dict

# Mapowanie sektorów dla normalizacji nazw sektorów w aplikacji
SECTOR_MAPPING: Dict[str, str] = {
    "Information Technology": "Technology",
    "IT": "Technology",
    "Financial Services": "Financials",
    "Biotech": "Biotechnology",
    "Health Care": "Biotechnology",
    "TECHNOLOGY": "Technology",
    "FINANCIALS": "Financials",
    "BIOTECHNOLOGY": "Biotechnology",
    "technology": "Technology",
    "financials": "Financials",
    "biotechnology": "Biotechnology"
}

def normalize_sector(sector: str) -> str:
    """
    Normalizuje nazwę sektora na podstawie mapowania.

    Args:
        sector: Nazwa sektora do normalizacji (np. 'Information Technology').

    Returns:
        Znormalizowana nazwa sektora (np. 'Technology') lub oryginalna nazwa, jeśli nie znaleziono mapowania.

    Example:
        >>> normalize_sector("Information Technology")
        'Technology'
        >>> normalize_sector("Unknown Sector")
        'Unknown Sector'
    """
    return SECTOR_MAPPING.get(sector, sector).title()