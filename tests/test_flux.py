"""
Unit tests for flux and flux_contribution functions.

These tests verify that the numerical flux computation follows the
upwind scheme based on the sign of the velocity-normal dot product,
and that flux contributions are scaled correctly by time step and area.
"""


import numpy as np
from src.simulation.physics.flux import flux, flux_contribution


def test_flux_positive_dot_uses_a():
    """
    Verify that flux uses the value from the current cell for positive flow.

    When the dot product between velocity and normal is positive,
    the flux should be computed using the value a.
    """
    a = 2.0
    b = 5.0
    normal = np.array([1.0, 0.0])
    velocity = np.array([3.0, 0.0])

    result = flux(a, b, normal, velocity)

    assert result == a * 3.0


def test_flux_negative_dot_uses_b():
    """
    Verify that flux uses the neighbor value for negative flow.

    When the dot product between velocity and normal is negative,
    the flux should be computed using the value b.
    """
    a = 2.0
    b = 5.0
    normal = np.array([1.0, 0.0])
    velocity = np.array([-4.0, 0.0])

    result = flux(a, b, normal, velocity)

    assert result == b * (-4.0)


def test_flux_zero_dot_is_zero():
    """
    Verify that flux is zero when the velocity is orthogonal to the normal.

    If the dot product between velocity and normal is zero,
    no flux should pass through the edge.
    """
    a = 2.0
    b = 5.0
    normal = np.array([1.0, 0.0])
    velocity = np.array([0.0, 2.0])

    result = flux(a, b, normal, velocity)

    assert result == 0.0


def test_flux_contribution_positive_flow():
    """
    Verify flux contribution for positive flow direction.

    The test checks that contribution uses the cell value u_i,
    applies the correct flux sign, and scales the result by dt / area.
    """
    u_i = 2.0
    u_ngh = 10.0
    area = 4.0
    dt = 0.5

    normal = np.array([1.0, 0.0])
    v_i = np.array([2.0, 0.0])
    v_ngh = np.array([2.0, 0.0])

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


def test_flux_contribution_zero_velocity_gives_zero():
    """
    Verify that zero velocity produces zero flux contribution.

    When both cell velocities are zero, the average velocity is zero
    and no flux contribution should occur.
    """
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
