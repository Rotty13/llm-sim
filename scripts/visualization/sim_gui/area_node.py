"""
area_node.py - AreaNode class for llm-sim GUI

Contains:
- AreaNode: Represents an area within a place node, with drawing logic.

LLM Usage: None (UI only)
CLI Args: None
"""

from PyQt5.QtGui import QPainter

class AreaNode:
    def __init__(self, name, angle, distance):
        self.name = name
        #radians
        self.angle = angle  # angle from place center
        self.distance = distance  # distance from place center
        self.depth = 0  # depth in area hierarchy, not used directly in rendering

    def draw(self, painter: QPainter, x, y, radius):
        color = "#e0f7fa"
        text = self.name
        # Import here to avoid circular imports if needed
        from sim_graph_widget import SimGraphWidget
        SimGraphWidget.draw_colored_circle_with_text_static(painter, x, y, radius, color, text)
