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

### Idea for class structure (mockup)

Mesh
- points
- cell
- compute_neighbors()

Cell (abstract)
- id
- point_ids
- neighbors
- \_\_str\_\_()

Triangle (Cell)
- area
- normals
- midpoint

Line (Cell)