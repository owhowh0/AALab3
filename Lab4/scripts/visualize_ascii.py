#!/usr/bin/env python3

from ascii_visualization import visualize_dijkstra, visualize_floyd_warshall
from graph_generation import generate_sparse_weighted_graph


def main() -> None:
    n = 8
    adjacency, matrix, _ = generate_sparse_weighted_graph(n=n, avg_degree=3, seed=42)

    print("Running Dijkstra visualization on sample sparse graph...")
    visualize_dijkstra(adjacency, source=0, delay=0.35, step_mode=True)

    print("Running Floyd-Warshall visualization on the same graph matrix...")
    visualize_floyd_warshall(matrix, delay=0.4, step_mode=True)


if __name__ == "__main__":
    main()
