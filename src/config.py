from pathlib import Path
import tomllib


class Config:
    """
    Reads and validates simulation configuration from a TOML file.
    """

    def __init__(self, filename: str):
        path = Path(filename)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filename}")

        with open(path, "rb") as f:
            data = tomllib.load(f)

        # required fields
        self.mesh_file = data.get("meshFile")
        self.dt = data.get("dt")
        self.t_end = data.get("tEnd")

        # optional fields (defaults)
        self.write_frequency = data.get("writeFrequency", None)
        self.log_name = data.get("logName", "logfile")

        self._validate()

    def _validate(self):
        if self.mesh_file is None:
            raise ValueError("Missing required config entry: meshFile")

        if self.dt is None:
            raise ValueError("Missing required config entry: dt")

        if self.t_end is None:
            raise ValueError("Missing required config entry: tEnd")

        if self.dt <= 0:
            raise ValueError("dt must be > 0")

        if self.t_end <= 0:
            raise ValueError("tEnd must be > 0")
