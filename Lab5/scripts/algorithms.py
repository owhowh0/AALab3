"""
Minimum Spanning Tree algorithms: Prim's and Kruskal's.
"""

from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
import heapq


@dataclass
class MST:
    """Result of MST computation."""
    edges: List[Tuple[int, int, float]]
    total_weight: float
    metrics: Dict


class UnionFind:
    """Union-Find (Disjoint Set Union) data structure for Kruskal's algorithm."""
    
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.operations = 0
    
    def find(self, x: int) -> int:
        """Find with path compression."""
        self.operations += 1
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """Union by rank. Returns True if union was performed (components were different)."""
        self.operations += 2
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False
        
        self.operations += 1  # for the assignment
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        return True


def prims_algorithm(
    n: int,
    adj_list: Dict[int, List[Tuple[int, float]]]
) -> MST:
    """
    Prim's algorithm for MST using a min-heap.
    
    Args:
        n: Number of nodes
        adj_list: Adjacency list representation {node: [(neighbor, weight), ...]}
    
    Returns:
        MST object with edges and metrics
    """
    in_mst = [False] * n
    mst_edges: List[Tuple[int, int, float]] = []
    total_weight = 0.0
    
    # Metrics
    key_updates = 0
    edges_considered = 0
    nodes_added = 0
    heap_operations = 0
    
    # Min-heap: (weight, node, parent)
    heap: List[Tuple[float, int, int]] = [(0.0, 0, -1)]  # Start from node 0
    
    while heap and nodes_added < n:
        weight, u, parent = heapq.heappop(heap)
        heap_operations += 1
        
        if in_mst[u]:
            continue
        
        in_mst[u] = True
        nodes_added += 1
        
        if parent != -1:
            mst_edges.append((parent, u, weight))
            total_weight += weight
        
        # Explore neighbors
        if u in adj_list:
            for v, w in adj_list[u]:
                edges_considered += 1
                if not in_mst[v]:
                    heapq.heappush(heap, (w, v, u))
                    heap_operations += 1
                    key_updates += 1
    
    return MST(
        edges=mst_edges,
        total_weight=total_weight,
        metrics={
            "key_updates": key_updates,
            "edges_considered": edges_considered,
            "nodes_added": nodes_added,
            "heap_operations": heap_operations,
        }
    )


def kruskal_algorithm(
    n: int,
    edges: List[Tuple[int, int, float]]
) -> MST:
    """
    Kruskal's algorithm for MST using Union-Find.
    
    Args:
        n: Number of nodes
        edges: List of (u, v, weight) tuples
    
    Returns:
        MST object with edges and metrics
    """
    mst_edges: List[Tuple[int, int, float]] = []
    total_weight = 0.0
    
    # Metrics
    edges_considered = 0
    edges_selected = 0
    
    # Sort edges by weight
    sorted_edges = sorted(edges, key=lambda x: x[2])
    
    # Union-Find
    uf = UnionFind(n)
    
    for u, v, w in sorted_edges:
        edges_considered += 1
        
        if uf.union(u, v):
            mst_edges.append((u, v, w))
            total_weight += w
            edges_selected += 1
            
            if edges_selected == n - 1:
                break
    
    return MST(
        edges=mst_edges,
        total_weight=total_weight,
        metrics={
            "edges_considered": edges_considered,
            "edges_selected": edges_selected,
            "uf_operations": uf.operations,
        }
    )


def prims_adjacency_matrix(
    n: int,
    matrix: List[List[float]]
) -> MST:
    """
    Prim's algorithm using adjacency matrix (suitable for dense graphs).
    
    Args:
        n: Number of nodes
        matrix: Adjacency matrix (n x n), with float('inf') for no edge
    
    Returns:
        MST object with edges and metrics
    """
    INF = float('inf')
    in_mst = [False] * n
    key = [INF] * n
    parent = [-1] * n
    mst_edges: List[Tuple[int, int, float]] = []
    total_weight = 0.0
    
    # Metrics
    key_updates = 0
    edges_considered = 0
    
    key[0] = 0.0
    
    for _ in range(n):
        # Find minimum key vertex not in MST
        min_key = INF
        u = -1
        for v in range(n):
            if not in_mst[v] and key[v] < min_key:
                min_key = key[v]
                u = v
        
        if u == -1:
            break
        
        in_mst[u] = True
        if parent[u] != -1:
            mst_edges.append((parent[u], u, key[u]))
            total_weight += key[u]
        
        # Update keys of adjacent vertices
        for v in range(n):
            edges_considered += 1
            if matrix[u][v] != INF and not in_mst[v] and matrix[u][v] < key[v]:
                key[v] = matrix[u][v]
                parent[v] = u
                key_updates += 1
    
    return MST(
        edges=mst_edges,
        total_weight=total_weight,
        metrics={
            "key_updates": key_updates,
            "edges_considered": edges_considered,
        }
    )
