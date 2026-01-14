import argparse
import subprocess
import sys
import logging
from pathlib import Path

from .config import Config
from .simulation.mesh.mesh import Mesh
from .simulation.simulation import Simulation
from .plotting import plot_solution
from .utils.logger import setup_logger


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

    result_folder = Path("results") / Path(args.config).stem
    result_folder.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(
        log_name=config.log_name,
        level=logging.INFO,
        folder=result_folder
    )

    logger.info("Simulation started.")
    logger.info(f"dt={config.dt}, t_end={config.t_end}, mesh={config.mesh_file}")

    # build mesh
    mesh = Mesh(config.mesh_file)
    mesh.computeNeighbors()

    # create and run simulation
    sim = Simulation(mesh, config.dt)
    sim.run(config.t_end, 1)

    plot_solution(mesh, sim.u, "final.png")
    subprocess.run([sys.executable, "src/video.py"])


if __name__ == "__main__":
    main()
