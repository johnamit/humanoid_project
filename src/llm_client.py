import os
import json
import re
from urllib import request
from groq import Groq
from src.actions import validate_action
from src.observations import build_observation
from src.world import GridWorld


def get_provider_name():
    return os.getenv("PROVIDER", "groq").lower()


def get_model_name(provider=None):
    provider = provider or get_provider_name()
    if provider == "ollama":
        model_name = os.getenv("OLLAMA_MODEL")
        if not model_name:
            raise ValueError("Missing OLLAMA_MODEL")
        return model_name
    model_name = os.getenv("MODEL")
    if not model_name:
        raise ValueError("Missing MODEL")
    return model_name


def create_groq_client_from_env():
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("Missing API_KEY")
    model_name = get_model_name("groq")
    client = Groq(api_key=api_key)
    return client, model_name


def create_ollama_client_from_env():
    host = "http://localhost:11434"
    model_name = get_model_name("ollama")
    return host, model_name


def create_client_from_env(provider):
    if provider == "groq":
        return create_groq_client_from_env()
    if provider == "ollama":
        return create_ollama_client_from_env()
    raise ValueError(f"Unsupported PROVIDER: {provider}")


def build_system_prompt():
    return (
        "You control a robot in a 2D grid world. "
        "Return exactly one JSON object and nothing else. "
        "No markdown. No explanation. "
        "Allowed actions: "
        '{"action":"move","direction":"up"}, '
        '{"action":"move","direction":"down"}, '
        '{"action":"move","direction":"left"}, '
        '{"action":"move","direction":"right"}, '
        '{"action":"pick_up"}, '
        '{"action":"open_door"}, '
        '{"action":"look"}. '
        "Decision priority rules: "
        "1) If on_key_tile is true and has_key is false, return {\"action\":\"pick_up\"}. "
        "2) If has_key is true and is_adjacent_to_door is true and door_open is false, return {\"action\":\"open_door\"}. "
        "3) If has_key is false, move toward key coordinates. "
        "4) If has_key is true and door_open is false, move toward door coordinates. "
        "5) If last_action_blocked is true, do not repeat the same blocked move direction. "
        "6) If valid_moves is present, choose move direction only from valid_moves. "
        "7) Use look only if no better valid action exists."
    )


def build_user_prompt(observation):
    return "Observation JSON:\n" + json.dumps(observation, ensure_ascii=True)


def extract_json_object(text):
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model response.")
    return json.loads(match.group())


def call_model_groq(client, model_name, system_prompt, user_prompt):
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        stream=False,
    )
    return completion.choices[0].message.content or ""


def call_model_ollama(host, model_name, system_prompt, user_prompt):
    payload = {
        "model": model_name,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    url = host.rstrip("/") + "/api/chat"
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    with request.urlopen(req, timeout=60) as res:
        body = res.read().decode("utf-8")
    parsed = json.loads(body)
    return parsed.get("message", {}).get("content", "")


def call_model_for_provider(provider, client, model_name, system_prompt, user_prompt):
    if provider == "groq":
        return call_model_groq(client, model_name, system_prompt, user_prompt)
    if provider == "ollama":
        return call_model_ollama(client, model_name, system_prompt, user_prompt)
    raise ValueError(f"Unsupported PROVIDER: {provider}")


def choose_action(observation):
    provider = get_provider_name()
    try:
        client, model_name = create_client_from_env(provider)
    except Exception as e:
        return {"action": {"action": "look"}, "raw_response": "", "used_fallback": True, "error": str(e)}

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(observation)
    raw_response = ""
    last_error = ""

    for attempt in range(2):
        try:
            prompt = user_prompt
            if attempt == 1:
                prompt = user_prompt + "\nYour previous output was invalid. Return only one valid JSON action object."

            raw_response = call_model_for_provider(provider, client, model_name, system_prompt, prompt)
            action = extract_json_object(raw_response)
            check = validate_action(action)

            if check["valid"]:
                return {"action": action, "raw_response": raw_response, "used_fallback": False, "error": None}

            last_error = f"Invalid action schema: {action}"
        except Exception as e:
            last_error = str(e)

    if not last_error:
        last_error = "Invalid model output. Fallback used."
    return {"action": {"action": "look"}, "raw_response": raw_response, "used_fallback": True, "error": last_error}


def script_test():
    world = GridWorld.from_map_file("maps/room_s.map")
    observation = build_observation(world)
    provider = get_provider_name()
    print(f"Provider: {provider}")
    print(f"Model: {get_model_name(provider)}")
    result = choose_action(observation)
    print("LLM result:")
    print(result)


if __name__ == "__main__":
    script_test()
