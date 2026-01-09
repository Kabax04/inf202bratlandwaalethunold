"""
test_cells.py

Contains unit tests for the Cell, Line, and Triangle classes in simulation.mesh.cells.
"""

from simulation.mesh.cells import Cell, Line, Triangle


def test_cell_init_sets_fields():
    """
    Tests that the Cell constructor correctly initializes the id, point_ids, and neighbors attributes.
    """
    c = Cell(idx=7, point_ids=(1, 2, 3))

    assert c.id == 7
    assert c.point_ids == [1, 2, 3]   # converts to list
    assert c.neighbors == []          # starts empty


def test_cell_str():
    """
    Tests that the Cell __str__ method returns the expected string representation.
    """
    c = Cell(idx=1, point_ids=[9, 8])
    assert str(c) == "Cell 1: points=[9, 8]"


def test_line_str():
    """
    Tests that the Line __str__ method returns the expected string representation.
    """
    line = Line(idx=2, point_ids=[0, 1])
    assert str(line) == "Line 2: points=[0, 1]"


def test_triangle_str():
    """
    Tests that the Triangle __str__ method returns the expected string representation.
    """
    triangle = Triangle(idx=3, point_ids=[1, 2, 3])
    assert str(triangle) == "Triangle 3: points=[1, 2, 3]"


def test_compute_neighbors_finds_one_neighbor_when_two_points_match():
    """
    Tests that compute_neighbors adds a neighbor when two cells share exactly two points.
    """
    t1 = Triangle(idx=0, point_ids=[0, 1, 2])
    t2 = Triangle(idx=1, point_ids=[1, 2, 3])   # shares points 1 and 2
    t3 = Triangle(idx=2, point_ids=[4, 5, 6])   # shares no points

    t1.compute_neighbors([t1, t2, t3])

    assert t1.neighbors == [1]


def test_compute_neighbors_adds_multiple_neighbors():
    """
    Tests that compute_neighbors can add multiple neighbors.
    """
    t1 = Triangle(idx=0, point_ids=[0, 1, 2])
    t2 = Triangle(idx=1, point_ids=[1, 2, 3])   # shares 1 and 2
    t3 = Triangle(idx=2, point_ids=[0, 2, 4])   # shares 1 and 2

    t1.compute_neighbors([t1, t2, t3])

    assert set(t1.neighbors) == {1, 2}


def test_compute_neighbors_does_not_add_neighbor_if_only_one_point_matches():
    """
    Tests that compute_neighbors does NOT add a neighbor if only one point is shared.
    """
    t1 = Triangle(idx=0, point_ids=[0, 1, 2])
    t2 = Triangle(idx=1, point_ids=[2, 7, 8])  # shares only point 2 (1 match)

    t1.compute_neighbors([t2])

    assert t1.neighbors == []


def test_compute_neighbors_does_not_add_neighbor_if_three_points_match():
    """
    Tests that compute_neighbors does NOT add a neighbor if all points match (3 matches).
    """
    t1 = Triangle(idx=0, point_ids=[0, 1, 2])
    t2 = Triangle(idx=1, point_ids=[0, 1, 2])  # shares 3 points

    t1.compute_neighbors([t2])

    assert t1.neighbors == []


def test_compute_neighbors_does_not_add_self_as_neighbor():
    """
    Tests that a cell does not add itself as a neighbor.
    """
    t1 = Triangle(idx=0, point_ids=[0, 1, 2])

    t1.compute_neighbors([t1])

    assert t1.neighbors == []
