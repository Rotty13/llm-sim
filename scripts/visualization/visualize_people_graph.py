
"""
visualize_people_graph.py

Visualizes relationships between people and places in the city using NetworkX and Matplotlib. Loads city and persona data from YAML and displays connections as a graph.

Usage:
    python scripts/visualization/visualize_people_graph.py city.yaml personas.yaml
"""

from sim.world.world_manager import WorldManager
import networkx as nx
import matplotlib.pyplot as plt
import argparse

def load_city(world_name):
    wm = WorldManager()
    return wm.load_city(world_name)

def load_personas(world_name):
    wm = WorldManager()
    return wm.load_personas(world_name)

def build_people_graph(city_data, people):
    G = nx.Graph()
    # Add places as nodes
    for p in city_data.get("places", []):
        G.add_node(p["name"], type="place", label=p["name"])
    # Add residents as leaf nodes connected to their home
    for person in people:
        name = person.get("name")
        home = person.get("start_place")
        if home and home in G:
            G.add_node(name, type="resident", label=name)
            G.add_edge(name, home, color="#888")
    # Add green edges for work location (direct mapping: resident to work_place)
    for person in people:
        name = person.get("name")
        job = person.get("job")
        work_place = None
        for place in city_data.get("places", []):
            if job and job.lower() in place["name"].lower():
                work_place = place["name"]
                break
        home = person.get("start_place")
        if name and work_place and home != work_place:
            G.add_edge(name, work_place, color="green")
    # Add city connectivity edges
    for conn in city_data.get("connections", []):
        if len(conn) == 2 and conn[0] in G and conn[1] in G:
            G.add_edge(conn[0], conn[1], color="#888")
    return G

def visualize_people_graph(G, city_name):
    pos = nx.spring_layout(G, seed=42)
    node_labels = nx.get_node_attributes(G, 'label')
    # Assign color per node type
    node_colors = []
    for n in G.nodes:
        t = G.nodes[n].get("type", "other")
        if t == "place":
            node_colors.append("skyblue")
        elif t == "resident":
            node_colors.append("lightgreen")
        else:
            node_colors.append("gray")
    # Draw normal edges
    normal_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("color") == "#888"]
    nx.draw_networkx_edges(G, pos, edgelist=normal_edges, edge_color="#888")
    # Draw green work edges
    work_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("color") == "green"]
    nx.draw_networkx_edges(G, pos, edgelist=work_edges, edge_color="green", width=2)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)
    plt.title(f"City People Graph: {city_name}")
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Visualize relationships between people and places in a city world.")
    parser.add_argument("--world", default="World_0", help="World name (folder) to visualize")
    args = parser.parse_args()
    city_data = load_city(args.world)
    people = load_personas(args.world)
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
    G = build_people_graph(city_data if city_data else {"places": [], "connections": []}, people)
    visualize_people_graph(G, city_name)

if __name__ == "__main__":
    main()
