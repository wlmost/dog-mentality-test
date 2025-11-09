# OCEAN-Analyse & Visualisierung

## Überblick

Die OCEAN-Analyse berechnet aus den Testergebnissen einer Testsession die Werte für die fünf OCEAN-Persönlichkeitsdimensionen und visualisiert sie in einem Radardiagramm.

## OCEAN-Dimensionen

- **O**penness (Offenheit für Erfahrungen)
- **C**onscientiousness (Gewissenhaftigkeit)
- **E**xtraversion (Extraversion)
- **A**greeableness (Verträglichkeit)
- **N**euroticism (Neurotizismus)

## Architektur

### OceanAnalyzer (`src/ocean_analyzer.py`)

**Zweck:** Berechnung der OCEAN-Scores aus Testergebnissen

**Eingabe:**
- `TestSession`: Enthält alle Testergebnisse mit Scores
- `TestBattery`: Enthält OCEAN-Dimensionszuordnung für jeden Test

**Ausgabe:**
- `OceanScores`: Dataclass mit Summen und Counts pro Dimension

**Funktionsweise:**
```python
analyzer = OceanAnalyzer(session, battery)
scores = analyzer.calculate_ocean_scores()

print(f"Openness: {scores.openness} (aus {scores.openness_count} Tests)")
# Durchschnitt optional verfügbar:
averages = scores.get_averages()
print(f"Openness Durchschnitt: {averages['openness']:.2f}")
```

**Design-Entscheidung: Summierung statt Durchschnitt**

Die primären Werte sind **Summenwerte**, nicht Durchschnitte. Grund:

- Bei unterschiedlicher Anzahl Tests pro Dimension wäre der Durchschnitt irreführend
- Beispiel: 10 Tests für Openness vs. 2 Tests für Neuroticism
- Der Summenwert zeigt die "Gesamtausprägung" über alle Tests
- Durchschnitt ist optional über `get_averages()` verfügbar

**Beispiel-Szenario:**

```python
# Testbatterie mit unterschiedlicher Verteilung
# - 5 Tests für Openness
# - 2 Tests für Conscientiousness
# - 1 Test für Extraversion
# - 1 Test für Agreeableness
# - 1 Test für Neuroticism

# Ergebnisse:
# Openness: [2, 1, 2, -1, 1] → Summe: 5, Count: 5, Avg: 1.0
# Conscientiousness: [-1, 2] → Summe: 1, Count: 2, Avg: 0.5
# Extraversion: [2] → Summe: 2, Count: 1, Avg: 2.0

# Der Summenwert (5 für Openness) zeigt die Gesamtausprägung
# Der Durchschnitt (1.0) wäre bei Vergleich mit Extraversion (Avg: 2.0) irreführend
```

### OceanRadarChart (`src/ocean_chart.py`)

**Zweck:** Visualisierung der OCEAN-Scores als Radardiagramm

**Technologie:** PySide6.QtCharts (native Qt-Charts, kein Matplotlib)

**Vorteile von QtCharts:**
- Native Integration in Qt-GUI
- Bessere Performance
- Konsistentes Look & Feel
- Touch-Support
- Keine zusätzlichen Dependencies

**Komponenten:**
- `QPolarChart`: Basis-Chart für Polar-Koordinaten
- `QAreaSeries`: Gefüllter Bereich für Radar
- `QValueAxis`: Achsen für Kategorien (Dimensionen) und Werte (Scores)

**Beispiel:**
```python
from src.ocean_chart import OceanRadarChart

scores = OceanScores(
    openness=3, conscientiousness=-1, extraversion=2,
    agreeableness=0, neuroticism=-2
)

chart_widget = OceanRadarChart(scores)
chart_widget.show()

# Chart kann aktualisiert werden:
new_scores = OceanScores(openness=5, ...)
chart_widget.update_scores(new_scores)
```

**Visuelle Eigenschaften:**
- Farbe: Blau (#3498db) mit 70% Transparenz
- Dynamische Achsen-Skalierung (Min/Max aus Daten + Padding)
- Geschlossene Polygon-Form
- Legende am unteren Rand

### GUI-Integration (`src/main_window.py`)

**Button:** "Radardiagramm erstellen" im Auswertungs-Tab

**Workflow:**
1. Prüfung: Session mit Testergebnissen vorhanden?
2. Prüfung: Testbatterie geladen?
3. `OceanAnalyzer` erstellen und Scores berechnen
4. `OceanRadarChart` erstellen mit berechneten Scores
5. Placeholder im Auswertungs-Tab ersetzen
6. Info-Dialog mit Anzahl Tests pro Dimension

**Code:**
```python
def _show_ocean_plot(self):
    # Validierung...
    
    analyzer = OceanAnalyzer(self._current_session, self._current_battery)
    scores = analyzer.calculate_ocean_scores()
    
    chart_widget = OceanRadarChart(scores)
    
    # Container-Layout aktualisieren
    layout = self._chart_container.layout()
    # Altes Widget entfernen...
    layout.addWidget(chart_widget)
```

## Alternativen & Entscheidungen

### Warum QtCharts statt Matplotlib?

**Matplotlib:**
- ✅ Sehr flexibel und mächtig
- ✅ Viele Plot-Typen
- ❌ Schwere Dependency (~50 MB)
- ❌ Schlechte Qt-Integration (benötigt matplotlib.backends)
- ❌ Langsamere Performance bei Interaktion

**QtCharts:**
- ✅ Native Qt-Integration
- ✅ Bereits in PySide6 enthalten
- ✅ Bessere Performance
- ✅ Konsistentes UI
- ❌ Weniger Plot-Typen (aber ausreichend für OCEAN)

**Entscheidung:** QtCharts für bessere Integration

### Summenwerte vs. Durchschnitt

**Summenwerte (gewählt):**
- ✅ Zeigt Gesamtausprägung über alle Tests
- ✅ Vermeidet Verzerrung bei unterschiedlicher Testanzahl
- ✅ Intuitiver bei vielen Tests pro Dimension
- ❌ Nicht direkt vergleichbar bei sehr unterschiedlicher Testanzahl

**Durchschnitt:**
- ✅ Normalisiert auf Test-Anzahl
- ❌ Kann bei wenigen Tests irreführend sein
- ❌ Verliert Information über Anzahl der Tests

**Entscheidung:** Summenwerte als Primärmetrik, Durchschnitt optional über `get_averages()`

### Skalierung der Radar-Achsen

**Dynamische Skalierung (gewählt):**
- Achsen-Range basiert auf Min/Max der Daten
- +1 Padding für bessere Visualisierung
- Beispiel: Scores [-2, -1, 0, 2, 3] → Achse: [-3, 4]

**Fixe Skalierung:**
- Achse immer z.B. [-10, +10]
- ❌ Verschwendet Platz bei kleinen Werten
- ❌ Kann bei großen Werten zu klein sein

**Entscheidung:** Dynamische Skalierung für optimale Darstellung

## Tests

### test_ocean_analyzer.py (9 Tests)

- Analyzer-Erstellung (mit/ohne Battery)
- Score-Berechnung (alle Dimensionen, einzelne Dimension, leer)
- Count-Validierung
- Durchschnitts-Berechnung
- Fehlerbehandlung (ohne Battery)

### test_ocean_chart.py (12 Tests)

- Chart-Erstellung
- Chart-Typ-Validierung (QPolarChart)
- Daten-Series (AreaSeries)
- Update-Funktionalität
- Edge-Cases (alle 0, alle negativ, alle positiv, gemischt)

**Gesamt:** 21 neue Tests für OCEAN-Analyse

## Nutzung in der Anwendung

1. **Testbatterie importieren:** Excel-Datei mit OCEAN-Dimensionszuordnung
2. **Stammdaten erfassen:** Besitzer & Hund
3. **Tests durchführen:** Scores in Tabelle eintragen
4. **Auswertungs-Tab öffnen**
5. **Button "Radardiagramm erstellen" klicken**
6. **Radardiagramm wird angezeigt**

## Erweiterungsmöglichkeiten

### Export des Radardiagramms
- Chart als PNG/PDF exportieren
- Integration in bestehende PDF/Excel-Exporte

### Vergleichswerte
- Durchschnittswerte aus mehreren Sessions
- Normwerte aus Datenbank
- Vergleich zwischen Hunden

### Zeitliche Entwicklung
- Mehrere Sessions pro Hund
- Liniendiagramm über Zeit
- Trend-Analyse

### Detailansicht pro Dimension
- Drill-Down auf einzelne Tests
- Balkendiagramm mit einzelnen Test-Scores
- Tooltip mit Testbeschreibung

## Dateien

```
src/
├── ocean_analyzer.py          # OCEAN-Score-Berechnung
├── ocean_chart.py             # Radardiagramm-Visualisierung
└── main_window.py             # GUI-Integration

tests/
├── test_ocean_analyzer.py     # 9 Tests für Analyzer
└── test_ocean_chart.py        # 12 Tests für Chart

docs/
├── concept_ocean_analyse.md   # Initiales Konzept (7 Punkte)
└── ocean_analysis.md          # Diese Dokumentation
```

## Erfolgs-Kriterien ✅

- [x] OceanAnalyzer berechnet alle 5 Dimensionen
- [x] Summenwerte und Counts werden korrekt gespeichert
- [x] Durchschnitt optional verfügbar
- [x] Radardiagramm wird erstellt
- [x] Dynamische Achsen-Skalierung funktioniert
- [x] GUI-Integration in MainWindow
- [x] Alle Tests bestehen (134 gesamt)
- [x] Fehlerbehandlung (keine Session, keine Battery)
- [x] Info-Dialog mit Testanzahl pro Dimension
