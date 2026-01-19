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


def looks_like_result_folder(path: Path) -> bool:
    """
    Check if a folder appears to be a simulation result folder.

    Heuristic check: returns True if folder contains log files, final.png, or video.avi.
    Used to prevent accidentally overwriting result folders with new simulations.

    Args:
        path (Path): Folder path to check.

    Returns:
        bool: True if folder appears to contain simulation results, False otherwise.
    """
    if not path.is_dir():
        return False
    # Check for log files, final plot, or video output
    if any(path.glob("*.log")):
        return True
    if (path / "final.png").exists():
        return True
    if (path / "video.avi").exists():
        return True
    return False


def run_single_config(config_path: Path) -> None:
    """
    Run a single simulation with the given configuration file.

    Workflow:
    1. Load and validate configuration from TOML file
    2. Create results folder (with safety check to prevent overwriting)
    3. Set up logging to results folder
    4. Build mesh and compute neighbor topology
    5. Run finite volume simulation
    6. Save final solution plot and generate video (if enabled)

    Args:
        config_path (Path): Path to TOML configuration file.

    Raises:
        FileExistsError: If result folder exists but doesn't look like a result folder
                        (safety check to prevent data loss).
        FileNotFoundError: If config file or mesh file not found.
        ValueError: If configuration is invalid.
    """
    # Load configuration from TOML file
    config = Config(str(config_path))

    # Create results folder structure: results/<config_name>/
    result_folder = Path("results") / config_path.stem

    # Safety check: prevent overwriting non-result folders
    if result_folder.exists() and not looks_like_result_folder(result_folder):
        raise FileExistsError(
            f"Will not overwrite existing non-result folder: {result_folder}"
        )

    result_folder.mkdir(parents=True, exist_ok=True)

    # Reset logger handlers so each config logs to its own file in batch mode
    base_logger = logging.getLogger("oil_simulation")
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)
        h.close()

    # Initialize logger (writes to file in results folder)
    logger = setup_logger(
        log_name=config.log_name,
        level=logging.INFO,
        folder=result_folder
    )

    # Log simulation parameters
    logger.info("Simulation started.")
    logger.info(f"Config file: {config_path}")
    logger.info("Simulation parameters (from TOML):")
    for k, v in config.raw.items():
        logger.info(f"  {k} = {v}")

    # Build computational mesh and identify neighboring cells
    mesh = Mesh(config.mesh_file)
    mesh.computeNeighbors()

    # If we will generate frames/video, ensure tmp/ is clean to avoid mixing runs
    if config.write_frequency is not None and config.write_frequency > 0:
        tmp_dir = Path("tmp")
        if tmp_dir.exists() and tmp_dir.is_dir():
            for f in tmp_dir.glob("img_*.png"):
                f.unlink()

    # Create and run finite volume simulation
    sim = Simulation(mesh, config.dt, config.borders)
    sim.run(config.t_end, writeFrequency=config.write_frequency, logger=logger)

    # Log final simulation results
    logger.info("Simulation summary (from main):")
    logger.info(f"  final_fishing_ground_oil = {sim.oil_in_fishing_ground():.12e}")

    borders = config.borders

    # Save final solution as image INSIDE the result folder
    plot_solution(mesh, sim.u, str(result_folder / "final.png"), borders)

    # Generate video if write_frequency is enabled
    if config.write_frequency is not None and config.write_frequency > 0:
        # Run video generation script
        subprocess.run([sys.executable, "src/video.py"], check=True)

        # Move generated video into this result folder
        video = Path("video.avi")
        if video.exists():
            video.replace(result_folder / "video.avi")
    else:
        print("Video not generated (write_frequency disabled)")


def main():
    """
    Main entry point for the oil spill simulation framework.

    Supports two execution modes:
    1. **Single config mode** (default): Run simulation with one TOML config file
    2. **Batch mode**: Find and run all config files in a folder

    Workflow:
    - Parse command-line arguments to determine execution mode
    - For each configuration: call run_single_config() to execute simulation
    - Each simulation creates its own results folder with logs, plots, and video

    Command-line Arguments:
        -c, --config (str): Path to TOML configuration file for single config mode.
                            Default: "input.toml"
        --find (str): Enable batch mode. Use "--find all" to run all configs in folder.
        -f, --folder (str): Folder to search for config files when using --find all.
                            Default: current directory (.)

    Returns:
        None

    Raises:
        FileNotFoundError: If config file, mesh file, or search folder not found.
        ValueError: If configuration is invalid.

    Examples:
        # Single config mode (default)
        python -m src.main -c config/test_case.toml

        # Batch mode: run all configs in a folder
        python -m src.main --find all -f config/
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Oil spill simulation: finite volume solver on unstructured meshes"
    )
    parser.add_argument(
        "-c", "--config",
        default="input.toml",
        help="Path to config file (default: input.toml)"
    )

    parser.add_argument(
        "--find",
        choices=["all"],
        default=None,
        help="Find and run all config files in a folder (use: --find all)"
    )

    parser.add_argument(
        "-f", "--folder",
        default=None,
        help="Folder to search for config files when using --find all (default: current directory)"
    )

    args = parser.parse_args()

    # Mode 1: Batch mode - find and run all configs in folder
    if args.find == "all":
        search_folder = Path(args.folder) if args.folder else Path(".")

        # Validate search folder exists
        if not search_folder.exists() or not search_folder.is_dir():
            raise FileNotFoundError(f"Folder not found: {search_folder}")

        # Find all TOML config files in the folder
        config_files = sorted([p for p in search_folder.glob("*.toml") if p.is_file()])

        if not config_files:
            print(f"No .toml config files found in {search_folder}")
            return

        # Run each config file sequentially
        for cfg in config_files:
            run_single_config(cfg)

        return

    # Mode 2: Single config mode (default) - run one specified config
    run_single_config(Path(args.config))


if __name__ == "__main__":
    main()
