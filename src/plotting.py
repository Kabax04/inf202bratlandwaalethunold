import numpy as np
import matplotlib.pyplot as plt

from .simulation.mesh.cells import Triangle


def plot_solution(mesh, u, filename, umin=None, umax=None):
    """
    Plot oil distribution on the triangular mesh.

    Parameters
    ----------
    mesh : Mesh
        Mesh object containing points and cells.
    u : np.ndarray
        Oil amount per cell (indexed by cell.idx).
    filename : str
        Output filename (e.g. "img_000.png").
    umin : float, optional
        Global minimum for colormap normalization.
    umax : float, optional
        Global maximum for colormap normalization.
    """

    if umin is None:
        umin = np.min(u)
    if umax is None:
        umax = np.max(u)

    fig, ax = plt.subplots()

    # Create colormap
    sm = plt.cm.ScalarMappable(cmap="viridis")
    sm.set_array([umin, umax])

    # Add colorbar
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Oil concentration")

    # Plot each triangle
    for cell in mesh.cells:
        if not isinstance(cell, Triangle):
            continue

        # Get triangle corner coordinates (ignore z-coordinate)
        pts = np.array([mesh.points[i][:2] for i in cell.point_ids])

        value = u[cell.idx]

        # Normalize value to [0, 1]
        color_value = (value - umin) / (umax - umin) if umax > umin else 0.0
        color = plt.cm.viridis(color_value)

        ax.add_patch(plt.Polygon(pts, color=color))

    # Mark the fishing grounds
    fishing_rect = plt.Rectangle(
        (0.0, 0.0), 0.45, 0.2,
        linewidth=2, edgecolor='red', facecolor='none', linestyle='dashed', label='Fishing grounds'
        )

    ax.add_patch(fishing_rect)
    ax.legend()

    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    fig.savefig(filename, bbox_inches="tight")
    plt.close()
