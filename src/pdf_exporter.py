"""
PDF-Export für Test-Sessions

Erstellt professionelle PDF-Reports mit Stammdaten und Testergebnissen
"""
from pathlib import Path
from typing import Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from src.test_session import TestSession
from src.test_battery import TestBattery


class PdfExportError(Exception):
    """Fehler beim PDF-Export"""
    pass


class PdfExporter:
    """
    Exportiert Test-Sessions als PDF-Report
    
    Features:
    - Professionelles Layout mit Titel und Datum
    - Stammdaten-Tabelle
    - Testergebnisse-Tabelle mit Scores
    - Session-Notizen
    """
    
    def __init__(self, battery: Optional[TestBattery] = None):
        """
        Initialisiert den Exporter
        
        Args:
            battery: Testbatterie für zusätzliche Test-Informationen (optional)
        """
        self._battery = battery
    
    def export_to_pdf(self, session: TestSession, filepath: str):
        """
        Exportiert Session als PDF-Datei
        
        Args:
            session: Test-Session mit Daten
            filepath: Pfad zur Ausgabedatei (.pdf)
            
        Raises:
            PdfExportError: Bei Fehlern während des Exports
        """
        try:
            # PDF-Dokument erstellen
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Story (Inhalt) aufbauen
            story = []
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Titel
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            story.append(Paragraph("Tierpsychologischer Test-Report", title_style))
            story.append(Spacer(1, 0.5*cm))
            
            # Stammdaten
            story.extend(self._create_master_data_section(session, styles))
            story.append(Spacer(1, 1*cm))
            
            # Testergebnisse
            story.extend(self._create_results_section(session, styles))
            
            # Session-Notizen
            if session.session_notes:
                story.append(Spacer(1, 1*cm))
                story.extend(self._create_notes_section(session, styles))
            
            # PDF generieren
            doc.build(story)
            
        except PermissionError as e:
            raise PdfExportError(
                f"Datei ist möglicherweise geöffnet oder schreibgeschützt: {filepath}"
            ) from e
        except Exception as e:
            raise PdfExportError(
                f"Fehler beim PDF-Export: {str(e)}"
            ) from e
    
    def _create_master_data_section(self, session: TestSession, styles):
        """Erstellt Stammdaten-Sektion"""
        elements = []
        
        # Überschrift
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=15
        )
        elements.append(Paragraph("Stammdaten", heading_style))
        
        # Datum formatieren
        try:
            date_obj = datetime.fromisoformat(session.date)
            date_str = date_obj.strftime("%d.%m.%Y %H:%M Uhr")
        except (ValueError, AttributeError):
            date_str = session.date
        
        # Tabelle mit Stammdaten
        data = [
            ['Datum:', date_str],
            ['Name des Halters:', session.dog_data.owner_name],
            ['Name des Hundes:', session.dog_data.dog_name],
            ['Alter:', session.dog_data.age_display()],
            ['Geschlecht:', session.dog_data.gender.value],
            ['Kastriert:', 'Ja' if session.dog_data.neutered else 'Nein'],
            ['Testbatterie:', session.battery_name],
        ]
        
        table = Table(data, colWidths=[5*cm, 10*cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_results_section(self, session: TestSession, styles):
        """Erstellt Testergebnisse-Sektion"""
        elements = []
        
        # Überschrift
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=15
        )
        elements.append(Paragraph("Testergebnisse", heading_style))
        
        # Tabellen-Header
        data = [['Nr.', 'Testname', 'OCEAN', 'Score', 'Notizen']]
        
        # Testergebnisse
        for test_number, result in sorted(session.results.items()):
            test_name = "—"
            ocean_dim = "—"
            
            # Testname und OCEAN-Dimension aus Battery (falls vorhanden)
            if self._battery:
                test = self._battery.get_test_by_number(test_number)
                if test:
                    test_name = test.name
                    ocean_dim = test.ocean_dimension.value
            
            data.append([
                str(test_number),
                test_name,
                ocean_dim,
                str(result.score),
                result.notes or ""
            ])
        
        # Tabelle erstellen
        table = Table(data, colWidths=[1.5*cm, 5*cm, 3*cm, 2*cm, 5*cm])
        table.setStyle(TableStyle([
            # Header-Style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data-Style
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Nr. zentriert
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Score zentriert
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_notes_section(self, session: TestSession, styles):
        """Erstellt Session-Notizen-Sektion"""
        elements = []
        
        # Überschrift
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=15
        )
        elements.append(Paragraph("Session-Notizen", heading_style))
        
        # Notizen als Paragraph
        notes_style = ParagraphStyle(
            'Notes',
            parent=styles['BodyText'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=10
        )
        elements.append(Paragraph(session.session_notes, notes_style))
        
        return elements
