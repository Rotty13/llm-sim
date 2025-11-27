# llm-sim

A tiny LLM-driven agent sandbox. Agents live in a small city, make decisions each tick, and write memories. Configurable via YAML.

## Quick start

```bash
# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the simulation
python scripts/run_sim.py
```

## Features

- **Agent Simulation**: Agents interact with the environment and make decisions.
- **Configurable Worlds**: Define cities, personas, and places using YAML files.
- **LLM Integration**: Agents use LLMs for decision-making and memory writing.

## Directory Structure

- `sim/`: Core simulation modules.
- `scripts/`: CLI tools and utilities.
- `worlds/`: Example worlds and scenario templates.
- `configs/`: Data schemas and config files.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License.
