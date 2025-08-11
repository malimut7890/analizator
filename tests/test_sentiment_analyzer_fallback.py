# ŚCIEŻKA: tests/test_sentiment_analyzer_fallback.py
import sys
import types

from src.core.sentiment_analyzer import SentimentAnalyzer


def test_sentiment_fallback_without_transformers(monkeypatch):
    # Usuń transformers z sys.modules (symulujemy brak pakietu)
    if "transformers" in sys.modules:
        del sys.modules["transformers"]

    sa = SentimentAnalyzer()
    assert sa.available is False
    assert sa.analyze("Cokolwiek") == 0.0
    assert sa.analyze("") == 0.0
    assert sa.analyze(None) == 0.0  # type: ignore


def test_sentiment_with_mocked_transformers(monkeypatch):
    # Wstrzykujemy atrapę transformers.pipeline
    fake_mod = types.ModuleType("transformers")

    def fake_pipeline(kind, model=None):
        def _runner(text, truncation=True):
            return [{"label": "POSITIVE", "score": 0.9}]
        return _runner

    fake_mod.pipeline = fake_pipeline  # type: ignore
    monkeypatch.setitem(sys.modules, "transformers", fake_mod)

    sa = SentimentAnalyzer()
    assert sa.available is True
    score = sa.analyze("Great job!")
    assert score > 0.0
