"""
Unit tests for the Mesh class.

These tests verify that Mesh:
- reads points and supported cell types from a meshio-like object,
- ignores unsupported cell types,
- raises a RuntimeError if mesh reading fails
- correctly computes neighbor relationships between cells.
"""

import numpy as np
import pytest

from src.simulation.mesh.mesh import Mesh
from src.simulation.mesh.cells import Line, Triangle


class Block:
    """
    Minimal mock for a meshio CellBlock.

    Meshio commonly represents cells as "blocks" where:
    - type is a string (triangle, line, etc)
    - data is an array of indices describing the element connectivity

    Parameters:
    t (str): Mesh element type name.
    data (np.ndarray): Connectivity data for the elements.
    """
    def __init__(self, t, data):
        self.type = t
        self.data = data


class FakeMsh:
    """
    Minimal mesh object that imitates the parts of meshio's return value.

    Attributes:
    points (np.ndarray): Array of point coordinates.
    cells (list of Block): List of cell blocks.
    """
    def __init__(self, points, cells):
        self.points = points
        self.cells = cells


def test_mesh_reads_cells(monkeypatch):
    """
   Verify that Mesh reads points and creates supported cell objects.

   The test provides a FakeMsh containing:
   - a vertex block (should be ignored)
   - a line block (should become a Line cell),
   - a triangle block (should become a Triangle cell).

   The test also checks that the created cells get correct indices (idx).
    """
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])

    msh = FakeMsh(
        points=points,
        cells=[
            Block("vertex", np.array([[0]])),
            Block("line", np.array([[0, 1]])),
            Block("triangle", np.array([[0, 1, 2]])),
        ],
    )

    monkeypatch.setattr("simulation.mesh.mesh.meshio.read", lambda _: msh)

    m = Mesh("dummy.msh")

    assert np.all(m.points == points)
    assert len(m.cells) == 2
    assert isinstance(m.cells[0], Line)
    assert isinstance(m.cells[1], Triangle)
    assert m.cells[0].idx == 0
    assert m.cells[1].idx == 1


def test_mesh_raises_if_read_fails(monkeypatch):
    """
    Verify that Mesh raises RuntimeError if meshio.read fails.

    We simulate a failing mesh reader by patching meshio.read to raise an Exception.
    Mesh should catch this and raise RuntimeError to signal mesh loading failure.
    """
    def boom(_):
        raise Exception("fail")

    monkeypatch.setattr("simulation.mesh.mesh.meshio.read", boom)

    with pytest.raises(RuntimeError):
        Mesh("bad.msh")


def test_computeNeighbors(monkeypatch):
    """
    Verify that Mesh.computeNeighbors assigns neighbor relationships correctly.

    Two triangles are provided that share an edge, so each should list the other
    as its single neighbor.
    """

    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])

    msh = FakeMsh(
        points=points,
        cells=[
            Block("triangle", np.array([
                [0, 1, 2],
                [1, 2, 3],
            ])),
        ],
    )

    monkeypatch.setattr("simulation.mesh.mesh.meshio.read", lambda _: msh)

    m = Mesh("dummy.msh")
    m.computeNeighbors()

    assert m.cells[0].neighbors == [1]
    assert m.cells[1].neighbors == [0]


def test_mesh_ignores_unknown_cell_types(monkeypatch):
    """
    Verify that Mesh ignores unsupported element types.

    The test provides a quad element and a triangle element.
    Only the triangle should be converted into a Cell and stored in m.cells.
    """
    points = np.array([[0, 0, 0],
                       [1, 0, 0],
                       [0, 1, 0],
                       [1, 1, 0]])

    msh = FakeMsh(
        points=points,
        cells=[
            Block("quad", np.array([[0, 1, 3, 2]])),
            Block("triangle", np.array([[0, 1, 2]])),
        ],
    )

    monkeypatch.setattr("simulation.mesh.mesh.meshio.read", lambda _: msh)

    m = Mesh("dummy.msh")

    assert len(m.cells) == 1
    assert isinstance(m.cells[0], Triangle)
    assert m.cells[0].idx == 0
