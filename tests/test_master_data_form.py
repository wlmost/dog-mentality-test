"""
Automatisierte GUI-Tests für das Stammdaten-Formular
"""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot
from src.master_data_form import MasterDataForm
from src.models import DogData, Gender


@pytest.fixture
def app(qapp):
    """Fixture für QApplication"""
    return qapp


@pytest.fixture
def form(qtbot: QtBot):
    """Fixture für MasterDataForm"""
    form = MasterDataForm()
    qtbot.addWidget(form)
    return form


class TestMasterDataForm:
    """Test-Suite für GUI-Formular"""

    def test_form_creation(self, form):
        """Test: Formular wird korrekt erstellt"""
        assert form is not None
        assert form.windowTitle() == "Stammdaten-Erfassung"

    def test_initial_state(self, form):
        """Test: Initiale Werte der Formularfelder"""
        assert form.owner_name_input.text() == ""
        assert form.dog_name_input.text() == ""
        assert form.age_input.value() == 0
        assert form.gender_input.currentText() == "Rüde"
        assert form.neutered_input.isChecked() is False

    def test_fill_form_programmatically(self, form):
        """Test: Automatisches Ausfüllen der Felder"""
        # Testdaten erstellen
        test_data = DogData(
            owner_name="Max Mustermann",
            dog_name="Bello",
            age=5,
            gender=Gender.MALE,
            neutered=True
        )
        
        # Formular ausfüllen
        form.fill_form(test_data)
        
        # Überprüfen
        assert form.owner_name_input.text() == "Max Mustermann"
        assert form.dog_name_input.text() == "Bello"
        assert form.age_input.value() == 5
        assert form.gender_input.currentText() == "Rüde"
        assert form.neutered_input.isChecked() is True

    def test_fill_form_female_dog(self, form):
        """Test: Automatisches Ausfüllen mit weiblichem Hund"""
        test_data = DogData(
            owner_name="Anna Schmidt",
            dog_name="Luna",
            age=3,
            gender=Gender.FEMALE,
            neutered=False
        )
        
        form.fill_form(test_data)
        
        assert form.owner_name_input.text() == "Anna Schmidt"
        assert form.dog_name_input.text() == "Luna"
        assert form.age_input.value() == 3
        assert form.gender_input.currentText() == "Hündin"
        assert form.neutered_input.isChecked() is False

    def test_reset_form(self, form, qtbot):
        """Test: Formular zurücksetzen"""
        # Felder ausfüllen
        form.owner_name_input.setText("Test Owner")
        form.dog_name_input.setText("Test Dog")
        form.age_input.setValue(7)
        form.gender_input.setCurrentIndex(1)
        form.neutered_input.setChecked(True)
        
        # Zurücksetzen
        qtbot.mouseClick(form.reset_button, Qt.MouseButton.LeftButton)
        
        # Überprüfen
        assert form.owner_name_input.text() == ""
        assert form.dog_name_input.text() == ""
        assert form.age_input.value() == 0
        assert form.gender_input.currentIndex() == 0
        assert form.neutered_input.isChecked() is False

    def test_save_valid_data(self, form, qtbot):
        """Test: Gültige Daten speichern"""
        # Signal-Spy erstellen
        saved_data = []
        form.data_saved.connect(lambda data: saved_data.append(data))
        
        # Formular ausfüllen
        form.owner_name_input.setText("Max Mustermann")
        form.dog_name_input.setText("Bello")
        form.age_input.setValue(5)
        form.gender_input.setCurrentText("Rüde")
        form.neutered_input.setChecked(True)
        
        # Speichern
        qtbot.mouseClick(form.save_button, Qt.MouseButton.LeftButton)
        
        # Überprüfen
        assert len(saved_data) == 1
        dog_data = saved_data[0]
        assert dog_data.owner_name == "Max Mustermann"
        assert dog_data.dog_name == "Bello"
        assert dog_data.age == 5
        assert dog_data.gender == Gender.MALE
        assert dog_data.neutered is True

    def test_save_invalid_empty_owner(self, form, qtbot):
        """Test: Speichern mit leerem Halternamen schlägt fehl"""
        saved_data = []
        form.data_saved.connect(lambda data: saved_data.append(data))
        
        # Nur Hundenamen eingeben
        form.owner_name_input.setText("")  # Leer!
        form.dog_name_input.setText("Bello")
        form.age_input.setValue(5)
        
        # Speichern versuchen
        qtbot.mouseClick(form.save_button, Qt.MouseButton.LeftButton)
        
        # Kein Signal ausgelöst
        assert len(saved_data) == 0

    def test_save_invalid_empty_dog_name(self, form, qtbot):
        """Test: Speichern mit leerem Hundenamen schlägt fehl"""
        saved_data = []
        form.data_saved.connect(lambda data: saved_data.append(data))
        
        form.owner_name_input.setText("Max Mustermann")
        form.dog_name_input.setText("")  # Leer!
        form.age_input.setValue(5)
        
        qtbot.mouseClick(form.save_button, Qt.MouseButton.LeftButton)
        
        assert len(saved_data) == 0

    def test_age_spinbox_validation(self, form):
        """Test: Alter-Eingabefeld akzeptiert nur Integer"""
        # SpinBox erlaubt nur Integer
        form.age_input.setValue(5)
        assert form.age_input.value() == 5
        
        # Minimum/Maximum-Grenzen
        assert form.age_input.minimum() == 0
        assert form.age_input.maximum() == 30

    def test_gender_dropdown_options(self, form):
        """Test: Geschlecht-Dropdown hat korrekte Optionen"""
        assert form.gender_input.count() == 2
        assert form.gender_input.itemText(0) == "Rüde"
        assert form.gender_input.itemText(1) == "Hündin"

    def test_neutered_checkbox(self, form):
        """Test: Kastriert-Checkbox funktioniert"""
        assert form.neutered_input.isChecked() is False
        form.neutered_input.setChecked(True)
        assert form.neutered_input.isChecked() is True
        form.neutered_input.setChecked(False)
        assert form.neutered_input.isChecked() is False
