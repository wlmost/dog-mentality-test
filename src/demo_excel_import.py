"""
Demo: Excel-Import der Testbatterie
"""
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.excel_importer import TestBatteryImporter


def main():
    """Demonstriert den Excel-Import"""
    excel_file = "Testbatterie_Tiergestuetzte_Arbeit_OCEAN.xlsx"
    
    if not Path(excel_file).exists():
        print(f"❌ Datei '{excel_file}' nicht gefunden!")
        return
    
    print("=" * 70)
    print("TESTBATTERIE-IMPORT DEMO")
    print("=" * 70)
    
    # Importer erstellen
    importer = TestBatteryImporter(excel_file)
    
    # Verfügbare Sheets anzeigen
    print("\n📋 Verfügbare Sheets:")
    for sheet in importer.get_sheet_names():
        print(f"   - {sheet}")
    
    # Testbatterie importieren
    print("\n⏳ Importiere Testbatterie...")
    battery = importer.import_battery("Testbatterie (35 Tests)")
    
    print(f"✅ Import erfolgreich!")
    print(f"\n📦 Testbatterie: {battery.name}")
    print(f"📊 Anzahl Tests: {len(battery.tests)}")
    
    # Statistik nach OCEAN-Dimensionen
    print("\n📈 Verteilung nach OCEAN-Dimensionen:")
    from src.test_battery import OceanDimension
    
    for dimension in OceanDimension:
        tests = battery.get_tests_by_dimension(dimension)
        print(f"   {dimension.value}: {len(tests)} Tests")
    
    # Erste 3 Tests anzeigen
    print("\n🔍 Beispiel: Erste 3 Tests")
    print("-" * 70)
    
    for test in battery.tests[:3]:
        print(f"\n#{test.number}: {test.name}")
        print(f"   OCEAN: {test.ocean_dimension.value}")
        print(f"   Dauer: {test.duration}")
        print(f"   Material: {test.materials[:50]}..." if len(test.materials) > 50 else f"   Material: {test.materials}")
        print(f"   Setting: {test.setting[:60]}..." if len(test.setting) > 60 else f"   Setting: {test.setting}")
    
    # Test nach Nummer suchen
    print("\n" + "=" * 70)
    print("🔎 Test #10 suchen...")
    test_10 = battery.get_test_by_number(10)
    if test_10:
        print(f"\n✅ Gefunden: #{test_10.number} - {test_10.name}")
        print(f"   OCEAN-Dimension: {test_10.ocean_dimension.value}")
        print(f"   Dauer: {test_10.duration}")
        print(f"\n   Beobachtungskriterien:")
        print(f"   {test_10.observation_criteria}")
    
    print("\n" + "=" * 70)
    print("✨ Demo abgeschlossen!")
    print("=" * 70)


if __name__ == "__main__":
    main()
