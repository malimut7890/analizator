# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\api\api_keys.py
from dotenv import load_dotenv
import os
import logging
from src.core.logging_config import setup_logging

# Inicjalizacja logowania
setup_logging()

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
FMP_API_KEY = os.getenv("FMP_API_KEY")
FINNHUB_API_KEYS = [
    os.getenv("FINNHUB_API_KEY_1"),
    os.getenv("FINNHUB_API_KEY_2"),
    os.getenv("FINNHUB_API_KEY_3")
]

def get_api_key(key_name: str, finnhub_index: int = 0) -> str | None:
    """
    Zwraca klucz API na podstawie nazwy, z obsługą rotacji kluczy Finnhub.
    Args:
        key_name: Nazwa klucza API (np. 'ALPHA_VANTAGE_API_KEY', 'FINNHUB_API_KEY').
        finnhub_index: Indeks klucza Finnhub do użycia (domyślnie 0).
    Returns:
        Klucz API lub None, jeśli klucz jest nieprawidłowy.
    """
    try:
        if key_name == "FINNHUB_API_KEY":
            key_value = FINNHUB_API_KEYS[finnhub_index % len(FINNHUB_API_KEYS)]
        else:
            key_value = globals().get(key_name)
        if not key_value or key_value.startswith("your_"):
            logging.warning(f"Nieprawidłowy lub brakujący klucz API: {key_name}")
            return None
        return key_value
    except Exception as e:
        logging.error(f"Błąd podczas pobierania klucza API {key_name}: {str(e)}")
        return None

# Walidacja kluczy
for key_name, key_value in [
    ("ALPHA_VANTAGE_API_KEY", ALPHA_VANTAGE_API_KEY),
    ("FMP_API_KEY", FMP_API_KEY)
]:
    if not key_value or key_value.startswith("your_"):
        logging.warning(f"Nieprawidłowy lub brakujący klucz API: {key_name}")

for i, key in enumerate(FINNHUB_API_KEYS, 1):
    if not key or key.startswith("your_"):
        logging.warning(f"Nieprawidłowy lub brakujący klucz FINNHUB_API_KEY_{i}")