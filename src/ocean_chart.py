"""
OCEAN Radar Chart: Visualisierung der OCEAN-Dimensionen

Erstellt ein interaktives Radardiagramm mit den 5 OCEAN-Dimensionen
unter Verwendung von Plotly.

HINWEIS: QPolarChart von PySide6.QtCharts führt zu Crashes in Version 6.10.0,
daher verwenden wir Plotly für stabile, interaktive und ansprechende Visualisierung.

Funktionsweise:
1. Plotly Scatterpolar für Radar-Chart
2. HTML-Rendering in QWebEngineView
3. Interaktive Features: Zoom, Pan, Hover
4. Automatische Skalierung

Design-Entscheidungen:
- Verwendung von Summenwerten (nicht Durchschnitt)
- Dynamische Achsen-Skalierung
- Blaue Farbe (#3498db) mit Transparenz
- Geschlossene Radar-Form
"""
import plotly.graph_objects as go
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout
from src.ocean_analyzer import OceanScores


class OceanRadarChart(QWidget):
    """
    Widget zur Darstellung eines OCEAN-Radardiagramms mit Plotly
    
    Zeigt die 5 OCEAN-Dimensionen als interaktives Radar-Chart:
    - Openness (O)
    - Conscientiousness (C)
    - Extraversion (E)
    - Agreeableness (A)
    - Neuroticism (N)
    
    Verwendet Plotly für moderne, interaktive Visualisierung.
    
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
        
        # WebEngineView für Plotly-HTML erstellen
        self._web_view = QWebEngineView(self)
        
        # Für Kompatibilität mit Tests: _chart als Referenz
        self._chart = None  # Plotly verwendet kein QChart-Objekt
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._web_view)
        
        # Chart erstellen und anzeigen
        self._update_chart()
    
    def _update_chart(self):
        """
        Erstellt und aktualisiert das Plotly Radar-Chart
        """
        # Daten für Radar-Chart
        dimension_values = [
            self.scores.openness,
            self.scores.conscientiousness,
            self.scores.extraversion,
            self.scores.agreeableness,
            self.scores.neuroticism,
        ]
        
        dimension_labels = [
            "Offenheit (O)",
            "Gewissenhaftigkeit (C)",
            "Extraversion (E)",
            "Verträglichkeit (A)",
            "Neurotizismus (N)",
        ]
        
        # Plotly Scatterpolar (Radar) Chart erstellen
        fig = go.Figure()
        
        # Trace 1: Ist-Profil (gemessene Werte) - Blau, durchgezogen
        fig.add_trace(go.Scatterpolar(
            r=dimension_values,
            theta=dimension_labels,
            fill='toself',
            fillcolor='rgba(52, 152, 219, 0.3)',  # Blau mit Transparenz
            line=dict(color='rgb(52, 152, 219)', width=3),  # Dickere Linie
            name='Ist-Profil',
            marker=dict(size=8, color='rgb(52, 152, 219)'),  # Größere Punkte
            hovertemplate='<b>%{theta}</b><br>Ist-Wert: %{r}<extra></extra>',
        ))
        
        # Trace 2: Fragebogen-Profil (falls vorhanden) - Rot, gepunktet
        if self.scores.owner_profile:
            owner_values = [
                self.scores.owner_profile.get('O', 0),
                self.scores.owner_profile.get('C', 0),
                self.scores.owner_profile.get('E', 0),
                self.scores.owner_profile.get('A', 0),
                self.scores.owner_profile.get('N', 0),
            ]
            fig.add_trace(go.Scatterpolar(
                r=owner_values,
                theta=dimension_labels,
                fill='toself',
                fillcolor='rgba(231, 76, 60, 0.15)',  # Rot mit Transparenz
                line=dict(color='rgb(231, 76, 60)', width=2, dash='dot'),  # Gepunktet
                name='Fragebogen-Profil',
                marker=dict(size=6, color='rgb(231, 76, 60)'),
                hovertemplate='<b>%{theta}</b><br>Fragebogen: %{r}<extra></extra>',
            ))
        
        # Trace 3: Ideal-Profil (falls vorhanden) - Grün, gestrichelt
        if self.scores.ideal_profile:
            ideal_values = [
                self.scores.ideal_profile.get('O', 0),
                self.scores.ideal_profile.get('C', 0),
                self.scores.ideal_profile.get('E', 0),
                self.scores.ideal_profile.get('A', 0),
                self.scores.ideal_profile.get('N', 0),
            ]
            fig.add_trace(go.Scatterpolar(
                r=ideal_values,
                theta=dimension_labels,
                fill='toself',
                fillcolor='rgba(46, 204, 113, 0.15)',  # Grün mit Transparenz
                line=dict(color='rgb(46, 204, 113)', width=2, dash='dash'),  # Gestrichelt
                name='Ideal-Profil (KI)',
                marker=dict(size=6, color='rgb(46, 204, 113)'),
                hovertemplate='<b>%{theta}</b><br>Ideal-Wert: %{r}<extra></extra>',
            ))
        
        # Bestimme Achsen-Range basierend auf Anzahl Tests pro Dimension
        # Jeder Test kann -2 bis +2 Punkte geben
        # Daher: Range = test_count * 2
        test_counts = [
            self.scores.openness_count,
            self.scores.conscientiousness_count,
            self.scores.extraversion_count,
            self.scores.agreeableness_count,
            self.scores.neuroticism_count,
        ]
        max_test_count = max(test_counts) if test_counts else 1
        axis_range = max_test_count * 2  # z.B. 7 Tests -> ±14
        
        # Layout konfigurieren - GRÖßERES Chart
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    showticklabels=True,
                    showline=True,
                    gridcolor='lightgray',
                    tickfont=dict(size=14),
                    range=[-axis_range, axis_range],  # Symmetrisch um 0, basierend auf Testanzahl
                ),
                angularaxis=dict(
                    tickfont=dict(size=16, color='black'),
                )
            ),
            showlegend=True,
            legend=dict(
                font=dict(size=14),
                orientation='h',
                yanchor='bottom',
                y=-0.15,
                xanchor='center',
                x=0.5
            ),
            title=dict(
                text="OCEAN-Persönlichkeitsprofil",
                font=dict(size=24, color='black'),
                x=0.5,
                xanchor='center',
                y=0.95
            ),
            font=dict(size=14),
            paper_bgcolor='white',
            plot_bgcolor='white',
            # Größere Margins für bessere Lesbarkeit
            margin=dict(l=120, r=120, t=120, b=100),
            # Feste Höhe für konsistente Darstellung
            height=700,
            # Responsive auf verschiedene Bildschirmgrößen
            autosize=True,
        )
        
        # HTML generieren mit deutscher Konfiguration
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'ocean_profil',
                'height': 700,
                'width': 700,
                'scale': 2
            },
            'locale': 'de'  # Deutsche Sprache für Toolbar
        }
        
        # HTML mit deutscher Lokalisierung
        html = fig.to_html(
            include_plotlyjs='cdn', 
            config=config,
            include_mathjax=False
        )
        self._web_view.setHtml(html)
    
    def update_scores(self, scores: OceanScores):
        """
        Aktualisiert das Chart mit neuen OCEAN-Scores
        
        Args:
            scores: Neue OceanScores
        """
        self.scores = scores
        self._update_chart()
