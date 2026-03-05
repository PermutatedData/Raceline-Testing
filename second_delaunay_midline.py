EPS = 1e-9

    
class Triangle:

    def __init__(self, a, b, c):
        self.v = [a,b,c]

    def edge(self,i):
        return (self.v[i], self.v[(i+1)%3])

    def edges(self):
        return [
            (self.v[0],self.v[1]),
            (self.v[1],self.v[2]),
            (self.v[2],self.v[0])
        ]
        

def is_triangle_edge(t, edge):
    """
    Checks if edge is an edge of the triangle
    Operation: checks if edge or reversed edge is in triangle edges

    Args:
        t (Triangle): triangle
        edge (list): list of two points
    """
    
    return edge in t.edges or edge[::-1] in t.edges


# ---------------------------------------------------------
# Geometry
# ---------------------------------------------------------

def orient(a, b, c):
    """ 
    Calculates |AB x AC|

    Args:
        a (list): x, y pair
        b (list): x, y pair
        c (list): x, y pair

    Returns:
        int: |AB x AC|. Positive if CCW, negative if CW
    """
    
    # For my own sake: AB = b - a, AC = c - a
    # Then, 2D cross product formula
    
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def in_circumcircle(a, b, c, point):
    """
    Calculates determinant of matrix to check if point is in triangle's circumcircle
    Big-brain technique. For explanation, see: https://ianthehenry.com/posts/delaunay/
    Assumes points are put counterclockwise

    Args:
        a (list): triangle x, y pair
        b (list): triangle x, y pair
        c (list): triangle x, y pair
        point (list): x, y pair

    Returns:
        bool: whether or not point is in circumcircle
    """
    ax, ay = a[0] - point[0], a[1] - point[1]
    bx, by = b[0] - point[0], b[1] - point[1]
    cx, cy = c[0] - point[0], c[1] - point[1]

    det = (
        (ax*ax + ay*ay)*(bx*cy - by*cx)
        - (bx*bx + by*by)*(ax*cy - ay*cx)
        + (cx*cx + cy*cy)*(ax*by - ay*bx)
    )
    return det > 0


def segments_intersect(p1, p2, p3, p4):
    """
    Another bit of comp geometry magic
    
    Args:
        p1 (list): segment 1 endpoint
        p2 (list): segment 1 endpoint
        p3 (list): segment 2 endpoint
        p4 (list): segment 2 endpoint
    """
    o1 = orient(p1,p2,p3)
    o2 = orient(p1,p2,p4)
    o3 = orient(p3,p4,p1)
    o4 = orient(p3,p4,p2)
    return o1*o2 < 0 and o3*o4 < 0


# ---------------------------------------------------------
# Polygon utilities
# ---------------------------------------------------------

def polygon_area(poly):
    area = 0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        area += x1*y2 - x2*y1
    return area/2


def ensure_ccw(poly):
    if polygon_area(poly) < 0:
        return poly[::-1]
    return poly


# ---------------------------------------------------------
# Super triangle
# ---------------------------------------------------------

def super_triangle(points):

    minx = min(p[0] for p in points)
    miny = min(p[1] for p in points)
    maxx = max(p[0] for p in points)
    maxy = max(p[1] for p in points)

    dx = maxx - minx
    dy = maxy - miny
    d = max(dx, dy) * 10

    midx = (minx + maxx) / 2
    midy = (miny + maxy) / 2

    return [
        (midx - d,midy - d),
        (midx, midy + d),
        (midx + d,midy - d)
    ]


# ---------------------------------------------------------
# Delaunay triangulation (Bowyer-Watson)
# ---------------------------------------------------------

def delaunay(points):

    st = super_triangle(points)

    triangles=[Triangle(st[0],st[1],st[2])]

    for p in points:

        bad=[]

        for t in triangles:
            a,b,c = t.v
            if in_circumcircle(a,b,c,p):
                bad.append(t)

        boundary=[]

        for t in bad:
            for e in t.edges():

                shared = False

                for ot in bad:
                    if ot == t:
                        continue

                    # Since for triangle edges, order matters. Note to self: fix this?
                    if is_triangle_edge(ot, e):
                        shared=True
                        break

                if not shared:
                    boundary.append(e)

        for t in bad:
            triangles.remove(t)

        for e in boundary:
            triangles.append(Triangle(e[0],e[1],p))

    triangles = [t for t in triangles if not any(v in st for v in t.v)]

    return triangles


# ---------------------------------------------------------
# Edge utilities
# ---------------------------------------------------------

def edge_exists(triangles, a, b):

    for t in triangles:
        for e in t.edges():
            if (e[0] == a and e[1] == b) or (e[0] == b and e[1] == a):
                return True

    return False


def flip_edge(triangles,edge):

    t1=None
    t2=None

    for t in triangles:
        for e in t.edges():
            if e==edge or e==edge[::-1]:
                if t1 is None:
                    t1=t
                else:
                    t2=t
                    break

    if not t1 or not t2:
        return

    a,b=edge

    c=next(v for v in t1.v if v not in edge)
    d=next(v for v in t2.v if v not in edge)

    triangles.remove(t1)
    triangles.remove(t2)

    triangles.append(Triangle(c,d,a))
    triangles.append(Triangle(c,d,b))


# ---------------------------------------------------------
# Constraint enforcement
# ---------------------------------------------------------

def enforce_constraints(triangles,constraints):

    changed=True

    while changed:

        changed=False

        for a,b in constraints:

            if edge_exists(triangles,a,b):
                continue

            for t in triangles:

                for e in t.edges():

                    if segments_intersect(a,b,e[0],e[1]):

                        flip_edge(triangles,e)
                        changed=True
                        break

                if changed:
                    break

    return triangles


# ---------------------------------------------------------
# Build FSAE CDT
# ---------------------------------------------------------

def build_fsae_cdt(left_sorted, right_sorted):
    polygon = left_sorted + right_sorted[::-1] # LIST CONCATENATION???? WTF
    polygon = ensure_ccw(polygon)

    constraints=[]

    for i in range(len(polygon)):
        constraints.append(
            (polygon[i],polygon[(i+1)%len(polygon)])
        )

    tris = delaunay(polygon)
    tris = enforce_constraints(tris,constraints)

    return tris, left_sorted, right_sorted


# ---------------------------------------------------------
# Centerline extraction
# ---------------------------------------------------------

def extract_centerline(triangles,left_set,right_set):

    centers=[]

    for t in triangles:

        for a,b in t.edges():

            if (a in left_set and b in right_set) or \
               (b in left_set and a in right_set):

                centers.append(
                    ((a[0]+b[0])/2,(a[1]+b[1])/2)
                )

    return centers


# ---------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------

def fsae_raceline(left_cones_sorted: list, right_cones_sorted: list):
    """
    Constructs midline with Delaunay

    Args:
        left_cones_sorted (list): sorted list of left cone coordinates
        right_cones_sorted (list): sorted list of right cone coordinates

    Returns:
        list: centerline
    """
    tris,left,right = build_fsae_cdt(left_cones_sorted, right_cones_sorted)

    # do sets really do anything here
    centerline = extract_centerline(tris, left, right)

    return centerline