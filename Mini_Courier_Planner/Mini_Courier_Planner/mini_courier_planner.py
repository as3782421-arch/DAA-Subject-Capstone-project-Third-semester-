"""
Mini-Courier Planner
A beginner-friendly DAA capstone project.

Algorithms:
1. Merge Sort: sorts parcels by priority (descending), then deadline (ascending).
2. 0/1 Knapsack: selects parcels with maximum total value within vehicle capacity.
3. Dijkstra: finds shortest paths in a weighted graph.
4. Nearest Neighbor TSP: creates an approximate delivery tour for selected destinations.
5. Performance testing: measures algorithm execution times and saves charts.

Run:
    python mini_courier_planner.py

Optional:
    python mini_courier_planner.py --no-performance
"""

import argparse
import csv
import heapq
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "datasets"
CHART_DIR = ROOT / "charts"

DEFAULT_CAPACITY = 20
DEPOT = "A"


def load_parcels(filename=DATA_DIR / "parcels.csv"):
    parcels = []
    with open(filename, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            parcels.append({
                "id": row["parcel_id"],
                "destination": row["destination"],
                "weight": int(row["weight"]),
                "value": int(row["value"]),
                "priority": int(row["priority"]),
                "deadline": int(row["deadline"]),
            })
    return parcels


def load_graph(filename=DATA_DIR / "locations.csv"):
    graph = {}
    with open(filename, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            source = row["from_location"]
            destination = row["to_location"]
            distance = float(row["distance"])
            graph.setdefault(source, {})[destination] = distance
            graph.setdefault(destination, {})[source] = distance
    return graph


def merge_sort_parcels(parcels):
    """Sort by priority descending; for ties, deadline ascending."""
    if len(parcels) <= 1:
        return parcels[:]

    middle = len(parcels) // 2
    left = merge_sort_parcels(parcels[:middle])
    right = merge_sort_parcels(parcels[middle:])

    result = []
    i = j = 0

    def comes_first(a, b):
        if a["priority"] != b["priority"]:
            return a["priority"] > b["priority"]
        if a["deadline"] != b["deadline"]:
            return a["deadline"] < b["deadline"]
        return a["id"] < b["id"]

    while i < len(left) and j < len(right):
        if comes_first(left[i], right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def knapsack(parcels, capacity):
    """0/1 Knapsack using a 2D dynamic-programming table."""
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        weight = parcels[i - 1]["weight"]
        value = parcels[i - 1]["value"]
        for cap in range(capacity + 1):
            dp[i][cap] = dp[i - 1][cap]
            if weight <= cap:
                dp[i][cap] = max(
                    dp[i][cap],
                    value + dp[i - 1][cap - weight]
                )

    selected = []
    cap = capacity
    for i in range(n, 0, -1):
        if dp[i][cap] != dp[i - 1][cap]:
            parcel = parcels[i - 1]
            selected.append(parcel)
            cap -= parcel["weight"]

    selected.reverse()
    total_weight = sum(p["weight"] for p in selected)
    total_value = sum(p["value"] for p in selected)
    return selected, total_weight, total_value, dp


def dijkstra(graph, start):
    """Return shortest distances and predecessor map from start."""
    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current = heapq.heappop(priority_queue)
        if current_distance != distances[current]:
            continue

        for neighbor, weight in graph[current].items():
            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current
                heapq.heappush(priority_queue, (new_distance, neighbor))

    return distances, previous


def reconstruct_path(previous, destination):
    path = []
    current = destination
    while current is not None:
        path.append(current)
        current = previous[current]
    return list(reversed(path))


def shortest_path(graph, source, destination):
    distances, previous = dijkstra(graph, source)
    if distances[destination] == float("inf"):
        return [], float("inf")
    return reconstruct_path(previous, destination), distances[destination]


def nearest_neighbor_tsp(graph, stops, depot=DEPOT):
    """
    Approximate a tour through the requested stops.
    Shortest-path distances are used between stops.
    """
    stops = list(dict.fromkeys(stops))
    stops = [stop for stop in stops if stop != depot]
    if not stops:
        return [depot, depot], 0.0, []

    all_distances = {}
    all_previous = {}
    for node in graph:
        all_distances[node], all_previous[node] = dijkstra(graph, node)

    unvisited = set(stops)
    current = depot
    tour = [depot]
    legs = []
    total_distance = 0.0

    while unvisited:
        next_stop = min(
            unvisited,
            key=lambda node: all_distances[current][node]
        )
        distance = all_distances[current][next_stop]
        if distance == float("inf"):
            raise ValueError(f"No route from {current} to {next_stop}")

        path = reconstruct_path(all_previous[current], next_stop)
        legs.append((current, next_stop, path, distance))
        total_distance += distance
        tour.append(next_stop)
        current = next_stop
        unvisited.remove(next_stop)

    return_distance = all_distances[current][depot]
    if return_distance == float("inf"):
        raise ValueError(f"No return route from {current} to {depot}")
    return_path = reconstruct_path(all_previous[current], depot)
    legs.append((current, depot, return_path, return_distance))
    total_distance += return_distance
    tour.append(depot)

    return tour, total_distance, legs


def performance_tests():
    """Measure representative execution times and save PNG charts."""
    random.seed(42)
    sizes = [10, 50, 100, 250, 500]
    sort_times = []
    knapsack_times = []
    knapsack_capacity = 100

    for size in sizes:
        sample = []
        for i in range(size):
            sample.append({
                "id": f"X{i}",
                "destination": "B",
                "weight": random.randint(1, 15),
                "value": random.randint(10, 200),
                "priority": random.randint(1, 5),
                "deadline": random.randint(1, 10),
            })

        start = time.perf_counter()
        merge_sort_parcels(sample)
        sort_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        knapsack(sample, knapsack_capacity)
        knapsack_times.append(time.perf_counter() - start)

    graph_sizes = [5, 10, 20, 30, 50]
    dijkstra_times = []
    for count in graph_sizes:
        graph = {f"N{i}": {} for i in range(count)}
        # Connected chain plus a few extra edges.
        for i in range(count - 1):
            a, b = f"N{i}", f"N{i+1}"
            graph[a][b] = 1 + (i % 7)
            graph[b][a] = 1 + (i % 7)
        for i in range(count - 2):
            a, b = f"N{i}", f"N{i+2}"
            graph[a][b] = 3
            graph[b][a] = 3

        start = time.perf_counter()
        dijkstra(graph, "N0")
        dijkstra_times.append(time.perf_counter() - start)

    CHART_DIR.mkdir(exist_ok=True)
    make_chart(sizes, sort_times, "Merge Sort Performance", "Number of parcels",
               "Execution time (seconds)", "merge_sort_performance.png")
    make_chart(sizes, knapsack_times, "0/1 Knapsack Performance", "Number of parcels",
               "Execution time (seconds)", "knapsack_performance.png")
    make_chart(graph_sizes, dijkstra_times, "Dijkstra Performance", "Number of locations",
               "Execution time (seconds)", "dijkstra_performance.png")

    print("\nPERFORMANCE TEST RESULTS")
    print("-" * 70)
    print(f"{'Input size':<15}{'Merge Sort (s)':<20}{'Knapsack (s)':<20}")
    for size, sort_t, dp_t in zip(sizes, sort_times, knapsack_times):
        print(f"{size:<15}{sort_t:<20.8f}{dp_t:<20.8f}")
    print("\nDijkstra:")
    for size, elapsed in zip(graph_sizes, dijkstra_times):
        print(f"{size:>3} locations: {elapsed:.8f} seconds")
    print(f"\nCharts saved in: {CHART_DIR}")


def make_chart(x_values, y_values, title, x_label, y_label, filename):
    plt.figure()
    plt.plot(x_values, y_values, marker="o")
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_DIR / filename, dpi=150)
    plt.close()


def print_parcels(parcels):
    print(f"{'ID':<8}{'Destination':<14}{'Weight':<10}{'Value':<10}{'Priority':<10}{'Deadline':<10}")
    for p in parcels:
        print(f"{p['id']:<8}{p['destination']:<14}{p['weight']:<10}"
              f"{p['value']:<10}{p['priority']:<10}{p['deadline']:<10}")


def main():
    parser = argparse.ArgumentParser(description="Mini-Courier Planner")
    parser.add_argument("--no-performance", action="store_true",
                        help="Skip performance tests and chart generation")
    args = parser.parse_args()

    parcels = load_parcels()
    graph = load_graph()

    print("=" * 65)
    print("                 MINI-COURIER PLANNER")
    print("=" * 65)

    print("\n1. PARCEL PRIORITIZATION - MERGE SORT")
    sorted_parcels = merge_sort_parcels(parcels)
    print_parcels(sorted_parcels)

    print("\n2. PACKAGE SELECTION - 0/1 KNAPSACK")
    selected, total_weight, total_value, dp = knapsack(sorted_parcels, DEFAULT_CAPACITY)
    print(f"Vehicle capacity: {DEFAULT_CAPACITY} kg")
    print("Selected parcels:")
    print_parcels(selected)
    print(f"Total selected weight: {total_weight} kg")
    print(f"Total selected value: {total_value}")

    print("\n3. SHORTEST PATHS - DIJKSTRA")
    distances, previous = dijkstra(graph, DEPOT)
    for location in sorted(graph):
        path = reconstruct_path(previous, location)
        print(f"{DEPOT} to {location}: {' -> '.join(path)} "
              f"(distance: {distances[location]:g})")

    print("\n4. DELIVERY TOUR - NEAREST NEIGHBOR TSP APPROXIMATION")
    destinations = [p["destination"] for p in selected]
    tour, total_distance, legs = nearest_neighbor_tsp(graph, destinations, DEPOT)
    print("Delivery tour:", " -> ".join(tour))
    for source, destination, path, distance in legs:
        print(f"{source} to {destination}: {' -> '.join(path)} "
              f"(distance: {distance:g})")
    print(f"Total tour distance: {total_distance:g}")

    print("\n5. PROJECT SUMMARY")
    print(f"Parcels considered: {len(parcels)}")
    print(f"Parcels selected: {len(selected)}")
    print(f"Total parcel value: {total_value}")
    print(f"Total route distance: {total_distance:g}")

    if not args.no_performance:
        performance_tests()


if __name__ == "__main__":
    main()
