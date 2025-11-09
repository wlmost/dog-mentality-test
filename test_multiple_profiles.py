"""
Quick test to visualize multiple profiles in OCEAN chart.
Blau = Ist-Profil, Rot = Fragebogen-Profil, Grün = Ideal-Profil
"""
import sys
from PySide6.QtWidgets import QApplication
from src.ocean_analyzer import OceanScores
from src.ocean_chart import OceanRadarChart

def main():
    app = QApplication(sys.argv)
    
    # Create test scores with all three profiles
    scores = OceanScores(
        openness=8,
        conscientiousness=-4,
        extraversion=6,
        agreeableness=2,
        neuroticism=-6,
        openness_count=7,
        conscientiousness_count=7,
        extraversion_count=7,
        agreeableness_count=7,
        neuroticism_count=7,
        # Fragebogen-Profil: Ergebnis des Fragebogens
        owner_profile={
            'O': 10,
            'C': 8,
            'E': 12,
            'A': 10,
            'N': -8
        },
        # Ideal-Profil: Von KI berechnet
        ideal_profile={
            'O': 6,
            'C': 2,
            'E': 10,
            'A': 12,
            'N': -10
        }
    )
    
    chart = OceanRadarChart(scores)
    chart.setWindowTitle("OCEAN Chart: Blau=Ist, Rot=Fragebogen, Grün=Ideal")
    chart.resize(900, 800)
    chart.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
