# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\tests\test_api_keys.py
import os
import importlib
import logging


def test_get_api_key_env_monkeypatch(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "aaa")
    monkeypatch.setenv("FMP_API_KEY", "bbb")
    monkeypatch.delenv("FINNHUB_API_KEY_1", raising=False)
    monkeypatch.delenv("FINNHUB_API_KEY_2", raising=False)

    # Wymuś ponowne załadowanie modułu
    if "src.api.api_keys" in list(importlib.sys.modules):
        del importlib.sys.modules["src.api.api_keys"]
    from src.api import api_keys  # noqa: E402

    assert api_keys.get_api_key("ALPHA_VANTAGE_API_KEY") == "aaa"
    assert api_keys.get_api_key("FMP_API_KEY") == "bbb"
    assert api_keys.get_api_key("FINNHUB_API_KEY") is None  # brak skonfigurowanych


def test_finnhub_rotation(monkeypatch):
    monkeypatch.setenv("FINNHUB_API_KEY_1", "k1")
    monkeypatch.setenv("FINNHUB_API_KEY_2", "k2")

    if "src.api.api_keys" in list(importlib.sys.modules):
        del importlib.sys.modules["src.api.api_keys"]
    from src.api import api_keys  # noqa: E402

    assert api_keys.get_api_key("FINNHUB_API_KEY", finnhub_index=0) == "k1"
    assert api_keys.get_api_key("FINNHUB_API_KEY", finnhub_index=1) == "k2"
    assert api_keys.get_api_key("FINNHUB_API_KEY", finnhub_index=2) == "k1"  # modulo


def test_placeholder_is_treated_as_missing(monkeypatch):
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "your_placeholder")

    if "src.api.api_keys" in list(importlib.sys.modules):
        del importlib.sys.modules["src.api.api_keys"]
    from src.api import api_keys  # noqa: E402

    assert api_keys.get_api_key("ALPHA_VANTAGE_API_KEY") is None
