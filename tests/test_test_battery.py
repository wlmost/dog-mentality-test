"""
Tests für Testbatterie-Datenmodell
"""
import pytest
from src.test_battery import Test, TestBattery, OceanDimension


class TestOceanDimension:
    """Tests für OCEAN-Dimensionen"""
    
    def test_ocean_dimensions_exist(self):
        """Test: Alle 5 OCEAN-Dimensionen sind definiert"""
        assert OceanDimension.OPENNESS.value == "Offenheit"
        assert OceanDimension.CONSCIENTIOUSNESS.value == "Gewissenhaftigkeit"
        assert OceanDimension.EXTRAVERSION.value == "Extraversion"
        assert OceanDimension.AGREEABLENESS.value == "Verträglichkeit"
        assert OceanDimension.NEUROTICISM.value == "Neurotizismus"


class TestTest:
    """Tests für Test-Modell"""
    
    def test_create_valid_test(self):
        """Test: Gültiges Test-Objekt erstellen"""
        test = Test(
            number=1,
            ocean_dimension=OceanDimension.OPENNESS,
            name="Unbekanntes Objekt",
            setting="Ruhiger Raum",
            materials="Klappstuhl, Timer",
            duration="2-3 Min",
            role_figurant="Neutral beobachten",
            observation_criteria="Annäherung, Schnüffeln",
            rating_scale="-2 bis +2"
        )
        
        assert test.number == 1
        assert test.ocean_dimension == OceanDimension.OPENNESS
        assert test.name == "Unbekanntes Objekt"
    
    def test_number_must_be_positive(self):
        """Test: Test-Nummer muss positiv sein"""
        with pytest.raises(ValueError, match="Test-Nummer muss positiv sein"):
            Test(
                number=0,
                ocean_dimension=OceanDimension.OPENNESS,
                name="Test",
                setting="", materials="", duration="",
                role_figurant="", observation_criteria="", rating_scale=""
            )
    
    def test_name_not_empty(self):
        """Test: Testname darf nicht leer sein"""
        with pytest.raises(ValueError, match="Testname darf nicht leer sein"):
            Test(
                number=1,
                ocean_dimension=OceanDimension.OPENNESS,
                name="   ",
                setting="", materials="", duration="",
                role_figurant="", observation_criteria="", rating_scale=""
            )
    
    def test_to_dict(self):
        """Test: Konvertierung zu Dictionary"""
        test = Test(
            number=1,
            ocean_dimension=OceanDimension.CONSCIENTIOUSNESS,
            name="Ruhiges Warten",
            setting="Raum", materials="Leine", duration="1 Min",
            role_figurant="Vorbei gehen", observation_criteria="Position halten",
            rating_scale="-2 bis +2"
        )
        
        data = test.to_dict()
        assert data["number"] == 1
        assert data["ocean_dimension"] == "Gewissenhaftigkeit"
        assert data["name"] == "Ruhiges Warten"
    
    def test_from_dict(self):
        """Test: Erstellen aus Dictionary"""
        data = {
            "number": 1,
            "ocean_dimension": "Offenheit",
            "name": "Test",
            "setting": "Raum",
            "materials": "Material",
            "duration": "2 Min",
            "role_figurant": "Rolle",
            "observation_criteria": "Kriterien",
            "rating_scale": "Skala"
        }
        
        test = Test.from_dict(data)
        assert test.number == 1
        assert test.ocean_dimension == OceanDimension.OPENNESS
        assert test.name == "Test"


class TestTestBattery:
    """Tests für TestBattery-Modell"""
    
    def test_create_valid_battery(self):
        """Test: Gültige Testbatterie erstellen"""
        test1 = Test(
            number=1, ocean_dimension=OceanDimension.OPENNESS,
            name="Test 1", setting="", materials="", duration="",
            role_figurant="", observation_criteria="", rating_scale=""
        )
        test2 = Test(
            number=2, ocean_dimension=OceanDimension.EXTRAVERSION,
            name="Test 2", setting="", materials="", duration="",
            role_figurant="", observation_criteria="", rating_scale=""
        )
        
        battery = TestBattery(name="Testbatterie", tests=[test1, test2])
        
        assert battery.name == "Testbatterie"
        assert len(battery.tests) == 2
    
    def test_name_not_empty(self):
        """Test: Name der Testbatterie darf nicht leer sein"""
        test1 = Test(
            number=1, ocean_dimension=OceanDimension.OPENNESS,
            name="Test", setting="", materials="", duration="",
            role_figurant="", observation_criteria="", rating_scale=""
        )
        
        with pytest.raises(ValueError, match="Name der Testbatterie darf nicht leer sein"):
            TestBattery(name="  ", tests=[test1])
    
    def test_must_have_tests(self):
        """Test: Testbatterie muss mindestens einen Test enthalten"""
        with pytest.raises(ValueError, match="Testbatterie muss mindestens einen Test enthalten"):
            TestBattery(name="Testbatterie", tests=[])
    
    def test_get_test_by_number(self):
        """Test: Test nach Nummer finden"""
        test1 = Test(
            number=1, ocean_dimension=OceanDimension.OPENNESS,
            name="Test 1", setting="", materials="", duration="",
            role_figurant="", observation_criteria="", rating_scale=""
        )
        test2 = Test(
            number=2, ocean_dimension=OceanDimension.EXTRAVERSION,
            name="Test 2", setting="", materials="", duration="",
            role_figurant="", observation_criteria="", rating_scale=""
        )
        
        battery = TestBattery(name="Testbatterie", tests=[test1, test2])
        
        found = battery.get_test_by_number(2)
        assert found is not None
        assert found.name == "Test 2"
        
        not_found = battery.get_test_by_number(99)
        assert not_found is None
    
    def test_get_tests_by_dimension(self):
        """Test: Tests nach OCEAN-Dimension filtern"""
        test1 = Test(
            number=1, ocean_dimension=OceanDimension.OPENNESS,
            name="Test 1", setting="", materials="", duration="",
            role_figurant="", observation_criteria="", rating_scale=""
        )
        test2 = Test(
            number=2, ocean_dimension=OceanDimension.OPENNESS,
            name="Test 2", setting="", materials="", duration="",
            role_figurant="", observation_criteria="", rating_scale=""
        )
        test3 = Test(
            number=3, ocean_dimension=OceanDimension.EXTRAVERSION,
            name="Test 3", setting="", materials="", duration="",
            role_figurant="", observation_criteria="", rating_scale=""
        )
        
        battery = TestBattery(name="Testbatterie", tests=[test1, test2, test3])
        
        openness_tests = battery.get_tests_by_dimension(OceanDimension.OPENNESS)
        assert len(openness_tests) == 2
        
        extraversion_tests = battery.get_tests_by_dimension(OceanDimension.EXTRAVERSION)
        assert len(extraversion_tests) == 1
