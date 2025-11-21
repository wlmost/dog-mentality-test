# Distribution Checkliste
## Dog Mentality Test - Windows Executable

### Vor der Verteilung prüfen

- [ ] **Build erfolgreich**: `dist/DogMentalityTest/DogMentalityTest.exe` existiert
- [ ] **Python DLL vorhanden**: `dist/DogMentalityTest/python312.dll` existiert
- [ ] **Lokaler Test**: Programm startet auf Entwicklungssystem
- [ ] **Clean-System Test**: Test auf System ohne Python-Installation

### Dateien in Distribution

```
DogMentalityTest/
├── DogMentalityTest.exe       ⚠️ ERFORDERLICH - Hauptprogramm
├── python312.dll               ⚠️ ERFORDERLICH - Python Runtime
├── .env.example                📝 OPTIONAL - KI-Konfigurations-Vorlage
├── _internal/                  ⚠️ ERFORDERLICH - Alle Libraries
│   ├── PySide6/               (Qt Framework)
│   ├── numpy/                 (Numerik)
│   ├── pandas/                (Datenverarbeitung)
│   ├── plotly/                (Charts)
│   ├── openai/                (KI-Integration)
│   └── [...weitere]
└── README.txt                  📝 Erstelle aus DISTRIBUTION_README.txt
```

### Distribution vorbereiten

1. **Kompletten Ordner kopieren**:
   ```
   dist/DogMentalityTest/  →  Ziel-Ordner
   ```

2. **README hinzufügen**:
   ```
   copy DISTRIBUTION_README.txt dist\DogMentalityTest\README.txt
   ```

3. **Optional: ZIP erstellen**:
   ```powershell
   Compress-Archive -Path dist\DogMentalityTest -DestinationPath DogMentalityTest-v1.0.0-Win64.zip
   ```

### Test auf Zielsystem

1. **Entpacken** (falls ZIP)
2. **Doppelklick** auf `DogMentalityTest.exe`
3. **Erwartetes Verhalten**:
   - Programm startet ohne Fehlermeldung
   - Hauptfenster erscheint
   - Menü "Datei" → "Testbatterie importieren" funktioniert

### Häufige Probleme & Lösungen

| Problem | Ursache | Lösung |
|---------|---------|--------|
| "python312.dll fehlt" | DLL nicht kopiert | Neuesten Build verwenden (mit DLL) |
| "Datei nicht gefunden" | Nur .exe kopiert | Kompletten Ordner inkl. _internal/ kopieren |
| SmartScreen-Warnung | Unsignierte EXE | "Weitere Informationen" → "Trotzdem ausführen" |
| Antivirus blockiert | False-Positive | Ausnahme hinzufügen oder signieren |
| Langsamer Start | Erststart | Normal - Libraries werden entpackt (~5-10 Sek.) |

### Größe & System-Anforderungen

- **Größe**: ~250-400 MB (komplett)
- **OS**: Windows 10/11 64-bit
- **RAM**: Mindestens 4 GB (8 GB empfohlen)
- **Festplatte**: 500 MB frei
- **Internet**: Nur für KI-Features erforderlich

### KI-Features aktivieren (optional)

Auf Zielsystem `.env` Datei erstellen:
```
DogMentalityTest/.env
```

Inhalt:
```env
OPENAI_API_KEY=sk-...ihr-key...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30
OPENAI_MAX_TOKENS=500
```

### Code-Signing (optional, für professionelle Verteilung)

Um SmartScreen-Warnung zu vermeiden:
1. Code-Signing Zertifikat besorgen (z.B. Sectigo, DigiCert)
2. EXE signieren: `signtool sign /f cert.pfx /p password /tr http://timestamp.digicert.com DogMentalityTest.exe`
3. Kostet ~$100-300/Jahr

### Support-Informationen für Endnutzer

Bei Problemen sollten Nutzer mitteilen:
- Windows-Version (Win + R → `winver`)
- Fehlermeldung (Screenshot)
- Event Log Einträge (Ereignisanzeige → Windows-Protokolle → Anwendung)

### Versions-Tracking

**Aktuelle Version**: 1.0.0
**Build-Datum**: [Datum eintragen]
**Changelog**: Siehe CHANGELOG.md (falls vorhanden)
