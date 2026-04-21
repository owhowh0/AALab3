#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from collections import defaultdict
from typing import Dict, List

from algorithms import dijkstra_adjacency_list, dijkstra_adjacency_matrix, floyd_warshall
from ascii_visualization import visualize_dijkstra, visualize_floyd_warshall
from benchmark import benchmark_repeated, loglog_slope
from graph_generation import generate_dense_weighted_graph, generate_sparse_weighted_graph
from reporting import (
    aggregate_summary,
    ensure_output_dirs,
    print_head_to_head_table,
    summarize_findings,
    print_terminal_table,
    write_csv,
    write_json,
    write_latex_summary_table,
    write_latex_trend_table,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dynamic Programming Lab: Dijkstra vs Floyd-Warshall")
    parser.add_argument("--sizes", type=str, default="10,20,40,60,80,100,140,180,220,300,400,600,800,1000,1200")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--avg-degree", type=int, default=4)
    parser.add_argument("--dense-prob", type=float, default=0.65)
    parser.add_argument("--max-floyd-n", type=int, default=220)
    parser.add_argument("--visualize", choices=["off", "dijkstra", "floyd", "both"], default="off")
    parser.add_argument("--viz-delay", type=float, default=0.4)
    parser.add_argument("--viz-step", action="store_true")
    parser.add_argument("--no-plots", action="store_true")
    return parser.parse_args()


def maybe_plot(rows: List[Dict[str, float]], base_dir: str, disabled: bool) -> None:
    if disabled:
        return

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not available; skipping PNG plots.")
        return

    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["algorithm"], row["density_type"])].append(row)

    for (algorithm, density), values in grouped.items():
        values = sorted(values, key=lambda v: v["n"])
        ns = [v["n"] for v in values]
        times = [v["avg_elapsed_s"] * 1000 for v in values]
        mems = [v["avg_peak_memory_kib"] for v in values]

        plt.figure(figsize=(7.2, 4.2))
        plt.plot(ns, times, marker="o")
        plt.title(f"{algorithm} Time vs n ({density})")
        plt.xlabel("Number of nodes")
        plt.ylabel("Time (ms)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(base_dir, "figures", f"{algorithm.lower()}_{density}_time.png"), dpi=180)
        plt.close()

        plt.figure(figsize=(7.2, 4.2))
        plt.plot(ns, mems, marker="o", color="tab:green")
        plt.title(f"{algorithm} Memory vs n ({density})")
        plt.xlabel("Number of nodes")
        plt.ylabel("Peak memory (KiB)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(base_dir, "figures", f"{algorithm.lower()}_{density}_memory.png"), dpi=180)
        plt.close()


def main() -> None:
    args = parse_args()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ensure_output_dirs(base_dir)

    sizes = [int(token.strip()) for token in args.sizes.split(",") if token.strip()]
    density_modes = ["sparse", "dense"]

    if args.visualize != "off":
        sample_n = 8
        sparse_adj, sparse_matrix, _ = generate_sparse_weighted_graph(sample_n, avg_degree=3, seed=args.seed)
        if args.visualize in ("dijkstra", "both"):
            visualize_dijkstra(sparse_adj, source=0, delay=args.viz_delay, step_mode=args.viz_step)
        if args.visualize in ("floyd", "both"):
            visualize_floyd_warshall(sparse_matrix, delay=args.viz_delay, step_mode=args.viz_step)

    all_rows: List[Dict[str, float]] = []
    for n in sizes:
        for density in density_modes:
            seed = args.seed + n * (1 if density == "sparse" else 1000)
            if density == "sparse":
                adjacency, matrix, edge_count = generate_sparse_weighted_graph(
                    n=n,
                    avg_degree=args.avg_degree,
                    seed=seed,
                )
            else:
                adjacency, matrix, edge_count = generate_dense_weighted_graph(
                    n=n,
                    edge_probability=args.dense_prob,
                    seed=seed,
                )

            # Use adjacency list on sparse graphs and matrix-based Dijkstra on dense graphs.
            if density == "sparse":
                dijkstra_result = benchmark_repeated(dijkstra_adjacency_list, args.repeats, adjacency, 0)
            else:
                dijkstra_result = benchmark_repeated(dijkstra_adjacency_matrix, args.repeats, matrix, 0)

            all_rows.append(
                {
                    "algorithm": "Dijkstra",
                    "density_type": density,
                    "n": n,
                    "m": edge_count,
                    **{k: v for k, v in dijkstra_result.items() if k != "runs"},
                }
            )

            if n <= args.max_floyd_n:
                floyd_result = benchmark_repeated(floyd_warshall, args.repeats, matrix)
                all_rows.append(
                    {
                        "algorithm": "FloydWarshall",
                        "density_type": density,
                        "n": n,
                        "m": edge_count,
                        **{k: v for k, v in floyd_result.items() if k != "runs"},
                    }
                )

    for row in all_rows:
        relax = max(float(row["avg_relax_attempts"]), 1.0)
        node_count = max(int(row["n"]), 1)
        edge_count = max(int(row["m"]), 1)
        row["update_ratio"] = float(row["avg_successful_relaxations"]) / relax
        row["ops_per_edge"] = float(row["avg_relax_attempts"]) / float(edge_count)
        row["memory_per_node_kib"] = float(row["avg_peak_memory_kib"]) / float(node_count)
        row["time_per_relax_us"] = float(row["avg_elapsed_s"]) * 1_000_000.0 / relax

    all_rows = sorted(all_rows, key=lambda row: (row["density_type"], row["algorithm"], row["n"]))
    print_terminal_table(all_rows)
    print_head_to_head_table(all_rows)

    summary_rows = aggregate_summary(all_rows)

    trend_rows = []
    grouped = defaultdict(list)
    for row in all_rows:
        grouped[(row["algorithm"], row["density_type"])].append(row)
    for (algorithm, density), values in grouped.items():
        points = sorted((int(v["n"]), float(v["avg_elapsed_s"])) for v in values)
        trend_rows.append(
            {
                "algorithm": algorithm,
                "density_type": density,
                "slope": loglog_slope(points),
            }
        )

    result_fields = [
        "algorithm",
        "density_type",
        "n",
        "m",
        "avg_elapsed_s",
        "avg_peak_memory_kib",
        "avg_relax_attempts",
        "avg_successful_relaxations",
        "avg_iterations",
        "update_ratio",
        "ops_per_edge",
        "memory_per_node_kib",
        "time_per_relax_us",
    ]
    summary_fields = [
        "algorithm",
        "density_type",
        "avg_time_ms",
        "avg_memory_kib",
        "avg_relax_attempts",
        "avg_successful_relaxations",
        "avg_iterations",
    ]

    write_csv(os.path.join(base_dir, "results", "benchmark_results.csv"), all_rows, result_fields)
    write_csv(os.path.join(base_dir, "results", "summary_results.csv"), summary_rows, summary_fields)
    write_json(
        os.path.join(base_dir, "results", "benchmark_results.json"),
        {
            "meta": {
                "sizes": sizes,
                "repeats": args.repeats,
                "seed": args.seed,
                "avg_degree": args.avg_degree,
                "dense_prob": args.dense_prob,
                "max_floyd_n": args.max_floyd_n,
            },
            "results": all_rows,
            "summary": summary_rows,
            "trend": trend_rows,
        },
    )

    # Keep table size manageable for PDF by sampling rows.
    latex_rows = [row for row in all_rows if row["n"] in (10, 40, 100, 220, 600, 1000)]
    write_latex_summary_table(
        os.path.join(base_dir, "results", "comparison_table.tex"),
        latex_rows,
        "Dijkstra and Floyd-Warshall Comparison (sampled n values)",
    )
    write_latex_trend_table(os.path.join(base_dir, "results", "trend_table.tex"), trend_rows)

    maybe_plot(all_rows, base_dir, disabled=args.no_plots)

    print("\nFinal Summary")
    print("-" * 60)
    for line in summarize_findings(all_rows, trend_rows):
        print(f"- {line}")
    print("- Floyd-Warshall is measured only up to max_floyd_n due to cubic complexity.")


if __name__ == "__main__":
    main()
