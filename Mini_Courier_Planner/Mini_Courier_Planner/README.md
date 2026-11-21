# Mini-Courier Planner

A beginner-friendly Design & Analysis of Algorithms (DAA) capstone project.

## Features
1. **Merge Sort** prioritizes parcels by higher priority, then earlier deadline.
2. **0/1 Knapsack (Dynamic Programming)** selects the highest-value parcel combination within the vehicle capacity.
3. **Dijkstra's Algorithm** finds shortest paths in a weighted, undirected graph.
4. **Nearest Neighbor TSP Approximation** creates a delivery tour through selected parcel destinations and returns to the depot.
5. **Performance testing** measures algorithm runtimes and saves charts in `charts/`.

## Requirements
- Python 3.9 or newer
- Matplotlib

Install Matplotlib:
```bash
python -m pip install matplotlib
```

## Run the project
Open a terminal in this folder and run:
```bash
python mini_courier_planner.py
```

To skip performance tests:
```bash
python mini_courier_planner.py --no-performance
```

## Project folder
- `mini_courier_planner.py` — complete source code
- `datasets/parcels.csv` — sample parcel data
- `datasets/locations.csv` — road network and distances
- `charts/` — generated runtime charts
- `screenshots/` — add your own screenshots after running the program
- `Project_Report.docx` — project documentation

## Important notes
- The sample data is provided for demonstration. Replace it with your own test data if required.
- Runtime values depend on your computer and should be measured by running the program.
- Nearest Neighbor is an approximation; it does not guarantee the globally shortest TSP tour.
- The graph uses non-negative distances, as required by Dijkstra's algorithm.
