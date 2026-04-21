from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


Edge = Tuple[int, int, float]


@dataclass
class Graph:
    n: int
    edges: List[Edge]
    adj: Dict[int, List[Tuple[int, float]]]


def normalize_edge(u: int, v: int) -> Tuple[int, int]:
    return (u, v) if u <= v else (v, u)


def build_graph(n: int, edges: Iterable[Tuple[int, int, float]]) -> Graph:
    edge_list: List[Edge] = []
    adj: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(n)}

    for u, v, w in edges:
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"Edge ({u}, {v}) is outside node range [0, {n - 1}].")
        if u == v:
            continue
        edge_list.append((u, v, float(w)))
        adj[u].append((v, float(w)))
        adj[v].append((u, float(w)))

    return Graph(n=n, edges=edge_list, adj=adj)


def sample_graphs() -> Dict[str, Graph]:
    samples: Dict[str, Graph] = {}

    samples["triangle"] = build_graph(
        3,
        [
            (0, 1, 4),
            (1, 2, 2),
            (0, 2, 3),
        ],
    )

    samples["sparse6"] = build_graph(
        6,
        [
            (0, 1, 4),
            (0, 2, 3),
            (1, 2, 1),
            (1, 3, 2),
            (2, 3, 4),
            (3, 4, 2),
            (4, 5, 6),
            (3, 5, 3),
        ],
    )

    samples["dense6"] = build_graph(
        6,
        [
            (0, 1, 2),
            (0, 2, 6),
            (0, 3, 5),
            (0, 4, 7),
            (0, 5, 9),
            (1, 2, 3),
            (1, 3, 4),
            (1, 4, 8),
            (1, 5, 7),
            (2, 3, 1),
            (2, 4, 5),
            (2, 5, 4),
            (3, 4, 2),
            (3, 5, 6),
            (4, 5, 3),
        ],
    )

    return samples


def load_graph_from_file(path: Path) -> Graph:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    lines: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)

    if not lines:
        raise ValueError("Input file is empty or contains only comments.")

    first = lines[0].replace(",", " ").split()
    idx = 0
    if len(first) == 2 and all(tok.lstrip("-").isdigit() for tok in first):
        n = int(first[0])
        idx = 1
    else:
        n = -1

    parsed_edges: List[Edge] = []
    max_node = -1
    for line in lines[idx:]:
        parts = line.replace(",", " ").split()
        if len(parts) != 3:
            raise ValueError(
                "Each edge line must have exactly 3 values: u v w (spaces or commas)."
            )
        u = int(parts[0])
        v = int(parts[1])
        w = float(parts[2])
        parsed_edges.append((u, v, w))
        max_node = max(max_node, u, v)

    if n < 0:
        n = max_node + 1

    return build_graph(n, parsed_edges)


def load_graph_manual() -> Graph:
    print("Manual graph input")
    print("Nodes are indexed from 0 to n-1.")
    n = int(input("Number of nodes n: ").strip())
    m = int(input("Number of edges m: ").strip())

    edges: List[Edge] = []
    print("Enter each edge as: u v w")
    for i in range(m):
        while True:
            raw = input(f"Edge {i + 1}/{m}: ").strip().replace(",", " ")
            parts = raw.split()
            if len(parts) != 3:
                print("Invalid format. Expected: u v w")
                continue
            try:
                u = int(parts[0])
                v = int(parts[1])
                w = float(parts[2])
                edges.append((u, v, w))
                break
            except ValueError:
                print("Invalid numeric values. Try again.")

    return build_graph(n, edges)


def render_graph_edge_list(
    graph: Graph,
    mst_edges: List[Edge],
    current_edge: Edge | None = None,
    skipped_edges: set[Tuple[int, int]] | None = None,
) -> str:
    mst_set = {normalize_edge(u, v) for u, v, _ in mst_edges}
    skipped = skipped_edges or set()

    lines = ["Graph edge list:"]
    sorted_edges = sorted(graph.edges, key=lambda e: (e[2], normalize_edge(e[0], e[1])))
    for u, v, w in sorted_edges:
        key = normalize_edge(u, v)
        marker = " "
        if current_edge and key == normalize_edge(current_edge[0], current_edge[1]) and abs(w - current_edge[2]) < 1e-9:
            marker = ">"
        elif key in mst_set:
            marker = "*"
        elif key in skipped:
            marker = "x"
        lines.append(f"  {marker} ({u}, {v}) w={w:.2f}")
    lines.append("Legend: * in MST, > current edge, x skipped")
    return "\n".join(lines)


def render_graph_matrix(graph: Graph, mst_edges: List[Edge]) -> str:
    mst_set = {normalize_edge(u, v) for u, v, _ in mst_edges}
    matrix = [["." for _ in range(graph.n)] for _ in range(graph.n)]
    for u, v, w in graph.edges:
        label = f"{int(w) if float(w).is_integer() else w:g}"
        if normalize_edge(u, v) in mst_set:
            label = f"*{label}"
        matrix[u][v] = label
        matrix[v][u] = label

    lines = ["Graph adjacency matrix (weights, * means edge in MST):"]
    header = "    " + " ".join(f"{j:>4}" for j in range(graph.n))
    lines.append(header)
    for i in range(graph.n):
        row = " ".join(f"{matrix[i][j]:>4}" for j in range(graph.n))
        lines.append(f"{i:>3} {row}")
    return "\n".join(lines)


def best_frontier_for_prim(graph: Graph, in_mst: set[int]) -> Tuple[List[Edge], Dict[int, Tuple[float, int]]]:
    frontier: List[Edge] = []
    best: Dict[int, Tuple[float, int]] = {}

    for u in sorted(in_mst):
        for v, w in graph.adj[u]:
            if v in in_mst:
                continue
            frontier.append((u, v, w))
            if v not in best or w < best[v][0]:
                best[v] = (w, u)

    frontier.sort(key=lambda e: (e[2], e[0], e[1]))
    return frontier, best


def render_prim_state(
    graph: Graph,
    step: int,
    in_mst: set[int],
    mst_edges: List[Edge],
    frontier: List[Edge],
    best: Dict[int, Tuple[float, int]],
    selected: Edge | None,
    show_matrix: bool,
) -> str:
    lines = []
    lines.append("=" * 78)
    lines.append(f"Prim step {step}")
    lines.append("=" * 78)
    lines.append(f"Current MST nodes: {sorted(in_mst)}")
    lines.append(f"Current MST edges: {[ (u, v, round(w, 2)) for (u, v, w) in mst_edges ]}")

    if selected is None:
        lines.append("Selected edge this step: START NODE (no edge yet)")
    else:
        u, v, w = selected
        lines.append(f"Selected minimum edge this step: ({u}, {v}) w={w:.2f}")

    if frontier:
        lines.append("Candidate edges crossing cut (MST -> outside):")
        for u, v, w in frontier:
            lines.append(f"  ({u}, {v}) w={w:.2f}")
    else:
        lines.append("Candidate edges crossing cut: none")

    lines.append("Best known connection weight for each node:")
    for node in range(graph.n):
        if node in in_mst:
            lines.append(f"  node {node}: IN_MST")
        else:
            if node in best:
                weight, parent = best[node]
                lines.append(f"  node {node}: key={weight:.2f}, parent={parent}")
            else:
                lines.append(f"  node {node}: key=inf, parent=-")

    lines.append("")
    lines.append(render_graph_matrix(graph, mst_edges) if show_matrix else render_graph_edge_list(graph, mst_edges, current_edge=selected))
    return "\n".join(lines)


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1
        return True

    def components(self) -> List[List[int]]:
        groups: Dict[int, List[int]] = {}
        for node in range(len(self.parent)):
            root = self.find(node)
            groups.setdefault(root, []).append(node)
        return [sorted(nodes) for nodes in groups.values()]


def render_kruskal_state(
    graph: Graph,
    step: int,
    edge: Edge,
    action: str,
    mst_edges: List[Edge],
    uf: UnionFind,
    sorted_edges: List[Edge],
    edge_index: int,
    skipped_edges: set[Tuple[int, int]],
    show_matrix: bool,
) -> str:
    lines = []
    lines.append("=" * 78)
    lines.append(f"Kruskal step {step}")
    lines.append("=" * 78)
    lines.append(f"Considering edge #{edge_index + 1}/{len(sorted_edges)}: ({edge[0]}, {edge[1]}) w={edge[2]:.2f}")
    lines.append(f"Decision: {action}")
    lines.append(f"Current MST edges: {[ (u, v, round(w, 2)) for (u, v, w) in mst_edges ]}")

    components = uf.components()
    lines.append("Connected components (union-find state):")
    for i, comp in enumerate(sorted(components, key=lambda c: (len(c), c)), start=1):
        lines.append(f"  C{i}: {comp}")

    lines.append("Edges sorted by weight:")
    for idx, (u, v, w) in enumerate(sorted_edges):
        marker = " "
        key = normalize_edge(u, v)
        if idx == edge_index:
            marker = ">"
        elif key in {normalize_edge(a, b) for a, b, _ in mst_edges}:
            marker = "*"
        elif key in skipped_edges:
            marker = "x"
        lines.append(f"  {marker} [{idx + 1:>2}] ({u}, {v}) w={w:.2f}")
    lines.append("Legend: * in MST, > current edge, x skipped")

    lines.append("")
    lines.append(render_graph_matrix(graph, mst_edges) if show_matrix else render_graph_edge_list(graph, mst_edges, current_edge=edge, skipped_edges=skipped_edges))
    return "\n".join(lines)


def wait_control(mode: str, delay: float) -> bool:
    if mode == "auto":
        time.sleep(max(0.0, delay))
        return True

    user = input("Press Enter for next step, or type 'q' to stop: ").strip().lower()
    return user != "q"


def run_prim(graph: Graph, start: int, mode: str, delay: float, show_matrix: bool) -> None:
    if not (0 <= start < graph.n):
        raise ValueError(f"Start node must be in [0, {graph.n - 1}].")

    print("\nRunning Prim step-by-step")

    in_mst: set[int] = {start}
    mst_edges: List[Edge] = []

    frontier, best = best_frontier_for_prim(graph, in_mst)
    print(render_prim_state(graph, step=0, in_mst=in_mst, mst_edges=mst_edges, frontier=frontier, best=best, selected=None, show_matrix=show_matrix))
    if not wait_control(mode, delay):
        return

    step = 1
    while len(in_mst) < graph.n:
        frontier, best = best_frontier_for_prim(graph, in_mst)
        if not frontier:
            print("Graph is disconnected: Prim cannot reach all nodes from this start node.")
            break

        selected = frontier[0]
        u, v, w = selected
        if v in in_mst:
            # Defensive fallback for unexpected duplicate selection orientation.
            for a, b, ww in frontier:
                if a in in_mst and b not in in_mst:
                    u, v, w = a, b, ww
                    selected = (u, v, w)
                    break

        in_mst.add(v)
        mst_edges.append((u, v, w))

        next_frontier, next_best = best_frontier_for_prim(graph, in_mst)
        print(
            render_prim_state(
                graph,
                step=step,
                in_mst=in_mst,
                mst_edges=mst_edges,
                frontier=next_frontier,
                best=next_best,
                selected=selected,
                show_matrix=show_matrix,
            )
        )
        if not wait_control(mode, delay):
            return
        step += 1

    total_weight = sum(w for _, _, w in mst_edges)
    print("\nPrim finished.")
    print(f"MST edges: {[(u, v, round(w, 2)) for u, v, w in mst_edges]}")
    print(f"Total MST weight: {total_weight:.2f}")


def run_kruskal(graph: Graph, mode: str, delay: float, show_matrix: bool) -> None:
    print("\nRunning Kruskal step-by-step")

    uf = UnionFind(graph.n)
    sorted_edges = sorted(graph.edges, key=lambda e: (e[2], normalize_edge(e[0], e[1])))

    mst_edges: List[Edge] = []
    skipped_edges: set[Tuple[int, int]] = set()
    step = 1

    for idx, edge in enumerate(sorted_edges):
        u, v, w = edge
        added = uf.union(u, v)
        if added:
            mst_edges.append(edge)
            action = "ADDED (connects two different components)"
        else:
            skipped_edges.add(normalize_edge(u, v))
            action = "SKIPPED (would create a cycle)"

        print(
            render_kruskal_state(
                graph=graph,
                step=step,
                edge=edge,
                action=action,
                mst_edges=mst_edges,
                uf=uf,
                sorted_edges=sorted_edges,
                edge_index=idx,
                skipped_edges=skipped_edges,
                show_matrix=show_matrix,
            )
        )
        if not wait_control(mode, delay):
            return

        if len(mst_edges) == graph.n - 1:
            break
        step += 1

    if len(mst_edges) < graph.n - 1:
        print("\nGraph is disconnected: Kruskal produced a minimum spanning forest.")
    else:
        print("\nKruskal finished.")

    total_weight = sum(w for _, _, w in mst_edges)
    print(f"MST/forest edges: {[(u, v, round(w, 2)) for u, v, w in mst_edges]}")
    print(f"Total weight: {total_weight:.2f}")


def choose_graph(source: str, sample_name: str, file_path: str | None) -> Graph:
    samples = sample_graphs()

    if source == "sample":
        if sample_name not in samples:
            names = ", ".join(sorted(samples.keys()))
            raise ValueError(f"Unknown sample '{sample_name}'. Available: {names}")
        return samples[sample_name]

    if source == "file":
        if not file_path:
            raise ValueError("--file is required when --source file")
        return load_graph_from_file(Path(file_path))

    if source == "manual":
        return load_graph_manual()

    raise ValueError(f"Unsupported source: {source}")


def interactive_defaults(args: argparse.Namespace) -> argparse.Namespace:
    if args.no_prompt:
        return args

    if args.source == "sample":
        samples = sorted(sample_graphs().keys())
        print("Available sample graphs:")
        for name in samples:
            print(f"  - {name}")

    return args


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ASCII step-by-step visualizer for Prim and Kruskal MST algorithms"
    )
    parser.add_argument("--algorithm", choices=["prim", "kruskal", "both"], default="both")
    parser.add_argument("--source", choices=["sample", "file", "manual"], default="sample")
    parser.add_argument("--sample", default="sparse6")
    parser.add_argument("--file", dest="file_path", default=None)
    parser.add_argument("--mode", choices=["step", "auto"], default="step")
    parser.add_argument("--delay", type=float, default=0.8)
    parser.add_argument("--start", type=int, default=0, help="Start node for Prim")
    parser.add_argument("--matrix", action="store_true", help="Show matrix form instead of edge list")
    parser.add_argument("--no-prompt", action="store_true", help="Skip helper prompts")
    return parser.parse_args()


def print_graph_overview(graph: Graph) -> None:
    density = (2 * len(graph.edges)) / (graph.n * (graph.n - 1)) if graph.n > 1 else 0.0
    print("\n" + "#" * 78)
    print("Graph overview")
    print("#" * 78)
    print(f"Nodes: {graph.n}")
    print(f"Edges: {len(graph.edges)}")
    print(f"Density: {density:.4f}")
    print("Edge list (u, v, w):")
    for u, v, w in sorted(graph.edges, key=lambda e: (e[2], normalize_edge(e[0], e[1]))):
        print(f"  ({u}, {v}, {w:.2f})")


def main() -> None:
    args = parse_args()
    args = interactive_defaults(args)

    graph = choose_graph(args.source, args.sample, args.file_path)
    print_graph_overview(graph)

    if args.algorithm in ("prim", "both"):
        run_prim(graph, start=args.start, mode=args.mode, delay=args.delay, show_matrix=args.matrix)

    if args.algorithm in ("kruskal", "both"):
        run_kruskal(graph, mode=args.mode, delay=args.delay, show_matrix=args.matrix)


if __name__ == "__main__":
    main()
