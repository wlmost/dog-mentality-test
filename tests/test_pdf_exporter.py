"""
Tests für PDF-Exporter
"""
import pytest
from pathlib import Path
from PyPDF2 import PdfReader

from src.pdf_exporter import PdfExporter, PdfExportError
from src.test_session import TestSession, TestResult
from src.models import DogData, Gender
from src.test_battery import TestBattery, Test, OceanDimension


@pytest.fixture
def sample_session():
    """Erstellt eine Test-Session mit Daten"""
    dog_data = DogData(
        owner_name="Max Mustermann",
        dog_name="Bello",
        age_years=3,
        age_months=6,
        gender=Gender.MALE,
        neutered=True
    )
    
    session = TestSession(
        dog_data=dog_data,
        battery_name="OCEAN Testbatterie"
    )
    
    # Einige Testergebnisse hinzufügen
    session.add_result(TestResult(test_number=1, score=2, notes="Sehr aufgeschlossen"))
    session.add_result(TestResult(test_number=2, score=-1, notes="Etwas zurückhaltend"))
    session.add_result(TestResult(test_number=5, score=0, notes=""))
    
    session.session_notes = "Hund war heute etwas müde, aber kooperativ."
    
    return session


@pytest.fixture
def sample_battery():
    """Erstellt eine Test-Batterie"""
    tests = [
        Test(
            number=1,
            ocean_dimension=OceanDimension.OPENNESS,
            name="Neugierverhalten",
            setting="Innenraum",
            materials="Spielzeug",
            duration="5 min",
            role_figurant="Beobachter",
            observation_criteria="Interesse",
            rating_scale="-2 bis +2"
        ),
        Test(
            number=2,
            ocean_dimension=OceanDimension.AGREEABLENESS,
            name="Sozialverhalten",
            setting="Außenbereich",
            materials="Keine",
            duration="10 min",
            role_figurant="Aktiv",
            observation_criteria="Freundlichkeit",
            rating_scale="-2 bis +2"
        ),
    ]
    
    return TestBattery(name="OCEAN Testbatterie", tests=tests)


class TestPdfExporter:
    """Tests für PdfExporter"""
    
    def test_exporter_creation(self):
        """Test: Exporter kann erstellt werden"""
        exporter = PdfExporter()
        assert exporter is not None
    
    def test_exporter_with_battery(self, sample_battery):
        """Test: Exporter kann mit Battery erstellt werden"""
        exporter = PdfExporter(battery=sample_battery)
        assert exporter is not None
    
    def test_export_creates_file(self, sample_session, tmp_path):
        """Test: Export erstellt PDF-Datei"""
        exporter = PdfExporter()
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(sample_session, str(filepath))
        
        assert filepath.exists()
    
    def test_pdf_is_valid(self, sample_session, tmp_path):
        """Test: Erstelltes PDF ist gültig und lesbar"""
        exporter = PdfExporter()
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(sample_session, str(filepath))
        
        # Versuche PDF zu lesen
        reader = PdfReader(str(filepath))
        assert len(reader.pages) >= 1
    
    def test_pdf_contains_title(self, sample_session, tmp_path):
        """Test: PDF enthält Titel"""
        exporter = PdfExporter()
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(sample_session, str(filepath))
        
        reader = PdfReader(str(filepath))
        page = reader.pages[0]
        text = page.extract_text()
        
        assert "Tierpsychologischer Test-Report" in text or "Test-Report" in text
    
    def test_pdf_contains_master_data(self, sample_session, tmp_path):
        """Test: PDF enthält Stammdaten"""
        exporter = PdfExporter()
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(sample_session, str(filepath))
        
        reader = PdfReader(str(filepath))
        page = reader.pages[0]
        text = page.extract_text()
        
        assert "Stammdaten" in text
        assert "Max Mustermann" in text
        assert "Bello" in text
    
    def test_pdf_contains_results(self, sample_session, tmp_path):
        """Test: PDF enthält Testergebnisse"""
        exporter = PdfExporter()
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(sample_session, str(filepath))
        
        reader = PdfReader(str(filepath))
        page = reader.pages[0]
        text = page.extract_text()
        
        assert "Testergebnisse" in text
        # Score sollte vorhanden sein
        assert "2" in text  # Score von Test 1
    
    def test_export_with_battery_includes_test_names(self, sample_session, sample_battery, tmp_path):
        """Test: PDF mit Battery enthält Testnamen"""
        exporter = PdfExporter(battery=sample_battery)
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(sample_session, str(filepath))
        
        reader = PdfReader(str(filepath))
        page = reader.pages[0]
        text = page.extract_text()
        
        # Testnamen sollten im PDF sein
        assert "Neugierverhalten" in text or "Neugier" in text
    
    def test_pdf_includes_session_notes(self, sample_session, tmp_path):
        """Test: Session-Notizen werden im PDF angezeigt"""
        exporter = PdfExporter()
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(sample_session, str(filepath))
        
        reader = PdfReader(str(filepath))
        page = reader.pages[0]
        text = page.extract_text()
        
        assert "Session-Notizen" in text or "Notizen" in text
        assert "Hund war heute" in text or "müde" in text
    
    def test_export_handles_permission_error(self, sample_session, tmp_path, monkeypatch):
        """Test: Fehlerbehandlung bei Schreibfehler"""
        exporter = PdfExporter()
        filepath = tmp_path / "test_export.pdf"
        
        # Mock SimpleDocTemplate.build um PermissionError zu simulieren
        def mock_build(*args, **kwargs):
            raise PermissionError("File is locked")
        
        from reportlab.platypus import SimpleDocTemplate
        monkeypatch.setattr(SimpleDocTemplate, "build", mock_build)
        
        with pytest.raises(PdfExportError) as exc_info:
            exporter.export_to_pdf(sample_session, str(filepath))
        
        assert "schreibgeschützt" in str(exc_info.value).lower()
    
    def test_export_without_battery_has_placeholders(self, sample_session, tmp_path):
        """Test: Export ohne Battery hat Platzhalter"""
        exporter = PdfExporter()
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(sample_session, str(filepath))
        
        # PDF sollte trotzdem erstellt werden
        assert filepath.exists()
        
        reader = PdfReader(str(filepath))
        assert len(reader.pages) >= 1
    
    def test_export_multiple_results(self, sample_battery, tmp_path):
        """Test: Export mit vielen Testergebnissen"""
        dog_data = DogData(
            owner_name="Test Owner",
            dog_name="Test Dog",
            age_years=2,
            age_months=0,
            gender=Gender.FEMALE,
            neutered=False
        )
        
        session = TestSession(dog_data=dog_data, battery_name="Test Battery")
        
        # Viele Ergebnisse hinzufügen
        for i in range(1, 11):
            session.add_result(TestResult(test_number=i, score=i % 5 - 2, notes=f"Note {i}"))
        
        exporter = PdfExporter(battery=sample_battery)
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(session, str(filepath))
        
        assert filepath.exists()
        reader = PdfReader(str(filepath))
        assert len(reader.pages) >= 1
    
    def test_export_without_notes(self, sample_battery, tmp_path):
        """Test: Export funktioniert auch ohne Session-Notizen"""
        dog_data = DogData(
            owner_name="Test Owner",
            dog_name="Test Dog",
            age_years=2,
            age_months=0,
            gender=Gender.FEMALE,
            neutered=False
        )
        
        session = TestSession(dog_data=dog_data, battery_name="Test Battery")
        session.add_result(TestResult(test_number=1, score=1, notes="Test"))
        # Keine session_notes gesetzt
        
        exporter = PdfExporter()
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(session, str(filepath))
        
        assert filepath.exists()
    
    def test_export_score_zero(self, tmp_path):
        """Test: Score 0 wird exportiert (neutrales Verhalten ist gültig)"""
        dog_data = DogData(
            owner_name="Test Owner",
            dog_name="Test Dog",
            age_years=2,
            age_months=0,
            gender=Gender.MALE,
            neutered=False
        )
        
        session = TestSession(dog_data=dog_data, battery_name="Test Battery")
        session.add_result(TestResult(test_number=1, score=0, notes="Neutral"))
        session.add_result(TestResult(test_number=2, score=0, notes=""))
        
        exporter = PdfExporter()
        filepath = tmp_path / "test_export.pdf"
        
        exporter.export_to_pdf(session, str(filepath))
        
        assert filepath.exists()
        
        # PDF sollte Score 0 enthalten
        from PyPDF2 import PdfReader
        reader = PdfReader(str(filepath))
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # Beide Tests sollten im PDF vorhanden sein
        assert "1" in text  # Test-Nummer
        assert "2" in text  # Test-Nummer
        assert "0" in text  # Score
