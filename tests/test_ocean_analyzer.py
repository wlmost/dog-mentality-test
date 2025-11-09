"""
Tests für OCEAN-Analyzer

Testet die Berechnung der OCEAN-Dimensionswerte aus Testergebnissen
"""
import pytest
from src.ocean_analyzer import OceanAnalyzer, OceanScores
from src.test_session import TestSession, TestResult
from src.test_battery import TestBattery, Test, OceanDimension
from src.models import DogData, Gender


@pytest.fixture
def sample_dog():
    """Erstellt Beispiel-Hunddaten"""
    return DogData(
        owner_name="Test Owner",
        dog_name="Test Dog",
        age_years=3,
        age_months=0,
        gender=Gender.MALE,
        neutered=False
    )


@pytest.fixture
def sample_battery():
    """Erstellt eine Testbatterie mit allen 5 OCEAN-Dimensionen"""
    tests = [
        Test(number=1, ocean_dimension=OceanDimension.OPENNESS, 
             name="Test 1", setting="Indoor", materials="", duration="5min",
             role_figurant="", observation_criteria="", rating_scale=""),
        Test(number=2, ocean_dimension=OceanDimension.OPENNESS,
             name="Test 2", setting="Outdoor", materials="", duration="5min",
             role_figurant="", observation_criteria="", rating_scale=""),
        Test(number=3, ocean_dimension=OceanDimension.CONSCIENTIOUSNESS,
             name="Test 3", setting="Indoor", materials="", duration="5min",
             role_figurant="", observation_criteria="", rating_scale=""),
        Test(number=4, ocean_dimension=OceanDimension.EXTRAVERSION,
             name="Test 4", setting="Outdoor", materials="", duration="5min",
             role_figurant="", observation_criteria="", rating_scale=""),
        Test(number=5, ocean_dimension=OceanDimension.AGREEABLENESS,
             name="Test 5", setting="Indoor", materials="", duration="5min",
             role_figurant="", observation_criteria="", rating_scale=""),
        Test(number=6, ocean_dimension=OceanDimension.NEUROTICISM,
             name="Test 6", setting="Outdoor", materials="", duration="5min",
             role_figurant="", observation_criteria="", rating_scale=""),
    ]
    return TestBattery("OCEAN Test Battery", tests)


@pytest.fixture
def sample_session_with_results(sample_dog, sample_battery):
    """Erstellt Session mit verschiedenen Scores"""
    session = TestSession(dog_data=sample_dog, battery_name="OCEAN Test Battery")
    
    # Openness: +2, +1 → Summe: +3, Count: 2
    session.add_result(TestResult(test_number=1, score=2, notes=""))
    session.add_result(TestResult(test_number=2, score=1, notes=""))
    
    # Conscientiousness: -1 → Summe: -1, Count: 1
    session.add_result(TestResult(test_number=3, score=-1, notes=""))
    
    # Extraversion: +2 → Summe: +2, Count: 1
    session.add_result(TestResult(test_number=4, score=2, notes=""))
    
    # Agreeableness: 0 → Summe: 0, Count: 1
    session.add_result(TestResult(test_number=5, score=0, notes=""))
    
    # Neuroticism: -2 → Summe: -2, Count: 1
    session.add_result(TestResult(test_number=6, score=-2, notes=""))
    
    return session


class TestOceanAnalyzerCreation:
    """Tests für die Erstellung des Analyzers"""
    
    def test_analyzer_creation(self, sample_session_with_results, sample_battery):
        """Test: Analyzer kann erstellt werden"""
        analyzer = OceanAnalyzer(sample_session_with_results, sample_battery)
        assert analyzer is not None
        assert analyzer.session == sample_session_with_results
        assert analyzer.battery == sample_battery
    
    def test_analyzer_without_battery(self, sample_session_with_results):
        """Test: Analyzer funktioniert auch ohne Battery (mit Einschränkungen)"""
        analyzer = OceanAnalyzer(sample_session_with_results, None)
        assert analyzer is not None
        assert analyzer.battery is None


class TestOceanScoresCalculation:
    """Tests für die OCEAN-Score-Berechnung"""
    
    def test_calculate_scores_all_dimensions(self, sample_session_with_results, sample_battery):
        """Test: Scores werden für alle 5 Dimensionen berechnet"""
        analyzer = OceanAnalyzer(sample_session_with_results, sample_battery)
        scores = analyzer.calculate_ocean_scores()
        
        assert isinstance(scores, OceanScores)
        assert scores.openness == 3  # +2 +1
        assert scores.conscientiousness == -1  # -1
        assert scores.extraversion == 2  # +2
        assert scores.agreeableness == 0  # 0
        assert scores.neuroticism == -2  # -2
    
    def test_score_counts(self, sample_session_with_results, sample_battery):
        """Test: Anzahl Tests pro Dimension wird gezählt"""
        analyzer = OceanAnalyzer(sample_session_with_results, sample_battery)
        scores = analyzer.calculate_ocean_scores()
        
        assert scores.openness_count == 2
        assert scores.conscientiousness_count == 1
        assert scores.extraversion_count == 1
        assert scores.agreeableness_count == 1
        assert scores.neuroticism_count == 1
    
    def test_empty_session(self, sample_dog, sample_battery):
        """Test: Leere Session ergibt alle Scores = 0"""
        session = TestSession(dog_data=sample_dog, battery_name="Test")
        analyzer = OceanAnalyzer(session, sample_battery)
        scores = analyzer.calculate_ocean_scores()
        
        assert scores.openness == 0
        assert scores.conscientiousness == 0
        assert scores.extraversion == 0
        assert scores.agreeableness == 0
        assert scores.neuroticism == 0
        
        assert scores.openness_count == 0
        assert scores.conscientiousness_count == 0
    
    def test_single_dimension_only(self, sample_dog):
        """Test: Session mit nur einer Dimension"""
        battery = TestBattery("Single Dim", [
            Test(number=1, ocean_dimension=OceanDimension.OPENNESS,
                 name="Test 1", setting="Indoor", materials="", duration="5min",
                 role_figurant="", observation_criteria="", rating_scale=""),
            Test(number=2, ocean_dimension=OceanDimension.OPENNESS,
                 name="Test 2", setting="Outdoor", materials="", duration="5min",
                 role_figurant="", observation_criteria="", rating_scale=""),
        ])
        
        session = TestSession(dog_data=sample_dog, battery_name="Single Dim")
        session.add_result(TestResult(test_number=1, score=1, notes=""))
        session.add_result(TestResult(test_number=2, score=2, notes=""))
        
        analyzer = OceanAnalyzer(session, battery)
        scores = analyzer.calculate_ocean_scores()
        
        assert scores.openness == 3
        assert scores.openness_count == 2
        assert scores.conscientiousness == 0
        assert scores.conscientiousness_count == 0


class TestOceanAnalyzerWithoutBattery:
    """Tests für Analyzer ohne Testbatterie"""
    
    def test_calculate_without_battery_fails_gracefully(self, sample_session_with_results):
        """Test: Ohne Battery kann nicht berechnet werden"""
        analyzer = OceanAnalyzer(sample_session_with_results, None)
        
        with pytest.raises(ValueError, match="Battery erforderlich"):
            analyzer.calculate_ocean_scores()


class TestOceanScoresAverages:
    """Tests für Durchschnitts-Berechnung"""
    
    def test_get_averages(self, sample_session_with_results, sample_battery):
        """Test: Durchschnittswerte werden korrekt berechnet"""
        analyzer = OceanAnalyzer(sample_session_with_results, sample_battery)
        scores = analyzer.calculate_ocean_scores()
        averages = scores.get_averages()
        
        assert averages['openness'] == pytest.approx(1.5)  # 3 / 2
        assert averages['conscientiousness'] == pytest.approx(-1.0)  # -1 / 1
        assert averages['extraversion'] == pytest.approx(2.0)  # 2 / 1
        assert averages['agreeableness'] == pytest.approx(0.0)  # 0 / 1
        assert averages['neuroticism'] == pytest.approx(-2.0)  # -2 / 1
    
    def test_average_with_zero_count(self, sample_dog, sample_battery):
        """Test: Division durch 0 wird vermieden"""
        session = TestSession(dog_data=sample_dog, battery_name="Test")
        analyzer = OceanAnalyzer(session, sample_battery)
        scores = analyzer.calculate_ocean_scores()
        averages = scores.get_averages()
        
        # Bei Count=0 sollte Average=0 sein
        assert averages['openness'] == 0.0
        assert averages['conscientiousness'] == 0.0
