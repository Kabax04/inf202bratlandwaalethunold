import meshio
from .cells import Line, Triangle


class Mesh:
    def __init__(self, filename: str):
        self.points = None
        self.cells = []
        self._read_mesh(filename)

    def _read_mesh(self, filename: str):

        try:
            msh = meshio.read(filename)
        except Exception as e:
            raise RuntimeError(f"Failed to read mesh file '{filename}': {e}")  # Raise error if reading fails

        self.points = msh.points       # Array of point coordinates
        cell_blocks = msh.cells        # Different types of cells in the mesh

        cell_id = 0                    # Initialize cell ID counter

        for block in cell_blocks:      # Iterate over each cell block
            cellType = block.type
            cellData = block.data

            if cellType == "vertex":   # Skip vertex cells
                continue

            for pts in cellData:       # Iterate over each cell in the block
                if cellType == "line":
                    cell = Line(cell_id, pts)
                elif cellType == "triangle":
                    cell = Triangle(cell_id, pts)
                else:
                    continue

                self.cells.append(cell)
                cell_id += 1
