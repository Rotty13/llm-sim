"""
world_editor.py - Editor widget for modifying world data in-memory

LLM Usage: None (UI only)
CLI Args: None
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit


class WorldEditor(QWidget):
    """
    Editor for modifying world data in-memory.
    Encompasses the world classes(e.g., World, Place) and allows editing of their attributes.
    
    """
    def __init__(self, world=None, parent=None):
        super().__init__(parent)
        self.world = world
        self.dirty = False
        self.v_layout = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.save_btn = QPushButton("Apply Changes")
        self.save_btn.clicked.connect(self.apply_changes)
        self.v_layout.addWidget(QLabel("Edit World Name:"))
        self.v_layout.addWidget(self.name_edit)
        self.v_layout.addWidget(self.save_btn)
        self.setLayout(self.v_layout)
        if world:
            self.load_world(world)

    def load_world(self, world):
        self.world = world
        self.name_edit.setText(world.get('name', ''))
        self.dirty = False

    def apply_changes(self):
        if not self.world:
            return
        new_name = self.name_edit.text()
        if self.world.get('name', '') != new_name:
            self.world['name'] = new_name
            self.dirty = True
        # Optionally: emit a signal here to notify parent/main window
        self.dirty = True
        # Signal to parent/main window that in-memory state is dirty
