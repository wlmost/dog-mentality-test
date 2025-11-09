"""
OCEAN-Analyzer: Berechnung der OCEAN-Dimensionswerte

Dieser Analyzer berechnet aus den Testergebnissen einer TestSession
die Summen- und Durchschnittswerte für die 5 OCEAN-Dimensionen:
- O: Openness (Offenheit)
- C: Conscientiousness (Gewissenhaftigkeit)
- E: Extraversion (Extraversion)
- A: Agreeableness (Verträglichkeit)
- N: Neuroticism (Neurotizismus)

Funktionsweise:
1. Gruppierung der TestResults nach OCEAN-Dimension (aus TestBattery)
2. Summierung der Scores pro Dimension
3. Zählung der Tests pro Dimension
4. Optional: Berechnung von Durchschnittswerten

Design-Entscheidung:
- Summierung statt Durchschnitt als Hauptwert (siehe concept_ocean_analyse.md)
- Durchschnitt optional verfügbar über get_averages()
- Grund: Bei unterschiedlicher Anzahl Tests pro Dimension wäre Durchschnitt irreführend
"""
from dataclasses import dataclass
from typing import Optional
from src.test_session import TestSession
from src.test_battery import TestBattery, OceanDimension


@dataclass
class OceanScores:
    """
    Speichert OCEAN-Dimensionswerte
    
    Attributes:
        openness: Summe aller Scores für Openness
        conscientiousness: Summe aller Scores für Conscientiousness
        extraversion: Summe aller Scores für Extraversion
        agreeableness: Summe aller Scores für Agreeableness
        neuroticism: Summe aller Scores für Neuroticism
        
        *_count: Anzahl Tests pro Dimension (für Durchschnittsberechnung)
    """
    openness: int = 0
    conscientiousness: int = 0
    extraversion: int = 0
    agreeableness: int = 0
    neuroticism: int = 0
    
    openness_count: int = 0
    conscientiousness_count: int = 0
    extraversion_count: int = 0
    agreeableness_count: int = 0
    neuroticism_count: int = 0
    
    def get_averages(self) -> dict[str, float]:
        """
        Berechnet Durchschnittswerte für alle Dimensionen
        
        Returns:
            Dictionary mit Durchschnittswerten {'openness': 1.5, ...}
            Bei Count=0 wird 0.0 zurückgegeben (statt Division durch 0)
        """
        return {
            'openness': self.openness / self.openness_count if self.openness_count > 0 else 0.0,
            'conscientiousness': self.conscientiousness / self.conscientiousness_count if self.conscientiousness_count > 0 else 0.0,
            'extraversion': self.extraversion / self.extraversion_count if self.extraversion_count > 0 else 0.0,
            'agreeableness': self.agreeableness / self.agreeableness_count if self.agreeableness_count > 0 else 0.0,
            'neuroticism': self.neuroticism / self.neuroticism_count if self.neuroticism_count > 0 else 0.0,
        }


class OceanAnalyzer:
    """
    Analysiert TestSession und berechnet OCEAN-Dimensionswerte
    
    Beispiel:
        battery = TestBattery.load("battery.xlsx")
        session = TestSession.load("session.json")
        
        analyzer = OceanAnalyzer(session, battery)
        scores = analyzer.calculate_ocean_scores()
        
        print(f"Openness: {scores.openness} (aus {scores.openness_count} Tests)")
        print(f"Durchschnitt: {scores.get_averages()['openness']:.2f}")
    """
    
    def __init__(self, session: TestSession, battery: Optional[TestBattery]):
        """
        Initialisiert den Analyzer
        
        Args:
            session: TestSession mit Testergebnissen
            battery: TestBattery mit OCEAN-Dimensionszuordnung (optional)
        """
        self.session = session
        self.battery = battery
    
    def calculate_ocean_scores(self) -> OceanScores:
        """
        Berechnet OCEAN-Dimensionswerte aus den Testergebnissen
        
        Returns:
            OceanScores mit Summenwerten und Counts
            
        Raises:
            ValueError: Wenn keine Battery vorhanden ist
            
        Funktionsweise:
            1. Durchläuft alle TestResults in der Session
            2. Findet zugehörigen Test in der Battery
            3. Addiert Score zur entsprechenden OCEAN-Dimension
            4. Erhöht Count für die Dimension
        """
        if self.battery is None:
            raise ValueError("Battery erforderlich für OCEAN-Berechnung")
        
        scores = OceanScores()
        
        # Durchlaufe alle TestResults
        for result in self.session.results.values():
            # Finde zugehörigen Test in Battery
            test = self._find_test_in_battery(result.test_number)
            
            if test is None:
                continue  # Test nicht in Battery gefunden → überspringen
            
            # Addiere Score zur richtigen Dimension
            dimension = test.ocean_dimension
            score = result.score
            
            if dimension == OceanDimension.OPENNESS:
                scores.openness += score
                scores.openness_count += 1
            elif dimension == OceanDimension.CONSCIENTIOUSNESS:
                scores.conscientiousness += score
                scores.conscientiousness_count += 1
            elif dimension == OceanDimension.EXTRAVERSION:
                scores.extraversion += score
                scores.extraversion_count += 1
            elif dimension == OceanDimension.AGREEABLENESS:
                scores.agreeableness += score
                scores.agreeableness_count += 1
            elif dimension == OceanDimension.NEUROTICISM:
                scores.neuroticism += score
                scores.neuroticism_count += 1
        
        return scores
    
    def _find_test_in_battery(self, test_number: int) -> Optional['Test']:
        """
        Findet Test in Battery anhand der Testnummer
        
        Args:
            test_number: Nummer des Tests
            
        Returns:
            Test-Objekt oder None wenn nicht gefunden
        """
        if self.battery is None:
            return None
        
        for test in self.battery.tests:
            if test.number == test_number:
                return test
        
        return None
