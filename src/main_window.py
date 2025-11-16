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
    QScrollArea, QApplication, QGroupBox, QFormLayout, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QKeySequence, QScreen
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

from src.master_data_form import MasterDataForm
from src.test_data_form import TestDataForm
from src.test_battery import TestBattery
from src.test_session import TestSession
from src.excel_importer import TestBatteryImporter
from src.excel_exporter import ExcelExporter, ExcelExportError
from src.pdf_exporter import PdfExporter, PdfExportError
from src.models import DogData
from src.ocean_analyzer import OceanAnalyzer
from src.ocean_chart import OceanRadarChart
from src.settings import settings
from src.ai_service import AIProfileService, AIProfileError, AIProfileConnectionError, AIProfileConfigError


class MainWindow(QMainWindow):
    """
    Hauptfenster der Dog Mentality Test Anwendung
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dog Mentality Test - OCEAN Persönlichkeitsanalyse")
        
        # Responsive Fenstergröße basierend auf Bildschirmauflösung
        self._setup_window_size()
        
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
    
    def _setup_window_size(self):
        """
        Setzt Fenstergröße responsiv basierend auf Bildschirmauflösung
        Passt sich flexibel an kleine Bildschirme an
        """
        # Bildschirmauflösung ermitteln
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # Für sehr kleine Bildschirme: Maximiere verfügbaren Platz
            if screen_height < 800:
                # Kleine Laptops: Nutze fast den gesamten Bildschirm
                width = screen_width - 40
                height = screen_height - 100  # Platz für Taskleiste/Dock
            else:
                # Normale/Große Bildschirme: 85-90% nutzen
                width = int(screen_width * 0.90)
                height = int(screen_height * 0.85)
            
            # Absolutes Minimum für Nutzbarkeit (sehr konservativ)
            width = max(900, width)
            height = max(650, height)
            
            # Maximum für große Bildschirme
            width = min(1600, width)
            height = min(1000, height)
            
            # Sicherstellen, dass Fenster niemals größer als Bildschirm
            width = min(width, screen_width - 40)
            height = min(height, screen_height - 100)
            
            # Fenster positionieren (oben, leicht zentriert)
            x = max(20, (screen_width - width) // 2)
            y = 20  # Immer 20px von oben (Menüleiste immer sichtbar)
            
            self.setGeometry(x, y, width, height)
        else:
            # Fallback: Sehr konservative Größe
            self.setGeometry(50, 30, 900, 650)
        
        # Minimale Fenstergröße flexibel setzen
        min_width = 900
        min_height = 650
        
        # Wenn Bildschirm kleiner als Minimum, anpassen
        if screen:
            screen_geom = screen.availableGeometry()
            if screen_geom.height() < 750:
                min_height = screen_geom.height() - 100
            if screen_geom.width() < 950:
                min_width = screen_geom.width() - 50
            
        self.setMinimumSize(max(800, min_width), max(600, min_height))
    
    def _setup_ui(self):
        """Erstellt das UI-Layout"""
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Tab-Widget für die drei Bereiche
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 10px 20px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background: #d5dbdb;
            }
        """)
        
        # Tab 1: Stammdaten (mit ScrollArea für kleine Bildschirme)
        self._master_data_form = MasterDataForm()
        master_scroll = QScrollArea()
        master_scroll.setWidgetResizable(True)
        master_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        master_widget = QWidget()
        master_layout = QVBoxLayout(master_widget)
        master_layout.setContentsMargins(20, 20, 20, 20)
        master_layout.addWidget(self._master_data_form)
        master_layout.addStretch()
        
        master_scroll.setWidget(master_widget)
        self._tab_widget.addTab(master_scroll, "📋 Stammdaten")
        
        # Tab 2: Test-Durchführung (mit ScrollArea)
        self._test_data_form = TestDataForm()
        test_scroll = QScrollArea()
        test_scroll.setWidgetResizable(True)
        test_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        test_widget = QWidget()
        test_layout = QVBoxLayout(test_widget)
        test_layout.setContentsMargins(20, 20, 20, 20)
        test_layout.addWidget(self._test_data_form)
        
        test_scroll.setWidget(test_widget)
        self._tab_widget.addTab(test_scroll, "🧪 Test-Durchführung")
        
        # Tab 3: Auswertung
        self._analysis_widget = self._create_analysis_tab()
        self._tab_widget.addTab(self._analysis_widget, "📊 Auswertung")
        
        layout.addWidget(self._tab_widget, stretch=1)
    
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
    
    def _create_analysis_tab(self) -> QWidget:
        """Erstellt den Auswertungs-Tab (mit ScrollArea)"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titel
        title = QLabel("OCEAN Persönlichkeitsanalyse")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Info-Text
        info = QLabel(
            "Hier wird das OCEAN-Radardiagramm angezeigt.\n\n"
            "Klicken Sie auf den Button 'Radardiagramm erstellen' um die Visualisierung zu erstellen."
        )
        info.setStyleSheet("color: #7f8c8d; font-size: 13px; margin: 20px 0;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Halter-Profil Eingabemaske
        owner_group = self._create_owner_profile_input()
        layout.addWidget(owner_group)
        
        # Platzhalter für Plot (wird durch OceanRadarChart ersetzt)
        self._plot_placeholder = QLabel("📊 OCEAN Radardiagramm")
        self._plot_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._plot_placeholder.setStyleSheet("""
            background-color: #ecf0f1;
            border: 2px dashed #bdc3c7;
            border-radius: 10px;
            padding: 100px;
            font-size: 16px;
            font-weight: bold;
            color: #95a5a6;
        """)
        
        # Container für Chart mit ScrollArea für große Diagramme
        self._chart_container = QWidget()
        chart_layout = QVBoxLayout(self._chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.addWidget(self._plot_placeholder)
        
        # ScrollArea für Chart (damit große Diagramme scrollbar sind)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self._chart_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        layout.addWidget(scroll_area, stretch=1)
        
        # Button-Leiste
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Statistik-Button
        stats_btn = QPushButton("Statistik anzeigen")
        stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        stats_btn.clicked.connect(self._show_statistics)
        button_layout.addWidget(stats_btn)
        
        # Plot-Button
        plot_btn = QPushButton("Radardiagramm erstellen")
        plot_btn.setStyleSheet("""
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
        """)
        plot_btn.clicked.connect(self._show_ocean_plot)
        button_layout.addWidget(plot_btn)
        
        layout.addLayout(button_layout)
        
        scroll.setWidget(widget)
        return scroll
    
    def _create_owner_profile_input(self) -> QGroupBox:
        """Erstellt die Eingabemaske für das Fragebogen-Profil"""
        group = QGroupBox("Fragebogen-Profil (Ergebnis des Fragebogens)")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #3498db;
            }
        """)
        
        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Info-Text
        info = QLabel(
            "Tragen Sie hier die OCEAN-Werte aus dem Fragebogen ein.\n"
            "Wertebereich: -14 bis +14 (abhängig von der Testbatterie)"
        )
        info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        info.setWordWrap(True)
        layout.addRow(info)
        
        # Eingabefelder für OCEAN-Dimensionen
        from PySide6.QtWidgets import QSpinBox
        
        self._owner_o_input = QSpinBox()
        self._owner_o_input.setRange(-14, 14)
        self._owner_o_input.setValue(0)
        self._owner_o_input.setMinimumHeight(30)
        layout.addRow("Offenheit (O):", self._owner_o_input)
        
        self._owner_c_input = QSpinBox()
        self._owner_c_input.setRange(-14, 14)
        self._owner_c_input.setValue(0)
        self._owner_c_input.setMinimumHeight(30)
        layout.addRow("Gewissenhaftigkeit (C):", self._owner_c_input)
        
        self._owner_e_input = QSpinBox()
        self._owner_e_input.setRange(-14, 14)
        self._owner_e_input.setValue(0)
        self._owner_e_input.setMinimumHeight(30)
        layout.addRow("Extraversion (E):", self._owner_e_input)
        
        self._owner_a_input = QSpinBox()
        self._owner_a_input.setRange(-14, 14)
        self._owner_a_input.setValue(0)
        self._owner_a_input.setMinimumHeight(30)
        layout.addRow("Verträglichkeit (A):", self._owner_a_input)
        
        self._owner_n_input = QSpinBox()
        self._owner_n_input.setRange(-14, 14)
        self._owner_n_input.setValue(0)
        self._owner_n_input.setMinimumHeight(30)
        layout.addRow("Neurotizismus (N):", self._owner_n_input)
        
        # Button zum Übernehmen
        apply_btn = QPushButton("Fragebogen-Profil übernehmen")
        apply_btn.setMinimumHeight(35)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        apply_btn.clicked.connect(self._apply_owner_profile)
        layout.addRow(apply_btn)
        
        # Separator
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #bdc3c7; margin: 10px 0;")
        layout.addRow(separator)
        
        # KI-Features Info
        ki_info = QLabel(
            "KI-gestützte Features (benötigt OpenAI API-Key in .env)"
        )
        ki_info.setStyleSheet("color: #7f8c8d; font-size: 12px; font-style: italic;")
        ki_info.setWordWrap(True)
        layout.addRow(ki_info)
        
        # KI-Idealprofil Button
        self._load_ideal_btn = QPushButton("KI-Idealprofil laden")
        self._load_ideal_btn.setMinimumHeight(35)
        self._load_ideal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #ecf0f1;
            }
        """)
        self._load_ideal_btn.clicked.connect(self._load_ideal_profile)
        layout.addRow(self._load_ideal_btn)
        
        # KI-Bewertung Button
        self._show_assessment_btn = QPushButton("KI-Bewertung anzeigen")
        self._show_assessment_btn.setMinimumHeight(35)
        self._show_assessment_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #ecf0f1;
            }
        """)
        self._show_assessment_btn.clicked.connect(self._show_assessment)
        self._show_assessment_btn.setEnabled(False)  # Erst aktiv wenn alle 3 Profile da
        layout.addRow(self._show_assessment_btn)
        
        # Prüfe ob API konfiguriert ist
        if not settings.is_openai_configured:
            self._load_ideal_btn.setEnabled(False)
            self._load_ideal_btn.setToolTip(
                "OpenAI API nicht konfiguriert. Bitte .env Datei erstellen.\n"
                "Siehe docs/api_setup.md für Anleitung."
            )
            self._show_assessment_btn.setToolTip(
                "OpenAI API nicht konfiguriert. Bitte .env Datei erstellen.\n"
                "Siehe docs/api_setup.md für Anleitung."
            )
        
        group.setLayout(layout)
        return group
    
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
            # Automatisch zum Test-Tab wechseln
            self._tab_widget.setCurrentIndex(1)
            self.statusBar().showMessage(f"Bereit für Tests mit {dog_data.dog_name}", 3000)
    
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
        
        # Zurück zum Stammdaten-Tab
        self._tab_widget.setCurrentIndex(0)
        
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
            
            # KI-Profile wiederherstellen (wenn vorhanden) - NACH Session-Zuweisung
            if session.ideal_profile or session.owner_profile:
                if session.results and self._current_battery:
                    # OCEAN-Analyse mit gespeicherten Profilen durchführen
                    analyzer = OceanAnalyzer(session, self._current_battery)
                    scores = analyzer.calculate_ocean_scores()
                    
                    # Gespeicherte Profile übernehmen
                    if session.ideal_profile:
                        scores.ideal_profile = session.ideal_profile
                    if session.owner_profile:
                        scores.owner_profile = session.owner_profile
                    
                    self._current_ocean_scores = scores
                    
                    # Chart mit allen Profilen anzeigen
                    layout = self._chart_container.layout()
                    if layout:
                        while layout.count():
                            item = layout.takeAt(0)
                            if item:
                                widget = item.widget()
                                if widget:
                                    widget.deleteLater()
                    else:
                        from PySide6.QtWidgets import QVBoxLayout
                        layout = QVBoxLayout(self._chart_container)
                        layout.setContentsMargins(0, 0, 0, 0)
                    
                    self._tab_widget.setCurrentIndex(2)
                    from PySide6.QtCore import QCoreApplication
                    QCoreApplication.processEvents()
                    
                    chart_widget = OceanRadarChart(scores, parent=self._chart_container)
                    layout.addWidget(chart_widget)
                    QCoreApplication.processEvents()
                    
                    self.statusBar().showMessage(
                        f"Session geladen mit KI-Profilen: {filename}", 3000
                    )
                    
                    # Assessment-Button-Status aktualisieren
                    self._update_assessment_button_state()
                    return
            
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
        """Speichert Session in Datei (inkl. KI-Profile)"""
        try:
            session = self._test_data_form.get_session()
            if not session:
                QMessageBox.warning(self, "Fehler", "Keine Session zum Speichern vorhanden.")
                return
            
            # Session-Notizen aktualisieren
            session.session_notes = self._test_data_form._session_notes.toPlainText()
            
            # KI-Profile speichern (falls vorhanden)
            if hasattr(self, '_current_ocean_scores') and self._current_ocean_scores is not None:
                session.ideal_profile = self._current_ocean_scores.ideal_profile
                session.owner_profile = self._current_ocean_scores.owner_profile
            
            # AI-Assessment wird nicht persistent gespeichert, da es bei Bedarf neu generiert wird
            
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
                # Zum Test-Tab wechseln wenn Stammdaten vorhanden
                self._tab_widget.setCurrentIndex(1)
            else:
                # Hinweis dass Stammdaten benötigt werden
                QMessageBox.information(
                    self,
                    "Testbatterie geladen",
                    f"Testbatterie '{battery.name}' wurde geladen.\n\n"
                    "Bitte geben Sie zuerst die Stammdaten ein, um mit den Tests zu beginnen."
                )
                self._tab_widget.setCurrentIndex(0)  # Zum Stammdaten-Tab
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import-Fehler",
                f"Fehler beim Importieren:\n{str(e)}"
            )
    
    def _export_to_excel(self):
        """Exportiert Ergebnisse als Excel"""
        if not self._current_session:
            QMessageBox.warning(
                self,
                "Keine Daten",
                "Bitte erst eine Session erstellen oder laden."
            )
            return
        
        # FileDialog für Speicherort
        default_name = f"export_{self._current_session.dog_data.dog_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Excel exportieren",
            str(Path.home() / "Documents" / default_name),
            "Excel-Dateien (*.xlsx)"
        )
        
        if not filepath:
            return
        
        try:
            # Export durchführen
            exporter = ExcelExporter(battery=self._current_battery)
            exporter.export_to_excel(self._current_session, filepath)
            
            QMessageBox.information(
                self,
                "Export erfolgreich",
                f"Session erfolgreich exportiert:\n{filepath}"
            )
            
            self.statusBar().showMessage(f"Excel-Export: {filepath}", 5000)
            
        except ExcelExportError as e:
            QMessageBox.critical(
                self,
                "Export-Fehler",
                f"Fehler beim Excel-Export:\n{str(e)}"
            )
    
    def _export_to_pdf(self):
        """Exportiert Ergebnisse als PDF"""
        if not self._current_session:
            QMessageBox.warning(
                self,
                "Keine Daten",
                "Bitte erst eine Session erstellen oder laden."
            )
            return
        
        # FileDialog für Speicherort
        default_name = f"report_{self._current_session.dog_data.dog_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "PDF exportieren",
            str(Path.home() / "Documents" / default_name),
            "PDF-Dateien (*.pdf)"
        )
        
        if not filepath:
            return
        
        try:
            # Export durchführen
            exporter = PdfExporter(battery=self._current_battery)
            exporter.export_to_pdf(self._current_session, filepath)
            
            QMessageBox.information(
                self,
                "Export erfolgreich",
                f"PDF-Report erfolgreich erstellt:\n{filepath}"
            )
            
            self.statusBar().showMessage(f"PDF-Export: {filepath}", 5000)
            
        except PdfExportError as e:
            QMessageBox.critical(
                self,
                "Export-Fehler",
                f"Fehler beim PDF-Export:\n{str(e)}"
            )
    
    def _show_ocean_plot(self):
        """Zeigt OCEAN Radardiagramm"""
        if not self._current_session or self._current_session.get_completed_count() == 0:
            QMessageBox.warning(
                self,
                "Keine Daten",
                "Bitte führen Sie zuerst Tests durch, um eine Auswertung zu erstellen."
            )
            return
        
        if not self._current_battery:
            QMessageBox.warning(
                self,
                "Keine Testbatterie",
                "Bitte laden Sie zuerst eine Testbatterie, um die OCEAN-Dimensionen zu berechnen."
            )
            return
        
        try:
            # OCEAN-Scores berechnen
            analyzer = OceanAnalyzer(self._current_session, self._current_battery)
            scores = analyzer.calculate_ocean_scores()
            
            # Bestehende Profile bewahren (falls vorhanden)
            if hasattr(self, '_current_ocean_scores') and self._current_ocean_scores is not None:
                scores.owner_profile = self._current_ocean_scores.owner_profile
                scores.ideal_profile = self._current_ocean_scores.ideal_profile
            
            # Scores speichern für spätere Updates (z.B. Fragebogen-Profil)
            self._current_ocean_scores = scores
            
            # Altes Widget aus Container entfernen und löschen
            layout = self._chart_container.layout()
            
            if layout:
                # Alle Widgets aus Layout entfernen
                while layout.count():
                    item = layout.takeAt(0)
                    if item:
                        widget = item.widget()
                        if widget:
                            widget.deleteLater()
            else:
                # Fallback: Layout neu erstellen falls nicht vorhanden
                from PySide6.QtWidgets import QVBoxLayout
                layout = QVBoxLayout(self._chart_container)
                layout.setContentsMargins(0, 0, 0, 0)
            
            # ERST zum Tab wechseln, DANN Chart erstellen!
            # Vermeidet Rendering-Probleme wenn Tab nicht sichtbar ist
            self._tab_widget.setCurrentIndex(2)
            
            # Event-Loop verarbeiten lassen
            from PySide6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            
            # Radardiagramm erstellen - NACH Tab-Wechsel!
            chart_widget = OceanRadarChart(scores, parent=self._chart_container)
            
            # Chart zum Layout hinzufügen
            layout.addWidget(chart_widget)
            
            # Event-Loop verarbeiten lassen, damit Chart gerendert wird
            QCoreApplication.processEvents()
            
            # Statusmeldung
            status_msg = (
                f"OCEAN-Analyse erstellt: "
                f"O={scores.openness_count}, "
                f"C={scores.conscientiousness_count}, "
                f"E={scores.extraversion_count}, "
                f"A={scores.agreeableness_count}, "
                f"N={scores.neuroticism_count} Tests"
            )
            self.statusBar().showMessage(status_msg, 5000)
            
            # Button-Status aktualisieren
            self._update_assessment_button_state()
        except Exception as e:
            import traceback
            error_msg = f"Fehler beim Erstellen des Radardiagramms:\n\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(
                self,
                "Fehler",
                error_msg
            )
    
    def _apply_owner_profile(self):
        """Übernimmt Fragebogen-Profil-Werte und aktualisiert das Radardiagramm"""
        # Prüfen ob OCEAN-Analyse existiert
        if not hasattr(self, '_current_ocean_scores') or self._current_ocean_scores is None:
            QMessageBox.warning(
                self,
                "Keine Analyse",
                "Bitte erstellen Sie zuerst eine OCEAN-Analyse, bevor Sie das Fragebogen-Profil übernehmen."
            )
            return
        
        # Werte aus SpinBoxes auslesen
        owner_dict = {
            'O': self._owner_o_input.value(),
            'C': self._owner_c_input.value(),
            'E': self._owner_e_input.value(),
            'A': self._owner_a_input.value(),
            'N': self._owner_n_input.value()
        }
        
        # Fragebogen-Profil in Scores speichern
        self._current_ocean_scores.owner_profile = owner_dict
        
        # Radardiagramm neu laden (refresh)
        self._show_ocean_plot()
        
        # Bestätigung
        self.statusBar().showMessage("Fragebogen-Profil übernommen und Diagramm aktualisiert", 3000)
        
        # Button-Status aktualisieren
        self._update_assessment_button_state()
    
    def _load_ideal_profile(self):
        """Lädt KI-generiertes Idealprofil"""
        # Prüfen ob OCEAN-Analyse existiert
        if not hasattr(self, '_current_ocean_scores') or self._current_ocean_scores is None:
            QMessageBox.warning(
                self,
                "Keine Analyse",
                "Bitte erstellen Sie zuerst eine OCEAN-Analyse, bevor Sie ein Idealprofil laden."
            )
            return
        
        # Prüfen ob Stammdaten vorhanden
        if not self._current_session or not self._current_session.dog_data:
            QMessageBox.warning(
                self,
                "Keine Stammdaten",
                "Bitte geben Sie zuerst Stammdaten ein."
            )
            return
        
        # Prüfen ob API konfiguriert ist
        if not settings.is_openai_configured:
            QMessageBox.warning(
                self,
                "API nicht konfiguriert",
                "OpenAI API ist nicht konfiguriert.\n\n"
                "Bitte erstellen Sie eine .env Datei mit Ihrem API-Key.\n"
                "Siehe docs/api_setup.md für eine Anleitung."
            )
            return
        
        # Loading-Dialog erstellen
        from PySide6.QtWidgets import QProgressDialog
        progress = QProgressDialog(
            "Generiere KI-Idealprofil...\nBitte warten Sie einen Moment.",
            "",  # Kein Cancel-Button
            0, 0,  # Indeterminate progress
            self
        )
        progress.setWindowTitle("KI-Analyse läuft")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)  # Sofort anzeigen
        progress.setValue(0)
        
        # Event-Loop verarbeiten
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()
        
        try:
            # AI Service initialisieren
            ai_service = AIProfileService()
            
            # Hundedaten extrahieren
            dog_data = self._current_session.dog_data
            test_count = len(self._current_battery.tests) if self._current_battery else 7
            
            # API-Call durchführen
            ideal_profile = ai_service.get_ideal_profile(
                breed=dog_data.breed,
                age_years=dog_data.age_years,
                age_months=dog_data.age_months,
                gender=dog_data.gender.value,
                intended_use=dog_data.intended_use,
                test_count=test_count
            )
            
            # Profil speichern
            self._current_ocean_scores.ideal_profile = ideal_profile
            
            # Radardiagramm aktualisieren
            self._show_ocean_plot()
            
            # Button-Status aktualisieren
            self._update_assessment_button_state()
            
            # Erfolg-Nachricht
            profile_str = ", ".join([f"{k}={v}" for k, v in ideal_profile.items()])
            self.statusBar().showMessage(
                f"KI-Idealprofil geladen: {profile_str}",
                5000
            )
            
            QMessageBox.information(
                self,
                "Idealprofil geladen",
                f"Das KI-generierte Idealprofil wurde erfolgreich geladen:\n\n"
                f"Offenheit (O): {ideal_profile['O']}\n"
                f"Gewissenhaftigkeit (C): {ideal_profile['C']}\n"
                f"Extraversion (E): {ideal_profile['E']}\n"
                f"Verträglichkeit (A): {ideal_profile['A']}\n"
                f"Neurotizismus (N): {ideal_profile['N']}\n\n"
                f"Das grün-gestrichelte Profil ist nun im Radardiagramm sichtbar."
            )
            
        except AIProfileConfigError as e:
            QMessageBox.critical(
                self,
                "Konfigurationsfehler",
                f"Fehler bei der API-Konfiguration:\n\n{str(e)}\n\n"
                f"Bitte überprüfen Sie Ihre .env Datei."
            )
        except AIProfileConnectionError as e:
            QMessageBox.critical(
                self,
                "Verbindungsfehler",
                f"Fehler beim Verbinden zur OpenAI API:\n\n{str(e)}\n\n"
                f"Bitte überprüfen Sie Ihre Internetverbindung und API-Key."
            )
        except AIProfileError as e:
            QMessageBox.critical(
                self,
                "KI-Fehler",
                f"Fehler bei der KI-Analyse:\n\n{str(e)}"
            )
        except Exception as e:
            import traceback
            QMessageBox.critical(
                self,
                "Unerwarteter Fehler",
                f"Ein unerwarteter Fehler ist aufgetreten:\n\n{str(e)}\n\n{traceback.format_exc()}"
            )
        finally:
            progress.close()
    
    def _show_assessment(self):
        """Zeigt KI-Bewertung basierend auf allen 3 Profilen"""
        # Prüfen ob alle Profile vorhanden
        if not hasattr(self, '_current_ocean_scores') or self._current_ocean_scores is None:
            QMessageBox.warning(
                self,
                "Keine Analyse",
                "Bitte erstellen Sie zuerst eine OCEAN-Analyse."
            )
            return
        
        scores = self._current_ocean_scores
        if not scores.ideal_profile or not scores.owner_profile:
            QMessageBox.warning(
                self,
                "Profile fehlen",
                "Bitte laden Sie zuerst ein KI-Idealprofil und übernehmen Sie das Fragebogen-Profil."
            )
            return
        
        # Prüfen ob Stammdaten vorhanden
        if not self._current_session or not self._current_session.dog_data:
            QMessageBox.warning(
                self,
                "Keine Stammdaten",
                "Stammdaten fehlen."
            )
            return
        
        # Loading-Dialog
        from PySide6.QtWidgets import QProgressDialog
        progress = QProgressDialog(
            "Erstelle KI-Bewertung...\nBitte warten Sie einen Moment.",
            "",
            0, 0,
            self
        )
        progress.setWindowTitle("KI-Analyse läuft")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()
        
        try:
            # AI Service initialisieren
            ai_service = AIProfileService()
            
            # Ist-Profil extrahieren
            ist_profile = {
                'O': scores.openness,
                'C': scores.conscientiousness,
                'E': scores.extraversion,
                'A': scores.agreeableness,
                'N': scores.neuroticism
            }
            
            # API-Call durchführen
            test_count = len(self._current_battery.tests) if self._current_battery else 7
            assessment_text = ai_service.get_assessment(
                dog_data=self._current_session.dog_data,
                ist_profile=ist_profile,
                ideal_profile=scores.ideal_profile,
                owner_profile=scores.owner_profile,
                test_count=test_count
            )
            
            # Dialog mit Bewertung anzeigen
            self._show_assessment_dialog(assessment_text)
            
            self.statusBar().showMessage("KI-Bewertung angezeigt", 3000)
            
        except AIProfileConfigError as e:
            QMessageBox.critical(
                self,
                "Konfigurationsfehler",
                f"Fehler bei der API-Konfiguration:\n\n{str(e)}"
            )
        except AIProfileConnectionError as e:
            QMessageBox.critical(
                self,
                "Verbindungsfehler",
                f"Fehler beim Verbinden zur OpenAI API:\n\n{str(e)}"
            )
        except AIProfileError as e:
            QMessageBox.critical(
                self,
                "KI-Fehler",
                f"Fehler bei der KI-Analyse:\n\n{str(e)}"
            )
        except Exception as e:
            import traceback
            QMessageBox.critical(
                self,
                "Unerwarteter Fehler",
                f"Ein unerwarteter Fehler ist aufgetreten:\n\n{str(e)}\n\n{traceback.format_exc()}"
            )
        finally:
            progress.close()
    
    def _show_assessment_dialog(self, assessment_text: str):
        """Zeigt Bewertungstext in einem Dialog"""
        from PySide6.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("KI-Bewertung")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Text-Widget
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(assessment_text)
        text_edit.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                line-height: 1.5;
                padding: 10px;
            }
        """)
        layout.addWidget(text_edit)
        
        # Schließen-Button
        close_btn = QPushButton("Schließen")
        close_btn.setMinimumHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def _update_assessment_button_state(self):
        """Aktualisiert Enable/Disable-Status des Bewertungs-Buttons"""
        if not hasattr(self, '_show_assessment_btn'):
            return
        
        # Button nur aktivieren wenn alle 3 Profile vorhanden
        has_all_profiles = (
            hasattr(self, '_current_ocean_scores') and
            self._current_ocean_scores is not None and
            self._current_ocean_scores.ideal_profile is not None and
            self._current_ocean_scores.owner_profile is not None and
            settings.is_openai_configured
        )
        
        self._show_assessment_btn.setEnabled(has_all_profiles)
        
        if has_all_profiles:
            self._show_assessment_btn.setToolTip(
                "Erstellt eine KI-basierte Bewertung anhand aller 3 Profile"
            )
        elif not settings.is_openai_configured:
            self._show_assessment_btn.setToolTip(
                "OpenAI API nicht konfiguriert. Bitte .env Datei erstellen."
            )
        else:
            self._show_assessment_btn.setToolTip(
                "Bitte laden Sie zuerst ein Idealprofil und übernehmen Sie das Fragebogen-Profil."
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
