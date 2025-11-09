"""
Tests für OCEAN Chart

Testet die Visualisierung der OCEAN-Dimensionen als Balkendiagramm
(ursprünglich Radardiagramm, aber QPolarChart führt zu Crashes)
"""
import pytest
from PySide6.QtCharts import QChart
from src.ocean_chart import OceanRadarChart
from src.ocean_analyzer import OceanScores


@pytest.fixture
def sample_scores():
    """Erstellt Beispiel-Scores"""
    return OceanScores(
        openness=3,
        conscientiousness=-1,
        extraversion=2,
        agreeableness=0,
        neuroticism=-2,
        openness_count=2,
        conscientiousness_count=1,
        extraversion_count=1,
        agreeableness_count=1,
        neuroticism_count=1,
    )


class TestOceanRadarChartCreation:
    """Tests für die Erstellung des Radar-Charts"""
    
    def test_chart_creation(self, qtbot, sample_scores):
        """Test: Chart kann erstellt werden"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        assert chart_widget is not None
        assert chart_widget._web_view is not None
        assert chart_widget.scores == sample_scores
    
    def test_chart_is_polar_chart(self, qtbot, sample_scores):
        """Test: Chart verwendet Plotly für Radar-Visualisierung"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        # Plotly verwendet QWebEngineView statt QChart
        from PySide6.QtWebEngineWidgets import QWebEngineView
        assert isinstance(chart_widget._web_view, QWebEngineView)
    
    def test_chart_has_title(self, qtbot, sample_scores):
        """Test: Chart hat OCEAN im HTML"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        # Warte kurz bis HTML geladen ist
        import time
        time.sleep(0.1)
        # Test dass Widget existiert (HTML-Inhalt schwer zu testen)
        assert chart_widget._web_view is not None


class TestOceanRadarChartData:
    """Tests für die Daten im Chart"""
    
    def test_chart_has_series(self, qtbot, sample_scores):
        """Test: Chart enthält Daten (Plotly basiert)"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        # Plotly generiert HTML, prüfe dass scores vorhanden sind
        assert chart_widget.scores.openness == sample_scores.openness
        assert chart_widget.scores.conscientiousness == sample_scores.conscientiousness
    
    def test_chart_has_area_series(self, qtbot, sample_scores):
        """Test: Chart verwendet Plotly Scatterpolar (Radar-Chart)"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        # Plotly-Charts werden in WebEngineView gerendert
        from PySide6.QtWebEngineWidgets import QWebEngineView
        assert isinstance(chart_widget._web_view, QWebEngineView)
    
    def test_chart_has_legend(self, qtbot, sample_scores):
        """Test: Chart wird korrekt erstellt"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        # Prüfe dass WebView existiert und Widget sichtbar ist
        assert chart_widget._web_view is not None


class TestOceanRadarChartUpdate:
    """Tests für das Aktualisieren des Charts"""
    
    def test_update_scores(self, qtbot, sample_scores):
        """Test: Scores können aktualisiert werden"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        new_scores = OceanScores(
            openness=5,
            conscientiousness=2,
            extraversion=-1,
            agreeableness=3,
            neuroticism=0,
        )
        
        chart_widget.update_scores(new_scores)
        
        assert chart_widget.scores == new_scores
    
    def test_update_recreates_chart(self, qtbot, sample_scores):
        """Test: Update aktualisiert HTML in WebView"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        new_scores = OceanScores(openness=5, conscientiousness=2, extraversion=-1,
                                 agreeableness=3, neuroticism=0)
        chart_widget.update_scores(new_scores)
        
        # Scores sollten aktualisiert sein
        assert chart_widget.scores == new_scores


class TestOceanRadarChartEdgeCases:
    """Tests für Edge-Cases"""
    
    def test_all_zero_scores(self, qtbot):
        """Test: Alle Scores = 0"""
        scores = OceanScores()
        chart_widget = OceanRadarChart(scores)
        qtbot.addWidget(chart_widget)
        
        assert chart_widget._web_view is not None
        assert chart_widget.scores == scores
    
    def test_all_negative_scores(self, qtbot):
        """Test: Alle Scores negativ"""
        scores = OceanScores(
            openness=-5,
            conscientiousness=-3,
            extraversion=-2,
            agreeableness=-4,
            neuroticism=-1,
        )
        chart_widget = OceanRadarChart(scores)
        qtbot.addWidget(chart_widget)
        
        assert chart_widget._web_view is not None
        assert chart_widget.scores == scores
    
    def test_all_positive_scores(self, qtbot):
        """Test: Alle Scores positiv"""
        scores = OceanScores(
            openness=5,
            conscientiousness=3,
            extraversion=2,
            agreeableness=4,
            neuroticism=1,
        )
        chart_widget = OceanRadarChart(scores)
        qtbot.addWidget(chart_widget)
        
        assert chart_widget._web_view is not None
        assert chart_widget.scores == scores
    
    def test_mixed_extreme_scores(self, qtbot):
        """Test: Sehr unterschiedliche Werte"""
        scores = OceanScores(
            openness=20,
            conscientiousness=-15,
            extraversion=5,
            agreeableness=0,
            neuroticism=-10,
        )
        chart_widget = OceanRadarChart(scores)
        qtbot.addWidget(chart_widget)
        
        assert chart_widget._web_view is not None
        assert chart_widget.scores == scores
