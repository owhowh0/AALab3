"""
Graph generation utilities for MST testing.
"""

import random
from typing import Dict, List, Tuple


def generate_random_graph_adjacency_list(
    n: int,
    edge_prob: float,
    seed: int = None,
    weight_range: Tuple[int, int] = (1, 100)
) -> Tuple[Dict[int, List[Tuple[int, float]]], List[Tuple[int, int, float]]]:
    """
    Generate a random undirected weighted graph.
    
    Args:
        n: Number of nodes
        edge_prob: Probability of an edge existing between any two nodes
        seed: Random seed for reproducibility
        weight_range: Tuple (min, max) for edge weights
    
    Returns:
        Tuple of (adjacency_list, edge_list)
    """
    if seed is not None:
        random.seed(seed)
    
    adj_list: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(n)}
    edge_list: List[Tuple[int, int, float]] = []
    
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                weight = float(random.randint(*weight_range))
                adj_list[u].append((v, weight))
                adj_list[v].append((u, weight))
                edge_list.append((u, v, weight))
    
    return adj_list, edge_list


def generate_sparse_graph(
    n: int,
    seed: int = None,
    avg_degree: int = 4
) -> Tuple[Dict[int, List[Tuple[int, float]]], List[Tuple[int, int, float]]]:
    """
    Generate a sparse graph with controlled average degree.
    
    Args:
        n: Number of nodes
        seed: Random seed
        avg_degree: Target average degree
    
    Returns:
        Tuple of (adjacency_list, edge_list)
    """
    edge_prob = min(1.0, avg_degree / (n - 1))
    return generate_random_graph_adjacency_list(n, edge_prob, seed)


def generate_dense_graph(
    n: int,
    seed: int = None,
    edge_prob: float = 0.65
) -> Tuple[Dict[int, List[Tuple[int, float]]], List[Tuple[int, int, float]]]:
    """
    Generate a dense graph with specified edge probability.
    
    Args:
        n: Number of nodes
        seed: Random seed
        edge_prob: Probability of edge existing
    
    Returns:
        Tuple of (adjacency_list, edge_list)
    """
    return generate_random_graph_adjacency_list(n, edge_prob, seed)


def graph_to_adjacency_matrix(
    n: int,
    edge_list: List[Tuple[int, int, float]]
) -> List[List[float]]:
    """
    Convert edge list to adjacency matrix.
    
    Args:
        n: Number of nodes
        edge_list: List of (u, v, weight) tuples
    
    Returns:
        n x n adjacency matrix (undirected)
    """
    INF = float('inf')
    matrix = [[INF] * n for _ in range(n)]
    
    for i in range(n):
        matrix[i][i] = 0.0
    
    for u, v, w in edge_list:
        matrix[u][v] = min(matrix[u][v], w)  # Handle potential multi-edges
        matrix[v][u] = min(matrix[v][u], w)
    
    return matrix


def graph_stats(
    n: int,
    edge_list: List[Tuple[int, int, float]]
) -> Dict:
    """Compute basic statistics about a graph."""
    m = len(edge_list)
    total_weight = sum(w for _, _, w in edge_list)
    avg_weight = total_weight / m if m > 0 else 0.0
    density = (2 * m) / (n * (n - 1)) if n > 1 else 0.0
    
    return {
        "nodes": n,
        "edges": m,
        "total_weight": total_weight,
        "avg_weight": avg_weight,
        "density": density,
    }
