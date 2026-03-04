# lmao this doesn't do shit

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from shapely.geometry import Polygon, Point

# --------------------------
# 1. Track edges
# --------------------------
left_edge = [(0, 0), (0, 5), (1, 10)]
right_edge = [(5, 0), (5, 5), (6, 10)]

# Create track polygon (finite-end)
track_polygon = Polygon(left_edge + right_edge[::-1])

# --------------------------
# 2. Interior points for triangulation
# --------------------------
interior_points = [(2, 2), (3, 4), (2.5, 6), (3.5, 7)]
points = np.array(left_edge + right_edge + interior_points)

# --------------------------
# 3. Delaunay triangulation
# --------------------------
tri = Delaunay(points)

# Keep only triangles whose centroid is inside the track polygon
valid_triangles = []
for simplex in tri.simplices:
    tri_pts = points[simplex]
    centroid = tri_pts.mean(axis=0)
    if track_polygon.contains(Point(centroid)):
        valid_triangles.append(simplex)
valid_triangles = np.array(valid_triangles)

# --------------------------
# 4. Plot
# --------------------------
plt.figure(figsize=(6, 8))

# Track polygon outline
poly_x, poly_y = track_polygon.exterior.xy
plt.plot(poly_x, poly_y, 'k-', linewidth=2, label='Track Polygon')

# Left and right edges
left_x, left_y = zip(*left_edge)
right_x, right_y = zip(*right_edge)
plt.plot(left_x, left_y, 'g--o', label='Left Edge')
plt.plot(right_x, right_y, 'b--o', label='Right Edge')

# Triangles inside track
for tri_pts_idx in valid_triangles:
    tri_pts = points[tri_pts_idx]
    plt.plot([tri_pts[0,0], tri_pts[1,0]], [tri_pts[0,1], tri_pts[1,1]], 'r-')
    plt.plot([tri_pts[1,0], tri_pts[2,0]], [tri_pts[1,1], tri_pts[2,1]], 'r-')
    plt.plot([tri_pts[2,0], tri_pts[0,0]], [tri_pts[2,1], tri_pts[0,1]], 'r-')

# Plot all points
plt.scatter(points[:,0], points[:,1], color='orange', zorder=5)

plt.gca().set_aspect('equal')
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Finite-End Racing Track CDT")
plt.legend()
plt.show()