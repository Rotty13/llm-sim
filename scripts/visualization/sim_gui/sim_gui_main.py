"""
sim_gui_main.py - Main window and entry point for llm-sim GUI

Contains:
- SimMainWindow: Main application window
- main(): Application entry point

LLM Usage: None (UI only)
CLI Args: None
"""

import sys


from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt
from scripts.visualization.sim_gui.graph_widget.sim_graph_widget import SimGraphWidget
from scripts.visualization.sim_gui.components.main_menu_panel import MainMenuPanel
from scripts.visualization.sim_gui.components.logs_output_panel import LogsOutputPanel
from scripts.visualization.sim_gui.widgets.agent_info_widget import AgentInfoWidget
from scripts.visualization.sim_gui.widgets.world_info_widget import WorldInfoWidget
from sim.world.world_manager import WorldManager



class SimMainWindow(QMainWindow):

            
    def __init__(self):
        super().__init__()
        self.setWindowTitle("llm-sim GUI")
        self.resize(1600, 860)
        self.world_manager = WorldManager()
        self.selected_world = None
        self.agents = []
        self.world_is_open = False
        self._init_ui()

    def _init_ui(self):
        from PyQt5.QtWidgets import QStackedLayout
        self.main_widget = QWidget()
        self.stacked_layout = QStackedLayout()

        
        # Create two MainMenuPanel instances: one for sidebar, one for full layout
        self.sidebar_menu_panel = MainMenuPanel(self.world_manager)
        self.full_menu_panel = MainMenuPanel(self.world_manager)

        # Main menu/sidebar only widget (shares the same instance)
        sidebar_only_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.sidebar_menu_panel)
        sidebar_only_widget.setLayout(sidebar_layout)
        self.stacked_layout.addWidget(sidebar_only_widget)  # index 0

        # Full layout widget (shares the same instance)
        full_widget = QWidget()
        full_layout = QVBoxLayout()

        self.h_splitter = QSplitter()
        self.h_splitter.setOrientation(Qt.Orientation.Horizontal)
        self.h_splitter.addWidget(self.full_menu_panel)
   
        full_widget.setLayout(full_layout)
        self.stacked_layout.addWidget(full_widget)  # index 1

        self.main_widget.setLayout(self.stacked_layout)
        self.setCentralWidget(self.main_widget)

        # Connect world controls panel signals to handlers and logs (for both instances)
        for menu_panel in [self.sidebar_menu_panel, self.full_menu_panel]:
            world_controls = menu_panel.get_world_controls()
            world_controls.log_message.connect(self._append_log)
            world_controls.world_loaded.connect(self.on_world_loaded)
            world_controls.world_saved.connect(self.on_world_saved)
            world_controls.world_closed.connect(self.on_world_closed)

        self._show_sidebar_only()

    def _append_log(self, msg):
        # Stub: do nothing if logs_output_panel is not initialized
        if hasattr(self, 'logs_output_panel') and self.logs_output_panel:
            self.logs_output_panel.append_log(msg)
        # else: ignore

    def _show_sidebar_only(self):
        self.stacked_layout.setCurrentIndex(0)

    def _show_full_layout(self):
        self.stacked_layout.setCurrentIndex(1)

        self._show_sidebar_only()


    def on_world_loaded(self, world_name):
        if self.world_is_open:
            self._append_log(f"[Main] A world is already open. Please close it before loading another.")
            return
        self.world_is_open = True
        self._append_log(f"[Main] World loaded: {world_name}")
        self._show_full_layout()

    def on_world_saved(self, world_name):
        self.logs_output_panel.append_log(f"[Main] World saved: {world_name}")
        # TODO: Add logic to save world state


    def on_world_closed(self, world_name):
        if not self.world_is_open:
            self._append_log(f"[Main] No world is currently open.")
            return
        self.world_is_open = False
        self._append_log(f"[Main] World closed: {world_name}")
        self._show_sidebar_only()
        def _sync_world_controls(self, src_panel, dst_panel):
            # Copy world selection state from src_panel to dst_panel
            src_controls = src_panel.get_world_controls()
            dst_controls = dst_panel.get_world_controls()
            # Sync dropdown selection
            idx = src_controls.world_dropdown.currentIndex()
            self.main_layout = QVBoxLayout()
            self.graph_widget = SimGraphWidget()
            self.agent_info_widget = AgentInfoWidget()
            self.world_info_widget = WorldInfoWidget()
            self.logs_output_panel = LogsOutputPanel()
            self.h_splitter = QSplitter()
            self.h_splitter.setOrientation(Qt.Orientation.Horizontal)
            self.h_splitter.addWidget(self.sidebar_menu_panel)
            self.h_splitter.addWidget(self.graph_widget)
            right_panel = QVBoxLayout()
            right_panel.addWidget(self.agent_info_widget)
            right_panel.addWidget(self.world_info_widget)
            right_container = QWidget()
            right_container.setLayout(right_panel)
            self.h_splitter.addWidget(right_container)
            self.v_splitter = QSplitter()
            self.v_splitter.setOrientation(Qt.Orientation.Vertical)
            self.v_splitter.addWidget(self.h_splitter)
            self.v_splitter.addWidget(self.logs_output_panel)
            self.v_splitter.setSizes([800, 120])
            self.main_layout.addWidget(self.v_splitter)
            self.main_widget.setLayout(self.main_layout)
            self.setCentralWidget(self.main_widget)
            world_controls = self.sidebar_menu_panel.get_world_controls()
            world_controls.log_message.connect(self._append_log)
            world_controls.world_loaded.connect(self.on_world_loaded)
            world_controls.world_saved.connect(self.on_world_saved)
            world_controls.world_closed.connect(self.on_world_closed)
            self._show_sidebar_only()
            dst_controls.world_dropdown.setCurrentIndex(idx)
        # TODO: Add logic to close world and update panels

            self.sidebar_menu_panel.show_sidebar_only()
            self.graph_widget.hide()
            self.agent_info_widget.hide()
            self.world_info_widget.hide()
            self.logs_output_panel.hide()
            self.h_splitter.setSizes([1, 0, 0])


    def on_world_selected(self, index):
        self.sidebar_menu_panel.show_full_sidebar()
        self.graph_widget.show()
        self.agent_info_widget.show()
        self.world_info_widget.show()
        self.logs_output_panel.show()
        self.h_splitter.setSizes([300, 800, 400])
        if index == 0:
            self.selected_world = None
            self.agent_list.clear()
            self.agent_dropdown.clear()
            self.agents = []
            self.agent_info_widget.display_agent(None)
            self.world_info_widget.display_world(self.world_manager, None)
            return
        world_name = self.world_dropdown.currentText()
        self.selected_world = world_name
        self.agents = self.world_manager.load_agents_with_schedules(world_name)
        agent_names = [agent.persona.name for agent in self.agents]
        self.agent_list.clear()
        self.agent_list.addItems(agent_names)
        self.agent_dropdown.clear()
        self.agent_dropdown.addItem("All Agents")
        self.agent_dropdown.addItems(agent_names)
        self.agent_info_widget.display_agent(None)
        self.world_info_widget.display_world(self.world_manager, world_name)

    def on_agent_selected(self, row):
        if row < 0 or row >= len(self.agents):
            self.agent_info_widget.display_agent(None)
            return
        agent = self.agents[row]
        self.agent_info_widget.display_agent(agent)

    def on_agent_dropdown_selected(self, index):
        if index == 0:
            self.agent_info_widget.display_agent(None)
            return
        agent_name = self.agent_dropdown.currentText()
        for agent in self.agents:
            if agent.persona.name == agent_name:
                self.agent_info_widget.display_agent(agent)
                break

def main():
    app = QApplication(sys.argv)
    window = SimMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
