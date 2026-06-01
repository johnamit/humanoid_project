from src.world import GridWorld
from src.ascii_renderer import render_world
from src.observations import build_observation
from src.llm_client import choose_action
from src.pygame_renderer import PygameRenderer


def get_scripted_actions():
    return [
        {"action": "move", "direction": "right"},
        {"action": "move", "direction": "right"},
        {"action": "move", "direction": "right"},
        {"action": "move", "direction": "down"},
        {"action": "move", "direction": "down"},
        {"action": "move", "direction": "down"},
        {"action": "move", "direction": "down"},
        {"action": "move", "direction": "right"},
        {"action": "move", "direction": "right"},
        {"action": "move", "direction": "up"},
        {"action": "move", "direction": "up"},
        {"action": "move", "direction": "up"},
        {"action": "pick_up"},
        {"action": "move", "direction": "down"},
        {"action": "move", "direction": "down"},
        {"action": "move", "direction": "down"},
        {"action": "move", "direction": "left"},
        {"action": "open_door"},
    ]


def run_scripted_approach(map_path, render_mode="ascii", max_steps=60):
    world = GridWorld.from_map_file(map_path)
    actions = get_scripted_actions()
    renderer = None

    print(f"Map: {map_path}")
    print(f"Max steps: {max_steps}\n")

    if render_mode == "pygame":
        renderer = PygameRenderer(world)
        renderer.render(world)
    elif render_mode == "ascii":
        print(f"{render_world(world)}\n")

    for action in actions:
        if world.step_count >= max_steps or world.mission_complete:
            break

        if renderer and not renderer.running:
            print("Stopped: window closed.")
            break

        result = world.apply_action(action)
        print(f"Step {result['STEP_COUNT']}: {action} -> {result['MESSAGE']}")

        if render_mode == "pygame":
            renderer.render(world)
        elif render_mode == "ascii":
            print(f"{render_world(world)}\n")

    if world.mission_complete:
        print("Mission complete.")
    elif world.step_count >= max_steps:
        print("Stopped: reached max steps.")
    else:
        print("Stopped: action list ended before mission completion.")

    print("Final State:")
    print(f"Agent: {world.agent_position}")
    print(f"Has key: {world.has_key}")
    print(f"Door open: {world.door_open}")
    print(f"Mission complete: {world.mission_complete}")

    if renderer:
        renderer.close()

    return world



def override_if_stuck(action, observation, fallback_streak):
    if fallback_streak < 3:
        return action, fallback_streak
    if observation["on_key_tile"] and not observation["has_key"]:
        return {"action": "pick_up"}, 0
    if observation["is_adjacent_to_door"] and observation["has_key"] and not observation["door_open"]:
        return {"action": "open_door"}, 0
    return action, fallback_streak


def action_signature(action):
    if action.get("action") != "move":
        return action.get("action", "")
    return f"move:{action.get('direction', '')}"


def override_if_blocked_loop(action, observation, blocked_repeat_count):
    if blocked_repeat_count < 2:
        return action
    valid_moves = observation.get("valid_moves", [])
    if action.get("action") == "move":
        for direction in valid_moves:
            if direction != action.get("direction"):
                return {"action": "move", "direction": direction}
    if valid_moves:
        return {"action": "move", "direction": valid_moves[0]}
    return {"action": "look"}


def run_llm_approach(map_path, render_mode="ascii", max_steps=60):
    world = GridWorld.from_map_file(map_path)
    renderer = None

    if render_mode == "pygame":
        renderer = PygameRenderer(world)
        renderer.render(world)
    elif render_mode == "ascii":
        print(f"{render_world(world)}\n")

    fallback_streak = 0
    blocked_repeat_count = 0
    previous_blocked_signature = ""

    while world.step_count < max_steps and not world.mission_complete:
        if renderer and not renderer.running:
            print("Stopped: window closed.")
            break

        observation = build_observation(world)
        llm_result = choose_action(observation)
        action = llm_result["action"]
        fallback_streak = fallback_streak + 1 if llm_result["used_fallback"] else 0
        action, fallback_streak = override_if_stuck(action, observation, fallback_streak)
        action = override_if_blocked_loop(action, observation, blocked_repeat_count)
        result = world.apply_action(action)

        is_blocked = "Blocked" in result["MESSAGE"]
        current_signature = action_signature(action)
        if is_blocked and current_signature == previous_blocked_signature:
            blocked_repeat_count += 1
        elif is_blocked:
            blocked_repeat_count = 1
        else:
            blocked_repeat_count = 0
        previous_blocked_signature = current_signature if is_blocked else ""

        line = f"Step {result['STEP_COUNT']}: {action} -> {result['MESSAGE']} | fallback={llm_result['used_fallback']}"
        
        if llm_result["used_fallback"] and llm_result["error"]:
            line += f" | error={llm_result['error']}"
        print(line)
        
        if llm_result["used_fallback"] and llm_result["raw_response"]:
            print(f"Raw: {llm_result['raw_response'][:160]}")

        if render_mode == "pygame":
            renderer.render(world)
        elif render_mode == "ascii":
            print(f"{render_world(world)}\n")

    print("Mission complete." if world.mission_complete else "Stopped: reached max steps.")

    print("Final State:")
    print(f"Agent: {world.agent_position}")
    print(f"Has key: {world.has_key}")
    print(f"Door open: {world.door_open}")
    print(f"Mission complete: {world.mission_complete}")

    if renderer:
        renderer.close()

    return world


def script_test(): # for development and debugging
    run_llm_approach("maps/room_s.map", "ascii", 60)
    # run_scripted_approach("maps/room_s.map", "ascii", 60)


if __name__ == "__main__":
    script_test()
