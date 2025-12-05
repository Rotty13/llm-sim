"""
visualize_city_graph.py

Visualizes the city structure as a graph using NetworkX and Matplotlib. Loads city configuration from YAML and displays places, streets, and houses as nodes and edges.

Usage:
    python scripts/visualization/visualize_city_graph.py city.yaml
"""
from sim.world.world_manager import WorldManager
import networkx as nx
import matplotlib.pyplot as plt
import argparse

# Load city config and visualize connectivity

def load_city(world_name):
    wm = WorldManager()
    return wm.load_city(world_name)

def build_graph(city_data):
    G = nx.Graph()
    # Only add places and streets, no central node
    for place in city_data.get("places", []):
        G.add_node(place["name"], type="place", category=place.get("category", "unknown"))
    for street in city_data.get("streets", []):
        G.add_node(street, type="street")
    # Add houses as nodes, connect to street and start_place
    for house in city_data.get("houses", []):
        addr = house["address"]
        street = house["street"]
        start_place = house["person_ref"].get("start_place")
        G.add_node(addr, type="house", owner=house["owner"])
        G.add_edge(addr, street)
        if start_place and start_place in G:
            G.add_edge(addr, start_place)
    # Optionally connect places to streets if names match
    for place in city_data.get("places", []):
        for street in city_data.get("streets", []):
            if street.lower() in place["name"].lower():
                G.add_edge(place["name"], street)

    # Add edges from connections field (ensure city graph connectivity)
    for conn in city_data.get("connections", []):
        if len(conn) == 2 and conn[0] in G and conn[1] in G:
            G.add_edge(conn[0], conn[1])
    return G

def visualize_graph(G, city_name):
    pos = nx.spring_layout(G, seed=42)
    node_colors = []
    for n in G.nodes:
        t = G.nodes[n].get("type", "other")
        if t == "place":
            node_colors.append("skyblue")
        elif t == "street":
            node_colors.append("orange")
        elif t == "house":
            node_colors.append("lightgreen")
        else:
            node_colors.append("gray")
    plt.figure(figsize=(12,8))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=700, font_size=8, edge_color="#888")
    plt.title(f"City Connectivity Graph: {city_name}")
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", default="World_0")
    args = parser.parse_args()
    city_data = load_city(args.world)
    if city_data:
        if "name" in city_data:
            city_name = city_data["name"]
        elif isinstance(city_data.get("city"), str):
            city_name = city_data["city"]
        elif isinstance(city_data.get("city"), dict):
            city_name = city_data["city"].get("name", "City")
        else:
            city_name = "City"
    else:
        city_name = "City"
    G = build_graph(city_data if city_data else {"places": [], "streets": [], "houses": [], "connections": []})
    visualize_graph(G, city_name)

if __name__ == "__main__":
    main()
