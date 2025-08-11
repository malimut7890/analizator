# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\core\utils.py
import json
import os
from src.core.logging_config import setup_logging
import logging
import chardet
import re

setup_logging()

def load_sector_config(sector):
    """
    Wczytuje konfigurację dla danego sektora z pliku JSON i waliduje sumę wag.
    Args:
        sector: Nazwa sektora (np. 'Technology').
    Returns:
        Słownik konfiguracyjny lub None w przypadku błędu.
    """
    try:
        path = os.path.join("src", "core", "sectors", f"{sector.lower()}.json")
        if not os.path.exists(path):
            logging.error(f"Brak pliku konfiguracyjnego dla sektora {sector}: {path}")
            return None
        # Sprawdzenie kodowania pliku
        with open(path, "rb") as f:
            raw_data = f.read()
            if not raw_data:
                logging.error(f"Plik {path} jest pusty")
                return None
            result = chardet.detect(raw_data)
            encoding = result["encoding"] or "utf-8"
            logging.debug(f"Wykryto kodowanie pliku {path}: {encoding}")
        # Wczytanie pliku z wykrytym kodowaniem
        with open(path, "r", encoding=encoding) as f:
            config = json.load(f)
        if "indicators" not in config:
            logging.error(f"Plik {path} nie zawiera sekcji 'indicators'")
            return None
        # Walidacja sumy wag
        for phase, phase_config in config["indicators"].items():
            weights = phase_config.get("weights", {})
            if weights:
                weight_sum = sum(weights.values())
                if abs(weight_sum - 1.0) > 0.01:
                    logging.warning(f"Suma wag dla fazy {phase} w sektorze {sector} wynosi {weight_sum}, powinna wynosić 1.0")
                    # Normalizacja wag
                    for indicator in weights:
                        weights[indicator] = weights[indicator] / weight_sum
                    logging.info(f"Znormalizowano wagi dla fazy {phase}: {weights}")
        return config
    except json.JSONDecodeError as e:
        logging.error(f"Błąd dekodowania JSON dla {path}: {str(e)}")
        return None
    except UnicodeDecodeError as e:
        logging.error(f"Błąd kodowania dla {path}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Błąd wczytywania pliku {path}: {str(e)}")
        return None

def format_number(value: float) -> str:
    """
    Formatuje liczbę na format XX.XXB (biliony) lub XX.XXm (miliony).
    Args:
        value: Wartość liczbowa.
    Returns:
        Formatowana wartość jako string (np. '37.68B', '12.22m').
    """
    if value is None:
        return ""
    try:
        abs_value = abs(float(value))
        if abs_value >= 1_000_000_000:
            return f"{abs_value / 1_000_000_000:.2f}B"
        elif abs_value >= 1_000_000:
            return f"{abs_value / 1_000_000:.2f}m"
        return f"{abs_value:.2f}"
    except (ValueError, TypeError):
        logging.warning(f"Nieprawidłowa wartość do formatowania: {value}")
        return ""

def parse_number(value: str) -> float:
    """
    Parsuje string w formacie XX.XXB lub XX.XXm na liczbę.
    Args:
        value: Wartość jako string (np. '37.68B', '12.22m').
    Returns:
        Wartość liczbowa jako float.
    Raises:
        ValueError: Jeśli format jest nieprawidłowy.
    """
    if not value:
        return None
    value = value.strip().upper()
    match = re.match(r"^-?(\d*\.?\d+)([BM])?$", value)
    if not match:
        raise ValueError(f"Nieprawidłowy format liczby: {value}")
    num = float(match.group(1))
    suffix = match.group(2)
    if suffix == "B":
        return num * 1_000_000_000
    elif suffix == "M":
        return num * 1_000_000
    return num