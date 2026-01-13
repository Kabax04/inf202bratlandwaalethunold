import argparse
import subprocess
import sys

from .config import Config
from .simulation.mesh.mesh import Mesh
from .simulation.simulation import Simulation
from .plotting import plot_solution


def main():
    parser = argparse.ArgumentParser(
        description="Oil spill simulation"
    )
    parser.add_argument(
        "-c", "--config",
        default="input.toml",
        help="Path to config file"
    )

    args = parser.parse_args()

    # read config
    config = Config(args.config)

    # build mesh
    mesh = Mesh(config.mesh_file)
    mesh.computeNeighbors()

    # create and run simulation
    sim = Simulation(mesh, config.dt)
    sim.run(config.t_end, 2)

    plot_solution(mesh, sim.u, "final.png")
    subprocess.run([sys.executable, "src/video.py"])


if __name__ == "__main__":
    main()
