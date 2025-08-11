# src/core/sector_mapping.py
from typing import Dict, Optional

# Minimalne aliasy bez łączenia "Information Technology" z "Technology"
# (zachowujemy rozdzielność!)
SECTOR_ALIASES: Dict[str, str] = {
    "it": "Information Technology",
    "infotech": "Information Technology",
    "tech": "Technology",
    "financial services": "Financials",
    "fin services": "Financials",
    "health care": "Biotechnology",   # jeśli potrzebujesz innej mapy, zmień tu
    "biotech": "Biotechnology",
}

def normalize_sector(sector: Optional[str]) -> Optional[str]:
    if not sector:
        return None
    key = sector.strip().lower()
    # 1) aliasy
    if key in SECTOR_ALIASES:
        return SECTOR_ALIASES[key]
    # 2) bez aliasu – zwracamy oryginał (walidacja i tak jest po stronie CompanyData
    #    względem plików w src/core/sectors/)
    return sector.strip()
