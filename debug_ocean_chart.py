"""
Debugging-Skript für OCEAN Chart Bug

Simuliert kompletten Workflow:
1. Testbatterie laden
2. Stammdaten erfassen
3. Tests durchführen
4. OCEAN Chart erstellen
"""
import sys
import io
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Fix encoding für Windows Console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_ocean_chart():
    """Testet OCEAN Chart Erstellung"""
    app = QApplication(sys.argv)
    
    from src.main_window import MainWindow
    from src.models import DogData, Gender
    from src.test_battery import TestBattery, Test, OceanDimension
    from src.test_session import TestSession, TestResult
    
    window = MainWindow()
    window.show()
    
    print("=" * 60)
    print("OCEAN Chart Debug Test")
    print("=" * 60)
    
    # 1. Testbatterie erstellen
    print("\n1. Erstelle Testbatterie...")
    tests = [
        Test(1, OceanDimension.OPENNESS, "Test 1", "Indoor", "", "5min", "", "", ""),
        Test(2, OceanDimension.CONSCIENTIOUSNESS, "Test 2", "Outdoor", "", "5min", "", "", ""),
        Test(3, OceanDimension.EXTRAVERSION, "Test 3", "Indoor", "", "5min", "", "", ""),
        Test(4, OceanDimension.AGREEABLENESS, "Test 4", "Outdoor", "", "5min", "", "", ""),
        Test(5, OceanDimension.NEUROTICISM, "Test 5", "Indoor", "", "5min", "", "", ""),
    ]
    battery = TestBattery("Debug Battery", tests)
    window._current_battery = battery
    print(f"   ✓ Battery geladen: {battery.name} mit {len(battery.tests)} Tests")
    
    # 2. Stammdaten erstellen
    print("\n2. Erstelle Stammdaten...")
    dog_data = DogData(
        owner_name="Test Owner",
        dog_name="Test Dog",
        age_years=3,
        age_months=0,
        gender=Gender.MALE,
        neutered=False
    )
    window._master_data_form._dog_data = dog_data
    print(f"   ✓ Hund: {dog_data.dog_name}, Besitzer: {dog_data.owner_name}")
    
    # 3. TestSession mit Ergebnissen erstellen
    print("\n3. Erstelle TestSession mit Ergebnissen...")
    session = TestSession(dog_data=dog_data, battery_name=battery.name)
    session.add_result(TestResult(1, 2, "Notiz 1"))
    session.add_result(TestResult(2, -1, "Notiz 2"))
    session.add_result(TestResult(3, 1, "Notiz 3"))
    session.add_result(TestResult(4, 0, "Notiz 4"))
    session.add_result(TestResult(5, -2, "Notiz 5"))
    window._current_session = session
    print(f"   ✓ Session mit {session.get_completed_count()} Testergebnissen")
    
    # 4. OCEAN Chart erstellen
    def create_chart():
        print("\n4. Erstelle OCEAN Chart...")
        try:
            window._show_ocean_plot()
            print("   ✓ Chart erfolgreich erstellt!")
        except Exception as e:
            print(f"   ✗ FEHLER: {e}")
            import traceback
            traceback.print_exc()
        
        # App nach 2 Sekunden beenden
        QTimer.singleShot(2000, app.quit)
    
    # Chart nach 1 Sekunde erstellen
    QTimer.singleShot(1000, create_chart)
    
    print("\n" + "=" * 60)
    print("Starte Anwendung...")
    print("=" * 60)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_ocean_chart()
