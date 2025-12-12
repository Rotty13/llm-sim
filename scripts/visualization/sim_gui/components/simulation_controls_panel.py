"""
simulation_controls_panel.py - Panel for simulation control buttons and status
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSpinBox, QDoubleSpinBox
from PyQt5.QtCore import Qt

class SimulationControlsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Simulation Status: Idle")
        self.status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Control buttons in a grid
        btn_grid1 = QHBoxLayout()
        self.start_btn = QPushButton("▶ Start")
        self.pause_btn = QPushButton("⏸ Pause")
        self.resume_btn = QPushButton("▶ Resume")
        btn_grid1.addWidget(self.start_btn)
        btn_grid1.addWidget(self.pause_btn)
        btn_grid1.addWidget(self.resume_btn)
        layout.addLayout(btn_grid1)
        
        btn_grid2 = QHBoxLayout()
        self.stop_btn = QPushButton("⏹ Stop")
        self.step_btn = QPushButton("⏭ Step")
        btn_grid2.addWidget(self.stop_btn)
        btn_grid2.addWidget(self.step_btn)
        layout.addLayout(btn_grid2)
        
        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Tick Speed (s):"))
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setMinimum(0.1)
        self.speed_spinbox.setMaximum(10.0)
        self.speed_spinbox.setValue(1.0)
        self.speed_spinbox.setSingleStep(0.1)
        speed_layout.addWidget(self.speed_spinbox)
        layout.addLayout(speed_layout)
        
        # Max ticks control
        ticks_layout = QHBoxLayout()
        ticks_layout.addWidget(QLabel("Max Ticks:"))
        self.max_ticks_spinbox = QSpinBox()
        self.max_ticks_spinbox.setMinimum(0)
        self.max_ticks_spinbox.setMaximum(100000)
        self.max_ticks_spinbox.setValue(1000)
        self.max_ticks_spinbox.setSpecialValueText("Unlimited")
        ticks_layout.addWidget(self.max_ticks_spinbox)
        layout.addLayout(ticks_layout)
        
        self.setLayout(layout)
        
        # Style the buttons
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.pause_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        self.resume_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.stop_btn.setStyleSheet("background-color: #F44336; color: white; font-weight: bold;")
        self.step_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
