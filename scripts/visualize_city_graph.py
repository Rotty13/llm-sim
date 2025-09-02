import yaml
import networkx as nx
import matplotlib.pyplot as plt
import argparse

# Load city config and visualize connectivity

def load_city(city_path):
    with open(city_path, "r") as f:
        return yaml.safe_load(f)

def build_graph(city_data):
    G = nx.Graph()
    # Add central node for city connectivity
    central_node = city_data.get("central_node", city_data.get("city", "City Center"))
    G.add_node(central_node, type="center")
    # Add places as nodes
    for place in city_data.get("places", []):
        G.add_node(place["name"], type="place", category=place.get("category", "unknown"))
    # Add streets as nodes and connect to central node
    for street in city_data.get("streets", []):
        G.add_node(street, type="street")
        G.add_edge(street, central_node)
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
        elif t == "center":
            node_colors.append("red")
        else:
            node_colors.append("gray")
    plt.figure(figsize=(12,8))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=700, font_size=8, edge_color="#888")
    plt.title(f"City Connectivity Graph: {city_name}")
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="configs/city.yaml")
    args = parser.parse_args()
    city_data = load_city(args.city)
    G = build_graph(city_data)
    visualize_graph(G, city_data.get("city", "City"))

if __name__ == "__main__":
    main()
