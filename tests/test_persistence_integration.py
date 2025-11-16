"""
Tests für Persistenz-Integration (Phase 4)
Validiert das Speichern/Laden von KI-Profilen
"""
import pytest
from pathlib import Path
from src.test_session import TestSession, TestResult
from src.models import DogData, Gender


class TestProfilePersistence:
    """Tests für KI-Profile-Persistenz"""
    
    def test_save_session_with_all_profiles(self, tmp_path):
        """Test: Session mit allen 3 Profilen speichern"""
        dog = DogData(
            owner_name="Anna", dog_name="Max",
            age_years=4, age_months=6,
            gender=Gender.MALE, neutered=True
        )
        
        # Session mit KI-Features erstellen
        session = TestSession(
            dog_data=dog,
            battery_name="Testbatterie",
            ideal_profile={'O': 10, 'C': 8, 'E': 6, 'A': 12, 'N': -6},
            owner_profile={'O': 9, 'C': 7, 'E': 5, 'A': 11, 'N': -5},
            ai_assessment="Hervorragender Therapiehund mit ausgeglichenem Temperament."
        )
        session.add_result(TestResult(test_number=1, score=2, notes="Exzellent"))
        session.add_result(TestResult(test_number=2, score=1, notes="Gut"))
        
        # Speichern
        filepath = tmp_path / "full_session.json"
        session.save_to_file(str(filepath))
        
        # Prüfen: Datei existiert
        assert filepath.exists()
        
        # Laden
        loaded = TestSession.load_from_file(str(filepath))
        
        # Validierung: Alle Profile korrekt
        assert loaded.ideal_profile == {'O': 10, 'C': 8, 'E': 6, 'A': 12, 'N': -6}
        assert loaded.owner_profile == {'O': 9, 'C': 7, 'E': 5, 'A': 11, 'N': -5}
        assert loaded.ai_assessment == "Hervorragender Therapiehund mit ausgeglichenem Temperament."
        
        # Validierung: Basisdaten korrekt
        assert loaded.dog_data.dog_name == "Max"
        assert loaded.dog_data.owner_name == "Anna"
        assert loaded.has_result(1)
        assert loaded.has_result(2)
    
    def test_save_session_with_only_ideal_profile(self, tmp_path):
        """Test: Session nur mit Idealprofil"""
        dog = DogData(
            owner_name="Bob", dog_name="Luna",
            age_years=2, age_months=3,
            gender=Gender.FEMALE, neutered=False
        )
        
        session = TestSession(
            dog_data=dog,
            battery_name="Test",
            ideal_profile={'O': 5, 'C': 7, 'E': -3, 'A': 10, 'N': 2}
        )
        session.add_result(TestResult(test_number=1, score=1))
        
        filepath = tmp_path / "ideal_only.json"
        session.save_to_file(str(filepath))
        
        loaded = TestSession.load_from_file(str(filepath))
        
        assert loaded.ideal_profile == {'O': 5, 'C': 7, 'E': -3, 'A': 10, 'N': 2}
        assert loaded.owner_profile is None
        assert loaded.ai_assessment is None
    
    def test_save_session_with_only_owner_profile(self, tmp_path):
        """Test: Session nur mit Fragebogen-Profil"""
        dog = DogData(
            owner_name="Charlie", dog_name="Bella",
            age_years=6, age_months=0,
            gender=Gender.FEMALE, neutered=True
        )
        
        session = TestSession(
            dog_data=dog,
            battery_name="Test",
            owner_profile={'O': -2, 'C': 4, 'E': 8, 'A': 6, 'N': -4}
        )
        
        filepath = tmp_path / "owner_only.json"
        session.save_to_file(str(filepath))
        
        loaded = TestSession.load_from_file(str(filepath))
        
        assert loaded.ideal_profile is None
        assert loaded.owner_profile == {'O': -2, 'C': 4, 'E': 8, 'A': 6, 'N': -4}
        assert loaded.ai_assessment is None
    
    def test_load_old_session_without_profiles(self, tmp_path):
        """Test: Alte Session ohne KI-Features laden (Backward-Compatibility)"""
        # JSON manuell erstellen (alte Session simulieren)
        import json
        old_session_data = {
            "dog_data": {
                "owner_name": "David",
                "dog_name": "Rocky",
                "age_years": 3,
                "age_months": 9,
                "gender": "Rüde",
                "neutered": False
            },
            "battery_name": "Alte Testbatterie",
            "results": {
                "1": {"test_number": 1, "score": 0, "notes": "Neutral"}
            },
            "date": "2024-01-15T10:30:00",
            "session_notes": "Alte Session ohne KI"
        }
        
        filepath = tmp_path / "old_format.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(old_session_data, f)
        
        # Laden sollte ohne Fehler funktionieren
        loaded = TestSession.load_from_file(str(filepath))
        
        # KI-Features sollten None sein
        assert loaded.ideal_profile is None
        assert loaded.owner_profile is None
        assert loaded.ai_assessment is None
        
        # Basisdaten korrekt
        assert loaded.dog_data.dog_name == "Rocky"
        assert loaded.battery_name == "Alte Testbatterie"
        assert loaded.session_notes == "Alte Session ohne KI"
    
    def test_roundtrip_preserves_all_data(self, tmp_path):
        """Test: Kompletter Roundtrip behält alle Daten"""
        dog = DogData(
            owner_name="Eva", dog_name="Charlie",
            age_years=5, age_months=2,
            gender=Gender.MALE, neutered=True
        )
        
        original = TestSession(
            dog_data=dog,
            battery_name="Vollständiger Test",
            ideal_profile={'O': 12, 'C': -8, 'E': 4, 'A': 10, 'N': 0},
            owner_profile={'O': 11, 'C': -7, 'E': 3, 'A': 9, 'N': 1},
            ai_assessment="Sehr gut geeignet für Rettungsarbeit."
        )
        original.add_result(TestResult(test_number=1, score=2, notes="Hervorragend"))
        original.add_result(TestResult(test_number=3, score=-1, notes="Zögerlich"))
        original.session_notes = "Wichtige Notizen zur Session"
        
        # Speichern und laden
        filepath = tmp_path / "roundtrip.json"
        original.save_to_file(str(filepath))
        loaded = TestSession.load_from_file(str(filepath))
        
        # Alle Felder prüfen
        assert loaded.dog_data.dog_name == original.dog_data.dog_name
        assert loaded.battery_name == original.battery_name
        assert loaded.ideal_profile == original.ideal_profile
        assert loaded.owner_profile == original.owner_profile
        assert loaded.ai_assessment == original.ai_assessment
        assert loaded.session_notes == original.session_notes
        assert len(loaded.results) == len(original.results)
        assert loaded.has_result(1)
        assert loaded.has_result(3)
        assert loaded.get_result(1).score == 2
        assert loaded.get_result(3).score == -1


class TestProfileDataValidation:
    """Tests für Profil-Datenvalidierung"""
    
    def test_profile_dict_structure(self):
        """Test: Profile haben korrektes Dict-Format"""
        dog = DogData(
            owner_name="Test", dog_name="Test",
            age_years=1, age_months=0,
            gender=Gender.MALE, neutered=False
        )
        
        profile = {'O': 5, 'C': 6, 'E': 7, 'A': 8, 'N': 9}
        session = TestSession(
            dog_data=dog,
            battery_name="Test",
            ideal_profile=profile
        )
        
        assert isinstance(session.ideal_profile, dict)
        assert set(session.ideal_profile.keys()) == {'O', 'C', 'E', 'A', 'N'}
        assert all(isinstance(v, int) for v in session.ideal_profile.values())
    
    def test_profile_values_within_range(self):
        """Test: Profile haben Werte im gültigen Bereich"""
        dog = DogData(
            owner_name="Test", dog_name="Test",
            age_years=1, age_months=0,
            gender=Gender.MALE, neutered=False
        )
        
        # Extremwerte testen
        extreme_profile = {'O': -14, 'C': 14, 'E': 0, 'A': -12, 'N': 12}
        session = TestSession(
            dog_data=dog,
            battery_name="Test",
            ideal_profile=extreme_profile,
            owner_profile={'O': -10, 'C': 10, 'E': 5, 'A': -5, 'N': 0}
        )
        
        # Alle Werte in [-14, +14]
        for key, value in session.ideal_profile.items():
            assert -14 <= value <= 14, f"{key} outside bounds: {value}"
        
        for key, value in session.owner_profile.items():
            assert -14 <= value <= 14, f"{key} outside bounds: {value}"
