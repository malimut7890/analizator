# ŚCIEŻKA: src/core/sentiment_analyzer.py
"""
Lekka warstwa analizy sentymentu z bezpiecznym fallbackiem, gdy `transformers` nie jest zainstalowane.

Zasady:
- ZERO side-effectów przy imporcie (brak pobierania modeli / logów).
- Import i inicjalizacja `pipeline` tylko wewnątrz __init__, z try/except.
- Jeśli brak modelu / biblioteki, zwracamy neutralny wynik.

API:
    analyzer = SentimentAnalyzer(model_name="cardiffnlp/twitter-roberta-base-sentiment-latest")
    score = analyzer.analyze("Text")  # float w przedziale [-1.0, 1.0], 0.0 = neutralny
"""

from __future__ import annotations
from typing import Optional


class SentimentAnalyzer:
    def __init__(self, model_name: str | None = None) -> None:
        """
        :param model_name: nazwa modelu dla transformers.pipeline('sentiment-analysis')
        """
        self._available = False
        self._pipeline = None
        self._model_name = model_name or "cardiffnlp/twitter-roberta-base-sentiment-latest"

        try:
            # Importowane leniwie – tylko jeśli ktoś faktycznie użyje analizatora
            from transformers import pipeline  # type: ignore

            self._pipeline = pipeline("sentiment-analysis", model=self._model_name)
            self._available = True
        except Exception:
            # Brak transformers / brak modelu – działamy z fallbackiem neutralnym
            self._pipeline = None
            self._available = False

    @property
    def available(self) -> bool:
        """Czy realny model jest dostępny."""
        return self._available

    def analyze(self, text: str) -> float:
        """
        Zwraca sentyment jako liczbę z zakresu [-1.0, 1.0].
        Fallback: 0.0 (neutralny), gdy brak modelu.

        Mapping prosty:
        - label == POSITIVE → ~ +0.8
        - label == NEGATIVE → ~ -0.8
        - label == NEUTRAL  → ~ 0.0
        Skala lekko ważona scorem, jeśli model go zwraca.
        """
        if not text or not isinstance(text, str):
            return 0.0

        if not self._available or self._pipeline is None:
            return 0.0

        try:
            result = self._pipeline(text, truncation=True)
            if not result:
                return 0.0
            first = result[0]
            label = (first.get("label") or "").upper()
            score = float(first.get("score") or 0.0)

            if "POS" in label:
                return min(1.0, 0.6 + 0.4 * score)
            if "NEG" in label:
                return max(-1.0, -0.6 - 0.4 * score)
            return 0.0
        except Exception:
            # W każdej wątpliwej sytuacji wolimy neutralny wynik
            return 0.0
