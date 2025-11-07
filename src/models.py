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
    age: int
    gender: Gender
    neutered: bool

    def __post_init__(self):
        """Validierung der Eingabedaten"""
        if not isinstance(self.age, int):
            raise TypeError("Alter muss ein Integer sein")
        if self.age < 0:
            raise ValueError("Alter muss positiv sein")
        if not self.owner_name.strip():
            raise ValueError("Name des Halters darf nicht leer sein")
        if not self.dog_name.strip():
            raise ValueError("Name des Hundes darf nicht leer sein")

    def to_dict(self) -> dict:
        """Konvertiert DogData zu Dictionary für JSON-Serialisierung"""
        return {
            "owner_name": self.owner_name,
            "dog_name": self.dog_name,
            "age": self.age,
            "gender": self.gender.value,
            "neutered": self.neutered
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DogData":
        """Erstellt DogData-Objekt aus Dictionary"""
        gender = Gender.MALE if data["gender"] == "Rüde" else Gender.FEMALE
        return cls(
            owner_name=data["owner_name"],
            dog_name=data["dog_name"],
            age=data["age"],
            gender=gender,
            neutered=data["neutered"]
        )
