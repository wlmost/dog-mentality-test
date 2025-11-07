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
            age_years=5,
            age_months=3,
            gender=Gender.MALE,
            neutered=True
        )
        assert dog.owner_name == "Max Mustermann"
        assert dog.dog_name == "Bello"
        assert dog.age_years == 5
        assert dog.age_months == 3
        assert dog.gender == Gender.MALE
        assert dog.neutered is True

    def test_age_years_must_be_integer(self):
        """Test: Alter (Jahre) muss Integer sein"""
        with pytest.raises(TypeError, match="Alter \\(Jahre\\) muss ein Integer sein"):
            DogData(
                owner_name="Max Mustermann",
                dog_name="Bello",
                age_years=5.5,  # Float statt Integer
                age_months=0,
                gender=Gender.MALE,
                neutered=False
            )

    def test_age_months_must_be_integer(self):
        """Test: Alter (Monate) muss Integer sein"""
        with pytest.raises(TypeError, match="Alter \\(Monate\\) muss ein Integer sein"):
            DogData(
                owner_name="Max Mustermann",
                dog_name="Bello",
                age_years=5,
                age_months=3.5,  # Float statt Integer
                gender=Gender.MALE,
                neutered=False
            )

    def test_age_years_must_be_positive(self):
        """Test: Alter (Jahre) muss positiv sein"""
        with pytest.raises(ValueError, match="Alter \\(Jahre\\) muss positiv sein"):
            DogData(
                owner_name="Max Mustermann",
                dog_name="Bello",
                age_years=-1,
                age_months=0,
                gender=Gender.MALE,
                neutered=False
            )

    def test_age_months_range(self):
        """Test: Alter (Monate) muss zwischen 0 und 11 liegen"""
        with pytest.raises(ValueError, match="Alter \\(Monate\\) muss zwischen 0 und 11 liegen"):
            DogData(
                owner_name="Max Mustermann",
                dog_name="Bello",
                age_years=5,
                age_months=12,  # Zu groß
                gender=Gender.MALE,
                neutered=False
            )

    def test_age_cannot_be_zero(self):
        """Test: Alter muss mindestens 1 Monat betragen"""
        with pytest.raises(ValueError, match="Alter muss mindestens 1 Monat betragen"):
            DogData(
                owner_name="Max Mustermann",
                dog_name="Bello",
                age_years=0,
                age_months=0,
                gender=Gender.MALE,
                neutered=False
            )

    def test_owner_name_not_empty(self):
        """Test: Name des Halters darf nicht leer sein"""
        with pytest.raises(ValueError, match="Name des Halters darf nicht leer sein"):
            DogData(
                owner_name="   ",
                dog_name="Bello",
                age_years=5,
                age_months=0,
                gender=Gender.MALE,
                neutered=False
            )

    def test_dog_name_not_empty(self):
        """Test: Name des Hundes darf nicht leer sein"""
        with pytest.raises(ValueError, match="Name des Hundes darf nicht leer sein"):
            DogData(
                owner_name="Max Mustermann",
                dog_name="",
                age_years=5,
                age_months=0,
                gender=Gender.MALE,
                neutered=False
            )

    def test_age_in_months(self):
        """Test: Gesamtalter in Monaten berechnen"""
        dog = DogData(
            owner_name="Max Mustermann",
            dog_name="Bello",
            age_years=2,
            age_months=5,
            gender=Gender.MALE,
            neutered=False
        )
        assert dog.age_in_months == 29  # 2*12 + 5

    def test_age_display_years_only(self):
        """Test: Altersanzeige nur Jahre"""
        dog = DogData(
            owner_name="Max Mustermann",
            dog_name="Bello",
            age_years=5,
            age_months=0,
            gender=Gender.MALE,
            neutered=False
        )
        assert dog.age_display() == "5 Jahre"

    def test_age_display_months_only(self):
        """Test: Altersanzeige nur Monate"""
        dog = DogData(
            owner_name="Max Mustermann",
            dog_name="Bello",
            age_years=0,
            age_months=8,
            gender=Gender.MALE,
            neutered=False
        )
        assert dog.age_display() == "8 Monate"

    def test_age_display_combined(self):
        """Test: Altersanzeige Jahre und Monate"""
        dog = DogData(
            owner_name="Max Mustermann",
            dog_name="Bello",
            age_years=2,
            age_months=3,
            gender=Gender.MALE,
            neutered=False
        )
        assert dog.age_display() == "2 Jahre, 3 Monate"

    def test_to_dict(self):
        """Test: Konvertierung zu Dictionary"""
        dog = DogData(
            owner_name="Max Mustermann",
            dog_name="Bello",
            age_years=5,
            age_months=3,
            gender=Gender.FEMALE,
            neutered=True
        )
        data = dog.to_dict()
        assert data["owner_name"] == "Max Mustermann"
        assert data["dog_name"] == "Bello"
        assert data["age_years"] == 5
        assert data["age_months"] == 3
        assert data["gender"] == "Hündin"
        assert data["neutered"] is True

    def test_from_dict(self):
        """Test: Erstellen aus Dictionary"""
        data = {
            "owner_name": "Max Mustermann",
            "dog_name": "Bello",
            "age_years": 5,
            "age_months": 3,
            "gender": "Rüde",
            "neutered": True
        }
        dog = DogData.from_dict(data)
        assert dog.owner_name == "Max Mustermann"
        assert dog.dog_name == "Bello"
        assert dog.age_years == 5
        assert dog.age_months == 3
        assert dog.gender == Gender.MALE
        assert dog.neutered is True
