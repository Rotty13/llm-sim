"""
logs_output_panel.py - Wide, bottom-docked panel for long-form logs/output
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class LogsOutputPanel(QWidget):
    def append_log(self, text):
        self.log_text.append(text)

    def clear_logs(self):
        self.log_text.clear()
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.label = QLabel("Simulation Output / Logs")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(80)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.label)
        layout.addWidget(self.log_text)
        self.setLayout(layout)
