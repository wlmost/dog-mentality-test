"""
Settings und Konfiguration für die Anwendung

Lädt Umgebungsvariablen aus .env Datei für API-Keys und andere Konfigurationen.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Settings:
    """
    Zentrale Konfiguration der Anwendung
    
    Lädt Einstellungen aus .env Datei und stellt sie als Singleton zur Verfügung.
    """
    
    _instance: Optional['Settings'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # .env Datei laden (falls vorhanden)
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        # OpenAI Konfiguration
        self.openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
        self.openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.openai_timeout: int = int(os.getenv('OPENAI_TIMEOUT', '30'))
        self.openai_max_tokens: int = int(os.getenv('OPENAI_MAX_TOKENS', '500'))
        
        # Letzter Battery-Pfad (für schnelleren Zugriff)
        self.last_battery_path: Optional[str] = os.getenv('LAST_BATTERY_PATH')
        
        self._initialized = True
    
    @property
    def is_openai_configured(self) -> bool:
        """Prüft ob OpenAI API Key konfiguriert ist"""
        return self.openai_api_key is not None and len(self.openai_api_key.strip()) > 0 and self.openai_api_key != 'your-api-key-here'
    
    def get_openai_config(self) -> dict:
        """
        Gibt OpenAI-Konfiguration als Dictionary zurück
        
        Returns:
            dict mit api_key, model, timeout, max_tokens
            
        Raises:
            ValueError: Wenn API Key nicht konfiguriert ist
        """
        if not self.is_openai_configured:
            raise ValueError(
                "OpenAI API Key ist nicht konfiguriert. "
                "Bitte erstelle eine .env Datei mit OPENAI_API_KEY. "
                "Siehe .env.example für Details."
            )
        
        return {
            'api_key': self.openai_api_key,
            'model': self.openai_model,
            'timeout': self.openai_timeout,
            'max_tokens': self.openai_max_tokens
        }
    
    def save_last_battery_path(self, path: str):
        """
        Speichert letzten Battery-Pfad in .env Datei
        
        Args:
            path: Absoluter Pfad zur Battery-Datei
        """
        env_path = Path(__file__).parent.parent / '.env'
        
        # Prüfen ob .env existiert, sonst von .env.example kopieren
        if not env_path.exists():
            example_path = env_path.parent / '.env.example'
            if example_path.exists():
                with open(example_path, 'r', encoding='utf-8') as f:
                    example_content = f.read()
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write(example_content)
        
        # Existierende Zeilen lesen
        lines = []
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # LAST_BATTERY_PATH aktualisieren oder hinzufügen
        battery_line = f"LAST_BATTERY_PATH={path}\n"
        found = False
        
        for i, line in enumerate(lines):
            if line.startswith('LAST_BATTERY_PATH='):
                lines[i] = battery_line
                found = True
                break
        
        if not found:
            # Am Ende hinzufügen (nach Leerzeile falls keine vorhanden)
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            if lines and lines[-1].strip():  # Letzte Zeile nicht leer
                lines.append('\n')
            lines.append('# Letzter Battery-Pfad (automatisch gespeichert)\n')
            lines.append(battery_line)
        
        # Zurückschreiben
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Lokale Variable aktualisieren
        self.last_battery_path = path


# Singleton-Instanz
settings = Settings()
