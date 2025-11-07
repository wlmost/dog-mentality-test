"""
Dialog zur Anzeige detaillierter Test-Informationen
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Qt

from src.test_battery import Test


class TestDetailDialog(QDialog):
    """Dialog zeigt Setting, Durchführung und Rolle der Figurant:in"""
    
    def __init__(self, test: Test, parent=None):
        super().__init__(parent)
        self._test = test
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt das UI-Layout"""
        self.setWindowTitle(f"Test {self._test.number}: {self._test.name}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titel
        title = QLabel(f"Test {self._test.number}: {self._test.name}")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # OCEAN-Dimension
        ocean_label = QLabel(f"OCEAN-Dimension: {self._test.ocean_dimension.value}")
        ocean_label.setStyleSheet("""
            font-size: 12px;
            color: #3498db;
            font-weight: bold;
        """)
        layout.addWidget(ocean_label)
        
        # Setting & Durchführung
        setting_group = self._create_text_group(
            "Setting & Durchführung",
            self._test.setting
        )
        layout.addWidget(setting_group)
        
        # Rolle der Figurant:in
        role_group = self._create_text_group(
            "Rolle der Figurant:in",
            self._test.role_figurant
        )
        layout.addWidget(role_group)
        
        # Zusatzinformationen (optional)
        details_group = self._create_details_section()
        layout.addWidget(details_group)
        
        # Schließen-Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Schließen")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _create_text_group(self, title: str, content: str) -> QGroupBox:
        """Erstellt eine GroupBox mit Textanzeige"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(content)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 10px;
                font-size: 11px;
            }
        """)
        layout.addWidget(text_edit)
        
        return group
    
    def _create_details_section(self) -> QGroupBox:
        """Erstellt Zusatzinformationen-Bereich"""
        group = QGroupBox("Weitere Details")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Material, Dauer, Beobachtungskriterien
        details_text = f"""<b>Material:</b> {self._test.materials}<br><br>
<b>Dauer:</b> {self._test.duration}<br><br>
<b>Beobachtungskriterien:</b> {self._test.observation_criteria}<br><br>
<b>Bewertungsskala:</b> {self._test.rating_scale}"""
        
        details_label = QLabel(details_text)
        details_label.setWordWrap(True)
        details_label.setTextFormat(Qt.TextFormat.RichText)
        details_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 10px;
                font-size: 11px;
            }
        """)
        layout.addWidget(details_label)
        
        return group
