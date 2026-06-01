<img src="assets/humanoid.png" alt="Humanoid" width="900"><br>

[<img src="https://img.shields.io/badge/Google_Drive-Demo Videos-black?style=for-the-badge&logo=google%20drive&logoColor=white&labelColor=4285F4" alt="View Videos on Drive"/>](https://drive.google.com/drive/folders/1bBEq9L27xcJ3dbpxMzgDkB5M00k15xmw?usp=sharing)

<p>
  <a href="#problem-statement"><img src="https://img.shields.io/badge/Problem-111111?style=for-the-badge" alt="Problem Statement"></a>
  <a href="#implementation"><img src="https://img.shields.io/badge/Implementation-111111?style=for-the-badge" alt="Implementation"></a>
  <a href="#world-observations-and-actions"><img src="https://img.shields.io/badge/World%20%26%20Actions-111111?style=for-the-badge" alt="World, Observations, and Actions"></a>
  <a href="#how-to-run"><img src="https://img.shields.io/badge/Run-111111?style=for-the-badge" alt="How To Run"></a>
  <a href="#example-runs"><img src="https://img.shields.io/badge/Example%20Runs-111111?style=for-the-badge" alt="Example Runs"></a>
  <a href="#limitations-and-future-work"><img src="https://img.shields.io/badge/Limitations-111111?style=for-the-badge" alt="Limitations and Future Work"></a>
  <a href="#license"><img src="https://img.shields.io/badge/License-111111?style=for-the-badge" alt="License"></a>
</p>

## Problem Statement
This project implements an LLM agent in a virtual 2D world. The agent observes the environment, selects actions, and completes a goal. The core focus is the harness between the model and the world, not game complexity.

## Implementation
The environment is a grid world loaded from text map files. The map uses `#` for walls, `.` for floor, `A` for agent start, `K` for key, and `D` for a locked door. The mission is complete when the agent picks up the key, moves adjacent to the door, and uses `open_door`.

The agent loop is step-based. On each step, the system builds a JSON observation, sends it to an LLM, validates the returned JSON action, applies the action in the world, and renders the updated state. Invalid or poor model outputs are handled safely with validation and fallback behavior ('look') so the run does not crash.

The project supports ASCII rendering and pygame rendering. World logic is separated from rendering. The LLM never mutates world state directly.

## World, Observations, and Actions
The world is a text-defined 2D grid. Symbols are `#` (wall), `.` (floor), `A` (agent start), `K` (key), and `D` (door). The primary evaluation maps are `maps/room_xs.map` and `maps/room_s.map`.

Each step sends a JSON observation to the model. The observation includes step count, agent position, key state, door state, valid moves, and last action result.

Each step expects one JSON action from a constrained action space. Allowed actions are `move` with `up/down/left/right`, `pick_up`, `open_door`, and `look`. Every action is validated before world state updates.

## How To Run
Create an environment and install dependencies first.

```bash
conda create -n humanoid python=3.10 -y
conda activate humanoid

pip install -r requirements.txt
```

Then set provider and model environment variables. For this project, I used Groq's llama-3.3-70b-versatile model for the final runs. To save token costs, I used Ollama's local qwen3.5:9b model for development and testing, which also performed well on the task. Results for both models can be found in the results folder.

### Groq (API)
```bash
export PROVIDER=groq
export MODEL=llama-3.3-70b-versatile
export API_KEY=YOUR_API_KEY
```

### Ollama (Local)
```bash
export PROVIDER=ollama
export OLLAMA_MODEL=qwen3.5:9b
```

Run the project with the default entrypoint.

```bash
python -m src.main
```

To run the model with specific maps, renderers, and step limits, use the following commands:

```bash
# Run the agent on room_xs. Ascii and pygame renderings are supported.
python -m src.main --render ascii --map maps/room_xs.map --max-steps 60
python -m src.main --render pygame --map maps/room_xs.map --max-steps 60

# Run the agent on room_xs. Ascii and pygame renderings are supported.
python -m src.main --render ascii --map maps/room_s.map --max-steps 60
python -m src.main --render pygame --map maps/room_s.map --max-steps 60
```

## Example Runs
Demo recordings of pygame 2D world runs using the llama-3.3-70b-versatile model via groq can be found [here](https://drive.google.com/drive/folders/1bBEq9L27xcJ3dbpxMzgDkB5M00k15xmw?usp=sharing).

Demo logs of ASCII runs using both ollama qwen models and the groq llama-3.3-70b-versatile model can be found in the results folder.


## Limitations and Future Work
On the baseline maps (room_xs.map and room_s.map), the agent completes the key-door task reliably with structured observations and constrained actions. On the maze map, results are less consistent. The model can fall into repeated behavior, such as moving up/down in loops or repeatedly trying directions that lead into walls, before it recovers. Longer maze runs are also more exposed to API rate limits, which can trigger fallback actions and reduce progress.

This can be seen in the maze map run in results. To reproduce the maze run please use the following command:

```bash
python -m src.main --render ascii --map maps/room_maze.map --max-steps 30
python -m src.main --render pygame --map maps/room_maze.map --max-steps 30
```

This is expected with a single-step action policy that does not maintain a strong long-horizon plan. A practical future improvement is to add a small planner layer that sets short subgoals, such as “reach the next open corridor,” then “reach key,” then “reach door.” A second improvement is to add short action memory, so the agent can avoid repeating recent failed action sequences (for example, repeated blocked moves in the same local area).

## License
This project is released under the MIT License.
