"""
Datenmodelle für Testbatterie und Tests
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class OceanDimension(Enum):
    """OCEAN-Persönlichkeitsdimensionen"""
    OPENNESS = "Offenheit"
    CONSCIENTIOUSNESS = "Gewissenhaftigkeit"
    EXTRAVERSION = "Extraversion"
    AGREEABLENESS = "Verträglichkeit"
    NEUROTICISM = "Neurotizismus"


@dataclass
class Test:
    """
    Einzelner Test aus der Testbatterie
    """
    number: int
    ocean_dimension: OceanDimension
    name: str
    setting: str
    materials: str
    duration: str
    role_figurant: str
    observation_criteria: str
    rating_scale: str
    
    def __post_init__(self):
        """Validierung"""
        if self.number < 1:
            raise ValueError("Test-Nummer muss positiv sein")
        if not self.name.strip():
            raise ValueError("Testname darf nicht leer sein")
    
    def to_dict(self) -> dict:
        """Konvertiert Test zu Dictionary"""
        return {
            "number": self.number,
            "ocean_dimension": self.ocean_dimension.value,
            "name": self.name,
            "setting": self.setting,
            "materials": self.materials,
            "duration": self.duration,
            "role_figurant": self.role_figurant,
            "observation_criteria": self.observation_criteria,
            "rating_scale": self.rating_scale
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Test":
        """Erstellt Test aus Dictionary"""
        # Ocean-Dimension finden
        ocean_dim = None
        for dim in OceanDimension:
            if dim.value == data["ocean_dimension"]:
                ocean_dim = dim
                break
        
        if ocean_dim is None:
            raise ValueError(f"Unbekannte OCEAN-Dimension: {data['ocean_dimension']}")
        
        return cls(
            number=data["number"],
            ocean_dimension=ocean_dim,
            name=data["name"],
            setting=data["setting"],
            materials=data["materials"],
            duration=data["duration"],
            role_figurant=data["role_figurant"],
            observation_criteria=data["observation_criteria"],
            rating_scale=data["rating_scale"]
        )


@dataclass
class TestBattery:
    """
    Sammlung von Tests
    """
    name: str
    tests: List[Test]
    
    def __post_init__(self):
        """Validierung"""
        if not self.name.strip():
            raise ValueError("Name der Testbatterie darf nicht leer sein")
        if not self.tests:
            raise ValueError("Testbatterie muss mindestens einen Test enthalten")
    
    def get_test_by_number(self, number: int) -> Optional[Test]:
        """Gibt Test mit bestimmter Nummer zurück"""
        for test in self.tests:
            if test.number == number:
                return test
        return None
    
    def get_tests_by_dimension(self, dimension: OceanDimension) -> List[Test]:
        """Gibt alle Tests einer OCEAN-Dimension zurück"""
        return [test for test in self.tests if test.ocean_dimension == dimension]
    
    def to_dict(self) -> dict:
        """Konvertiert TestBattery zu Dictionary"""
        return {
            "name": self.name,
            "tests": [test.to_dict() for test in self.tests]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TestBattery":
        """Erstellt TestBattery aus Dictionary"""
        tests = [Test.from_dict(test_data) for test_data in data["tests"]]
        return cls(
            name=data["name"],
            tests=tests
        )
