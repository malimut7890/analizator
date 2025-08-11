# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\src\core\utils.py
import json
import os
from src.core.logging_config import setup_logging
import logging
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

        # Najpierw próbuj UTF-8, potem UTF-8-SIG, a na końcu latin-1 (bez zależności od chardet)
        encodings = ["utf-8", "utf-8-sig", "latin-1"]
        last_exc = None
        for enc in encodings:
            try:
                with open(path, "r", encoding=enc) as f:
                    config = json.load(f)
                break
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                last_exc = e
                config = None
        if config is None:
            logging.error(f"Nie udało się wczytać pliku {path}: {last_exc}")
            return None

        if "indicators" not in config:
            logging.error(f"Plik {path} nie zawiera sekcji 'indicators'")
            return None

        # Walidacja sumy wag
        for phase, phase_config in config["indicators"].items():
            weights = phase_config.get("weights", {})
            if weights:
                weight_sum = sum(weights.values())
                if abs(weight_sum - 1.0) > 0.01 and weight_sum != 0:
                    logging.warning(
                        f"Suma wag dla fazy {phase} w sektorze {sector} wynosi {weight_sum}, powinna wynosić 1.0"
                    )
                    # Normalizacja wag (proporcjonalnie)
                    for indicator in list(weights.keys()):
                        weights[indicator] = weights[indicator] / weight_sum
                    logging.info(f"Znormalizowano wagi dla fazy {phase}: {weights}")

        return config
    except Exception as e:
        logging.error(f"Błąd wczytywania pliku {path}: {str(e)}")
        return None


def _strip_spaces(value: str) -> str:
    return value.replace(" ", "").strip()


def parse_number(value: str) -> float | None:
    """
    Parsuje różne formaty liczb zgodnie z zasadami edytora:

    Obsługiwane przypadki:
    - "37.68B" / "12.22m" (sufiksy)
    - "130,497,000" (separator tysięcy przecinkiem)
    - "3,2" (przecinek jako separator dziesiętny)
    - "1234.56" (kropka dziesiętna)
    - "-","NA","N/A","" -> None

    Zwraca float (wartość w jednostkach bazowych, bez sufiksów),
    albo None gdy brak wartości.
    """
    if value is None:
        return None
    s = str(value).strip()
    if s == "" or s.lower() in {"-", "na", "n/a", "none", "nan"}:
        return None

    s = _strip_spaces(s)
    s_upper = s.upper()

    # Obsługa sufiksów B/M
    m = re.match(r"^(-?\d+(?:[.,]\d+)?)([BM])$", s_upper)
    if m:
        num_txt, suf = m.groups()
        num_txt = num_txt.replace(",", ".")  # dopuszczamy przecinek jako dziesiętny
        try:
            num = float(num_txt)
        except ValueError:
            raise ValueError(f"Nieprawidłowy format liczby: {value}")
        if suf == "B":
            return num * 1_000_000_000
        if suf == "M":
            return num * 1_000_000
        return num  # nie powinno się zdarzyć

    # Przypadek z kropką dziesiętną i separatorami tysięcy
    # jeśli jest kropka, to przecinki traktujemy jako separatory tysięcy -> usuwamy
    if "." in s and "," in s:
        try:
            return float(s.replace(",", ""))
        except ValueError:
            pass  # spróbuj inne ścieżki

    # Przypadek z samymi przecinkami:
    # - jeśli jest dokładnie jeden przecinek i brak kropki -> traktuj jako separator dziesiętny
    # - jeśli jest wiele przecinków i brak kropki -> traktuj jako separatory tysięcy (usuń wszystkie)
    if "," in s and "." not in s:
        if s.count(",") == 1:
            try:
                return float(s.replace(",", "."))
            except ValueError:
                pass
        # wiele przecinków -> separatory tysięcy
        try:
            return float(s.replace(",", ""))
        except ValueError:
            pass

    # Prosty przypadek: tylko kropka dziesiętna lub tylko cyfry
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"Nieprawidłowy format liczby: {value}")


def format_large_int_grouped(value: float | int | str) -> str:
    """
    Do wyświetlania w edytorze dużych wartości (przychody, market cap itd.)
    Formatuje jako INTEGER z grupowaniem przecinkiem: 130,497,000
    """
    val = parse_number(value) if isinstance(value, str) else float(value)
    if val is None:
        return ""
    try:
        return f"{int(round(val)):,}"
    except Exception:
        logging.warning(f"Nie można sformatować dużej liczby: {value}")
        return ""


def format_float_for_editor(value: float | int | str, decimals: int = 2) -> str:
    """
    Dla wskaźników typu PE/ROE/margins itd. – zwraca string z przecinkiem dziesiętnym,
    bez znaków %, zgodnie z przykładem '3,2'.
    """
    if value is None or value == "":
        return ""
    num = parse_number(value) if isinstance(value, str) else float(value)
    if num is None:
        return ""
    txt = f"{num:.{decimals}f}"
    # zamień kropkę dziesiętną na przecinek
    if "." in txt:
        int_part, frac = txt.split(".")
        # usuń zbędne zera na końcu części ułamkowej
        frac = frac.rstrip("0")
        return f"{int_part},{frac}" if frac else int_part
    return txt


def format_number(value: float) -> str:
    """
    [ZACHOWANE dla kompatybilności w miejscach, gdzie był używany]
    Sformatuje liczbę na XX.XXB/XX.XXm lub zwykłe XX.XX.
    Nie używamy w edytorze, ale pozostaje dla ewentualnych raportów.
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
