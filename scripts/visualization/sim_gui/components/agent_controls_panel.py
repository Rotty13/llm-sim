"""
agent_controls_panel.py - Panel for agent selection and agent-level actions
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QComboBox, QPushButton
from PyQt5.QtCore import Qt

class AgentControlsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.agent_list = QListWidget()
        self.agent_dropdown = QComboBox()
        self.edit_btn = QPushButton("Edit Agent")
        self.add_btn = QPushButton("Add Agent")
        self.remove_btn = QPushButton("Remove Agent")

        layout.addWidget(QLabel("Agents"))
        layout.addWidget(self.agent_list)
        layout.addWidget(QLabel("Search/Select Agent"))
        layout.addWidget(self.agent_dropdown)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.remove_btn)
