# ============================================================
# map_editor.py — Node Management Utilities for Dead World Map
# ============================================================
# Provides rename, remove, and auto-create operations for map
# nodes.  All changes propagate to both the in-memory `rooms`
# dictionary AND the on-disk `custom_map_layout.json`.
#
# Usage from your Pygame loop:
#
#   from map_editor import MapEditor
#   editor = MapEditor(rooms, MAP_LAYOUT_FILE)
#
#   editor.rename_node('old_room', 'new_room')
#   editor.remove_node('some_room')
#   editor.add_exit('room_a', 'norden', 'room_b')   # auto-creates room_b
#   editor.save()                                     # explicit save
# ============================================================

import json
import os

# Optional: if game_map is available, patch BIOME_MAP too
try:
    from game_map import BIOME_MAP, UNIMPLEMENTED_ROOMS
except ImportError:
    BIOME_MAP = None
    UNIMPLEMENTED_ROOMS = None


class MapEditor:
    """
    Editor for the Dead World map graph.

    Operates on:
      • rooms_dict  – the live `rooms` dict from the main game module
      • layout_path – path to `custom_map_layout.json`
    """

    def __init__(self, rooms_dict: dict, layout_path: str):
        self.rooms = rooms_dict
        self.layout_path = layout_path
        self.layout = self._load_layout()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_layout(self) -> dict:
        """Load the JSON layout file, or create a minimal one."""
        if os.path.exists(self.layout_path):
            with open(self.layout_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"nodes": {}, "custom_blocks": []}

    def save(self):
        """Persist the current layout to disk."""
        with open(self.layout_path, 'w', encoding='utf-8') as f:
            json.dump(self.layout, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # 1.  Rename Node
    # ------------------------------------------------------------------

    def rename_node(self, old_name: str, new_name: str) -> bool:
        """
        Rename a room node everywhere:
          • rooms dict key
          • all exit references across every room
          • JSON layout nodes
          • BIOME_MAP (if available)

        Returns True on success, False if old_name doesn't exist
        or new_name already exists.
        """
        if old_name not in self.rooms:
            print(f"[MapEditor] Fehler: Raum '{old_name}' existiert nicht.")
            return False
        if new_name in self.rooms:
            print(f"[MapEditor] Fehler: Raum '{new_name}' existiert bereits.")
            return False

        # --- rooms dict: move the entry ---
        self.rooms[new_name] = self.rooms.pop(old_name)

        # --- exits: update every reference ---
        for room_data in self.rooms.values():
            exits = room_data.get('exits', {})
            for direction, target in list(exits.items()):
                if target == old_name:
                    exits[direction] = new_name

        # --- JSON layout nodes ---
        nodes = self.layout.get('nodes', {})
        if old_name in nodes:
            nodes[new_name] = nodes.pop(old_name)

        # --- BIOME_MAP ---
        if BIOME_MAP is not None and old_name in BIOME_MAP:
            BIOME_MAP[new_name] = BIOME_MAP.pop(old_name)

        # --- UNIMPLEMENTED_ROOMS ---
        if UNIMPLEMENTED_ROOMS is not None and old_name in UNIMPLEMENTED_ROOMS:
            UNIMPLEMENTED_ROOMS.discard(old_name)
            UNIMPLEMENTED_ROOMS.add(new_name)

        self.save()
        print(f"[MapEditor] Raum '{old_name}' → '{new_name}' umbenannt.")
        return True

    # ------------------------------------------------------------------
    # 2.  Remove Node
    # ------------------------------------------------------------------

    def remove_node(self, name: str) -> bool:
        """
        Remove a room node and scrub all references:
          • delete from rooms dict
          • remove any exit in other rooms that points to this room
          • delete from JSON layout nodes
          • remove from BIOME_MAP (if available)

        Returns True on success, False if the room doesn't exist.
        """
        if name not in self.rooms:
            print(f"[MapEditor] Fehler: Raum '{name}' existiert nicht.")
            return False

        # --- delete the room itself ---
        del self.rooms[name]

        # --- scrub exits everywhere ---
        for room_data in self.rooms.values():
            exits = room_data.get('exits', {})
            dirs_to_remove = [d for d, t in exits.items() if t == name]
            for d in dirs_to_remove:
                del exits[d]

        # --- JSON layout ---
        nodes = self.layout.get('nodes', {})
        nodes.pop(name, None)

        # --- BIOME_MAP ---
        if BIOME_MAP is not None:
            BIOME_MAP.pop(name, None)

        # --- UNIMPLEMENTED_ROOMS ---
        if UNIMPLEMENTED_ROOMS is not None:
            UNIMPLEMENTED_ROOMS.discard(name)

        self.save()
        print(f"[MapEditor] Raum '{name}' gelöscht (alle Referenzen entfernt).")
        return True

    # ------------------------------------------------------------------
    # 3.  Auto-Create Node  (ensure it exists)
    # ------------------------------------------------------------------

    def ensure_node(self, name: str, source_room: str | None = None) -> bool:
        """
        Make sure a room exists.  If it already does, return False (no-op).
        Otherwise create a minimal room entry with default coordinates.

        source_room: if given, the new node's coords are offset +2 in x
                     from the source room's position (so it appears nearby
                     on the map).

        Returns True if a new room was created.
        """
        if name in self.rooms:
            return False  # already exists, nothing to do

        # --- Create minimal room entry ---
        self.rooms[name] = {
            'name': name.replace('_', ' ').title(),
            'description': '',
            'exits': {},
            'items': [],
            'in_development': True,
        }

        # --- Determine coordinates ---
        nodes = self.layout.setdefault('nodes', {})
        if source_room and source_room in nodes:
            sx, sy = nodes[source_room]
            coords = [sx + 2.0, sy]
        else:
            coords = [0.0, 0.0]
        nodes[name] = coords

        self.save()
        print(f"[MapEditor] Neuer Raum '{name}' erstellt bei {coords}.")
        return True

    # ------------------------------------------------------------------
    # 4.  Add Exit  (with auto-creation of target)
    # ------------------------------------------------------------------

    def add_exit(self, from_room: str, direction: str, to_room: str) -> bool:
        """
        Add an exit from *from_room* in *direction* to *to_room*.
        If *to_room* doesn't exist yet, it is automatically created
        (auto-generation logic).

        Returns True on success.
        """
        if from_room not in self.rooms:
            print(f"[MapEditor] Fehler: Quellraum '{from_room}' existiert nicht.")
            return False

        # Auto-create target if missing
        created = self.ensure_node(to_room, source_room=from_room)

        # Wire the exit
        self.rooms[from_room]['exits'][direction] = to_room

        self.save()
        verb = "erstellt und " if created else ""
        print(f"[MapEditor] Ausgang {from_room} → [{direction}] → {to_room} {verb}verbunden.")
        return True

    # ------------------------------------------------------------------
    # 5.  Remove Exit
    # ------------------------------------------------------------------

    def remove_exit(self, from_room: str, direction: str) -> bool:
        """Remove a single exit from a room."""
        if from_room not in self.rooms:
            print(f"[MapEditor] Fehler: Raum '{from_room}' existiert nicht.")
            return False
        exits = self.rooms[from_room].get('exits', {})
        if direction not in exits:
            print(f"[MapEditor] Kein Ausgang '{direction}' in '{from_room}'.")
            return False
        del exits[direction]
        self.save()
        print(f"[MapEditor] Ausgang '{direction}' aus '{from_room}' entfernt.")
        return True

    # ------------------------------------------------------------------
    # 6.  Insert Node Between
    # ------------------------------------------------------------------

    def insert_node_between(self, from_room: str, to_room: str, new_node: str) -> bool:
        """
        Inserts new_node between from_room and to_room.
        Finds the direction from from_room -> to_room. Replaces it with from_room -> new_node.
        Then creates an exit from new_node -> to_room using the same direction.
        
        If there was a reciprocal exit to_room -> from_room, it also replaces that
        with to_room -> new_node and new_node -> from_room.
        """
        if from_room not in self.rooms or to_room not in self.rooms:
            print(f"[MapEditor] insert_node_between fehler: {from_room} oder {to_room} fehlt.")
            return False

        self.ensure_node(new_node)

        # 1. Forward direction (from -> to)
        forward_dir = None
        for d, t in list(self.rooms[from_room].get('exits', {}).items()):
            if t == to_room:
                forward_dir = d
                # A -> B
                self.rooms[from_room]['exits'][d] = new_node
                # B -> C
                self.rooms[new_node]['exits'][d] = to_room
                break

        if not forward_dir:
            print(f"[MapEditor] Fehler: Kein Ausgang von {from_room} nach {to_room} gefunden.")
            return False

        # 2. Backward direction (to -> from)
        backward_dir = None
        for d, t in list(self.rooms[to_room].get('exits', {}).items()):
            if t == from_room:
                backward_dir = d
                # C -> B
                self.rooms[to_room]['exits'][d] = new_node
                # B -> A
                self.rooms[new_node]['exits'][d] = from_room
                break

        # Put new node physically between them if possible
        nodes = self.layout.setdefault('nodes', {})
        if from_room in nodes and to_room in nodes:
            fx, fy = nodes[from_room]
            tx, ty = nodes[to_room]
            nodes[new_node] = [(fx + tx) / 2.0, (fy + ty) / 2.0]

        self.save()
        print(f"[MapEditor] {new_node} zwischen {from_room} und {to_room} eingefügt.")
        return True

    # ------------------------------------------------------------------
    # 7.  Utility:  list all rooms / list exits
    # ------------------------------------------------------------------

    def list_rooms(self) -> list[str]:
        """Return a sorted list of all room keys."""
        return sorted(self.rooms.keys())

    def list_exits(self, room: str) -> dict:
        """Return the exits dict for a room, or empty dict."""
        return dict(self.rooms.get(room, {}).get('exits', {}))

    def get_node_coords(self, name: str):
        """Return [x, y] for a node, or None."""
        return self.layout.get('nodes', {}).get(name)

    def set_node_coords(self, name: str, x: float, y: float):
        """Update coordinates for a node and save."""
        nodes = self.layout.setdefault('nodes', {})
        nodes[name] = [x, y]
        self.save()


# ======================================================================
# Module-level convenience functions
# ======================================================================
# These let you call map_editor.rename_node(...) etc. without managing
# the class instance yourself.  Call init_editor() once after your
# rooms dict is ready.
# ======================================================================

_editor: MapEditor | None = None


def init_editor(rooms_dict: dict, layout_path: str) -> MapEditor:
    """Initialise the module-level editor singleton."""
    global _editor
    _editor = MapEditor(rooms_dict, layout_path)
    return _editor


def get_editor() -> MapEditor:
    """Return the current editor (raises if not initialised)."""
    if _editor is None:
        raise RuntimeError(
            "MapEditor not initialised — call map_editor.init_editor() first."
        )
    return _editor


def rename_node(old_name: str, new_name: str) -> bool:
    return get_editor().rename_node(old_name, new_name)


def remove_node(name: str) -> bool:
    return get_editor().remove_node(name)


def ensure_node(name: str, source_room: str | None = None) -> bool:
    return get_editor().ensure_node(name, source_room)


def add_exit(from_room: str, direction: str, to_room: str) -> bool:
    return get_editor().add_exit(from_room, direction, to_room)


def remove_exit(from_room: str, direction: str) -> bool:
    return get_editor().remove_exit(from_room, direction)


def insert_node_between(from_room: str, to_room: str, new_node: str) -> bool:
    return get_editor().insert_node_between(from_room, to_room, new_node)


def save():
    get_editor().save()
