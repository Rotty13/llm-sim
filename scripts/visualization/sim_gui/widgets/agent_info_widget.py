"""
agent_info_widget.py - Widget for displaying agent information in llm-sim GUI

LLM Usage: None (UI only)
CLI Args: None
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class AgentInfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.v_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.v_layout.addWidget(QLabel("Agent Information"))
        self.v_layout.addWidget(self.info_text)
        self.setLayout(self.v_layout)

    def display_agent(self, agent):
        if agent is None:
            self.info_text.setText("")
            return
        persona = agent.persona
        info = f"Name: {persona.name}\nAge: {persona.age}\nJob: {persona.job}\nCity: {persona.city}\nBio: {persona.bio}\nValues: {', '.join(persona.values)}\nGoals: {', '.join(persona.goals)}\nTraits: {persona.traits}\nAspirations: {', '.join(persona.aspirations)}"
        self.info_text.setText(info)
