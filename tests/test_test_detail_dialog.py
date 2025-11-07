"""
Tests für TestDetailDialog
"""
import pytest
from PySide6.QtWidgets import QPushButton, QTextEdit, QLabel
from PySide6.QtCore import Qt

from src.test_detail_dialog import TestDetailDialog
from src.test_battery import Test, OceanDimension


@pytest.fixture
def sample_test():
    """Erstellt einen Test für die Tests"""
    return Test(
        number=1,
        ocean_dimension=OceanDimension.OPENNESS,
        name="Testbeispiel",
        setting="Setting-Beschreibung: Hier wird erklärt, wie der Test durchgeführt wird.",
        materials="Leine, Ball, Dummy",
        duration="5-10 Minuten",
        role_figurant="Figurant steht ruhig in 5m Entfernung und beobachtet den Hund.",
        observation_criteria="Neugierverhalten, Annäherung, Körpersprache",
        rating_scale="-2 = sehr ängstlich, +2 = sehr neugierig"
    )


def test_dialog_creation(qtbot, sample_test):
    """Test: Dialog kann erstellt werden"""
    dialog = TestDetailDialog(sample_test)
    qtbot.addWidget(dialog)
    
    assert dialog.windowTitle() == "Test 1: Testbeispiel"


def test_dialog_displays_test_info(qtbot, sample_test):
    """Test: Dialog zeigt Test-Informationen an"""
    dialog = TestDetailDialog(sample_test)
    qtbot.addWidget(dialog)
    
    # Titel-Label finden
    title_label = dialog.findChild(QLabel)
    assert title_label is not None
    assert "Test 1: Testbeispiel" in title_label.text()


def test_dialog_displays_setting(qtbot, sample_test):
    """Test: Dialog zeigt Setting & Durchführung"""
    dialog = TestDetailDialog(sample_test)
    qtbot.addWidget(dialog)
    
    # Alle TextEdits finden
    text_edits = dialog.findChildren(QTextEdit)
    setting_texts = [te.toPlainText() for te in text_edits]
    
    assert any("Setting-Beschreibung" in text for text in setting_texts)


def test_dialog_displays_role_figurant(qtbot, sample_test):
    """Test: Dialog zeigt Rolle der Figurant:in"""
    dialog = TestDetailDialog(sample_test)
    qtbot.addWidget(dialog)
    
    # Alle TextEdits finden
    text_edits = dialog.findChildren(QTextEdit)
    role_texts = [te.toPlainText() for te in text_edits]
    
    assert any("Figurant steht ruhig" in text for text in role_texts)


def test_dialog_displays_additional_details(qtbot, sample_test):
    """Test: Dialog zeigt zusätzliche Details (Material, Dauer, etc.)"""
    dialog = TestDetailDialog(sample_test)
    qtbot.addWidget(dialog)
    
    # Alle Labels finden und Text sammeln
    labels = dialog.findChildren(QLabel)
    all_text = " ".join([label.text() for label in labels])
    
    assert "Leine, Ball, Dummy" in all_text
    assert "5-10 Minuten" in all_text
    assert "Neugierverhalten" in all_text


def test_dialog_has_close_button(qtbot, sample_test):
    """Test: Dialog hat Schließen-Button"""
    dialog = TestDetailDialog(sample_test)
    qtbot.addWidget(dialog)
    
    # Schließen-Button finden
    buttons = dialog.findChildren(QPushButton)
    close_buttons = [btn for btn in buttons if "Schließen" in btn.text()]
    
    assert len(close_buttons) == 1


def test_dialog_close_button_works(qtbot, sample_test):
    """Test: Schließen-Button schließt den Dialog"""
    dialog = TestDetailDialog(sample_test)
    qtbot.addWidget(dialog)
    
    # Schließen-Button finden und klicken
    buttons = dialog.findChildren(QPushButton)
    close_button = next(btn for btn in buttons if "Schließen" in btn.text())
    
    qtbot.mouseClick(close_button, Qt.MouseButton.LeftButton)
    
    # Dialog sollte akzeptiert sein
    assert dialog.result() == dialog.DialogCode.Accepted


def test_dialog_minimum_size(qtbot, sample_test):
    """Test: Dialog hat Mindestgröße"""
    dialog = TestDetailDialog(sample_test)
    qtbot.addWidget(dialog)
    
    assert dialog.minimumWidth() >= 600
    assert dialog.minimumHeight() >= 500


def test_dialog_ocean_dimension_display(qtbot, sample_test):
    """Test: Dialog zeigt OCEAN-Dimension an"""
    dialog = TestDetailDialog(sample_test)
    qtbot.addWidget(dialog)
    
    # OCEAN-Label finden
    labels = dialog.findChildren(QLabel)
    ocean_labels = [label for label in labels if "OCEAN-Dimension" in label.text()]
    
    assert len(ocean_labels) == 1
    assert "Offenheit" in ocean_labels[0].text()


def test_dialog_text_edits_are_readonly(qtbot, sample_test):
    """Test: TextEdit-Felder sind read-only"""
    dialog = TestDetailDialog(sample_test)
    qtbot.addWidget(dialog)
    
    text_edits = dialog.findChildren(QTextEdit)
    
    # Mindestens 2 TextEdits (Setting und Rolle)
    assert len(text_edits) >= 2
    
    for text_edit in text_edits:
        assert text_edit.isReadOnly()
