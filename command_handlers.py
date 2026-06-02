# ============================================================
# command_handlers.py — Extracted Command Handlers for Dead World
# ============================================================
# Each handler function returns True if it handled the command,
# False otherwise. The main process_command() uses these as a
# dispatcher chain.
#
# IMPORTANT: This module must NOT import from the main game file
# at module level. Instead, it receives references at init time.

import random
import datetime
import pygame
from config import *



_game = None  # Reference to main game module (set at runtime)


def init_handlers(game_module):
    """Call once at startup. Pass the main game module so handlers can
    access add_to_history, rooms, player_inventory, player_stats, etc."""
    global _game
    _game = game_module


# ========================
# HELPER — shorter alias
# ========================
def _h(text):
    """Shorthand for add_to_history."""
    _game.add_to_history(text)


# ========================
# HELP
# ========================
def handle_help(cmd):
    if cmd not in ('hilfe', 'help', '?'):
        return False

    _h("DEAD WORLD - BEFEHLE")
    _h("")
    _h("Bewegung:")
    _h("  n, norden - Gehe nach Norden")
    _h("  o, osten - Gehe nach Osten")
    _h("  s, süden - Gehe nach Süden")
    _h("  w, westen - Gehe nach Westen")
    _h("  r, runter - Gehe nach Unten")
    _h("  h, hoch - Gehe nach Oben")
    _h("  gehe [richtung] - Alternative Schreibweise")
    _h("  schaue, look - Raum beschreiben")
    _h("  untersuche [objekt] - Raum/Objekt genau untersuchen")
    _h("")
    _h("Gegenstände:")
    _h("  nimm [item] - Item aufheben")
    _h("  lese [item] - Item lesen (Zeitung, Notizen)")
    _h("  esse [item] - Essen/Trinken konsumieren")
    _h("  inventar, inv - Inventar anzeigen")
    _h("")
    _h("Kampf:")
    _h("  ausrüsten [waffe] - Waffe ausrüsten")
    _h("  schlag [ziel] - Nahkampf (Timing-Leiste: LEERTASTE)")
    _h("  stich auf [ziel] - Mit Messer angreifen (Timing-Leiste)")
    _h("  schieße auf [ziel] - Schusswaffe nutzen")
    _h("  nachladen - Ausgerüstete Schusswaffe nachladen (braucht Magazin im Inventar)")
    _h("  ignoriere [ziel] - Gegner ignorieren (Kampfmodus beenden, Musik stoppt)")
    _h("  [Angriff] - LEERTASTE wenn der Marker die Mitte trifft!")
    _h("  [Gegenangriff] - Pfeiltasten: Herz ausweichen!")
    _h("")
    _h("Begleiter:")
    _h("  folge mir - Begleiter-Status / reaktivieren")
    _h("  bleib hier - Begleiter wartet (Boni aus)")
    _h("  begleiter status - Begleiter-Info anzeigen")
    _h("")
    _h("Terminal:")
    _h("  clear, cls - Terminal leeren")
    _h("  echo [text] - Text ausgeben")
    _h("  time - Aktuelle Zeit anzeigen")
    _h("  whoami - Charakter-Info")
    _h("  karte, map - Standort-Info anzeigen")
    _h("")
    _h("System:")
    _h("  save, speichern - Spiel speichern")
    _h("  restore, laden - Spiel laden")
    _h("  score, punkte - Punkte anzeigen")
    _h("  zeit - Spielzeit anzeigen")
    _h("  diagnose, d - Gesundheits- und Zustandsbericht")
    _h("  info - Spielinfo")
    _h("  q, quit - Beenden")
    _h("  verbose/brief/superbrief - Beschreibungsmodus")
    _h("  neu - Neustart nach Tod")
    _h("")
    _h("Behälter:")
    _h("  öffne/schließe [behälter]")
    _h("  lege [item] in [behälter]")
    _h("  nimm [item] aus [behälter]")
    _h("  schaue in [behälter]")
    _h("")
    return True


# ========================
# MOVEMENT
# ========================
# Direction alias map
# Bewegungs-Aliase (vollständige Wörter; der Dispatcher kürzt keine Tokens mehr).
_DIRECTION_MAP = {
    'n': 'norden', 'norden': 'norden', 'nord': 'norden',
    'o': 'osten', 'osten': 'osten', 'ost': 'osten',
    's': 'süden', 'süden': 'süden', 'süd': 'süden', 'sued': 'süden',
    'w': 'westen', 'westen': 'westen', 'west': 'westen',
    'so': 'südosten', 'südosten': 'südosten', 'suedosten': 'südosten',
    'süd-osten': 'südosten', 'sued-osten': 'südosten',
    'nw': 'nordwesten', 'nordwesten': 'nordwesten', 'nord-westen': 'nordwesten',
    'h': 'hoch', 'hoch': 'hoch', 'up': 'hoch',
    'r': 'runter', 'runter': 'runter', 'down': 'runter',
}


def handle_movement(cmd):
    if cmd == 'gehe':
        _h("Wohin willst du gehen?")
        _h("")
        return True

    if cmd.startswith('gehe '):
        raw_dir = cmd[5:].strip()
        direction = _DIRECTION_MAP.get(raw_dir, raw_dir)
        _game.move_direction(direction)
        return True

    direction = _DIRECTION_MAP.get(cmd)
    if direction:
        _game.move_direction(direction)
        return True

    return False


# ========================
# ITEM COMMANDS
# ========================
def handle_item_commands(cmd):
    """Handles: nimm, lese/lies, inventar/inv, esse/iss"""

    # --- NIMM (without 'aus') ---
    if cmd == 'nimm':
        room = _game.rooms[_game.current_room]
        available = room.get('items', [])
        if len(available) == 1:
            _game.process_command(f'nimm {available[0]}')
        elif len(available) > 1:
            _h("Was möchtest du nehmen?")
            for idx, it in enumerate(available, 1):
                _h(f"  {idx}. {_game.get_item_name(it)}")
            _game.pending_ambiguity = {'action': 'nimm', 'candidates': available[:], 'original_cmd': 'nimm'}
            _h("")
        else:
            _h("Hier gibt es nichts zum Nehmen.")
            _h("")
        return True

    if cmd.startswith('nimm ') and ' aus ' not in cmd:
        item = cmd[5:].strip()
        # Boot am Fluss kann nicht aufgehoben werden – stattdessen nutzen
        if item in ('boot', 'boat', 'ruderboot') and _game.current_room == 'fluss':
            _h("Das Boot ist zu groß zum Tragen. Tippe 'nutze boot', um damit zu fahren.")
            _h("")
            return True
        room = _game.rooms[_game.current_room]
        if item in room['items']:
            idef = _game.ITEM_DEFS.get(item)
            item_weight = idef.weight if idef else 1
            if _game.get_player_carry_weight() + item_weight > _game.player_stats['max_weight']:
                _h("Deine Last ist zu schwer. Du kannst nichts mehr tragen.")
                _h("")
            else:
                room['items'].remove(item)
                _game.player_inventory.append(item)
                _h(f"Du nimmst {_game.get_item_name(item)}.")
                _game.add_score('item_pickup', context=item)
                enc = _game.get_encumbrance_description()
                if enc:
                    _h(enc)
                _h("")
        else:
            _h(f"Hier gibt es kein '{item}'.")
            _h("")
        return True

    # --- LESE / LIES ---
    if cmd.startswith('lese ') or cmd.startswith('lies ') or cmd.startswith('lesen '):
        if cmd.startswith('lese '):
            item = cmd[5:].strip()
        elif cmd.startswith('lies '):
            item = cmd[5:].strip()
        elif cmd.startswith('lesen '):
            item = cmd[6:].strip()

        _game.read_item(item)
        if item == 'tagebuch':
            _h("Im Tagebuch hast du deine letzen 2 Jahre in diesem haus Dokumentiert.")
            _h("Jeder einzelne zombie oder Mensch der versuchte reinzukommen.")
        elif item == 'stück papier':
            _h("Ein stück Papier, es hat blut schmieren drauf, teile der Notiz dadurch unlesbar.")
            _h("Sie sind üb....... nirgends ist man sicher. Alles geshah nu........... em Präs......... abor.")
        elif item == 'Zettel':
            _h("Der Zettel zerknittert und drecking, manches kaum lesbar")
            _h("Die Stadt ist komplett überrant, alles voller zombies, jedes haus durchrannt, kau.............rgendwo sicher.")
            _h("Ich bin hier noch mit .....dren überlebenden, wir sind hier und mehr essen und trinken zu finden aber fast alles ist leer oder aufgebraucht.")
            _h("Hoffentlich schaffen wir es noch aus dem Laden, scho.............en waren zombies hinter uns her und wir konnten sie gerade so abwimmeln")
        elif item == 'Wichtiges Dokument':
            _h("Vieles vom dokument nicht mehr lesbar außer ein paar Zeilen.")
            _h("25.08.04")
            _h("8 Neue Patienten ......... wut, agression..... mit 3 bissspuren........,1 patient nicht ansprechbar.......")
            _h("Viel mehr kannst du nicht entziffern.")
        elif item == 'Akten': 
            _h("In den Akten stehen die untersuchungen von Viralen infektionen und deren auswirkung auf menschen.")
            _h("Sowie auch mutationen die durch die infektionen entstehen und wie man sie ausnutzen kann zur gezwungenen evolution der Menschheit.")
        return True

    # --- INVENTAR ---
    if cmd in ('inventar', 'inv', 'i'):
        _h("INVENTAR")
        _h("")
        if _game.player_inventory:
            item_names = [_game.get_item_name(it) for it in _game.player_inventory]
            _h(f"Items: {', '.join(item_names)}")
        else:
            _h("Items: Leer")
        if _game.player_stats['equipped_weapon']:
            weapon = weapons[_game.player_stats['equipped_weapon']]
            _h(f"Waffe: {weapon['name']}")
        else:
            _h("Waffe: Keine")
        _h("")
        _h(_game.get_health_description())
        enc = _game.get_encumbrance_description()
        if enc:
            _h(enc)
        _h("")
        return True

    # --- ESSE / ISS ---
    if cmd.startswith('esse ') or cmd.startswith('iss '):
        if cmd.startswith('esse '):
            item = cmd[5:].strip()
        else:
            item = cmd[4:].strip()

        if item not in _game.player_inventory:
            _h(f"Du hast kein '{item}' im Inventar.")
            _h("")
        elif item not in food_items:
            _h(f"'{item}' kann man nicht essen.")
            _h("")
        else:
            food = food_items[item]
            old_hp = _game.player_stats['health']
            _game.player_stats['health'] = min(100, _game.player_stats['health'] + food['heal'])
            healed = _game.player_stats['health'] - old_hp
            _game.player_inventory.remove(item)
            _game.player_stats['hunger'] = max(0, _game.player_stats['hunger'] - 30)
            _game.player_stats['turns_since_last_meal'] = 0
            _game.player_stats['strength'] = min(100, _game.player_stats['strength'] + food['heal'] // 2)
            _h(food['message'])
            if healed > 0:
                if healed >= 30:
                    _h("Du fühlst dich deutlich besser.")
                elif healed >= 15:
                    _h("Etwas Kraft kehrt in deinen Körper zurück.")
                else:
                    _h("Du fühlst dich ein wenig gestärkt.")
            else:
                _h("Du bist bereits in guter Verfassung.")
            if _game.player_stats['hunger'] <= 0:
                _h("Dein Hunger ist gestillt.")
            _h("")
        return True

    # --- NUTZE / BENUTZE ---
    if cmd.startswith('nutze ') or cmd.startswith('benutze '):
        if cmd.startswith('nutze '):
            item = cmd[6:].strip()
        else:
            item = cmd[8:].strip()

        # Raum-Objekt (kein Inventar-Item) -> an Interaktions-Handler weitergeben
        if item in ('numpad', 'nummernpad', 'nummern pad'):
            return False

        # Boot am Fluss benutzen → 2-stündige Bootsfahrt zur Walddorf-Dorfstraße
        if item in ('boot', 'boat', 'ruderboot') and _game.current_room == 'fluss':
            _h("")
            _h("Du löst das Boot vom Pflock und steigst ein.")
            _h("Die Strömung erfasst dich sofort — der Fluss ist tiefer als gedacht.")
            _h("Du greifst die Ruder und richtest das Boot flussabwärts aus.")
            _h("")
            _h("Dunkle Bäume ziehen langsam an dir vorbei.")
            _h("Nebel liegt über dem Wasser. Das Plätschern der Ruder ist das einzige Geräusch.")
            _h("Einmal glaubst du, etwas Großes unter dem Boot zu spüren — dann ist es vorbei.")
            _h("")
            _h("        ... NACH ZWEI STUNDEN ...")
            _h("")
            _h("Das Ufer weicht zurück. Du siehst Lichter — nein, Fackeln.")
            _h("Ein altes Dorf. Du legst an einem moosbedeckten Steg an.")
            _h("")
            _game.stop_zombie_sounds()
            _game.stop_combat_sounds()
            _game.player_stats['in_combat'] = False
            _game.stop_combat_resume_ambient()
            _game.current_room = 'walddorf_straße'
            _game.visited_rooms.add('walddorf_straße')
            _game.describe_room()
            return True

        if item not in _game.player_inventory:
            _h(f"Du hast kein '{item}' im Inventar.")
            _h("")
        elif item in weapons:
            # Waffe ausrüsten
            _game.equip_weapon(item)
        elif item in food_items:
            # Heilitem / Essen benutzen
            if item == 'medkit' and _game.player_stats['health'] >= 100:
                _h("Du bist bereits in perfekter Verfassung. Das Medkit wäre Verschwendung.")
                _h("")
            elif _game.player_stats['health'] >= 100 and food_items[item]['heal'] > 0:
                _h("Du bist bereits vollständig geheilt. Das wäre Verschwendung.")
                _h("")
            else:
                food = food_items[item]
                old_hp = _game.player_stats['health']
                _game.player_stats['health'] = min(100, _game.player_stats['health'] + food['heal'])
                healed = _game.player_stats['health'] - old_hp
                _game.player_inventory.remove(item)
                _game.player_stats['hunger'] = max(0, _game.player_stats['hunger'] - 30)
                _game.player_stats['turns_since_last_meal'] = 0
                _game.player_stats['strength'] = min(100, _game.player_stats['strength'] + food['heal'] // 2)
                _h(food['message'])
                if healed > 0:
                    if healed >= 30:
                        _h("Du fühlst dich deutlich besser.")
                    elif healed >= 15:
                        _h("Etwas Kraft kehrt in deinen Körper zurück.")
                    else:
                        _h("Du fühlst dich ein wenig gestärkt.")
                else:
                    _h("Du bist bereits in guter Verfassung.")
                if _game.player_stats['hunger'] <= 0:
                    _h("Dein Hunger ist gestillt.")
                _h("")
        else:
            _h(f"Du weißt nicht, wie du '{_game.get_item_name(item)}' benutzen sollst.")
            _h("")
        return True

    return False


# ========================
# RELOAD COMMAND
# ========================
_AMMO_MAP = {
    'ak':      ('ak_munition',       30),
    'pistole': ('pistolen_munition', 12),
}

def handle_reload(cmd):
    """Handles: nachladen, reload, laden – lädt die ausgerüstete Schusswaffe nach."""
    if cmd not in ('nachladen', 'reload', 'laden') and \
       not cmd.startswith('nachladen ') and not cmd.startswith('reload '):
        return False

    ps = _game.player_stats
    inv = _game.player_inventory
    ws = _game.weapons

    weapon_key = ps.get('equipped_weapon')

    # Optionales Argument: nachladen ak / nachladen pistole
    parts = cmd.split(None, 1)
    if len(parts) == 2:
        arg = parts[1].strip()
        if arg in _AMMO_MAP:
            weapon_key = arg

    if not weapon_key or weapon_key not in ws:
        _h("Du hast keine Schusswaffe ausgerüstet. Rüste zuerst eine aus.")
        _h("")
        return True

    weapon = ws[weapon_key]
    if weapon.get('type') != 'ranged':
        _h(f"{weapon['name']} braucht keine Munition.")
        _h("")
        return True

    ammo_key, max_ammo = _AMMO_MAP.get(weapon_key, (None, 0))
    if not ammo_key:
        _h("Für diese Waffe gibt es keine passende Munition.")
        _h("")
        return True

    current_ammo = weapon.get('ammo', 0)
    if current_ammo >= max_ammo:
        _h(f"Das Magazin ist bereits voll ({current_ammo}/{max_ammo}).")
        _h("")
        return True

    if ammo_key not in inv:
        _h(f"Du hast kein {_game.ITEM_DEFS[ammo_key].name} im Inventar.")
        _h("Suche Munition in der Welt – z.B. in der Polizeistation oder im Casino.")
        _h("")
        return True

    inv.remove(ammo_key)
    weapon['ammo'] = max_ammo
    _h(f"Du lädst die {weapon['name']} nach. Munition: {max_ammo}/{max_ammo}.")
    _h("")
    return True


# ========================
# COMBAT COMMANDS
# ========================
def _handle_tanga_ziehen(cmd):
    """Spezial-Angriff: Tangazieher gegen die Zombie-Hure im Sex Dungeon."""
    TANGA_CMDS = {
        'ziehe tanga', 'zieh tanga', 'ziehe tanga hoch', 'zieh tanga hoch',
        'tangazieher', 'hosenzieher', 'tanga ziehen', 'tanga hochziehen',
        'ziehe den tanga', 'zieh den tanga', 'ziehe den tanga hoch',
    }
    if cmd not in TANGA_CMDS:
        return False

    if _game.current_room != 'sex_dungeon':
        _h("Hier gibt es keinen Tanga zum Ziehen.")
        _h("")
        return True

    room = _game.rooms['sex_dungeon']
    enemy_in_room = room.get('enemy')
    if not enemy_in_room or enemy_in_room != 'zombie_hure':
        _h("Die Zombie-Hure ist bereits besiegt.")
        _h("")
        return True

    enemy = _game.enemies.get('zombie_hure')
    if not enemy or enemy['health'] <= 0:
        _h("Die Zombie-Hure ist bereits besiegt.")
        _h("")
        return True

    _h("")
    _h("Du weichst einem ihrer Schläge aus — ein Schritt zur Seite, zwei nach vorne.")
    _h("Deine Finger greifen nach dem Tanga-Stoff...")
    _h("")
    _h("Du ziehst. Mit aller Kraft. Nach OBEN.")
    _h("")
    _h("Ein Reißen. Ein Knacken. Ein Geräusch das du nie vergessen wirst.")
    _h("")
    _h("Die Zombie-Hure kreischt — ein Laut der aus tausend Metern Tiefe kommt.")
    _h("Ihr Körper bäumt sich auf, zuckt, verkrampft sich.")
    _h("Der Stoff gräbt sich tiefer als physikalisch möglich in den Körper.")
    _h("Das Monster kollabiert.")
    _h("")
    _h("=== SIEG — TANGAZIEHER AUSGEFÜHRT ===")
    _h("")

    enemy['health'] = 0
    _game._resolve_enemy_defeat(enemy, 'zombie_hure', room)
    return True


def handle_combat_commands(cmd):
    """Handles: ausrüsten, schieße/schiesse, schlag/schlage, stich"""

    # Tangazieher — einzige Schwachstelle der Zombie-Hure
    if _handle_tanga_ziehen(cmd):
        return True

    # ── FRIEDHOF BOSS INTERCEPT ──────────────────────────────────────────
    # Fängt alle Angriffs-Befehle auf dem Friedhof ab, solange der Boss aktiv ist.
    # Erlaubt weiterhin: ausrüsten, nachladen (Vorbereitung auf den Kampf).
    _ANGRIFF = (
        cmd.startswith('schieß') or cmd.startswith('schiess') or
        cmd.startswith('schlag') or cmd.startswith('schlage') or
        cmd.startswith('stich') or
        cmd.startswith('töte') or cmd.startswith('töten') or cmd.startswith('tote') or
        cmd.startswith('greife') or cmd.startswith('greif ') or
        cmd.startswith('kämpfe') or cmd.startswith('kämpf ') or
        cmd.startswith('angriff') or cmd.startswith('attacke')
    )
    if (_ANGRIFF and
            _game.current_room == 'friedhof' and
            getattr(_game, 'friedhof_boss_intro_gezeigt', False) and
            not getattr(_game, 'friedhof_event_abgeschlossen', False)):
        _game.trigger_friedhof_boss_fight()
        return True

    if cmd.startswith('ausrüsten '):
        weapon_key = cmd[10:].strip()
        _game.equip_weapon(weapon_key)
        return True

    if cmd.startswith('schieße auf ') or cmd.startswith('schiesse auf ') or \
       cmd.startswith('schieße ') or cmd.startswith('schiesse '):
        if 'auf ' in cmd:
            target = cmd.split('auf ', 1)[1].strip()
        else:
            target = cmd.split('schieße ', 1)[1].strip() if 'schieße ' in cmd else cmd.split('schiesse ', 1)[1].strip()

        room = _game.rooms[_game.current_room]
        if _game.current_room == 'start' and room.get('enemy') == 'zombie' and not _game.player_stats['equipped_weapon']:
            _h("Du hast keine Waffe!")
            _h("Du stolperst zurück und weichst aus!")
            _h("Schnell, nimm eine Waffe!")
            _h("")
        else:
            _game.ranged_attack(target)
        return True

    if cmd.startswith('schlag ') or cmd.startswith('schlage '):
        if ' mit ' in cmd:
            parts = cmd.split(' ', 1)[1]
            target_and_weapon = parts.split(' mit ')
            if len(target_and_weapon) == 2:
                target = target_and_weapon[0].strip()
                weapon_name = target_and_weapon[1].strip()
                room = _game.rooms[_game.current_room]
                enemy_in_room = room.get('enemy', None)
                if not enemy_in_room:
                    _h("Es gibt hier nichts zum Angreifen!")
                    _h("")
                else:
                    enemy = enemies.get(enemy_in_room)
                    if not enemy:
                        _h("Es gibt hier nichts zum Angreifen!")
                        _h("")
                        return True
                    if _game.enemy_target_matches(target, enemy_in_room, enemy):
                        _game.attack_with_weapon(target, weapon_name)
                    else:
                        _h(f"Hier ist kein '{target}'.")
                        _h(f"Hier ist: {enemy['name']}")
                        _h("")
            else:
                _h("Falsches Format. Nutze: schlag [ziel] mit [waffe]")
                _h("")
        else:
            target = cmd.split(' ', 1)[1].strip()
            room = _game.rooms[_game.current_room]
            enemy_in_room = room.get('enemy', None)
            if not enemy_in_room:
                _h("Es gibt hier nichts zum Angreifen!")
                _h("")
            else:
                enemy = enemies.get(enemy_in_room)
                if not enemy:
                    _h("Es gibt hier nichts zum Angreifen!")
                    _h("")
                    return True
                if _game.enemy_target_matches(target, enemy_in_room, enemy):
                    _game.unarmed_attack(target)
                else:
                    _h(f"Hier ist kein '{target}'.")
                    _h(f"Hier ist: {enemy['name']}")
                    _h("")
        return True

    if cmd.startswith('stich auf '):
        target = cmd[10:].strip()
        _game.melee_attack(target)
        return True

    if cmd.startswith('töte ') or cmd.startswith('töten ') or cmd.startswith('tote '):
        target = cmd.split(' ', 1)[1].strip()
        room = _game.rooms[_game.current_room]
        enemy_in_room = room.get('enemy', None)
        if not enemy_in_room:
            _h("Es gibt hier nichts zum Angreifen!")
            _h("")
            return True
        enemy = enemies.get(enemy_in_room)
        if not enemy:
            _h("Es gibt hier nichts zum Angreifen!")
            _h("")
            return True
        if not _game.enemy_target_matches(target, enemy_in_room, enemy):
            _h(f"Hier ist kein '{target}'.")
            _h(f"Hier ist: {enemy['name']}")
            _h("")
            return True
        # Greife mit der ausgerüsteten Waffe an (Fernkampf/Nahkampf), sonst Fäuste
        weapon_key = _game.player_stats['equipped_weapon']
        if weapon_key and weapons[weapon_key]['type'] == 'ranged':
            _game.ranged_attack(target)
        elif weapon_key:
            _game.melee_attack(target)
        else:
            _game.unarmed_attack(target)
        return True

    if cmd.startswith('ignoriere ') or cmd == 'ignoriere' or \
       cmd.startswith('ignore ') or cmd == 'ignore' or \
       cmd.startswith('ignorier ') or cmd == 'ignorier':
        room = _game.rooms[_game.current_room]
        enemy_in_room = room.get('enemy')
        if enemy_in_room:
            enemy = enemies.get(enemy_in_room)
            if enemy and enemy['health'] > 0:
                _h(f"Du wendest den Blick ab und ignorierst {enemy['name']}.")
                _h("Die Bedrohung ist noch da — aber du lässt sie vorerst hinter dir.")
                _h("")
                _game.player_stats['in_combat'] = False
                _game.stop_combat_resume_ambient()
                return True
        _h("Es gibt hier nichts zu ignorieren.")
        _h("")
        return True

    return False


def _reset_player():
    """Reset player stats to defaults (used on death)."""
    _game.player_stats['health'] = 100
    _game.player_stats['strength'] = 100
    _game.player_stats['hunger'] = 0
    _game.player_stats['turns_since_last_meal'] = 0
    _game.player_stats['last_recovery_turn'] = 0
    _game.player_stats['equipped_weapon'] = None
    _game.player_stats['weapon_type'] = None
    _game.player_stats['in_combat'] = False
    _game.player_stats['companion'] = None
    _game.player_stats['companion_hp'] = 100
    _game.player_stats['companion_stunned_turns'] = 0
    for enemy_key in enemies:
        enemies[enemy_key]['health'] = enemies[enemy_key]['max_health']


# ========================
# SYSTEM COMMANDS
# ========================
def handle_system_commands(cmd):
    """Handles: clear, echo, time, whoami, neu, verbose/brief/superbrief,
    info, quit, save, restore, score, zeit, diagnose"""

    if cmd in ('clear', 'cls'):
        _game.game_history.clear()
        _h("Terminal geleert.")
        _h("")
        return True

    if cmd.startswith('echo '):
        text = cmd[5:].strip()
        _h(text)
        _h("")
        return True

    if cmd == 'time':
        now = datetime.datetime.now()
        _h(f"Aktuelle Zeit: {now.strftime('%H:%M:%S')}")
        _h(f"Datum: {now.strftime('%d.%m.%Y')}")
        _h("")
        return True

    if cmd == 'whoami':
        _h("Name: Albert Wesker Cristal")
        _h("Status: Überlebender")
        _h("Standort: Bunker")
        _h("")
        return True

    if cmd == 'neu':
        _reset_player()
        _game.scored_items.clear()
        _game.scored_kills.clear()
        _game.game_score = 0
        _game.game_moves = 0
        for idef in _game.ITEM_DEFS.values():
            if idef.max_charge >= 0:
                idef.charge = idef.max_charge
        _game.rooms['start']['first_visit'] = True
        _game.rooms['start']['enemy'] = 'zombie'
        _game.rooms['start']['items'] = ['feuerlöscher', 'zeitung']
        _game.reset_transitions()
        _game.start_game()
        return True

    if cmd in ('verbose', 'ausführl', 'ausführli', 'ausführlich'):
        _game.view_mode = 'verbose'
        _h("Modus: VERBOSE – Volle Beschreibungen.")
        _h("")
        return True

    if cmd in ('brief', 'kurz'):
        _game.view_mode = 'brief'
        _h("Modus: BRIEF – Kurze Beschreibungen bei Wiederbesuch.")
        _h("")
        return True

    if cmd in ('superbrie', 'superkur', 'superkurz', 'superbrief'):
        _game.view_mode = 'superbrief'
        _h("Modus: SUPERBRIEF – Nur Raumnamen.")
        _h("")
        return True

    if cmd == 'info':
        _h("═══════════════════════════════")
        _h("  DEAD WORLD v1.0")
        _h("  Ein Zork-inspiriertes")
        _h("  Survival Text-Adventure")
        _h("  mit Pygame Terminal-UI")
        _h("═══════════════════════════════")
        _h(f"  Züge: {_game.game_moves}")
        _h(f"  Punkte: {_game.game_score}")
        _h(f"  Spielzeit: {_game.format_elapsed_time()}")
        _h("")
        return True

    if cmd in ('q', 'quit', 'beenden'):
        _h("═══ SPIELENDE ═══")
        _h(f"Punkte: {_game.game_score}")
        _h(f"Züge: {_game.game_moves}")
        _h(f"Spielzeit: {_game.format_elapsed_time()}")
        _h("")
        _h("Willst du wirklich beenden? (Tippe 'neu' für Neustart)")
        _h("")
        return True

    if cmd in ('save', 'speicher', 'speichern'):
        _game.save_game()
        return True

    if cmd in ('restore', 'laden'):
        _game.restore_game()
        return True

    if cmd in ('score', 'punkte'):
        _h(f"Punkte: {_game.game_score}")
        _h(f"Züge: {_game.game_moves}")
        _h("")
        return True

    if cmd == 'zeit':
        _h(f"Spielzeit: {_game.format_elapsed_time()}")
        ticks_total = pygame.time.get_ticks() - _game.game_start_ticks
        _h(f"Pygame Ticks: {ticks_total}")
        _h("")
        return True

    if cmd in ('diagnose', 'd'):
        _h("═══ DIAGNOSE ═══")
        _h(_game.get_health_description())
        _h(_game.get_strength_description())
        hunger_desc = _game.get_hunger_description()
        if hunger_desc:
            _h(hunger_desc)
        if _game.player_stats['equipped_weapon']:
            w = weapons[_game.player_stats['equipped_weapon']]
            _h(f"Waffe: {w['name']}")
        else:
            _h("Waffe: Keine")
        _h(f"Kampfstatus: {'IM KAMPF' if _game.player_stats['in_combat'] else 'Sicher'}")
        enc = _game.get_encumbrance_description()
        if enc:
            _h(enc)
        for litem in _game.player_inventory:
            lidef = _game.ITEM_DEFS.get(litem)
            if lidef and lidef.max_charge >= 0:
                if lidef.charge <= 0:
                    _h(f"{lidef.name}: Erloschen")
                elif lidef.charge <= 20:
                    _h(f"{lidef.name}: Schwaches Licht")
                else:
                    _h(f"{lidef.name}: Leuchtet")
        _h("")
        return True

    return False


# ========================
# INTERACTION COMMANDS
# ========================
def _has_any(text, *needles):
    """True wenn mindestens eines der Suchwörter in text vorkommt."""
    return any(n in text for n in needles)


def _has_all(text, *needles):
    """True wenn alle Suchwörter in text vorkommen."""
    return all(n in text for n in needles)


def handle_interaction_commands(cmd):
    """Handles: schieben, aufbrechen, Türen, Schubladen, Safe, Numpad.

    Eingaben sind bereits lowercased; lange Wörter wie „bücherregal“ bleiben erhalten.
    """

    # ------------------------------------------------------------
    # NUMPAD: Code-Eingabe — wird als nächster Befehl erwartet.
    # Wir benutzen kein input() (das würde pygame einfrieren),
    # sondern setzen ein Flag und werten den NÄCHSTEN Befehl aus.
    # ------------------------------------------------------------
    if getattr(_game, 'numpad_awaiting_code', False):
        _game.numpad_awaiting_code = False
        code_str = cmd.strip()
        if code_str.isdigit():
            if int(code_str) == 250804831:
                _game.numpad_nutzen = True
                _game.unlock_transition('krankenhaus_geheim_treppe')
                _h("Du tippst die Ziffern langsam ein...")
                _h("Klick. *Beep* Die Tür summt — und öffnet sich.")
                _h("")
            else:
                _h("Falscher Code. Die Tür bleibt verschlossen.")
                _h("")
        else:
            _h("Numpad-Eingabe abgebrochen.")
            _h("")
        return True

    # ------------------------------------------------------------
    # BIBLIOTHEK: Bücherregal schieben
    # ------------------------------------------------------------
    if _has_any(cmd, 'schieb', 'beweg') and _has_any(cmd, 'regal', 'bücherregal'):
        if _game.current_room == 'bibliothek_3':
            if not _game.bibliothek_4_schrank_geschoben:
                _game.bibliothek_4_schrank_geschoben = True
                _game.unlock_transition('bib_3_4')
                _h("Du stemmst dich gegen das schwere Bücherregal...")
                _h("Mit aller Kraft schiebst du es zur Seite!")
                _h("Der Weg nach NORDEN ist jetzt frei.")
                _h("")
            else:
                _h("Das Bücherregal wurde bereits zur Seite geschoben.")
                _h("")
            return True
        _h("Hier gibt es kein Bücherregal zum Schieben.")
        _h("")
        return True

    # ------------------------------------------------------------
    # KRANKENHAUS: Schrank schieben (Labor)
    # ------------------------------------------------------------
    if _has_any(cmd, 'schieb', 'beweg') and 'schrank' in cmd and 'nachtschr' not in cmd:
        in_hospital_labor_area = (
            _game.current_room in ('krankenhaus_labor', 'krankenhaus_Labor')
            or str(_game.current_room).startswith('krankenhaus_labor')
        )
        if in_hospital_labor_area:
            if not _game.krankenhaus_schrank_geschoben:
                _game.krankenhaus_schrank_geschoben = True
                _game.unlock_transition('krankenhaus_geheim_treppe')
                _h("Du schiebst den Schrank langsam zur Seite...")
                _h("Dahinter ist eine Tür mit einem Nummern-Pad.")
                _h("Ein kleines Fenster zeigt eine Treppe nach unten.")
                _h("")
            else:
                _h("Der Schrank ist bereits aus dem Weg.")
                _h("")
            return True
        if str(_game.current_room).startswith('krankenhaus_'):
            _h("Hier steht kein relevanter Schrank.")
            _h("")
            return True
        _h("Hier ist kein Schrank zum Schieben.")
        _h("")
        return True

    # ------------------------------------------------------------
    # "schieben" ohne Objekt -> erkenne anhand des Raums
    # ------------------------------------------------------------
    if cmd in ('schieb', 'schieben'):
        if _game.current_room == 'bibliothek_3':
            return handle_interaction_commands('schiebe regal')
        if str(_game.current_room).startswith('krankenhaus_labor'):
            return handle_interaction_commands('schiebe schrank')
        _h("Was möchtest du schieben?")
        _h("")
        return True

    # ------------------------------------------------------------
    # HAUS1: Tür mit Axt aufbrechen
    # ------------------------------------------------------------
    if (
        ('tür' in cmd and _has_any(cmd, 'aufbreche', 'aufschlag', 'aufschalg', 'zerhacke'))
        or _has_all(cmd, 'brech', 'auf')
        or (_has_any(cmd, 'schlag', 'schlage') and 'tür' in cmd)
    ):
        if _game.current_room == 'haus1':
            if 'axt' not in _game.player_inventory:
                _h("Du brauchst etwas Schweres, um die Tür aufzubrechen — eine Axt vielleicht.")
                _h("")
                return True
            if not _game.haus1_tür_auf:
                _game.haus1_tür_auf = True
                _game.unlock_transition('haus1_tür')
                _h("Du nimmst die Axt fest in beide Hände.")
                _h("Mit voller Wucht schlägst du auf die Tür ein!")
                _h("Splitter fliegen — der Weg ins Haus ist frei.")
                _h("")
            else:
                _h("Die Tür ist bereits aufgebrochen.")
                _h("")
            return True
        _h("Hier ist keine verschlossene Tür zum Aufbrechen.")
        _h("")
        return True

    # ------------------------------------------------------------
    # HAUS1: Dachbodentür mit Gehstock herunterziehen
    # ------------------------------------------------------------
    if 'dachboden' in cmd and _has_any(cmd, 'ziehe', 'runter', 'öffne', 'oeffne', 'gehstock'):
        if _game.current_room == 'haus1_dachbodentür':
            if 'gehstock' not in _game.player_inventory:
                _h("Der Griff der Dachbodentür ist zu hoch — du brauchst etwas Langes wie einen Gehstock.")
                _h("")
                return True
            if not _game.haus1_dachbodentür_auf:
                _game.haus1_dachbodentür_auf = True
                _game.unlock_transition('haus1_dachbodentür')
                _h("Du nimmst den Gehstock und hakst ihn in den Griff der Dachbodentür.")
                _h("Mit einem festen Ruck öffnet sich die Klappe — die Leiter klappt herunter.")
                _h("")
            else:
                _h("Die Dachbodentür ist bereits offen.")
                _h("")
            return True
        _h("Hier gibt es keine Dachbodentür.")
        _h("")
        return True

    # ------------------------------------------------------------
    # HAUS1: Nachtschrank öffnen
    # Substring 'nachtschr' matcht sowohl 'nachtschrank' als auch Teil-Eingaben (kein Längen-Limit).
    # ------------------------------------------------------------
    if 'nachtschr' in cmd and _has_any(cmd, 'öffne', 'oeffne', 'auf'):
        if _game.current_room == 'haus1_schlafzimmer':
            if not _game.nachtschrank_auf:
                _game.nachtschrank_auf = True
                _game.unlock_transition('haus1_schlafzimmer_nachtschrank')
                _h("Du ziehst die Schublade des Nachtschrankes auf.")
                _h("Ein Zettel liegt darin.")
                _h("Auf dem Zettel steht eine Kombination für einen Safe: 123456")
                _h("")
            else:
                _h("Die Schublade ist bereits auf.")
                _h("")
            return True
        _h("Hier gibt es keinen Nachtschrank.")
        _h("")
        return True

    # ------------------------------------------------------------
    # HAUS1: Safe öffnen
    # ------------------------------------------------------------
    if 'safe' in cmd and _has_any(cmd, 'öffne', 'oeffne', 'auf') and 'durchsuch' not in cmd:
        if _game.current_room != 'haus1_dachboden':
            _h("Hier gibt es keinen Safe.")
            _h("")
            return True
        if not _game.nachtschrank_auf:
            _h("Du kennst die Kombination nicht. Du müsstest sie erst irgendwo finden.")
            _h("")
            return True
        if _game.safe_auf_haus1:
            _h("Der Safe ist bereits offen.")
            _h("")
            return True
        _game.safe_auf_haus1 = True
        _game.unlock_transition('haus1_dachboden_safe')
        _h("Du gibst die Kombination langsam ein.")
        _h("Bei jeder richtigen Zahl ertönt ein leises Klicken.")
        _h("Nach der letzten Ziffer hörst du ein lautes Klick — der Safe öffnet sich.")
        _h("")
        return True

    # ------------------------------------------------------------
    # HAUS1: Safe durchsuchen
    # ------------------------------------------------------------
    if 'safe' in cmd and 'durchsuch' in cmd:
        if _game.current_room != 'haus1_dachboden':
            _h("Hier gibt es keinen Safe.")
            _h("")
            return True
        if not _game.safe_auf_haus1:
            _h("Der Safe ist verschlossen — du musst ihn erst öffnen.")
            _h("")
            return True
        if _game.safe_durchsucht_haus1:
            _h("Den Safe hast du bereits durchsucht. Er ist leer.")
            _h("")
            return True
        _game.safe_durchsucht_haus1 = True
        _h("Im Safe liegen 50 Schuss Munition.")
        _h("Du steckst sie ein.")
        _h("")
        return True

    # ------------------------------------------------------------
    # KRANKENHAUS: Numpad benutzen
    # ------------------------------------------------------------
    if _has_any(cmd, 'numpad', 'nummernpad') or _has_all(cmd, 'nummern', 'pad'):
        in_lab_area = (
            str(_game.current_room).startswith('krankenhaus_labor')
            or _game.current_room in ('krankenhaus_Labor', 'krankenhaus_geheim_treppe')
        )
        if not in_lab_area:
            _h("Hier ist kein Nummern-Pad.")
            _h("")
            return True
        if not _game.krankenhaus_schrank_geschoben:
            _h("Das Nummern-Pad ist hinter dem Schrank. Schiebe erst den Schrank zur Seite.")
            _h("")
            return True
        if _game.numpad_nutzen:
            _h("Die Tür hinter dem Numpad ist bereits offen.")
            _h("")
            return True
        _game.numpad_awaiting_code = True
        _h("Du legst deine Hand auf das Nummern-Pad.")
        _h("Tippe die 8 Ziffern als nächsten Befehl ein.")
        _h("(Beispiel: 12345678)")
        _h("")
        return True

    # ------------------------------------------------------------
    # COFFEESHOP: Tür mit Schlüssel öffnen
    # ------------------------------------------------------------
    if _game.current_room == 'gasse_ende':
        is_open_cmd = _has_any(cmd, 'öffne', 'oeffne', 'auf', 'nutze', 'benutze', 'unlock')
        is_door_target = _has_any(cmd, 'tür', 'tur', 'coffeeshop', 'coffee', 'schlüssel', 'schlussel')
        if is_open_cmd and is_door_target:
            if _game.coffeeshop_tür_auf:
                _h("Die Tür ist bereits offen.")
                _h("")
                return True
            if 'coffeeshop_schlüssel' not in _game.player_inventory:
                _h("Die Tür ist fest verschlossen. Du brauchst wohl einen passenden Schlüssel.")
                _h("")
                return True
            _game.coffeeshop_tür_auf = True
            _game.unlock_transition('coffeeshop_tür')
            _h("Du steckst den Schlüssel ins Schloss.")
            _h("Ein leises Klicken — die schwere Holztür schwingt auf.")
            _h("Dahinter liegt ein verlassener Coffeeshop.")
            _h("")
            return True

    # ------------------------------------------------------------
    # CHRISTOPHER THOMSON — Dialog & Untersuchung
    # Raum: coffeeshop
    # Befehle: spreche/rede/grüß mit christopher, untersuche christopher/mann
    # ------------------------------------------------------------
    # Hinweis: Wörter werden NICHT mehr gekürzt. Die Präfixe 'christoph'/'überleben'
    # matchen per Substring-Check trotzdem die vollen Eingaben.
    _CHRISTOPHER_CMDS = (
        _has_any(cmd, 'spreche', 'sprich', 'rede', 'grüße', 'grüß', 'hallo', 'hi') and
        _has_any(cmd, 'christoph', 'thomson', 'mann', 'typ', 'kerl', 'überleben')
    )
    _CHRISTOPHER_EXAMINE = (
        _has_any(cmd, 'untersuche', 'untersuchen', 'schau') and
        _has_any(cmd, 'christoph', 'thomson', 'mann', 'typ', 'kerl')
    )

    if (_CHRISTOPHER_CMDS or _CHRISTOPHER_EXAMINE) and _game.current_room == 'coffeeshop':

        idx = getattr(_game, 'christopher_dialog_index', 0)

        # Untersuchungs-Beschreibung (immer verfügbar)
        if _CHRISTOPHER_EXAMINE and not _CHRISTOPHER_CMDS:
            _h("Christopher Thomson, 32 Jahre alt, etwa 190 cm groß.")
            _h("Ein großer, kräftiger Mann mit vollem Bart und rissigen Händen —")
            _h("die Hände eines Farmers. Seine Kleider sind zerschlissen aber sauber.")
            _h("In seinen Augen liegt eine Mischung aus Erleichterung und tiefer Erschöpfung.")
            _h("")
            return True

        # Dialog-Sequenz
        if idx == 0:
            _h('Christopher nickt dir zögernd zu.')
            _h('"Ich heiße Christopher. Christopher Thomson. Freut mich, dich zu treffen —"')
            _h('Er lacht kurz auf, fast ungläubig.')
            _h('"Weißt du, wie lange ich das nicht mehr sagen konnte?"')
            _h("")
            _h('"Zwei Jahre. Zwei Jahre lebe ich jetzt in einem Bunker meiner Großeltern.')
            _h('Den haben sie damals im Zweiten Weltkrieg gebaut. Massiv. Sicher."')
            _h("")
            _h('"Aber irgendwann braucht man Vorräte. Und so lande ich hier."')
            _h('Er deutet auf die geplünderte Vitrine.')
            _h('"Nicht viel geblieben."')
            _h("")
            _game.christopher_dialog_index = 1

        elif idx == 1:
            _h('Du fragst Christopher nach dem Anfang.')
            _h("")
            _h('Sein Blick wird schwerer.')
            _h('"Der erste Tag... meinen Opa habe ich sterben sehen."')
            _h('Er schluckt. Pause.')
            _h('"Er wollte den Nachbarn helfen. Der schien verletzt. Aber er war es schon —"')
            _h('Christopher schüttelt den Kopf.')
            _h('"Ich konnte nichts tun. Ich hab einfach... weggerannt."')
            _h("")
            _h('Er reibt sich die Augen.')
            _h('"Seitdem lebe ich damit. Aber ich lebe. Das muss reichen."')
            _h("")
            _game.christopher_dialog_index = 2

        elif idx == 2:
            _h('Du fragst ihn nach dem Bunker.')
            _h("")
            _h('"Meine Großeltern haben ihn 1943 gebaut. Unter dem Bauernhof."')
            _h('"Strom über einen Generator, Wasservorrat — genug für Monate."')
            _h('"Mein Vater hat mir als Kind alles gezeigt. Zum Glück."')
            _h("")
            _h('"Ich kenne mich mit Landwirtschaft aus. Ich weiß, was man essen kann,')
            _h('wie man Wasser filtert, wie man Fallen stellt."')
            _h('Er klopft auf einen kleinen Rucksack neben ihm.')
            _h('"Das Wissen meiner Familie hat mich am Leben gehalten."')
            _h("")
            _game.christopher_dialog_index = 3

        elif idx == 3:
            _h('Du fragst, ob er sich dir anschließen möchte.')
            _h("")
            _h('Christopher sieht dich lange an.')
            _h('"Alleine ist man draußen so gut wie tot. Das weiß ich."')
            _h('"Und du... du scheinst zu wissen, was du tust."')
            _h("")
            _h('Er streckt dir die Hand entgegen.')
            _h('"Abgemacht. Wohin auch immer du gehst — ich bin dabei."')
            _h("")
            _h('[Christopher Thomson ist jetzt dein Begleiter.]')
            _h('[Im Kampf: 25% Chance Angriffe abzufangen, +10% Fernkampf-Genauigkeit]')
            _h("")
            _game.christopher_dialog_index = 4
            _game.player_stats['companion'] = 'christopher'
            _game.player_stats['companion_hp'] = 100
            _game.player_stats['companion_stunned_turns'] = 0

        else:
            _h('Christopher nickt dir ruhig zu.')
            _h('"Ich bin bereit, wenn du es bist."')
            _h('"Sag einfach, wenn es weitergehen soll."')
            _h("")

        return True

    elif (_CHRISTOPHER_CMDS or _CHRISTOPHER_EXAMINE) and _game.current_room != 'coffeeshop':
        comp = _game.player_stats.get('companion')
        if comp == 'christopher':
            _h('Christopher sieht dich kurz an.')
            _h('"Alles klar? Ich bin dabei — ruf mich, wenn du mich brauchst."')
            _h("")
        elif comp == 'christopher_waiting':
            _h('"Ich warte hier auf dich. Ruf mich, wenn es weitergeht."')
            _h("[Tippe 'folge mir' um ihn wieder zu aktivieren.]")
            _h("")
        else:
            _h("Christopher ist nicht in der Nähe.")
            _h("Du kannst ihn im Coffeeshop treffen.")
            _h("")
        return True

    # ------------------------------------------------------------------
    # BEGLEITER-MANAGEMENT: folge mir / bleib hier / begleiter status / gruppe
    # ------------------------------------------------------------------
    _IS_EMILIA_CMD = _has_any(cmd, 'emilia', 'albrecht', 'mädchen')
    _IS_HELENE_CMD = _has_any(cmd, 'helene', 'oma', 'großmutt', 'großmutter', 'alte')
    _FOLLOW_CMD  = (
        _has_any(cmd, 'folge', 'komm', 'begleite') and
        _has_any(cmd, 'mir', 'mich', 'christoph') and
        not _IS_EMILIA_CMD and not _IS_HELENE_CMD
    )
    _STAY_CMD    = (
        _has_any(cmd, 'bleib', 'warte', 'halt') and
        _has_any(cmd, 'hier', 'christoph', 'stop') and
        not _IS_EMILIA_CMD and not _IS_HELENE_CMD
    )
    _COMP_STATUS = _has_any(cmd, 'begleiter', 'companion', 'christopher') and _has_any(cmd, 'status', 'zustand', 'hp', 'leben')
    _BONI_STATUS = _has_any(cmd, 'boni', 'bonus', 'buffs', 'buff', 'stärke', 'aktiv') and _has_any(cmd, 'status', 'zeig', 'liste', 'aktiv', 'boni', 'bonus')
    _GRUPPE_STATUS = _has_any(cmd, 'gruppe', 'group', 'team', 'begleiter', 'gefährten', 'wer', 'folgt') and \
                     _has_any(cmd, 'gruppe', 'group', 'team', 'mir', 'dabei', 'folgt', 'status', 'liste', 'zeig')

    if _GRUPPE_STATUS and not _COMP_STATUS:
        comp         = _game.player_stats.get('companion')
        emilia_f     = _game.player_stats.get('emilia_following', False)
        helene_f     = _game.player_stats.get('helene_following', False)
        emilia_met   = getattr(_game, 'emilia_getroffen', False)
        c_verletzt   = getattr(_game, 'christopher_verletzt', False)
        e_entführt   = getattr(_game, 'friedhof_event_abgeschlossen', False) and not emilia_f
        h_tot        = getattr(_game, 'friedhof_event_abgeschlossen', False) and not helene_f and emilia_met

        _h("=== GRUPPE ===")

        # Christopher
        if comp == 'christopher':
            hp = _game.player_stats.get('companion_hp', 100)
            stunned = _game.player_stats.get('companion_stunned_turns', 0)
            zustand = "Schwer verletzt" if c_verletzt else ("Betäubt" if stunned > 0 else "Einsatzbereit")
            _h(f"Christopher Thomson  — folgt dir  [HP: {hp}/100 | {zustand}]")
        elif comp == 'christopher_waiting':
            _h("Christopher Thomson  — wartet  ['folge mir' zum Reaktivieren]")
        else:
            _h("Christopher Thomson  — nicht dabei")

        # Emilia
        if not emilia_met:
            _h("Emilia Albrecht      — unbekannt")
        elif e_entführt:
            _h("Emilia Albrecht      — ENTFÜHRT vom Strecker")
        elif emilia_f:
            _h("Emilia Albrecht      — folgt dir  [Liebeskraft aktiv]")
        else:
            _h("Emilia Albrecht      — wartet  ['folge mir emilia']")

        # Helene
        if not emilia_met:
            _h("Helene Albrecht      — unbekannt")
        elif h_tot:
            _h("Helene Albrecht      — TOT (Friedhof)")
        elif helene_f:
            _h("Helene Albrecht      — folgt dir  [Kräuterheilung aktiv]")
        else:
            _h("Helene Albrecht      — wartet  ['folge mir helene']")

        _h("")
        return True

    if _FOLLOW_CMD:
        comp = _game.player_stats.get('companion')
        if not comp:
            _h("Du hast keinen Begleiter.")
            _h("Finde Christopher im Coffeeshop und sprich mit ihm.")
            _h("")
        elif comp == 'christopher_waiting':
            _game.player_stats['companion'] = 'christopher'
            _h("Christopher schließt sich dir wieder an.")
            _h(f"HP: {_game.player_stats['companion_hp']}/100")
            _h("")
        else:
            _h("Christopher folgt dir bereits.")
            _h(f"HP: {_game.player_stats['companion_hp']}/100")
            stunned = _game.player_stats.get('companion_stunned_turns', 0)
            if stunned > 0:
                _h(f"Status: Verletzt — erholt sich in {stunned} Zügen.")
            else:
                _h("Status: Einsatzbereit")
            _h("")
        return True

    if _STAY_CMD:
        comp = _game.player_stats.get('companion')
        if not comp:
            _h("Du hast keinen Begleiter.")
            _h("")
        elif comp == 'christopher_waiting':
            _h("Christopher wartet bereits.")
            _h("")
        else:
            if _game.current_room in OUTDOOR_ROOMS:
                _h('Christopher schüttelt den Kopf.')
                _h('"Draußen bleiben? Nein. Da draußen bin ich ein leichtes Ziel."')
                _h('"Sag mir wenn wir in einem Gebäude sind — dann warte ich gerne."')
                _h("")
            else:
                _h("Christopher nickt. Er wartet hier auf dich.")
                _h("[Begleiter-Boni temporär deaktiviert — 'folge mir' zum Reaktivieren]")
                _game.player_stats['companion'] = 'christopher_waiting'
                _h("")
        return True

    if _COMP_STATUS:
        comp = _game.player_stats.get('companion')
        if not comp:
            _h("Du hast keinen aktiven Begleiter.")
            _h("")
        elif comp == 'christopher_waiting':
            _h("Christopher wartet irgendwo auf dich.")
            _h("Tippe 'folge mir' um ihn wieder zu aktivieren.")
            _h("")
        else:
            hp = _game.player_stats['companion_hp']
            stunned = _game.player_stats.get('companion_stunned_turns', 0)
            _h("=== BEGLEITER: Christopher Thomson ===")
            _h(f"HP: {hp}/100")
            _h(f"Status: {'Verletzt (' + str(stunned) + ' Züge)' if stunned > 0 else 'Einsatzbereit'}")
            _h("Kampf-Boni:")
            _h("  - 25% Chance Gegenangriff abzufangen (-50% Schaden)")
            _h("  - +10% Fernkampf-Genauigkeit")
            _h("  - Passive HP-Regen nach Kämpfen")
            _h("")
            if getattr(_game, 'emilia_getroffen', False):
                emilia_f = _game.player_stats.get('emilia_following', False)
                helene_f = _game.player_stats.get('helene_following', False)
                if emilia_f or helene_f:
                    _h("Zusatz-Boni:")
                    if emilia_f:
                        _h("  - Emilia: +10 Schaden [Liebeskraft — AKTIV]")
                    if helene_f:
                        _h("  - Helene: +8 HP/Treffer [Kräuterheilung — AKTIV]")
                    _h("")
        return True

    if _BONI_STATUS:
        emilia_met = getattr(_game, 'emilia_getroffen', False)
        comp = _game.player_stats.get('companion')
        emilia_follow = _game.player_stats.get('emilia_following', False)
        helene_follow = _game.player_stats.get('helene_following', False)
        has_any = comp or emilia_met
        if not has_any:
            _h("Keine bekannten Verbündeten.")
            _h("Finde Verbündete um Kampf-Boni freizuschalten.")
            _h("")
        else:
            _h("=== KAMPF-BONI ÜBERSICHT ===")
            if comp and comp != 'christopher_waiting':
                _h("Christopher Thomson [AKTIV]:")
                _h("  - 50% Schaden abfangen")
                _h("  - HP-Regen nach Kämpfen")
            elif comp == 'christopher_waiting':
                _h("Christopher Thomson [WARTET — folge mir]")
            if emilia_met:
                status_e = "AKTIV" if emilia_follow else "WARTET — 'folge mir emilia'"
                _h(f"Emilia Albrecht [{status_e}]:")
                _h("  - +10 Schaden pro Angriff [Liebeskraft]")
                status_h = "AKTIV" if helene_follow else "WARTET — 'folge mir helene'"
                _h(f"Helene Albrecht [{status_h}]:")
                _h("  - +8 HP nach jedem Feindtreffer [Kräuterheilung]")
            _h("")
        return True

    # ------------------------------------------------------------------
    # EMILIA ALBRECHT — Dialog & Untersuchung (Waldhaus)
    # Befehle: rede/spreche/hallo mit emilia / mädchen / frau
    # Untersuche: untersuche emilia / junge frau / albrecht
    # ------------------------------------------------------------------
    _EMILIA_CMDS = (
        _has_any(cmd, 'spreche', 'sprich', 'rede', 'grüße', 'grüß', 'hallo', 'hi') and
        _has_any(cmd, 'emilia', 'mädchen', 'albrecht')
    )
    _EMILIA_EXAMINE = (
        _has_any(cmd, 'untersuche', 'untersuchen', 'schau', 'betracht') and
        _has_any(cmd, 'emilia', 'mädchen', 'albrecht')
    )

    if (_EMILIA_CMDS or _EMILIA_EXAMINE) and _game.current_room == 'waldhaus':
        if not getattr(_game, 'emilia_getroffen', False):
            _h("Du musst erst ins Waldhaus hineingehen.")
            _h("")
            return True

        if _EMILIA_EXAMINE and not _EMILIA_CMDS:
            _h("Emilia Albrecht, 26 Jahre alt, etwa 167 cm groß.")
            _h("Dunkles, schulterlanges Haar, ruhige braune Augen.")
            _h("Ihre Kleidung ist schlicht und praktisch — selbst geflickt,")
            _h("aber sauber. Sie trägt einen kleinen Beutel mit Kräutern am Gürtel.")
            _h("Etwas an ihr ist schwer in Worte zu fassen —")
            _h("eine Ruhe, die man in der Apokalypse selten findet.")
            _h("")
            return True

        idx = getattr(_game, 'emilia_dialog_index', 0)

        if idx == 0:
            _h('Emilia sieht dich kurz an — abschätzend, aber nicht feindlich.')
            _h('"Wie lange seid ihr schon unterwegs?"')
            _h('Sie wischt ihre Hände an einem Tuch ab.')
            _h('"Wir sind seit dem ersten Tag hier. Meine Großmutter kennt den')
            _h('Wald wie ihre Westentasche — das hat uns am Leben gehalten."')
            _h("")
            _h('"Die Stadt... die meide ich. Zu gefährlich. Zu laut."')
            _h('Sie schaut kurz Richtung Nebenraum.')
            _h('"Hier ist es still. Und still bedeutet sicher."')
            _h("")
            _game.emilia_dialog_index = 1

        elif idx == 1:
            _h('Du fragst sie nach dem Anfang der Pandemie.')
            _h("")
            _h('Emilia schweigt einen Moment lang.')
            _h('"Ich habe meiner Großmutter einen Schwur gegeben.')
            _h('Dass ich sie nicht alleine lasse. Dass ich sie schütze."')
            _h("")
            _h('Ihr Blick wird kurz irgendwo anders.')
            _h('"Helene ist nicht mehr die Jüngste. Und die Welt draußen ist')
            _h('nicht mehr... die Welt, in der sie aufgewachsen ist."')
            _h("")
            _h('"Also bleiben wir hier."')
            _h("")
            if _game.player_stats.get('companion') == 'christopher':
                _h('Christopher lehnt an der Wand und hört zu.')
                _h('Er sagt nichts, aber du siehst wie sein Blick an Emilia')
                _h('hängenbleibt — einen Atemzug zu lang.')
                _h("")
            _game.emilia_dialog_index = 2

        elif idx == 2:
            _h('Du fragst, wie sie sich versorgen.')
            _h("")
            _h('"Meine Großmutter weiß alles über Heilpflanzen. Über Konservieren.')
            _h('Sie hat mir beigebracht, was ich wissen muss."')
            _h('Emilia deutet auf einen Tisch voller getrockneter Kräuter.')
            _h('"Infektionen behandeln, Fieber senken, Schmerzen lindern."')
            _h("")
            _h('Sie zögert kurz — dann:')
            _h('"Helene ist... zäher als sie aussieht."')
            _h('Es klingt wie eine Warnung und ein Versprechen zugleich.')
            _h("")
            _game.emilia_dialog_index = 3

        elif idx == 3:
            _h('Du fragst Emilia, ob sie und Helene alleine hierher kamen.')
            _h("")
            _h('"Wir hatten andere. Am Anfang."')
            _h('Pause.')
            _h('"Jetzt sind es nur noch wir zwei."')
            _h("")
            _h('Keine weiteren Worte. Ihr Blick sagt genug.')
            _h("")
            if _game.player_stats.get('companion') == 'christopher':
                _h('Christopher räuspert sich.')
                _h('"Falls ihr jemals... Verstärkung braucht."')
                _h('Es klingt beiläufig. Es ist es nicht.')
                _h("")
            _game.emilia_dialog_index = 4

        else:
            _h('Emilia nickt dir ruhig zu.')
            _h('"Wir sind hier, wenn ihr uns braucht."')
            _h("")

        return True

    elif (_EMILIA_CMDS or _EMILIA_EXAMINE) and _game.current_room != 'waldhaus':
        if getattr(_game, 'emilia_getroffen', False):
            _h("Emilia ist nicht hier. Du findest sie im Waldhaus.")
        else:
            _h("Diesen Namen kennst du noch nicht.")
        _h("")
        return True

    # ------------------------------------------------------------------
    # HELENE ALBRECHT — Dialog & Untersuchung (Waldhaus)
    # Befehle: rede/spreche/hallo mit helene / oma / großmutter
    # Präfix 'großmutt' matcht per Substring auch das volle 'großmutter' (kein Längen-Limit).
    # ------------------------------------------------------------------
    _HELENE_CMDS = (
        _has_any(cmd, 'spreche', 'sprich', 'rede', 'grüße', 'grüß', 'hallo', 'hi') and
        _has_any(cmd, 'helene', 'oma', 'großmutt', 'großmutter', 'ältere', 'alte')
    )
    _HELENE_EXAMINE = (
        _has_any(cmd, 'untersuche', 'untersuchen', 'schau', 'betracht') and
        _has_any(cmd, 'helene', 'oma', 'großmutt', 'großmutter', 'ältere', 'alte')
    )

    if (_HELENE_CMDS or _HELENE_EXAMINE) and _game.current_room == 'waldhaus':
        if not getattr(_game, 'emilia_getroffen', False):
            _h("Du musst erst ins Waldhaus hineingehen.")
            _h("")
            return True

        if _HELENE_EXAMINE and not _HELENE_CMDS:
            _h("Helene Albrecht, 63 Jahre alt, etwa 154 cm groß.")
            _h("Weiß-silbernes Haar, zurückgesteckt. Kleine, wache Augen.")
            _h("Ihre Hände — die Hände einer Frau, die ihr Leben lang gearbeitet hat —")
            _h("bewegen sich langsam aber sicher zwischen ihren Kräutern.")
            _h("Am linken Unterarm, knapp unter dem Ärmel, etwas das wie eine alte")
            _h("Narbe aussieht. Sie zieht den Stoff darüber, bevor du genauer")
            _h("hinschauen kannst.")
            _h("")
            return True

        idx = getattr(_game, 'helene_dialog_index', 0)

        if idx == 0:
            _h('Helene schaut dich über die Schulter kurz an.')
            _h('Ihr Blick ist direkt — der Blick von jemandem, der Menschen')
            _h('einschätzen kann.')
            _h("")
            _h('"Setzt euch", sagt sie schließlich.')
            _h('"Ein Mensch, der steht und redet, schläft schlecht."')
            _h("")
            _h('Sie stellt zwei alte Tassen auf den Tisch.')
            _h('"Kräutertee. Kein Zucker mehr. Aber warm."')
            _h("")
            _game.helene_dialog_index = 1

        elif idx == 1:
            _h('Du fragst Helene nach dem Wald — wie sie ihn so gut kennen.')
            _h("")
            _h('"Ich bin hier groß geworden. Meine Mutter hat mir jeden Baum')
            _h('gezeigt, jede Pflanze, jede Beere."')
            _h('Sie lächelt — kurz, aber echt.')
            _h('"Damals dachte ich, das wäre nur... Heimatkunde."')
            _h("")
            _h('Sie faltet die Hände auf dem Tisch.')
            _h('"Nun ja. Jetzt weiß ich es besser."')
            _h("")
            _game.helene_dialog_index = 2

        elif idx == 2:
            _h('Du fragst sie nach ihrem Befinden — sie wirkt manchmal müde.')
            _h("")
            _h('Helene hält kurz inne.')
            _h('"Ich bin alt. Alter macht müde."')
            _h('Ein kurzes Innehalten — kaum merklich.')
            _h('"Aber ich bin noch hier. Das reicht."')
            _h("")
            _h('Emilia, die am anderen Ende des Raumes steht,')
            _h('dreht sich kurz um. Ihr Blick streift dich — dann blickt sie')
            _h('schnell wieder weg.')
            _h("")
            _game.helene_dialog_index = 3

        else:
            _h('Helene nickt dir freundlich zu.')
            _h('"Passt aufeinander auf. Das ist das Einzige, was noch zählt."')
            _h("")

        return True

    elif (_HELENE_CMDS or _HELENE_EXAMINE) and _game.current_room != 'waldhaus':
        if getattr(_game, 'emilia_getroffen', False):
            if _game.player_stats.get('helene_following'):
                _h('Helene geht hinter dir. "Ich bin hier."')
            else:
                _h("Helene ist nicht hier. Du findest sie im Waldhaus.")
        else:
            _h("Diesen Namen kennst du noch nicht.")
        _h("")
        return True

    # ------------------------------------------------------------------
    # ALBRECHT-BEGLEITER: folge mir emilia/helene — bleib hier emilia/helene
    # ------------------------------------------------------------------
    _EMILIA_FOLLOW = (
        _has_any(cmd, 'folge', 'komm', 'begleite', 'mitkommen', 'mitkomm') and
        _has_any(cmd, 'emilia', 'albrecht', 'mädchen')
    )
    _EMILIA_STAY = (
        _has_any(cmd, 'bleib', 'warte', 'halt', 'stop') and
        _has_any(cmd, 'emilia', 'albrecht', 'mädchen')
    )
    _HELENE_FOLLOW = (
        _has_any(cmd, 'folge', 'komm', 'begleite', 'mitkommen', 'mitkomm') and
        _has_any(cmd, 'helene', 'oma', 'großmutt', 'großmutter', 'alte')
    )
    _HELENE_STAY = (
        _has_any(cmd, 'bleib', 'warte', 'halt', 'stop') and
        _has_any(cmd, 'helene', 'oma', 'großmutt', 'großmutter', 'alte')
    )

    if _EMILIA_FOLLOW:
        if not getattr(_game, 'emilia_getroffen', False):
            _h("Du kennst Emilia noch nicht.")
            _h("")
            return True
        if _game.player_stats.get('emilia_following'):
            _h('Emilia ist bereits bei dir.')
            _h('"Ich bin hier", sagt sie ruhig.')
            _h("")
        else:
            _game.player_stats['emilia_following'] = True
            _h('Emilia schaut dich kurz an, dann nickt sie.')
            _h('"Gut. Ich bleibe nicht gerne alleine hier."')
            _h("[Emilia folgt dir jetzt. Liebeskraft-Bonus aktiv.]")
            _h("")
        return True

    if _EMILIA_STAY:
        if not getattr(_game, 'emilia_getroffen', False):
            _h("Du kennst Emilia noch nicht.")
            _h("")
            return True
        if not _game.player_stats.get('emilia_following'):
            _h('Emilia wartet bereits.')
            _h("")
        elif _game.current_room in OUTDOOR_ROOMS:
            _h('Emilia schüttelt den Kopf.')
            _h('"Draußen bleiben? Alleine? Nein."')
            _h('"Sag mir wenn wir in einem Gebäude sind."')
            _h("")
        else:
            _game.player_stats['emilia_following'] = False
            _h('Emilia lehnt sich gegen die Wand.')
            _h('"Ich warte hier auf euch. Passt auf euch auf."')
            _h("[Emilia wartet. Liebeskraft-Bonus deaktiviert — 'folge mir emilia' zum Reaktivieren]")
            _h("")
        return True

    if _HELENE_FOLLOW:
        if not getattr(_game, 'emilia_getroffen', False):
            _h("Du kennst Helene noch nicht.")
            _h("")
            return True
        if _game.player_stats.get('helene_following'):
            _h('Helene geht bereits mit dir.')
            _h('"Ich bin noch dabei, keine Sorge."')
            _h("")
        else:
            _game.player_stats['helene_following'] = True
            _h('Helene seufzt kurz, dann steht sie auf.')
            _h('"Na gut. Ich bin alt, nicht tot."')
            _h('Sie packt ihren Kräuterbeutel zusammen.')
            _h("[Helene folgt dir jetzt. Kräuterheilung-Bonus aktiv.]")
            _h("")
        return True

    if _HELENE_STAY:
        if not getattr(_game, 'emilia_getroffen', False):
            _h("Du kennst Helene noch nicht.")
            _h("")
            return True
        if not _game.player_stats.get('helene_following'):
            _h('Helene wartet bereits.')
            _h("")
        elif _game.current_room in OUTDOOR_ROOMS:
            _h('Helene schüttelt entschieden den Kopf.')
            _h('"Draußen? In meinem Alter? Ich brauche ein Dach über dem Kopf."')
            _h("")
        else:
            _game.player_stats['helene_following'] = False
            _h('Helene setzt sich langsam auf einen Stuhl.')
            _h('"Gut. Meine Knie danken es euch."')
            _h("[Helene wartet. Kräuterheilung-Bonus deaktiviert — 'folge mir helene' zum Reaktivieren]")
            _h("")
        return True

    return False

# ========================
# CONTAINER COMMANDS
# ========================
def handle_container_commands(cmd):
    """Handles: öffne, schließe, lege...in, nimm...aus, schaue in"""

    if cmd.startswith('öffne ') or cmd.startswith('oeffne '):
        target = cmd.split(' ', 1)[1].strip()
        _game.handle_container_open(target)
        return True

    if cmd.startswith('schließ') or cmd.startswith('schliess'):
        parts = cmd.split(' ', 1)
        if len(parts) > 1:
            target = parts[1].strip()
            _game.handle_container_close(target)
        else:
            _h("Was willst du schließen?")
            _h("")
        return True

    if ' in ' in cmd and cmd.startswith('lege '):
        rest = cmd[5:].strip()
        parts = rest.split(' in ', 1)
        if len(parts) == 2:
            _game.handle_put_in(parts[0].strip(), parts[1].strip())
        else:
            _h("Format: lege [item] in [behälter]")
            _h("")
        return True

    if ' aus ' in cmd and cmd.startswith('nimm '):
        rest = cmd[5:].strip()
        parts = rest.split(' aus ', 1)
        if len(parts) == 2:
            _game.handle_take_from(parts[0].strip(), parts[1].strip())
        else:
            _h("Format: nimm [item] aus [behälter]")
            _h("")
        return True

    if cmd.startswith('schaue in ') or cmd.startswith('schau in '):
        target = cmd.split(' in ', 1)[1].strip()
        _game.handle_look_in(target)
        return True

    return False


# ========================
# EXAMINE COMMAND
# ========================
def handle_examine_command(cmd):
    """Handles: untersuche / untersuchen / u [objekt]
    Durchsucht den aktuellen Raum nach versteckten Details oder Items.
    """
    words = cmd.split()
    verb = words[0] if words else ''

    if verb not in ('untersuche', 'untersuchen', 'u'):
        return False

    obj = ' '.join(words[1:]).strip() if len(words) > 1 else ''
    room_key = _game.current_room

    # ── GASSE ENDE: Mülltonne / Boden / allgemein ──────────────────
    if room_key == 'gasse_ende':
        if _game.gasse_ende_untersucht:
            if obj:
                _h(f"Du hast den Bereich bereits gründlich untersucht. Außer dem Schlüssel findest du nichts mehr.")
            else:
                _h("Du hast das Gassenende bereits gründlich untersucht.")
            _h("")
            return True
        # Erster Untersuchungsversuch → Schlüssel enthüllen
        _game.gasse_ende_untersucht = True
        room = _game.rooms.get('gasse_ende', {})
        if 'coffeeshop_schlüssel' not in room.get('items', []):
            room.setdefault('items', []).append('coffeeshop_schlüssel')
        _h("Du schaust dich im Gassenende genauer um.")
        _h("")
        _h("Du kippst die umgestürzte Mülltonne zur Seite.")
        _h("Darunter, halb im Dreck vergraben, liegt ein kleiner Schlüssel.")
        _h("An der Schlaufe hängt ein verblasster Anhänger — eine Kaffeetasse.")
        _h("")
        _h("Du hast gefunden: Coffeeshop-Schlüssel")
        _h("")
        return True

    # ── SKYSCRAPER 1 LOBBY: Rezeptionstresen / Axt ─────────────────
    if room_key == 'skyscraper_1_lobby':
        if _game.skyscraper1_rezeption_untersucht:
            if obj:
                _h("Du hast die Lobby bereits gründlich durchsucht. Außer der Axt gibt es nichts mehr zu finden.")
            else:
                _h("Du hast die Lobby bereits gründlich untersucht.")
            _h("")
            return True
        _game.skyscraper1_rezeption_untersucht = True
        room = _game.rooms.get('skyscraper_1_lobby', {})
        if 'axt' not in room.get('items', []):
            room.setdefault('items', []).append('axt')
        _h("Du leuchtest hinter den Rezeptionstresen.")
        _h("")
        _h("Unter dem umgekippten Drehstuhl liegt eine Axt —")
        _h("das Blatt noch scharf, der Stiel mit getrocknetem Blut bedeckt.")
        _h("")
        _h("Du hast gefunden: Axt")
        _h("")
        return True

    # ── ALLGEMEINE UNTERSUCHUNG (andere Räume) ──────────────────────
    room = _game.rooms.get(room_key, {})
    room_name = room.get('name', room_key)

    if obj:
        # Spieler untersucht ein bestimmtes Objekt
        all_items = set(room.get('items', [])) | set(_game.player_inventory)
        if obj in all_items:
            idef = _game.ITEM_DEFS.get(obj)
            if idef:
                _h(f"Du untersuchst {idef.name} genauer.")
                _h(idef.description)
                _h("")
                return True
        _h(f"Hier gibt es kein '{obj}' zum Untersuchen.")
        _h("")
        return True

    # Allgemeine Raumuntersuchung — generische Reaktion
    items_here = room.get('items', [])
    _h(f"Du schaust dich in '{room_name}' genau um.")
    _h("")
    if items_here:
        sichtbare = [_game.get_item_name(i) for i in items_here]
        _h("Du bemerkst folgende Gegenstände: " + ", ".join(sichtbare) + ".")
    else:
        _h("Du durchsuchst den Raum gründlich. Nichts Besonderes fällt dir auf.")
    _h("")
    return True


# ========================
# LOOK / MAP (inline, small)
# ========================
def handle_look_map(cmd):
    """Handles: schaue/look/l, karte/map"""

    if cmd in ('schaue', 'look', 'l'):
        _game.describe_room()
        return True

    if cmd in ('karte', 'map'):
        bldg_name, bldg_title, floor = _game.get_room_context(_game.current_room)
        room_name = _game.rooms.get(_game.current_room, {}).get('name', _game.current_room)
        _h(">>> STANDORT INFO <<<")
        _h(f"Gebäude: {bldg_title}")
        _h(f"Etage:   {floor.capitalize()}")
        _h(f"Raum:    {room_name}")
        _h("")
        _h("Gefundene Ausgänge:")
        transitions = _game.get_transitions_from(_game.current_room)
        if not transitions:
            _h("  (Keine sichtbaren Ausgänge)")
        else:
            for d, tgt, t in transitions:
                tgt_name = _game.rooms.get(tgt, {}).get('name', tgt)
                t_type = t.get('type', 'passage')
                lock_str = " [VERSCHLOSSEN]" if t.get('locked') else ""
                icon = "🚪" if t_type in ('door', 'entrance') else "🪜" if t_type == 'stairs' else "➡️"
                _h(f"  {d.capitalize():<12} {icon} {tgt_name} {lock_str}")
        _h("")
        return True

    return False


# ========================
# GODMODE
# ========================
def handle_godmode(cmd, raw_cmd=None):
    """Handles: godmode (toggle), tp/teleport [raum] (nur im Godmode)

    raw_cmd: Rohversion des Befehls (vor der Wort-Auflösung),
             damit Raumnamen wie 'home_depot_sw' unversehrt ankommen.
    """
    if raw_cmd is None:
        raw_cmd = cmd

    # --- Godmode ein-/ausschalten ---
    if cmd == 'godmode':
        _game.player_stats['godmode'] = not _game.player_stats.get('godmode', False)
        if _game.player_stats['godmode']:
            _h("╔══════════════════════════════════╗")
            _h("║  *** GODMODE AKTIVIERT ***       ║")
            _h("║  One-Hit-Kills aktiv.            ║")
            _h("║  Kein Gegenschaden.              ║")
            _h("║  Teleport: tp [raumname]         ║")
            _h("╚══════════════════════════════════╝")
        else:
            _h("[ Godmode deaktiviert. ]")
        _h("")
        return True

    # --- Teleport (nur im Godmode) ---
    if raw_cmd.startswith('tp ') or raw_cmd.startswith('teleport '):
        if not _game.player_stats.get('godmode'):
            _h("Unbekannter Befehl. (Godmode nicht aktiv)")
            _h("")
            return True
        dest = raw_cmd.split(' ', 1)[1].strip()
        if dest not in _game.rooms:
            # Versuche Teilübereinstimmung
            matches = [k for k in _game.rooms if dest in k]
            if len(matches) == 1:
                dest = matches[0]
            elif len(matches) > 1:
                _h("Mehrdeutig. Meinst du einen davon?")
                for m in matches:
                    _h(f"  {m} — {_game.rooms[m].get('name', m)}")
                _h("")
                return True
            else:
                _h(f"Raum '{dest}' nicht gefunden.")
                _h("Tipp: Nutze den internen Raumnamen (z.B. 'corridor', 'storage', 'park').")
                _h("")
                return True
        _game.current_room = dest
        room_name = _game.rooms[dest].get('name', dest)
        _h(f"[GODMODE] Teleportiert nach: {room_name}")
        _h("")
        _game.describe_room()
        return True

    return False


# ========================
# REACTIVE PARSER (unknown commands)
# ========================
def handle_unknown_command(cmd, words):
    """Last-resort handler: reactive parser for unknown/ambiguous commands."""
    verb = words[0] if words else ''
    obj = ' '.join(words[1:]) if len(words) > 1 else ''
    room = _game.rooms[_game.current_room]
    all_known_items = set(_game.ITEM_DEFS.keys())
    room_items = set(room.get('items', []))
    inv_items = set(_game.player_inventory)

    # 1) Verb braucht Objekt aber keins angegeben
    if verb in VERBS_NEED_OBJECT and not obj:
        infinitiv = VERBS_NEED_OBJECT[verb]
        _h(f"Was willst du {infinitiv}?")
        _game.pending_ambiguity = {'action': verb, 'candidates': list(room_items | inv_items), 'original_cmd': verb}
        _h("")
        return

    # 2) Logisch unmögliche Aktionen
    if verb in ('esse', 'iss') and obj:
        if obj in weapons:
            _h(random.choice(ILLOGICAL_RESPONSES['eat_weapon']))
            _h("")
            return
        if obj in all_known_items and obj not in food_items:
            _h(random.choice(ILLOGICAL_RESPONSES['eat_inedible']))
            _h("")
            return
    if verb in ('ausrüsten',) and obj:
        if obj in food_items:
            _h(random.choice(ILLOGICAL_RESPONSES['equip_food']))
            _h("")
            return
        if obj in all_known_items and obj not in weapons:
            _h(random.choice(ILLOGICAL_RESPONSES['equip_non_weapon']))
            _h("")
            return

    # 3) Objekt existiert im Spiel aber nicht hier
    if obj and obj in all_known_items:
        if obj not in room_items and obj not in inv_items:
            _h(f"Du siehst hier kein '{_game.get_item_name(obj)}'.")
            _h("")
            return

    # 4) Partielle Objekterkennung / Disambiguation
    if obj:
        available = list(room_items | inv_items)
        matches = [it for it in available if obj in it or it.startswith(obj)]
        if len(matches) == 1 and verb in VERBS_NEED_OBJECT:
            _game.process_command(f"{verb} {matches[0]}")
            return
        elif len(matches) > 1:
            _h("Was meinst du?")
            for idx, m in enumerate(matches, 1):
                _h(f"  {idx}. {_game.get_item_name(m)}")
            _game.pending_ambiguity = {'action': verb, 'candidates': matches, 'original_cmd': cmd}
            _h("")
            return

    # 5) Unbekanntes Verb
    if verb and verb not in KNOWN_VERBS:
        resp = random.choice(UNKNOWN_VERB_RESPONSES).format(verb=verb)
        _h(resp)
        _h("")
