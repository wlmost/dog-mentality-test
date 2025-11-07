"""
Demo-Anwendung für Testdaten-Eingabe

Demonstriert die Funktionalität des Test Data Form Widgets.
Lädt Stammdaten und eine Testbatterie und ermöglicht die Eingabe von Test-Scores.
"""
import sys
from pathlib import Path

# Stelle sicher, dass src im Pfad ist
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from src.test_data_form import TestDataForm
from src.models import DogData, Gender
from src.excel_importer import TestBatteryImporter


class DemoWindow(QMainWindow):
    """Demo-Fenster für TestDataForm"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test-Data-Eingabe Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # TestDataForm
        self.form = TestDataForm()
        self.form.session_saved.connect(self._on_session_saved)
        layout.addWidget(self.form)
        
        # Lade Beispieldaten
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Lädt Beispiel-Hunddaten und Testbatterie"""
        # Beispiel-Hund
        dog = DogData(
            owner_name="Maria Schmidt",
            dog_name="Luna",
            age_years=3,
            age_months=6,
            gender=Gender.FEMALE,
            neutered=True
        )
        
        # Testbatterie aus Excel laden
        try:
            importer = TestBatteryImporter("data/Testbatterie_OCEAN.xlsx")
            battery = importer.import_battery()
            
            # Form mit Daten befüllen
            self.form.load_data(dog, battery)
            
            print(f"✅ Testbatterie geladen: {battery.name}")
            print(f"   Anzahl Tests: {len(battery.tests)}")
            print(f"✅ Hund: {dog.dog_name} ({dog.age_display()})")
        
        except FileNotFoundError:
            print("⚠️ Excel-Datei nicht gefunden. Bitte zuerst Excel-Import ausführen.")
            print("   Datei: data/Testbatterie_OCEAN.xlsx")
        except Exception as e:
            print(f"❌ Fehler beim Laden: {e}")
    
    def _on_session_saved(self, session):
        """Callback wenn Session gespeichert wurde"""
        print(f"\n✅ Session gespeichert!")
        print(f"   Hund: {session.dog_data.dog_name}")
        print(f"   Testbatterie: {session.battery_name}")
        print(f"   Abgeschlossene Tests: {session.get_completed_count()}")


def main():
    """Startet die Demo-Anwendung"""
    app = QApplication(sys.argv)
    
    print("=== Test-Data-Eingabe Demo ===\n")
    
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
