"""
GUI-Formular für die Eingabe von Testdaten
Zeigt alle Tests der Batterie in einer Tabelle mit editierbaren Score- und Notizen-Feldern
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox, QComboBox, QTextEdit,
    QGroupBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from datetime import datetime
from typing import Optional

from src.models import DogData
from src.test_battery import TestBattery, Test
from src.test_session import TestSession, TestResult
from src.test_detail_dialog import TestDetailDialog


class TestDataForm(QWidget):
    """Widget zur Eingabe von Testdaten in tabellarischer Form"""
    
    session_saved = Signal(TestSession)  # Signal beim Speichern
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dog_data: Optional[DogData] = None
        self._battery: Optional[TestBattery] = None
        self._session: Optional[TestSession] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt das UI-Layout"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # Reduziert von 20 auf 10
        layout.setContentsMargins(15, 15, 15, 15)  # Reduziert von 20 auf 15
        
        # Titelbereich (kompakt)
        title = QLabel("Testdaten-Eingabe")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")  # Reduziert von 18px
        layout.addWidget(title)
        
        # Info-Bereich (kompakt, kein stretch)
        self._info_group = self._create_info_section()
        layout.addWidget(self._info_group, stretch=0)
        
        # Tabelle für Test-Ergebnisse (größter Bereich, nutzt verfügbaren Platz)
        self._table = self._create_results_table()
        layout.addWidget(self._table, stretch=10)  # Erhöht von 1 auf 10 für mehr Platz
        
        # Notizen-Bereich (kompakt)
        notes_group = QGroupBox("Session-Notizen")
        notes_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        notes_layout = QVBoxLayout(notes_group)
        self._session_notes = QTextEdit()
        self._session_notes.setPlaceholderText("Allgemeine Notizen zur Test-Session...")
        self._session_notes.setMinimumHeight(60)
        self._session_notes.setMaximumHeight(80)  # Reduziert von 100 auf 80
        notes_layout.addWidget(self._session_notes)
        layout.addWidget(notes_group, stretch=0)  # Kein stretch, feste Größe
        
        # Button-Leiste
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self._save_btn = QPushButton("Session speichern")
        self._save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self._save_btn.clicked.connect(self._save_session)
        self._save_btn.setEnabled(False)
        button_layout.addWidget(self._save_btn)
        
        layout.addLayout(button_layout)
    
    def _create_info_section(self) -> QGroupBox:
        """Erstellt den Info-Bereich (kompakt)"""
        group = QGroupBox("Session-Information")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)  # Reduzierter Abstand
        layout.setContentsMargins(10, 10, 10, 10)  # Kompakte Margins
        
        self._dog_info_label = QLabel("Kein Hund ausgewählt")
        self._dog_info_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self._dog_info_label)
        
        self._battery_info_label = QLabel("Keine Testbatterie geladen")
        self._battery_info_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self._battery_info_label)
        
        self._progress_label = QLabel("Fortschritt: 0 / 0 Tests")
        self._progress_label.setStyleSheet("color: #3498db; font-weight: bold; font-size: 12px;")
        layout.addWidget(self._progress_label)
        
        group.setMaximumHeight(100)  # Maximale Höhe begrenzen
        
        return group
    
    def _create_results_table(self) -> QTableWidget:
        """Erstellt die Ergebnistabelle"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Nr.", "Testbeschreibung", "OCEAN", "Score (-2 bis +2)", "Notizen"
        ])
        
        # Minimale Höhe für mindestens 5 sichtbare Zeilen
        table.setMinimumHeight(250)
        
        # Spaltenbreiten
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        # Styling
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #ecf0f1;
                border: 1px solid #bdc3c7;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        
        table.setAlternatingRowColors(True)
        # itemChanged wird nach populate_table verbunden
        # itemClicked wird für Testbeschreibung-Details verbunden
        table.itemClicked.connect(self._on_item_clicked)
        
        return table
    
    def load_battery(self, battery: TestBattery):
        """
        Lädt nur die Testbatterie (ohne Hunddaten)
        
        Args:
            battery: Testbatterie
        """
        self._battery = battery
        self._battery_info_label.setText(f"Testbatterie: {battery.name}")
        
        # Tabelle füllen
        self._populate_table()
        
        # Signal nur verbinden wenn noch nicht verbunden
        try:
            self._table.itemChanged.disconnect(self._on_table_changed)
        except RuntimeError:
            pass  # War noch nicht verbunden
        
        self._table.itemChanged.connect(self._on_table_changed)
        
        # Session wird erst erstellt wenn Stammdaten vorhanden
        self._update_progress()
    
    def load_data(self, dog_data: DogData, battery: TestBattery):
        """
        Lädt Hunddaten und Testbatterie
        
        Args:
            dog_data: Stammdaten des Hundes
            battery: Testbatterie
        """
        self._dog_data = dog_data
        self._battery = battery
        self._session = TestSession(dog_data=dog_data, battery_name=battery.name)
        
        # Info aktualisieren
        self._dog_info_label.setText(
            f"Hund: {dog_data.dog_name} ({dog_data.age_display()}, {dog_data.gender.value})"
        )
        self._battery_info_label.setText(f"Testbatterie: {battery.name}")
        
        # Tabelle füllen
        self._populate_table()
        
        # Signal nur verbinden wenn noch nicht verbunden
        try:
            self._table.itemChanged.disconnect(self._on_table_changed)
        except RuntimeError:
            pass  # War noch nicht verbunden
        
        self._table.itemChanged.connect(self._on_table_changed)
        
        # Buttons aktivieren
        self._save_btn.setEnabled(True)
        
        self._update_progress()
    
    def _populate_table(self):
        """Füllt die Tabelle mit Tests aus der Batterie"""
        if not self._battery:
            return
        
        tests = sorted(self._battery.tests, key=lambda t: t.number)
        self._table.setRowCount(len(tests))
        
        for row, test in enumerate(tests):
            # Test-Nummer (nicht editierbar)
            num_item = QTableWidgetItem(str(test.number))
            num_item.setFlags(num_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 0, num_item)
            
            # Beschreibung (nicht editierbar, aber klickbar für Details)
            desc_item = QTableWidgetItem(test.name)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            desc_item.setData(Qt.ItemDataRole.UserRole, test)  # Test-Objekt speichern
            desc_item.setToolTip("Klicken für Details zum Test")
            desc_item.setForeground(QColor("#3498db"))  # Blaue Farbe für Klickbarkeit
            self._table.setItem(row, 1, desc_item)
            
            # OCEAN-Dimension (nicht editierbar)
            ocean_item = QTableWidgetItem(test.ocean_dimension.value)
            ocean_item.setFlags(ocean_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            ocean_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Farben für OCEAN-Dimensionen
            colors = {
                "Openness": "#e74c3c",
                "Conscientiousness": "#3498db",
                "Extraversion": "#f39c12",
                "Agreeableness": "#2ecc71",
                "Neuroticism": "#9b59b6"
            }
            ocean_item.setBackground(QColor(colors.get(test.ocean_dimension.value, "#95a5a6")))
            ocean_item.setForeground(QColor("white"))
            self._table.setItem(row, 2, ocean_item)
            
            # Score (editierbar mit SpinBox)
            score_widget = QSpinBox()
            score_widget.setRange(-2, 2)
            score_widget.setValue(0)
            score_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            score_widget.valueChanged.connect(self._on_score_changed)
            self._table.setCellWidget(row, 3, score_widget)
            
            # Notizen (editierbar)
            notes_item = QTableWidgetItem("")
            notes_item.setData(Qt.ItemDataRole.UserRole, test.number)  # Test-Nummer speichern
            self._table.setItem(row, 4, notes_item)
    
    def _on_item_clicked(self, item: QTableWidgetItem):
        """
        Callback bei Klick auf Tabellenzelle
        Öffnet Detail-Dialog bei Klick auf Testbeschreibung (Spalte 1)
        """
        if item.column() == 1:  # Testbeschreibung-Spalte
            test = item.data(Qt.ItemDataRole.UserRole)
            if test:
                dialog = TestDetailDialog(test, self)
                dialog.exec()
    
    def _on_score_changed(self):
        """Callback bei Score-Änderung"""
        self._update_session_data()
        self._update_progress()
    
    def _on_table_changed(self, item: QTableWidgetItem):
        """Callback bei Tabellen-Änderung"""
        if item.column() == 4:  # Notizen-Spalte
            self._update_session_data()
    
    def _update_session_data(self):
        """Aktualisiert die Session-Daten aus der Tabelle"""
        if not self._session:
            return
        
        for row in range(self._table.rowCount()):
            test_num = int(self._table.item(row, 0).text())
            score_widget = self._table.cellWidget(row, 3)
            notes_item = self._table.item(row, 4)
            
            score = score_widget.value()
            notes = notes_item.text() if notes_item else ""
            
            # Immer speichern - Score 0 ist ein valider Wert (neutrales Verhalten)
            result = TestResult(test_number=test_num, score=score, notes=notes)
            self._session.add_result(result)
    
    def _update_progress(self):
        """Aktualisiert die Fortschrittsanzeige"""
        if not self._session or not self._battery:
            return
        
        # Zähle nur Tests mit Score != 0 als "bearbeitet"
        completed = sum(1 for result in self._session.results.values() if result.score != 0)
        total = len(self._battery.tests)
        self._progress_label.setText(f"Fortschritt: {completed} / {total} Tests")
    
    def _save_session(self):
        """Speichert die Test-Session"""
        if not self._session:
            return
        
        # Session-Notizen übernehmen
        self._session.session_notes = self._session_notes.toPlainText()
        
        # Daten aus Tabelle aktualisieren
        self._update_session_data()
        
        # Dateiname generieren
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dog_name = self._dog_data.dog_name.replace(" ", "_")
        filename = f"data/session_{dog_name}_{timestamp}.json"
        
        try:
            self._session.save_to_file(filename)
            self.session_saved.emit(self._session)
            
            QMessageBox.information(
                self,
                "Gespeichert",
                f"Session erfolgreich gespeichert:\n{filename}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Speichern:\n{str(e)}"
            )
    
    def get_session(self) -> Optional[TestSession]:
        """Gibt die aktuelle Session zurück"""
        return self._session
