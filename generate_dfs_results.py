import csv
import time
from numbers import Real
from typing import List, Tuple

import matplotlib.pyplot as plt

INPUTS: List[int] = [
    1000,
    2000,
    4000,
    6000,
    8000,
    10000,
    12000,
    15000,
    18000,
    20000,
    30000,
    40000,
    60000,
    80000,
    100000,
    120000,
    150000,
    180000,
    200000,
    300000,
    400000,
    600000,
    800000,
    1000000,
]

RUNS = 5
DEGREE_STEPS = (3, 2, 1)


def normalize_node_count(node_count: Real) -> int:
    if isinstance(node_count, bool) or not isinstance(node_count, Real):
        raise TypeError("node_count must be an int or float")
    if node_count <= 0:
        return 0
    return int(node_count)


def normalize_start(start: Real, node_count: int) -> int:
    if isinstance(start, bool) or not isinstance(start, Real):
        raise TypeError("start must be an int or float")
    return int(start) % node_count


def dfs(node_count: Real, start: Real = 0) -> int:
    node_count_int = normalize_node_count(node_count)
    if node_count_int <= 0:
        return 0

    start_int = normalize_start(start, node_count_int)
    visited = bytearray(node_count_int)
    stack = [start_int]
    visited_count = 0

    while stack:
        node = stack.pop()
        if visited[node]:
            continue

        visited[node] = 1
        visited_count += 1

        for step in DEGREE_STEPS:
            neighbor_plus = (node + step) % node_count_int
            neighbor_minus = (node - step) % node_count_int

            if not visited[neighbor_plus]:
                stack.append(neighbor_plus)

            if not visited[neighbor_minus]:
                stack.append(neighbor_minus)

    return visited_count


def measure_times(inputs: List[int], runs: int) -> List[Tuple[int, float]]:
    results: List[Tuple[int, float]] = []

    for n in inputs:
        # Warm-up traversal (not included in timing).
        dfs(n, 0)

        elapsed_sum = 0.0
        for _ in range(runs):
            start = time.perf_counter()
            dfs(n, 0)
            elapsed_sum += time.perf_counter() - start

        results.append((n, elapsed_sum / runs))

    return results


def format_time(value: float) -> str:
    return f"{value:.6f}"


def save_csv(results: List[Tuple[int, float]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["n", "avg_time_s"])
        for n, avg_time in results:
            writer.writerow([n, f"{avg_time:.12f}"])


def save_table(results: List[Tuple[int, float]], path: str) -> None:
    table_height = max(6.5, 2.0 + 0.35 * len(results))
    fig, ax = plt.subplots(figsize=(7.0, table_height))
    ax.axis("off")
    cell_text = [[str(n), format_time(t)] for n, t in results]
    table = ax.table(
        cellText=cell_text,
        colLabels=["n", "avg_time_s"],
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.1, 1.2)
    fig.tight_layout(pad=0.5)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def save_graph(results: List[Tuple[int, float]], path: str) -> None:
    xs = [n for n, _ in results]
    ys = [t for _, t in results]
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.plot(xs, ys, marker="o", linewidth=1.5)
    ax.set_xlabel("Number of vertices (n)")
    ax.set_ylabel("Average time (s)")
    ax.set_title("DFS Performance")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    fig.tight_layout(pad=0.5)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    data = measure_times(INPUTS, RUNS)
    save_csv(data, "dfs_results.csv")
    save_table(data, "dfs_table.png")
    save_graph(data, "dfs_graph.png")
    for n, avg_time in data:
        print(f"{n}: {format_time(avg_time)} s")


if __name__ == "__main__":
    main()
