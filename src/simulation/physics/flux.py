import numpy as np


def flux(a, b, normal, edge_velocity):
    """
    Compute flux across a cell edge.

    Parameters:
    a = u_i, oil amount in cell.
    b = u_ngh, oil amount in neighbor cell.
    normal = scaled normal.
    edge_velocity = velocity field contribution at edge of cell.

    Returns: flow contribution across the edge.
    """
    dot = np.dot(edge_velocity, normal)
    if dot > 0:
        return a * dot
    else:
        return b * dot


def flux_contribution(
        u_i, u_ngh,
        area_i,
        normal_i_l,
        edge_velocity_i, edge_velocity_ngh,
        dt
        ):
    """
    Compute flux contribution from a neighboring cell.

    Parameters:
    u_i = oil amount in cell i.
    u_ngh = oil amount in neighbor cell.
    area_i = area of cell i.
    normal_i_l = scaled outward normal between cell i and neighbor cell l.
    edge_velocity_i = velocity field at midpoint of cell i.
    edge_velocity_ngh = velocity field at midpoint of neighbor cell.
    dt = timestep for simulation.

    Returns: Change in oil amount in cell i due to this neighbor.
    """

    # avg velocity field contribution at edge of the two neighbor cells
    edge_velocity_avg = 0.5 * (edge_velocity_i + edge_velocity_ngh)
    return -dt / area_i * flux(u_i, u_ngh, normal_i_l, edge_velocity_avg)
