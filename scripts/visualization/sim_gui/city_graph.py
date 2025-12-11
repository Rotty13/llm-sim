"""
city_graph.py - CityGraph, PlaceNode, AreaSubgraph for llm-sim GUI

Contains:
- CityGraph: Manages the city graph structure and drawing
- PlaceNode: Represents a place in the city
- AreaSubgraph: Manages area nodes within a place

LLM Usage: None (UI only)
CLI Args: None
"""

import stat
import time
import numpy as np
from PyQt5.QtGui import QPainter, QPen, QColor
from area_node import AreaNode
from area_subgraph import AreaSubgraph
from scripts.visualization.sim_gui import area_subgraph


class PlaceNode:
    def __init__(self, name, angle, radius, area_count=5, subgraph_radius_ratio=0.80, area_radius_ratio=0.09, area_subgraph=None, seed=None):
        self.name = name
        self.angle = angle
        self.radius = radius
        self.subgraph_radius_ratio = subgraph_radius_ratio
        self.area_radius_ratio = area_radius_ratio
        self.wx = radius * np.cos(angle)
        self.wy = radius * np.sin(angle)
        self.area_subgraph = area_subgraph if area_subgraph is not None else AreaSubgraph.GenerateRandomAreaSubgraph(area_count, area_radius_ratio, radius, seed)


    def draw(self, painter, x, y, radius):
        color = "white"
        text = self.name
        from sim_graph_widget import SimGraphWidget
        SimGraphWidget.draw_colored_circle_with_text_static(painter, x, y, radius, color, text)
        if radius < 20:
            return
        if self.area_subgraph:
            self.area_subgraph.draw(painter, x, y, radius * self.subgraph_radius_ratio, self.area_subgraph.area_radius_ratio)

    def area_subgraph_visibility_threshold(self, node_radius):
        return node_radius >= 20

    @staticmethod
    def CreateTestPlaceNode():
        name = "Test Place"
        angle = 0.0
        radius = 200
        area_subgraph = AreaSubgraph.create_test_area_graph(200, 0.09)
        """area_subgraph = AreaSubgraph.create_test_area_based_on_angles(
            angles=[0, 0, 0],
            area_radius_ratio=0.09,
            place_radius=200)
        """

        node=PlaceNode(name, angle, radius, area_subgraph=area_subgraph)
        return node

class CityGraph:
    def __init__(self, radius=200):
        self.nodes = []
        self.edges = []
        self.place_names = []
        self.radius = radius

    @staticmethod
    def generate(place_names, radius=200):
        """
        Static method to create and return a new CityGraph instance for the given place_names and radius.
        """
        graph = CityGraph(radius=radius)
        graph.place_names = place_names
        graph.nodes = []
        n = len(place_names)
        angle_step = 2 * np.pi / max(n, 1)
        import random
        time_seed = int(time.time())
        for i, name in enumerate(place_names):
            # salt the seed with time to get different layouts
            random.seed(time_seed + i)
            area_count = random.randint(3, 7)
            node = PlaceNode(name, i * angle_step, radius, area_count=area_count, seed=i)
            graph.nodes.append(node)
        if n > 1:
            graph.edges = [(i, (i+1)%n) for i in range(n)]
        else:
            graph.edges = []
        return graph
    
    @staticmethod
    def TestSinglePlace():
        place_names = ["Test Place"]
        # Create a CityGraph with a single test place
        graph = CityGraph(radius=200)
        node = PlaceNode.CreateTestPlaceNode()
        graph.nodes.append(node)
        graph.edges = []
        return graph 

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
