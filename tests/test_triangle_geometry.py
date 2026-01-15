"""
Unit tests for the Triangle cell.

These tests verify geometric properties of Triangle:
- midpoint location
- area computation
- edge point extraction and edge vector lengths
- normal vector count, length, orientation and orthogonality
- correct error handling when Triangle is constructed with invalid input.
"""

import numpy as np
import pytest
from src.simulation.mesh.cells import Triangle


@pytest.fixture
def simple_triangle():
    """
    Provide a simple right triangle for geometric unit tests.

    The triangle is defined by the points:
    (0,0), (1,0), (0,1) in the xy-plane, which gives:
    - area = 0.5,
    - centroid = (1/3, 1/3)
    - edge lengths = 1.0, 1.0, sqrt(2)

    Returns:
    Triangle: Triangle instance with points set and idx=0.
    """

    points = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ])
    point_ids = [0, 1, 2]
    return Triangle(point_ids=point_ids, idx=0, points=points)


def test_triangle_midpoint(simple_triangle):
    """
    Verify that the triangle midpoint is correctly computed.

    For vertices at (0,0), (1,0), (0,1), the centroid should be at (1/3, 1/3).
    """
    expected = np.array([1/3, 1/3])
    np.testing.assert_allclose(simple_triangle.x_mid, expected)


def test_triangle_area(simple_triangle):
    """
    Verify that the triangle area is computed correctly.

    For the right triangle with base=1 and height=1
    area = 0.5 * base * height = 0.5
    """
    assert simple_triangle.area == pytest.approx(0.5)


def test_edge_points(simple_triangle):
    """
    Verify that edge_points returns three edges, each defined by two 2D points.

    Expected:
    - 3 edges in total
    - each endpoint returned as a 2D vector
    """
    edges = simple_triangle.edge_points
    assert len(edges) == 3
    for p1, p2 in edges:
        assert p1.shape == (2,)
        assert p2.shape == (2,)


def test_edge_vectors_lengths(simple_triangle):
    """
    Verify that edge vectors have expected lengths.

    For the triangle (0,0), (1,0), (0,1):
    - two legs have length 1
    - the hypotenuse has length sqrt(2)
    """
    vectors = simple_triangle.edge_vector
    lengths = sorted(np.linalg.norm(v) for v in vectors)
    expected = sorted([1.0, 1.0, np.sqrt(2)])
    np.testing.assert_allclose(lengths, expected)


def test_normals_count(simple_triangle):
    """
    Verify that Triangle provides one normal vector per edge.

    A triangle has exactly three edges, so it should have three normals.
    """
    assert len(simple_triangle.normals) == 3


def test_normals_lengths(simple_triangle):
    """
    Verify that each normal vector has the same magnitude as its corresponding edge vector.

    Many finite-volume implementations define normals as edge-length-scaled normals.
    """
    normals = simple_triangle.normals
    edges = simple_triangle.edge_vector

    for n, e in zip(normals, edges):
        assert np.linalg.norm(n) == pytest.approx(np.linalg.norm(e))


def test_normals_point_outward(simple_triangle):
    """
    Verify that each normal points outward from the triangle.

    We check outward orientation by:
    - taking the triangle center
    - taking the midpoint of each edge
    - forming direction = edge_midpoint - center (points outward from interior)
    - verifying dot(normal, direction) > 0
    """
    center = simple_triangle.x_mid

    for (p1, p2), normal in zip(simple_triangle.edge_points, simple_triangle.normals):
        midpoint = 0.5 * (p1 + p2)
        direction = midpoint - center
        assert np.dot(normal, direction) > 0


def test_normals_orthogonal_to_edges(simple_triangle):
    """
    Verify that each normal vector is orthogonal to its corresponding edge vector.

    Orthogonality means dot(normal, edge) == 0
    """
    for normal, edge in zip(simple_triangle.normals, simple_triangle.edge_vector):
        assert np.dot(normal, edge) == pytest.approx(0.0)


def test_triangle_without_points():
    """
    Verify that Triangle raises RuntimeError when geometric properties are accessed
    without point coordinates

    The triangle is constructed with points=None, so derived geometry such as:
    - x_mid, area, edge_points, normals
    - cannot be computed and should raise RuntimeError.
    """
    tri = Triangle(point_ids=[0, 1, 2], idx=0, points=None)

    with pytest.raises(RuntimeError):
        _ = tri.x_mid

    with pytest.raises(RuntimeError):
        _ = tri.area

    with pytest.raises(RuntimeError):
        _ = tri.edge_points

    with pytest.raises(RuntimeError):
        _ = tri.normals


def test_triangle_wrong_number_of_points():
    """
    Verify that Triangle rejects invalid connectivity definitions.

    A triangle must be defined by exactly three point indices.
    Providing fewer or more should raise ValueError
    """
    with pytest.raises(ValueError):
        Triangle(point_ids=[0, 1], idx=0, points=np.zeros((3, 3)))
