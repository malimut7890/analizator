# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\dotenv\__init__.py
"""
Lekka atrapa dla 'python-dotenv' aby projekt działał bez zależności.
Jeżeli właściwy pakiet jest zainstalowany – ten moduł nie będzie użyty.
"""

def load_dotenv(*args, **kwargs):
    """No-op: zwraca False, nic nie ładuje."""
    return False

def find_dotenv(*args, **kwargs):
    """No-op: zwraca pustą ścieżkę."""
    return ""
