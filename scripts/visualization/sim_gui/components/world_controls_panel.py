"""
world_controls_panel.py - Panel for world selection and world-level actions
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QStackedLayout, QHBoxLayout


from PyQt5.QtCore import pyqtSignal

class WorldControlsPanel(QWidget):
    # Signals for world actions and logging
    world_loaded = pyqtSignal(str)
    world_saved = pyqtSignal(str)
    world_closed = pyqtSignal(str)
    log_message = pyqtSignal(str)



    def __init__(self, world_manager, parent=None):
        super().__init__(parent)
        self.world_manager = world_manager

        self.stacked_layout = QStackedLayout()
        self._init_select_state()
        self._init_loaded_state()
        self.setLayout(self.stacked_layout)

        self.set_state_select()

    def _init_select_state(self):
        # State 1: World selection, Load and Delete
        select_widget = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Worlds"))
        self.world_dropdown = QComboBox()
        self.world_dropdown.addItem("Select World")
        self.world_dropdown.addItems(self.world_manager.list_worlds())
        vbox.addWidget(self.world_dropdown)

        btn_row = QHBoxLayout()
        self.load_btn = QPushButton("Load World")
        self.delete_btn = QPushButton("Delete World")
        btn_row.addWidget(self.load_btn)
        btn_row.addWidget(self.delete_btn)
        vbox.addLayout(btn_row)

        select_widget.setLayout(vbox)
        self.stacked_layout.addWidget(select_widget)

        self.load_btn.clicked.connect(self._on_load)
        self.delete_btn.clicked.connect(self._on_delete)

    def _init_loaded_state(self):
        # State 2: Loaded world, readonly name, Save and Close
        loaded_widget = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Loaded World"))
        self.loaded_world_name = QLineEdit()
        self.loaded_world_name.setReadOnly(True)
        vbox.addWidget(self.loaded_world_name)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save World")
        self.close_btn = QPushButton("Close World")
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.close_btn)
        vbox.addLayout(btn_row)

        loaded_widget.setLayout(vbox)
        self.stacked_layout.addWidget(loaded_widget)

        self.save_btn.clicked.connect(self._on_save)
        self.close_btn.clicked.connect(self._on_close)

    def set_state_select(self):
        self.stacked_layout.setCurrentIndex(0)
        self.world_dropdown.setCurrentIndex(0)

    def set_state_loaded(self, world_name):
        self.stacked_layout.setCurrentIndex(1)
        self.loaded_world_name.setText(world_name)

    def _on_load(self):
        idx = self.world_dropdown.currentIndex()
        if idx <= 0:
            self.log_message.emit("No world selected to load.") # type: ignore
            return
        world_name = self.world_dropdown.currentText()
        self.world_loaded.emit(world_name) # type: ignore
        self.set_state_loaded(world_name)

    def _on_delete(self):
        idx = self.world_dropdown.currentIndex()
        if idx <= 0:
            self.log_message.emit("No world selected to delete.") # type: ignore
            return
        world_name = self.world_dropdown.currentText()
        # Emit a log for now; actual deletion logic can be added later
        self.log_message.emit(f"Delete requested for world: {world_name}") # type: ignore

    def _on_save(self):
        world_name = self.loaded_world_name.text()
        if not world_name:
            self.log_message.emit("No world loaded to save.") # type: ignore
            return
        self.world_saved.emit(world_name) # type: ignore

    def _on_close(self):
        world_name = self.loaded_world_name.text()
        if not world_name:
            self.log_message.emit("No world loaded to close.") # type: ignore
            return
        self.world_closed.emit(world_name) # type: ignore
        self.set_state_select()

