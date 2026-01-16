"""
Tests for the Config class.

These tests verify that simulation configuration files written in TOML format
are correctly read, validated, and rejected when invalid. The focus is on input
validation, default values, and error handling.
"""

import pytest
from src.config import Config


def write_toml(tmp_path, content: str):
    """
    Write a temporary TOML config file for testing.

    Parameters:
    tmp_path (parathlib.Path): Temporary directory provided by pytest.
    content (str): The TOML-formatted config content.

    Returns:
    pathlib.Path: Path to the written config file.
    """
    p = tmp_path / "config.toml"
    p.write_text(content, encoding="utf-8")
    return p


def test_config_file_not_found():
    """
    Verify that an error is raised when the config file does not exist.

    Raises:
    FileNotFoundError: If the specified config file cannot be found.
    """
    with pytest.raises(FileNotFoundError):
        Config("file not found")


def test_config_happy_path_reads_required_and_defaults(tmp_path):
    """
    Verify that a valid config file is read correctly, with defaults applied.

    The test checks that required values are correctly read from the
    config file, and that optional values take on their default settings
    """
    p = write_toml(
        tmp_path,
        """
meshName = "bay.msh"
nSteps = 100
tEnd = 1.0
borders = [[0.0, 0.45], [0.0, 0.2]]
""",
    )

    cfg = Config(str(p))

    assert cfg.mesh_file == "bay.msh"
    assert cfg.n_steps == 100
    assert cfg.dt == 0.01
    assert cfg.t_end == 1.0
    assert cfg.borders == [[0.0, 0.45], [0.0, 0.2]]

    assert cfg.write_frequency is None
    assert cfg.log_name == "logfile"


def test_config_missing_mesh_file_raises(tmp_path):
    """
    Verify that an error is raised when the mesh file is missing.

    Raises:
    ValueError: If the required meshFile parameter is missing.
    """
    p = write_toml(
        tmp_path,
        """
nSteps = 100
tEnd = 1.0
""",
    )

    with pytest.raises(ValueError) as excinfo:
        Config(str(p))
    assert "meshFile" in str(excinfo.value)


def test_config_nSteps_must_be_positive(tmp_path):
    """
    Verify that the time step must be positive

    Raises:
    ValueError: If dt is zero or negative.
    """
    p = write_toml(
        tmp_path, """
meshName = "bay.msh"
nSteps = 0
tEnd = 1.0
""",
    )

    with pytest.raises(ValueError) as excinfo:
        Config(str(p))
    assert "nSteps must be > 0" in str(excinfo.value)


def test_config_tend_must_be_positive(tmp_path):
    """
    Verify that the simulation end time must be positive.

    Raises:
    ValueError: If tEnd is zero or negative.
    """
    p = write_toml(
        tmp_path,
        """
meshName = "bay.msh"
nSteps = 100
tEnd = 0
""",
    )

    with pytest.raises(ValueError) as excinfo:
        Config(str(p))
    assert "tEnd must be > 0" in str(excinfo.value)
