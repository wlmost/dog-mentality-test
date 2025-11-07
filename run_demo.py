"""
Startscript für die Demo-Anwendung
"""
import sys
from PySide6.QtWidgets import QApplication
from src.master_data_form import MasterDataForm
from src.models import DogData


def on_data_saved(dog_data: DogData):
    """Callback wenn Daten gespeichert wurden"""
    print("\n" + "="*50)
    print("Daten erfolgreich gespeichert:")
    print("="*50)
    print(f"Halter:     {dog_data.owner_name}")
    print(f"Hund:       {dog_data.dog_name}")
    print(f"Alter:      {dog_data.age_display()}")
    print(f"Geschlecht: {dog_data.gender.value}")
    print(f"Kastriert:  {'Ja' if dog_data.neutered else 'Nein'}")
    print("="*50)
    print("\nJSON-Format:")
    print(dog_data.to_dict())
    print()


def main():
    """Hauptfunktion"""
    app = QApplication(sys.argv)
    
    # Formular erstellen
    form = MasterDataForm()
    form.setWindowTitle("Dog Mentality Test - Stammdaten")
    
    # Signal verbinden
    form.data_saved.connect(on_data_saved)
    
    # Formular anzeigen
    form.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
