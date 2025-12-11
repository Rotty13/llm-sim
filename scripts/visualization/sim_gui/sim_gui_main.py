"""
sim_gui_main.py - Main window and entry point for llm-sim GUI

Contains:
- SimMainWindow: Main application window
- main(): Application entry point

LLM Usage: None (UI only)
CLI Args: None
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QComboBox, QLabel, QSplitter
from scripts.visualization.sim_gui.sim_graph_widget import SimGraphWidget

class SimMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("llm-sim GUI")
        self.resize(1600, 860)
        self._init_ui()

    def _init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        self.agent_list = QListWidget()
        self.agent_list.addItems(["Agent A", "Agent B", "Agent C"])
        self.agent_dropdown = QComboBox()
        self.agent_dropdown.addItems(["All Agents", "Agent A", "Agent B", "Agent C"])
        left_panel.addWidget(QLabel("Agents"))
        left_panel.addWidget(self.agent_list)
        left_panel.addWidget(QLabel("Search/Select Agent"))
        left_panel.addWidget(self.agent_dropdown)
        self.graph_widget = SimGraphWidget()
        splitter = QSplitter()
        left_container = QWidget()
        left_container.setLayout(left_panel)
        splitter.addWidget(left_container)
        splitter.addWidget(self.graph_widget)
        splitter.setSizes([200, 600])
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

def main():
    app = QApplication(sys.argv)
    window = SimMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
