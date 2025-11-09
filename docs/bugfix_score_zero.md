# Bugfix: Score 0 wird nicht exportiert

## 🐛 Problem

**Symptom:** Testergebnisse mit Score 0 wurden nicht exportiert (weder Excel noch PDF).

**Ursache:** In `src/test_data_form.py` Zeile 295 wurde folgende Bedingung verwendet:
```python
if score != 0 or notes:
    result = TestResult(test_number=test_num, score=score, notes=notes)
    self._session.add_result(result)
```

**Warum war das falsch?**
- Score 0 bedeutet **neutrales Verhalten** und ist ein gültiger Wert im Bereich -2 bis +2
- Die Bedingung `score != 0` filterte Tests mit neutralem Verhalten heraus
- Nur Tests mit Notizen wurden trotzdem gespeichert

---

## ✅ Lösung

### 1. Session-Daten speichern (test_data_form.py, Zeile 295)

**Vorher:**
```python
# Nur speichern wenn Score != 0 (Standard)
if score != 0 or notes:
    result = TestResult(test_number=test_num, score=score, notes=notes)
    self._session.add_result(result)
```

**Nachher:**
```python
# Immer speichern - Score 0 ist ein valider Wert (neutrales Verhalten)
result = TestResult(test_number=test_num, score=score, notes=notes)
self._session.add_result(result)
```

### 2. Fortschrittsanzeige anpassen (test_data_form.py, Zeile 300)

**Problem:** Wenn alle Tests gespeichert werden, zeigt die Fortschrittsanzeige immer "X / X Tests"

**Lösung:** Fortschritt basiert nur auf Tests mit Score ≠ 0 (bearbeitete Tests)

**Vorher:**
```python
completed = self._session.get_completed_count()
```

**Nachher:**
```python
# Zähle nur Tests mit Score != 0 als "bearbeitet"
completed = sum(1 for result in self._session.results.values() if result.score != 0)
```

---

## 🧪 Tests

### Neue Tests hinzugefügt

**Excel-Export (test_excel_exporter.py):**
```python
def test_export_score_zero(self, tmp_path):
    """Test: Score 0 wird exportiert (neutrales Verhalten ist gültig)"""
    session.add_result(TestResult(test_number=1, score=0, notes="Neutral"))
    session.add_result(TestResult(test_number=2, score=0, notes=""))
    # ...
    assert ws.cell(row=4, column=4).value == 0
    assert ws.cell(row=5, column=4).value == 0
```

**PDF-Export (test_pdf_exporter.py):**
```python
def test_export_score_zero(self, tmp_path):
    """Test: Score 0 wird exportiert (neutrales Verhalten ist gültig)"""
    session.add_result(TestResult(test_number=1, score=0, notes="Neutral"))
    # ...
    assert "0" in text  # Score
```

**Bestehende Tests:** 
- `test_progress_update` wurde automatisch korrigiert (funktioniert weiterhin)

---

## 📊 Ergebnis

**Tests:** 113 passed (zuvor 111, +2 neue Tests)
- ✅ Excel-Exporter: 12 Tests (zuvor 11, +1)
- ✅ PDF-Exporter: 14 Tests (zuvor 13, +1)
- ✅ TestDataForm: 15 Tests (alle bestanden nach Anpassung)

**Verhalten:**
- ✅ Score 0 wird gespeichert und exportiert
- ✅ Fortschrittsanzeige zählt nur bearbeitete Tests (Score ≠ 0)
- ✅ Export enthält **alle** Tests (auch Score 0)

---

## 💡 Lessons Learned

1. **Semantik beachten:** Score 0 ist nicht "kein Ergebnis", sondern "neutrales Verhalten"
2. **Daten vs. UI-Logik:** Speichern ≠ Fortschrittsanzeige
   - Speichern: Alle validen Werte (inkl. 0)
   - Fortschritt: Nur "bearbeitete" Tests (Score ≠ 0)
3. **Tests für Edge Cases:** Score 0 ist ein typischer Edge Case

---

## 🔧 Commit-Nachricht

```
fix: Score 0 wird jetzt korrekt exportiert

- test_data_form.py: Alle Tests werden gespeichert (auch Score 0)
- test_data_form.py: Fortschritt zählt nur Tests mit Score ≠ 0
- test_excel_exporter.py: Neuer Test für Score 0 (12 Tests total)
- test_pdf_exporter.py: Neuer Test für Score 0 (14 Tests total)

Score 0 bedeutet neutrales Verhalten und ist ein valider Wert.

113 Tests bestehen
```
