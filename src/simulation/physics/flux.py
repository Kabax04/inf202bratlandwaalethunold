import numpy as np


def flux(a, b, normal, edge_velocity):

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

    edge_velocity_avg = 0.5 * (edge_velocity_i + edge_velocity_ngh)
    return -dt / area_i * flux(u_i, u_ngh, normal_i_l, edge_velocity_avg)
