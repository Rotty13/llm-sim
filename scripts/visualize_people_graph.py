
import yaml
import networkx as nx
import matplotlib.pyplot as plt
import argparse

def load_city(city_path):
    with open(city_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_personas(personas_path):
    with open(personas_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("people", [])

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="configs/city.yaml")
    parser.add_argument("--personas", default="configs/personas.yaml")
    args = parser.parse_args()
    city_data = load_city(args.city)
    people = load_personas(args.personas)
    G = build_people_graph(city_data, people)
    visualize_people_graph(G, city_data.get("city", "City"))

if __name__ == "__main__":
    main()
