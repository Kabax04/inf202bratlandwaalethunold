import numpy as np


class Cell():
    """
    Base class representing a single element in a computational mesh.

    This is a general base class. For actual use, instantiate specific subclasses:
    - Line: A 1D cell with 2 points
    - Triangle: A 2D cell with 3 points

    Attributes:
        idx (int): A unique identifier/number for this cell.
        point_ids (list): Indices of the points that form this cell's vertices.
        neighbors (list): Indices of cells that share edges or points with this cell.
                          Populated by calling compute_neighbors().

    Example:
        A Triangle cell might have point_ids=[0, 1, 2], meaning it uses points 0, 1,
        and 2 from a shared point array. If another triangle shares two of these points,
        it will be added to the neighbors list.
    """

    def __init__(self, idx: int, point_ids):
        self.idx = idx
        self.point_ids = list(point_ids)
        self.neighbors = []

    def compute_neighbors(self, cell_list):
        """
        Find and store all neighboring cells that share at least 2 points.

        For Triangle cells, also maps each edge to its neighboring cell index.

        Args:
            cell_list (list): List of all cells to check for neighbors.
        """
        self.neighbors = []

        # Check if this is a Triangle (has edge_to_neighbor attribute)
        is_triangle = hasattr(self, "edge_to_neighbor")

        if is_triangle:
            self.edge_to_neighbor = [None, None, None]

        for cell in cell_list:
            if cell is self:
                continue

            # Find shared points between this cell and neighbor candidate
            shared = set(self.point_ids) & set(cell.point_ids)
            # Only neighbors if they share exactly 2 points (an edge)
            if len(shared) != 2:
                continue

            self.neighbors.append(cell.idx)

            # For Triangle cells, determine which edge is shared
            if not is_triangle or not hasattr(cell, "edge_to_neighbor"):
                continue

            shared = set(shared)

            # Check each of the 3 edges to find which one matches the shared points
            for k in range(3):
                edge_ids = {
                    self.point_ids[k],
                    self.point_ids[(k + 1) % 3]  # Wrap around: edge 2 connects point 2 to point 0
                }
                if edge_ids == shared:
                    self.edge_to_neighbor[k] = cell.idx
                    break

    def __str__(self):
        """Return string representation of the cell."""
        return f"Cell {self.idx}: points={self.point_ids}"


class Line(Cell):
    """
    1D line cell representing a one-dimensional element in a mesh.

    Attributes:
        idx (int): Unique identifier for this line cell.
        point_ids (list): Indices of the 2 points that form the line endpoints.
        neighbors (list): Indices of other cells that share points with this line.

    Example:
        A Line with point_ids=[0, 1] connects points 0 and 1. If another line or cell
        shares point 0 or 1, it will be a neighbor of this line.
    """

    def __str__(self):
        return f"Line {self.idx}: points={self.point_ids}"


class Triangle(Cell):
    """
    2D triangle cell with geometric properties.

    Supports two modes:
    - **Topology-only** (points=None): Stores only vertex indices
    - **Geometry** (points provided): Computes area, centroid, edges, normals

    Args:
        point_ids (list): Indices of 3 vertices.
        idx (int): Unique identifier.
        points (np.ndarray, optional): Global point coordinates. If None, only topology is stored.

    Attributes:
        point_ids (list): The 3 vertex indices.
        edge_to_neighbor (list): Maps each edge (0,1,2) to neighboring cell index.
        x_mid (np.ndarray): Triangle centroid (geometry mode only).
        area (float): Triangle area (geometry mode only).
        edge_points (list): 3 tuples of (start, end) points per edge (geometry mode only).
        normals (np.ndarray): Outward edge normals weighted by edge length (geometry mode only).
        velocity (np.ndarray): Prescribed velocity at centroid (geometry mode only).
        edge_vector (list): Edge vectors [(p2-p1), (p3-p2), (p1-p3)] (geometry mode only).

    Raises:
        ValueError: If point_ids doesn't have exactly 3 points.
        RuntimeError: If geometry properties accessed in topology-only mode.
    """

    def __str__(self):
        return f"Triangle {self.idx}: points={self.point_ids}"

    def __init__(self, point_ids, idx, points=None):
        super().__init__(idx, point_ids)
        if len(point_ids) != 3:  # ensure triangle has 3 points
            raise ValueError("Triangle must have exactly 3 point IDs")

        # --- TOPOLOGY ONLY MODE ---
        if points is None:
            self._points = None
            self._x_mid = None
            self._area = None
            self._edge_points = None
            self._normals = None
            self._velocity = None
            return

        # --- GEOMETRY MODE ---
        self._points = points[self.point_ids, :2]

        self._x_mid = self._compute_midpoint()
        self._area = self._compute_area()
        self._edge_points = self._compute_edge_points()
        self._normals = self._compute_normals()
        self._velocity = self._velocity_field()

        self.edge_to_neighbor = [None, None, None]

    def _compute_midpoint(self):
        """Calculate the centroid (center point) of the triangle."""
        p = self._points
        return np.mean(p[:, :2], axis=0)

    def _compute_area(self):
        """Calculate triangle area using the determinant method."""
        p = self._points
        x1, y1 = p[0][:2]
        x2, y2 = p[1][:2]
        x3, y3 = p[2][:2]
        return abs((x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2)

    def _compute_edge_points(self):
        """Return list of 3 edge tuples: [(p1,p2), (p2,p3), (p3,p1)]."""
        p = self._points[:, :2]
        p1, p2, p3 = p
        return [
            (p1, p2),
            (p2, p3),
            (p3, p1)
        ]

    def _compute_normals(self):
        """
        Calculate outward-pointing normals for each edge, weighted by edge length.
        Returns list of 3 normal vectors.
        """
        normals = []

        for pi, pj in self._edge_points:
            edge = pj - pi
            edge_length = np.linalg.norm(edge)

            # Perpendicular to edge: rotate 90 degrees counterclockwise
            normal = np.array([-edge[1], edge[0]], dtype=float)

            # Check if normal points outward by comparing with direction from edge to centroid
            edge_midpoint = 0.5 * (pi + pj)
            direction = edge_midpoint - self._x_mid

            # Flip normal if it points inward (negative dot product)
            if np.dot(normal, direction) < 0:
                normal = -normal

            # Normalize to unit vector, then weight by edge length
            normal /= np.linalg.norm(normal)

            normals.append(normal*edge_length)

        return normals

    def _velocity_field(self):
        """
        Prescribed ocean velocity field evaluated at cell centroid.
        Returns velocity vector [vx, vy].
        """
        x, y = self._x_mid
        return np.array([y-0.2*x, -x])

    # --- Property getters for geometric attributes ---
    # Raise RuntimeError if accessed in topology-only mode (when points=None)

    @property  # getter for midpoint
    def x_mid(self):
        if self._x_mid is None:
            raise RuntimeError("Triangle has no geometry (points=None)")
        return self._x_mid

    @property  # getter for area
    def area(self):
        if self._area is None:
            raise RuntimeError("Triangle has no geometry (points=None)")
        return self._area

    @property  # getter for edge_points
    def edge_points(self):
        if self._edge_points is None:
            raise RuntimeError("Triangle has no geometry (points=None)")
        return self._edge_points

    @property  # getter for normals
    def normals(self):
        if self._normals is None:
            raise RuntimeError("Triangle has no geometry (points=None)")
        return self._normals

    @property  # getter for midpoint
    def midpoint(self):
        if self._x_mid is None:
            raise RuntimeError("Triangle has no geometry (points=None)")
        return self._x_mid

    @property  # getter for velocity
    def velocity(self):
        if self._velocity is None:
            raise RuntimeError("Triangle has no geometry (points=None)")
        return self._velocity

    @property
    def edge_vector(self):
        """
        Edge vectors for the 3 triangle edges, in the same ordering as edge_points:
        [(p2-p1), (p3-p2), (p1-p3)].
        Computed on-the-fly to avoid storing redundant state.
        """
        # Reuse existing validation in edge_points (will raise if geometry missing)
        return [pj - pi for pi, pj in self.edge_points]
