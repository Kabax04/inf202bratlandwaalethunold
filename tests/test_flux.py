import numpy as np
from src.simulation.physics.flux import flux, flux_contribution


# TESTS FOR flux FUNCTION

def test_flux_positive_dot_uses_a():  # positive dot product
    a = 2.0
    b = 5.0
    normal = np.array([1.0, 0.0])
    velocity = np.array([3.0, 0.0])  # dot = 3

    result = flux(a, b, normal, velocity)

    assert result == a * 3.0


def test_flux_negative_dot_uses_b():  # negative dot product
    a = 2.0
    b = 5.0
    normal = np.array([1.0, 0.0])
    velocity = np.array([-4.0, 0.0])  # dot = -4

    result = flux(a, b, normal, velocity)

    assert result == b * (-4.0)


def test_flux_zero_dot_is_zero():  # zero dot product
    a = 2.0
    b = 5.0
    normal = np.array([1.0, 0.0])
    velocity = np.array([0.0, 2.0])  # dot = 0

    result = flux(a, b, normal, velocity)

    assert result == 0.0


# TEST FOR flux_contribution FUNCTION

def test_flux_contribution_positive_flow():  # positive dot product case
    u_i = 2.0
    u_ngh = 10.0
    area = 4.0
    dt = 0.5

    normal = np.array([1.0, 0.0])
    v_i = np.array([2.0, 0.0])
    v_ngh = np.array([2.0, 0.0])  # avg = (2,0)

    # dot = 2 → bruker u_i
    expected_flux = u_i * 2.0
    expected = -dt / area * expected_flux

    result = flux_contribution(
        u_i, u_ngh,
        area,
        normal,
        v_i, v_ngh,
        dt
    )

    assert np.isclose(result, expected)


# SANITY CHECK FOR flux_contribution FUNCTION

def test_flux_contribution_zero_velocity_gives_zero():  # zero velocity case
    u_i = 3.0
    u_ngh = 7.0
    area = 2.0
    dt = 0.1

    normal = np.array([1.0, 0.0])
    v_i = np.array([0.0, 0.0])
    v_ngh = np.array([0.0, 0.0])

    result = flux_contribution(
        u_i, u_ngh,
        area,
        normal,
        v_i, v_ngh,
        dt
    )

    assert result == 0.0
