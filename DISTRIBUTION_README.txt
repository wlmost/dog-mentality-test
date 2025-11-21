# Dog Mentality Test
## OCEAN Persönlichkeitsanalyse für Hunde

Version 1.0.0

---

## Schnellstart

1. **Programm starten**: Doppelklick auf `DogMentalityTest.exe`
2. **Testbatterie importieren**: Datei → Testbatterie importieren → Excel-Datei auswählen
3. **Stammdaten eingeben**: Name, Alter, Geschlecht des Hundes
4. **Tests durchführen**: Bewertungen (-2 bis +2) für jeden Test eingeben
5. **OCEAN-Analyse**: Automatische Berechnung der 5 Persönlichkeitsdimensionen
6. **Exportieren**: Ergebnisse als PDF oder Excel speichern

---

## KI-Features (optional)

Für erweiterte KI-Funktionen:

1. Erstelle Datei `.env` in diesem Ordner
2. Füge deinen OpenAI API-Key hinzu:
   ```
   OPENAI_API_KEY=sk-...dein-key...
   OPENAI_MODEL=gpt-4o-mini
   ```
3. KI-Buttons werden aktiviert:
   - **KI-Idealprofil laden**: Generiert optimales OCEAN-Profil für Einsatzzweck
   - **KI-Bewertung anzeigen**: Ausführliche Analyse aller 3 Profile

### API-Key erhalten
- Registrierung: https://platform.openai.com/
- Kosten: ca. $0.01 pro Jahr bei normalem Gebrauch (gpt-4o-mini)

---

## OCEAN-Dimensionen

Die "Big Five" der Persönlichkeitspsychologie:

- **O - Openness (Offenheit)**: Neugier, Lernbereitschaft
- **C - Conscientiousness (Gewissenhaftigkeit)**: Zuverlässigkeit, Selbstkontrolle  
- **E - Extraversion**: Geselligkeit, Aktivitätslevel
- **A - Agreeableness (Verträglichkeit)**: Freundlichkeit, Kooperation
- **N - Neuroticism (Neurotizismus)**: Emotionale Stabilität

Werte: -14 bis +14 (je nach Anzahl Tests)

---

## Fragebogen-Profil

Zusätzlich zum Test-Profil können Sie ein Fragebogen-Profil erfassen:

1. OCEAN-Analyse erstellen
2. Button "Fragebogen-Profil übernehmen" klicken
3. Erwartungen des Besitzers eingeben (-14 bis +14)
4. Chart zeigt alle 3 Profile (Test, Fragebogen, Ideal)

---

## Export-Funktionen

### PDF Export
- Stammdaten, Test-Ergebnisse, OCEAN-Chart
- Session-Notizen
- Professionell formatiert

### Excel Export
- Zwei Arbeitsblätter: Stammdaten & Ergebnisse
- OCEAN-Werte in separater Spalte
- Import in Statistik-Software möglich

---

## Session-Verwaltung

**Speichern**: Datei → Session speichern (`.json` Format)  
**Laden**: Datei → Session laden

Sessions enthalten:
- Stammdaten
- Test-Ergebnisse
- OCEAN-Scores
- KI-Profile (falls vorhanden)
- Notizen

---

## Technische Details

- **Betriebssystem**: Windows 11 64-bit (auch Windows 10 kompatibel)
- **Größe**: ca. 250-400 MB
- **Python**: Keine Installation erforderlich (enthält Runtime)
- **Internet**: Nur für KI-Features benötigt

---

## Fehlerbehebung

### Programm startet nicht
- Starte über Kommandozeile für Error-Meldungen
- Prüfe Windows Event Log
- Antivirus-Ausnahme hinzufügen

### SmartScreen-Warnung
- Normal bei unsignierten Programmen
- "Weitere Informationen" → "Trotzdem ausführen"

### KI-Features funktionieren nicht
- `.env` Datei korrekt angelegt?
- API-Key gültig?
- Internetverbindung aktiv?

---

## Support & Lizenz

**Version**: 1.0.0  
**Entwickelt mit**: Python 3.12, PySide6, OpenAI API  
**Lizenz**: Siehe LICENSE Datei

---

## Datenordner

- `data/`: Hier werden Sessions gespeichert (automatisch erstellt)
- Sessions bleiben erhalten bei Updates

---

**Viel Erfolg bei der Hundeanalyse! 🐕**
