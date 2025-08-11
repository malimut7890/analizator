# Analizator Spółek Giełdowych

## Opis projektu
Analizator to aplikacja Pythonowa do analizy danych finansowych spółek giełdowych. Pobiera dane z różnych API (yfinance, FMP, Alpha Vantage, Finnhub, yahooquery, MarketWatch, Investing.com), przetwarza je i wyświetla w interfejsie graficznym (Tkinter). Obsługuje klasyfikację faz rozwoju, punktację spółek oraz analizę sentymentu postów z platformy X.

## Struktura katalogów
- **src/api/**: Moduły do pobierania danych z API i scrapingu.
  - `api_fetcher.py`: Pobiera dane z yfinance, FMP, Alpha Vantage, Finnhub, yahooquery, MarketWatch i Investing.com.
  - `api_field_mapping.py`: Mapuje pola z API na standardowy format.
  - `api_keys.py`: Zarządza kluczami API z pliku `.env`.
  - `scraper.py`: Scrapuje dane z MarketWatch i Investing.com.
- **src/core/**: Logika biznesowa aplikacji.
  - `company_data.py`: Zarządza danymi spółek (dodawanie, usuwanie, zapisywanie).
  - `logging_config.py`: Konfiguruje logowanie.
  - `phase_classifier.py`: Klasyfikuje fazy rozwoju spółek.
  - `scoring_calculator.py`: Oblicza punktację spółek.
  - `sentiment_analyzer.py`: Analizuje sentyment postów z platformy X.
  - `utils.py`: Funkcje pomocnicze, np. wczytywanie konfiguracji sektorowej.
  - `sectors/technology.json`: Plik konfiguracyjny dla sektora Technology.
- **src/gui/**: Interfejs graficzny aplikacji.
  - `main_window.py`: Główna klasa GUI z tabelą spółek i wykresami.
  - `edit_window.py`: Okno edycji danych spółek.
  - `indicator_calculator.py`: Okno do obliczania wskaźników finansowych.
  - `macro_tab.py`: Zakładka do wyświetlania danych makroekonomicznych.
  - `momentum_tab.py`: Zakładka do obliczania momentum sektorowego.
  - `settings_tab.py`: Zakładka do zarządzania ustawieniami (klucze API, logowanie).
- **tests/**: Testy jednostkowe.
  - `test_api_field_mapping.py`: Testy dla mapowania pól API.
  - `test_company_data.py`: Testy dla klasy `CompanyData`.
  - `test_edit_window.py`: Testy dla okna edycji.
  - `test_scoring_calculator.py`: Testy dla punktacji i trendów.
  - `test_api_fetcher.py`: Testy dla pobierania danych z API i scrapingu.
- **data/**: Pliki danych, np. `AMD.json` z danymi historycznymi.

## Instalacja
1. Sklonuj repozytorium:
   ```bash
   git clone <adres_repozytorium>
   cd Analizator
   # ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\README.md
# Analizator – instrukcja uruchomienia i konfiguracji

## Wymagania
- Python 3.10+ (Windows 10/11)
- (Opcjonalnie) `python-dotenv` do lokalnego wczytywania pliku `.env`

## Instalacja (Windows CMD)
```bat
cd /d C:\Users\Msi\Desktop\analizator
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
