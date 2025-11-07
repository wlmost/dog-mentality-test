"""
Tests für TestDataForm GUI
"""
import pytest
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpinBox

from src.test_data_form import TestDataForm
from src.models import DogData, Gender
from src.test_battery import TestBattery, Test, OceanDimension


@pytest.fixture
def sample_dog():
    """Beispiel-Hunddaten"""
    return DogData(
        owner_name="Max Mustermann",
        dog_name="Bello",
        age_years=5,
        age_months=6,
        gender=Gender.MALE,
        neutered=True
    )


@pytest.fixture
def sample_battery():
    """Beispiel-Testbatterie"""
    tests = [
        Test(
            number=1,
            ocean_dimension=OceanDimension.OPENNESS,
            name="Test Neugier",
            setting="Innenraum",
            materials="Spielzeug",
            duration="5 min",
            role_figurant="Beobachter",
            observation_criteria="Interesse",
            rating_scale="-2 bis +2"
        ),
        Test(
            number=2,
            ocean_dimension=OceanDimension.CONSCIENTIOUSNESS,
            name="Test Gehorsam",
            setting="Außenbereich",
            materials="Leine",
            duration="3 min",
            role_figurant="Beobachter",
            observation_criteria="Folgsamkeit",
            rating_scale="-2 bis +2"
        ),
        Test(
            number=3,
            ocean_dimension=OceanDimension.EXTRAVERSION,
            name="Test Sozialverhalten",
            setting="Hundewiese",
            materials="Keine",
            duration="10 min",
            role_figurant="Andere Hunde",
            observation_criteria="Kontaktfreudigkeit",
            rating_scale="-2 bis +2"
        ),
        Test(
            number=4,
            ocean_dimension=OceanDimension.AGREEABLENESS,
            name="Test Freundlichkeit",
            setting="Park",
            materials="Leckerlis",
            duration="5 min",
            role_figurant="Fremde Person",
            observation_criteria="Freundlichkeit",
            rating_scale="-2 bis +2"
        ),
        Test(
            number=5,
            ocean_dimension=OceanDimension.NEUROTICISM,
            name="Test Angst",
            setting="Innenraum",
            materials="Laute Geräusche",
            duration="2 min",
            role_figurant="Beobachter",
            observation_criteria="Stressreaktionen",
            rating_scale="-2 bis +2"
        ),
    ]
    return TestBattery("Test-Batterie", tests)


class TestTestDataFormCreation:
    """Tests für die Erstellung des Formulars"""
    
    def test_form_creation(self, qtbot):
        """Test: Formular kann erstellt werden"""
        form = TestDataForm()
        qtbot.addWidget(form)
        
        assert form is not None
        assert form._table is not None
        assert form._save_btn is not None
    
    def test_initial_state(self, qtbot):
        """Test: Initiale Werte sind korrekt"""
        form = TestDataForm()
        qtbot.addWidget(form)
        
        assert form._dog_data is None
        assert form._battery is None
        assert form._session is None
        assert not form._save_btn.isEnabled()


class TestTestDataFormDataLoading:
    """Tests für das Laden von Daten"""
    
    def test_load_data(self, qtbot, sample_dog, sample_battery):
        """Test: Daten können geladen werden"""
        form = TestDataForm()
        qtbot.addWidget(form)
        
        form.load_data(sample_dog, sample_battery)
        
        assert form._dog_data == sample_dog
        assert form._battery == sample_battery
        assert form._session is not None
        assert form._save_btn.isEnabled()
    
    def test_table_population(self, qtbot, sample_dog, sample_battery):
        """Test: Tabelle wird mit Tests gefüllt"""
        form = TestDataForm()
        qtbot.addWidget(form)
        
        form.load_data(sample_dog, sample_battery)
        
        assert form._table.rowCount() == 5
        
        # Erste Zeile prüfen
        assert form._table.item(0, 0).text() == "1"
        assert form._table.item(0, 1).text() == "Test Neugier"
        assert form._table.item(0, 2).text() == "Offenheit"  # Deutsche Übersetzung
    
    def test_score_widgets(self, qtbot, sample_dog, sample_battery):
        """Test: Score-SpinBoxes sind korrekt"""
        form = TestDataForm()
        qtbot.addWidget(form)
        
        form.load_data(sample_dog, sample_battery)
        
        for row in range(form._table.rowCount()):
            widget = form._table.cellWidget(row, 3)
            assert isinstance(widget, QSpinBox)
            assert widget.minimum() == -2
            assert widget.maximum() == 2
            assert widget.value() == 0
    
    def test_info_labels(self, qtbot, sample_dog, sample_battery):
        """Test: Info-Labels werden aktualisiert"""
        form = TestDataForm()
        qtbot.addWidget(form)
        
        form.load_data(sample_dog, sample_battery)
        
        dog_info = form._dog_info_label.text()
        assert "Bello" in dog_info
        assert "5 Jahre, 6 Monate" in dog_info
        
        battery_info = form._battery_info_label.text()
        assert "Test-Batterie" in battery_info


class TestTestDataFormScoreEntry:
    """Tests für die Score-Eingabe"""
    
    def test_enter_score(self, qtbot, sample_dog, sample_battery):
        """Test: Score kann eingegeben werden"""
        form = TestDataForm()
        qtbot.addWidget(form)
        form.load_data(sample_dog, sample_battery)
        
        # Score für Test 1 setzen
        score_widget = form._table.cellWidget(0, 3)
        score_widget.setValue(2)
        
        # Prüfen ob in Session gespeichert
        form._update_session_data()
        session = form.get_session()
        result = session.get_result(1)
        
        assert result is not None
        assert result.score == 2
    
    def test_enter_notes(self, qtbot, sample_dog, sample_battery):
        """Test: Notizen können eingegeben werden"""
        form = TestDataForm()
        qtbot.addWidget(form)
        form.load_data(sample_dog, sample_battery)
        
        # Notiz für Test 1 setzen
        form._table.item(0, 4).setText("Sehr aufgeschlossen")
        
        # Manuell Update triggern
        form._update_session_data()
        session = form.get_session()
        result = session.get_result(1)
        
        assert result is not None
        assert result.notes == "Sehr aufgeschlossen"
    
    def test_progress_update(self, qtbot, sample_dog, sample_battery):
        """Test: Fortschritt wird aktualisiert"""
        form = TestDataForm()
        qtbot.addWidget(form)
        form.load_data(sample_dog, sample_battery)
        
        # Initial 0 Tests
        assert "0 / 5" in form._progress_label.text()
        
        # Score für Test 1 setzen
        score_widget = form._table.cellWidget(0, 3)
        score_widget.setValue(2)
        
        # Fortschritt sollte aktualisiert sein
        assert "1 / 5" in form._progress_label.text()


class TestTestDataFormSaving:
    """Tests für das Speichern"""
    
    def test_save_session(self, qtbot, sample_dog, sample_battery, tmp_path, monkeypatch):
        """Test: Session kann gespeichert werden"""
        form = TestDataForm()
        qtbot.addWidget(form)
        form.load_data(sample_dog, sample_battery)
        
        # Scores eingeben
        form._table.cellWidget(0, 3).setValue(2)
        form._table.cellWidget(1, 3).setValue(-1)
        
        # Session-Notizen
        form._session_notes.setPlainText("Test-Session erfolgreich")
        
        # Speichern in tmp_path
        test_file = tmp_path / "test_session.json"
        monkeypatch.setattr(
            'src.test_data_form.datetime',
            type('MockDatetime', (), {'now': lambda: type('dt', (), {'strftime': lambda self, fmt: '20250101_120000'})()})
        )
        
        # Speichern triggern
        session = form.get_session()
        session.session_notes = form._session_notes.toPlainText()
        session.save_to_file(str(test_file))
        
        # Prüfen
        assert test_file.exists()
        
        # Laden und prüfen
        from src.test_session import TestSession
        loaded = TestSession.load_from_file(str(test_file))
        
        assert loaded.dog_data.dog_name == "Bello"
        assert loaded.get_result(1).score == 2
        assert loaded.get_result(2).score == -1
        assert loaded.session_notes == "Test-Session erfolgreich"
    
    def test_session_signal(self, qtbot, sample_dog, sample_battery):
        """Test: Signal wird beim Speichern emittiert"""
        form = TestDataForm()
        qtbot.addWidget(form)
        form.load_data(sample_dog, sample_battery)
        
        # Signal-Spy
        with qtbot.waitSignal(form.session_saved, timeout=1000):
            # Speichern triggern (wird durch qtbot abgefangen)
            form._save_btn.click()
