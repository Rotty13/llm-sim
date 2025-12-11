"""
visualize_triangle_inequality.py

Visualizes a convex room with 2 entrances, 4 interior objects, and the center.
Checks and displays the triangle inequality for all point triplets using integer distances.

Usage:
    python scripts/visualization/visualize_triangle_inequality.py

Requirements:
    - matplotlib
"""
import matplotlib.pyplot as plt
import itertools
import math

# Example points: 2 entrances, 4 objects, 1 center
points = [
    {"id": "center", "label": "Center", "distance": 0, "angle": 0, "point_type": "center"},
    {"id": "entranceA", "label": "Entrance A", "distance": 5, "angle": 0, "point_type": "entrance"},
    {"id": "entranceB", "label": "Entrance B", "distance": 5, "angle": 120, "point_type": "entrance"},
    {"id": "obj1", "label": "Obj 1", "distance": 3, "angle": 30, "point_type": "interior"},
    {"id": "obj2", "label": "Obj 2", "distance": 4, "angle": 60, "point_type": "interior"},
    {"id": "obj3", "label": "Obj 3", "distance": 2, "angle": 90, "point_type": "interior"},
    {"id": "obj4", "label": "Obj 4", "distance": 4, "angle": 150, "point_type": "interior"},
]

def polar_to_cartesian(distance, angle_deg):
    rad = math.radians(angle_deg)
    return distance * math.cos(rad), distance * math.sin(rad)

# Compute Cartesian coordinates for plotting

# Compute Cartesian coordinates for plotting
for p in points:
    p["x"], p["y"] = polar_to_cartesian(p["distance"], p["angle"])

# Shift all points so that entranceA is at (0, 0) and center is at (0, d(center, entranceA))
entranceA = next(p for p in points if p["id"] == "entranceA")
center = next(p for p in points if p["id"] == "center")
# First, shift so entranceA is at (0,0)
shift_x, shift_y = entranceA["x"], entranceA["y"]
for p in points:
    p["x"] -= shift_x
    p["y"] -= shift_y
# Now, compute new center position (should be on y-axis at (0, d(center, entranceA)))
center_dist = int(round(math.hypot(center["x"], center["y"])))
center_shift_x, center_shift_y = center["x"], center["y"]
# Shift all points so that center moves to (0, center_dist)
for p in points:
    p["x"] -= center_shift_x
    p["y"] -= center_shift_y
    # rotate so that center is on positive y-axis
    # only if center is not already at (0, center_dist)
    if center_dist != 0:
        angle = math.atan2(center_shift_y, center_shift_x)
        cos_a = math.cos(-angle + math.pi/2)
        sin_a = math.sin(-angle + math.pi/2)
        x_new = p["x"] * cos_a - p["y"] * sin_a
        y_new = p["x"] * sin_a + p["y"] * cos_a
        p["x"], p["y"] = x_new, y_new


def float_distance(p1, p2):
    return math.hypot(p1["x"] - p2["x"], p1["y"] - p2["y"])

def check_triangle_inequality(points):
    violations = []
    for a, b, c in itertools.combinations(points, 3):
        d_ab = float_distance(a, b)
        d_bc = float_distance(b, c)
        d_ac = float_distance(a, c)
        if d_ac > d_ab + d_bc + 1e-8:  # small epsilon for floating point tolerance
            violations.append((a["id"], b["id"], c["id"], d_ac, d_ab, d_bc))
    return violations

def plot_points(points):
    colors = {"center": "black", "entrance": "red", "interior": "blue"}
    for p in points:
        plt.scatter(p["x"], p["y"], color=colors[p["point_type"]], s=100, label=p["label"])
        plt.text(p["x"]+0.1, p["y"]+0.1, p["label"])
    plt.gca().set_aspect('equal')
    plt.title("Room Points and Triangle Inequality")
    plt.xlabel("X")
    plt.ylabel("Y")
    # Draw lines between all points
    for a, b in itertools.combinations(points, 2):
        plt.plot([a["x"], b["x"]], [a["y"], b["y"]], color="gray", linestyle=":", linewidth=0.5)
    plt.legend(["Center", "Entrance", "Interior"], loc="upper right")
    # Set symmetric grid bounds
    max_x = max(abs(p["x"]) for p in points)
    max_y = max(abs(p["y"]) for p in points)
    bound_x = max(1, math.ceil(max_x))
    bound_y = max(1, math.ceil(max_y))
    plt.xlim(-bound_x, bound_x)
    plt.ylim(-bound_y, bound_y)
    plt.grid(True)
    plt.show()

def main():
    violations = check_triangle_inequality(points)
    if violations:
        print("Triangle inequality violations:")
        for v in violations:
            print(f"{v[0]}-{v[1]}-{v[2]}: d({v[0]},{v[2]})={v[3]} > d({v[0]},{v[1]})+d({v[1]},{v[2]})={v[4]}+{v[5]}")
    else:
        print("All triangle inequalities satisfied.")
    plot_points(points)

if __name__ == "__main__":
    main()
