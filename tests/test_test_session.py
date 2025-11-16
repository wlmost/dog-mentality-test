"""
Tests für Test-Session und Ergebnisse
"""
import pytest
import json
from pathlib import Path
from src.test_session import TestResult, TestSession
from src.models import DogData, Gender


class TestTestResult:
    """Tests für TestResult-Modell"""
    
    def test_create_valid_result(self):
        """Test: Gültiges TestResult erstellen"""
        result = TestResult(test_number=1, score=2, notes="Sehr gut")
        assert result.test_number == 1
        assert result.score == 2
        assert result.notes == "Sehr gut"
    
    def test_score_must_be_integer(self):
        """Test: Score muss Integer sein"""
        with pytest.raises(TypeError, match="Score muss ein Integer sein"):
            TestResult(test_number=1, score=1.5)
    
    def test_score_range_validation(self):
        """Test: Score muss zwischen -2 und +2 liegen"""
        # Zu hoch
        with pytest.raises(ValueError, match="Score muss zwischen -2 und \\+2 liegen"):
            TestResult(test_number=1, score=3)
        
        # Zu niedrig
        with pytest.raises(ValueError, match="Score muss zwischen -2 und \\+2 liegen"):
            TestResult(test_number=1, score=-3)
        
        # Gültige Werte
        for score in [-2, -1, 0, 1, 2]:
            result = TestResult(test_number=1, score=score)
            assert result.score == score
    
    def test_test_number_positive(self):
        """Test: Test-Nummer muss positiv sein"""
        with pytest.raises(ValueError, match="Test-Nummer muss positiv sein"):
            TestResult(test_number=0, score=1)
    
    def test_to_dict(self):
        """Test: Konvertierung zu Dictionary"""
        result = TestResult(test_number=5, score=-1, notes="Zögerlich")
        data = result.to_dict()
        
        assert data["test_number"] == 5
        assert data["score"] == -1
        assert data["notes"] == "Zögerlich"
    
    def test_from_dict(self):
        """Test: Erstellen aus Dictionary"""
        data = {"test_number": 3, "score": 2, "notes": "Exzellent"}
        result = TestResult.from_dict(data)
        
        assert result.test_number == 3
        assert result.score == 2
        assert result.notes == "Exzellent"


class TestTestSession:
    """Tests für TestSession-Modell"""
    
    def test_create_valid_session(self):
        """Test: Gültige TestSession erstellen"""
        dog = DogData(
            owner_name="Max Mustermann",
            dog_name="Bello",
            age_years=5,
            age_months=0,
            gender=Gender.MALE,
            neutered=True
        )
        
        session = TestSession(
            dog_data=dog,
            battery_name="Testbatterie OCEAN"
        )
        
        assert session.dog_data.dog_name == "Bello"
        assert session.battery_name == "Testbatterie OCEAN"
        assert len(session.results) == 0
    
    def test_battery_name_not_empty(self):
        """Test: Battery-Name darf nicht leer sein"""
        dog = DogData(
            owner_name="Max", dog_name="Bello",
            age_years=5, age_months=0,
            gender=Gender.MALE, neutered=False
        )
        
        with pytest.raises(ValueError, match="Battery-Name darf nicht leer sein"):
            TestSession(dog_data=dog, battery_name="  ")
    
    def test_add_result(self):
        """Test: Ergebnis hinzufügen"""
        dog = DogData(
            owner_name="Max", dog_name="Bello",
            age_years=5, age_months=0,
            gender=Gender.MALE, neutered=False
        )
        session = TestSession(dog_data=dog, battery_name="Test")
        
        result = TestResult(test_number=1, score=2)
        session.add_result(result)
        
        assert len(session.results) == 1
        assert session.has_result(1)
    
    def test_get_result(self):
        """Test: Ergebnis abrufen"""
        dog = DogData(
            owner_name="Max", dog_name="Bello",
            age_years=5, age_months=0,
            gender=Gender.MALE, neutered=False
        )
        session = TestSession(dog_data=dog, battery_name="Test")
        
        result1 = TestResult(test_number=1, score=2)
        result2 = TestResult(test_number=2, score=-1)
        session.add_result(result1)
        session.add_result(result2)
        
        retrieved = session.get_result(1)
        assert retrieved is not None
        assert retrieved.score == 2
        
        not_found = session.get_result(99)
        assert not_found is None
    
    def test_get_completed_count(self):
        """Test: Anzahl abgeschlossener Tests"""
        dog = DogData(
            owner_name="Max", dog_name="Bello",
            age_years=5, age_months=0,
            gender=Gender.MALE, neutered=False
        )
        session = TestSession(dog_data=dog, battery_name="Test")
        
        assert session.get_completed_count() == 0
        
        session.add_result(TestResult(test_number=1, score=1))
        assert session.get_completed_count() == 1
        
        session.add_result(TestResult(test_number=2, score=0))
        assert session.get_completed_count() == 2
    
    def test_to_dict(self):
        """Test: Konvertierung zu Dictionary"""
        dog = DogData(
            owner_name="Max", dog_name="Bello",
            age_years=5, age_months=0,
            gender=Gender.MALE, neutered=False
        )
        session = TestSession(dog_data=dog, battery_name="Test")
        session.add_result(TestResult(test_number=1, score=2))
        
        data = session.to_dict()
        
        assert data["battery_name"] == "Test"
        assert data["dog_data"]["dog_name"] == "Bello"
        assert "1" in data["results"]
        assert data["results"]["1"]["score"] == 2
    
    def test_from_dict(self):
        """Test: Erstellen aus Dictionary"""
        data = {
            "dog_data": {
                "owner_name": "Max",
                "dog_name": "Bello",
                "age_years": 5,
                "age_months": 0,
                "gender": "Rüde",
                "neutered": False
            },
            "battery_name": "Test",
            "results": {
                "1": {"test_number": 1, "score": 2, "notes": "Gut"}
            },
            "date": "2025-01-01T12:00:00",
            "session_notes": "Test-Session"
        }
        
        session = TestSession.from_dict(data)
        
        assert session.dog_data.dog_name == "Bello"
        assert session.battery_name == "Test"
        assert session.has_result(1)
        assert session.get_result(1).score == 2
    
    def test_save_and_load_file(self, tmp_path):
        """Test: Speichern und Laden aus Datei"""
        dog = DogData(
            owner_name="Max", dog_name="Bello",
            age_years=5, age_months=0,
            gender=Gender.MALE, neutered=False
        )
        session = TestSession(dog_data=dog, battery_name="Test")
        session.add_result(TestResult(test_number=1, score=2, notes="Sehr gut"))
        session.session_notes = "Test-Session erfolgreich"
        
        # Speichern
        filepath = tmp_path / "test_session.json"
        session.save_to_file(str(filepath))
        
        # Prüfen ob Datei existiert
        assert filepath.exists()
        
        # Laden
        loaded_session = TestSession.load_from_file(str(filepath))
        
        assert loaded_session.dog_data.dog_name == "Bello"
        assert loaded_session.battery_name == "Test"
        assert loaded_session.has_result(1)
        assert loaded_session.get_result(1).score == 2
        assert loaded_session.session_notes == "Test-Session erfolgreich"
    
    def test_save_and_load_with_profiles(self, tmp_path):
        """Test: Speichern und Laden mit KI-Profilen"""
        dog = DogData(
            owner_name="Max", dog_name="Bello",
            age_years=5, age_months=0,
            gender=Gender.MALE, neutered=False
        )
        
        # Session mit allen KI-Features erstellen
        session = TestSession(
            dog_data=dog, 
            battery_name="Test",
            ideal_profile={'O': 8, 'C': 10, 'E': 6, 'A': 12, 'N': -4},
            owner_profile={'O': 7, 'C': 9, 'E': 5, 'A': 11, 'N': -3},
            ai_assessment="Sehr guter Hund für Therapiearbeit."
        )
        session.add_result(TestResult(test_number=1, score=2))
        
        # Speichern
        filepath = tmp_path / "test_with_profiles.json"
        session.save_to_file(str(filepath))
        
        # Laden
        loaded = TestSession.load_from_file(str(filepath))
        
        # KI-Features prüfen
        assert loaded.ideal_profile == {'O': 8, 'C': 10, 'E': 6, 'A': 12, 'N': -4}
        assert loaded.owner_profile == {'O': 7, 'C': 9, 'E': 5, 'A': 11, 'N': -3}
        assert loaded.ai_assessment == "Sehr guter Hund für Therapiearbeit."
        
        # Basisdaten prüfen
        assert loaded.dog_data.dog_name == "Bello"
        assert loaded.has_result(1)
    
    def test_backward_compatibility_load(self, tmp_path):
        """Test: Alte Sessions ohne KI-Features laden"""
        # Alte Session ohne KI-Features simulieren
        old_data = {
            "dog_data": {
                "owner_name": "Max",
                "dog_name": "Bello",
                "age_years": 5,
                "age_months": 0,
                "gender": "Rüde",
                "neutered": False
            },
            "battery_name": "Test",
            "results": {
                "1": {"test_number": 1, "score": 2, "notes": "Gut"}
            },
            "date": "2025-01-01T12:00:00",
            "session_notes": "Alte Session"
        }
        
        # Als JSON speichern
        filepath = tmp_path / "old_session.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(old_data, f)
        
        # Laden sollte funktionieren ohne Fehler
        loaded = TestSession.load_from_file(str(filepath))
        
        # KI-Features sollten None sein
        assert loaded.ideal_profile is None
        assert loaded.owner_profile is None
        assert loaded.ai_assessment is None
        
        # Basisdaten sollten korrekt sein
        assert loaded.dog_data.dog_name == "Bello"
        assert loaded.battery_name == "Test"
        assert loaded.session_notes == "Alte Session"
