from __future__ import annotations

import heapq
from typing import Any, Dict, List, Tuple

INF = float("inf")


def dijkstra_adjacency_list(graph: List[List[Tuple[int, int]]], source: int = 0) -> Dict[str, Any]:
    n = len(graph)
    dist = [INF] * n
    dist[source] = 0.0

    heap: List[Tuple[float, int]] = [(0.0, source)]
    visited = [False] * n

    relax_attempts = 0
    successful_relaxations = 0
    heap_pushes = 1
    extract_ops = 0

    while heap:
        current_distance, node = heapq.heappop(heap)
        extract_ops += 1
        if visited[node]:
            continue
        visited[node] = True

        if current_distance > dist[node]:
            continue

        for neighbor, weight in graph[node]:
            relax_attempts += 1
            new_distance = current_distance + weight
            if new_distance < dist[neighbor]:
                dist[neighbor] = new_distance
                successful_relaxations += 1
                heapq.heappush(heap, (new_distance, neighbor))
                heap_pushes += 1

    return {
        "distances": dist,
        "relax_attempts": relax_attempts,
        "successful_relaxations": successful_relaxations,
        "iterations": extract_ops,
        "heap_pushes": heap_pushes,
    }


def dijkstra_adjacency_matrix(matrix: List[List[float]], source: int = 0) -> Dict[str, Any]:
    n = len(matrix)
    dist = [INF] * n
    visited = [False] * n
    dist[source] = 0.0

    relax_attempts = 0
    successful_relaxations = 0
    selections = 0

    for _ in range(n):
        best_node = -1
        best_distance = INF
        for node in range(n):
            if not visited[node] and dist[node] < best_distance:
                best_distance = dist[node]
                best_node = node

        if best_node == -1:
            break

        visited[best_node] = True
        selections += 1

        for neighbor in range(n):
            weight = matrix[best_node][neighbor]
            if visited[neighbor] or weight == INF:
                continue
            relax_attempts += 1
            candidate = dist[best_node] + weight
            if candidate < dist[neighbor]:
                dist[neighbor] = candidate
                successful_relaxations += 1

    return {
        "distances": dist,
        "relax_attempts": relax_attempts,
        "successful_relaxations": successful_relaxations,
        "iterations": selections,
    }


def floyd_warshall(matrix: List[List[float]]) -> Dict[str, Any]:
    n = len(matrix)
    dist = [row[:] for row in matrix]

    updates = 0
    checks = 0

    for k in range(n):
        row_k = dist[k]
        for i in range(n):
            dik = dist[i][k]
            if dik == INF:
                continue
            row_i = dist[i]
            for j in range(n):
                if row_k[j] == INF:
                    continue
                checks += 1
                candidate = dik + row_k[j]
                if candidate < row_i[j]:
                    row_i[j] = candidate
                    updates += 1

    return {
        "distances": dist,
        "relax_attempts": checks,
        "successful_relaxations": updates,
        "iterations": n,
    }
