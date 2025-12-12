# llm-sim GUI Documentation

## Overview

The llm-sim GUI provides a comprehensive graphical interface for running, visualizing, and controlling agent-based simulations. Built with PyQt5, it offers real-time monitoring, interactive controls, and detailed information panels.

## Installation

### Requirements
- Python 3.8 or higher
- PyQt5
- numpy
- PyYAML
- requests

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Launching the GUI

### Quick Launch
```bash
python gui_launcher.py
```

### From Python Code
```python
from PyQt5.QtWidgets import QApplication
from scripts.visualization.sim_gui.sim_gui_main import SimMainWindow
import sys

app = QApplication(sys.argv)
window = SimMainWindow()
window.show()
sys.exit(app.exec_())
```

## GUI Components

### 1. World Controls Panel

Located in the left sidebar, this panel manages world selection and loading.

**Features:**
- **World Selection**: Dropdown menu listing all available worlds
- **Load World**: Opens the selected world for simulation
- **Delete World**: Removes a world (with confirmation)
- **Save World**: Saves current world state (when implemented)
- **Close World**: Closes the active world and returns to selection view

**Workflow:**
1. Select a world from the dropdown
2. Click "Load World"
3. The interface expands to show full simulation controls

### 2. Simulation Controls Panel

Controls simulation execution and timing.

**Buttons:**
- **▶ Start**: Begin simulation from current state
- **⏸ Pause**: Temporarily halt simulation (can be resumed)
- **▶ Resume**: Continue paused simulation
- **⏹ Stop**: Stop simulation completely
- **⏭ Step**: Advance simulation by exactly one tick

**Settings:**
- **Tick Speed**: Time (in seconds) between simulation ticks (0.1 - 10.0s)
- **Max Ticks**: Maximum number of ticks to run (0 = unlimited)

**Status Display:**
Shows current simulation state: `Tick: N | Running/Paused/Stopped`

### 3. Agent Controls Panel

Manage and inspect individual agents.

**Features:**
- **Agent List**: Scrollable list of all agents in the world
- **Agent Dropdown**: Quick search and selection
- **Edit Agent**: Modify agent properties (planned)
- **Add Agent**: Create new agents (planned)
- **Remove Agent**: Delete agents (planned)

### 4. Graph Visualization Widget

Interactive 2D graph view of the simulation world.

**Features:**
- **Place Nodes**: Circular nodes representing locations
- **Zoom**: Mouse wheel to zoom in/out
- **Pan**: Click and drag to pan around the world
- **Agent Visualization**: (Planned) Real-time agent positions

**Controls:**
- **Mouse Wheel**: Zoom in/out
- **Left Click + Drag**: Pan view
- **Mouse Position**: Coordinates transform to zoom/pan

### 5. Agent Information Widget

Displays detailed information about the selected agent.

**Information Shown:**
- Name
- Age
- Job/Occupation
- City/Location
- Biography
- Values and beliefs
- Goals and aspirations
- Personality traits
- Current state (planned)
- Recent activities (planned)

### 6. World Information Widget

Provides overview of the entire world.

**Information Shown:**
- List of all places
- Place properties and capabilities
- World statistics (planned)
- Active events (planned)

### 7. Logs Output Panel

Real-time log of simulation events and system messages.

**Features:**
- Scrollable text output
- Timestamped messages
- Color-coded by source: `[GUI]`, `[Sim]`, `[World]`
- Auto-scroll to latest messages
- Clear logs button (planned)

## Usage Guide

### Basic Simulation Workflow

1. **Launch GUI**
   ```bash
   python gui_launcher.py
   ```

2. **Load a World**
   - Select world from dropdown (e.g., "World_0")
   - Click "Load World"
   - Wait for confirmation in logs

3. **Start Simulation**
   - Adjust tick speed if desired (default: 1.0s)
   - Set max ticks if desired (default: 1000)
   - Click "▶ Start"

4. **Monitor Progress**
   - Watch status update in simulation controls
   - View logs for detailed events
   - Select agents to inspect their state

5. **Control Execution**
   - **Pause**: Temporarily halt (data preserved)
   - **Resume**: Continue from paused state
   - **Step**: Advance one tick at a time for debugging
   - **Stop**: End simulation (cannot resume)

6. **Close World**
   - Click "Close World" when finished
   - Returns to world selection view

### Advanced Features

#### Adjusting Simulation Speed
- Lower values (0.1-0.5s): Fast simulation for testing
- Medium values (0.5-2.0s): Balanced for observation
- Higher values (2.0-10.0s): Slow for detailed analysis

#### Single-Step Debugging
1. Load world without starting simulation
2. Use "⏭ Step" button repeatedly
3. Observe changes between each tick
4. Useful for debugging agent behavior

#### Monitoring Specific Agents
1. Click agent name in Agent List
2. View detailed info in Agent Information panel
3. Track changes as simulation progresses

## Keyboard Shortcuts

(Planned)
- `Ctrl+O`: Open world
- `Ctrl+S`: Save world state
- `Space`: Start/Pause simulation
- `Right Arrow`: Step forward one tick
- `Ctrl+Q`: Quit application

## Troubleshooting

### GUI Won't Launch

**Check Dependencies:**
```bash
python -c "import PyQt5; print('PyQt5 OK')"
python -c "import numpy; print('numpy OK')"
```

**Reinstall Requirements:**
```bash
pip install --force-reinstall -r requirements.txt
```

### World Won't Load

**Verify World Exists:**
```bash
python scripts/cli/world_cli.py list
```

**Check World Files:**
```bash
ls worlds/World_0/
# Should show: city.yaml, personas.yaml, world.yaml
```

### Simulation Won't Start

- Ensure world is loaded first
- Check logs panel for error messages
- Verify LLM is configured (if required)

### Performance Issues

- Increase tick speed (slower ticks = less CPU)
- Reduce max ticks
- Close other applications
- Check system resources

## Architecture

### Component Hierarchy
```
SimMainWindow (QMainWindow)
├── QStackedWidget (view switcher)
│   ├── Sidebar View (world selection)
│   │   └── MainMenuPanel
│   └── Full View (simulation)
│       ├── MainMenuPanel (left)
│       ├── SimGraphWidget (center)
│       ├── Info Panels (right)
│       │   ├── AgentInfoWidget
│       │   └── WorldInfoWidget
│       └── LogsOutputPanel (bottom)
```

### Data Flow
1. User action (button click) → Signal emitted
2. Signal → Main window handler
3. Handler → Simulation controller
4. Controller → World/Agent updates
5. Updates → Display refresh via timer
6. Display → Widget updates

### Update Cycle
- QTimer fires every 500ms when simulation running
- Fetches current state from SimulationController
- Updates all display components
- Logs any errors or warnings

## Extending the GUI

### Adding New Panels

1. Create widget class in `scripts/visualization/sim_gui/widgets/`
2. Inherit from `QWidget`
3. Implement display methods
4. Add to main window layout in `sim_gui_main.py`

### Adding New Controls

1. Create control panel in `scripts/visualization/sim_gui/components/`
2. Define signals for user actions
3. Connect signals in main window
4. Implement handlers

### Customizing Appearance

Edit styles in component constructors:
```python
button.setStyleSheet("background-color: #4CAF50; color: white;")
```

## Known Limitations

1. **No Real-time Agent Visualization**: Agent positions not yet shown on graph
2. **No Save/Load State**: World state persistence not implemented in GUI
3. **No Agent Editing**: Runtime agent modification not available
4. **No Metrics Dashboard**: Statistics visualization planned
5. **Single World**: Can only have one world open at a time

## Planned Features

- [ ] Real-time agent position visualization on graph
- [ ] Agent path history trails
- [ ] Interactive agent creation/editing
- [ ] World editor with place management
- [ ] Metrics dashboard with charts
- [ ] Event timeline visualization
- [ ] Export logs and statistics
- [ ] Theme customization
- [ ] Multi-world tabs
- [ ] Keyboard shortcuts

## API Reference

### SimMainWindow

**Methods:**
- `on_world_loaded(world_name: str)`: Handle world load
- `on_world_saved(world_name: str)`: Handle world save
- `on_world_closed(world_name: str)`: Handle world close
- `on_simulation_start()`: Start simulation
- `on_simulation_pause()`: Pause simulation
- `on_simulation_resume()`: Resume simulation
- `on_simulation_stop()`: Stop simulation
- `on_simulation_step()`: Advance one tick

**Attributes:**
- `world_manager`: WorldManager instance
- `simulation_controller`: SimulationController instance
- `selected_world`: Currently loaded world name
- `agents`: List of agents in current world

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation in `docs/`
- Review code comments in GUI source files

## License

MIT License - See LICENSE file for details
