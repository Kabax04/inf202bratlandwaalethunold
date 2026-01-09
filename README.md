# INF202 Project

Oil spill simulation in a 2D triangular mesh.

### Authors:

Jonas Okkenhaug Bratland (Kabax04)

Tobias Galteland Wåle (Twaale)

Oscar Wiersdalen Thunold (Oggyboggi)

## Project Plan

### End goal

A python program that can:

- read a .msh file
- represent mesh + cells object oriented
- move oil in time via fluxes
- be run with config (.toml)
- log and visualize results

## Usage

### Requirements

To use this project, ensure you have **Python** installed along with the required dependencies listed in `requirements.txt`. You can install the dependencies using pip:

```bash
pip install -r requirements.txt
```

### Running the program

***WIP: Config file yet implemented.***

***Features are so far testable with included test files.***

## File structure documentation

### Class structure and features (updated continously)

#### Mesh

The `Mesh` class is responsible for reading and representing a finite element mesh from a file. It uses the `meshio` library to support various mesh formats (such as `.msh`). The class stores mesh point coordinates and constructs cell objects (e.g., `Line`, `Triangle`) for each element in the mesh.

**Key attributes:**
- `points`: NumPy array of mesh point coordinates.
- `cells`: List of cell objects (`Line`, `Triangle`, etc.).

**Key methods:**
- `__init__(filename: str)`: Loads the mesh from the specified file.
- `computeNeighbors()`: Computes and assigns neighboring cells for each cell in the mesh.

The class currently supports line and triangle cells. Other cell types are ignored.

---

#### Cell

The abstract base class for mesh cells. Provides common functionality for all cell types.

**Key attributes:**
- `idx`: Integer index of the cell.
- `point_ids`: List of indices of points that define the cell.
- `neighbors`: List of indices of neighboring cells.

**Key methods:**
- `compute_neighbors(cell_list)`: Finds and stores neighboring cells that share two points.
- `__str__()`: Abstract method for string representation (implemented by subclasses).

---

#### Line

Represents a 1D line cell, inheriting from `Cell`.

**Key attributes:**
- Inherits all attributes from `Cell`.

**Key methods:**
- `__str__()`: Returns a string representation of the line cell.

---

#### Triangle

Represents a 2D triangle cell, inheriting from `Cell`. Computes geometric properties on initialization.

**Key attributes:**
- Inherits all attributes from `Cell`.
- `_points`: Array of point coordinates for the mesh.
- `_x_mid`: Centroid (midpoint) of the triangle.
- `_area`: Area of the triangle.

**Key methods:**
- `__init__(point_ids, idx, points)`: Initializes the triangle and computes its centroid and area.
- `x_mid`: Property getter for the centroid.
- `area`: Property getter for the area.
- `__str__()`: Returns a string representation of the triangle cell.

---
***Bratland, Wåle, Thunold***

***NMBU, 2026***