# Windows Build Anleitung
# Dog Mentality Test - Executable für Windows 11 64-bit

⏱️ **Build-Dauer**: Erster Build ca. 5-10 Minuten (abhängig von Hardware)

## Voraussetzungen
- Python 3.11+ installiert
- Virtuelle Umgebung aktiviert (`venv\Scripts\activate`)
- Alle Abhängigkeiten installiert (`pip install -r requirements.txt`)

## Build durchführen

### Methode 1: Automatischer Build (empfohlen)
```batch
build_windows.bat
```

### Methode 2: Manueller Build
```batch
# Virtuelle Umgebung aktivieren
venv\Scripts\activate

# PyInstaller installieren (falls nicht vorhanden)
pip install pyinstaller

# Build durchführen
pyinstaller --clean build_windows.spec
```

## Ergebnis
Nach erfolgreichem Build befindet sich die Anwendung in:
```
dist/DogMentalityTest/
├── DogMentalityTest.exe    # Hauptprogramm
├── data/                   # Beispiel-Daten (falls vorhanden)
├── .env.example            # Konfigurations-Vorlage
└── [weitere Bibliotheken]
```

## Anwendung starten
1. Navigiere zu `dist/DogMentalityTest/`
2. Erstelle `.env` Datei mit OpenAI API Key (optional)
3. Starte `DogMentalityTest.exe`

## Verteilung
Der komplette `dist/DogMentalityTest/` Ordner kann kopiert und verteilt werden.
Keine Python-Installation beim Endnutzer erforderlich!

## Konfiguration (.env)
Für KI-Features (optional):
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30
OPENAI_MAX_TOKENS=500
```

## Hinweise
- **Größe**: Die Anwendung ist ca. 250-400 MB groß (inkl. Python Runtime & Qt)
- **Erststart**: Kann etwas länger dauern (Bibliotheken werden entpackt)
- **Antivirus**: Manche Antivirus-Programme blockieren PyInstaller-Builds, als Ausnahme hinzufügen
- **Windows Defender**: Evtl. SmartScreen-Warnung bei erstem Start (normal bei unsignierten Apps)

## Troubleshooting

### Build schlägt fehl
- Stelle sicher, dass alle Dependencies installiert sind: `pip install -r requirements.txt`
- Lösche alte Builds: `rmdir /s /q build dist`
- Prüfe Python Version: `python --version` (sollte 3.11+)

### Anwendung startet nicht
- Starte über Kommandozeile für Error-Meldungen: `dist\DogMentalityTest\DogMentalityTest.exe`
- Prüfe ob alle DLLs vorhanden sind
- Windows Event Log prüfen

### Import-Fehler
Fehlende Module in `build_windows.spec` unter `hiddenimports` ergänzen

## Performance-Optimierung
Für kleinere Executable-Größe:
- Entferne nicht benötigte Dependencies
- UPX-Kompression nutzen (bereits aktiviert)
- Einzelne EXE statt Folder: In spec-Datei `EXE(..., onefile=True)`
