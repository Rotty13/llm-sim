"""
area_subgraph.py - AreaSubgraph class for llm-sim GUI

Contains:
- AreaSubgraph: Manages area nodes within a place and their drawing logic.

LLM Usage: None (UI only)
CLI Args: None
"""

import stat
import numpy as np
from PyQt5.QtGui import QPainter, QPen, QColor
from area_node import AreaNode

class AreaSubgraph:
    def __init__(self, areas=[], edges=[], area_radius_ratio=0.09, place_radius=200):
        self.areas: list[AreaNode] = areas
        self.edges: list[tuple[int, int]] = edges
        self.max_area_depth = 0
        self._area_depths = []
        self.area_radius_ratio = area_radius_ratio
        self.place_radius = place_radius

    @property
    def area_count(self):
        return len(self.areas)

    @staticmethod
    def generate_random_node_tree(area_count, max_children=3, seed=None):
        """
        Generates a random tree structure.
        Return a list of ids and edges.
        """
        import random
        if seed is not None:
            random.seed(seed)
        area_infos = []  # (parent_index, depth)
        area_infos.append((-1, 0))  # root node
        for i in range(1, area_count):
            parent_index = random.randint(0, i - 1)
            parent_depth = area_infos[parent_index][1]
            area_infos.append((parent_index, parent_depth + 1))
        return area_infos
    
    @staticmethod
    def create_test_area_based_on_angles(angles, area_radius_ratio=0.09, place_radius=200):
        """
        Static method to create and return a test AreaSubgraph instance based on given angles.
        """
        area_count = len(angles)
        area_infos = []
        for i in range(area_count):
            if i == 0:
                area_infos.append((-1, 0))  # root
            else:
                area_infos.append((0, 1))  # all children of root
        # Create areas
        areas = []
        edges = []
        for i in range(area_count):
            parent, depth = area_infos[i]
            distance = depth * (place_radius * area_radius_ratio * 1.5)
            area = AreaNode(f"A{i+1}", angles[i], distance)
            areas.append(area)
            if i == 0:
                continue  # Root node has no parent edge
            edges.append((parent, i))
        # Normalize distances
        AreaSubgraph.normalize_distances(areas)
        return AreaSubgraph(areas, edges, area_radius_ratio, place_radius)

    @staticmethod
    def create_test_area_graph(place_radius=200,area_radius_ratio=0.09):
        """
        Static method to create and return a test AreaSubgraph instance.
        """
        area_infos = [
            (-1, 0),  # A1
            (0, 1),   # A2
            (0, 1),   # A3
            (0, 1),   # A4
            (1, 2),   # A5
            (1, 2),   # A6
            (2, 2),   # A7
        ]
        return AreaSubgraph.create_area_graph_from_infos(area_infos, area_radius_ratio=area_radius_ratio, place_radius=place_radius)

    @staticmethod
    def GenerateRandomAreaSubgraph(area_count, area_radius_ratio=0.09, place_radius=200, seed=None):
        """
        Static method to create and return a random AreaSubgraph instance.
        """
        area_infos = AreaSubgraph.generate_random_node_tree(area_count, seed=seed)
        return AreaSubgraph.create_area_graph_from_infos(area_infos, area_radius_ratio, place_radius)

    @staticmethod
    def create_area_graph_from_infos(area_infos, area_radius_ratio=0.09, place_radius=200):
        """
        Static method to build and return an AreaSubgraph from area_infos.
        Combines all logic for node/edge creation, angle assignment, and normalization.
        """
        area_count = len(area_infos)
        area_radius = place_radius * area_radius_ratio

        # Group areas by depth
        from collections import defaultdict
        depth_to_indices = defaultdict(list)
        for idx, (parent, depth) in enumerate(area_infos):
            depth_to_indices[depth].append(idx)


        # Create nodes and edges
        areas = []
        edges = []
        for i in range(area_count):
            parent, depth = area_infos[i]
            distance = depth * (area_radius * 1.5)
            area = AreaNode(f"A{i+1}", 0, distance)
            areas.append(area)
            if i == 0:
                continue  # Root node has no parent edge
            edges.append((parent, i))

        
        

        # Normalize all area distances so the farthest is at 1.0
        AreaSubgraph.normalize_distances(areas)
        area_subgraph = AreaSubgraph(areas, edges, area_radius_ratio, place_radius)
        # Assign angles to nodes based on their depth groups
        area_subgraph.align_area_node_angles()
        return area_subgraph

    @staticmethod
    def depths_from_edges(area_count, edges):
        """
        Compute depths of nodes from edges.
        Returns a list of (parent_index, depth) for each node.
        """
        from collections import defaultdict, deque
        parent_to_children = defaultdict(list)
        for parent, child in edges:
            parent_to_children[parent].append(child)

        depths = [0] * area_count
        queue = deque([(0, 0)])  # (node_index, depth)
        while queue:
            node_idx, depth = queue.popleft()
            depths[node_idx] = depth
            for child in parent_to_children.get(node_idx, []):
                queue.append((child, depth + 1))
        
        area_infos = []
        for i in range(area_count):
            parent = next((p for p, c in edges if c == i), -1)
            area_infos.append((parent, depths[i]))
        return area_infos
    
    
    def align_area_node_angles(self):
        """
        Align area node angles so that each parent's children are distributed evenly around it.
        This method updates the angle of each AreaNode in self.areas.
        """
        # Build parent->children mapping
        parent_to_children = {}
        for idx, (parent, _) in enumerate(AreaSubgraph.depths_from_edges(len(self.areas), self.edges)):
            if parent not in parent_to_children:
                parent_to_children[parent] = []
            parent_to_children[parent].append(idx)

        # Recursive function to assign angles
        def assign_angles_recursively(node_idx, base_angle=0.0, spread=2 * np.pi):
            children = parent_to_children.get(node_idx, [])
            n = len(children)
            if n == 0:
                return
            angle_step = spread / n
            for i, child_idx in enumerate(children):
                #if only one child, align with parent
                if n == 1:
                    angle = base_angle
                else:
                    angle = base_angle - (spread / 2) + (i + 0.5) * angle_step
                self.areas[child_idx].angle = angle
                assign_angles_recursively(child_idx, angle, angle_step)

        # Set root angle and start recursion
        if self.areas:
            self.areas[0].angle = 0.0  # root at 0
            assign_angles_recursively(0, 0.0, 2 * np.pi)
    

    @staticmethod
    def normalize_distances(areas):
        """
        Normalize all area distances so the farthest is at 1.0.
        """
        max_distance = max(area.distance for area in areas) if areas else 1
        for area in areas:
            area.distance = area.distance / max_distance


    def draw(self, painter, x, y, subgraph_radius, area_radius_ratio):
        area_positions = []
        for area in self.areas:
            ax = x + subgraph_radius * area.distance * np.cos(area.angle)
            ay = y + subgraph_radius * area.distance * np.sin(area.angle)
            area_positions.append((ax, ay))
        
        self.draw_edges(painter, area_positions)
        area_radius = subgraph_radius * area_radius_ratio
        #shrink area radius based on max depth to avoid overlap
        area_radius *= (1.0 / (self.max_area_depth + 1))
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
