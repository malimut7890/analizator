
# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\src\api\api_keys.py
"""
Bezpieczne pobieranie kluczy API:
- Preferuj zmienne środowiskowe.
- Plik `.env` jest opcjonalny (tylko dev).
- Brak twardej zależności od `python-dotenv`.
"""
from __future__ import annotations

import os
import logging
from typing import Optional, List

from src.core.logging_config import setup_logging

# Konfiguracja logowania (singleton)
setup_logging()
logger = logging.getLogger(__name__)


def _load_dotenv_if_available() -> bool:
    """Spróbuj wczytać .env, jeśli moduł i plik istnieją. Zwróć True gdy wczytano."""
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        logger.debug("python-dotenv niedostępny – pomijam ładowanie .env")
        return False
    if os.path.exists(".env"):
        try:
            load_dotenv()
            logger.info("Załadowano lokalny plik .env (środowisko developerskie).")
            return True
        except Exception as e:
            logger.warning(f"Nie udało się wczytać .env: {e}")
            return False
    logger.debug(".env nie znaleziono – używam zmiennych środowiskowych.")
    return False


_LOAD_ENV_DONE = False
if not _LOAD_ENV_DONE:
    _LOAD_ENV_DONE = _load_dotenv_if_available()


def _normalize(value: Optional[str]) -> Optional[str]:
    """Zwraca None dla pustych wartości lub placeholderów 'your_*'."""
    if not value:
        return None
    v = value.strip()
    if not v or v.lower().startswith("your_"):
        return None
    return v


def _get_finnhub_keys_from_env(max_slots: int = 5) -> List[str]:
    """Zbierz FINNHUB_API_KEY_1..N, pomijając puste/placeholdery."""
    keys: List[str] = []
    for i in range(1, max_slots + 1):
        v = _normalize(os.getenv(f"FINNHUB_API_KEY_{i}"))
        if v:
            keys.append(v)
    return keys


def get_api_key(key_name: str, *, finnhub_index: int = 0) -> Optional[str]:
    """
    Pobierz klucz API wg nazwy.
    - Dla 'FINNHUB_API_KEY' obsługuje rotację po indeksie.
    - Zwraca None, jeśli brak prawidłowego klucza.

    Args:
        key_name: 'ALPHA_VANTAGE_API_KEY' | 'FMP_API_KEY' | 'FINNHUB_API_KEY'
        finnhub_index: indeks rotacji (0..n-1) dla FINNHUB
    """
    key_name = key_name.upper().strip()
    try:
        if key_name == "FINNHUB_API_KEY":
            keys = _get_finnhub_keys_from_env()
            if not keys:
                logger.warning("Brak skonfigurowanych kluczy FINNHUB_API_KEY_{i}")
                return None
            return keys[finnhub_index % len(keys)]
        return _normalize(os.getenv(key_name))
    except Exception as e:
        logger.error(f"Błąd podczas pobierania klucza API {key_name}: {e}")
        return None


# Wygodne stałe (mogą być None)
ALPHA_VANTAGE_API_KEY: Optional[str] = get_api_key("ALPHA_VANTAGE_API_KEY")
FMP_API_KEY: Optional[str] = get_api_key("FMP_API_KEY")
FINNHUB_API_KEYS: List[str] = _get_finnhub_keys_from_env()

# Ostrzeżenia (nie blokują uruchomienia)
for name, val in [
    ("ALPHA_VANTAGE_API_KEY", ALPHA_VANTAGE_API_KEY),
    ("FMP_API_KEY", FMP_API_KEY),
]:
    if not val:
        logger.warning(f"Nieprawidłowy lub brakujący klucz API: {name}")

if not FINNHUB_API_KEYS:
    logger.warning("Nieprawidłowe lub brakujące klucze FINNHUB_API_KEY_{i}")
