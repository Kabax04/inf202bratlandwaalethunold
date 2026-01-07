class Cell:
    """
    Base class for mesh cells.
    """

    def __init__(self, cell_id: int, point_ids):
        self.id = cell_id
        self.point_ids = list(point_ids)
        self.neighbors = []

    def compute_neighbors(self, cell_list):
        for cell in cell_list:
            matches = set(self.point_ids) & set(cell.point_ids)
            if len(matches) == 2:
                self.neighbors.append(cell.id)

    def __str__(self):
        return f"Cell {self.id}: points={self.point_ids}"


class Line(Cell):
    """
    1D line cell.
    """

    def __str__(self):
        return f"Line {self.id}: points={self.point_ids}"


class Triangle(Cell):
    """
    2D triangle cell.
    """

    def __str__(self):
        return f"Triangle {self.id}: points={self.point_ids}"
