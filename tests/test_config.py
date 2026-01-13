import pytest
from config import Config


def write_toml(tmp_path, content: str):
    p = tmp_path / "config.toml"
    p.write_text(content, encoding="utf-8")
    return p


def test_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        Config("file not found")


def test_config_happy_path_reads_required_and_defaults(tmp_path):
    p = write_toml(
        tmp_path,
        """
meshFile = "bay.msh"
dt = 0.01
tEnd = 1.0
""",
    )

    cfg = Config(str(p))

    assert cfg.mesh_file == "bay.msh"
    assert cfg.dt == 0.01
    assert cfg.t_end == 1.0

    assert cfg.write_frequency is None
    assert cfg.log_name == "logfile"


def test_config_missing_mesh_file_raises(tmp_path):
    p = write_toml(
        tmp_path,
        """
dt = 0.01
tEnd = 1.0
""",
    )

    with pytest.raises(ValueError) as excinfo:
        Config(str(p))
    assert "meshFile" in str(excinfo.value)


def test_config_dt_must_be_positive(tmp_path):
    p = write_toml(
        tmp_path, """
meshFile = "bay.msh"
dt = 0
tEnd = 1.0
""",
    )

    with pytest.raises(ValueError) as excinfo:
        Config(str(p))
    assert "dt must be > 0" in str(excinfo.value)


def test_config_tend_must_be_positive(tmp_path):
    p = write_toml(
        tmp_path,
        """
meshFile = "bay.msh"
dt = 0.1
tEnd = 0
""",
    )

    with pytest.raises(ValueError) as excinfo:
        Config(str(p))
    assert "tEnd must be > 0" in str(excinfo.value)
