"""
agent_editor.py - Editor widget for modifying agent data in-memory

LLM Usage: None (UI only)
CLI Args: None
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit

class AgentEditor(QWidget):
    """
    Editor for modifying agent data in-memory.
    Encompasses the agent classes(e.g., Agent, Persona) and allows editing of their attributes.
    """
    def __init__(self, agent=None, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.dirty = False
        self.v_layout = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.bio_edit = QTextEdit()
        self.save_btn = QPushButton("Apply Changes")
        self.save_btn.clicked.connect(self.apply_changes)
        self.v_layout.addWidget(QLabel("Edit Agent Name:"))
        self.v_layout.addWidget(self.name_edit)
        self.v_layout.addWidget(QLabel("Edit Agent Bio:"))
        self.v_layout.addWidget(self.bio_edit)
        self.v_layout.addWidget(self.save_btn)
        self.setLayout(self.v_layout)
        if agent:
            self.load_agent(agent)

    def load_agent(self, agent):
        self.agent = agent
        self.name_edit.setText(agent.persona.name)
        self.bio_edit.setText(agent.persona.bio)
        self.dirty = False

    def apply_changes(self):
        if not self.agent:
            return
        changed = False
        new_name = self.name_edit.text()
        new_bio = self.bio_edit.toPlainText()
        if self.agent.persona.name != new_name:
            self.agent.persona.name = new_name
            changed = True
        if self.agent.persona.bio != new_bio:
            self.agent.persona.bio = new_bio
            changed = True
        if changed:
            self.dirty = True
        # Optionally: emit a signal here to notify parent/main window
