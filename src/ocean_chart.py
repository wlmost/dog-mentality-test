"""
OCEAN Radar Chart: Visualisierung der OCEAN-Dimensionen

Erstellt ein Radardiagramm (Polar Chart) mit den 5 OCEAN-Dimensionen
unter Verwendung von PySide6.QtCharts.

Funktionsweise:
1. QPolarChart mit 5 Achsen (eine pro OCEAN-Dimension)
2. QAreaSeries für gefüllten Radar-Plot
3. QValueAxis für jeden Dimension-Wert
4. Automatische Skalierung basierend auf Max/Min-Werten

Design-Entscheidungen:
- Verwendung von Summenwerten (nicht Durchschnitt)
- Dynamische Achsen-Skalierung
- Blaue Farbe (#3498db) mit Transparenz
- Interaktive Labels mit Hover-Effekt
"""
from PySide6.QtCharts import QChart, QChartView, QPolarChart, QValueAxis, QLineSeries, QAreaSeries
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QWidget
from src.ocean_analyzer import OceanScores


class OceanRadarChart(QWidget):
    """
    Widget zur Darstellung eines OCEAN-Radardiagramms
    
    Zeigt die 5 OCEAN-Dimensionen in einem Polar-Chart:
    - Openness (O)
    - Conscientiousness (C)
    - Extraversion (E)
    - Agreeableness (A)
    - Neuroticism (N)
    
    Beispiel:
        scores = OceanScores(
            openness=3, conscientiousness=-1, extraversion=2,
            agreeableness=0, neuroticism=-2
        )
        
        chart_widget = OceanRadarChart(scores)
        chart_widget.show()
    """
    
    def __init__(self, scores: OceanScores, parent=None):
        """
        Initialisiert das Radar-Chart
        
        Args:
            scores: OceanScores mit berechneten Dimensionswerten
            parent: Parent-Widget (optional)
        """
        super().__init__(parent)
        self.scores = scores
        
        # Chart erstellen
        self._chart = self._create_chart()
        
        # ChartView erstellen
        self._chart_view = QChartView(self._chart, self)
        self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Layout (ChartView füllt gesamtes Widget)
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._chart_view)
    
    def _create_chart(self) -> QChart:
        """
        Erstellt das Polar-Chart mit OCEAN-Daten
        
        Returns:
            Konfiguriertes QChart-Objekt
        """
        chart = QPolarChart()
        chart.setTitle("OCEAN-Persönlichkeitsprofil")
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        
        # Daten als Liste (O, C, E, A, N)
        dimension_values = [
            self.scores.openness,
            self.scores.conscientiousness,
            self.scores.extraversion,
            self.scores.agreeableness,
            self.scores.neuroticism,
        ]
        
        dimension_labels = [
            "Openness",
            "Conscientiousness",
            "Extraversion",
            "Agreeableness",
            "Neuroticism",
        ]
        
        # Achsen-Range dynamisch berechnen
        min_val = min(dimension_values)
        max_val = max(dimension_values)
        
        # Etwas Padding hinzufügen
        axis_min = min_val - 1 if min_val < 0 else 0
        axis_max = max_val + 1
        
        # Winkelachse (Kategorien)
        angular_axis = QValueAxis()
        angular_axis.setTickCount(len(dimension_labels) + 1)
        angular_axis.setRange(0, len(dimension_labels))
        angular_axis.setLabelsVisible(True)
        
        # Radiale Achse (Werte)
        radial_axis = QValueAxis()
        radial_axis.setRange(axis_min, axis_max)
        radial_axis.setTickCount(5)
        radial_axis.setLabelsVisible(True)
        
        # LineSeries für Radar erstellen
        series = QLineSeries()
        series.setName("OCEAN-Werte")
        
        # Punkte hinzufügen (Winkel, Radius)
        for i, value in enumerate(dimension_values):
            series.append(QPointF(i, value))
        
        # Ersten Punkt nochmal anhängen für geschlossene Form
        series.append(QPointF(0, dimension_values[0]))
        
        # AreaSeries für gefüllten Bereich
        area_series = QAreaSeries(series)
        area_series.setName("OCEAN-Profil")
        
        # Farbe: Blau mit Transparenz
        color = QColor("#3498db")
        color.setAlpha(100)
        
        pen = QPen(QColor("#3498db"))
        pen.setWidth(2)
        
        area_series.setPen(pen)
        area_series.setBrush(QBrush(color))
        area_series.setOpacity(0.7)
        
        # Series zum Chart hinzufügen
        chart.addSeries(area_series)
        
        # Achsen zuweisen
        chart.addAxis(angular_axis, QPolarChart.PolarOrientation.PolarOrientationAngular)
        chart.addAxis(radial_axis, QPolarChart.PolarOrientation.PolarOrientationRadial)
        
        area_series.attachAxis(angular_axis)
        area_series.attachAxis(radial_axis)
        
        # Legende
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        return chart
    
    def update_scores(self, scores: OceanScores):
        """
        Aktualisiert das Chart mit neuen OCEAN-Scores
        
        Args:
            scores: Neue OceanScores
        """
        self.scores = scores
        
        # Chart neu erstellen
        new_chart = self._create_chart()
        self._chart_view.setChart(new_chart)
        self._chart = new_chart
