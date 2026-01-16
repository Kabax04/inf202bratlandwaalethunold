from pathlib import Path
import numpy as np
from .physics.flux import flux_contribution
from .mesh.cells import Triangle, Line
from ..plotting import plot_solution


class Simulation:
    """
    Finite volume solver for advection-diffusion problems on unstructured meshes.

    Solves a conservation law by computing fluxes across cell edges and updating
    cell-centered solution values. Supports boundary conditions via Line cells
    (set to zero) and initial conditions via Gaussian distributions.

    Attributes:
        mesh (Mesh): Computational mesh containing cells and points.
        dt (float): Time step size for temporal discretization.
        u (np.ndarray): Solution vector, one value per cell (shape: [n_cells]).
        u_new (np.ndarray): Temporary storage for updated solution after one time step.

    Example:
        mesh = Mesh("domain.msh")
        mesh.computeNeighbors()
        sim = Simulation(mesh, dt=0.001)
        sim.run(t_end=1.0, writeFrequency=10)
    """

    def __init__(self, mesh, dt, borders=None):
        """
        Initialize simulation with mesh and time step.

        Args:
            mesh (Mesh): Computational mesh object.
            dt (float): Time step size for temporal discretization.
        """
        self.mesh = mesh
        self.dt = dt
        self.borders = borders

        # Solution: one value per cell (cell-centered)
        self.u = np.zeros(len(mesh.cells))

        # Temporary storage for updated solution (avoids overwriting during iteration)
        self.u_new = np.zeros_like(self.u)

    def step(self):
        """
        Advance the solution by one time step using the finite volume method.

        For each triangle cell:
        1. Compute flux contributions across all edges
        2. Update cell value based on flux balance and time step
        3. Enforce boundary conditions (Line cells set to zero)
        """
        # Start with current solution values
        self.u_new[:] = self.u[:]

        # Process each triangle cell (Line cells are boundaries, skip in update)
        for cell in self.mesh.cells:
            if not isinstance(cell, Triangle):
                continue

            i = cell.idx
            Ai = cell.area

            # Skip degenerate cells with zero or negative area
            if Ai <= 0:
                continue

            ui = self.u[i]
            update = 0.0

            # Loop over the 3 edges of the triangle
            for k in range(len(cell.neighbors)):
                # Get neighbor index for this specific edge (may be None if boundary)
                ngh_idx = cell.edge_to_neighbor[k]
                if ngh_idx is None:
                    continue

                ngh = self.mesh.cells[ngh_idx]
                # Outward normal vector for this edge (weighted by edge length)
                normal = cell.normals[k]

                # Get neighbor solution value; handle Line cells (boundary) as u=0
                if isinstance(ngh, Triangle):
                    u_ngh = self.u[ngh_idx]
                    v_ngh = ngh.velocity
                else:
                    u_ngh = 0.0
                    v_ngh = np.zeros_like(cell.velocity)

                # Compute flux across edge and accumulate update
                update += flux_contribution(
                    ui,
                    u_ngh,
                    Ai,
                    normal,
                    cell.velocity,
                    v_ngh,
                    self.dt
                )

            # Update solution for this cell
            self.u_new[i] = ui + update

        # Enforce boundary condition: Line cells (boundaries) are always zero
        for cell in self.mesh.cells:
            if isinstance(cell, Line):
                self.u_new[cell.idx] = 0.0

        # Swap solution and temporary arrays (efficient update without copying)
        self.u, self.u_new = self.u_new, self.u

    def run(self, t_end, writeFrequency=1):
        """
        Run the simulation until time t_end, optionally saving plots.

        Args:
            t_end (float): Final simulation time.
            writeFrequency (int, optional): Save plot every N steps. None or <=0 disables plotting.
        """
        self.set_initial_state()

        # Check if plotting is enabled
        do_plot = (writeFrequency is not None) and (writeFrequency > 0)
        if do_plot:
            # Create tmp directory for output images
            Path("tmp").mkdir(parents=True, exist_ok=True)

        # Calculate number of time steps
        n_steps = int(t_end / self.dt)
        for step in range(n_steps):
            self.step()

            # Write output at specified frequency
            if do_plot and (step % writeFrequency == 0):
                plot_solution(
                    self.mesh,
                    self.u,
                    f"tmp/img_{step:04d}.png",
                    self.borders
                )

    def set_initial_state(self, x_start=np.array([0.35, 0.45]), sigma2=0.01):
        """
        Initialize solution with a Gaussian bump centered at x_start.

        Sets Line cells (boundaries) to zero and Triangle cells to Gaussian values
        based on distance from center.

        Args:
            x_start (np.ndarray): Center of Gaussian bump [x, y] coordinates.
            sigma2 (float): Variance parameter for Gaussian decay.
        """
        for cell in self.mesh.cells:
            if isinstance(cell, Triangle):
                # Get cell centroid coordinates
                x = cell.x_mid
                dx = x - x_start
                # Gaussian: exp(-distance^2 / sigma2)
                self.u[cell.idx] = np.exp(-np.dot(dx, dx) / sigma2)
            else:
                # Boundary cells start at zero
                self.u[cell.idx] = 0.0

    def find_fishing_ground_cells(self, borders):
        """
        Identify all triangle cells within the fishing ground domain.

        Stores indices of cells in region: 0 <= x <= 0.45, 0 <= y <= 0.2.
        Call this before computing oil_in_fishing_ground().
        """
        self.fishing_cells = []

        for cell in self.mesh.cells:
            if not isinstance(cell, Triangle):
                continue

            x_min, x_max = borders[0]
            y_min, y_max = borders[1]
            # Get cell centroid
            x, y = cell.x_mid
            # Check if cell is within fishing ground bounds
            if x_min <= x <= x_max and y_min <= y <= y_max:
                self.fishing_cells.append(cell.idx)

    def oil_in_fishing_ground(self):
        """
        Compute total amount of oil (integrated solution) in fishing ground region.

        Returns sum of (cell_value * cell_area) over all fishing ground cells.
        Requires find_fishing_ground_cells() to be called first.

        Returns:
            float: Total integrated concentration in fishing ground.
        """
        return sum(self.u[i] * self.mesh.cells[i].area for i in self.fishing_cells)
