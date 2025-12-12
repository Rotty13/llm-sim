"""
simulation_controls_panel.py - Panel for simulation control buttons and status
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class SimulationControlsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.status_label = QLabel("Simulation Status: Idle")
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.resume_btn = QPushButton("Resume")
        self.stop_btn = QPushButton("Stop")
        self.step_btn = QPushButton("Step")
        self.speed_btn = QPushButton("Set Speed")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.resume_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.step_btn)
        btn_layout.addWidget(self.speed_btn)
        layout.addWidget(self.status_label)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
