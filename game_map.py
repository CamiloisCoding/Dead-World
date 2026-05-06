# ============================================================================
# game_map.py — Dead World 2D Spatial Map
# ============================================================================
# Auto-generates (x, y) grid coordinates for every room using BFS traversal.
# Import GAME_MAP from this module to get a dict keyed by (x,y) tuples.
# ============================================================================

from collections import deque

# ---------------------------------------------------------------------------
# Direction → (dx, dy) offsets
# Convention: North = -Y (up on screen), South = +Y, East = +X, West = -X
# ---------------------------------------------------------------------------
DIRECTION_DELTAS = {
    'norden':     ( 0, -1),
    'süden':      ( 0,  1),
    'osten':      ( 1,  0),
    'westen':     (-1,  0),
    'nordosten':  ( 1, -1),
    'nordwesten': (-1, -1),
    'südosten':   ( 1,  1),
    'südwesten':  (-1,  1),
    'hoch':       ( 0, -1),   # stairs up   = visual north
    'runter':     ( 0,  1),   # stairs down = visual south
}

# ---------------------------------------------------------------------------
# Biome / terrain classification per room key
# ---------------------------------------------------------------------------
BIOME_MAP = {
    # --- Bunker ---
    'start':        'bunker',
    'corridor':     'bunker',
    'laboratory':   'bunker',
    'storage':      'bunker',
    'tunnel':       'tunnel',
    # --- Versteck (Safehouse) ---
    'spawn':           'safehouse',
    'schlafzimmer':    'indoor',
    'flur':            'indoor',
    'badezimmer':      'indoor',
    'eingangsbereich': 'indoor',
    'wohnzimmer':      'indoor',
    'wohnbereich':     'indoor',
    'schlafzimmer2':   'indoor',
    'kueche':          'indoor',
    'vordertuer':      'indoor',
    'treppen':         'indoor',
    'keller':          'underground',
    'lagerraum':       'underground',
    # --- Stadt (Streets) ---
    'suedlich_haus':               'street',
    'westlich_haus_gabelung':      'street',
    'oestlich_weggabelung':        'street',
    'nord_westliche_weggabelung':  'street',
    'nord_östliche_weggabelung':   'street',
    'östliche_straße':             'street',
    'norden_straße':               'street',
    'park_straße':                 'street',
    'skyscraper_weggabelung':      'street',
    'weggabelung_skyscraper2':     'street',
    'noerdlich_haus':              'street',
    # --- Krankenhaus ---
    'krankenhaus_straße':  'street',
    'krankenhaus_eingang': 'hospital',
    # --- Bibliothek ---
    'bibliothek_straße':   'street',
    'bibliothek_eingang':  'library',
    'bibliothek_1.1':      'library',
    'bibliothek_1.2':      'library',
    'bibliothek_2':        'library',
    'bibliothek_3':        'library',
    'bibliothek_4':        'library',
    'bibliothek_5':        'library',
    'bibliothek_6':        'library',
    'bibliothek_7':        'library',
    'bibliothek_8':        'library',
    # --- Walmart ---
    'parkplatz':       'parking',
    'walmart_eingang': 'store',
    'walmart_1':       'store',
    'walmart_2':       'store',
    'walmart_3':       'store',
    'walmart_4':       'store',
    'walmart_5':       'store',
    'walmart_6':       'store',
    'walmart_7':       'store',
    'walmart_8':       'store',
    'walmart_9':       'store',
    'walmart_10':      'store',
    'walmart_11':      'store',
    'walmart_12.1':    'store',
    'walmart_12.2':    'store',
    'walmart_13':      'store',
    'walmart_14':      'store',
    # --- Haus 1 ---
    'haus1':           'house',
    # --- Haus 3 ---
    'haus_3_eingang':      'house',
    'haus_3_v':            'house',
    'haus_3_wohnbereich':  'house',
    'wohnzimmer_h3':       'house',
    'küche_h3':            'house',
    'bathroom_3':          'house',
    'bedroom_3':           'house',
    # === MAP-INTEGRATION (40+ new districts) ===
    'noerdlich_walmart_straße': 'street',
    'mickey_mouse_straße': 'street',
    'mickey_mouse_eingang': 'amusement',
    'mickey_mouse_spielraum': 'amusement',
    'mickey_mouse_storycorner': 'amusement',
    'strand_straße': 'beach',
    'strand': 'beach',
    'strand_brücke': 'beach',
    'bruce_wayne_straße': 'street',
    'bruce_wayne_eingang': 'mansion',
    'bruce_wayne_wohnzimmer': 'mansion',
    'bruce_wayne_küche': 'mansion',
    'bruce_wayne_library': 'mansion',
    'bruce_wayne_master': 'mansion',
    'batcave_garage': 'mansion',
    'batcave_computer': 'mansion',
    'batcave_suits': 'mansion',
    'batcave_training': 'mansion',
    'wald_nordwest': 'forest',
    'wald_norden': 'forest',
    'wald_fluss': 'forest',
    'berg': 'mountain',
    'berg_höhle': 'mountain',
    'berg_hütte': 'mountain',
    'amusement_eingang': 'amusement',
    'amusement_riesenrad': 'amusement',
    'amusement_achterbahn': 'amusement',
    'amusement_karussell': 'amusement',
    'joestar_eingang': 'mansion',
    'joestar_wohnzimmer': 'mansion',
    'joestar_küche': 'mansion',
    'joestar_jonathan': 'mansion',
    'joestar_joseph': 'mansion',
    'joestar_jotaro': 'mansion',
    'pollos_eingang': 'restaurant',
    'pollos_küche': 'restaurant',
    'casino_eingang': 'entertainment',
    'casino_floor': 'entertainment',
    'casino_vip': 'entertainment',
    'casino_vault': 'entertainment',
    'stark_lobby': 'tower',
    'stark_lab': 'tower',
    'stark_penthouse': 'tower',
    'stark_suits': 'tower',
    'stark_helipad': 'tower',
    'cinema_eingang': 'entertainment',
    'cinema_saal1': 'entertainment',
    'cinema_saal2': 'entertainment',
    'disco_eingang': 'entertainment',
    'disco_tanzfläche': 'entertainment',
    'disco_dj': 'entertainment',
    'disco_vip': 'entertainment',
    'disco_bar': 'entertainment',
    'timesquare': 'street',
    'wald_osten': 'forest',
    'wald_fluss_osten': 'forest',
    'oestlich_park_erweiterung': 'street',
    'oestlich_skyscraper2_erweiterung': 'street',
    'oestlich_skyscraper2_erweiterung_süd': 'street',
    'westlich_krankenhaus_erweiterung': 'street',
    'weiter_westlich_straße': 'street',
    'westlich_süd_straße': 'street',
    'maze_eingang': 'maze',
    'maze_zentrum': 'maze',
    'friedhof_eingang': 'graveyard',
    'friedhof_krypta': 'graveyard',
    'town_hall_eingang': 'civic',
    'town_hall_office': 'civic',
    'town_hall_conference': 'civic',
    'university_eingang': 'university',
    'university_library': 'university',
    'university_dorm': 'university',
    'waterpark_eingang': 'waterpark',
    'waterpark_pool': 'waterpark',
    'waterpark_slides': 'waterpark',
    'storage_eingang': 'storage',
    'lab_eingang': 'laboratory',
    'lab_chemie': 'laboratory',
    'lab_biologie': 'laboratory',
    'lab_datacenter': 'laboratory',
    'feuerwehr_eingang': 'fire_dept',
    'feuerwehr_garage': 'fire_dept',
    'feuerwehr_schlafraum': 'fire_dept',
    'feuerwehr_training': 'fire_dept',
    'sex_dungeon_eingang': 'underground',
    'sex_dungeon_lounge': 'underground',
    'sex_dungeon_hauptraum': 'underground',
    'military_eingang': 'military',
    'military_barracks': 'military',
    'military_messhall': 'military',
    'military_armory': 'military',
    'military_vehicles': 'military',
    'hacienda_eingang': 'mansion',
    'hacienda_wohnzimmer': 'mansion',
    'hacienda_küche': 'mansion',
    'hacienda_pablo': 'mansion',
    'hacienda_lab': 'underground',
    'hacienda_vault': 'underground',
    'hacienda_pool': 'mansion',
    'prison_eingang': 'prison',
    'prison_zellen': 'prison',
    'prison_yard': 'prison',
    'prison_cafeteria': 'prison',
    'stadium_eingang': 'arena',
    'stadium_feld': 'arena',
    'stadium_tribuene': 'arena',
    'stadium_food': 'arena',
    'capsule_eingang': 'tech',
    'capsule_lab': 'tech',
    'capsule_haus': 'tech',
    'capsule_gravity': 'tech',
    'bunker_eingang': 'bunker',
    'bunker_vaults': 'bunker',
    'bunker_supplies': 'bunker',
    'bunker_bunks': 'bunker',
    'doof_eingang': 'tower',
    'doof_workshop': 'tower',
    'doof_penthouse': 'tower',
    'doof_roof': 'tower',
    'studio_eingang': 'studio',
    'studio_news': 'studio',
    'studio_drama': 'studio',
    'studio_control': 'studio',
    'bau_eingang': 'construction',
    'bau_tower': 'construction',
    'bau_kran': 'construction',
    'bau_material': 'construction',
    'airport_terminal': 'airport',
    'airport_warten': 'airport',
    'airport_runway': 'airport',
    'airport_security': 'airport',
    'südlich_skyscraper2_straße': 'street',
    'weit_süd_landschaft': 'street',
    'feen_tal': 'landscape',
    'tal_lichtung': 'landscape',
    'wald_haus_eingang': 'forest',
    'wald_haus_drinnen': 'forest',
    'landschaft': 'landscape',
    # === FIXUP: pre-existing rooms missing biome ===
    'bedroom_2': 'unknown',
    'haus1_Flur': 'house',
    'haus1_Flur2': 'house',
    'haus1_Flur3': 'house',
    'haus1_badezimmer': 'house',
    'haus1_dachboden': 'house',
    'haus1_dachbodentür': 'house',
    'haus1_küche': 'house',
    'haus1_schlafzimmer': 'house',
    'haus1_schlafzimmer2': 'house',
    'haus1_vordertür': 'house',
    'haus1_wohnzimmer': 'house',
    'haus2': 'unknown',
    'home_depot_straße_nord': 'street',
    'home_depot_straße_süd': 'street',
    'home_depot_straße_west': 'street',
    'home_depot_weggabelung_nord_ost': 'street',
    'home_depot_weggabelung_nord_west': 'street',
    'hacienda_straße':    'street',
    'puente_juanchito':   'street',
    'wald_west_zugang':   'forest',
    'home_depot_weggabelung_osten': 'street',
    'home_depot_weggabelung_süd_ost': 'street',
    'home_depot_weggabelung_west_nord': 'street',
    'home_depot_weggabelung_west_süd': 'street',
    'krankenhaus_Labor': 'hospital',
    'krankenhaus_OP_raum': 'hospital',
    'krankenhaus_Rezeption': 'hospital',
    'krankenhaus_Treppe': 'hospital',
    'krankenhaus_Treppe_F2': 'hospital',
    'krankenhaus_aufnahmeraum': 'hospital',
    'krankenhaus_behandlungs_raum': 'hospital',
    'krankenhaus_flur': 'hospital',
    'krankenhaus_flur_mitte_f2': 'hospital',
    'krankenhaus_flur_nord_ost': 'hospital',
    'krankenhaus_flur_nord_westen_1': 'hospital',
    'krankenhaus_flur_nord_westen_2': 'hospital',
    'krankenhaus_flur_norden': 'hospital',
    'krankenhaus_flur_norden_f2': 'hospital',
    'krankenhaus_flur_osten': 'hospital',
    'krankenhaus_flur_osten_f2': 'hospital',
    'krankenhaus_flur_süd_westen': 'hospital',
    'krankenhaus_flur_süden_f2': 'hospital',
    'krankenhaus_flur_westen': 'hospital',
    'krankenhaus_flur_westen_f2': 'hospital',
    'krankenhaus_geheim_treppe': 'hospital',
    'krankenhaus_krankenzimmer': 'hospital',
    'krankenhaus_labor_rezeption': 'hospital',
    'krankenhaus_mitarbeiter_flur': 'hospital',
    'krankenhaus_mitarbeiter_raum': 'hospital',
    'krankenhaus_preperations_raum': 'hospital',
    'krankenhaus_schliefach_raum': 'hospital',
    'krankenhaus_schwesterstation': 'hospital',
    'krankenhaus_treppenhaus_flur': 'hospital',
    'krankenhaus_treppenhaus_flur_f2': 'hospital',
    'krankenhaus_wartebereich': 'hospital',
    'krankenhaus_waschraum': 'hospital',
    'krankenhaus_waschraum_flur': 'hospital',
    'krankenhaus_waschraum_flur_süden': 'hospital',
    'krankenhaus_zwischen_flur': 'hospital',
    'park': 'unknown',
    'straße_pizzeria': 'street',
    'süd_östliche_skyscraper_weggabelung': 'street',
    'südliche_pizzeria_straße': 'street',
    'westliche_haus_gabelung': 'unknown',
    'westliche_skyscraper2_weggabelung': 'street',
    'östliche_skyscraper2_straße': 'street',
}

# Placeholder rooms that are referenced in exits but not yet defined
UNIMPLEMENTED_ROOMS = {
    'haus2', 'park', 'haus1_vordertür', 'bedroom_2',
    'straße_pizzeria', 'home_depot_straße_ost',
}


# ---------------------------------------------------------------------------
# DISTRICT_GRID — single source of truth for the Idea-Map layout
# ---------------------------------------------------------------------------
# Maps (row, col) on the canonical 8x9 grid -> "anchor room" key in rooms{}.
# This anchor is the room you arrive at when entering the district from the
# street side (= the door room or the central street of that district).
#
# Special cells:
#   None  = empty / placeholder cell (no district there)
#   '__RIVER__' = river cell, blocks movement (Forest/River in Excalidraw)
#   '__FOREST__' = forest terrain, walkable but no specific room defined yet
#
# Convention from Idea-Map (Excalidraw): R0 = north edge, R7 = south edge
#                                        C0 = west edge,  C8 = east edge
DISTRICT_GRID = {
    # ── ROW 0 (north edge) ────────────────────────────────────────────
    (0, 0): 'mickey_mouse_eingang',     # Mickey Mouse Club House
    (0, 1): '__FOREST__',               # Forest
    (0, 2): '__RIVER__',                # Forest/River (big river)
    (0, 3): 'military_eingang',         # Military Base
    (0, 4): None,                       # empty cell
    (0, 5): 'strand',                   # Beach
    (0, 6): 'strand_brücke',            # Beach/Bridge (over the sea)
    (0, 7): 'amusement_eingang',        # Amusement Park
    (0, 8): 'bruce_wayne_eingang',      # Bruce Wayne Manor
    # ── ROW 1 ────────────────────────────────────────────────────────
    (1, 0): '__FOREST__',
    (1, 1): '__RIVER__',
    (1, 2): '__FOREST__',
    (1, 3): 'bibliothek_eingang',       # Library
    (1, 4): 'haus_3_eingang',           # House3
    (1, 5): 'walmart_eingang',          # Walmart
    (1, 6): 'pollos_eingang',           # Sanchéz / Los Pollos Hermanos
    (1, 7): None,                       # Bank — not yet implemented
    (1, 8): None,                       # empty
    # ── ROW 2 (Spawn row) ────────────────────────────────────────────
    (2, 0): 'wald_west_zugang',         # West-Wald, Zugang von der Brücke
    (2, 1): 'puente_juanchito',         # Puente Juanchito (the ONE bridge)
    (2, 2): 'hacienda_eingang',         # Hacienda Nápoles
    (2, 3): 'krankenhaus_eingang',      # Hospital
    (2, 4): 'vordertuer',               # SPAWN (Versteck-Vordertür)
    (2, 5): 'haus2',                    # House2 (placeholder)
    (2, 6): 'waterpark_eingang',        # Waterpark
    (2, 7): 'town_hall_eingang',        # Town Hall
    (2, 8): 'batcave_garage',           # Batcave entrance
    # ── ROW 3 ────────────────────────────────────────────────────────
    (3, 0): 'feen_tal',                 # Valley / Fairy Tale Valley
    (3, 1): '__RIVER__',
    (3, 2): 'lab_eingang',              # Filtration / Laboratory exterior
    (3, 3): 'home_depot_weggabelung_nord_ost',  # Home Depot
    (3, 4): 'haus1',                    # House1
    (3, 5): 'park',                     # Park (placeholder)
    (3, 6): None,                       # los pollos (in row 1) — leave empty
    (3, 7): 'cinema_eingang',           # Cinema
    (3, 8): 'joestar_eingang',          # Joestar Mansion
    # ── ROW 4 ────────────────────────────────────────────────────────
    (4, 0): '__FOREST__',
    (4, 1): '__RIVER__',
    (4, 2): '__RIVER__',
    (4, 3): 'lab_chemie',               # laboratory inner
    (4, 4): None,                       # Police — not yet implemented
    (4, 5): 'skyscraper_weggabelung',   # Skyscraper 1
    (4, 6): 'timesquare',               # Times Square
    (4, 7): 'university_eingang',       # University
    (4, 8): 'disco_eingang',            # Discotec
    # ── ROW 5 ────────────────────────────────────────────────────────
    (5, 0): 'tal_lichtung',             # Fairy valley clearing
    (5, 1): 'friedhof_eingang',         # Graveyard
    (5, 2): '__RIVER__',
    (5, 3): 'casino_eingang',           # Casino
    (5, 4): 'südliche_pizzeria_straße', # Pizzeria street
    (5, 5): None,
    (5, 6): 'westliche_skyscraper2_weggabelung',  # Skyscraper 2 (anchor existing room)
    (5, 7): None,
    (5, 8): 'doof_eingang',             # Doofenshmirtz Tower
    # ── ROW 6 ────────────────────────────────────────────────────────
    (6, 0): 'wald_haus_eingang',        # Forest/House
    (6, 1): 'maze_eingang',             # Maze
    (6, 2): '__RIVER__',
    (6, 3): 'landschaft',               # landscape
    (6, 4): 'feuerwehr_eingang',        # Fire Department
    (6, 5): 'stadium_eingang',          # Stadium
    (6, 6): 'airport_terminal',         # Airport
    (6, 7): 'bau_eingang',              # Construction
    (6, 8): None,
    # ── ROW 7 (south edge) ───────────────────────────────────────────
    (7, 0): 'sex_dungeon_eingang',      # Sex Dungeon
    (7, 1): '__RIVER__',
    (7, 2): 'berg',                     # Mountain
    (7, 3): 'prison_eingang',           # Prison
    (7, 4): 'storage_eingang',          # Storage
    (7, 5): 'stark_lobby',              # Stark Tower
    (7, 6): 'bunker_eingang',           # Bunker
    (7, 7): 'capsule_eingang',          # Capsule Corp
    (7, 8): 'studio_eingang',           # Studio
}

# Reverse lookup: room_key -> (row, col)
DISTRICT_OF = {v: rc for rc, v in DISTRICT_GRID.items()
               if v and v not in ('__RIVER__', '__FOREST__')}


def get_district_grid_position(room_key):
    """Return (row, col) on the Idea-Map grid for a district anchor room, or None."""
    return DISTRICT_OF.get(room_key)


def is_river_cell(rc):
    """True if (row, col) is a river cell (impassable)."""
    return DISTRICT_GRID.get(rc) == '__RIVER__'


def get_grid_neighbors(rc):
    """Return [(direction, neighbor_rc, neighbor_room_or_None)] for orthogonal neighbors
    not blocked by the river."""
    r, c = rc
    out = []
    for dr, dc, name in [(-1, 0, 'norden'), (1, 0, 'süden'),
                         (0, -1, 'westen'), (0, 1, 'osten')]:
        nrc = (r + dr, c + dc)
        if nrc not in DISTRICT_GRID:
            continue
        if is_river_cell(nrc):
            continue  # river blocks
        out.append((name, nrc, DISTRICT_GRID[nrc]))
    return out


# ---------------------------------------------------------------------------
# Auto-Layout: snap all rooms to coordinates derived from DISTRICT_GRID
# ---------------------------------------------------------------------------
# For each district anchor, fix its position to its (col, row) on the grid (scaled).
# All other rooms (street rooms, internal building rooms) are placed via BFS
# from their nearest anchor, so they cluster around the right district.

# How many GRAPH_LAYOUT units per grid cell. The renderer multiplies coords by
# UNIT = scale(50) * map_zoom, so spacing of 12 units ≈ 600px at zoom=1.
GRID_CELL_SPACING = 12

# Within a cell, sub-rooms get arranged in a small spiral around the anchor.
# 1 step = SUBROOM_STEP layout units (small enough to stay inside the cell).
SUBROOM_STEP = 1.5


def compute_auto_layout(rooms):
    """
    Returns: dict {room_key: (x, y)} layout positions for all rooms.

    Algorithm:
      1) Place every district-anchor room at its grid (col*S, row*S) coordinate.
      2) For every other room, BFS-walk along its exits until we find the
         nearest already-placed anchor; place this room at anchor + small spiral offset.
      3) Orphans go into a side strip below the grid.
    """
    from collections import deque
    
    layout = {}
    occupied = {}  # (x, y) rounded -> room_key (for spiral collision avoidance)
    
    # ---- Step 1: place anchors on their grid cells ----
    for (r, c), anchor_key in DISTRICT_GRID.items():
        if not anchor_key or anchor_key in ('__RIVER__', '__FOREST__'):
            continue
        if anchor_key not in rooms:
            continue
        x = c * GRID_CELL_SPACING
        y = r * GRID_CELL_SPACING
        layout[anchor_key] = (x, y)
        occupied[(round(x, 2), round(y, 2))] = anchor_key
    
    # ---- Step 2: build adjacency for BFS-from-anchors ----
    # bidirectional graph for traversal (since some exits are one-way in the data)
    nbrs = {rk: set() for rk in rooms}
    for rk, rd in rooms.items():
        for d, t in rd.get('exits', {}).items():
            if t in rooms:
                nbrs[rk].add(t)
                nbrs.setdefault(t, set()).add(rk)
    
    # Multi-source BFS from all placed anchors. Each non-anchor room learns
    # which anchor is its "owner" and at what BFS-depth.
    owner = {a: a for a in layout}    # room_key -> anchor_key
    depth = {a: 0 for a in layout}
    queue = deque(layout.keys())
    while queue:
        cur = queue.popleft()
        for nb in nbrs.get(cur, ()):
            if nb in owner:
                continue
            owner[nb] = owner[cur]
            depth[nb] = depth[cur] + 1
            queue.append(nb)
    
    # ---- Step 3: place each non-anchor room in a spiral around its owner ----
    # We'll generate spiral offsets in order so each owner gets its own counter.
    def _spiral_offsets(n):
        """Yield up to n (dx, dy) offsets in a square-ring spiral order."""
        yield (0, 0)
        if n <= 1: return
        ring = 1
        produced = 1
        while produced < n:
            for dx in range(-ring, ring + 1):
                for dy in range(-ring, ring + 1):
                    if abs(dx) != ring and abs(dy) != ring:
                        continue
                    yield (dx * SUBROOM_STEP, dy * SUBROOM_STEP)
                    produced += 1
                    if produced >= n: return
            ring += 1
    
    # Group non-anchor rooms by their owner anchor
    by_owner = {}
    for rk, ow in owner.items():
        if rk == ow:  # anchor itself
            continue
        by_owner.setdefault(ow, []).append(rk)
    
    for anchor_key, sub_rooms in by_owner.items():
        ax, ay = layout[anchor_key]
        # Sort sub_rooms by BFS depth so closest go to inner ring
        sub_rooms.sort(key=lambda k: depth[k])
        # Build full spiral once, drop (0,0) (anchor's slot)
        offsets = list(_spiral_offsets(len(sub_rooms) + 256))[1:]
        offset_idx = 0
        for rk in sub_rooms:
            placed = False
            while offset_idx < len(offsets):
                ox, oy = offsets[offset_idx]
                offset_idx += 1
                px = ax + ox
                py = ay + oy
                key = (round(px, 2), round(py, 2))
                if key not in occupied:
                    layout[rk] = (px, py)
                    occupied[key] = rk
                    placed = True
                    break
            if not placed:
                # Last-resort: linear strip below the anchor
                px = ax
                py = ay + SUBROOM_STEP * (len(sub_rooms) + 1)
                layout[rk] = (px, py)
    
    # ---- Step 4: orphans (rooms not connected to any anchor) ----
    # Place them in a strip below the grid.
    grid_max_row = max(r for (r, _) in DISTRICT_GRID)
    orphan_y = (grid_max_row + 2) * GRID_CELL_SPACING
    orphan_x = 0.0
    for rk in rooms:
        if rk not in layout:
            layout[rk] = (orphan_x, orphan_y)
            orphan_x += SUBROOM_STEP
            if orphan_x > 9 * GRID_CELL_SPACING:
                orphan_x = 0.0
                orphan_y += SUBROOM_STEP * 2
    
    return layout


# ---------------------------------------------------------------------------
# Bidirectional adjacency builder
# ---------------------------------------------------------------------------

_OPPOSITE = {
    'norden': 'süden', 'süden': 'norden',
    'osten': 'westen', 'westen': 'osten',
    'nordosten': 'südwesten', 'südwesten': 'nordosten',
    'nordwesten': 'südosten', 'südosten': 'nordwesten',
    'hoch': 'runter', 'runter': 'hoch',
}

def _build_adjacency(rooms):
    """
    Build a bidirectional adjacency dict from the rooms graph.
    adj[room_a] = set of (direction_from_a, room_b)

    Rooms with empty exits (e.g. 'start', 'spawn') gain reverse edges
    from their neighbors, so they are still reachable by BFS.
    """
    adj = {rk: set() for rk in rooms}

    for rk, room in rooms.items():
        for direction, target in room.get('exits', {}).items():
            adj[rk].add((direction, target))
            # Reverse edge for rooms that exist
            rev_dir = _OPPOSITE.get(direction)
            if rev_dir and target in rooms:
                adj.setdefault(target, set()).add((rev_dir, rk))

    return adj


# ---------------------------------------------------------------------------
# BFS Coordinate Solver
# ---------------------------------------------------------------------------

def build_game_map(rooms, seed_room='vordertuer', seed_coord=(0, 0),
                   bunker_seed_room='corridor', bunker_seed_coord=(0, 10)):
    """
    Walk the rooms graph via BFS on a bidirectional adjacency graph,
    assigning (x, y) coordinates based on directional exits.

    Returns: (game_map, coord_of)
      - game_map: { (x,y): { room data dict } }
      - coord_of: { room_key: (x,y) }

    Three BFS passes:
      1. Main world seeded at vordertuer (0, 0)
      2. Bunker seeded at corridor (0, 10) — disconnected underground
      3. Orphan sweep for anything still unmapped
    """
    adj = _build_adjacency(rooms)
    coord_of = {}     # room_key → (x, y)
    occupied = {}     # (x, y) → room_key

    def _nearest_free(target_x, target_y):
        """Spiral outward from (target_x, target_y) to find a free cell."""
        if (target_x, target_y) not in occupied:
            return (target_x, target_y)
        for radius in range(1, 50):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) == radius or abs(dy) == radius:
                        candidate = (target_x + dx, target_y + dy)
                        if candidate not in occupied:
                            return candidate
        return (target_x + 50, target_y)  # fallback

    def _bfs(start_key, start_xy):
        if start_key not in rooms:
            return
        if start_key in coord_of:
            return  # already placed by a previous pass
        sx, sy = start_xy
        actual = _nearest_free(sx, sy)
        coord_of[start_key] = actual
        occupied[actual] = start_key

        queue = deque([start_key])
        visited = {start_key}

        while queue:
            current = queue.popleft()
            cx, cy = coord_of[current]

            for direction, target_key in adj.get(current, set()):
                if target_key in visited:
                    continue
                if target_key not in rooms and target_key not in UNIMPLEMENTED_ROOMS:
                    continue

                delta = DIRECTION_DELTAS.get(direction, (0, 0))
                tx, ty = cx + delta[0], cy + delta[1]
                actual = _nearest_free(tx, ty)

                visited.add(target_key)
                coord_of[target_key] = actual
                occupied[actual] = target_key

                if target_key in rooms:
                    queue.append(target_key)

    # --- Pass 1: Main world (everything reachable from vordertuer) ---
    _bfs(seed_room, seed_coord)

    # --- Pass 2: Bunker (disconnected underground) ---
    _bfs(bunker_seed_room, bunker_seed_coord)

    # --- Pass 3: catch any orphan rooms not reached by either BFS ---
    orphan_y = max(y for (_, y) in occupied) + 2 if occupied else 20
    orphan_x = 0
    for rk in rooms:
        if rk not in coord_of:
            actual = _nearest_free(orphan_x, orphan_y)
            coord_of[rk] = actual
            occupied[actual] = rk
            orphan_x += 2

    # -----------------------------------------------------------------
    # Build the final GAME_MAP dict keyed by (x, y)
    # -----------------------------------------------------------------
    game_map = {}
    for room_key, (gx, gy) in coord_of.items():
        if room_key in rooms:
            room_data = rooms[room_key]
            biome = BIOME_MAP.get(room_key, 'unknown')
            # Compute adjacency list with coordinates
            connections = {}
            for direction, target_key in room_data.get('exits', {}).items():
                if target_key in coord_of:
                    connections[direction] = {
                        'target': target_key,
                        'coord': coord_of[target_key],
                    }
                else:
                    connections[direction] = {
                        'target': target_key,
                        'coord': None,  # unimplemented target
                    }

            game_map[(gx, gy)] = {
                'key':          room_key,
                'name':         room_data.get('name', room_key),
                'description':  room_data.get('description', ''),
                'biome':        biome,
                'items':        room_data.get('items', []),
                'exits':        room_data.get('exits', {}),
                'connections':  connections,
                'enemy':        room_data.get('enemy'),
                'is_safehouse': room_data.get('is_safehouse', False),
                'in_development': room_data.get('in_development', False),
                'zombie_spawn': room_data.get('zombie_spawn', False),
                'spawn_chance': room_data.get('spawn_chance', False),
                'status':       'active',
            }
        elif room_key in UNIMPLEMENTED_ROOMS:
            game_map[(gx, gy)] = {
                'key':          room_key,
                'name':         room_key.replace('_', ' ').title(),
                'description':  '',
                'biome':        'unknown',
                'items':        [],
                'exits':        {},
                'connections':  {},
                'enemy':        None,
                'is_safehouse': False,
                'in_development': True,
                'zombie_spawn': False,
                'spawn_chance': False,
                'status':       'unimplemented',
            }

    return game_map, coord_of


# ---------------------------------------------------------------------------
# Reverse lookup helper:  room_key → (x, y)
# ---------------------------------------------------------------------------
_coord_lookup = {}  # populated after build

def get_room_coord(room_key):
    """Return (x, y) for a room key, or None if not mapped."""
    return _coord_lookup.get(room_key)


# ---------------------------------------------------------------------------
# Build the map at import time using the rooms dict from the main game module
# ---------------------------------------------------------------------------
# We import rooms lazily to avoid circular imports.
# If this module is imported before the main game, GAME_MAP will be empty
# and must be rebuilt with rebuild_game_map().

GAME_MAP = {}

def rebuild_game_map(rooms_dict):
    """
    (Re)build GAME_MAP from a rooms dictionary.
    Call this after the rooms dict is available.
    Returns the GAME_MAP for convenience.
    """
    global GAME_MAP, _coord_lookup
    GAME_MAP, _coord_lookup = build_game_map(rooms_dict)
    return GAME_MAP


# ---------------------------------------------------------------------------
# Biome color palette for Pygame rendering
# ---------------------------------------------------------------------------
BIOME_COLORS = {
    'bunker':       (80,  80,  90),    # dark steel gray
    'tunnel':       (60,  55,  50),    # earthy brown
    'safehouse':    (40, 120,  60),    # safe green
    'indoor':       (100, 90,  80),    # warm beige
    'underground':  (50,  45,  55),    # deep purple-gray
    'street':       (70,  75,  85),    # asphalt blue-gray
    'hospital':     (180, 50,  50),    # medical red
    'library':      (110, 85,  60),    # old book brown
    'parking':      (90,  90,  90),    # concrete gray
    'store':        (50,  90, 150),    # walmart blue
    'house':        (130, 100, 70),    # wooden brown
    'unknown':      (55,  55,  55),    # dim gray placeholder
    'beach': (230, 200, 130),
    'forest': (30, 90, 40),
    'mountain': (110, 100, 100),
    'mansion': (100, 70, 50),
    'tower': (90, 110, 150),
    'restaurant': (220, 130, 50),
    'entertainment': (150, 70, 180),
    'university': (80, 90, 160),
    'military': (60, 90, 50),
    'prison': (90, 90, 90),
    'airport': (60, 60, 80),
    'waterpark': (90, 170, 220),
    'amusement': (220, 100, 160),
    'studio': (180, 60, 60),
    'graveyard': (50, 55, 60),
    'maze': (50, 130, 60),
    'landscape': (130, 180, 110),
    'arena': (60, 130, 60),
    'tech': (180, 100, 200),
    'civic': (90, 100, 130),
    'fire_dept': (180, 50, 50),
    'construction': (180, 130, 50),
    'storage': (110, 110, 100),
    'laboratory': (100, 150, 180),
}

# Icon glyphs (Unicode) for map node rendering
BIOME_ICONS = {
    'bunker':       '⚙',
    'tunnel':       '🕳',
    'safehouse':    '🏠',
    'indoor':       '🚪',
    'underground':  '⬇',
    'street':       '🛣',
    'hospital':     '🏥',
    'library':      '📚',
    'parking':      '🅿',
    'store':        '🛒',
    'house':        '🏡',
    'unknown':      '❓',
    'beach': '🏖',
    'forest': '🌲',
    'mountain': '⛰',
    'mansion': '🏰',
    'tower': '🏢',
    'restaurant': '🍔',
    'entertainment': '🎰',
    'university': '🎓',
    'military': '🎖',
    'prison': '🚔',
    'airport': '✈',
    'waterpark': '🏊',
    'amusement': '🎡',
    'studio': '🎬',
    'graveyard': '🪦',
    'maze': '🌳',
    'landscape': '🌅',
    'arena': '🏟',
    'tech': '🧪',
    'civic': '🏛',
    'fire_dept': '🚒',
    'construction': '🏗',
    'storage': '📦',
    'laboratory': '🧬',
}


# ---------------------------------------------------------------------------
# Standalone: print info when run directly
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("\n=== game_map.py standalone mode ===")
    print("To generate the map, call from your game:")
    print("  from game_map import rebuild_game_map, GAME_MAP")
    print("  rebuild_game_map(rooms)")
    print(f"  # GAME_MAP will contain {{(x,y): room_data}} entries")
    print(f"\nDefined {len(BIOME_MAP)} biome classifications")
    print(f"Defined {len(UNIMPLEMENTED_ROOMS)} placeholder rooms")
    print(f"Defined {len(BIOME_COLORS)} biome colors for rendering")
    print(f"Defined {len(DIRECTION_DELTAS)} direction deltas")
