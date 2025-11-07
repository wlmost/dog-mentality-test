# Dog Mentality Test Application

**Tierpsychologische Testdiagnostik auf Basis des OCEAN-Modells für Hunde**

The dog-mentality-test is used to conduct personality tests on dogs with graphical evaluation. This application is designed to enable personality tests to be stored digitally in your own customer database.

---

## 📋 Projektübersicht

Diese Anwendung unterstützt Hundeschulen bei der systematischen Erfassung und Auswertung tierpsychologischer Tests nach dem **OCEAN-Modell** (Big Five Persönlichkeitsmerkmale für Hunde).

### Module

1. **Stammdaten-Erfassung** – Halter- und Hundedaten
2. **Testbatterie-Import** – Excel-Import von Testdefinitionen
3. **Testdaten-Eingabe** – GUI-Tabelle zur Werteingabe
4. **Export-Funktion** – CSV/Excel-Export
5. **OCEAN-Analyse** – Visualisierung als Radar-Diagramm

---

## 🚀 Installation

### Voraussetzungen

- Python 3.12+ 
- Git

### Setup

1. **Repository klonen:**
   ```bash
   git clone https://github.com/wlmost/dog-mentality-test.git
   cd dog-mentality-test
   ```

2. **Virtuelle Umgebung erstellen:**
   ```bash
   python -m venv venv
   ```

3. **Virtuelle Umgebung aktivieren:**
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux/macOS:**
     ```bash
     source venv/bin/activate
     ```

4. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🎯 Verwendung

### Hauptanwendung starten

```bash
python main.py
```

Die Hauptanwendung bietet:
- **Tab-basierte Oberfläche** für übersichtliche Navigation
  - Tab 1: Stammdaten (Hund/Halter)
  - Tab 2: Test-Durchführung (vollständige Test-Tabelle)
  - Tab 3: Auswertung (OCEAN-Plot, Statistik)
- **Menüleiste** mit allen Funktionen
- **Automatischer Tab-Wechsel** nach Aktionen
- **Import/Export** von Daten
- **Session-Management** mit Warnung vor Datenverlust

### Workflow

1. **Testbatterie importieren:**
   - Menü: Import → Testbatterie (Excel)
   - Datei auswählen: `data/Testbatterie_OCEAN.xlsx`
   - Die Tests werden sofort im Tab "Test-Durchführung" angezeigt

2. **Stammdaten eingeben:**
   - Im Tab "Stammdaten": Halter- und Hundedaten eingeben
   - "Speichern" klicken
   - **Automatischer Wechsel** zum Tab "Test-Durchführung"

3. **Tests durchführen:**
   - Im Tab "Test-Durchführung": Scores (-2 bis +2) eingeben
   - Notizen für jeden Test hinzufügen
   - Fortschritt wird automatisch angezeigt

4. **Session speichern:**
   - Menü: Datei → Speichern (oder Strg+S)
   - JSON-Datei wird im `data/` Ordner gespeichert

5. **Auswertung anzeigen:**
   - Tab "Auswertung" wechseln
   - Button "Statistik anzeigen" für Übersicht
   - OCEAN-Radardiagramm (in Entwicklung)

6. **Session laden:**
   - Menü: Datei → Öffnen (oder Strg+O)
   - JSON-Datei auswählen
   - Alle Daten werden wiederhergestellt

### Demo-Anwendungen

```bash
# Stammdaten-Demo
python run_demo.py

# Test-Tabellen-Demo
python run_test_data_demo.py

# Excel-Import-Demo
python -m src.demo_excel_import
```
     ```

4. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧪 Tests ausführen

```bash
pytest
```

---

## 📦 Projektstruktur

```
dog-mentality-test/
├── src/                    # Quellcode
├── tests/                  # Automatisierte Tests
├── docs/                   # Dokumentation
├── data/                   # Daten (JSON, Excel-Templates)
├── requirements.txt        # Python-Dependencies
├── pytest.ini              # Pytest-Konfiguration
└── README.md               # Projektdokumentation
```

---

## 🎨 Entwicklungsprinzipien

- **Clean Code** – Lesbar, wartbar, idiomatisch
- **Test Driven Development (TDD)** – Tests zuerst
- **Moderne UX** – Freundliches, aufgeräumtes Design

---

## 📄 Lizenz

Siehe [LICENSE](LICENSE)

---

## 👤 Autor

Wolfgang Leidinger (@wlmost)
