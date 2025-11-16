"""
Datenmodelle für Test-Ergebnisse und Bewertungen
"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
import json
from pathlib import Path
from src.models import DogData
from src.test_battery import TestBattery


@dataclass
class TestResult:
    """
    Ergebnis eines einzelnen Tests
    Bewertung von -2 bis +2
    """
    test_number: int
    score: int
    notes: str = ""
    
    def __post_init__(self):
        """Validierung"""
        if not isinstance(self.score, int):
            raise TypeError("Score muss ein Integer sein")
        if self.score < -2 or self.score > 2:
            raise ValueError("Score muss zwischen -2 und +2 liegen")
        if self.test_number < 1:
            raise ValueError("Test-Nummer muss positiv sein")
    
    def to_dict(self) -> dict:
        """Konvertiert TestResult zu Dictionary"""
        return {
            "test_number": self.test_number,
            "score": self.score,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TestResult":
        """Erstellt TestResult aus Dictionary"""
        return cls(
            test_number=data["test_number"],
            score=data["score"],
            notes=data.get("notes", "")
        )


@dataclass
class TestSession:
    """
    Komplette Test-Session mit Hund und allen Ergebnissen
    
    Erweitert mit KI-Features:
    - ideal_profile: KI-generiertes Idealprofil für die Rolle des Hundes
    - owner_profile: Fragebogen-Profil basierend auf Halter-Erwartungen
    - ai_assessment: KI-Bewertung basierend auf allen 3 Profilen
    """
    dog_data: DogData
    battery_name: str
    results: Dict[int, TestResult] = field(default_factory=dict)
    date: str = field(default_factory=lambda: datetime.now().isoformat())
    session_notes: str = ""
    
    # KI-Features (Phase 2/3)
    ideal_profile: Optional[Dict[str, int]] = None
    owner_profile: Optional[Dict[str, int]] = None
    ai_assessment: Optional[str] = None
    
    def __post_init__(self):
        """Validierung"""
        if not self.battery_name.strip():
            raise ValueError("Battery-Name darf nicht leer sein")
    
    def add_result(self, result: TestResult):
        """Fügt Test-Ergebnis hinzu"""
        self.results[result.test_number] = result
    
    def get_result(self, test_number: int) -> Optional[TestResult]:
        """Gibt Ergebnis für Test-Nummer zurück"""
        return self.results.get(test_number)
    
    def has_result(self, test_number: int) -> bool:
        """Prüft ob Ergebnis für Test existiert"""
        return test_number in self.results
    
    def get_completed_count(self) -> int:
        """Gibt Anzahl abgeschlossener Tests zurück"""
        return len(self.results)
    
    def to_dict(self) -> dict:
        """Konvertiert TestSession zu Dictionary (inkl. KI-Features)"""
        data = {
            "dog_data": self.dog_data.to_dict(),
            "battery_name": self.battery_name,
            "results": {
                str(num): result.to_dict() 
                for num, result in self.results.items()
            },
            "date": self.date,
            "session_notes": self.session_notes
        }
        
        # KI-Features optional hinzufügen
        if self.ideal_profile is not None:
            data["ideal_profile"] = self.ideal_profile
        if self.owner_profile is not None:
            data["owner_profile"] = self.owner_profile
        if self.ai_assessment is not None:
            data["ai_assessment"] = self.ai_assessment
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "TestSession":
        """Erstellt TestSession aus Dictionary (inkl. KI-Features)"""
        dog_data = DogData.from_dict(data["dog_data"])
        
        # Results konvertieren
        results = {}
        for num_str, result_data in data.get("results", {}).items():
            num = int(num_str)
            results[num] = TestResult.from_dict(result_data)
        
        return cls(
            dog_data=dog_data,
            battery_name=data["battery_name"],
            results=results,
            date=data.get("date", datetime.now().isoformat()),
            session_notes=data.get("session_notes", ""),
            ideal_profile=data.get("ideal_profile"),
            owner_profile=data.get("owner_profile"),
            ai_assessment=data.get("ai_assessment")
        )
    
    def save_to_file(self, filepath: str):
        """Speichert Session als JSON-Datei"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "TestSession":
        """Lädt Session aus JSON-Datei"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
