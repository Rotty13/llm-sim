"""
sim_cli.py - Command-line interface for controlling llm-sim simulations


Commands:
    list-worlds                             List available worlds
    start <world> [--ticks N] [--speed S]   Start simulation
    stop                                    Stop simulation
    pause                                   Pause simulation
    resume                                  Resume simulation
    step                                    Advance one tick
    speed <S>                               Set tick speed (seconds)
    state                                   Show current simulation state
    reload-world <world>                    Reload or switch to a different world
    show-log [N]                            Show last N log lines (default 10)
    gui                                     Show/hide GUI window
    gui-status                              Show if GUI is open or closed
    last-error                              Show last error/exception
    exit                                    Exit CLI

LLM Usage: None
CLI Args: See above
"""

import sys
import threading
from sim.utils.simulation_controller import SimulationController
from sim.world.world_manager import WorldManager

# Placeholder for GUI integration
try:
    from scripts.visualization.sim_gui.sim_gui_main import SimMainWindow
    from PyQt5.QtWidgets import QApplication
except ImportError:
    SimMainWindow = None
    QApplication = None

class SimCLI:
    def __init__(self):
        self.world_manager = WorldManager()
        self.sim = None
        self.gui_app = None
        self.gui_window = None
        self.gui_thread = None

    def run(self):
        print("llm-sim Simulation CLI. Type 'help' for commands.")

        self.last_error = None
        while True:
            try:
                cmd = input("sim> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
            if not cmd:
                continue
            args = cmd.split()
            try:
                if args[0] == 'list-worlds':
                    worlds = self.world_manager.list_worlds()
                    print("Available worlds:", ", ".join(worlds) if worlds else "(none)")
                elif args[0] == 'start' and len(args) >= 2:
                    world = args[1]
                    ticks = None
                    speed = 0.5
                    for i, arg in enumerate(args):
                        if arg == '--ticks' and i+1 < len(args):
                            ticks = int(args[i+1])
                        if arg == '--speed' and i+1 < len(args):
                            speed = float(args[i+1])
                    self.sim = SimulationController(self.world_manager, world, tick_interval=speed)
                    self.sim.start(max_ticks=ticks)
                    print(f"Simulation started for world '{world}' (speed={speed}s/tick)")
                elif args[0] == 'stop' and self.sim:
                    self.sim.stop()
                    print("Simulation stopped.")
                elif args[0] == 'pause' and self.sim:
                    self.sim.pause()
                    print("Simulation paused.")
                elif args[0] == 'resume' and self.sim:
                    self.sim.resume()
                    print("Simulation resumed.")
                elif args[0] == 'step' and self.sim:
                    self.sim.step()
                    print("Simulation advanced one tick.")
                elif args[0] == 'speed' and self.sim and len(args) == 2:
                    self.sim.set_speed(float(args[1]))
                    print(f"Tick speed set to {args[1]}s.")
                elif args[0] == 'state' and self.sim:
                    state = self.sim.get_state()
                    print(f"Tick: {state['tick']}, Running: {state['running']}, Paused: {state['paused']}")
                    print(f"World: {state['world']}")
                    print(f"Agents: {len(state['agents'])}")
                elif args[0] == 'reload-world' and len(args) == 2:
                    world = args[1]
                    if self.sim:
                        self.sim.stop()
                    self.sim = SimulationController(self.world_manager, world)
                    self.sim.start()
                    print(f"World reloaded and simulation started for '{world}'.")
                elif args[0] == 'show-log' and self.sim:
                    n = int(args[1]) if len(args) > 1 else 10
                    # Placeholder: logs integration
                    print(f"(Log display not yet implemented, would show last {n} lines)")
                elif args[0] == 'gui':
                    self.show_gui()
                elif args[0] == 'gui-status':
                    if self.gui_window and self.gui_window.isVisible():
                        print("GUI is open.")
                    else:
                        print("GUI is closed.")
                elif args[0] == 'last-error':
                    if self.last_error:
                        print(self.last_error)
                    else:
                        print("No errors recorded.")
                elif args[0] == 'help':
                    print(__doc__)
                elif args[0] == 'exit':
                    if self.sim:
                        self.sim.stop()
                    print("Exiting.")
                    break
                else:
                    print("Unknown or invalid command. Type 'help' for usage.")
            except Exception as e:
                self.last_error = e
                print(f"Error: {e}")

    def show_gui(self):
        if SimMainWindow is None or QApplication is None:
            print("GUI not available (PyQt5 not installed or import failed).")
            return
        if self.gui_app is None:
            self.gui_app = QApplication(sys.argv)
        if self.gui_window is None:
            self.gui_window = SimMainWindow()
        self.gui_window.show()
        # Run the GUI in a separate thread so CLI remains interactive
        if self.gui_thread is None or not self.gui_thread.is_alive():
            self.gui_thread = threading.Thread(target=self.gui_app.exec_, daemon=True)
            self.gui_thread.start()
        print("GUI window shown. Close the window to hide (simulation continues).")

if __name__ == "__main__":
    SimCLI().run()
