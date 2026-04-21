from __future__ import annotations

import time
from typing import List, Tuple

INF = float("inf")


def _clear() -> None:
    print("\033[2J\033[H", end="")


def _pause(step_mode: bool, delay: float) -> None:
    if step_mode:
        input("Press Enter for next step...")
    else:
        time.sleep(delay)


def _format_distances(distances: List[float]) -> str:
    formatted = []
    for value in distances:
        formatted.append("INF" if value == INF else f"{value:.0f}")
    return "[" + ", ".join(formatted) + "]"


def visualize_dijkstra(
    graph: List[List[Tuple[int, int]]], source: int = 0, delay: float = 0.4, step_mode: bool = True
) -> None:
    import heapq

    n = len(graph)
    dist = [INF] * n
    dist[source] = 0.0
    visited = [False] * n
    heap = [(0.0, source)]

    step = 0
    while heap:
        current_dist, node = heapq.heappop(heap)
        if visited[node]:
            continue
        visited[node] = True
        step += 1

        updates = []
        for neighbor, weight in graph[node]:
            candidate = current_dist + weight
            if candidate < dist[neighbor]:
                dist[neighbor] = candidate
                heapq.heappush(heap, (candidate, neighbor))
                updates.append((neighbor, candidate))

        _clear()
        print("DIJKSTRA ASCII VISUALIZATION")
        print("=" * 78)
        print(f"Step: {step}")
        print(f"Current node: {node}, distance: {current_dist:.0f}")
        print(f"Visited: {[idx for idx, ok in enumerate(visited) if ok]}")
        print(f"Distances: {_format_distances(dist)}")
        print(f"Updates this step: {updates if updates else 'none'}")
        print("=" * 78)
        _pause(step_mode, delay)


def _format_matrix(matrix: List[List[float]], max_size: int = 8) -> str:
    n = len(matrix)
    lim = min(n, max_size)
    rows = []
    for i in range(lim):
        rendered = []
        for j in range(lim):
            value = matrix[i][j]
            rendered.append(" INF" if value == INF else f"{int(value):4d}")
        rows.append(" ".join(rendered))
    if n > max_size:
        rows.append("... matrix truncated for readability ...")
    return "\n".join(rows)


def visualize_floyd_warshall(
    matrix: List[List[float]], delay: float = 0.5, step_mode: bool = True
) -> None:
    n = len(matrix)
    dist = [row[:] for row in matrix]

    for k in range(n):
        updates = 0
        changed_cells = []
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[k][j] == INF:
                    continue
                candidate = dist[i][k] + dist[k][j]
                if candidate < dist[i][j]:
                    dist[i][j] = candidate
                    updates += 1
                    if len(changed_cells) < 10:
                        changed_cells.append((i, j, int(candidate)))

        _clear()
        print("FLOYD-WARSHALL ASCII VISUALIZATION")
        print("=" * 78)
        print(f"k iteration: {k + 1}/{n}")
        print(f"Updates in this iteration: {updates}")
        print(f"Sample updated cells: {changed_cells if changed_cells else 'none'}")
        print("Current distance matrix (top-left block):")
        print(_format_matrix(dist))
        print("=" * 78)
        _pause(step_mode, delay)
