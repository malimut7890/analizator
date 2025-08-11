# ŚCIEŻKA: C:\Users\Msi\Desktop\analizator\run.py
import os
import sys
import subprocess

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(root, "main.py")
    if not os.path.exists(script):
        print(f"Nie znaleziono pliku: {script}")
        sys.exit(1)
    # Uruchom main.py tym samym interpreterem
    subprocess.run([sys.executable, script], check=False)

if __name__ == "__main__":
    main()
