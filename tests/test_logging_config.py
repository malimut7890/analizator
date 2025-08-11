# ŚCIEŻKA: C:\Users\Msi\Desktop\Analizator\tests\test_logging_config.py
import pytest
import os
import logging
from src.core.logging_config import setup_logging

@pytest.fixture
def setup_logging_fixture(tmp_path):
    error_log = tmp_path / "error.log"
    errors_only_log = tmp_path / "errors_only.log"
    logging.basicConfig(level=logging.DEBUG)
    setup_logging(log_level="DEBUG")
    yield error_log, errors_only_log
    logging.getLogger().handlers = []

def test_logging_config_errors_only(setup_logging_fixture):
    """Testuje zapis błędów do errors_only.log."""
    error_log, errors_only_log = setup_logging_fixture
    logging.error("Testowy błąd do errors_only.log")
    with open(errors_only_log, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Testowy błąd do errors_only.log" in content
    with open(error_log, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Testowy błąd do errors_only.log" in content

def test_logging_config_debug(setup_logging_fixture):
    """Testuje zapis debugowania do error.log."""
    error_log, errors_only_log = setup_logging_fixture
    logging.debug("Testowy debug")
    with open(error_log, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Testowy debug" in content
    with open(errors_only_log, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Testowy debug" not in content