from src.ascii_renderer import render_world
from src.world import GridWorld

MISSION_TEXT = "Walk to the key, collect it, walk adjacent to the door, and open the door."

def is_adjacent(pos_a, pos_b):
    return abs(pos_a.row - pos_b.row) + abs(pos_a.col - pos_b.col) == 1


def next_position(world, direction):
    row = world.agent_position.row
    col = world.agent_position.col
    if direction == "up":
        return type(world.agent_position)(row - 1, col)
    if direction == "down":
        return type(world.agent_position)(row + 1, col)
    if direction == "left":
        return type(world.agent_position)(row, col - 1)
    return type(world.agent_position)(row, col + 1)


def get_valid_moves(world):
    valid_moves = []
    for direction in ["up", "down", "left", "right"]:
        pos = next_position(world, direction)
        if world.is_within_bounds(pos) and world.is_walkable(pos):
            valid_moves.append(direction)
    return valid_moves

def build_observation(world):
    on_key_tile = world.agent_position == world.key_position and not world.has_key
    adjacent_to_door = is_adjacent(world.agent_position, world.door_position)
    last_action_blocked = "Blocked" in world.last_action_result

    return {
        "step_count": world.step_count,
        "mission": MISSION_TEXT,
        "agent": {"row": world.agent_position.row, "col": world.agent_position.col},
        "key": {"row": world.key_position.row, "col": world.key_position.col, "collected": world.has_key},
        "door": {"row": world.door_position.row, "col": world.door_position.col, "open": world.door_open},
        "on_key_tile": on_key_tile,
        "is_adjacent_to_door": adjacent_to_door,
        "has_key": world.has_key,
        "door_open": world.door_open,
        "valid_moves": get_valid_moves(world),
        "last_action_blocked": last_action_blocked,
        "last_action_result": world.last_action_result,
        "allowed_actions": [
            {"action": "move", "direction": "up"},
            {"action": "move", "direction": "down"},
            {"action": "move", "direction": "left"},
            {"action": "move", "direction": "right"},
            {"action": "pick_up"},
            {"action": "open_door"},
            {"action": "look"},
        ],
        "map_ascii": render_world(world).split("\n"),
    }

def script_test(): # for development and debugging
    world = GridWorld.from_map_file("maps/room_s.map")
    print(f"Initial observation:\n{build_observation(world)}\n")

    world.apply_action({"action": "move", "direction": "right"})
    world.apply_action({"action": "move", "direction": "right"})
    print(f"After two actions:\n{build_observation(world)}\n")

if __name__ == "__main__":
    script_test()
