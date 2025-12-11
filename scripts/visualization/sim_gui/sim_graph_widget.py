"""
sim_graph_widget.py - SimGraphWidget for llm-sim GUI

Contains:
- SimGraphWidget: Widget for drawing planar graphs, pan/zoom, and border

LLM Usage: None (UI only)
CLI Args: None
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt
from city_graph import CityGraph
import numpy as np

class SimGraphWidget(QWidget):
    """Widget for drawing planar graphs (nodes and edges), with pan and zoom."""
    def __init__(self, parent=None):
        super().__init__(parent)
        place_names = ["Place 1"]
        self.city_graph = CityGraph(place_names)
        self.zoom = 1.0
        self.logical_center = (0.0, 0.0)
        self.last_mouse_pos = None
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_border(painter)
        self.city_graph.draw(painter, self, self.zoom, self.logical_center)

    def draw_border(self, painter):
        border_pen = QPen(QColor("gray"), 3)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(5, 5, self.width() - 10, self.height() - 10)

    @staticmethod
    def draw_colored_circle_with_text_static(painter, x, y, radius, color, text):
        radius = int(radius)
        max_textsize = 60
        min_textsize = 12
        invisible_threshold = 10
        painter.setBrush(QColor(color))
        painter.setPen(QPen(QColor("black"), 2))
        painter.drawEllipse(int(x) - radius, int(y) - radius, radius * 2, radius * 2)
        font = painter.font()
        fontsize = max(min_textsize, min(max_textsize, int(radius * 0.5)))
        font.setPointSize(fontsize)
        painter.setFont(font)
        if radius < invisible_threshold:
            return
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_x = int(x) - text_width // 2
        text_y = int(y) - int(radius+font.pointSize()/2) + metrics.ascent()
        painter.drawText(text_x, text_y, text)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 0.9
        old_zoom = self.zoom
        # Mouse position in screen coordinates
        # PyQt5 compatibility: event.x(), event.y() always available
        mx, my = event.x(), event.y()
        # Convert mouse position to logical coordinates
        wx = self.logical_center[0] + (mx - self.width() / 2) / self.zoom
        wy = self.logical_center[1] + (my - self.height() / 2) / self.zoom
        # After zoom, recalculate logical center so mouse stays at same world position
        new_zoom = self.zoom * factor
        new_logical_center_x = wx - (mx - self.width() / 2) / new_zoom
        new_logical_center_y = wy - (my - self.height() / 2) / new_zoom
        self.zoom = new_zoom
        self.logical_center = (new_logical_center_x, new_logical_center_y)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            self.logical_center = (
                self.logical_center[0] - dx / self.zoom,
                self.logical_center[1] - dy / self.zoom
            )
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None
