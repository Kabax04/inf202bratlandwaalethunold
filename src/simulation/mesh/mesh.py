import meshio
from .cells import Line, Triangle


class Mesh:
    """
    Container for a computational mesh loaded from a file.

    Reads mesh data from standard formats (e.g., .msh, .vtk) using meshio and creates
    Cell objects (Line, Triangle) to represent the mesh topology and geometry.

    Attributes:
        points (np.ndarray): Array of all point coordinates in the mesh (shape: [n_points, 3]).
        cells (list): List of Cell objects (Line, Triangle) that make up the mesh.

    Example:
        mesh = Mesh("domain.msh")
        mesh.computeNeighbors()  # Find adjacent cells
        print(f"Mesh has {len(mesh.points)} points and {len(mesh.cells)} cells")
    """

    def __init__(self, filename: str):
        self.points = None
        self.cells = []
        self._read_mesh(filename)  # .msh, .vtk, etc.

    def _read_mesh(self, filename: str):
        """
        Read mesh from file and create Cell objects.

        Supports line and triangle cells. Skips vertex cells. Creates Triangle cells
        with geometry information and Line cells with topology only.

        Args:
            filename (str): Path to mesh file.

        Raises:
            RuntimeError: If file cannot be read or parsed.
        """
        try:
            # Read mesh file using meshio library
            msh = meshio.read(filename)
        except Exception as e:
            raise RuntimeError(f"Failed to read mesh file '{filename}': {e}")

        # Extract point coordinates array and cell information blocks
        self.points = msh.points
        cell_blocks = msh.cells

        # Initialize cell ID counter (unique identifier for each cell)
        cell_id = 0

        # Iterate over each block of cells (may contain different cell types)
        for block in cell_blocks:
            cellType = block.type
            cellData = block.data

            # Skip vertex cells (1-node elements with no topology)
            if cellType == "vertex":
                continue

            # Create Cell object for each cell in this block
            for pts in cellData:
                if cellType == "line":
                    # Line: 1D cells with topology only (no geometry needed)
                    cell = Line(cell_id, pts)
                elif cellType == "triangle":
                    # Triangle: 2D cells with full geometry computation
                    cell = Triangle(point_ids=pts, idx=cell_id, points=self.points)
                else:
                    # Skip unsupported cell types
                    continue

                self.cells.append(cell)
                cell_id += 1

    def computeNeighbors(self):
        """
        Identify and store neighboring cells for all cells in the mesh.

        For each cell, finds all adjacent cells that share 2 or more points (edges).
        For Triangle cells, also maps each edge to its neighboring triangle.

        Must be called after mesh initialization before accessing neighbor information.
        """
        for cell in self.cells:
            cell.compute_neighbors(self.cells)
