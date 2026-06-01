import argparse
from src.agent_loop import run_llm_approach
from src.llm_client import get_provider_name, get_model_name

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", default="maps/room_s.map")
    parser.add_argument("--render", choices=["none", "ascii", "pygame"], default="pygame")
    parser.add_argument("--max-steps", type=int, default=30)
    return parser.parse_args()

def run():
    args = parse_args()

    print("Humanoid Internship Application Project")
    print(f"Map: {args.map}")
    print(f"Render: {args.render}")
    print(f"Max steps: {args.max_steps}")
    provider = get_provider_name()
    model = get_model_name(provider)
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    return run_llm_approach(args.map, args.render, args.max_steps)

if __name__ == "__main__":
    run()
