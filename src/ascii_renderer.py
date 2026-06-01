from src.world import GridWorld

def render_world(world):
    draw_grid = [row[:] for row in world.grid_rows]

    start = world.agent_start_position
    draw_grid[start.row][start.col] = "."

    if world.has_key:
        key = world.key_position
        draw_grid[key.row][key.col] = "."

    if world.door_open:
        door = world.door_position
        draw_grid[door.row][door.col] = "O"

    agent = world.agent_position
    draw_grid[agent.row][agent.col] = "A"

    lines = []
    for row in draw_grid:
        lines.append("".join(row))
    return "\n".join(lines)


def script_test(): # for development and debugging
    world = GridWorld.from_map_file("maps/room_s.map")
    print("Initial")
    print(render_world(world))
    print()

    world.apply_action({"action": "move", "direction": "down"})
    world.apply_action({"action": "move", "direction": "right"})
    print("After two moves")
    print(render_world(world))


if __name__ == "__main__":
    script_test()
