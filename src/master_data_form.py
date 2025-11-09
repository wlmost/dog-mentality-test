"""
GUI-Formular für die Stammdaten-Erfassung
Modernes, benutzerfreundliches Design nach UX-Best-Practices
"""
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QCheckBox,
    QPushButton, QLabel, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from src.models import DogData, Gender


class MasterDataForm(QWidget):
    """
    Formular zur Erfassung von Halter- und Hundedaten
    
    Design-Prinzipien:
    - Klare visuelle Hierarchie
    - Logische Gruppierung (Halter / Hund)
    - Ausreichend Whitespace
    - Hilfreiche Labels
    - Sofortige Validierung
    """
    
    # Signal wird ausgelöst, wenn Daten erfolgreich gespeichert wurden
    data_saved = Signal(DogData)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stammdaten-Erfassung")
        self._init_ui()
        
    def _init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Überschrift
        title = QLabel("Stammdaten-Erfassung")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Untertitel
        subtitle = QLabel("Bitte geben Sie die Daten des Hundes und seines Halters ein.")
        subtitle.setStyleSheet("color: #666; margin-bottom: 10px;")
        main_layout.addWidget(subtitle)
        
        # Halter-Daten Gruppe
        owner_group = self._create_owner_group()
        main_layout.addWidget(owner_group)
        
        # Hunde-Daten Gruppe
        dog_group = self._create_dog_group()
        main_layout.addWidget(dog_group)
        
        # Button-Bereich
        button_layout = self._create_button_layout()
        main_layout.addLayout(button_layout)
        
        # Spacer für bessere Verteilung
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        self.setMinimumWidth(500)
        
    def _create_owner_group(self) -> QGroupBox:
        """Erstellt die Gruppe für Halterdaten"""
        group = QGroupBox("Daten des Halters")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # Name des Halters
        self.owner_name_input = QLineEdit()
        self.owner_name_input.setPlaceholderText("z.B. Max Mustermann")
        self.owner_name_input.setMinimumHeight(30)
        layout.addRow("Name des Halters*:", self.owner_name_input)
        
        group.setLayout(layout)
        return group
        
    def _create_dog_group(self) -> QGroupBox:
        """Erstellt die Gruppe für Hundedaten"""
        group = QGroupBox("Daten des Hundes")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # Name des Hundes
        self.dog_name_input = QLineEdit()
        self.dog_name_input.setPlaceholderText("z.B. Bello")
        self.dog_name_input.setMinimumHeight(30)
        layout.addRow("Name des Hundes*:", self.dog_name_input)
        
        # Rasse
        self.breed_input = QLineEdit()
        self.breed_input.setPlaceholderText("z.B. Deutscher Schäferhund, Labrador...")
        self.breed_input.setMinimumHeight(30)
        layout.addRow("Rasse:", self.breed_input)
        
        # Alter (Jahre und Monate)
        age_layout = QHBoxLayout()
        age_layout.setSpacing(10)
        
        self.age_years_input = QSpinBox()
        self.age_years_input.setMinimum(0)
        self.age_years_input.setMaximum(30)
        self.age_years_input.setSuffix(" Jahre")
        self.age_years_input.setMinimumHeight(30)
        self.age_years_input.setMinimumWidth(120)
        age_layout.addWidget(self.age_years_input)
        
        self.age_months_input = QSpinBox()
        self.age_months_input.setMinimum(0)
        self.age_months_input.setMaximum(11)
        self.age_months_input.setSuffix(" Monate")
        self.age_months_input.setMinimumHeight(30)
        self.age_months_input.setMinimumWidth(120)
        age_layout.addWidget(self.age_months_input)
        
        age_layout.addStretch()
        
        layout.addRow("Alter*:", age_layout)
        
        # Geschlecht
        self.gender_input = QComboBox()
        self.gender_input.addItems([Gender.MALE.value, Gender.FEMALE.value])
        self.gender_input.setMinimumHeight(30)
        layout.addRow("Geschlecht*:", self.gender_input)
        
        # Kastriert
        self.neutered_input = QCheckBox("Ja, kastriert/sterilisiert")
        layout.addRow("Kastriert:", self.neutered_input)
        
        # Zukünftiges Einsatzgebiet
        self.intended_use_input = QLineEdit()
        self.intended_use_input.setPlaceholderText("z.B. Familienhund, Therapiehund, Schutzhund...")
        self.intended_use_input.setMinimumHeight(30)
        layout.addRow("Zukünftiges Einsatzgebiet:", self.intended_use_input)
        
        group.setLayout(layout)
        return group
        
    def _create_button_layout(self) -> QHBoxLayout:
        """Erstellt den Button-Bereich"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Zurücksetzen-Button
        self.reset_button = QPushButton("Zurücksetzen")
        self.reset_button.setMinimumHeight(35)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.reset_button.clicked.connect(self.reset_form)
        
        # Speichern-Button
        self.save_button = QPushButton("Speichern")
        self.save_button.setMinimumHeight(35)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.save_button.clicked.connect(self.save_data)
        
        layout.addStretch()
        layout.addWidget(self.reset_button)
        layout.addWidget(self.save_button)
        
        return layout
        
    def save_data(self):
        """Speichert die eingegebenen Daten nach Validierung"""
        try:
            # Geschlecht konvertieren
            gender_text = self.gender_input.currentText()
            gender = Gender.MALE if gender_text == "Rüde" else Gender.FEMALE
            
            # DogData erstellen (mit automatischer Validierung)
            dog_data = DogData(
                owner_name=self.owner_name_input.text(),
                dog_name=self.dog_name_input.text(),
                age_years=self.age_years_input.value(),
                age_months=self.age_months_input.value(),
                gender=gender,
                neutered=self.neutered_input.isChecked(),
                breed=self.breed_input.text().strip(),
                intended_use=self.intended_use_input.text().strip()
            )
            
            # Signal aussenden
            self.data_saved.emit(dog_data)
            
            # Erfolgs-Nachricht
            QMessageBox.information(
                self,
                "Erfolgreich gespeichert",
                f"Die Daten für {dog_data.dog_name} wurden erfolgreich gespeichert."
            )
            
            # Formular zurücksetzen
            self.reset_form()
            
        except (ValueError, TypeError) as e:
            # Fehler-Nachricht bei Validierungsproblemen
            QMessageBox.warning(
                self,
                "Eingabefehler",
                f"Bitte überprüfen Sie Ihre Eingaben:\n{str(e)}"
            )
    
    def reset_form(self):
        """Setzt alle Formularfelder zurück"""
        self.owner_name_input.clear()
        self.dog_name_input.clear()
        self.breed_input.clear()
        self.age_years_input.setValue(0)
        self.age_months_input.setValue(0)
        self.gender_input.setCurrentIndex(0)
        self.neutered_input.setChecked(False)
        self.intended_use_input.clear()
        self.owner_name_input.setFocus()
        
    def fill_form(self, dog_data: DogData):
        """
        Füllt das Formular mit vorhandenen Daten
        Nützlich für Tests und Bearbeitung
        """
        self.owner_name_input.setText(dog_data.owner_name)
        self.dog_name_input.setText(dog_data.dog_name)
        self.breed_input.setText(dog_data.breed)
        self.age_years_input.setValue(dog_data.age_years)
        self.age_months_input.setValue(dog_data.age_months)
        
        if dog_data.gender == Gender.MALE:
            self.gender_input.setCurrentText("Rüde")
        else:
            self.gender_input.setCurrentText("Hündin")
            
        self.neutered_input.setChecked(dog_data.neutered)
        self.intended_use_input.setText(dog_data.intended_use)
    
    def get_current_data(self) -> Optional[DogData]:
        """
        Gibt die aktuellen Formulardaten zurück (ohne Validierung zu triggern)
        
        Returns:
            DogData wenn Formular ausgefüllt, sonst None
        """
        # Prüfe ob Pflichtfelder ausgefüllt sind
        if not self.owner_name_input.text().strip() or not self.dog_name_input.text().strip():
            return None
        
        if self.age_years_input.value() == 0 and self.age_months_input.value() == 0:
            return None
        
        try:
            gender = Gender.MALE if self.gender_input.currentText() == "Rüde" else Gender.FEMALE
            
            return DogData(
                owner_name=self.owner_name_input.text().strip(),
                dog_name=self.dog_name_input.text().strip(),
                age_years=self.age_years_input.value(),
                age_months=self.age_months_input.value(),
                gender=gender,
                neutered=self.neutered_input.isChecked(),
                breed=self.breed_input.text().strip(),
                intended_use=self.intended_use_input.text().strip()
            )
        except Exception:
            return None
