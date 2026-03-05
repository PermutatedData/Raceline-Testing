from helpers import *

t = Triangle([0, 0], [-1, 1], [1, 1])

print(t.edges())
print(is_triangle_CCW(t))

# t = Triangle([0, 0], [-1, 0], [1, 0]) # Degeneracy works