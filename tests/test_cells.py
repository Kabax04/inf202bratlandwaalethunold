from simulation.mesh.cells import Cell, Line, Triangle


def test_cell_init_sets_fields():
    """
    Tests that the Cell constructor correctly initializes the id, point_ids, and neighbors attributes.
    """
    c = Cell(idx=7, point_ids=(1, 2, 3))

    assert c.idx == 7
    assert c.point_ids == [1, 2, 3]   # konverteres til list
    assert c.neighbors == []          # starter tom


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
    triangle = Triangle(cell_id=3, point_ids=[1, 2, 3])
    assert str(triangle) == "Triangle 3: points=[1, 2, 3]"


def test_compute_neighbors_finds_one_neighbor_when_two_points_match():
    """
    Tests that compute_neighbors adds a neighbor when two cells share exactly two points.
    """
    t1 = Triangle(cell_id=0, point_ids=[0, 1, 2])
    t2 = Triangle(cell_id=1, point_ids=[1, 2, 3])   # deler punktene 1 og 2 med t1
    t3 = Triangle(cell_id=2, point_ids=[4, 5, 6])   # deler ingen punkter

    t1.compute_neighbors([t1, t2, t3])

    assert t1.neighbors == [1]


def test_compute_neighbors_adds_multiple_neighbors():
    """
    Tests that compute_neighbors can add multiple neighbors.
    """
    t1 = Triangle(cell_id=0, point_ids=[0, 1, 2])
    t2 = Triangle(cell_id=1, point_ids=[1, 2, 3])   # deler 1 og 2
    t3 = Triangle(cell_id=2, point_ids=[0, 2, 4])   # deler 0 og 2

    t1.compute_neighbors([t1, t2, t3])

    assert set(t1.neighbors) == {1, 2}


def test_compute_neighbors_does_not_add_neighbor_if_only_one_point_matches():
    """
    Tests that compute_neighbors does NOT add a neighbor if only one point is shared.
    """
    t1 = Triangle(cell_id=0, point_ids=[0, 1, 2])
    t2 = Triangle(cell_id=1, point_ids=[2, 7, 8])  # deler bare punkt 2 (1 match)

    t1.compute_neighbors([t2])

    assert t1.neighbors == []


def test_compute_neighbors_does_not_add_neighbor_if_three_points_match():
    """
    Tests that compute_neighbors does NOT add a neighbor if all points match (3 matches).
    """
    t1 = Triangle(cell_id=0, point_ids=[0, 1, 2])
    t2 = Triangle(cell_id=1, point_ids=[0, 1, 2])  # deler 3 punkter

    t1.compute_neighbors([t2])

    assert t1.neighbors == []


def test_compute_neighbors_does_not_add_self_as_neighbor():
    """
    Tests that a cell does not add itself as a neighbor.
    """
    t1 = Triangle(cell_id=0, point_ids=[0, 1, 2])

    t1.compute_neighbors([t1])

    assert t1.neighbors == []
