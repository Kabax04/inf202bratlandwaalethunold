"""
test_cells.py

Contains unit tests for the Cell, Line, and Triangle classes in simulation.mesh.cells.

The tests cover:
- Object initialization and default values
- string representations (__str__)
- and neighbor detection logic for Triangle cells.
"""

from src.simulation.mesh.cells import Cell, Line, Triangle


def test_cell_init_sets_fields():
    """
    Verify that cell initialization sets idx, point_ids, and neighbors correctly.

    Expected Behavior:
    - idx is stored as given
    - point_ids starts as an empty list
    """
    c = Cell(idx=7, point_ids=(1, 2, 3))

    assert c.idx == 7
    assert c.point_ids == [1, 2, 3]   # converts to list
    assert c.neighbors == []          # starts empty


def test_cell_str():
    """
    Verify that Cell.__str__ returns the expected string representation.
    """
    c = Cell(idx=1, point_ids=[9, 8])
    assert str(c) == "Cell 1: points=[9, 8]"


def test_line_str():
    """
    Verify that Line.__str__ returns the expected string representation.
    """
    line = Line(idx=2, point_ids=[0, 1])
    assert str(line) == "Line 2: points=[0, 1]"


def test_triangle_str():
    """
    Verify that Triangle.__str__ returns the expected string representation.
    """
    triangle = Triangle(idx=3, point_ids=[1, 2, 3])
    assert str(triangle) == "Triangle 3: points=[1, 2, 3]"


def test_compute_neighbors_finds_one_neighbor_when_two_points_match():
    """
    Verify that compute_neighbors adds a neighbor when exactly two points are shared.

    Two triangle cells are considered neighbors if they share exactly two point indices.
    """
    t1 = Triangle(idx=0, point_ids=[0, 1, 2])
    t2 = Triangle(idx=1, point_ids=[1, 2, 3])   # shares points {1, 2} with t1
    t3 = Triangle(idx=2, point_ids=[4, 5, 6])   # shares no points with t1

    t1.compute_neighbors([t1, t2, t3])

    assert t1.neighbors == [1]


def test_compute_neighbors_adds_multiple_neighbors():
    """
    Verify that compute_neighbors can detect multiple neighbors.

    If multiple triangle cells share exactly two points with the target cell,
    all corresponding indices should be added.
    """
    t1 = Triangle(idx=0, point_ids=[0, 1, 2])
    t2 = Triangle(idx=1, point_ids=[1, 2, 3])   # shares points {1, 2} with t1
    t3 = Triangle(idx=2, point_ids=[0, 2, 4])   # shares points {0, 2} with t1

    t1.compute_neighbors([t1, t2, t3])

    assert set(t1.neighbors) == {1, 2}


def test_compute_neighbors_does_not_add_neighbor_if_only_one_point_matches():
    """
    Verify that compute_neighbors does not add a neighbor if only one point is shared

    Sharing a single point is not sufficient for triangles to be neighbors.
    """
    t1 = Triangle(idx=0, point_ids=[0, 1, 2])
    t2 = Triangle(idx=1, point_ids=[2, 7, 8])  # shares only point 2 with t1

    t1.compute_neighbors([t2])

    assert t1.neighbors == []


def test_compute_neighbors_does_not_add_neighbor_if_three_points_match():
    """
    Verify that compute neighbors does not add a neighbor if all three points match.

    Identical triangles (sharing all three points) should be treated as neighbors
    via the "share exactly two points" rule.
    """
    t1 = Triangle(idx=0, point_ids=[0, 1, 2])
    t2 = Triangle(idx=1, point_ids=[0, 1, 2])  # shares all three points

    t1.compute_neighbors([t2])

    assert t1.neighbors == []


def test_compute_neighbors_does_not_add_self_as_neighbor():
    """
    Verify that a cell does not add itself to its neighbor list..
    """
    t1 = Triangle(idx=0, point_ids=[0, 1, 2])

    t1.compute_neighbors([t1])

    assert t1.neighbors == []
