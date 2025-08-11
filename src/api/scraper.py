# Lokalizacja: C:\Users\Msi\Desktop\Analizator\src\api\scraper.py
import requests
from bs4 import BeautifulSoup
import logging
from src.core.logging_config import setup_logging

# Inicjalizacja logowania
setup_logging()

def scrape_marketwatch(ticker: str) -> dict:
    """
    Scrapuje dane z MarketWatch dla podanego tickera.
    Args:
        ticker: Symbol tickera (np. 'AAPL').
    Returns:
        Słownik z danymi lub pusty słownik w przypadku błędu.
    """
    try:
        url = f"https://www.marketwatch.com/investing/stock/{ticker}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        data = {}
        # Nazwa spółki
        name_elem = soup.find("h1", class_="company__name")
        data["company_name"] = name_elem.text.strip() if name_elem else ""
        
        # Sektor
        sector_elem = soup.find("small", string="Sector")
        if sector_elem:
            sector = sector_elem.find_next("span", class_="primary")
            data["sector"] = sector.text.strip() if sector else ""
        
        # Cena
        price_elem = soup.find("bg-quote", class_="value")
        data["current_price"] = price_elem.text.strip() if price_elem else ""
        
        # PE Ratio
        pe_elem = soup.find("small", string="P/E Ratio")
        if pe_elem:
            pe = pe_elem.find_next("span", class_="primary")
            data["pe_ratio"] = pe.text.strip() if pe else ""
        
        # EPS
        eps_elem = soup.find("small", string="EPS")
        if eps_elem:
            eps = eps_elem.find_next("span", class_="primary")
            data["eps"] = eps.text.strip() if eps else ""
        
        logging.debug(f"Zescrapowano dane z MarketWatch dla {ticker}: {data}")
        return data
    except Exception as e:
        logging.error(f"Błąd scrapowania danych z MarketWatch dla {ticker}: {str(e)}")
        return {}

def scrape_investing(ticker: str) -> dict:
    """
    Scrapuje dane z Investing.com dla podanego tickera.
    Args:
        ticker: Symbol tickera (np. 'AAPL').
    Returns:
        Słownik z danymi lub pusty słownik w przypadku błędu.
    """
    try:
        url = f"https://www.investing.com/equities/{ticker.lower()}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        data = {}
        # Nazwa spółki
        name_elem = soup.find("h1", class_="instrument-header_title__GTWDv")
        data["company_name"] = name_elem.text.strip() if name_elem else ""
        
        # Sektor
        sector_elem = soup.find("span", string="Sector")
        if sector_elem:
            sector = sector_elem.find_next("span")
            data["sector"] = sector.text.strip() if sector else ""
        
        # Cena
        price_elem = soup.find("div", class_="instrument-price_instrument-price__3uw25")
        data["current_price"] = price_elem.text.strip() if price_elem else ""
        
        # PE Ratio
        pe_elem = soup.find("span", string="P/E Ratio")
        if pe_elem:
            pe = pe_elem.find_next("span")
            data["pe_ratio"] = pe.text.strip() if pe else ""
        
        # EPS
        eps_elem = soup.find("span", string="EPS")
        if eps_elem:
            eps = eps_elem.find_next("span")
            data["eps"] = eps.text.strip() if eps else ""
        
        logging.debug(f"Zescrapowano dane z Investing.com dla {ticker}: {data}")
        return data
    except Exception as e:
        logging.error(f"Błąd scrapowania danych z Investing.com dla {ticker}: {str(e)}")
        return {}