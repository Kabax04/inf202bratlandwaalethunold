from .mesh.mesh import Mesh

# TESTING THE MESH READER

mesh = Mesh("bay.msh")

for cell in mesh.cells[:10]:
    print(cell)
