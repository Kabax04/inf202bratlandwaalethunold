"""
test_mesh.py

Contains unit tests for the Mesh class in simulation.mesh.mesh.
"""

import numpy as np
import pytest

from simulation.mesh.mesh import Mesh
from simulation.mesh.cells import Line, Triangle


class Block:  # fake class to mimic meshio Block
    def __init__(self, t, data):
        self.type = t
        self.data = data


class FakeMsh:  # fake class to mimic meshio Mesh
    def __init__(self, points, cells):
        self.points = points
        self.cells = cells


def test_mesh_reads_cells(monkeypatch):  # monkeypatch used to mock meshio.read
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])

    msh = FakeMsh(
        points=points,
        cells=[
            Block("vertex", np.array([[0]])),          # should be ignored
            Block("line", np.array([[0, 1]])),         # cell id 0
            Block("triangle", np.array([[0, 1, 2]])),  # cell id 1
        ],
    )

    monkeypatch.setattr("simulation.mesh.mesh.meshio.read", lambda _: msh)

    m = Mesh("dummy.msh")

    assert np.all(m.points == points)
    assert len(m.cells) == 2
    assert isinstance(m.cells[0], Line)
    assert isinstance(m.cells[1], Triangle)
    assert m.cells[0].id == 0
    assert m.cells[1].id == 1


def test_mesh_raises_if_read_fails(monkeypatch):  # monkeypatch used to mock meshio.read
    def boom(_):
        raise Exception("fail")

    monkeypatch.setattr("simulation.mesh.mesh.meshio.read", boom)

    with pytest.raises(RuntimeError):
        Mesh("bad.msh")


def test_computeNeighbors(monkeypatch):
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])

    msh = FakeMsh(
        points=points,
        cells=[
            Block("triangle", np.array([
                [0, 1, 2],  # id 0
                [1, 2, 3],  # id 1 (neighbor to id 0   )
            ])),
        ],
    )

    monkeypatch.setattr("simulation.mesh.mesh.meshio.read", lambda _: msh)

    m = Mesh("dummy.msh")
    m.computeNeighbors()

    assert m.cells[0].neighbors == [1]
    assert m.cells[1].neighbors == [0]

def test_mesh_ignores_unknown_cell_types(monkeypatch):
    points = np.array([[0, 0, 0],
                       [1, 0, 0],
                       [0, 1, 0],
                       [1, 1, 0]])

    msh = FakeMsh(
        points=points,
        cells=[
            Block("quad", np.array([[0, 1, 3, 2]])),      # ukjent type -> treffer else: continue
            Block("triangle", np.array([[0, 1, 2]])),     # kjent type -> blir med
        ],
    )

    monkeypatch.setattr("simulation.mesh.mesh.meshio.read", lambda _: msh)

    m = Mesh("dummy.msh")

    # quad skal ignoreres, bare triangle blir med
    assert len(m.cells) == 1
    assert isinstance(m.cells[0], Triangle)
    assert m.cells[0].id == 0
