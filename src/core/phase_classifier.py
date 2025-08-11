import logging
import os
from src.core.utils import load_sector_config
from src.core.logging_config import setup_logging
from typing import Optional

# Inicjalizacja logowania
setup_logging()

def classify_phase(sector: str, data: dict) -> Optional[str]:
    """
    Określa fazę rozwoju spółki na podstawie punktowej klasyfikacji.
    Args:
        sector: Nazwa sektora (np. 'Technology').
        data: Słownik z danymi finansowymi spółki.
    Returns:
        'Start-up', 'Wzrost', 'Dojrzałość', 'Schyłek' lub None.
    Example:
        >>> classify_phase("Technology", {"revenue_growth": 50, "eps_ttm": -1})
        'Start-up'
    """
    try:
        if not sector or sector.lower() not in [f.replace(".json", "") for f in os.listdir(os.path.join("src", "core", "sectors"))]:
            logging.error(f"Nieprawidłowy lub brakujący sektor: {sector}")
            return None
        config = load_sector_config(sector)
        if not config:
            logging.error(f"Brak konfiguracji dla sektora {sector}")
            return None

        def safe_float(value, default=None) -> float | None:
            MISSING = {None, "", "-", "NA", "N/A", "None", "nan"}
            if value in MISSING:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        phase_scores = {}
        any_data_available = False
        for phase, conditions in config["phase_classification"].items():
            score = 0
            for condition in conditions:
                indicator = condition["indicator"]
                value = safe_float(data.get(indicator))
                cond_type = condition["condition"]
                threshold = condition["value"]
                points = condition.get("points", 1)
                if value is not None:
                    any_data_available = True
                    if cond_type == ">":
                        if value > threshold:
                            score += points
                    elif cond_type == ">=":
                        if value >= threshold:
                            score += points
                    elif cond_type == "<":
                        if value < threshold:
                            score += points
                    elif cond_type == "<=":
                        if value <= threshold:
                            score += points
                    elif cond_type == "> or None":
                        if value is None or value > threshold:
                            score += points
            phase_scores[phase] = score

        if not any_data_available:
            logging.warning(f"Brak jakichkolwiek danych finansowych dla sektora {sector}, zwracam None")
            return None
        if not phase_scores:
            logging.warning(f"Brak danych do sklasyfikowania fazy dla sektora {sector}")
            return None
        best_phase = max(phase_scores, key=phase_scores.get)
        if phase_scores[best_phase] == 0:
            logging.warning(f"Żadna faza nie zdobyła punktów dla sektora {sector}, zwracam None")
            return None
        logging.info(f"Spółka sklasyfikowana w fazie {best_phase} dla sektora {sector} z punktami {phase_scores[best_phase]}")
        return best_phase
    except Exception as e:
        logging.error(f"Błąd klasyfikacji fazy dla sektora {sector}: {str(e)}")
        return None