@echo off
REM Build-Script für Windows 64-bit Executable
REM Dog Mentality Test

echo ====================================
echo Dog Mentality Test - Windows Build
echo ====================================
echo.

REM Virtuelle Umgebung aktivieren
echo [1/4] Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo FEHLER: Virtuelle Umgebung konnte nicht aktiviert werden!
    pause
    exit /b 1
)
echo OK
echo.

REM PyInstaller installieren falls nicht vorhanden
echo [2/4] Prüfe PyInstaller Installation...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller nicht gefunden, installiere...
    pip install pyinstaller
)
echo OK
echo.

REM Alte Build-Dateien löschen
echo [3/4] Räume alte Build-Dateien auf...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo OK
echo.

REM Build durchführen
echo [4/4] Erstelle Windows Executable...
echo Dies kann einige Minuten dauern...
pyinstaller --clean build_windows.spec
if errorlevel 1 (
    echo.
    echo FEHLER: Build fehlgeschlagen!
    pause
    exit /b 1
)
echo.

echo ====================================
echo Build erfolgreich!
echo ====================================
echo.
echo Die Anwendung befindet sich in:
echo dist\DogMentalityTest\
echo.
echo Starte mit: dist\DogMentalityTest\DogMentalityTest.exe
echo.
echo WICHTIG: Vergiss nicht die .env Datei anzulegen!
echo Beispiel: .env.example
echo.
pause
