"""
city_graph.py - CityGraph, PlaceNode, AreaSubgraph for llm-sim GUI

Contains:
- CityGraph: Manages the city graph structure and drawing
- PlaceNode: Represents a place in the city
- AreaSubgraph: Manages area nodes within a place

LLM Usage: None (UI only)
CLI Args: None
"""

import numpy as np
from PyQt5.QtGui import QPainter, QPen, QColor
from area_node import AreaNode

class AreaSubgraph:
    def __init__(self, area_count, area_radius_ratio, place_radius, seed=None):
        area_radius = place_radius * area_radius_ratio
        area_angle_step = 2 * np.pi / area_count
        import random
        if seed is not None:
            random.seed(seed)
        self.areas = []
        self.edges = []
        self._area_depths = [0]
        for i in range(area_count):
            parent = random.randint(0, i-1) if i > 0 else None
            depth = self._area_depths[parent] + 1 if parent is not None else 0
            distance = depth * (area_radius * 1.5)
            area = AreaNode(f"A{i+1}", i * area_angle_step, distance)
            self._area_depths.append(depth)
            self.areas.append(area)
            if i == 0:
                continue
            self.edges.append((parent, i))
        max_distance = max(area.distance for area in self.areas) if self.areas else 1
        for area in self.areas:
            area.distance = area.distance / max_distance
        self.max_area_depth = max(self._area_depths) if self._area_depths else 1

    def draw(self, painter, x, y, radius):
        area_positions = []
        for area in self.areas:
            ax = x + radius * area.distance * np.cos(area.angle)
            ay = y + radius * area.distance * np.sin(area.angle)
            area_positions.append((ax, ay))
        area_radius = radius * 0.1
        self.draw_edges(painter, area_positions)
        self.draw_nodes(painter, area_positions, area_radius)

    def draw_edges(self, painter, area_positions):
        painter.setPen(QPen(QColor("blue"), 1))
        for i, j in self.edges:
            a1 = area_positions[i]
            a2 = area_positions[j]
            painter.drawLine(int(a1[0]), int(a1[1]), int(a2[0]), int(a2[1]))

    def draw_nodes(self, painter, area_positions, area_radius):
        for aidx, (ax, ay) in enumerate(area_positions):
            self.areas[aidx].draw(painter, ax, ay, area_radius)

class PlaceNode:
    def __init__(self, name, angle, radius, area_count=5, area_radius_ratio=0.09, seed=None):
        self.name = name
        self.angle = angle
        self.radius = radius
        self.wx = radius * np.cos(angle)
        self.wy = radius * np.sin(angle)
        self.area_subgraph = AreaSubgraph(area_count, area_radius_ratio, radius, seed)

    def draw(self, painter, x, y, radius):
        color = "white"
        text = self.name
        from sim_graph_widget import SimGraphWidget
        SimGraphWidget.draw_colored_circle_with_text_static(painter, x, y, radius, color, text)
        if radius < 20:
            return
        self.area_subgraph.draw(painter, x, y, radius * 0.70)

    def area_subgraph_visibility_threshold(self, node_radius):
        return node_radius >= 20

class CityGraph:
    def __init__(self, place_names, radius=200):
        self.nodes = []
        n = len(place_names)
        angle_step = 2 * np.pi / max(n, 1)
        import random
        for i, name in enumerate(place_names):
            random.seed(i)
            area_count = random.randint(3, 7)
            node = PlaceNode(name, i * angle_step, radius, area_count=area_count, seed=i)
            self.nodes.append(node)
        if n > 1:
            self.edges = [(i, (i+1)%n) for i in range(n)]
        else:
            self.edges = []

    def draw(self, painter, widget, zoom, logical_center):
        positions = []
        for node in self.nodes:
            sx = widget.width() / 2 + (node.wx - logical_center[0]) * zoom
            sy = widget.height() / 2 + (node.wy - logical_center[1]) * zoom
            positions.append((sx, sy))
        painter.setPen(QPen(QColor("black"), 2))
        for i, j in self.edges:
            p1 = positions[i]
            p2 = positions[j]
            painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
        node_radius = 50 * zoom
        for idx, (x, y) in enumerate(positions):
            node = self.nodes[idx]
            node.draw(painter, x, y, node_radius)
