import numpy as np


class Cell():
    """
    Base class for mesh cells.
    Abstract because different cell types have different properties.
    """

    def __init__(self, idx: int, point_ids):
        self.idx = idx
        self.point_ids = list(point_ids)
        self.neighbors = []

    def compute_neighbors(self, cell_list):
        self.neighbors = []

        is_triangle = hasattr(self, "edge_to_neighbor")

        if is_triangle:
            self.edge_to_neighbor = [None, None, None]

        for cell in cell_list:
            if cell is self:
                continue

            shared = set(self.point_ids) & set(cell.point_ids)
            if len(shared) != 2:
                continue

            self.neighbors.append(cell.idx)

            if not is_triangle or not hasattr(cell, "edge_to_neighbor"):
                continue

            shared = set(shared)

            for k in range(3):
                edge_ids = {
                    self.point_ids[k],
                    self.point_ids[(k + 1) % 3]
                }
                if edge_ids == shared:
                    self.edge_to_neighbor[k] = cell.idx
                    break

    def __str__(self):
        return f"Cell {self.idx}: points={self.point_ids}"


class Line(Cell):
    """
    1D line cell.
    """

    def __str__(self):
        return f"Line {self.idx}: points={self.point_ids}"


class Triangle(Cell):
    """
    2D triangle cell.
    Computes midpoint and area upon initialization.
    """

    def __str__(self):
        return f"Triangle {self.idx}: points={self.point_ids}"

    def __init__(self, point_ids, idx, points=None):  # points is an array of point coordinates
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
        self._points = points[self.point_ids, :2]  # shape (3, 2)

        self._x_mid = self._compute_midpoint()
        self._area = self._compute_area()
        self._edge_points = self._compute_edge_points()
        self._normals = self._compute_normals()
        self._velocity = self._velocity_field()

        self.edge_to_neighbor = [None, None, None]

    def _compute_midpoint(self):  # computes centroid of triangle
        p = self._points
        return np.mean(p[:, :2], axis=0)

    def _compute_area(self):  # computes area using determinant method
        p = self._points
        x1, y1 = p[0][:2]
        x2, y2 = p[1][:2]
        x3, y3 = p[2][:2]
        return abs((x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2)

    def _compute_edge_points(self):
        p = self._points[:, :2]
        p1, p2, p3 = p
        return [
            (p1, p2),
            (p2, p3),
            (p3, p1)
        ]

    def _compute_normals(self):
        normals = []

        for pi, pj in self._edge_points:
            edge = pj - pi
            edge_length = np.linalg.norm(edge)

            normal = np.array([-edge[1], edge[0]], dtype=float)

            edge_midpoint = 0.5 * (pi + pj)
            direction = edge_midpoint - self._x_mid

            if np.dot(normal, direction) < 0:
                normal = -normal

            normal /= np.linalg.norm(normal)

            normals.append(normal*edge_length)

        return normals

    def _velocity_field(self):
        """
        Prescribed ocean velocity field.
        Evaluated at cell centroid.
        """
        x, y = self._x_mid
        return np.array([y-0.2*x, -x])

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
