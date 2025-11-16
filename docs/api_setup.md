# OpenAI API Konfiguration

## Was macht die KI?

Die KI generiert **IDEAL-Profile** basierend auf:
- **Rasse** (z.B. Border Collie, Golden Retriever)
- **Alter** (Welpe, erwachsen, Senior)
- **Geschlecht** (Rüde/Hündin)
- **Einsatzgebiet** (Therapiehund, Rettungshund, Familienhund, etc.)

💡 Das Idealprofil zeigt die **optimalen OCEAN-Werte**, die ein Hund für seine Aufgabe haben sollte.
Beispiel: Therapiehund benötigt hohe Verträglichkeit (A+) und niedrige Nervosität (N-).

## Setup-Anleitung

1. **Kopiere `.env.example` zu `.env`:**
   ```bash
   cp .env.example .env
   ```

2. **Trage deinen OpenAI API Key ein:**
   - Öffne `.env` in einem Texteditor
   - Ersetze `your-api-key-here` mit deinem echten API Key
   - Dein Key findest du hier: https://platform.openai.com/api-keys

3. **Fertig!** Die Anwendung nutzt nun automatisch die API.

## Empfohlenes Modell

Für **~30 Anfragen pro Jahr** empfehlen wir **gpt-4o-mini**:
- ✅ Kostengünstig (~$0.01/Jahr bei 30 Anfragen)
- ✅ Schnell
- ✅ Ausreichend qualitativ für OCEAN-Profil-Generierung

## Sicherheit

⚠️ **Wichtig:** Die `.env` Datei ist in `.gitignore` und wird **nicht** ins Repository commited.
Dein API Key bleibt lokal und sicher.

## Fehlerbehandlung

Falls die API nicht erreichbar ist, werden die KI-Features automatisch deaktiviert.
Die Anwendung läuft weiter mit manueller Fragebogen-Eingabe.
