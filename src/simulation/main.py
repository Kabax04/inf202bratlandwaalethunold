from .mesh.mesh import Mesh

# TESTING THE MESH READER

mesh = Mesh("bay.msh")

for cell in mesh.cells[:10]:
    print(cell)

mesh.computeNeighbors()
for cell in mesh.cells:
    print(f'Cell {cell.id}: neighbors = {cell.neighbors}')
