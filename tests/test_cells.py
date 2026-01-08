"""
test_cells.py

Contains unit tests for the Line and Triangle classes in simulation.mesh.cells.
"""

import numpy as np
import pytest

from simulation.mesh.cells import Line, Triangle, Cell

# Sample points array for use in tests
POINTS = np.array([
    [0.0, 0.0, 0.0],  # 0
    [1.0, 0.0, 0.0],  # 1
    [0.0, 1.0, 0.0],  # 2
    [1.0, 1.0, 0.0],  # 3
    [2.0, 0.0, 0.0],  # 4
    [0.0, 2.0, 0.0],  # 5
    [2.0, 2.0, 0.0],  # 6
    [3.0, 3.0, 0.0],  # 7
    [4.0, 4.0, 0.0],  # 8
])


def test_line_str():
    line = Line(idx=2, point_ids=[0, 1])
    assert str(line) == "Line 2: points=[0, 1]"


def test_triangle_str():
    triangle = Triangle(point_ids=[1, 2, 3], idx=3, points=POINTS)
    assert str(triangle) == "Triangle 3: points=[1, 2, 3]"


def test_triangle_midpoint_and_area():
    points = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ])

    t = Triangle(point_ids=[0, 1, 2], idx=0, points=points)

    assert np.allclose(t.x_mid, [1/3, 1/3])
    assert t.area == 0.5


def test_triangle_asserts_three_points():
    with pytest.raises(AssertionError):
        Triangle(point_ids=[0, 1], idx=0, points=POINTS)


def test_compute_neighbors_finds_one_neighbor_when_two_points_match():
    t1 = Triangle(point_ids=[0, 1, 2], idx=0, points=POINTS)
    t2 = Triangle(point_ids=[1, 2, 3], idx=1, points=POINTS)
    t3 = Triangle(point_ids=[4, 5, 6], idx=2, points=POINTS)

    t1.compute_neighbors([t1, t2, t3])
    assert t1.neighbors == [1]


def test_compute_neighbors_adds_multiple_neighbors():
    t1 = Triangle(point_ids=[0, 1, 2], idx=0, points=POINTS)
    t2 = Triangle(point_ids=[1, 2, 3], idx=1, points=POINTS)
    t3 = Triangle(point_ids=[0, 2, 4], idx=2, points=POINTS)

    t1.compute_neighbors([t1, t2, t3])
    assert set(t1.neighbors) == {1, 2}


def test_compute_neighbors_does_not_add_neighbor_if_only_one_point_matches():
    t1 = Triangle(point_ids=[0, 1, 2], idx=0, points=POINTS)
    t2 = Triangle(point_ids=[2, 7, 8], idx=1, points=POINTS)

    t1.compute_neighbors([t2])
    assert t1.neighbors == []


def test_compute_neighbors_does_not_add_neighbor_if_three_points_match():
    t1 = Triangle(point_ids=[0, 1, 2], idx=0, points=POINTS)
    t2 = Triangle(point_ids=[0, 1, 2], idx=1, points=POINTS)

    t1.compute_neighbors([t2])
    assert t1.neighbors == []


def test_compute_neighbors_does_not_add_self_as_neighbor():
    t1 = Triangle(point_ids=[0, 1, 2], idx=0, points=POINTS)

    t1.compute_neighbors([t1])
    assert t1.neighbors == []


def test_cell_abstract_str_pass_is_covered():
    class ConcreteCell(Cell):
        def __str__(self):
            return "ok"

    c = ConcreteCell(idx=0, point_ids=[1, 2])

    assert str(c) == "ok"

    assert Cell.__str__(c) is None
