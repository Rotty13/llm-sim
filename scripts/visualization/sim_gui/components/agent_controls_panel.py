"""
agent_controls_panel.py - Panel for agent selection and agent-level actions
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QComboBox, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class AgentControlsPanel(QWidget):
    # Signals
    agent_selected = pyqtSignal(int)  # row in list
    agent_filter_changed = pyqtSignal(str)  # filter text
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Agent list
        layout.addWidget(QLabel("Agents in World"))
        self.agent_list = QListWidget()
        self.agent_list.currentRowChanged.connect(self._on_agent_selected)
        layout.addWidget(self.agent_list)
        
        # Agent dropdown/search
        layout.addWidget(QLabel("Quick Select"))
        self.agent_dropdown = QComboBox()
        self.agent_dropdown.currentIndexChanged.connect(self._on_dropdown_changed)
        layout.addWidget(self.agent_dropdown)
        
        # Action buttons
        self.edit_btn = QPushButton("✏ Edit Agent")
        self.add_btn = QPushButton("➕ Add Agent")
        self.remove_btn = QPushButton("➖ Remove Agent")
        
        # Disable buttons initially (until world is loaded)
        self.edit_btn.setEnabled(False)
        self.add_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.remove_btn)
    
    def _on_agent_selected(self, row):
        """Handle agent selection in list."""
        if row >= 0:
            self.agent_selected.emit(row)
            # Sync dropdown
            if row + 1 < self.agent_dropdown.count():  # +1 for "All Agents"
                self.agent_dropdown.setCurrentIndex(row + 1)
    
    def _on_dropdown_changed(self, index):
        """Handle agent selection in dropdown."""
        if index > 0:  # Skip "All Agents" at index 0
            list_row = index - 1
            self.agent_list.setCurrentRow(list_row)
        elif index == 0:
            self.agent_list.clearSelection()
            self.agent_selected.emit(-1)
    
    def load_agents(self, agents):
        """Load agent list from world data."""
        self.agent_list.clear()
        self.agent_dropdown.clear()
        self.agent_dropdown.addItem("All Agents")
        
        if not agents:
            self.edit_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)
            return
        
        # Populate list and dropdown
        for agent in agents:
            name = agent.persona.name if hasattr(agent, 'persona') else str(agent)
            self.agent_list.addItem(name)
            self.agent_dropdown.addItem(name)
        
        # Enable buttons
        self.add_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
    
    def clear_agents(self):
        """Clear all agents from display."""
        self.agent_list.clear()
        self.agent_dropdown.clear()
        self.agent_dropdown.addItem("All Agents")
        self.edit_btn.setEnabled(False)
        self.add_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
