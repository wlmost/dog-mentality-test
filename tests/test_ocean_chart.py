"""
Tests für OCEAN Radar Chart

Testet die Visualisierung der OCEAN-Dimensionen als Radardiagramm
"""
import pytest
from PySide6.QtCharts import QChart, QPolarChart, QAreaSeries
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
        assert chart_widget._chart is not None
        assert chart_widget._chart_view is not None
    
    def test_chart_is_polar_chart(self, qtbot, sample_scores):
        """Test: Chart ist ein QPolarChart"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        assert isinstance(chart_widget._chart, QPolarChart)
    
    def test_chart_has_title(self, qtbot, sample_scores):
        """Test: Chart hat Titel"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        assert "OCEAN" in chart_widget._chart.title()


class TestOceanRadarChartData:
    """Tests für die Daten im Chart"""
    
    def test_chart_has_series(self, qtbot, sample_scores):
        """Test: Chart enthält Daten-Series"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        series_list = chart_widget._chart.series()
        assert len(series_list) > 0
    
    def test_chart_has_area_series(self, qtbot, sample_scores):
        """Test: Chart verwendet AreaSeries für gefüllten Radar"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        series_list = chart_widget._chart.series()
        area_series = [s for s in series_list if isinstance(s, QAreaSeries)]
        assert len(area_series) > 0
    
    def test_chart_has_legend(self, qtbot, sample_scores):
        """Test: Legende ist sichtbar"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        assert chart_widget._chart.legend().isVisible()


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
        """Test: Update erstellt neues Chart"""
        chart_widget = OceanRadarChart(sample_scores)
        qtbot.addWidget(chart_widget)
        
        old_chart = chart_widget._chart
        
        new_scores = OceanScores(openness=5, conscientiousness=2, extraversion=-1,
                                 agreeableness=3, neuroticism=0)
        chart_widget.update_scores(new_scores)
        
        # Neues Chart-Objekt sollte erstellt worden sein
        assert chart_widget._chart is not old_chart


class TestOceanRadarChartEdgeCases:
    """Tests für Edge-Cases"""
    
    def test_all_zero_scores(self, qtbot):
        """Test: Alle Scores = 0"""
        scores = OceanScores()
        chart_widget = OceanRadarChart(scores)
        qtbot.addWidget(chart_widget)
        
        assert chart_widget._chart is not None
    
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
        
        assert chart_widget._chart is not None
    
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
        
        assert chart_widget._chart is not None
    
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
        
        assert chart_widget._chart is not None
