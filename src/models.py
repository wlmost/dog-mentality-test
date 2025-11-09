"""
Datenmodelle für die Dog Mentality Test Application
"""
from dataclasses import dataclass
from enum import Enum


class Gender(Enum):
    """Geschlecht des Hundes"""
    MALE = "Rüde"
    FEMALE = "Hündin"


@dataclass
class DogData:
    """Stammdaten für einen Hund und seinen Halter"""
    owner_name: str
    dog_name: str
    age_years: int
    age_months: int
    gender: Gender
    neutered: bool
    breed: str = ""
    intended_use: str = ""

    def __post_init__(self):
        """Validierung der Eingabedaten"""
        if not isinstance(self.age_years, int):
            raise TypeError("Alter (Jahre) muss ein Integer sein")
        if not isinstance(self.age_months, int):
            raise TypeError("Alter (Monate) muss ein Integer sein")
        if self.age_years < 0:
            raise ValueError("Alter (Jahre) muss positiv sein")
        if self.age_months < 0 or self.age_months > 11:
            raise ValueError("Alter (Monate) muss zwischen 0 und 11 liegen")
        if self.age_years == 0 and self.age_months == 0:
            raise ValueError("Alter muss mindestens 1 Monat betragen")
        if not self.owner_name.strip():
            raise ValueError("Name des Halters darf nicht leer sein")
        if not self.dog_name.strip():
            raise ValueError("Name des Hundes darf nicht leer sein")

    @property
    def age_in_months(self) -> int:
        """Gibt das Gesamtalter in Monaten zurück"""
        return self.age_years * 12 + self.age_months

    def age_display(self) -> str:
        """Gibt das Alter in lesbarer Form zurück"""
        if self.age_years == 0:
            return f"{self.age_months} Monat{'e' if self.age_months != 1 else ''}"
        elif self.age_months == 0:
            return f"{self.age_years} Jahr{'e' if self.age_years != 1 else ''}"
        else:
            return f"{self.age_years} Jahr{'e' if self.age_years != 1 else ''}, {self.age_months} Monat{'e' if self.age_months != 1 else ''}"

    def to_dict(self) -> dict:
        """Konvertiert DogData zu Dictionary für JSON-Serialisierung"""
        return {
            "owner_name": self.owner_name,
            "dog_name": self.dog_name,
            "breed": self.breed,
            "age_years": self.age_years,
            "age_months": self.age_months,
            "gender": self.gender.value,
            "neutered": self.neutered,
            "intended_use": self.intended_use
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DogData":
        """Erstellt DogData-Objekt aus Dictionary"""
        gender = Gender.MALE if data["gender"] == "Rüde" else Gender.FEMALE
        return cls(
            owner_name=data["owner_name"],
            dog_name=data["dog_name"],
            breed=data.get("breed", ""),  # Rückwärtskompatibilität
            age_years=data.get("age_years", data.get("age", 0)),  # Rückwärtskompatibilität
            age_months=data.get("age_months", 0),
            gender=gender,
            neutered=data["neutered"],
            intended_use=data.get("intended_use", "")  # Rückwärtskompatibilität
        )
