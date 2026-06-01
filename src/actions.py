VALID_ACTIONS = {"move", "pick_up", "open_door", "look"}
VALID_DIRECTIONS = {"up", "down", "left", "right"}

def action_result(valid, message, action_name=None, direction=None):
    return {"valid": valid, "message": message, "action": action_name, "direction": direction}

def validate_action(action):
    if not isinstance(action, dict):
        return action_result(False, "Action must be a JSON object")
    
    action_name = action.get("action")
    if action_name not in VALID_ACTIONS:
        return action_result(False, "Invalid action. Use move, pick_up, open_door, or look")
    
    if action_name == "move":
        direction = action.get("direction")
        if direction not in VALID_DIRECTIONS:
            return action_result(False, "Move action needs direction: up, down, left, or right.", action_name)
        return action_result(True, "Action is valid.", action_name, direction)

    if action_name in {"pick_up", "open_door", "look"}:
        return action_result(True, "Action is valid.", action_name)
    
    return action_result(False, "Unknown validation error.")


def direction_delta(direction):
    if direction == "up":
        return -1, 0
    if direction == "down":
        return 1, 0
    if direction == "left":
        return 0, -1
    if direction == "right":
        return 0, 1
    return None, None


def script_test(): # for development and debugging
    tests = [
        {"action": "move", "direction": "up"},
        {"action": "move", "direction": "north"},
        {"action": "pick_up"},
        {"action": "open_door"},
        {"action": "look"},
        {"action": "dance"},
        "not a dict",
    ]

    for test_action in tests:
        result = validate_action(test_action)
        print(f"input={test_action} -> {result}")

    print(f"delta up: {direction_delta('up')}")
    print(f"delta right: {direction_delta('right')}")


if __name__ == "__main__":
    script_test()
