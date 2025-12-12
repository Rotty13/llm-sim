"""
main_menu_panel.py - Groups and manages all main menu/sidebar components for the llm-sim GUI
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from scripts.visualization.sim_gui.components.world_controls_panel import WorldControlsPanel
from scripts.visualization.sim_gui.components.simulation_controls_panel import SimulationControlsPanel
from scripts.visualization.sim_gui.components.agent_controls_panel import AgentControlsPanel

class MainMenuPanel(QWidget):

    def __init__(self, world_manager, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout()
        self.world_controls = WorldControlsPanel(world_manager)
        self.sim_controls = SimulationControlsPanel()
        self.agent_controls = AgentControlsPanel()
        self._layout.addWidget(self.world_controls)
        self._layout.addWidget(self.sim_controls)
        self._layout.addWidget(self.agent_controls)
        self._layout.addStretch(1)
        self.setLayout(self._layout)
        self.show_sidebar_only()

    def show_sidebar_only(self):
        self.world_controls.setVisible(True)
        self.sim_controls.setVisible(False)
        self.agent_controls.setVisible(False)

    def show_full_sidebar(self):
        self.world_controls.setVisible(True)
        self.sim_controls.setVisible(True)
        self.agent_controls.setVisible(True)

    def get_world_controls(self):
        return self.world_controls

    def get_simulation_controls(self):
        return self.sim_controls

    def get_agent_controls(self):
        return self.agent_controls
