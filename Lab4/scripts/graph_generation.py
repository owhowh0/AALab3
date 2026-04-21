from __future__ import annotations

import random
from typing import List, Tuple

INF = float("inf")


def _add_undirected_edge(adj: List[List[Tuple[int, int]]], matrix: List[List[float]], u: int, v: int, w: int) -> None:
    adj[u].append((v, w))
    adj[v].append((u, w))
    matrix[u][v] = float(w)
    matrix[v][u] = float(w)


def _base_matrix(n: int) -> List[List[float]]:
    matrix = [[INF for _ in range(n)] for _ in range(n)]
    for i in range(n):
        matrix[i][i] = 0.0
    return matrix


def generate_sparse_weighted_graph(
    n: int,
    avg_degree: int = 4,
    weight_range: Tuple[int, int] = (1, 20),
    seed: int | None = None,
) -> Tuple[List[List[Tuple[int, int]]], List[List[float]], int]:
    rng = random.Random(seed)
    matrix = _base_matrix(n)
    adjacency: List[List[Tuple[int, int]]] = [[] for _ in range(n)]

    edges = set()

    # Build a random spanning tree first to guarantee connectivity.
    for node in range(1, n):
        parent = rng.randint(0, node - 1)
        a, b = (parent, node) if parent < node else (node, parent)
        if (a, b) in edges:
            continue
        edges.add((a, b))
        weight = rng.randint(*weight_range)
        _add_undirected_edge(adjacency, matrix, a, b, weight)

    max_edges = n * (n - 1) // 2
    target_edges = min(max_edges, max(n - 1, (n * avg_degree) // 2))

    while len(edges) < target_edges:
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) in edges:
            continue
        edges.add((a, b))
        weight = rng.randint(*weight_range)
        _add_undirected_edge(adjacency, matrix, a, b, weight)

    return adjacency, matrix, len(edges)


def generate_dense_weighted_graph(
    n: int,
    edge_probability: float = 0.65,
    weight_range: Tuple[int, int] = (1, 20),
    seed: int | None = None,
) -> Tuple[List[List[Tuple[int, int]]], List[List[float]], int]:
    rng = random.Random(seed)
    matrix = _base_matrix(n)
    adjacency: List[List[Tuple[int, int]]] = [[] for _ in range(n)]

    edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() <= edge_probability:
                weight = rng.randint(*weight_range)
                _add_undirected_edge(adjacency, matrix, i, j, weight)
                edges += 1

    # Densify connectivity if needed.
    if edges < n - 1:
        for node in range(1, n):
            if matrix[node - 1][node] == INF:
                weight = rng.randint(*weight_range)
                _add_undirected_edge(adjacency, matrix, node - 1, node, weight)
                edges += 1

    return adjacency, matrix, edges
