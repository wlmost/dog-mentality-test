"""
Excel-Export für Test-Sessions

Exportiert Stammdaten und Testergebnisse in eine strukturierte Excel-Datei
"""
from pathlib import Path
from typing import Optional
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

from src.test_session import TestSession
from src.test_battery import TestBattery


class ExcelExportError(Exception):
    """Fehler beim Excel-Export"""
    pass


class ExcelExporter:
    """
    Exportiert Test-Sessions in Excel-Format
    
    Features:
    - Zwei Sheets: Stammdaten und Testergebnisse
    - Formatierung: Header fett, gefärbt
    - Auto-Spaltenbreite
    """
    
    def __init__(self, battery: Optional[TestBattery] = None):
        """
        Initialisiert den Exporter
        
        Args:
            battery: Testbatterie für zusätzliche Test-Informationen (optional)
        """
        self._battery = battery
    
    def export_to_excel(self, session: TestSession, filepath: str):
        """
        Exportiert Session in Excel-Datei
        
        Args:
            session: Test-Session mit Daten
            filepath: Pfad zur Ausgabedatei (.xlsx)
            
        Raises:
            ExcelExportError: Bei Fehlern während des Exports
        """
        try:
            # Workbook erstellen
            wb = Workbook()
            
            # Sheet 1: Stammdaten
            ws_master = wb.active
            ws_master.title = "Stammdaten"
            self._write_master_data(ws_master, session)
            
            # Sheet 2: Testergebnisse
            ws_results = wb.create_sheet("Testergebnisse")
            self._write_test_results(ws_results, session)
            
            # Speichern
            wb.save(filepath)
            
        except PermissionError as e:
            raise ExcelExportError(
                f"Datei ist möglicherweise geöffnet oder schreibgeschützt: {filepath}"
            ) from e
        except Exception as e:
            raise ExcelExportError(
                f"Fehler beim Excel-Export: {str(e)}"
            ) from e
    
    def _write_master_data(self, ws, session: TestSession):
        """Schreibt Stammdaten in Worksheet"""
        # Header-Style
        header_font = Font(bold=True, size=12, color="FFFFFF")
        header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
        
        # Titel
        ws["A1"] = "Stammdaten"
        ws["A1"].font = Font(bold=True, size=14)
        
        # Überschriften
        headers = ["Feld", "Wert"]
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
        
        # Datum formatieren (session.date ist ISO-String)
        try:
            date_obj = datetime.fromisoformat(session.date)
            date_str = date_obj.strftime("%d.%m.%Y %H:%M")
        except (ValueError, AttributeError):
            date_str = session.date
        
        # Daten
        data = [
            ("Datum", date_str),
            ("Name des Halters", session.dog_data.owner_name),
            ("Name des Hundes", session.dog_data.dog_name),
            ("Alter", session.dog_data.age_display()),
            ("Geschlecht", session.dog_data.gender.value),
            ("Kastriert", "Ja" if session.dog_data.neutered else "Nein"),
            ("Testbatterie", session.battery_name),
        ]
        
        for row, (field, value) in enumerate(data, start=4):
            ws.cell(row=row, column=1, value=field)
            ws.cell(row=row, column=2, value=value)
        
        # Session-Notizen
        if session.session_notes:
            ws.cell(row=len(data) + 5, column=1, value="Session-Notizen")
            ws.cell(row=len(data) + 5, column=1).font = Font(bold=True)
            ws.cell(row=len(data) + 6, column=1, value=session.session_notes)
            ws.merge_cells(f"A{len(data) + 6}:B{len(data) + 6}")
        
        # Spaltenbreiten anpassen
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 40
    
    def _write_test_results(self, ws, session: TestSession):
        """Schreibt Testergebnisse in Worksheet"""
        # Header-Style
        header_font = Font(bold=True, size=12, color="FFFFFF")
        header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
        
        # Titel
        ws["A1"] = "Testergebnisse"
        ws["A1"].font = Font(bold=True, size=14)
        
        # Überschriften
        headers = ["Nr.", "Testname", "OCEAN-Dimension", "Score", "Notizen"]
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
        
        # Daten aus Session
        row = 4
        for test_number, result in sorted(session.results.items()):
            ws.cell(row=row, column=1, value=test_number)
            
            # Testname und OCEAN-Dimension aus Battery (falls vorhanden)
            if self._battery:
                test = self._battery.get_test_by_number(test_number)
                if test:
                    ws.cell(row=row, column=2, value=test.name)
                    ws.cell(row=row, column=3, value=test.ocean_dimension.value)
                else:
                    ws.cell(row=row, column=2, value="—")
                    ws.cell(row=row, column=3, value="—")
            else:
                ws.cell(row=row, column=2, value="—")
                ws.cell(row=row, column=3, value="—")
            
            ws.cell(row=row, column=4, value=result.score)
            ws.cell(row=row, column=5, value=result.notes or "")
            
            row += 1
        
        # Spaltenbreiten anpassen
        ws.column_dimensions["A"].width = 8
        ws.column_dimensions["B"].width = 40
        ws.column_dimensions["C"].width = 20
        ws.column_dimensions["D"].width = 10
        ws.column_dimensions["E"].width = 50
        
        # Score-Spalte zentrieren
        for row_idx in range(4, row):
            ws.cell(row=row_idx, column=4).alignment = Alignment(horizontal="center")
