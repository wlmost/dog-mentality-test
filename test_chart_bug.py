"""
Testprogramm um OCEAN Chart-Bug zu reproduzieren
"""
import sys
from PySide6.QtWidgets import QApplication
from src.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    print("Anwendung gestartet. Teste mit Testbatterie und Testdaten.")
    print("Drücke Ctrl+R um OCEAN-Chart zu erstellen.")
    
    sys.exit(app.exec())
