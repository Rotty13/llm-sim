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

# Run the GUI
python gui_launcher.py

# Or run the simulation from CLI
python scripts/run_sim.py
```

## Features

- **Graphical User Interface**: Modern PyQt5-based GUI for real-time simulation control and visualization
- **Agent Simulation**: Agents interact with the environment and make decisions
- **Configurable Worlds**: Define cities, personas, and places using YAML files
- **LLM Integration**: Agents use LLMs for decision-making and memory writing
- **Real-time Visualization**: View agent positions, activities, and world state in real-time
- **Simulation Controls**: Start, pause, resume, stop, and step through simulations

## Using the GUI

Launch the GUI with:
```bash
python gui_launcher.py
```

The GUI provides:
- **World Management**: Load, save, and close simulation worlds
- **Simulation Controls**: Start/pause/resume/stop simulation with adjustable speed
- **Real-time Visualization**: Interactive graph view of the world and agents
- **Agent Information**: Detailed view of agent states, memories, and activities
- **World Information**: Overview of places, agents, and world statistics
- **Live Logs**: Real-time simulation event logging

### GUI Workflow
1. Select a world from the dropdown menu
2. Click "Load World" to open the full interface
3. Use simulation controls to start/pause/step through ticks
4. View agent and world information in the side panels
5. Monitor simulation progress in the logs panel

## Directory Structure

- `sim/`: Core simulation modules
- `scripts/`: CLI tools and utilities
- `scripts/visualization/sim_gui/`: GUI components and widgets
- `worlds/`: Example worlds and scenario templates
- `configs/`: Data schemas and config files

## Requirements

- Python 3.8+
- PyQt5 (for GUI)
- numpy (for visualization)
- PyYAML (for configuration)
- requests (for LLM API calls)

## Contributing

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Submit a pull request with a detailed description of your changes

## License

This project is licensed under the MIT License.
