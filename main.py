"""
Dog Mentality Test - Hauptanwendung

OCEAN Persönlichkeitsanalyse für Hunde
"""
import sys
from pathlib import Path

# Stelle sicher, dass src im Pfad ist
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from src.main_window import MainWindow


def main():
    """Startet die Hauptanwendung"""
    app = QApplication(sys.argv)
    
    # App-Informationen
    app.setApplicationName("Dog Mentality Test")
    app.setOrganizationName("Dog Psychology Lab")
    app.setApplicationVersion("1.0.0")
    
    # Hauptfenster erstellen und anzeigen
    window = MainWindow()
    window.show()
    
    # Event-Loop starten
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
