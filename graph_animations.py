from __future__ import annotations

import csv
from collections import deque
from pathlib import Path
from typing import Deque, Dict, List, Sequence, Tuple

from manim import (
    BLUE_D,
    DOWN,
    FadeIn,
    Graph,
    GREEN_D,
    LEFT,
    ORANGE,
    PI,
    RIGHT,
    Scene,
    Text,
    Transform,
    UP,
    UR,
    VGroup,
    WHITE,
    Write,
    Axes,
    Create,
    Dot,
)

GRAPH_NODE_COUNT = 12
GRAPH_STEPS = (1, 2, 3)
BFS_STEPS = (1, 2, 3)
DFS_STEPS = (3, 2, 1)

UNVISITED_COLOR = "#243B55"
ACTIVE_COLOR = "#F4A261"
VISITED_COLOR = "#2A9D8F"
NEIGHBOR_COLOR = "#90BE6D"
EDGE_COLOR = "#8D99AE"


def build_ring_edges(node_count: int, steps: Sequence[int] = GRAPH_STEPS) -> List[Tuple[int, int]]:
    edges = set()
    for node in range(node_count):
        for step in steps:
            neighbor = (node + step) % node_count
            edges.add(tuple(sorted((node, neighbor))))
    return sorted(edges)


def build_graph(node_count: int = GRAPH_NODE_COUNT) -> Graph:
    labels = {node: Text(str(node), font_size=18, color=WHITE) for node in range(node_count)}
    return Graph(
        vertices=list(range(node_count)),
        edges=build_ring_edges(node_count),
        layout="circular",
        layout_scale=2.8,
        labels=labels,
        vertex_config={
            "radius": 0.16,
            "fill_color": UNVISITED_COLOR,
            "fill_opacity": 1.0,
            "stroke_color": WHITE,
            "stroke_width": 1.5,
        },
        edge_config={
            "stroke_color": EDGE_COLOR,
            "stroke_width": 1.8,
            "stroke_opacity": 0.55,
        },
    )


def compact(values: Sequence[int], max_items: int = 10) -> str:
    if len(values) <= max_items:
        return "[" + ", ".join(str(value) for value in values) + "]"
    preview = ", ".join(str(value) for value in values[:max_items])
    return f"[{preview}, ...]"


def bfs_snapshots(node_count: int, start: int = 0) -> List[Tuple[int, List[int], List[int]]]:
    start_index = start % node_count
    visited = bytearray(node_count)
    queue: Deque[int] = deque([start_index])
    visited[start_index] = 1

    order: List[int] = []
    snapshots: List[Tuple[int, List[int], List[int]]] = []

    while queue:
        node = queue.popleft()
        order.append(node)

        for step in BFS_STEPS:
            neighbor_plus = (node + step) % node_count
            neighbor_minus = (node - step) % node_count

            if not visited[neighbor_plus]:
                visited[neighbor_plus] = 1
                queue.append(neighbor_plus)

            if not visited[neighbor_minus]:
                visited[neighbor_minus] = 1
                queue.append(neighbor_minus)

        snapshots.append((node, list(queue), order.copy()))

    return snapshots


def dfs_snapshots(node_count: int, start: int = 0) -> List[Tuple[int, List[int], List[int]]]:
    start_index = start % node_count
    visited = bytearray(node_count)
    stack: List[int] = [start_index]

    order: List[int] = []
    snapshots: List[Tuple[int, List[int], List[int]]] = []

    while stack:
        node = stack.pop()
        if visited[node]:
            continue

        visited[node] = 1
        order.append(node)

        for step in DFS_STEPS:
            neighbor_plus = (node + step) % node_count
            neighbor_minus = (node - step) % node_count

            if not visited[neighbor_plus]:
                stack.append(neighbor_plus)

            if not visited[neighbor_minus]:
                stack.append(neighbor_minus)

        snapshots.append((node, stack.copy(), order.copy()))

    return snapshots


def load_results(path: Path) -> Dict[int, float]:
    if not path.exists():
        return {}

    data: Dict[int, float] = {}
    with path.open("r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            n_value = int(row["n"])
            avg_time = float(row["avg_time_s"])
            data[n_value] = avg_time
    return data


def load_comparison_data(base_dir: Path) -> Tuple[List[int], List[float], List[float]]:
    bfs_data = load_results(base_dir / "bfs_results.csv")
    dfs_data = load_results(base_dir / "dfs_results.csv")

    common_sizes = sorted(set(bfs_data.keys()) & set(dfs_data.keys()))
    if not common_sizes:
        return [], [], []

    bfs_times = [bfs_data[size] for size in common_sizes]
    dfs_times = [dfs_data[size] for size in common_sizes]
    return common_sizes, bfs_times, dfs_times


class GraphModelScene(Scene):
    def construct(self) -> None:
        title = Text("Implicit Degree-6 Graph", font_size=36).to_edge(UP)
        rule = Text("neighbors(i) = i +/- {1, 2, 3} mod n", font_size=26).next_to(title, DOWN, buff=0.2)
        graph = build_graph()

        self.play(Write(title), FadeIn(rule, shift=DOWN * 0.1))
        self.play(Create(graph), run_time=2.0)

        center = 0
        neighbors = [
            (center + 1) % GRAPH_NODE_COUNT,
            (center - 1) % GRAPH_NODE_COUNT,
            (center + 2) % GRAPH_NODE_COUNT,
            (center - 2) % GRAPH_NODE_COUNT,
            (center + 3) % GRAPH_NODE_COUNT,
            (center - 3) % GRAPH_NODE_COUNT,
        ]

        self.play(graph.vertices[center].animate.set_fill(ACTIVE_COLOR), run_time=0.4)
        self.play(
            *[graph.vertices[node].animate.set_fill(NEIGHBOR_COLOR) for node in neighbors],
            run_time=0.8,
        )
        self.wait(1.0)


class TraversalSceneBase(Scene):
    title_text = "Traversal"
    structure_name = "Frontier"

    def get_snapshots(self) -> List[Tuple[int, List[int], List[int]]]:
        raise NotImplementedError

    def construct(self) -> None:
        graph = build_graph()
        title = Text(self.title_text, font_size=34).to_edge(UP)
        order_text = Text("Order: []", font_size=24).to_edge(DOWN).shift(LEFT * 3.0)
        structure_text = Text(f"{self.structure_name}: []", font_size=24).to_edge(DOWN).shift(RIGHT * 2.6)

        self.play(Write(title))
        self.play(Create(graph), run_time=1.8)
        self.play(FadeIn(order_text), FadeIn(structure_text), run_time=0.5)

        for node, structure, order in self.get_snapshots():
            updated_order = Text(f"Order: {compact(order, max_items=12)}", font_size=24).move_to(order_text)
            updated_structure = Text(
                f"{self.structure_name}: {compact(structure)}",
                font_size=24,
            ).move_to(structure_text)

            self.play(
                Transform(order_text, updated_order),
                Transform(structure_text, updated_structure),
                run_time=0.25,
            )
            self.play(graph.vertices[node].animate.set_fill(ACTIVE_COLOR), run_time=0.18)
            self.play(graph.vertices[node].animate.set_fill(VISITED_COLOR), run_time=0.22)

        self.wait(1.0)


class BFSTraversalScene(TraversalSceneBase):
    title_text = "BFS Traversal (Queue)"
    structure_name = "Queue"

    def get_snapshots(self) -> List[Tuple[int, List[int], List[int]]]:
        return bfs_snapshots(GRAPH_NODE_COUNT, start=0)


class DFSTraversalScene(TraversalSceneBase):
    title_text = "DFS Traversal (Stack)"
    structure_name = "Stack"

    def get_snapshots(self) -> List[Tuple[int, List[int], List[int]]]:
        return dfs_snapshots(GRAPH_NODE_COUNT, start=0)


class BFSvsDFSChartScene(Scene):
    def construct(self) -> None:
        title = Text("Empirical Timing: BFS vs DFS", font_size=34).to_edge(UP)
        self.play(Write(title))

        base_dir = Path(__file__).resolve().parent
        xs, bfs_times, dfs_times = load_comparison_data(base_dir)

        if not xs:
            warning = Text("Missing bfs_results.csv or dfs_results.csv", font_size=28, color=ORANGE)
            self.play(FadeIn(warning))
            self.wait(1.5)
            return

        max_x = max(xs)
        max_y = max(max(bfs_times), max(dfs_times))
        x_step = max(1, int(max_x / 5))
        y_step = max(max_y / 5, 1e-6)

        axes = Axes(
            x_range=[0, max_x * 1.05, x_step],
            y_range=[0, max_y * 1.2, y_step],
            x_length=9.2,
            y_length=4.8,
            tips=False,
            axis_config={"include_numbers": False, "color": WHITE},
        ).to_edge(DOWN, buff=0.6)

        x_label = Text("Number of vertices (n)", font_size=20).next_to(axes.x_axis, DOWN, buff=0.2)
        y_label = Text("Average time (s)", font_size=20).rotate(PI / 2).next_to(axes.y_axis, LEFT, buff=0.35)

        bfs_line = axes.plot_line_graph(
            x_values=xs,
            y_values=bfs_times,
            line_color=BLUE_D,
            add_vertex_dots=True,
            vertex_dot_radius=0.035,
        )
        dfs_line = axes.plot_line_graph(
            x_values=xs,
            y_values=dfs_times,
            line_color=GREEN_D,
            add_vertex_dots=True,
            vertex_dot_radius=0.035,
        )

        bfs_legend = VGroup(Dot(color=BLUE_D, radius=0.06), Text("BFS", font_size=22)).arrange(RIGHT, buff=0.15)
        dfs_legend = VGroup(Dot(color=GREEN_D, radius=0.06), Text("DFS", font_size=22)).arrange(RIGHT, buff=0.15)
        legend = VGroup(bfs_legend, dfs_legend).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UR).shift(DOWN * 0.6)

        delta = abs(bfs_times[-1] - dfs_times[-1])
        summary = Text(
            f"At n={xs[-1]:,}, |BFS-DFS| = {delta:.6f} s",
            font_size=22,
        ).next_to(axes, UP, buff=0.15)

        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=1.2)
        self.play(Create(bfs_line), run_time=1.2)
        self.play(Create(dfs_line), run_time=1.2)
        self.play(FadeIn(legend), FadeIn(summary), run_time=0.8)
        self.wait(1.0)
