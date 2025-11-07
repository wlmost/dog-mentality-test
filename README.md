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
