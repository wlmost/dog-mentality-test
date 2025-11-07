"""
Tests für Excel-Importer
"""
import pytest
from pathlib import Path
from src.excel_importer import TestBatteryImporter, ExcelImportError
from src.test_battery import OceanDimension


class TestExcelImporter:
    """Tests für Excel-Import"""
    
    def test_file_not_found(self):
        """Test: Fehler wenn Datei nicht existiert"""
        with pytest.raises(FileNotFoundError):
            TestBatteryImporter("nicht_existent.xlsx")
    
    def test_invalid_file_format(self):
        """Test: Fehler bei ungültigem Dateiformat"""
        with pytest.raises(ValueError, match="Ungültiges Dateiformat"):
            TestBatteryImporter("test.txt")
    
    def test_import_real_battery(self):
        """Test: Reale Testbatterie importieren"""
        # Prüfe ob Datei existiert
        excel_file = Path("Testbatterie_Tiergestuetzte_Arbeit_OCEAN.xlsx")
        if not excel_file.exists():
            pytest.skip("Excel-Datei nicht vorhanden")
        
        importer = TestBatteryImporter(str(excel_file))
        battery = importer.import_battery("Testbatterie (35 Tests)")
        
        # Grundlegende Validierung
        assert battery is not None
        assert battery.name == "Testbatterie (35 Tests)"
        assert len(battery.tests) > 0
        
        # Erster Test sollte "Unbekanntes Objekt" sein
        first_test = battery.tests[0]
        assert first_test.number == 1
        assert first_test.ocean_dimension == OceanDimension.OPENNESS
        assert "Unbekanntes Objekt" in first_test.name
    
    def test_import_default_sheet(self):
        """Test: Import ohne expliziten Sheet-Namen (aktives Sheet)"""
        excel_file = Path("Testbatterie_Tiergestuetzte_Arbeit_OCEAN.xlsx")
        if not excel_file.exists():
            pytest.skip("Excel-Datei nicht vorhanden")
        
        importer = TestBatteryImporter(str(excel_file))
        battery = importer.import_battery()
        
        assert battery is not None
        assert len(battery.tests) > 0
    
    def test_get_sheet_names(self):
        """Test: Sheet-Namen abrufen"""
        excel_file = Path("Testbatterie_Tiergestuetzte_Arbeit_OCEAN.xlsx")
        if not excel_file.exists():
            pytest.skip("Excel-Datei nicht vorhanden")
        
        importer = TestBatteryImporter(str(excel_file))
        sheets = importer.get_sheet_names()
        
        assert "Testbatterie (35 Tests)" in sheets
    
    def test_import_nonexistent_sheet(self):
        """Test: Fehler bei nicht existierendem Sheet"""
        excel_file = Path("Testbatterie_Tiergestuetzte_Arbeit_OCEAN.xlsx")
        if not excel_file.exists():
            pytest.skip("Excel-Datei nicht vorhanden")
        
        importer = TestBatteryImporter(str(excel_file))
        
        with pytest.raises(ExcelImportError, match="Sheet.*nicht gefunden"):
            importer.import_battery("NonExistentSheet")
    
    def test_imported_tests_have_all_fields(self):
        """Test: Importierte Tests haben alle Pflichtfelder"""
        excel_file = Path("Testbatterie_Tiergestuetzte_Arbeit_OCEAN.xlsx")
        if not excel_file.exists():
            pytest.skip("Excel-Datei nicht vorhanden")
        
        importer = TestBatteryImporter(str(excel_file))
        battery = importer.import_battery("Testbatterie (35 Tests)")
        
        # Prüfe ersten Test
        test = battery.tests[0]
        assert test.number > 0
        assert test.ocean_dimension is not None
        assert test.name
        assert test.setting
        assert test.materials
        assert test.duration
    
    def test_ocean_dimensions_mapped_correctly(self):
        """Test: OCEAN-Dimensionen werden korrekt gemappt"""
        excel_file = Path("Testbatterie_Tiergestuetzte_Arbeit_OCEAN.xlsx")
        if not excel_file.exists():
            pytest.skip("Excel-Datei nicht vorhanden")
        
        importer = TestBatteryImporter(str(excel_file))
        battery = importer.import_battery("Testbatterie (35 Tests)")
        
        # Sammle alle verwendeten Dimensionen
        dimensions = set(test.ocean_dimension for test in battery.tests)
        
        # Es sollten mehrere Dimensionen vorkommen
        assert len(dimensions) > 1
        
        # Alle sollten gültige OCEAN-Dimensionen sein
        for dim in dimensions:
            assert dim in OceanDimension
