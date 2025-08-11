# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\core\scoring_calculator.py
import logging
from typing import Tuple, Dict, Union, Optional
from src.core.utils import load_sector_config
from src.core.logging_config import setup_logging
from src.core.company_data import CompanyData

# Inicjalizacja logowania
setup_logging()

def calculate_sector_phase_average(sector: str, phase: str, company_data: CompanyData) -> float:
    """
    Oblicza średnią punktację dla spółek w danym sektorze i fazie, wymagając minimum 3 danych.
    Args:
        sector: Nazwa sektora (np. 'Technology').
        phase: Faza rozwoju (np. 'Wzrost').
        company_data: Obiekt CompanyData z danymi spółek.
    Returns:
        Średnia punktacja lub 0, jeśli brak wystarczającej liczby danych.
    """
    try:
        scores = []
        for company in company_data.companies:
            if company.get("sektor") == sector and company.get("faza") == phase:
                score = company.get("punkty")
                if score not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                    scores.append(float(score))
        if len(scores) < 3:
            logging.warning(f"Niewystarczająca liczba spółek ({len(scores)}) dla sektora {sector}, faza {phase}. Zwracam 0.0")
            return 0.0
        avg = sum(scores) / len(scores)
        logging.info(f"Średnia punktacja dla sektora {sector}, faza {phase}: {avg:.2f}")
        return avg
    except Exception as e:
        logging.error(f"Błąd obliczania średniej dla sektora {sector}, faza {phase}: {str(e)}")
        return 0.0

def calculate_sector_average(sector: str, company_data: CompanyData) -> float:
    """
    Oblicza średnią punktację dla wszystkich spółek w danym sektorze, wymagając minimum 3 danych.
    Args:
        sector: Nazwa sektora (np. 'Technology').
        company_data: Obiekt CompanyData z danymi spółek.
    Returns:
        Średnia punktacja lub 0, jeśli brak wystarczającej liczby danych.
    """
    try:
        scores = []
        for company in company_data.companies:
            if company.get("sektor") == sector:
                score = company.get("punkty")
                if score not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                    scores.append(float(score))
        if len(scores) < 3:
            logging.warning(f"Niewystarczająca liczba spółek ({len(scores)}) dla sektora {sector}. Zwracam 0.0")
            return 0.0
        avg = sum(scores) / len(scores)
        logging.info(f"Średnia punktacja dla sektora {sector}: {avg:.2f}")
        return avg
    except Exception as e:
        logging.error(f"Błąd obliczania średniej dla sektora {sector}: {str(e)}")
        return 0.0

def calculate_overall_average(company_data: CompanyData) -> float:
    """
    Oblicza średnią punktację dla wszystkich spółek.
    Args:
        company_data: Obiekt CompanyData z danymi spółek.
    Returns:
        Średnia punktacja lub 0, jeśli brak danych.
    """
    try:
        scores = []
        for company in company_data.companies:
            score = company.get("punkty")
            if score not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                scores.append(float(score))
        avg = sum(scores) / len(scores) if scores else 0.0
        logging.info(f"Ogólna średnia punktacja: {avg:.2f}")
        return avg
    except Exception as e:
        logging.error(f"Błąd obliczania ogólnej średniej: {str(e)}")
        return 0.0

def calculate_sector_averages(sector: str, phase: str, company_data: CompanyData, indicators: list) -> Dict[str, float]:
    """
    Oblicza średnie sektorowe dla podanych wskaźników w danej fazie i sektorze, wymagając minimum 3 danych.
    Ujemne wartości są traktowane jako 0 w obliczeniach średniej.
    Args:
        sector: Nazwa sektora.
        phase: Faza rozwoju.
        company_data: Obiekt CompanyData.
        indicators: Lista wskaźników (np. ['revenue_growth', 'roe']).
    Returns:
        Słownik z średnimi sektorowymi dla każdego wskaźnika.
    """
    try:
        averages = {}
        config = load_sector_config(sector)
        if not config or phase not in config["indicators"]:
            logging.warning(f"Brak konfiguracji dla sektora {sector} lub fazy {phase}")
            return {indicator: None for indicator in indicators}
        main_indicators = config["indicators"][phase]["main"]
        for indicator in indicators:
            if indicator not in main_indicators:
                averages[indicator] = None
                continue
            values = []
            for company in company_data.companies:
                if company.get("sektor") == sector and company.get("faza") == phase:
                    value = company.get(indicator)
                    if value not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                        try:
                            float_value = float(value)
                            values.append(max(float_value, 0))  # Zamiana ujemnych na 0
                        except (ValueError, TypeError):
                            continue
            if len(values) >= 3:
                avg = sum(values) / len(values)
                averages[indicator] = round(avg, 2)
                logging.info(f"Średnia sektorowa dla {indicator} w sektorze {sector}, faza {phase}: {avg:.2f}")
            else:
                averages[indicator] = None
                logging.warning(f"Niewystarczająca liczba danych ({len(values)}) dla {indicator} w sektorze {sector}, faza {phase}")
        return averages
    except Exception as e:
        logging.error(f"Błąd obliczania średnich sektorowych dla sektora {sector}, faza {phase}: {str(e)}")
        return {indicator: None for indicator in indicators}

def calculate_trend(ticker: str, company_data: CompanyData, sector: str, phase: str) -> Tuple[Optional[float], Dict]:
    """
    Oblicza punkty za trendy przychodów (roczne i kwartalne) dla danej spółki.
    Args:
        ticker: Symbol giełdowy.
        company_data: Obiekt CompanyData z danymi historycznymi.
        sector: Nazwa sektora (np. 'Technology').
        phase: Faza rozwoju (np. 'Wzrost').
    Returns:
        Krotka (punkty za trendy, szczegóły trendów).
    """
    try:
        trend_points = None
        trend_details = {"revenue_trend": {"yearly": [], "quarterly": [], "points": 0.0, "warnings": []}}
        history = company_data.load_company_history(ticker)
        
        if not history:
            logging.warning(f"Brak danych historycznych dla {ticker} do analizy trendów")
            return None, trend_details
        
        config = load_sector_config(sector)
        if not config or phase not in config["indicators"]:
            logging.warning(f"Brak konfiguracji dla sektora {sector} lub fazy {phase}")
            return None, trend_details
        
        # Analiza trendów rocznych (revenue rok do roku)
        yearly_revenues = []
        for entry in sorted(history, key=lambda x: x.get("date", "")):
            revenue = entry.get("yearly_revenue", [])
            if isinstance(revenue, list) and revenue:
                for rev in revenue:
                    if rev.get("revenue") not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                        try:
                            yearly_revenues.append({"date": rev["date"], "revenue": float(rev["revenue"])})
                        except (ValueError, TypeError) as e:
                            logging.warning(f"Nieprawidłowa wartość przychodu rocznego dla {ticker}, data {rev.get('date')}: {str(e)}")
                            continue
        
        if len(yearly_revenues) >= 2:
            for i in range(1, len(yearly_revenues)):
                current = yearly_revenues[i]["revenue"]
                previous = yearly_revenues[i-1]["revenue"]
                if previous != 0:
                    growth = (current - previous) / previous * 100
                    trend_details["revenue_trend"]["yearly"].append({
                        "date": yearly_revenues[i]["date"],
                        "growth": round(growth, 2)
                    })
                    if growth < 0:
                        trend_details["revenue_trend"]["warnings"].append(f"Spadek przychodów w {yearly_revenues[i]['date']}: {growth:.2f}%")
        
        # Analiza trendów kwartalnych
        quarterly_revenues = []
        for entry in sorted(history, key=lambda x: x.get("date", "")):
            revenue = entry.get("quarterly_revenue", [])
            if isinstance(revenue, list) and revenue:
                for rev in revenue:
                    if rev.get("revenue") not in [None, "", "-", "NA", "N/A", "None", "nan"]:
                        try:
                            quarterly_revenues.append({"date": rev["date"], "revenue": float(rev["revenue"])})
                        except (ValueError, TypeError) as e:
                            logging.warning(f"Nieprawidłowa wartość przychodu kwartalnego dla {ticker}, data {rev.get('date')}: {str(e)}")
                            continue
        
        if len(quarterly_revenues) >= 3:
            growth_sequence = []
            valid_quarters = 0
            for i in range(1, len(quarterly_revenues)):
                current = quarterly_revenues[i]["revenue"]
                previous = quarterly_revenues[i-1]["revenue"]
                if previous != 0 and current is not None:
                    growth = (current - previous) / previous * 100
                    trend_details["revenue_trend"]["quarterly"].append({
                        "date": quarterly_revenues[i]["date"],
                        "growth": round(growth, 2)
                    })
                    growth_sequence.append(growth)
                    valid_quarters += 1
                    if growth < 0:
                        trend_details["revenue_trend"]["warnings"].append(f"Spadek przychodów w Q{quarterly_revenues[i]['date']}: {growth:.2f}%")
            
            # Punktacja za trendy kwartalne
            if valid_quarters >= 3:
                trend_points = 0.0
                last_three = growth_sequence[-3:]
                if all(g > 0 for g in last_three):
                    trend_points += 5.0
                    trend_details["revenue_trend"]["points"] += 5.0
                    logging.info(f"Dodano +5 pkt za 3 kolejne kwartały wzrostu przychodów dla {ticker}")
                elif len(growth_sequence) >= 2 and all(g < 0 for g in growth_sequence[-2:]):
                    trend_points -= 10.0
                    trend_details["revenue_trend"]["points"] -= 10.0
                    logging.info(f"Odjęto -10 pkt za 2 kolejne kwartały spadku przychodów dla {ticker}")
            else:
                logging.warning(f"Niewystarczająca liczba ważnych kwartałów ({valid_quarters}) dla {ticker} do analizy trendów")
                trend_points = None
        
        if trend_points is None:
            logging.warning(f"Brak wystarczających danych kwartalnych dla {ticker} do analizy trendów")
        return trend_points, trend_details
    except Exception as e:
        logging.error(f"Błąd obliczania trendów dla {ticker}: {str(e)}")
        return None, {"revenue_trend": {"yearly": [], "quarterly": [], "points": 0.0, "warnings": []}}

def calculate_score(sector: str, phase: str, data: dict, company_data: Optional[CompanyData] = None) -> Tuple[Union[float, None], Dict]:
    """
    Oblicza punktację (0-100) dla spółki w danym sektorze i fazie z bonusami i trendami.
    Ujemne wartości wskaźników są traktowane jako 0 w punktacji, ale zapisywane jako ujemne w danych.
    Wartości powyżej najwyższego progu są nagradzane proporcjonalnie.
    Args:
        sector: Nazwa sektora (np. 'Technology').
        phase: Faza rozwoju (np. 'Wzrost').
        data: Słownik z danymi finansowymi spółki.
        company_data: Obiekt CompanyData z danymi spółek (dla bonusów, średnich i trendów).
    Returns:
        Krotka (punktacja, szczegóły punktacji z listą użytych zastępnych, bonusów i trendów).
    """
    try:
        if not sector or not phase:
            logging.error(f"Brak sektora ({sector}) lub fazy ({phase})")
            return None, {"used_fallbacks": {}, "bonuses": {}, "indicators": {}, "sector_phase_avg": 0.0, "sector_avg": 0.0, "trend_details": {}}
        config = load_sector_config(sector)
        if not config or phase not in config["indicators"]:
            logging.error(f"Brak konfiguracji dla sektora {sector} lub fazy {phase}")
            return None, {"used_fallbacks": {}, "bonuses": {}, "indicators": {}, "sector_phase_avg": 0.0, "sector_avg": 0.0, "trend_details": {}}
        MISSING = {None, "", "-", "NA", "N/A", "None", "nan"}

        def safe_float(value, default=None) -> Optional[float]:
            if value in MISSING:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                logging.warning(f"Nieprawidłowa wartość: {value}, zwracam {default}")
                return default

        def get_fallback_value(indicator: str, data: dict, phase_config: dict) -> Tuple[Optional[float], Optional[Dict]]:
            if indicator in phase_config["fallback"]:
                fallbacks = sorted(phase_config["fallback"][indicator], key=lambda x: x["weight"], reverse=True)
                for fallback in fallbacks:
                    fallback_indicator = fallback["indicator"]
                    weight = fallback["weight"]
                    value = safe_float(data.get(fallback_indicator))
                    if value is not None:
                        logging.info(f"Użyto zastępczego wskaźnika {fallback_indicator}={value} dla {indicator} w sektorze {sector}, faza {phase}")
                        return value, {"indicator": fallback_indicator, "value": value, "weight": weight}
            return None, None

        score = 0.0
        score_details = {
            "used_fallbacks": {},
            "bonuses": {},
            "indicators": {},
            "sector_phase_avg": 0.0,
            "sector_avg": 0.0,
            "trend_details": {}
        }
        phase_config = config["indicators"][phase]
        thresholds = config["scoring_thresholds"][phase]
        weights = phase_config.get("weights", {indicator: 1.0 / len(phase_config["main"]) for indicator in phase_config["main"]})

        # Obliczanie dynamicznych progów dla wszystkich wskaźników
        dynamic_thresholds = {}
        sector_averages = {}
        if company_data:
            all_indicators = phase_config["main"] + [fb["indicator"] for ind in phase_config["fallback"] for fb in phase_config["fallback"][ind]]
            sector_averages = calculate_sector_averages(sector, phase, company_data, all_indicators)
            for indicator in all_indicators:
                avg = sector_averages.get(indicator)
                if avg is not None and indicator in phase_config["main"]:
                    static_thresholds = thresholds.get(indicator, [])
                    dynamic_thresholds[indicator] = []
                    for thresh in static_thresholds:
                        if thresh["condition"] in [">", ">="]:
                            new_threshold = thresh["threshold"] + (avg - static_thresholds[len(static_thresholds)//2]["threshold"])
                        else:
                            new_threshold = thresh["threshold"] - (avg - static_thresholds[len(static_thresholds)//2]["threshold"])
                        dynamic_thresholds[indicator].append({
                            "threshold": round(new_threshold, 2),
                            "points": thresh["points"],
                            "condition": thresh["condition"]
                        })
                    logging.info(f"Dynamiczne progi dla {indicator}: {dynamic_thresholds[indicator]}")
                else:
                    dynamic_thresholds[indicator] = thresholds.get(indicator, [])

        any_indicator_available = False
        for orig_indicator in phase_config["main"]:
            indicator = orig_indicator
            value = safe_float(data.get(indicator))
            indicator_weight = weights.get(orig_indicator, 1.0)
            fallback_info = None
            if value is None:
                value, fallback_info = get_fallback_value(orig_indicator, data, phase_config)
                if fallback_info:
                    score_details["used_fallbacks"][orig_indicator] = fallback_info
                    indicator = fallback_info["indicator"]
                    indicator_weight = fallback_info["weight"]
                else:
                    logging.warning(f"Brak danych i zastępnych dla {orig_indicator} w sektorze {sector}, faza {phase}")
                    score_details["indicators"][orig_indicator] = {"points": 0, "value": None, "weight": indicator_weight, "dynamic_thresholds": sector_averages.get(orig_indicator) is not None}
                    continue
            any_indicator_available = True
            current_thresholds = dynamic_thresholds.get(indicator, thresholds.get(indicator, []))
            if not current_thresholds:
                logging.warning(f"Brak progów dla {indicator} w sektorze {sector}, faza {phase}")
                score_details["indicators"][orig_indicator] = {"points": 0, "value": value, "weight": indicator_weight, "dynamic_thresholds": False}
                continue
            points_assigned = False
            max_threshold = max((t["threshold"] for t in current_thresholds if t["condition"] in [">", ">="]), default=None)
            max_points = max((t["points"] for t in current_thresholds if t["condition"] in [">", ">="]), default=0)
            scaling_factor = 0.1  # Skalowanie proporcjonalnych punktów
            for threshold in sorted(current_thresholds, key=lambda x: x["points"], reverse=True):
                threshold_value = threshold["threshold"]
                points = threshold["points"]
                condition = threshold["condition"]
                weighted_points = points * indicator_weight
                if points < 0:  # Pomijaj ujemne punkty
                    continue
                if condition == ">" and value is not None and value > threshold_value:
                    if value > max_threshold and max_threshold is not None and threshold["threshold"] == max_threshold:
                        excess = value - max_threshold
                        proportional_points = max_points + (excess * scaling_factor)
                        weighted_points = proportional_points * indicator_weight
                        score += weighted_points
                        score_details["indicators"][orig_indicator] = {
                            "points": weighted_points,
                            "value": value,
                            "weight": indicator_weight,
                            "dynamic_thresholds": sector_averages.get(indicator) is not None,
                            "proportional": True
                        }
                    else:
                        score += weighted_points
                        score_details["indicators"][orig_indicator] = {
                            "points": weighted_points,
                            "value": value,
                            "weight": indicator_weight,
                            "dynamic_thresholds": sector_averages.get(indicator) is not None
                        }
                    points_assigned = True
                    break
                elif condition == "<" and value is not None and value < threshold_value:
                    score += weighted_points
                    score_details["indicators"][orig_indicator] = {
                        "points": weighted_points,
                        "value": value,
                        "weight": indicator_weight,
                        "dynamic_thresholds": sector_averages.get(indicator) is not None
                    }
                    points_assigned = True
                    break
                elif condition == ">=" and value is not None and value >= threshold_value:
                    if value > max_threshold and max_threshold is not None and threshold["threshold"] == max_threshold:
                        excess = value - max_threshold
                        proportional_points = max_points + (excess * scaling_factor)
                        weighted_points = proportional_points * indicator_weight
                        score += weighted_points
                        score_details["indicators"][orig_indicator] = {
                            "points": weighted_points,
                            "value": value,
                            "weight": indicator_weight,
                            "dynamic_thresholds": sector_averages.get(indicator) is not None,
                            "proportional": True
                        }
                    else:
                        score += weighted_points
                        score_details["indicators"][orig_indicator] = {
                            "points": weighted_points,
                            "value": value,
                            "weight": indicator_weight,
                            "dynamic_thresholds": sector_averages.get(indicator) is not None
                        }
                    points_assigned = True
                    break
                elif condition == "<=" and value is not None and value <= threshold_value:
                    score += weighted_points
                    score_details["indicators"][orig_indicator] = {
                        "points": weighted_points,
                        "value": value,
                        "weight": indicator_weight,
                        "dynamic_thresholds": sector_averages.get(indicator) is not None
                    }
                    points_assigned = True
                    break
            if not points_assigned:
                score_details["indicators"][orig_indicator] = {
                    "points": 0,
                    "value": value,
                    "weight": indicator_weight,
                    "dynamic_thresholds": sector_averages.get(indicator) is not None
                }

        if not any_indicator_available:
            logging.warning(f"Żadne dane nie dostępne dla sektora {sector}, faza {phase}, zwracam None")
            return None, score_details

        # Obliczanie trendów
        if company_data:
            trend_points, trend_details = calculate_trend(data.get("ticker", ""), company_data, sector, phase)
            if trend_points is not None:
                score += trend_points
                score_details["trend_details"] = trend_details
                if trend_points > 0:
                    score_details["bonuses"]["trend"] = trend_points
                elif trend_points < 0:
                    score_details["bonuses"]["trend_penalty"] = trend_points

        # Obliczanie bonusów sektorowych
        if company_data:
            score_details["sector_phase_avg"] = calculate_sector_phase_average(sector, phase, company_data)
            score_details["sector_avg"] = calculate_sector_average(sector, company_data)
            if score_details["sector_avg"] > 0 and score > score_details["sector_avg"]:
                score += 5
                score_details["bonuses"]["sector"] = 5
                logging.info(f"Dodano +5 punktów za przekroczenie średniej sektora {sector} ({score_details['sector_avg']})")
            overall_avg = calculate_overall_average(company_data)
            if overall_avg > 0 and score > overall_avg:
                score += 2
                score_details["bonuses"]["overall"] = 2
                logging.info(f"Dodano +2 punkty za przekroczenie ogólnej średniej ({overall_avg})")

        # Ograniczenie końcowej punktacji do 100
        score = min(max(score, 0), 100.0)
        logging.debug(f"Punktacja dla {data.get('ticker')}: {score} (bazowa + trendy + bonusy), szczegóły: {score_details}")
        return score, score_details
    except Exception as e:
        logging.error(f"Błąd obliczania punktacji dla sektora {sector}, faza {phase}: {str(e)}")
        return None, {"used_fallbacks": {}, "bonuses": {}, "indicators": {}, "sector_phase_avg": 0.0, "sector_avg": 0.0, "trend_details": {}}