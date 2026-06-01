from dataclasses import dataclass
from pathlib import Path
from src.actions import validate_action, direction_delta

WALKABLE_TILES = {".", "A", "K", "D"}
REQUIRED_SINGLE_TILES = {"A", "K", "D"}
VALID_TILES = {"#", ".", "A", "K", "D"}


@dataclass(frozen=True)
class Position:
    row: int
    col: int


def validate_tiles(map_lines):
    for row_index, line in enumerate(map_lines):
        for col_index, tile_symbol in enumerate(line):
            if tile_symbol not in VALID_TILES:
                raise ValueError(f"Invalid tile '{tile_symbol}' at row {row_index}, col {col_index}")


def find_tile_positions(map_lines):
    tile_positions = {"A": [], "K": [], "D": []}
    for row_index, line in enumerate(map_lines):
        for col_index, tile_symbol in enumerate(line):
            if tile_symbol in tile_positions:
                tile_positions[tile_symbol].append(Position(row_index, col_index))
    return tile_positions


def is_adjacent(pos_a, pos_b):
    row_gap = abs(pos_a.row - pos_b.row)
    col_gap = abs(pos_a.col - pos_b.col)
    return row_gap + col_gap == 1


@dataclass
class GridWorld:
    grid_rows: list[list[str]]
    agent_start_position: Position
    key_position: Position
    door_position: Position
    map_height: int
    map_width: int
    agent_position: Position
    has_key: bool
    door_open: bool
    step_count: int
    last_action_result: str
    mission_complete: bool

    @classmethod
    def from_map_file(cls, map_file_path):
        file_path = Path(map_file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Map file not found: {map_file_path}")

        raw_lines = file_path.read_text(encoding="utf-8").splitlines()
        map_lines = [line for line in raw_lines if line.strip()]
        if not map_lines:
            raise ValueError("Map file is empty.")

        map_width = len(map_lines[0])
        if any(len(line) != map_width for line in map_lines):
            raise ValueError("All map rows need to have the same width.")

        validate_tiles(map_lines)
        tile_positions = find_tile_positions(map_lines)

        for tile_symbol in REQUIRED_SINGLE_TILES:
            if len(tile_positions[tile_symbol]) != 1:
                raise ValueError(f"Map must contain exactly one '{tile_symbol}' tile.")

        grid_rows = [list(line) for line in map_lines]

        return cls(
            grid_rows=grid_rows,
            agent_start_position=tile_positions["A"][0],
            key_position=tile_positions["K"][0],
            door_position=tile_positions["D"][0],
            map_height=len(map_lines),
            map_width=map_width,
            agent_position=tile_positions["A"][0],
            has_key=False,
            door_open=False,
            step_count=0,
            last_action_result="World loaded.",
            mission_complete=False,
        )

    def is_within_bounds(self, position):
        return 0 <= position.row < self.map_height and 0 <= position.col < self.map_width

    def tile_at(self, position):
        if not self.is_within_bounds(position):
            raise IndexError(f"Position out of bounds: row={position.row}, col={position.col}")
        return self.grid_rows[position.row][position.col]

    def is_walkable(self, position):
        tile = self.tile_at(position)
        if tile == "#":
            return False
        if tile == "D" and not self.door_open:
            return False
        return tile in WALKABLE_TILES

    def make_result(self, valid, action, direction, message):
        return {"VALID": valid, "ACTION": action, "DIRECTION": direction, "MESSAGE": message, "MISSION_COMPLETE": self.mission_complete, "STEP_COUNT": self.step_count}

    def apply_action(self, action):
        check = validate_action(action)
        action_name = check.get("action")
        direction = check.get("direction")
        if not check["valid"]:
            self.last_action_result = check["message"]
            return self.make_result(False, action_name, direction, self.last_action_result)

        self.step_count += 1

        if action_name == "look":
            self.last_action_result = "Looked around."
            return self.make_result(True, action_name, direction, self.last_action_result)

        if action_name == "move":
            d_row, d_col = direction_delta(direction)
            next_position = Position(self.agent_position.row + d_row, self.agent_position.col + d_col)

            if not self.is_within_bounds(next_position):
                self.last_action_result = "Blocked: map boundary."
                return self.make_result(False, action_name, direction, self.last_action_result)
            
            if not self.is_walkable(next_position):
                self.last_action_result = "Blocked: wall or locked door."
                return self.make_result(False, action_name, direction, self.last_action_result)
            
            self.agent_position = next_position
            self.last_action_result = f"Moved {direction}."
            return self.make_result(True, action_name, direction, self.last_action_result)

        if action_name == "pick_up":
            if self.has_key:
                self.last_action_result = "Key already collected."
                return self.make_result(False, action_name, direction, self.last_action_result)
            
            if self.agent_position != self.key_position:
                self.last_action_result = "No key on this tile."
                return self.make_result(False, action_name, direction, self.last_action_result)
            
            self.has_key = True
            self.last_action_result = "Picked up key."
            return self.make_result(True, action_name, direction, self.last_action_result)

        if action_name == "open_door":
            if self.door_open:
                self.last_action_result = "Door already open."
                return self.make_result(False, action_name, direction, self.last_action_result)
            
            if not self.has_key:
                self.last_action_result = "Need key to open door."
                return self.make_result(False, action_name, direction, self.last_action_result)
            
            if not is_adjacent(self.agent_position, self.door_position):
                self.last_action_result = "Must be adjacent to door."
                return self.make_result(False, action_name, direction, self.last_action_result)
            
            self.door_open = True
            self.mission_complete = True
            self.last_action_result = "Door opened. Mission complete."
            return self.make_result(True, action_name, direction, self.last_action_result)

        self.last_action_result = "Unknown action."
        return self.make_result(False, action_name, direction, self.last_action_result)


def script_test(): # for development and debugging
    world = GridWorld.from_map_file("maps/room_s.map")
    print("Start:", world.agent_position)
    print(world.apply_action({"action": "move", "direction": "right"}))
    print(world.apply_action({"action": "pick_up"}))
    print(world.apply_action({"action": "move", "direction": "down"}))
    print(world.apply_action({"action": "open_door"}))
    print("Has key:", world.has_key)
    print("Door open:", world.door_open)
    print("Mission complete:", world.mission_complete)


if __name__ == "__main__":
    script_test()
