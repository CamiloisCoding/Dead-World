@echo off
title Dead World - Build
echo ============================================
echo  Dead World - EXE Build
echo ============================================
echo.

:: Alten Build-Ordner loeschen damit alles frisch ist
if exist "dist\DeadWorld" (
    echo [*] Alten Build loeschen...
    rmdir /s /q "dist\DeadWorld"
)

echo [*] Starte PyInstaller...
echo.
pyinstaller dead_world.spec

echo.
if exist "dist\DeadWorld\DeadWorld.exe" (
    echo ============================================
    echo  BUILD ERFOLGREICH!
    echo  EXE liegt in: dist\DeadWorld\DeadWorld.exe
    echo  Zum Spielen: dist\DeadWorld\ Ordner oeffnen
    echo ============================================
) else (
    echo ============================================
    echo  FEHLER: Build fehlgeschlagen!
    echo  Lies die Fehlermeldung oben nach.
    echo ============================================
)

echo.
pause
