import numpy as np
import pytest
from simulation.mesh.cells import Triangle

# TEST TRIANGLE GEOMETRY


@pytest.fixture
def simple_triangle():
    """
    Fixture that provides a simple triangle for testing.
    """
    # Points: (0,0), (1,0), (0,1)
    points = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ])
    point_ids = [0, 1, 2]
    return Triangle(point_ids=point_ids, idx=0, points=points)


def test_triangle_midpoint(simple_triangle):
    expected = np.array([1/3, 1/3])
    np.testing.assert_allclose(simple_triangle.x_mid, expected)


def test_triangle_area(simple_triangle):
    assert simple_triangle.area == pytest.approx(0.5)


def test_edge_points(simple_triangle):
    """
    Test that triangle has three edges with two points.
    """
    edges = simple_triangle.edge_points
    assert len(edges) == 3
    for p1, p2 in edges:
        assert p1.shape == (2,)
        assert p2.shape == (2,)


def test_edge_vectors_lengths(simple_triangle):
    """
    Test hypotenuse (sqrt(2)) and kathete (1.0) lengths of the triangle edges.
    """
    vectors = simple_triangle.edge_vector
    lengths = sorted(np.linalg.norm(v) for v in vectors)
    expected = sorted([1.0, 1.0, np.sqrt(2)])
    np.testing.assert_allclose(lengths, expected)

# TEST NORMAL VECTORS


def test_normals_count(simple_triangle):
    """
    Test that the triangle has three normal vectors.
    """
    assert len(simple_triangle.normals) == 3


def test_normals_lengths(simple_triangle):
    """
    Test that each normal vector has the same length as its corresponding edge vector.
    """
    normals = simple_triangle.normals
    edges = simple_triangle.edge_vector

    for n, e in zip(normals, edges):
        assert np.linalg.norm(n) == pytest.approx(np.linalg.norm(e))


def test_normals_point_outward(simple_triangle):
    """
    Test that each normal vector points outward from the triangle.
    """
    center = simple_triangle.x_mid

    for (p1, p2), normal in zip(simple_triangle.edge_points, simple_triangle.normals):
        midpoint = 0.5 * (p1 + p2)
        direction = midpoint - center
        assert np.dot(normal, direction) > 0

# TEST OTHERS


def test_normals_orthogonal_to_edges(simple_triangle):
    for normal, edge in zip(simple_triangle.normals, simple_triangle.edge_vector):
        assert np.dot(normal, edge) == pytest.approx(0.0)


def test_triangle_without_points():
    tri = Triangle(point_ids=[0, 1, 2], idx=0, points=None)
    assert tri.x_mid is None
    assert tri.area is None
    assert tri.edge_points is None
    assert tri.normals is None


def test_triangle_wrong_number_of_points():
    with pytest.raises(ValueError):
        Triangle(point_ids=[0, 1], idx=0, points=np.zeros((3, 3)))
