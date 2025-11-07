"""
Tests für Datenmodelle
"""
import pytest
from src.models import DogData, Gender


class TestDogData:
    """Test-Suite für DogData-Modell"""

    def test_create_valid_dog_data(self):
        """Test: Gültige DogData-Instanz erstellen"""
        dog = DogData(
            owner_name="Max Mustermann",
            dog_name="Bello",
            age=5,
            gender=Gender.MALE,
            neutered=True
        )
        assert dog.owner_name == "Max Mustermann"
        assert dog.dog_name == "Bello"
        assert dog.age == 5
        assert dog.gender == Gender.MALE
        assert dog.neutered is True

    def test_age_must_be_integer(self):
        """Test: Alter muss Integer sein"""
        with pytest.raises(TypeError, match="Alter muss ein Integer sein"):
            DogData(
                owner_name="Max Mustermann",
                dog_name="Bello",
                age=5.5,  # Float statt Integer
                gender=Gender.MALE,
                neutered=False
            )

    def test_age_must_be_positive(self):
        """Test: Alter muss positiv sein"""
        with pytest.raises(ValueError, match="Alter muss positiv sein"):
            DogData(
                owner_name="Max Mustermann",
                dog_name="Bello",
                age=-1,
                gender=Gender.MALE,
                neutered=False
            )

    def test_owner_name_not_empty(self):
        """Test: Name des Halters darf nicht leer sein"""
        with pytest.raises(ValueError, match="Name des Halters darf nicht leer sein"):
            DogData(
                owner_name="   ",
                dog_name="Bello",
                age=5,
                gender=Gender.MALE,
                neutered=False
            )

    def test_dog_name_not_empty(self):
        """Test: Name des Hundes darf nicht leer sein"""
        with pytest.raises(ValueError, match="Name des Hundes darf nicht leer sein"):
            DogData(
                owner_name="Max Mustermann",
                dog_name="",
                age=5,
                gender=Gender.MALE,
                neutered=False
            )

    def test_to_dict(self):
        """Test: Konvertierung zu Dictionary"""
        dog = DogData(
            owner_name="Max Mustermann",
            dog_name="Bello",
            age=5,
            gender=Gender.FEMALE,
            neutered=True
        )
        data = dog.to_dict()
        assert data["owner_name"] == "Max Mustermann"
        assert data["dog_name"] == "Bello"
        assert data["age"] == 5
        assert data["gender"] == "Hündin"
        assert data["neutered"] is True

    def test_from_dict(self):
        """Test: Erstellen aus Dictionary"""
        data = {
            "owner_name": "Max Mustermann",
            "dog_name": "Bello",
            "age": 5,
            "gender": "Rüde",
            "neutered": True
        }
        dog = DogData.from_dict(data)
        assert dog.owner_name == "Max Mustermann"
        assert dog.dog_name == "Bello"
        assert dog.age == 5
        assert dog.gender == Gender.MALE
        assert dog.neutered is True
