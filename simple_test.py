"""
Einfacher Test für OCEAN Chart
"""
import sys
from pathlib import Path

# Füge src zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from main_window import MainWindow

def main():
    print("Starte Anwendung...")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    print("Anwendung gestartet. Bitte:")
    print("1. Lade eine Testbatterie (Menu: Datei > Testbatterie laden)")
    print("2. Gib Stammdaten ein")
    print("3. Fuehre Tests durch")
    print("4. Druecke STRG+R oder waehle 'Analyse > OCEAN Diagramm'")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
