from abc import ABC, abstractmethod
import numpy as np


class Cell(ABC):
    """
    Base class for mesh cells.
    Abstract because different cell types have different properties.
    """

    def __init__(self, idx: int, point_ids):
        self.idx = idx
        self.point_ids = list(point_ids)
        self.neighbors = []

    def compute_neighbors(self, cell_list):  # finds neighboring cells sharing 2 points
        for cell in cell_list:
            if cell is self:
                continue
            matches = set(self.point_ids) & set(cell.point_ids)
            if len(matches) == 2:
                self.neighbors.append(cell.idx)

    @abstractmethod
    def __str__(self):
        pass


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

    def __init__(self, point_ids, idx, points):  # points is an array of point coordinates
        super().__init__(idx, point_ids)
        self._points = points
        assert len(point_ids) == 3  # ensure triangle has 3 points

        self._x_mid = self._compute_midpoint()
        self._area = self._compute_area()

    def _compute_midpoint(self):  # computes centroid of triangle
        p = self._points[self.point_ids]
        return np.mean(p[:, :2], axis=0)

    def _compute_area(self):  # computes area using determinant method
        p = self._points[self.point_ids]
        x1, y1 = p[0][:2]
        x2, y2 = p[1][:2]
        x3, y3 = p[2][:2]
        return abs((x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2)

    @property  # getter for midpoint
    def x_mid(self):
        return self._x_mid

    @property  # getter for area
    def area(self):
        return self._area
