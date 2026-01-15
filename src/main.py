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
    """
    Main entry point for the oil spill simulation.

    Orchestrates the complete simulation workflow:
    1. Parse command-line arguments and load configuration
    2. Set up logging to results folder
    3. Build computational mesh and detect neighbors
    4. Initialize and run the finite volume simulation
    5. Save final solution plot and generate output video

    Command-line Arguments:
        -c, --config (str): Path to TOML configuration file. Default: "input.toml"

    Returns:
        None

    Raises:
        FileNotFoundError: If config file or mesh file not found.
        RuntimeError: If mesh parsing or simulation fails.

    Example:
        python -m src.main -c config/test_case.toml
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Oil spill simulation"
    )
    parser.add_argument(
        "-c", "--config",
        default="input.toml",
        help="Path to config file"
    )

    args = parser.parse_args()

    # Load configuration from TOML file
    config = Config(args.config)

    # Create results folder structure: results/<config_name>/
    result_folder = Path("results") / Path(args.config).stem
    result_folder.mkdir(parents=True, exist_ok=True)

    # Initialize logger (writes to file in results folder)
    logger = setup_logger(
        log_name=config.log_name,
        level=logging.INFO,
        folder=result_folder
    )

    # Log simulation parameters
    logger.info("Simulation started.")
    logger.info(f"dt={config.dt}, t_end={config.t_end}, mesh={config.mesh_file}")

    # Build computational mesh and identify neighboring cells
    mesh = Mesh(config.mesh_file)
    mesh.computeNeighbors()

    # Create and run finite volume simulation
    sim = Simulation(mesh, config.dt)
    sim.run(config.t_end, writeFrequency=1)

    # Save final solution as image
    plot_solution(mesh, sim.u, "final.png")

    # Generate video from output images (if any were saved during simulation)
    subprocess.run([sys.executable, "src/video.py"])


if __name__ == "__main__":
    main()
