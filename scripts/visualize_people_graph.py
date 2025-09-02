import yaml
import networkx as nx
import matplotlib.pyplot as plt
import argparse

def load_personas(personas_path):
    with open(personas_path, "r") as f:
        return yaml.safe_load(f).get("people", [])

def build_people_graph(people):
    G = nx.Graph()
    # Add nodes for people, residences, and workplaces
    for person in people:
        name = person.get("name")
        residence = person.get("address", f"Residence of {name}")
        workplace = person.get("job", None)
        start_place = person.get("start_place", None)
        # Add person node
        G.add_node(name, type="person")
        # Add residence node
        G.add_node(residence, type="residence")
        G.add_edge(name, residence, relation="lives_at")
        # Add workplace node (use start_place if available, else job)
        if start_place:
            G.add_node(start_place, type="workplace")
            G.add_edge(name, start_place, relation="works_at")
        elif workplace:
            G.add_node(workplace, type="workplace")
            G.add_edge(name, workplace, relation="works_at")
    return G

def visualize_people_graph(G, title):
    pos = nx.spring_layout(G, seed=42)
    node_colors = []
    for n in G.nodes:
        t = G.nodes[n].get("type", "other")
        if t == "person":
            node_colors.append("skyblue")
        elif t == "residence":
            node_colors.append("lightgreen")
        elif t == "workplace":
            node_colors.append("orange")
        else:
            node_colors.append("gray")
    plt.figure(figsize=(14,10))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=800, font_size=9, edge_color="#888")
    plt.title(title)
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--personas", default="configs/personas.yaml")
    parser.add_argument("--title", default="People-Oriented City Graph")
    args = parser.parse_args()
    people = load_personas(args.personas)
    G = build_people_graph(people)
    visualize_people_graph(G, args.title)

if __name__ == "__main__":
    main()
