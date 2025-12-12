"""
sim_gui_main.py - Main window and entry point for llm-sim GUI

Contains:
- SimMainWindow: Main application window with two views (sidebar-only and full layout)
- main(): Application entry point

LLM Usage: None (UI only)
CLI Args: None
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QSplitter, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer
from scripts.visualization.sim_gui.graph_widget.sim_graph_widget import SimGraphWidget
from scripts.visualization.sim_gui.components.main_menu_panel import MainMenuPanel
from scripts.visualization.sim_gui.components.logs_output_panel import LogsOutputPanel
from scripts.visualization.sim_gui.widgets.agent_info_widget import AgentInfoWidget
from scripts.visualization.sim_gui.widgets.world_info_widget import WorldInfoWidget
from sim.world.world_manager import WorldManager
from sim.utils.simulation_controller import SimulationController


class SimMainWindow(QMainWindow):
    """Main window for llm-sim GUI with simulation control and visualization."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("llm-sim GUI - Agent Simulation")
        self.resize(1600, 900)
        
        # Core state
        self.world_manager = WorldManager()
        self.selected_world = None
        self.agents = []
        self.world_is_open = False
        self.simulation_controller = None
        
        # Update timer for real-time display
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_simulation_display)
        self.update_timer.setInterval(500)  # Update every 500ms
        
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface with two views: sidebar-only and full layout."""
        # Main container with stacked widget for switching views
        self.main_widget = QWidget()
        self.stacked_widget = QStackedWidget()
        
        # ===== View 1: Sidebar Only (World Selection) =====
        self.sidebar_menu_panel = MainMenuPanel(self.world_manager)
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.sidebar_menu_panel)
        sidebar_layout.addStretch(1)
        sidebar_widget.setLayout(sidebar_layout)
        self.stacked_widget.addWidget(sidebar_widget)  # index 0
        
        # ===== View 2: Full Layout (Simulation View) =====
        full_widget = QWidget()
        full_layout = QVBoxLayout()
        
        # Create additional UI components for full view
        self.full_menu_panel = MainMenuPanel(self.world_manager)
        self.graph_widget = SimGraphWidget()
        self.agent_info_widget = AgentInfoWidget()
        self.world_info_widget = WorldInfoWidget()
        self.logs_output_panel = LogsOutputPanel()
        
        # Horizontal splitter: menu | graph | info panels
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h_splitter.addWidget(self.full_menu_panel)
        self.h_splitter.addWidget(self.graph_widget)
        
        # Right panel with agent and world info
        right_panel_widget = QWidget()
        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(self.agent_info_widget)
        right_panel_layout.addWidget(self.world_info_widget)
        right_panel_widget.setLayout(right_panel_layout)
        self.h_splitter.addWidget(right_panel_widget)
        self.h_splitter.setSizes([300, 800, 400])
        
        # Vertical splitter: main area | logs
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.addWidget(self.logs_output_panel)
        self.v_splitter.setSizes([700, 200])
        
        full_layout.addWidget(self.v_splitter)
        full_widget.setLayout(full_layout)
        self.stacked_widget.addWidget(full_widget)  # index 1
        
        # Set main widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.main_widget.setLayout(main_layout)
        self.setCentralWidget(self.main_widget)
        
        # Connect signals from both menu panels
        for menu_panel in [self.sidebar_menu_panel, self.full_menu_panel]:
            world_controls = menu_panel.get_world_controls()
            world_controls.log_message.connect(self._append_log)
            world_controls.world_loaded.connect(self.on_world_loaded)
            world_controls.world_saved.connect(self.on_world_saved)
            world_controls.world_closed.connect(self.on_world_closed)
            
            # Connect simulation controls
            sim_controls = menu_panel.get_simulation_controls()
            sim_controls.start_btn.clicked.connect(self.on_simulation_start)
            sim_controls.pause_btn.clicked.connect(self.on_simulation_pause)
            sim_controls.resume_btn.clicked.connect(self.on_simulation_resume)
            sim_controls.stop_btn.clicked.connect(self.on_simulation_stop)
            sim_controls.step_btn.clicked.connect(self.on_simulation_step)
            
            # Connect agent controls
            agent_controls = menu_panel.get_agent_controls()
            agent_controls.agent_selected.connect(self.on_agent_selected)
        
        # Start with sidebar-only view
        self._show_sidebar_only()
        self._append_log("[GUI] llm-sim GUI initialized. Select a world to begin.")

    def _append_log(self, msg):
        """Append a message to the logs panel."""
        if hasattr(self, 'logs_output_panel') and self.logs_output_panel:
            self.logs_output_panel.append_log(msg)

    def _show_sidebar_only(self):
        """Show only the sidebar (world selection view)."""
        self.stacked_widget.setCurrentIndex(0)

    def _show_full_layout(self):
        """Show the full layout (simulation view)."""
        self.stacked_widget.setCurrentIndex(1)

    def on_world_loaded(self, world_name):
        """Handle world loaded signal."""
        if self.world_is_open:
            self._append_log("[GUI] A world is already open. Please close it first.")
            return
        
        self.world_is_open = True
        self.selected_world = world_name
        self._append_log(f"[GUI] Loading world: {world_name}")
        
        try:
            # Load world data
            self.agents = self.world_manager.load_agents_with_schedules(world_name)
            self._append_log(f"[GUI] Loaded {len(self.agents)} agents")
            
            # Update info widgets
            self.world_info_widget.display_world(self.world_manager, world_name)
            
            # Populate agent controls in both menu panels
            for menu_panel in [self.sidebar_menu_panel, self.full_menu_panel]:
                agent_controls = menu_panel.get_agent_controls()
                agent_controls.load_agents(self.agents)
            
            # Switch to full layout
            self._show_full_layout()
            self._append_log(f"[GUI] World '{world_name}' loaded successfully")
        except Exception as e:
            self._append_log(f"[GUI] Error loading world: {e}")
            self.world_is_open = False

    def on_world_saved(self, world_name):
        """Handle world saved signal."""
        self._append_log(f"[GUI] Saving world: {world_name}")
        # TODO: Implement world state saving
        self._append_log(f"[GUI] World '{world_name}' saved (stub)")

    def on_world_closed(self, world_name):
        """Handle world closed signal."""
        if not self.world_is_open:
            self._append_log("[GUI] No world is currently open.")
            return
        
        # Stop simulation if running
        if self.simulation_controller:
            self.simulation_controller.stop()
            self.update_timer.stop()
        
        # Clear agent controls in both menu panels
        for menu_panel in [self.sidebar_menu_panel, self.full_menu_panel]:
            agent_controls = menu_panel.get_agent_controls()
            agent_controls.clear_agents()
        
        # Clear agent info display
        self.agent_info_widget.display_agent(None)
        
        self.world_is_open = False
        self.selected_world = None
        self.agents = []
        self.simulation_controller = None
        
        self._append_log(f"[GUI] World '{world_name}' closed")
        self._show_sidebar_only()
    
    def on_agent_selected(self, row):
        """Handle agent selection from agent controls."""
        if row < 0 or not self.agents or row >= len(self.agents):
            self.agent_info_widget.display_agent(None)
            self._append_log("[GUI] No agent selected")
            return
        
        agent = self.agents[row]
        self.agent_info_widget.display_agent(agent)
        self._append_log(f"[GUI] Selected agent: {agent.persona.name}")

    def on_simulation_start(self):
        """Start the simulation."""
        if not self.world_is_open:
            self._append_log("[Sim] No world is loaded. Load a world first.")
            return
        
        if self.simulation_controller and self.simulation_controller.running:
            self._append_log("[Sim] Simulation is already running")
            return
        
        self._append_log(f"[Sim] Starting simulation for world: {self.selected_world}")
        self.simulation_controller = SimulationController(
            self.world_manager, 
            self.selected_world, 
            tick_interval=1.0
        )
        self.simulation_controller.start()
        self.update_timer.start()
        self._append_log("[Sim] Simulation started")

    def on_simulation_pause(self):
        """Pause the simulation."""
        if self.simulation_controller:
            self.simulation_controller.pause()
            self._append_log("[Sim] Simulation paused")
        else:
            self._append_log("[Sim] No simulation is running")

    def on_simulation_resume(self):
        """Resume the simulation."""
        if self.simulation_controller:
            self.simulation_controller.resume()
            self._append_log("[Sim] Simulation resumed")
        else:
            self._append_log("[Sim] No simulation is running")

    def on_simulation_stop(self):
        """Stop the simulation."""
        if self.simulation_controller:
            self.simulation_controller.stop()
            self.update_timer.stop()
            self._append_log("[Sim] Simulation stopped")
        else:
            self._append_log("[Sim] No simulation is running")

    def on_simulation_step(self):
        """Advance simulation by one tick."""
        if self.simulation_controller:
            self.simulation_controller.step()
            self._update_simulation_display()
            self._append_log("[Sim] Advanced one tick")
        else:
            self._append_log("[Sim] No simulation is running")

    def _update_simulation_display(self):
        """Update the display with current simulation state."""
        if not self.simulation_controller:
            return
        
        state = self.simulation_controller.get_state()
        
        # Update simulation status in menu panels
        for menu_panel in [self.sidebar_menu_panel, self.full_menu_panel]:
            sim_controls = menu_panel.get_simulation_controls()
            status = f"Tick: {state['tick']} | "
            status += "Running" if state['running'] and not state['paused'] else "Paused" if state['paused'] else "Stopped"
            sim_controls.status_label.setText(f"Simulation: {status}")


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)
    window = SimMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
