# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\src\core\sentiment_analyzer.py
import logging
from typing import Dict, Optional
from transformers import pipeline
from src.core.logging_config import setup_logging

# Inicjalizacja logowania
setup_logging()

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analizuje sentyment postów z platformy X dla danej spółki."""

    def __init__(self):
        """Inicjalizuje model ML do analizy sentymentu."""
        try:
            self.classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
            logger.info("Model sentymentu zainicjalizowany pomyślnie")
        except Exception as e:
            logger.error(f"Błąd inicjalizacji modelu sentymentu: {e}")
            self.classifier = None

    def analyze_posts(self, posts: list[str]) -> Dict[str, float]:
        """Analizuje sentyment listy postów i zwraca średni wynik."""
        if not self.classifier:
            logger.warning("Model sentymentu nie jest dostępny")
            return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

        results = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        total = len(posts)

        if total == 0:
            logger.warning("Brak postów do analizy")
            return results

        for post in posts:
            try:
                result = self.classifier(post, truncation=True, max_length=512)[0]
                label = result["label"].lower()
                score = result["score"]

                if label == "positive":
                    results["positive"] += score
                elif label == "negative":
                    results["negative"] += score
                else:
                    results["neutral"] += score
            except Exception as e:
                logger.error(f"Błąd analizy posta: {e}")

        # Normalizacja wyników
        results = {k: v / total if total > 0 else 0.0 for k, v in results.items()}
        logger.debug(f"Wyniki analizy sentymentu: {results}")
        return results

    def get_sentiment_score(self, ticker: str, posts: list[str]) -> Optional[float]:
        """Zwraca punktację sentymentu dla tickera (0-10)."""
        results = self.analyze_posts(posts)
        if not results:
            return None

        # Punktacja: +10 za pozytywny, -10 za negatywny, 0 za neutralny
        score = (results["positive"] * 10 - results["negative"] * 10 + results["neutral"] * 0)
        logger.info(f"Punktacja sentymentu dla {ticker}: {score}")
        return round(score, 2)

if __name__ == "__main__":
    # Przykład użycia
    analyzer = SentimentAnalyzer()
    sample_posts = [
        "$AAPL is killing it with the new iPhone launch!",
        "Disappointed with $AAPL earnings, expected more.",
        "Just holding $AAPL for the long term."
    ]
    score = analyzer.get_sentiment_score("AAPL", sample_posts)
    print(f"Sentiment score for AAPL: {score}")