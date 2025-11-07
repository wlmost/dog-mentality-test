# Modul 1: Stammdaten-Erfassung

## 📌 Sinn & Zweck

Die Stammdaten-Erfassung bildet die Grundlage für alle weiteren Tests und Analysen. Sie erfasst die wesentlichen Informationen über den Hund und seinen Halter, die für die tierpsychologische Bewertung relevant sind.

**Warum diese Funktionalität?**
- Eindeutige Identifikation des Hundes
- Kontextinformationen für die Testauswertung (Alter, Geschlecht)
- Nachvollziehbarkeit bei mehreren Tests über Zeit
- Professionelle Dokumentation für Hundeschulen

---

## 🔀 Alternativen & Design-Entscheidungen

### Datenmodell

**Gewählt:** Dataclass mit Validierung im `__post_init__`
- ✅ Klare Struktur, typsicher
- ✅ Automatische Validierung bei Instanziierung
- ✅ Einfache JSON-Serialisierung

**Alternative:** Pydantic Models
- ❌ Zusätzliche Dependency
- ✅ Noch mächtigere Validierung
- → Für diesen Umfang nicht notwendig

### GUI-Framework

**Gewählt:** PySide6
- ✅ Native Look & Feel
- ✅ Professionell, wartbar
- ✅ LGPL-Lizenz (kommerziell nutzbar)

**Alternative:** Tkinter
- ❌ Veraltetes Design
- ❌ Schwierigere Anpassung
- ✅ In Python enthalten

**Alternative:** Web-GUI (Flask/Django + HTML/CSS)
- ❌ Mehr Komplexität
- ❌ Erfordert Browser
- ✅ Plattformunabhängig

### Validierung

**Gewählt:** Sofortige Validierung im Datenmodell
- ✅ Fehler werden früh erkannt
- ✅ Wiederverwendbar (nicht nur GUI)
- ✅ Klare Fehlermeldungen

**Alternative:** Nur GUI-Validierung
- ❌ Validierungslogik in Präsentationsschicht
- ❌ Schwerer testbar

---

## ⚙️ Funktionsweise

### Architektur

```
┌─────────────────────┐
│  MasterDataForm     │  ← GUI (PySide6)
│  (Präsentation)     │
└──────────┬──────────┘
           │
           │ verwendet
           │
           ▼
┌─────────────────────┐
│  DogData            │  ← Datenmodell
│  (Business Logic)   │
└─────────────────────┘
```

### Datenfluss

1. **Benutzereingabe** → Felder im Formular
2. **Speichern-Klick** → `save_data()` wird aufgerufen
3. **Validierung** → `DogData.__post_init__()` prüft Daten
4. **Signal** → `data_saved` Signal mit DogData-Objekt
5. **Erfolgsmeldung** → QMessageBox + Formular zurücksetzen

### Validierungsregeln

| Feld          | Regel                           | Fehlermeldung                      |
|---------------|---------------------------------|------------------------------------|
| Haltername    | Nicht leer (nach trim)          | "Name des Halters darf nicht..."   |
| Hundename     | Nicht leer (nach trim)          | "Name des Hundes darf nicht..."    |
| Alter         | Integer, >= 0                   | "Alter muss ein Integer sein"      |
| Geschlecht    | "Rüde" oder "Hündin"            | (Dropdown, keine Fehlerquelle)     |
| Kastriert     | Boolean                         | (Checkbox, keine Fehlerquelle)     |

### UX-Design-Prinzipien

1. **Visuelle Hierarchie**
   - Titel (16pt, bold)
   - Untertitel (grau, kleiner)
   - Gruppierungen (QGroupBox)

2. **Whitespace**
   - 30px Margins
   - 20px Spacing zwischen Gruppen
   - 15px Spacing innerhalb Forms

3. **Feedback**
   - Placeholder-Texte ("z.B. Bello")
   - Suffixe ("Jahre")
   - Erfolgs-/Fehlermeldungen

4. **Konsistenz**
   - Einheitliche Button-Höhe (35px)
   - Einheitliche Input-Höhe (30px)
   - Farbschema (Grün für Primäraktion)

---

## 💻 Code-Beispiele

### Datenmodell verwenden

```python
from src.models import DogData, Gender

# Hund erstellen
dog = DogData(
    owner_name="Max Mustermann",
    dog_name="Bello",
    age=5,
    gender=Gender.MALE,
    neutered=True
)

# JSON-Export
data_dict = dog.to_dict()
# {'owner_name': 'Max Mustermann', 'dog_name': 'Bello', ...}

# JSON-Import
dog2 = DogData.from_dict(data_dict)
```

### Formular in eigener Anwendung nutzen

```python
from PySide6.QtWidgets import QApplication
from src.master_data_form import MasterDataForm

app = QApplication([])
form = MasterDataForm()

# Signal verbinden
def handle_save(dog_data):
    print(f"Gespeichert: {dog_data.dog_name}")
    
form.data_saved.connect(handle_save)
form.show()
app.exec()
```

### Formular programmatisch ausfüllen (Tests)

```python
from src.master_data_form import MasterDataForm
from src.models import DogData, Gender

form = MasterDataForm()

# Testdaten
test_dog = DogData(
    owner_name="Anna Schmidt",
    dog_name="Luna",
    age=3,
    gender=Gender.FEMALE,
    neutered=False
)

# Formular ausfüllen
form.fill_form(test_dog)

# Speichern simulieren
form.save_button.click()
```

---

## 🧪 Tests

### Ausführen

```bash
# Nur Model-Tests
pytest tests/test_models.py -v

# Nur GUI-Tests
pytest tests/test_master_data_form.py -v

# Alle Tests
pytest -v
```

### Test-Coverage

- **Datenmodell:** 7 Tests (Validierung, Serialisierung)
- **GUI:** 11 Tests (Formular-Funktionen, automatisches Ausfüllen)
- **Gesamt:** 18 Tests für Modul 1

### Demo starten

```bash
python src/demo_master_data.py
```

---

## 📊 Dateistruktur

```
src/
├── models.py              # Datenmodell (DogData, Gender)
├── master_data_form.py    # GUI-Formular
└── demo_master_data.py    # Demo-Anwendung

tests/
├── test_models.py              # Model-Tests
└── test_master_data_form.py    # GUI-Tests
```

---

## 🔗 Schnittstellen

### Öffentliche API

**DogData:**
- `__init__(owner_name, dog_name, age, gender, neutered)`
- `to_dict() -> dict`
- `from_dict(data: dict) -> DogData`

**MasterDataForm:**
- `data_saved: Signal(DogData)` - Signal bei erfolgreichem Speichern
- `fill_form(dog_data: DogData)` - Formular ausfüllen
- `reset_form()` - Formular zurücksetzen

### Integration mit anderen Modulen

Modul 1 liefert `DogData`-Objekte, die von folgenden Modulen genutzt werden:
- **Modul 3:** Speicherung (JSON)
- **Modul 4:** Export (CSV/Excel)
- **Modul 5:** Visualisierung (Radar-Diagramm Header)

---

## ✅ Status

**Abgeschlossen:** ✓
- Datenmodell mit Validierung
- GUI mit modernem UX-Design
- Automatisierte Tests (18 Tests, alle bestanden)
- Demo-Anwendung
- Dokumentation
