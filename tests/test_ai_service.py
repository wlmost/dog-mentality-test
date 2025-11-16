"""
Tests für Settings und AI Service Configuration
"""
import pytest
from unittest.mock import patch, MagicMock
from src.settings import Settings, settings
from src.ai_service import AIProfileService, AIProfileConfigError


class TestSettings:
    """Tests für Settings-Klasse"""
    
    def test_settings_singleton(self):
        """Settings sollte ein Singleton sein"""
        s1 = Settings()
        s2 = Settings()
        assert s1 is s2
    
    def test_settings_has_openai_config(self):
        """Settings sollte OpenAI-Konfiguration haben"""
        assert hasattr(settings, 'openai_api_key')
        assert hasattr(settings, 'openai_model')
        assert hasattr(settings, 'openai_timeout')
        assert hasattr(settings, 'openai_max_tokens')
    
    def test_settings_default_model(self):
        """Standard-Modell sollte gpt-4o-mini sein"""
        assert settings.openai_model == 'gpt-4o-mini'
    
    def test_is_openai_configured_false_without_key(self):
        """is_openai_configured sollte False sein ohne API Key"""
        with patch.dict('os.environ', {}, clear=True):
            with patch('src.settings.load_dotenv'):  # Mock load_dotenv
                # Neue Instanz erzwingen durch Zurücksetzen des Singleton
                Settings._instance = None
                s = Settings()
                assert not s.is_openai_configured
    
    def test_get_openai_config_raises_without_key(self):
        """get_openai_config sollte ValueError werfen ohne API Key"""
        with patch.dict('os.environ', {}, clear=True):
            with patch('src.settings.load_dotenv'):  # Mock load_dotenv
                # Neue Instanz erzwingen durch Zurücksetzen des Singleton
                Settings._instance = None
                s = Settings()
                with pytest.raises(ValueError, match="nicht konfiguriert"):
                    s.get_openai_config()


class TestAIProfileService:
    """Tests für AIProfileService"""
    
    def test_service_requires_api_key(self):
        """Service sollte ConfigError werfen ohne API Key"""
        with patch('src.ai_service.settings') as mock_settings:
            mock_settings.is_openai_configured = False
            
            with pytest.raises(AIProfileConfigError, match="nicht konfiguriert"):
                AIProfileService()
    
    @patch('src.ai_service.settings')
    @patch('src.ai_service.OpenAI')
    def test_service_initialization_with_key(self, mock_openai, mock_settings):
        """Service sollte initialisiert werden mit API Key"""
        mock_settings.is_openai_configured = True
        mock_settings.get_openai_config.return_value = {
            'api_key': 'test-key',
            'model': 'gpt-4o-mini',
            'timeout': 30,
            'max_tokens': 500
        }
        
        service = AIProfileService()
        
        assert service.model == 'gpt-4o-mini'
        assert service.max_tokens == 500
    
    @patch('src.ai_service.settings')
    @patch('src.ai_service.OpenAI')
    def test_profile_values_are_clamped_to_range(self, mock_openai, mock_settings):
        """Profil-Werte sollten auf den erlaubten Bereich begrenzt werden"""
        import warnings
        from unittest.mock import MagicMock
        
        # Settings mocken
        mock_settings.is_openai_configured = True
        mock_settings.get_openai_config.return_value = {
            'api_key': 'test-key',
            'model': 'gpt-4o-mini',
            'timeout': 30,
            'max_tokens': 500
        }
        
        # OpenAI Client mocken mit Response außerhalb des Bereichs
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"O": 20, "C": -20, "E": 14, "A": 0, "N": -14}'
        mock_client_instance = MagicMock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance
        
        service = AIProfileService()
        
        # Test mit 7 Tests (max_value = 14)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            profile = service.get_ideal_profile(
                breed="Test",
                age_years=3,
                age_months=0,
                gender="Rüde",
                intended_use="Test",
                test_count=7
            )
            
            # Prüfe dass Werte geclampt wurden
            assert profile['O'] == 14, "O sollte auf 14 geclampt werden (war 20)"
            assert profile['C'] == -14, "C sollte auf -14 geclampt werden (war -20)"
            assert profile['E'] == 14, "E sollte unverändert 14 bleiben"
            assert profile['A'] == 0, "A sollte unverändert 0 bleiben"
            assert profile['N'] == -14, "N sollte unverändert -14 bleiben"
            
            # Prüfe dass Warnungen ausgegeben wurden
            # 2 Warnungen für Clamping (O, C) + 1 Warnung für Extremwerte = 3 total
            assert len(w) >= 2, f"Sollte mindestens 2 Warnungen ausgeben, erhielt {len(w)}"
            
            # Prüfe dass Clamping-Warnungen vorhanden sind
            clamping_warnings = [warning for warning in w if "außerhalb des erlaubten Bereichs" in str(warning.message)]
            assert len(clamping_warnings) == 2, "Sollte 2 Clamping-Warnungen für O und C haben"
            
            # Prüfe dass Extremwert-Warnung vorhanden ist
            extreme_warnings = [warning for warning in w if "Extremwerte" in str(warning.message)]
            assert len(extreme_warnings) >= 1, "Sollte Warnung für zu viele Extremwerte haben"
        mock_openai.assert_called_once()
