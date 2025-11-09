# Concept-Checkliste: Modul 5 - OCEAN-Analyse & Visualisierung

## 🎯 Ziel
Berechnung und Visualisierung der OCEAN-Persönlichkeitsdimensionen aus den Testergebnissen.

---

## 📋 Checkliste (5-7 Punkte)

### 1. **OCEAN-Analyzer Klasse** ✅
- **Zweck**: Berechnet die 5 Dimensionswerte aus den Scores
- **Input**: TestSession mit Results + TestBattery
- **Output**: Dictionary mit OCEAN-Werten (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism)
- **Logik**: 
  - Gruppiere Results nach OCEAN-Dimension
  - Summiere Scores pro Dimension
  - Optional: Normalisierung oder Durchschnitt

**Beispiel:**
```python
analyzer = OceanAnalyzer(session, battery)
scores = analyzer.calculate_ocean_scores()
# {'O': 5, 'C': -2, 'E': 3, 'A': 0, 'N': -1}
```

---

### 2. **Radardiagramm mit PySide6-Charts** ✅
- **Zweck**: Visualisiert die 5 OCEAN-Dimensionen als Polar/Spider-Chart
- **Library**: PySide6-Charts (QPolarChart)
- **Features**:
  - 5 Achsen für O, C, E, A, N (QValueAxis)
  - Ausgefüllte Fläche mit QAreaSeries
  - Beschriftungen für jede Achse
  - Native Qt-Integration (besser als matplotlib)

**Design:**
- Farbe: Blau (#3498db) mit Transparenz
- Gridlines für bessere Lesbarkeit
- Animation bei Anzeige (optional)
- Tooltip bei Hover

---

### 3. **QChartView-Widget** ✅
- **Zweck**: Native Qt-Chart-Darstellung
- **Klasse**: `QChartView` mit `QPolarChart`
- **Integration**: Ersetze Placeholder im Auswertungs-Tab
- **Vorteile gegenüber matplotlib**:
  - Bessere Performance
  - Native Qt-Look & Feel
  - Kein zusätzliches Canvas-Widget nötig
  - Touch-Unterstützung
- **Interaktivität**: 
  - Zoom/Pan mit Maus
  - Refresh-Button zum Neu-Berechnen
  - Export als PNG (optional)

---

### 4. **Datenvalidierung** ✅
- **Prüfungen**:
  - Sind genug Tests vorhanden? (Mind. 1 pro Dimension?)
  - Gibt es eine Battery mit OCEAN-Zuordnungen?
  - Sind Results vollständig?
- **Error-Handling**:
  - Zeige Warnung wenn Daten unvollständig
  - Deaktiviere Plot-Button bei fehlenden Daten

---

### 5. **Statistik-Anzeige** ✅
- **Zweck**: Textuelle Zusammenfassung der OCEAN-Werte
- **Inhalt**:
  - Tabelle: Dimension | Score | Anzahl Tests
  - Interpretation (optional): "Hoch", "Mittel", "Niedrig"
  - Gesamtanzahl Tests
- **Format**: QLabel oder QTextEdit mit HTML-Formatierung

---

### 6. **Tests für OCEAN-Analyzer** ✅
- **Unit Tests**:
  - Berechnung mit einfachen Beispieldaten
  - Alle 5 Dimensionen vertreten
  - Nur eine Dimension vertreten
  - Leere Session (Edge Case)
  - Ohne Battery
- **Erwartete Test-Abdeckung**: ~8-10 Tests

---

### 7. **GUI-Integration & Polishing** ✅
- **Auswertungs-Tab**:
  - Ersetze Placeholder durch MatplotlibCanvas
  - "Radardiagramm erstellen" Button → Berechnung + Plot
  - "Statistik anzeigen" Button → Textuelle Zusammenfassung
- **Layout**:
  - Plot nimmt Hauptbereich ein
  - Buttons am unteren Rand
  - Statusbar-Update bei Fehler/Erfolg

---

## 🔧 Technische Details

### Dependencies
```python
# QtCharts ist bereits in PySide6>=6.6.0 enthalten!
# Keine zusätzliche Installation nötig
```

### Imports
```python
from PySide6.QtCharts import (
    QChart, QChartView, QPolarChart,
    QValueAxis, QCategoryAxis,
    QLineSeries, QAreaSeries
)
```

### Datei-Struktur
```
src/
  ocean_analyzer.py      # OceanAnalyzer Klasse
  ocean_chart.py         # Radardiagramm mit QPolarChart
tests/
  test_ocean_analyzer.py # Unit Tests
```

---

## 🎨 Design-Entscheidungen

### Normalisierung?
**Option A: Summierung** (gewählt)
- Addiere alle Scores pro Dimension
- Einfach, direkt verständlich
- Range: -2n bis +2n (n=Anzahl Tests)

**Option B: Durchschnitt**
- Durchschnitt aller Scores pro Dimension
- Range: -2 bis +2
- Vergleichbarer zwischen Sessions

**Entscheidung:** Start mit Summierung, später optional Durchschnitt

### Radar-Skalierung?
- **Dynamisch**: Min/Max basierend auf Daten → **Gewählt**
- **Fest**: z.B. -10 bis +10

---

## 📊 Beispiel-Szenario

**Session mit 10 Tests:**
- Openness: 3 Tests → Scores: +2, +1, 0 → Summe: +3
- Conscientiousness: 2 Tests → Scores: -1, +2 → Summe: +1
- Extraversion: 2 Tests → Scores: +2, +1 → Summe: +3
- Agreeableness: 2 Tests → Scores: 0, -1 → Summe: -1
- Neuroticism: 1 Test → Score: -2 → Summe: -2

**Radardiagramm:**
```
        O (+3)
       /     \
  N(-2)       C(+1)
       \     /
        A(-1) - E(+3)
```

---

## ✅ Erfolgskriterien

1. ✅ OceanAnalyzer berechnet korrekte Werte
2. ✅ Radardiagramm wird korrekt angezeigt
3. ✅ GUI-Integration funktioniert ohne Fehler
4. ✅ Mindestens 8 Tests für OCEAN-Analyzer
5. ✅ Dokumentation in Markdown
6. ✅ Alle bestehenden Tests bleiben grün

---

## 🚀 Umsetzungsreihenfolge

1. **OceanAnalyzer** → Tests → Funktioniert isoliert
2. **Radardiagramm** → Funktioniert standalone
3. **MatplotlibCanvas** → Einbettung in GUI
4. **Integration** → MainWindow verbinden
5. **Polishing** → Fehlerbehandlung, Styling
6. **Dokumentation** → README + Code-Kommentare
