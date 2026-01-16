from pathlib import Path
import tomllib


class Config:
    """
    Reads and validates simulation configuration from a TOML file.

    Parses a TOML configuration file and extracts required and optional parameters
    for the oil spill simulation. Validates all required fields and their values
    before storing them as instance attributes.

    Attributes:
        mesh_file (str): Path to the mesh file (.msh or .vtk format). Required.
        dt (float): Time step size for temporal discretization. Required, must be > 0.
        t_end (float): Final simulation time. Required, must be > 0.
        write_frequency (int, optional): Save output every N steps. Default: None (no output).
        log_name (str, optional): Name of the log file (without extension). Default: "logfile"

    Args:
        filename (str): Path to TOML configuration file.

    Raises:
        FileNotFoundError: If configuration file does not exist.
        ValueError: If required fields are missing or have invalid values.

    Example:
        config = Config("input.toml")
        print(f"Mesh: {config.mesh_file}, dt: {config.dt}, t_end: {config.t_end}")
    """

    def __init__(self, filename: str):
        """
        Initialize Config by reading and validating a TOML file.

        Args:
            filename (str): Path to TOML configuration file.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If validation fails (see _validate method).
        """
        path = Path(filename)

        # Check if configuration file exists
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {filename}")

        # Read TOML file and parse into dictionary
        with open(path, "rb") as f:
            data = tomllib.load(f)
            self.raw = data

        # Extract required fields from config dictionary
        self.mesh_file = data.get("meshName")
        self.borders = data.get("borders")
        self.n_steps = data.get("nSteps")
        self.t_end = data.get("tEnd")

        # Extract optional fields with default values
        self.write_frequency = data.get("writeFrequency", None)
        self.log_name = data.get("logName", "logfile")

        # Validate all configuration values
        self._validate()

        self.dt = self.t_end/self.n_steps

    def _validate(self):
        """
        Validate that all required configuration fields are present and valid.

        Checks:
        - All required fields (meshFile, n_steps, tEnd) are provided
        - dt and tEnd are positive numbers

        Raises:
            ValueError: If any validation check fails.
        """
        # Check that mesh_file is provided
        if self.mesh_file is None:
            raise ValueError("Missing required config entry: meshFile")

        # Check that n_steps is provided
        if self.n_steps is None:
            raise ValueError("Missing required config entry: nSteps")

        # Check that t_end is provided
        if self.t_end is None:
            raise ValueError("Missing required config entry: tEnd")

        # Ensure n_steps is a positive number (number of steps must be positive)
        if self.n_steps <= 0:
            raise ValueError("nSteps must be > 0")

        # Ensure n_steps is an integer
        if not isinstance(self.n_steps, int):
            raise ValueError("nSteps must be an integer")

        # Ensure t_end is a positive number (final time must be positive)
        if self.t_end <= 0:
            raise ValueError("tEnd must be > 0")

        # Check that log_name is provided
        if self.log_name is not None:
            if not isinstance(self.log_name, str) or self.log_name.strip() == "":
                raise ValueError("logName must be a non-empty string")

        if self.borders is None:
            raise ValueError("Missing required config entry: geometry.borders")

        if (
            not isinstance(self.borders, list)
            or len(self.borders) != 2
            or not all(isinstance(v, list) and len(v) == 2 for v in self.borders)
        ):
            raise ValueError("geometry.borders must have format [[x_min, x_max], [y_min, y_max]]")

        x_min, x_max = self.borders[0]
        y_min, y_max = self.borders[1]

        if not (isinstance(x_min, (int, float)) and isinstance(x_max, (int, float))):
            raise ValueError("geometry.borders x-limits must be numbers")
        if not (isinstance(y_min, (int, float)) and isinstance(y_max, (int, float))):
            raise ValueError("geometry.borders y-limits must be numbers")

        if x_min >= x_max or y_min >= y_max:
            raise ValueError("geometry.borders must satisfy x_min < x_max and y_min < y_max")
