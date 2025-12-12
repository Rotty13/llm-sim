
Current Task: Integrate Simulation GUI with Core Engine

Objective:
Integrate scripts/visualization/sim_gui/sim_gui_main.py with the modular simulation engine in sim/, enabling real-time visualization and control of simulation state, agent actions, and world data via the GUI.

Plan:
1. Review sim_gui_main.py to identify its current input/output and UI structure.
2. Define the core simulation API: what data and controls the GUI needs from sim (e.g., agent states, world state, tick controls).
3. Identify entry points in sim/ (likely sim/world/world_manager.py, sim/agents/agents.py, sim/scheduler/scheduler.py) for data access and simulation control.
4. Design a communication layer (direct Python calls, or an event/message system) between the GUI and sim modules.
5. Refactor sim_gui_main.py to:
	- Load world/agent data via WorldManager.
	- Display simulation state (agents, world, ticks) in the GUI.
	- Provide controls to start/stop/pause simulation, step ticks, and visualize agent actions.
6. Implement callbacks or listeners in sim/ to update the GUI in real time.
7. Test integration with a sample world (e.g., worlds/World_0).
8. Document the integration points and update this file as progress is made.



