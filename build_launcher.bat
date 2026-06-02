@echo off
title Dead World  -  Launcher Build
echo =====================================================
echo   Dead World  -  Launcher.exe Build
echo =====================================================
echo.

:: Sicherstellen, dass requests und psutil installiert sind
echo [*] Pruefe Abhaengigkeiten...
pip show requests >nul 2>&1 || (
    echo [*] Installiere requests...
    pip install requests
)
pip show psutil >nul 2>&1 || (
    echo [*] Installiere psutil...
    pip install psutil
)
pip show pyinstaller >nul 2>&1 || (
    echo [*] Installiere pyinstaller...
    pip install pyinstaller
)
echo [*] Abhaengigkeiten OK.
echo.

:: Alten Launcher-Build loeschen
if exist "dist\Launcher.exe" (
    echo [*] Alten Launcher loeschen...
    del /f /q "dist\Launcher.exe"
)

echo [*] Starte PyInstaller fuer Launcher...
echo.
pyinstaller launcher.spec

echo.
if exist "dist\Launcher.exe" (
    echo =====================================================
    echo   BUILD ERFOLGREICH!
    echo   Launcher.exe liegt in: dist\Launcher.exe
    echo.
    echo   Naechste Schritte:
    echo   1. dist\Launcher.exe in den Spielordner kopieren
    echo   2. version.txt daneben legen
    echo   3. DeadWorld.exe daneben legen
    echo =====================================================
) else (
    echo =====================================================
    echo   FEHLER: Build fehlgeschlagen!
    echo   Lies die Fehlermeldung oben nach.
    echo =====================================================
)

echo.
pause
