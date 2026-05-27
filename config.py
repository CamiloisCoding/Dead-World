# ============================================================
# config.py — Constants, Colors, and Static Data for Dead World
# ============================================================
# All immutable configuration extracted from the main game file.
# Import with: from config import *

import os

# ========================
# SCREEN & DISPLAY
# ========================
WIDTH, HEIGHT = 1920, 1080
FPS = 60
REFERENCE_WIDTH = 1920    
REFERENCE_HEIGHT = 1080

# Resolution Presets (Name, Breite, Höhe)
RESOLUTION_PRESETS = [
    ('Sehr Niedrig', 800, 450),
    ('Niedrig', 1024, 576),
    ('Mittel', 1280, 720),
    ('Hoch', 1680, 1050),
    ('Sehr Hoch', 1920, 1080)
]

# Terminal-Font (Cascadia Code = moderner Microsoft-Monospace-Font)
TERMINAL_FONT_NAME = "cascadiacode"

# ========================
# GAME STATES
# ========================
INTRO = 0
MENU = 1
OPTIONS = 2
GAME = 3
PAUSED = 5

# ========================
# COLORS — Atmospheric Post-Apocalyptic Palette
# ========================
BLACK = (0, 0, 0)
BLOOD_RED = (170, 20, 20)
DARK_RED = (90, 5, 5)
DEEP_RED = (50, 0, 0)
GRAY = (55, 50, 55)
LIGHT_GRAY = (120, 115, 120)
DARK_GRAY = (22, 18, 22)
HOVER_RED = (220, 40, 30)
GREEN = (0, 255, 0)
EMBER_ORANGE = (255, 120, 30)
EMBER_DIM = (180, 70, 10)
ACCENT_GLOW = (255, 60, 40)
FOG_COLOR = (20, 18, 25)

# Amber-Phosphor Terminal Palette
TERMINAL_AMBER        = (215, 155, 40)   # Haupttext — warmes Amber
TERMINAL_AMBER_BRIGHT = (255, 205, 80)   # Helles Amber — Spieler-Input
TERMINAL_AMBER_DIM    = (110, 75, 18)    # Gedimmtes Amber — System/UI
TERMINAL_AMBER_BAR    = (12, 8, 0)       # Fast-Schwarz mit Amber-Hauch — Top-Bar BG
TERMINAL_GREEN        = TERMINAL_AMBER   # Alias für Scrollbar-Kompatibilität
TERMINAL_DIM          = TERMINAL_AMBER_DIM
TERMINAL_BG           = BLACK

# Overlay-Farbkodierung (Amber-Phosphor Terminal)
COLOR_NORMAL  = (215, 155, 40)    # Normaler Erzähltext — Amber
COLOR_PLAYER  = (255, 205, 80)    # Spieler-Eingabe-Echo — helles Amber
COLOR_DANGER  = (220, 55, 35)     # Kampf / Gefahr — Rot
COLOR_SYSTEM  = (110, 75, 18)     # System-Trennzeilen — gedimmtes Amber
COLOR_SUCCESS = (80, 200, 100)    # Erfolg / Level-Up — Grün

# ========================
# TERMINAL COLOR THEMES
# ========================
# Each entry: name, normal, bright, dim, bar (top-bar background)
TERMINAL_COLOR_THEMES = [
    {
        'name':   'Amber',
        'normal': (215, 155,  40),
        'bright': (255, 205,  80),
        'dim':    (110,  75,  18),
        'bar':    ( 12,   8,   0),
    },
    {
        'name':   'Grün',
        'normal': ( 55, 200,  70),
        'bright': (110, 255, 100),
        'dim':    ( 22,  80,  28),
        'bar':    (  0,  10,   2),
    },
    {
        'name':   'Weiß',
        'normal': (195, 195, 195),
        'bright': (255, 255, 255),
        'dim':    ( 85,  85,  85),
        'bar':    (  8,   8,   8),
    },
    {
        'name':   'Cyan',
        'normal': ( 35, 195, 220),
        'bright': ( 75, 240, 255),
        'dim':    ( 12,  72,  88),
        'bar':    (  0,   6,  12),
    },
    {
        'name':   'Rot',
        'normal': (200,  38,  38),
        'bright': (255,  75,  55),
        'dim':    ( 80,  14,  14),
        'bar':    ( 10,   0,   0),
    },
]

# ========================
# KEY REPEAT TIMING (ms)
# ========================
backspace_initial_delay = 250
backspace_repeat_delay = 25
key_initial_delay = 250
key_repeat_delay = 35

# ========================
# TYPEWRITER EFFECT
# ========================
TYPEWRITER_SPEED = 1  # Millisekunden pro Zeichen (1 = extrem schnell)

# ========================
# COMBAT SYSTEM
# ========================
ZOMBIE_RESPAWN_COOLDOWN = 300  # 5 Minuten in Sekunden

# Bonus-Stats pro Fäuste-Level
FIST_LEVEL_BONUSES = {
    1: {'damage': [99, 100]},
    2: {'damage': [99, 100]},
    3: {'damage': [12, 22]},
    4: {'damage': [18, 30]},
    5: {'damage': [25, 40]}   # Max Level
}

# QTE defaults
qte_duration = 2.0  # Sekunden

# Waffen, dmg, crit_chance
weapons = {
    'ak': {'name': 'AK-47', 'type': 'ranged', 'damage': [50, 75], 'accuracy': 0.7, 'ammo': 30},
    'pistole': {'name': 'Pistole', 'type': 'ranged', 'damage': [40, 60], 'accuracy': 0.8, 'ammo': 12},
    'küchenmesser': {'name': 'Küchenmesser', 'type': 'melee', 'damage': [20, 35], 'crit_chance': 0.3},
    'kampfmesser': {'name': 'Kampfmesser', 'type': 'melee', 'damage': [25, 40], 'crit_chance': 0.35},
    'feuerlöscher': {'name': 'Feuerlöscher', 'type': 'melee', 'damage': [50, 80], 'crit_chance': 0.25},
    'fäuste': {'name': 'Fäuste', 'type': 'melee', 'damage': [99, 100], 'black_flash': 1.00},
    'baseball_schläger': {'name': 'Baseball Schläger', 'type': 'melee', 'damage': [25, 35], 'crit_chance': 0.25},
    'axt': {'name': 'Axt', 'type': 'melee', 'damage': [35, 50], 'crit_chance': 0.3},
    'machete': {'name': 'Machete', 'type': 'melee', 'damage': [30, 45], 'crit_chance': 0.35},
}

# Essbare Items (Zork-inspiriert)
food_items = {
    'konserven': {'name': 'Konservendose', 'heal': 25, 'message': 'Du öffnest die Konservendose und isst den Inhalt. Nicht gerade ein Gourmetmahl, aber es füllt den Magen.'},
    'medkit': {'name': 'Medkit', 'heal': 50, 'message': 'Du öffnest das Medkit und versorgst deine Wunden. Schon besser.'},
    'schokoriegel': {'name': 'Schokoriegel', 'heal': 10, 'message': 'Du beißt in den alten Schokoriegel. Etwas trocken, aber der Zucker gibt dir Energie.'},
    'dosenfleisch': {'name': 'Dosenfleisch', 'heal': 30, 'message': 'Du öffnest die Dose Fleisch. Es riecht fragwürdig, schmeckt aber noch... akzeptabel.'},
    'wasser': {'name': 'Wasserflasche', 'heal': 15, 'message': 'Du trinkst die Wasserflasche in großen Zügen leer. Erfrischend.'},
    'energieriegel': {'name': 'Energieriegel', 'heal': 20, 'message': 'Du isst den Energieriegel. Kompakt und nahrhaft - genau was du brauchst.'},
    'crackers': {'name': 'Crackers', 'heal': 10, 'message': 'Du knabberst die trockenen Crackers. Nicht viel, aber besser als nichts.'},
    'apfel': {'name': 'Apfel', 'heal': 12, 'message': 'Du beißt in den Apfel. Etwas schrumpelig, aber erstaunlich saftig.'},
}

# Gegner-Datenbank
enemies = {
    'zombie': {'name': 'Toxoplasma-Zombie', 'health': 100, 'max_health': 100, 'damage': [8, 20], 'distance': 'nah'},
    'infizierter': {'name': 'Infizierter Mensch', 'health': 80, 'max_health': 80, 'damage': [8, 15], 'distance': 'mittel'},
    'geheimlabor_boss': {'name': 'Mutierter Labor-Leiter', 'health': 280, 'max_health': 280, 'damage': [18, 38], 'distance': 'nah'},
}

# ========================
# SCORING
# ========================
SCORE_VALUES = {
    'zombie_kill': 30,
    'item_pickup': 5,
    'new_room': 2,
    'container_found': 10,
    'move': 0,  # Züge kosten keine Punkte, werden aber gezählt
}

# ========================
# PARSER SYSTEM
# ========================
KNOWN_VERBS = {
    'n', 'norden', 'nord', 'o', 'osten', 'ost', 's', 'süden', 'süd', 'sued',
    'w', 'westen', 'west', 'so', 'südosten', 'nw', 'nordwesten', 'h', 'hoch',
    'r', 'runter', 'gehe', 'nimm', 'lese', 'lies', 'lesen', 'esse', 'iss',
    'inventar', 'inv', 'i', 'schaue', 'schau', 'look', 'l', 'karte', 'map',
    'ausrüsten', 'schieße', 'schiesse', 'schlag', 'schlage', 'stich',
    'clear', 'cls', 'echo', 'time', 'whoami', 'neu',
    'hilfe', 'help', 'öffne', 'oeffne', 'schließ', 'schliess', 'lege',
    'verbose', 'ausführl', 'ausführli', 'ausführlich', 'brief', 'kurz',
    'superbrie', 'superbrief', 'superkur', 'superkurz',
    'info', 'q', 'quit', 'beenden', 'save', 'speicher', 'speichern',
    'restore', 'laden', 'score', 'punkte', 'zeit', 'diagnose', 'd',
    'schieben', 'schieb', 'brech', 'zerhacke', '?', 'mapedit',
    'nutze', 'benutze',
    'untersuche', 'untersuchen', 'u',
}

VERBS_NEED_OBJECT = {
    'nimm': 'nehmen', 'lese': 'lesen', 'lies': 'lesen', 'lesen': 'lesen',
    'esse': 'essen', 'iss': 'essen', 'öffne': 'öffnen', 'oeffne': 'öffnen',
    'ausrüsten': 'ausrüsten', 'lege': 'legen',
    'schlag': 'schlagen', 'schlage': 'schlagen',
    'schieße': 'schießen', 'schiesse': 'schießen',
    'stich': 'stechen',
    'nutze': 'benutzen', 'benutze': 'benutzen',
}

UNKNOWN_VERB_RESPONSES = [
    "Das Wort '{verb}' kenne ich nicht.",
    "Ich weiß nicht, was '{verb}' bedeuten soll.",
    "'{verb}'? Das ist kein Befehl, den ich verstehe.",
    "Weder Mensch noch Maschine kennt den Befehl '{verb}'.",
    "Du murmelst '{verb}' vor dich hin. Nichts passiert.",
    "'{verb}' ergibt für mich keinen Sinn.",
    "Selbst in der Apokalypse versteht niemand '{verb}'.",
    "Bitte was? '{verb}' ist mir nicht bekannt.",
]

ILLOGICAL_RESPONSES = {
    'eat_weapon': [
        "Das wäre unglaublich schmerzhaft und überhaupt nicht nahrhaft.",
        "Du versuchst hineinzubeißen... Nein. Einfach nein.",
        "Dein Magen würde das nicht überleben.",
        "Das ist eine Waffe, kein Snack.",
    ],
    'eat_inedible': [
        "Das kannst du nicht essen, so verzweifelt bist du noch nicht.",
        "Das sieht nicht besonders appetitlich aus...",
        "Dein Magen protestiert schon beim Gedanken daran.",
        "Das ist definitiv nicht essbar.",
    ],
    'equip_food': [
        "Du schwingst drohend die Konserve... Nicht sehr angsteinflößend.",
        "Das ist Essen, keine Waffe. Obwohl... nein.",
        "Damit würdest du höchstens dich selbst verletzen.",
    ],
    'equip_non_weapon': [
        "Das lässt sich nicht als Waffe verwenden.",
        "Du versuchst es drohend zu schwingen. Es sieht lächerlich aus.",
        "Das ist keine Waffe.",
    ],
}

# ========================
# FILE PATHS
# ========================
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dead_world_save.json')
