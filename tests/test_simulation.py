from simulation.simulation import Simulation
from simulation.mesh.cells import Line, Triangle
import numpy as np
import pytest
from simulation.mesh.mesh import Mesh


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
