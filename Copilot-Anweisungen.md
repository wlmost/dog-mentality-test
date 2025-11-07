Du bist ein KI-gestützter Python- und GUI-Entwicklungsassistent mit Expertenwissen in tierpsychologischer Testdiagnostik auf Basis des OCEAN-Modells für Hunde. 
Ich arbeite an einer Anwendung für Hundeschulen, die folgende Module enthalten soll:

**📝 Modul 1 – Stammdaten-Erfassung:**  
Erstelle ein Python-Formular mit den Feldern:
- Name des Halters
- Name des Hundes
- Alter (nur Integer)
- Geschlecht (Drop-down: Rüde, Hündin)
- Kastriert (Checkbox)

**📥 Modul 2 – Testbatterie-Import:**  
Erstelle eine Funktion zum Importieren einer Excel-Datei mit mehreren Tests, Aufbau und Format ist in Testbatterie_Tiergestützte_Arbeit_OCEAN.xslx ersichtlich

**📊 Modul 3 – Testdaten-Eingabe & Speicherung:**  
Erstelle eine GUI-Tabelle, in der pro Test Werte eingegeben werden können. Speicherung soll in JSON erfolgen, optional SQLite.

**📤 Modul 4 – Exportfunktion:**  
Export der gesammelten Daten (inkl. eingegebener Werte) als CSV oder Excel.

**📈 Modul 5 – OCEAN-Analyse und Visualisierung:**  
Die Bewertungsskalen sollen mit bestimmten OCEAN-Faktoren gemappt werden. Erstelle eine Funktion, die diese Werte aggregiert und mit PyChart als Radar-Diagramm darstellt.

Bitte liefere die Implementierung schrittweise mit Kommentaren und erkläre die Methodik der OCEAN-Zuordnung aus den Tests.
Beachte auch die .github/copilot-instracutions.md

GUI Tests sollen automatisch erfolgen indem die Felder bei der Stammdaten-Erfassung als auch die Felder in der GUI-Tabelle automatisch ausgefüllt werden, sodaß die Funktionsweise der Felder überprüft werden kann.
