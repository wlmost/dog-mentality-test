"""
Hauptfenster der Anwendung

Integriert alle Module:
- Stammdaten-Erfassung
- Testbatterie-Import
- Testdaten-Eingabe
- Export-Funktionen
- OCEAN-Auswertung
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QMenuBar, QMenu, QFileDialog, QMessageBox, QLabel, QPushButton,
    QGroupBox, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QKeySequence
from pathlib import Path
from typing import Optional
import json

from src.master_data_form import MasterDataForm
from src.test_data_form import TestDataForm
from src.test_battery import TestBattery
from src.test_session import TestSession
from src.excel_importer import TestBatteryImporter
from src.models import DogData


class MainWindow(QMainWindow):
    """
    Hauptfenster der Dog Mentality Test Anwendung
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dog Mentality Test - OCEAN Persönlichkeitsanalyse")
        self.setGeometry(100, 50, 1400, 900)
        
        # Daten
        self._current_battery: Optional[TestBattery] = None
        self._current_session: Optional[TestSession] = None
        self._current_file: Optional[Path] = None
        self._unsaved_changes = False
        
        # UI aufbauen
        self._setup_ui()
        self._create_menu_bar()
        self._connect_signals()
        
        # Statusleiste
        self.statusBar().showMessage("Bereit")
    
    def _setup_ui(self):
        """Erstellt das UI-Layout"""
        # Central Widget mit Splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Splitter für Stammdaten und Test-Tabelle
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Stammdaten-Formular
        self._master_data_form = MasterDataForm()
        master_group = QGroupBox("Stammdaten")
        master_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        master_layout = QVBoxLayout(master_group)
        master_layout.addWidget(self._master_data_form)
        splitter.addWidget(master_group)
        
        # Test-Daten-Formular
        self._test_data_form = TestDataForm()
        test_group = QGroupBox("Test-Durchführung")
        test_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        test_layout = QVBoxLayout(test_group)
        test_layout.addWidget(self._test_data_form)
        splitter.addWidget(test_group)
        
        # Splitter-Verhältnis: 30% Stammdaten, 70% Tests
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter, stretch=1)
    
    def _create_header(self) -> QWidget:
        """Erstellt den Header-Bereich"""
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                color: white;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(header)
        
        title = QLabel("🐕 Dog Mentality Test")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        subtitle = QLabel("OCEAN Persönlichkeitsanalyse für Hunde")
        subtitle.setStyleSheet("font-size: 14px; color: #ecf0f1;")
        layout.addWidget(subtitle)
        
        return header
    
    def _create_menu_bar(self):
        """Erstellt die Menüleiste"""
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu("&Datei")
        
        # Neue Session
        new_action = QAction("&Neu", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Neue Test-Session erstellen")
        new_action.triggered.connect(self._new_session)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # Laden
        load_action = QAction("&Öffnen...", self)
        load_action.setShortcut(QKeySequence.StandardKey.Open)
        load_action.setStatusTip("Test-Session laden")
        load_action.triggered.connect(self._load_session)
        file_menu.addAction(load_action)
        
        # Speichern
        save_action = QAction("&Speichern", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip("Test-Session speichern")
        save_action.triggered.connect(self._save_session)
        file_menu.addAction(save_action)
        
        # Speichern als
        save_as_action = QAction("Speichern &als...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip("Test-Session unter neuem Namen speichern")
        save_as_action.triggered.connect(self._save_session_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Beenden
        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Anwendung beenden")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Import-Menü
        import_menu = menubar.addMenu("&Import")
        
        # Testbatterie importieren
        import_battery_action = QAction("&Testbatterie (Excel)...", self)
        import_battery_action.setStatusTip("Testbatterie aus Excel-Datei importieren")
        import_battery_action.triggered.connect(self._import_battery)
        import_menu.addAction(import_battery_action)
        
        # Export-Menü
        export_menu = menubar.addMenu("&Export")
        
        # Excel Export
        export_excel_action = QAction("Als &Excel...", self)
        export_excel_action.setStatusTip("Ergebnisse als Excel exportieren")
        export_excel_action.triggered.connect(self._export_to_excel)
        export_menu.addAction(export_excel_action)
        
        # PDF Export
        export_pdf_action = QAction("Als &PDF...", self)
        export_pdf_action.setStatusTip("Ergebnisse als PDF exportieren")
        export_pdf_action.triggered.connect(self._export_to_pdf)
        export_menu.addAction(export_pdf_action)
        
        # Auswertung-Menü
        analysis_menu = menubar.addMenu("&Auswertung")
        
        # OCEAN Plot
        plot_action = QAction("&OCEAN Radardiagramm", self)
        plot_action.setShortcut("Ctrl+R")
        plot_action.setStatusTip("OCEAN-Werte als Radardiagramm anzeigen")
        plot_action.triggered.connect(self._show_ocean_plot)
        analysis_menu.addAction(plot_action)
        
        # Statistik
        stats_action = QAction("&Statistik", self)
        stats_action.setStatusTip("Statistische Auswertung anzeigen")
        stats_action.triggered.connect(self._show_statistics)
        analysis_menu.addAction(stats_action)
        
        # Hilfe-Menü
        help_menu = menubar.addMenu("&Hilfe")
        
        # Über
        about_action = QAction("&Über", self)
        about_action.setStatusTip("Über diese Anwendung")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """Verbindet Signale"""
        # Wenn Stammdaten gespeichert werden, Session erstellen
        self._master_data_form.data_saved.connect(self._on_master_data_saved)
        
        # Wenn Test-Session gespeichert wird
        self._test_data_form.session_saved.connect(self._on_test_session_saved)
    
    def _on_master_data_saved(self, dog_data: DogData):
        """Callback wenn Stammdaten gespeichert wurden"""
        self.statusBar().showMessage(f"Stammdaten für {dog_data.dog_name} gespeichert", 3000)
        self._unsaved_changes = True
        
        # Wenn Testbatterie geladen ist, Test-Session initialisieren
        if self._current_battery:
            self._test_data_form.load_data(dog_data, self._current_battery)
    
    def _on_test_session_saved(self, session: TestSession):
        """Callback wenn Test-Session gespeichert wurde"""
        self._current_session = session
        self._unsaved_changes = False
        self.statusBar().showMessage("Test-Session gespeichert", 3000)
    
    def _new_session(self):
        """Erstellt eine neue Session"""
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Ungespeicherte Änderungen",
                "Es gibt ungespeicherte Änderungen. Wirklich neue Session starten?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Formulare zurücksetzen
        self._master_data_form.reset_form()
        # Test-Form hat keinen Reset - wird neu geladen wenn Stammdaten eingegeben
        
        self._current_session = None
        self._current_file = None
        self._unsaved_changes = False
        
        self.statusBar().showMessage("Neue Session erstellt", 3000)
    
    def _load_session(self):
        """Lädt eine gespeicherte Session"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Test-Session laden",
            "data",
            "JSON Files (*.json)"
        )
        
        if not filename:
            return
        
        try:
            session = TestSession.load_from_file(filename)
            
            # Stammdaten in Formular laden
            self._master_data_form.fill_form(session.dog_data)
            
            # Testbatterie muss auch geladen werden
            if not self._current_battery or self._current_battery.name != session.battery_name:
                QMessageBox.warning(
                    self,
                    "Testbatterie fehlt",
                    f"Die Testbatterie '{session.battery_name}' muss zuerst importiert werden."
                )
                return
            
            # Test-Daten laden
            self._test_data_form.load_data(session.dog_data, self._current_battery)
            
            # Gespeicherte Ergebnisse in Tabelle eintragen
            for test_num, result in session.results.items():
                row = int(test_num) - 1
                if row < self._test_data_form._table.rowCount():
                    # Score setzen
                    score_widget = self._test_data_form._table.cellWidget(row, 3)
                    if score_widget:
                        score_widget.setValue(result.score)
                    
                    # Notizen setzen
                    notes_item = self._test_data_form._table.item(row, 4)
                    if notes_item:
                        notes_item.setText(result.notes)
            
            # Session-Notizen
            self._test_data_form._session_notes.setPlainText(session.session_notes)
            
            self._current_session = session
            self._current_file = Path(filename)
            self._unsaved_changes = False
            
            self.statusBar().showMessage(f"Session geladen: {filename}", 3000)
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Laden:\n{str(e)}"
            )
    
    def _save_session(self):
        """Speichert die aktuelle Session"""
        if self._current_file:
            self._save_to_file(self._current_file)
        else:
            self._save_session_as()
    
    def _save_session_as(self):
        """Speichert die Session unter neuem Namen"""
        if not self._test_data_form.get_session():
            QMessageBox.warning(
                self,
                "Keine Daten",
                "Bitte zuerst Stammdaten und Tests eingeben."
            )
            return
        
        # Standardnamen vorschlagen
        dog_data = self._master_data_form.get_current_data()
        if dog_data:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dog_name = dog_data.dog_name.replace(" ", "_")
            default_name = f"session_{dog_name}_{timestamp}.json"
        else:
            default_name = "session.json"
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Test-Session speichern",
            f"data/{default_name}",
            "JSON Files (*.json)"
        )
        
        if filename:
            self._save_to_file(Path(filename))
    
    def _save_to_file(self, filepath: Path):
        """Speichert Session in Datei"""
        try:
            session = self._test_data_form.get_session()
            if not session:
                QMessageBox.warning(self, "Fehler", "Keine Session zum Speichern vorhanden.")
                return
            
            # Session-Notizen aktualisieren
            session.session_notes = self._test_data_form._session_notes.toPlainText()
            
            session.save_to_file(str(filepath))
            
            self._current_file = filepath
            self._current_session = session
            self._unsaved_changes = False
            
            self.statusBar().showMessage(f"Gespeichert: {filepath.name}", 3000)
        
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern:\n{str(e)}")
    
    def _import_battery(self):
        """Importiert eine Testbatterie aus Excel"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Testbatterie importieren",
            "data",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if not filename:
            return
        
        try:
            importer = TestBatteryImporter(filename)
            battery = importer.import_battery()
            
            self._current_battery = battery
            
            QMessageBox.information(
                self,
                "Import erfolgreich",
                f"Testbatterie '{battery.name}' importiert.\n"
                f"Anzahl Tests: {len(battery.tests)}"
            )
            
            self.statusBar().showMessage(f"Testbatterie '{battery.name}' importiert", 3000)
            
            # Tests sofort anzeigen
            self._test_data_form.load_battery(battery)
            
            # Wenn Stammdaten bereits vorhanden, komplett laden
            dog_data = self._master_data_form.get_current_data()
            if dog_data:
                self._test_data_form.load_data(dog_data, battery)
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import-Fehler",
                f"Fehler beim Importieren:\n{str(e)}"
            )
    
    def _export_to_excel(self):
        """Exportiert Ergebnisse als Excel"""
        QMessageBox.information(
            self,
            "Noch nicht implementiert",
            "Excel-Export wird in Modul 4 implementiert."
        )
    
    def _export_to_pdf(self):
        """Exportiert Ergebnisse als PDF"""
        QMessageBox.information(
            self,
            "Noch nicht implementiert",
            "PDF-Export wird in Modul 4 implementiert."
        )
    
    def _show_ocean_plot(self):
        """Zeigt OCEAN Radardiagramm"""
        QMessageBox.information(
            self,
            "Noch nicht implementiert",
            "OCEAN-Radardiagramm wird in Modul 5 implementiert."
        )
    
    def _show_statistics(self):
        """Zeigt Statistik"""
        if not self._current_session:
            QMessageBox.warning(
                self,
                "Keine Daten",
                "Bitte zuerst eine Session laden oder Tests durchführen."
            )
            return
        
        # Einfache Statistik
        total = len(self._current_battery.tests) if self._current_battery else 0
        completed = self._current_session.get_completed_count()
        
        stats_text = f"""
Test-Session Statistik
═══════════════════════

Hund: {self._current_session.dog_data.dog_name}
Testbatterie: {self._current_session.battery_name}

Fortschritt:
  Abgeschlossen: {completed} / {total} Tests
  Prozent: {(completed / total * 100) if total > 0 else 0:.1f}%
"""
        
        QMessageBox.information(self, "Statistik", stats_text)
    
    def _show_about(self):
        """Zeigt About-Dialog"""
        about_text = """
<h2>Dog Mentality Test</h2>
<p><b>Version 1.0</b></p>
<p>OCEAN Persönlichkeitsanalyse für Hunde</p>
<br>
<p>Entwickelt mit:</p>
<ul>
<li>Python 3.12</li>
<li>PySide6 6.10</li>
<li>openpyxl, pandas, matplotlib</li>
</ul>
<br>
<p>© 2025 - Clean Code & TDD</p>
"""
        QMessageBox.about(self, "Über Dog Mentality Test", about_text)
    
    def closeEvent(self, event):
        """Überschreibt Close-Event für Abfrage bei ungespeicherten Änderungen"""
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Ungespeicherte Änderungen",
                "Es gibt ungespeicherte Änderungen. Wirklich beenden?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
