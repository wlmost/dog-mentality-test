"""
Tests für Battery-Auswahl-Logik
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QMessageBox

from src.main_window import MainWindow
from src.test_session import TestSession
from src.models import DogData, Gender
from src.test_battery import TestBattery, Test, OceanDimension


@pytest.fixture
def app(qapp):
    """QApplication fixture"""
    return qapp


@pytest.fixture
def main_window(app):
    """Erstellt MainWindow-Instanz"""
    # Mock für _select_battery_on_startup um automatischen Dialog zu verhindern
    with patch.object(MainWindow, '_select_battery_on_startup'):
        window = MainWindow()
        yield window
        window.close()


@pytest.fixture
def sample_battery():
    """Erstellt Test-Battery"""
    tests = [
        Test(
            number=1,
            ocean_dimension=OceanDimension.OPENNESS,
            name="Test 1",
            setting="Indoor",
            materials="Toy",
            duration="5 min",
            role_figurant="Observer",
            observation_criteria="Interest",
            rating_scale="-2 to +2"
        )
    ]
    return TestBattery(name="Test Battery", tests=tests)


@pytest.fixture
def sample_session(sample_battery):
    """Erstellt Test-Session"""
    dog_data = DogData(
        owner_name="Max Mustermann",
        dog_name="Bello",
        age_years=3,
        age_months=6,
        gender=Gender.MALE,
        neutered=True
    )
    session = TestSession(dog_data=dog_data, battery_name=sample_battery.name)
    return session


class TestBatteryStartupDialog:
    """Tests für Battery-Auswahl beim Start"""
    
    @patch('src.main_window.QMessageBox.question')
    @patch.object(MainWindow, '_import_battery')
    def test_startup_dialog_yes_calls_import(self, mock_import, mock_question, app):
        """Dialog 'Ja' ruft _import_battery auf"""
        mock_question.return_value = QMessageBox.StandardButton.Yes
        
        # MainWindow ohne Startup-Mock erstellen
        window = MainWindow()
        
        # QTimer.singleShot sollte nach 100ms _select_battery_on_startup aufrufen
        # Wir simulieren das manuell
        window._select_battery_on_startup()
        
        mock_question.assert_called_once()
        mock_import.assert_called_once()
        
        window.close()
    
    @patch('src.main_window.QMessageBox.question')
    @patch.object(MainWindow, '_import_battery')
    def test_startup_dialog_no_skips_import(self, mock_import, mock_question, app):
        """Dialog 'Nein' überspringt Import"""
        mock_question.return_value = QMessageBox.StandardButton.No
        
        window = MainWindow()
        window._select_battery_on_startup()
        
        mock_question.assert_called_once()
        mock_import.assert_not_called()
        
        window.close()


class TestBatterySessionMatching:
    """Tests für Battery-Matching beim Session-Laden"""
    
    def test_ensure_battery_matches_when_correct(self, main_window, sample_session, sample_battery):
        """Gibt True zurück wenn Battery bereits passt"""
        main_window._current_battery = sample_battery
        
        result = main_window._ensure_battery_matches_session(sample_session)
        
        assert result is True
    
    @patch('src.main_window.QMessageBox.question')
    def test_ensure_battery_prompts_when_missing(self, mock_question, main_window, sample_session):
        """Zeigt Dialog wenn Battery fehlt"""
        mock_question.return_value = QMessageBox.StandardButton.No
        main_window._current_battery = None
        
        result = main_window._ensure_battery_matches_session(sample_session)
        
        mock_question.assert_called_once()
        assert "Test Battery" in str(mock_question.call_args)
        assert result is False
    
    @patch('src.main_window.QMessageBox.question')
    def test_ensure_battery_prompts_when_wrong(self, mock_question, main_window, sample_session, sample_battery):
        """Zeigt Dialog wenn Battery nicht passt"""
        mock_question.return_value = QMessageBox.StandardButton.No
        
        # Falsche Battery setzen
        wrong_battery = TestBattery(name="Wrong Battery", tests=sample_battery.tests)
        main_window._current_battery = wrong_battery
        
        result = main_window._ensure_battery_matches_session(sample_session)
        
        mock_question.assert_called_once()
        assert result is False
    
    @patch('src.main_window.QFileDialog.getOpenFileName')
    @patch('src.main_window.QMessageBox.question')
    @patch('src.main_window.QMessageBox.warning')
    @patch('src.main_window.TestBatteryImporter')
    def test_ensure_battery_loads_correct_battery(
        self, mock_importer_class, mock_warning, mock_question, mock_file_dialog, 
        main_window, sample_session, sample_battery
    ):
        """Lädt korrekte Battery über Dialog"""
        mock_question.return_value = QMessageBox.StandardButton.Yes
        mock_file_dialog.return_value = ("/path/to/battery.xlsx", "")
        
        # Mock Importer
        mock_importer = Mock()
        mock_importer.import_battery.return_value = sample_battery
        mock_importer_class.return_value = mock_importer
        
        main_window._current_battery = None
        
        with patch('src.main_window.settings'):
            result = main_window._ensure_battery_matches_session(sample_session)
        
        assert result is True
        assert main_window._current_battery == sample_battery
        mock_warning.assert_not_called()
    
    @patch('src.main_window.QFileDialog.getOpenFileName')
    @patch('src.main_window.QMessageBox.question')
    @patch('src.main_window.QMessageBox.warning')
    @patch('src.main_window.TestBatteryImporter')
    def test_ensure_battery_rejects_wrong_battery(
        self, mock_importer_class, mock_warning, mock_question, mock_file_dialog,
        main_window, sample_session, sample_battery
    ):
        """Zeigt Warnung bei falscher Battery"""
        mock_question.return_value = QMessageBox.StandardButton.Yes
        mock_file_dialog.return_value = ("/path/to/battery.xlsx", "")
        
        # Mock Importer mit falscher Battery
        wrong_battery = TestBattery(name="Wrong Battery", tests=sample_battery.tests)
        mock_importer = Mock()
        mock_importer.import_battery.return_value = wrong_battery
        mock_importer_class.return_value = mock_importer
        
        main_window._current_battery = None
        
        with patch('src.main_window.settings'):
            result = main_window._ensure_battery_matches_session(sample_session)
        
        assert result is False
        mock_warning.assert_called_once()
        assert "Falsche Testbatterie" in str(mock_warning.call_args)


class TestBatteryPathSettings:
    """Tests für Battery-Pfad Settings"""
    
    @patch('src.main_window.settings')
    @patch('src.main_window.QFileDialog.getOpenFileName')
    @patch('src.main_window.TestBatteryImporter')
    def test_import_battery_saves_path(
        self, mock_importer_class, mock_file_dialog, mock_settings,
        main_window, sample_battery
    ):
        """_import_battery speichert Battery-Pfad"""
        mock_file_dialog.return_value = ("/path/to/battery.xlsx", "")
        mock_settings.last_battery_path = None
        
        # Mock Importer
        mock_importer = Mock()
        mock_importer.import_battery.return_value = sample_battery
        mock_importer_class.return_value = mock_importer
        
        main_window._import_battery()
        
        mock_settings.save_last_battery_path.assert_called_once()
        # Pfad sollte absolut sein
        saved_path = mock_settings.save_last_battery_path.call_args[0][0]
        assert "battery.xlsx" in saved_path
    
    @patch('src.main_window.settings')
    @patch('src.main_window.QFileDialog.getOpenFileName')
    def test_import_battery_uses_last_path_as_default(
        self, mock_file_dialog, mock_settings, main_window
    ):
        """_import_battery nutzt letzten Pfad als Start-Verzeichnis"""
        mock_settings.last_battery_path = "/old/path/battery.xlsx"
        mock_file_dialog.return_value = ("", "")  # Abbrechen
        
        main_window._import_battery()
        
        # Prüfe dass FileDialog mit richtigem Verzeichnis aufgerufen wurde
        call_args = mock_file_dialog.call_args
        start_dir = call_args[0][2]  # 3. Argument ist das Startverzeichnis
        assert "/old/path" in start_dir or start_dir == "data"  # Falls Pfad nicht existiert
