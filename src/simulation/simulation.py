import numpy as np
from physics.flux import flux
from mesh.cells import Triangle


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
        self.u_new[:] = self.u  # start with copy

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
                ngh = self.mesh.cells[ngh_idx]  # neighbor cell

                if not isinstance(ngh, Triangle):
                    continue

                # solution within neighbor cell
                u_ngh = self.u[ngh_idx]

                # scaled normal vector
                normal = cell.normals[k]

                # velocity
                v = 0.5 * (cell.velocity + ngh.velocity)

                update -= (self.dt / Ai) * flux(
                    ui,
                    u_ngh,
                    normal,
                    v
                )

            self.u_new[i] = ui + update

        # swap
        self.u, self.u_new = self.u_new, self.u

    def run(self, n_steps):
        '''
        Run the simulation for a given number of time steps.
        '''
        for _ in range(n_steps):
            self.step()
