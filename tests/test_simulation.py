"""
Integration and behavior tests for the simulation class.

These tests verify that the simulation:
- remains numerically stable (no NaN or Inf values)
- respects boundry/line-cell constraints (Line cells must remain at u = 0),
- only transports oil to neighboring cells in one step,
- does not increase total mass (numerical diffusion / boundary loss allowed),
- moves oil in the expected direction based on flux/upwinding
- handles fishing ground queries and area-weighted oil computation correctly.

A small mesh(simple_mesh_2.msh) is used to make tests fast and repeatable
"""
from src.simulation.simulation import Simulation
from src.simulation.mesh.cells import Line, Triangle
import numpy as np
import pytest
from src.simulation.mesh.mesh import Mesh


@pytest.fixture
def simple_mesh():
    """
    Provide a small Mesh instance for Simulation tests.

    The mesh is loaded form a fixed test file so tests are deterministic and fast.

    Returns:
    Mesh: A mesh containing a mix of Triangle and Line cells with neighbors computed by Mesh.
    """

    # Using a real mesh file here makes these tests closer to integration tests
    # than pure unit tests, but still small enough to run quickly
    return Mesh("tests/data/simple_mesh_2.msh")


def test_no_nan_after_one_step(simple_mesh):
    """
    Verify that one simulation step does not produce NaN or Inf values

    This is a basic numerical stability check: starting from a constant field,
    the update should remain finite.
    """
    sim = Simulation(simple_mesh, dt=0.01)

    sim.u[:] = 1.0

    sim.step()

    assert not np.isnan(sim.u).any()
    assert not np.isinf(sim.u).any()


def test_line_cells_remain_zero(simple_mesh):
    """
    Verify that line cells remain at u = 0 after a simulation step.

    Line cells represents boundaries and should not store oil.
    Even if u is initialized to a non-zero value everywhere, the step should enforce u=0
    on line cells.
    """
    sim = Simulation(simple_mesh, dt=0.01)

    sim.u[:] = 1.0

    sim.step()

    for cell in simple_mesh.cells:
        if isinstance(cell, Line):
            assert sim.u[cell.idx] == 0.0


def test_oil_only_moves_to_neighbors(simple_mesh):
    """
    Verify that, in one time step, oil can only appear in neighboring cells.

    We place oil in exactly one source cell and step one.
    Then any non-source cell that is not a neighbor of the source must remain zero.
    This checks that the discretization only exchanges quantities across shared edges."""
    sim = Simulation(simple_mesh, dt=0.01)

    sim.u[:] = 0.0
    source = 0
    sim.u[source] = 1.0

    sim.step()

    neighbors = simple_mesh.cells[source].neighbors

    for i, val in enumerate(sim.u):
        if i == source:
            continue
        if i in neighbors:
            continue
        assert val == 0.0


def test_mass_is_non_increasing(simple_mesh):
    """
    Verify that total mass of u is non-increasing over multiple steps.

    Depending on the scheme and boundry handling, mass may decrease
    (outflow or numerical diffusion), but should not increase.
    """
    sim = Simulation(simple_mesh, dt=0.001)

    sim.u[:] = 1.0
    total_before = sim.u.sum()

    for _ in range(10):
        sim.step()

    total_after = sim.u.sum()

    assert total_after <= total_before


def test_flux_direction_reduces_upstream_cell(simple_mesh):
    """
    Verify that flux/outflow reduces the value in an upstream cell.

    We choose a Triangle cell that has at least one Triangle neighbor.
    If we initialize u high in the upstream cell and low in the neighbor,
    then after one step the upstream value should be reduced by outflow.
    """
    candidates = [
        (idx, cell) for idx, cell in enumerate(simple_mesh.cells)
        if isinstance(cell, Triangle) and len(cell.neighbors) > 0
    ]

    if not candidates:
        pytest.skip("Mesh has no triangle–triangle neighbors")

    sim = Simulation(simple_mesh, dt=0.01)
    sim.u[:] = 0.0

    i, cell = candidates[0]
    ngh = cell.neighbors[0]

    sim.u[i] = 1.0
    sim.u[ngh] = 0.0

    sim.step()

    assert sim.u[i] < 1.0


def test_initial_state_positive_and_peaked(simple_mesh):
    """
    Verify properties of the initial state produced by set_initial_state().

    Expected behavior:
    - u >= 0 everywhere (no negative oil concentration),
    - u has its maximum near x* = (0.35, 0.45).
    - Line celles should effectively behave as boundary,
    - though this test primarily checks peak location among Triangle cells.
    """
    sim = Simulation(simple_mesh, dt=0.01)
    sim.set_initial_state()

    u = sim.u

    assert (u >= 0).all()

    x_star = np.array([0.35, 0.45])
    distances = []

    for cell in simple_mesh.cells:
        if isinstance(cell, Triangle):
            distances.append(
                np.linalg.norm(cell.midpoint - x_star)
            )
        else:
            distances.append(np.inf)

    i_min = np.argmin(distances)
    assert u[i_min] == pytest.approx(u.max())


def test_empty_fishing_ground(simple_mesh):
    """
    Verify that oil_in_fishing_ground returns 0.0 when no fishing cells exist.

    This is a safety/edge-case test: if find_fishing_ground_cells finds none,
    then the computed oil in fishing ground should be zero
    """
    sim = Simulation(simple_mesh, dt=0.01)
    sim.u[:] = 1.0

    borders = [[0.0, 0.45], [0.0, 0.2]]
    sim.find_fishing_ground_cells(borders)

    if len(sim.fishing_cells) == 0:
        assert sim.oil_in_fishing_ground() == 0.0


def test_fishing_ground_area_weighted(simple_mesh):
    """
    Verify that oil_in_fishing_ground is area weighted.

    We set u = 1.0 in all Triangle cells.
    Then the oil in fishing ground should equal the sum of areas
    of the fishing ground cells.(since u acts as a density here)
    """
    borders = [[0.0, 0.45], [0.0, 0.2]]

    sim = Simulation(simple_mesh, dt=0.01)
    sim.find_fishing_ground_cells(borders)

    for cell in simple_mesh.cells:
        if isinstance(cell, Triangle):
            sim.u[cell.idx] = 1.0

    expected = sum(
        simple_mesh.cells[i].area
        for i in sim.fishing_cells
    )

    assert sim.oil_in_fishing_ground() == pytest.approx(expected)


def test_simulation_stability(simple_mesh):
    """
    Verify stability over many steps using the full run() method.

    The test initializes u using set_initial_state, runs multiple steps,
    and asserts that all values remain finite (no NaN or Inf).
    This checks that the main simulation loop is stable for the chosen dt.
    """
    sim = Simulation(simple_mesh, dt=0.001)
    sim.set_initial_state()

    sim.run(50, writeFrequency=None)

    assert np.isfinite(sim.u).all()
