import numpy

def sort_points_nearest(points):
    """
    Nearest neighbor walk

    Parameters
    ----------
    points : (x, y) Numpy array

    Returns
    -------
    sorted points : (x, y) Numpy array
    """

    points = points.tolist()
    
    # Not a fan of lambda, but ok
    # Looks for smallest x. If tie, then smallest y. Used for geometrical algorithms, but it might be best to use nearest distance like FASTTUBE does
    start = min(points, key=lambda p: (p[0], p[1]))
    
    ordered = [start]
    points.remove(start)
    
    current = start

    while points:
        next_pt = min(points, key=lambda p: (p[0]-current[0])**2 + (p[1]-current[1])**2)
        ordered.append(next_pt)
        points.remove(next_pt)
        current = next_pt

    return numpy.array(ordered)