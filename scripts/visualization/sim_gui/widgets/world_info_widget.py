"""
world_info_widget.py - Widget for displaying world information in llm-sim GUI

LLM Usage: None (UI only)
CLI Args: None
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class WorldInfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.v_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.v_layout.addWidget(QLabel("World Information"))
        self.v_layout.addWidget(self.info_text)
        self.setLayout(self.v_layout)

    def display_world(self, world_manager, world_name):
        if not world_name:
            self.info_text.setText("")
            return
        places = world_manager.load_places(world_name)
        if not places:
            self.info_text.setText("No place data available.")
            return
        place_info = "Places in world:\n"
        for place_name, place_data in places.items():
            place_info += f"- {place_name}: {place_data}\n"
        self.info_text.setText(place_info)
