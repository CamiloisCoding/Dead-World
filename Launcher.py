# =============================================================================
# Launcher.py  –  Auto-Updater-Launcher für Dead World
# =============================================================================
# Kompilierbar mit PyInstaller:
#   pyinstaller launcher.spec
#
# Ablauf beim Start:
#   1. Kleines Fenster "Suche nach Updates..." erscheint.
#   2. Onlineversion auf GitHub wird abgerufen.
#   3. Falls neuer → Download mit Fortschrittsbalken, altes EXE ersetzen.
#   4. Falls kein Internet oder gleiche Version → Spiel direkt starten.
# =============================================================================

import os
import sys
import time
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional

# requests wird für HTTP-Downloads verwendet
try:
    import requests
except ImportError:
    # Sollte bei kompilierter EXE nicht passieren, aber sicher ist sicher
    requests = None  # type: ignore

# psutil zum Beenden laufender Spielprozesse
try:
    import psutil
except ImportError:
    psutil = None  # type: ignore


# =============================================================================
# KONFIGURATION  –  hier deine eigenen GitHub-Werte eintragen
# =============================================================================

# GitHub-Benutzername  (z. B. "maxmustermann")
GITHUB_USER: str = "DEIN_GITHUB_BENUTZERNAME"

# Name des GitHub-Repositorys  (z. B. "dead-world")
GITHUB_REPO: str = "DEIN_REPO_NAME"

# Release-Tag: "latest" liefert immer den neuesten Release
RELEASE_TAG: str = "latest"

# Dateiname der Spiel-EXE im GitHub-Release (muss exakt übereinstimmen)
RELEASE_ASSET: str = "DeadWorld.exe"

# Raw-URL zur version.txt im Hauptzweig des Repos
VERSION_URL: str = (
    f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.txt"
)

# Download-URL für die Spiel-EXE aus dem GitHub-Release
DOWNLOAD_URL: str = (
    f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}"
    f"/releases/{RELEASE_TAG}/download/{RELEASE_ASSET}"
)

# Lokaler Dateiname der Spiel-EXE
GAME_EXE: str = "DeadWorld.exe"

# Temporärer Dateiname während des Downloads
GAME_EXE_TEMP: str = "DeadWorld_new.exe"

# Name der lokalen Versionsdatei
VERSION_FILE: str = "version.txt"

# Timeout für HTTP-Anfragen in Sekunden
REQUEST_TIMEOUT: int = 15

# Fenstergröße des Launchers
WINDOW_WIDTH:  int = 440
WINDOW_HEIGHT: int = 150

# Farbpalette (Catppuccin Mocha – passend zum Spiel-Thema)
COLOR_BG:       str = "#1e1e2e"
COLOR_TEXT:     str = "#cdd6f4"
COLOR_SUBTEXT:  str = "#a6adc8"
COLOR_ACCENT:   str = "#89b4fa"
COLOR_TROUGH:   str = "#313244"


# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================

def get_base_dir() -> Path:
    """
    Gibt das Verzeichnis zurück, in dem der Launcher liegt.
    Unterscheidet zwischen PyInstaller-Modus (.exe) und normalem Python.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller: sys.executable zeigt auf Launcher.exe
        return Path(sys.executable).parent
    # Normaler Python-Aufruf
    return Path(__file__).resolve().parent


# Basisverzeichnis einmalig berechnen
BASE_DIR: Path = get_base_dir()


def read_local_version() -> str:
    """
    Liest die lokale Versionsnummer aus der version.txt.
    Gibt '0.0.0' zurück wenn die Datei fehlt oder fehlerhaft ist.
    """
    version_path = BASE_DIR / VERSION_FILE
    try:
        return version_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "0.0.0"
    except Exception as fehler:
        print(f"[Fehler] Lokale version.txt nicht lesbar: {fehler}")
        return "0.0.0"


def fetch_online_version() -> Optional[str]:
    """
    Ruft die aktuelle Versionsnummer von GitHub ab.
    Gibt None zurück wenn keine Verbindung möglich ist.
    """
    if requests is None:
        return None
    try:
        antwort = requests.get(VERSION_URL, timeout=REQUEST_TIMEOUT)
        antwort.raise_for_status()
        return antwort.text.strip()
    except requests.exceptions.ConnectionError:
        # Kein Internet oder GitHub nicht erreichbar
        print("[Info] Keine Internetverbindung.")
        return None
    except requests.exceptions.Timeout:
        # Verbindung zu langsam / Server antwortet nicht
        print("[Info] Timeout beim Abrufen der Online-Version.")
        return None
    except requests.exceptions.HTTPError as fehler:
        # HTTP-Fehlercode (z. B. 404 – Datei nicht gefunden)
        print(f"[Warnung] HTTP-Fehler beim Versionscheck: {fehler}")
        return None
    except requests.exceptions.RequestException as fehler:
        # Alle anderen requests-Fehler
        print(f"[Warnung] Netzwerkfehler beim Versionscheck: {fehler}")
        return None


def version_als_tupel(version_str: str) -> tuple:
    """
    Wandelt '1.2.3' in (1, 2, 3) um, damit Versionen verglichen werden können.
    Ungültige Teile werden als 0 behandelt.
    """
    teile = []
    for teil in version_str.split("."):
        try:
            teile.append(int(teil))
        except ValueError:
            teile.append(0)
    return tuple(teile) if teile else (0,)


def ist_neuer(online: str, lokal: str) -> bool:
    """
    Gibt True zurück, wenn die Online-Version neuer als die lokale Version ist.
    Beispiel: '1.1.0' > '1.0.3'  →  True
    """
    return version_als_tupel(online) > version_als_tupel(lokal)


def spielprozesse_beenden() -> None:
    """
    Beendet alle laufenden Instanzen der Spiel-EXE, damit die Datei
    ersetzt werden kann (Windows sperrt laufende Prozesse).
    Benötigt psutil – wird übersprungen wenn nicht verfügbar.
    """
    if psutil is None:
        print("[Info] psutil nicht verfügbar – Spielprozesse werden nicht beendet.")
        return

    gesuchter_name = GAME_EXE.lower()
    gefunden = False

    for prozess in psutil.process_iter(["pid", "name"]):
        try:
            if prozess.info["name"].lower() == gesuchter_name:
                print(f"[Info] Beende Prozess PID {prozess.info['pid']} ({GAME_EXE})")
                prozess.terminate()
                prozess.wait(timeout=5)
                gefunden = True
        except psutil.NoSuchProcess:
            pass  # Prozess hat sich bereits selbst beendet
        except psutil.AccessDenied:
            print(f"[Warnung] Kein Zugriff auf Prozess {prozess.info.get('pid')}")
        except psutil.TimeoutExpired:
            # Erzwungenes Beenden wenn terminate() nicht hilft
            try:
                prozess.kill()
            except psutil.NoSuchProcess:
                pass

    if not gefunden:
        print("[Info] Kein laufender Spielprozess gefunden.")


def spiel_starten() -> None:
    """
    Startet die Spiel-EXE als eigenständigen Prozess.
    DETACHED_PROCESS stellt sicher, dass der Launcher den Spielprozess
    nicht als Kind-Prozess hält – das Spiel läuft nach Launcher-Beendigung weiter.
    """
    spiel_pfad = BASE_DIR / GAME_EXE

    if not spiel_pfad.exists():
        raise FileNotFoundError(
            f"'{GAME_EXE}' nicht gefunden in: {BASE_DIR}"
        )

    # Windows-spezifische Flags: Prozess komplett loslösen
    flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

    subprocess.Popen(
        [str(spiel_pfad)],
        cwd=str(BASE_DIR),
        creationflags=flags,
    )
    print(f"[Info] '{GAME_EXE}' wurde gestartet.")


# =============================================================================
# GUI-KLASSE
# =============================================================================

class LauncherFenster(tk.Tk):
    """
    Kleines Tkinter-Fenster mit:
    - Titel-Label
    - Status-Label (zeigt aktuellen Schritt an)
    - ttk.Progressbar (unbestimmt oder bestimmt je nach Situation)

    Die gesamte Update-Logik läuft in einem Hintergrund-Thread, damit
    das Fenster nicht einfriert.
    """

    def __init__(self) -> None:
        super().__init__()

        # ── Fenster-Grundeinstellungen ─────────────────────────────────────
        self.title("Dead World  –  Launcher")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)

        # Fenstergröße setzen und in der Bildschirmmitte platzieren
        bildschirm_b = self.winfo_screenwidth()
        bildschirm_h = self.winfo_screenheight()
        x = (bildschirm_b - WINDOW_WIDTH) // 2
        y = (bildschirm_h - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # Schließen-Button (X) während kritischer Operationen sperren
        self._schliessen_erlaubt: bool = False
        self.protocol("WM_DELETE_WINDOW", self._fenster_schliessen_angefragt)

        # ── Widgets aufbauen ───────────────────────────────────────────────
        self._widgets_erstellen()

        # ── Fortschrittsbalken-Style ───────────────────────────────────────
        stil = ttk.Style(self)
        stil.theme_use("default")
        stil.configure(
            "Launcher.Horizontal.TProgressbar",
            troughcolor=COLOR_TROUGH,
            background=COLOR_ACCENT,
            thickness=16,
        )

        # ── Hintergrund-Thread starten ─────────────────────────────────────
        self._thread = threading.Thread(
            target=self._update_logik_ausfuehren,
            daemon=True,
            name="UpdateThread",
        )
        self._thread.start()

    # ── Widget-Erstellung ──────────────────────────────────────────────────

    def _widgets_erstellen(self) -> None:
        """Erstellt alle GUI-Elemente."""

        # Titel
        self._label_titel = tk.Label(
            self,
            text="☠  DEAD WORLD",
            font=("Segoe UI", 13, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG,
        )
        self._label_titel.pack(pady=(18, 2))

        # Statuszeile
        self._label_status = tk.Label(
            self,
            text="Suche nach Updates...",
            font=("Segoe UI", 9),
            fg=COLOR_SUBTEXT,
            bg=COLOR_BG,
        )
        self._label_status.pack(pady=(0, 6))

        # Fortschrittsbalken
        self._progressbar = ttk.Progressbar(
            self,
            orient="horizontal",
            length=WINDOW_WIDTH - 60,
            mode="indeterminate",
            style="Launcher.Horizontal.TProgressbar",
        )
        self._progressbar.pack(pady=(2, 0))
        self._progressbar.start(10)

    # ── Thread-sichere GUI-Helfer ──────────────────────────────────────────

    def _status_setzen(self, text: str) -> None:
        """Aktualisiert den Status-Text thread-sicher über after()."""
        self.after(0, lambda: self._label_status.config(text=text))

    def _progress_bestimmt(self, prozent: float) -> None:
        """
        Schaltet den Fortschrittsbalken in den bestimmten Modus
        und setzt den Prozentwert (0–100).
        """
        def _aktualisieren() -> None:
            self._progressbar.stop()
            self._progressbar.config(mode="determinate")
            self._progressbar["value"] = prozent

        self.after(0, _aktualisieren)

    def _progress_unbestimmt(self) -> None:
        """Schaltet den Fortschrittsbalken zurück in den Animations-Modus."""
        def _aktualisieren() -> None:
            self._progressbar.config(mode="indeterminate")
            self._progressbar.start(10)

        self.after(0, _aktualisieren)

    def _fenster_schliessen_angefragt(self) -> None:
        """Wird aufgerufen wenn der Nutzer auf das X klickt."""
        if self._schliessen_erlaubt:
            self.destroy()
        # Sonst: ignorieren (Update soll nicht abgebrochen werden)

    def _launcher_schliessen(self) -> None:
        """Schließt den Launcher sauber aus einem beliebigen Thread heraus."""
        self._schliessen_erlaubt = True
        self.after(0, self.destroy)

    # ── Update-Logik (läuft im Hintergrund-Thread) ─────────────────────────

    def _update_logik_ausfuehren(self) -> None:
        """
        Vollständiger Update-Ablauf:
          1. Online-Version von GitHub abrufen
          2. Mit lokaler Version vergleichen
          3. Bei neuer Version: Download, Prozesse beenden, EXE ersetzen
          4. Spiel starten und Launcher beenden
        """
        try:
            # ── Schritt 1: Versionen vergleichen ──────────────────────────
            self._status_setzen("Suche nach Updates...")

            online_ver = fetch_online_version()

            if online_ver is None:
                # Kein Internet → Spiel trotzdem starten
                self._status_setzen("Keine Verbindung gefunden. Starte Spiel...")
                time.sleep(1.5)
                self._spiel_starten_und_beenden()
                return

            lokal_ver = read_local_version()
            print(f"[Info] Lokale Version: {lokal_ver}  |  Online-Version: {online_ver}")

            if not ist_neuer(online_ver, lokal_ver):
                # Spiel ist aktuell
                self._status_setzen(
                    f"Spiel ist aktuell (v{lokal_ver}). Starte..."
                )
                time.sleep(1.0)
                self._spiel_starten_und_beenden()
                return

            # ── Schritt 2: Update herunterladen ───────────────────────────
            self._status_setzen(
                f"Update verfügbar: v{lokal_ver} → v{online_ver}. Lade herunter..."
            )
            time.sleep(0.6)  # kurze Pause damit der Nutzer die Meldung liest

            ziel_temp = BASE_DIR / GAME_EXE_TEMP
            erfolg = self._datei_herunterladen(DOWNLOAD_URL, ziel_temp)

            if not erfolg:
                # Download fehlgeschlagen → alte Version starten
                self._status_setzen(
                    "Download fehlgeschlagen. Starte vorhandene Version..."
                )
                time.sleep(2)
                self._spiel_starten_und_beenden()
                return

            # ── Schritt 3: Laufende Spielprozesse beenden ─────────────────
            self._progress_unbestimmt()
            self._status_setzen("Beende laufende Spielinstanzen...")
            spielprozesse_beenden()
            time.sleep(0.4)

            # ── Schritt 4: Alte EXE durch neue ersetzen ───────────────────
            self._status_setzen("Installiere Update...")
            ziel_alt = BASE_DIR / GAME_EXE

            try:
                if ziel_alt.exists():
                    ziel_alt.unlink()           # alte Datei löschen
                shutil.move(str(ziel_temp), str(ziel_alt))  # neue einsetzen
            except PermissionError:
                # Datei noch von einem anderen Prozess gehalten
                self._status_setzen(
                    "Fehler: Datei gesperrt. Starte vorhandene Version..."
                )
                time.sleep(2)
                if ziel_temp.exists():
                    ziel_temp.unlink()
                self._spiel_starten_und_beenden()
                return
            except OSError as fehler:
                self._status_setzen(f"Fehler beim Ersetzen: {fehler}")
                time.sleep(3)
                self._spiel_starten_und_beenden()
                return

            # ── Schritt 5: Lokale version.txt aktualisieren ───────────────
            try:
                (BASE_DIR / VERSION_FILE).write_text(online_ver, encoding="utf-8")
                print(f"[Info] version.txt auf {online_ver} aktualisiert.")
            except OSError as fehler:
                # Nicht kritisch – Spiel läuft trotzdem
                print(f"[Warnung] version.txt konnte nicht aktualisiert werden: {fehler}")

            # ── Schritt 6: Spiel mit neuer Version starten ────────────────
            self._status_setzen(
                f"Update auf v{online_ver} installiert! Starte Spiel..."
            )
            time.sleep(1.0)
            self._spiel_starten_und_beenden()

        except Exception as fehler:
            # Unerwarteter Absturz der Update-Logik → Spiel trotzdem starten
            print(f"[Fehler] Unerwarteter Fehler in der Update-Logik: {fehler}")
            self._status_setzen(f"Fehler: {fehler}. Starte Spiel...")
            time.sleep(2)
            self._spiel_starten_und_beenden()

    def _datei_herunterladen(self, url: str, ziel: Path) -> bool:
        """
        Lädt eine Datei per HTTP herunter und speichert sie unter 'ziel'.
        Aktualisiert den Fortschrittsbalken anhand des Content-Length-Headers.

        Rückgabe:
            True  → Download erfolgreich
            False → Fehler aufgetreten
        """
        if requests is None:
            self._status_setzen("Fehler: requests-Bibliothek nicht verfügbar.")
            return False

        try:
            antwort = requests.get(
                url,
                stream=True,
                timeout=REQUEST_TIMEOUT,
            )
            antwort.raise_for_status()

            # Gesamtgröße aus Header lesen (fehlt manchmal)
            gesamt_bytes = int(antwort.headers.get("content-length", 0))

            if gesamt_bytes > 0:
                self._progress_bestimmt(0)
            else:
                self._progress_unbestimmt()

            heruntergeladen = 0
            chunk_groesse = 8192  # 8 KB pro Schreibvorgang

            with open(ziel, "wb") as datei:
                for chunk in antwort.iter_content(chunk_size=chunk_groesse):
                    if chunk:
                        datei.write(chunk)
                        heruntergeladen += len(chunk)

                        if gesamt_bytes > 0:
                            # Echten Prozentwert berechnen und anzeigen
                            prozent = (heruntergeladen / gesamt_bytes) * 100
                            self._progress_bestimmt(prozent)

                            dl_mb  = heruntergeladen / (1024 * 1024)
                            tot_mb = gesamt_bytes    / (1024 * 1024)
                            self._status_setzen(
                                f"Lädt herunter...  {dl_mb:.1f} / {tot_mb:.1f} MB"
                                f"  ({prozent:.0f} %)"
                            )

            print(f"[Info] Download abgeschlossen: {ziel}")
            return True

        except requests.exceptions.ConnectionError:
            self._status_setzen("Verbindungsfehler beim Download.")
            return False
        except requests.exceptions.Timeout:
            self._status_setzen("Download-Timeout überschritten.")
            return False
        except requests.exceptions.HTTPError as fehler:
            self._status_setzen(f"HTTP-Fehler: {fehler}")
            return False
        except OSError as fehler:
            self._status_setzen(f"Schreibfehler: {fehler}")
            return False
        except Exception as fehler:
            self._status_setzen(f"Unbekannter Download-Fehler: {fehler}")
            return False

    def _spiel_starten_und_beenden(self) -> None:
        """
        Startet die Spiel-EXE und schließt anschließend den Launcher.
        Bei Fehlern wird eine Fehlermeldung angezeigt.
        """
        try:
            spiel_starten()
        except FileNotFoundError:
            # Spiel-EXE existiert gar nicht
            self._schliessen_erlaubt = True
            self.after(
                0,
                lambda: messagebox.showerror(
                    "Fehler – Spiel nicht gefunden",
                    f"'{GAME_EXE}' wurde nicht gefunden.\n\n"
                    "Bitte lade das Spiel erneut von GitHub herunter\n"
                    f"und platziere '{GAME_EXE}' neben den Launcher.",
                ),
            )
            self.after(200, self.destroy)
            return
        except Exception as fehler:
            self._schliessen_erlaubt = True
            self.after(
                0,
                lambda: messagebox.showerror(
                    "Fehler – Start fehlgeschlagen",
                    f"Das Spiel konnte nicht gestartet werden:\n\n{fehler}",
                ),
            )
            self.after(200, self.destroy)
            return

        # Alles gut – Launcher schließen
        self._launcher_schliessen()


# =============================================================================
# EINSTIEGSPUNKT
# =============================================================================

if __name__ == "__main__":
    app = LauncherFenster()
    app.mainloop()
