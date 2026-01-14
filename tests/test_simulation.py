from src.simulation.simulation import Simulation
from src.simulation.mesh.cells import Line, Triangle
import numpy as np
import pytest
from src.simulation.mesh.mesh import Mesh


@pytest.fixture
def simple_mesh():
    return Mesh("tests/data/simple_mesh_2.msh")


# TEST TO ENSURE NO NaN OR INF VALUES AFTER ONE SIMULATION STEP

def test_no_nan_after_one_step(simple_mesh):
    sim = Simulation(simple_mesh, dt=0.01)

    # init med noe > 0
    sim.u[:] = 1.0

    sim.step()

    assert not np.isnan(sim.u).any()
    assert not np.isinf(sim.u).any()


# TEST TO ENSURE LINE CELLS REMAIN ZERO AFTER ONE SIMULATION STEP

def test_line_cells_remain_zero(simple_mesh):
    sim = Simulation(simple_mesh, dt=0.01)

    # sett alt til 1 først
    sim.u[:] = 1.0

    sim.step()

    for cell in simple_mesh.cells:
        if isinstance(cell, Line):
            assert sim.u[cell.idx] == 0.0


# TEST TO ENSURE OIL ONLY MOVES TO NEIGHBORING CELLS AFTER ONE SIMULATION STEP

def test_oil_only_moves_to_neighbors(simple_mesh):
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


# TEST TO ENSURE MASS IS APPROXIMATELY CONSERVED OVER MULTIPLE STEPS

def test_mass_is_non_increasing(simple_mesh):
    sim = Simulation(simple_mesh, dt=0.001)

    sim.u[:] = 1.0
    total_before = sim.u.sum()

    for _ in range(10):
        sim.step()

    total_after = sim.u.sum()

    # oil can only move out through boundaries, so total should not increase
    assert total_after <= total_before


# TEST TO ENSURE FLUX DIRECTION REDUCES UPSTREAM CELL VALUE

def test_flux_direction_reduces_upstream_cell(simple_mesh):
    candidates = [
        (idx, cell) for idx, cell in enumerate(simple_mesh.cells)
        if isinstance(cell, Triangle) and len(cell.neighbors) > 0
    ]

    if not candidates:
        # This test requires a triangle–triangle interface.
        # Some meshes contain only triangle–line boundaries, in which case
        # the flux direction test is not applicable and is therefore skipped.
        pytest.skip("Mesh has no triangle–triangle neighbors")

    sim = Simulation(simple_mesh, dt=0.01)
    sim.u[:] = 0.0

    i, cell = candidates[0]
    ngh = cell.neighbors[0]

    sim.u[i] = 1.0
    sim.u[ngh] = 0.0

    sim.step()

    assert sim.u[i] < 1.0


# TEST TO ENSURE INITIAL STATE IS POSITIVE AND PEAKED AT GIVEN POINT

def test_initial_state_positive_and_peaked(simple_mesh):
    '''
    u >= 0 everywhere
    maximum at point x* = (0.35, 0.45)
    Line cells allways have u == 0
    '''
    sim = Simulation(simple_mesh, dt=0.01)
    sim.set_initial_state()

    u = sim.u

    # 1. No negative values
    assert (u >= 0).all()

    # 2. Find triangle closest to x*
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


# TEST TO ENSURE NO OIL IN FISHING GROUND WHEN INITIAL STATE IS ZERO

def test_empty_fishing_ground(simple_mesh):
    sim = Simulation(simple_mesh, dt=0.01)
    sim.u[:] = 1.0  # puts oil everywhere

    sim.find_fishing_ground_cells()

    if len(sim.fishing_cells) == 0:
        assert sim.oil_in_fishing_ground() == 0.0


# AREA-WEIGHTED SUM

def test_fishing_ground_area_weighted(simple_mesh):
    sim = Simulation(simple_mesh, dt=0.01)
    sim.find_fishing_ground_cells()

    # sett u = 1 på alle triangle-celler
    for cell in simple_mesh.cells:
        if isinstance(cell, Triangle):
            sim.u[cell.idx] = 1.0

    expected = sum(
        simple_mesh.cells[i].area
        for i in sim.fishing_cells
    )

    assert sim.oil_in_fishing_ground() == pytest.approx(expected)


# STABILITY TEST: NO NAN OR INF

def test_simulation_stability(simple_mesh):
    sim = Simulation(simple_mesh, dt=0.001)
    sim.set_initial_state()

    sim.run(50, writeFrequency=None)  # disable plotting for test to save time

    assert np.isfinite(sim.u).all()
