import numpy as np
from .physics.flux import flux_contribution
from .mesh.cells import Triangle, Line
from src.plotting import plot_solution


class Simulation:
    def __init__(self, mesh, dt):
        '''
        Initialize simulation with given mesh and time step.
        '''
        self.mesh = mesh
        self.dt = dt

        # solution: one value per cell
        self.u = np.zeros(len(mesh.cells))

        # temporary storage for updated solution
        self.u_new = np.zeros_like(self.u)

    def step(self):
        '''
        Advance the solution by one time step using finite volume method.
        '''
        self.u_new[:] = self.u[:]  # start with current solution

        for cell in self.mesh.cells:
            if not isinstance(cell, Triangle):
                continue

            i = cell.idx
            Ai = cell.area

            if Ai <= 0:
                continue

            ui = self.u[i]

            update = 0.0

            for k, ngh_idx in enumerate(cell.neighbors):
                ngh_idx = cell.edge_to_neighbor[k]
                if ngh_idx is None:
                    continue

                ngh = self.mesh.cells[ngh_idx]  # neighbor cell
                normal = cell.normals[k]  # scaled normal vector

                if isinstance(ngh, Triangle):
                    u_ngh = self.u[ngh_idx]
                    v_ngh = ngh.velocity
                else:
                    u_ngh = 0.0
                    v_ngh = np.zeros_like(cell.velocity)

                update += flux_contribution(
                    ui,
                    u_ngh,
                    Ai,
                    normal,
                    cell.velocity,
                    v_ngh,
                    self.dt
                )

            self.u_new[i] = ui + update

        # enforce boundary condition: line cells are always zero
        for cell in self.mesh.cells:
            if isinstance(cell, Line):
                self.u_new[cell.idx] = 0.0

        # swap
        self.u, self.u_new = self.u_new, self.u

    def run(self, t_end, writeFrequency=1):
        '''
        Run the simulation for a given number of time steps.
        '''
        self.set_initial_state()

        n_steps = int(t_end / self.dt)
        for step in range(n_steps):
            self.step()

            if step % writeFrequency == 0:
                plot_solution(
                    self.mesh,
                    self.u,
                    f"tmp/img_{step:04d}.png"
                )

    def set_initial_state(self, x_start=np.array([0.35, 0.45]), sigma2=0.01):
        for cell in self.mesh.cells:
            if isinstance(cell, Triangle):
                x = cell.midpoint
                dx = x - x_start
                self.u[cell.idx] = np.exp(-np.dot(dx, dx) / sigma2)
            else:
                self.u[cell.idx] = 0.0

    def find_fishing_ground_cells(self):

        self.fishing_cells = []

        for cell in self.mesh.cells:
            if not isinstance(cell, Triangle):
                continue

            x, y = cell.midpoint
            if 0.0 <= x <= 0.45 and 0.0 <= y <= 0.2:
                self.fishing_cells.append(cell.idx)

    def oil_in_fishing_ground(self):
        return sum(self.u[i] * self.mesh.cells[i].area for i in self.fishing_cells)
