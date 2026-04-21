from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_float_series(rows: list[dict[str, str]], key: str) -> list[float]:
    return [float(row[key]) for row in rows]


def to_int_series(rows: list[dict[str, str]], key: str) -> list[int]:
    return [int(row[key]) for row in rows]


def plot_sparse_times(rows: list[dict[str, str]]) -> None:
    n = to_int_series(rows, "n")
    prim = to_float_series(rows, "prim_avg_time_ms")
    kruskal = to_float_series(rows, "kruskal_avg_time_ms")

    plt.figure(figsize=(8.5, 5.2))
    plt.plot(n, prim, marker="o", linewidth=2.0, label="Prim (adj list + heap)")
    plt.plot(n, kruskal, marker="s", linewidth=2.0, label="Kruskal")
    plt.title("Sparse Graphs: Execution Time vs Number of Nodes")
    plt.xlabel("Number of nodes (n)")
    plt.ylabel("Execution time (ms)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "sparse_time_vs_nodes.png", dpi=180)
    plt.close()


def plot_dense_times(rows: list[dict[str, str]]) -> None:
    n = to_int_series(rows, "n")
    prim_heap = to_float_series(rows, "prim_heap_time_ms")
    prim_matrix = to_float_series(rows, "prim_matrix_time_ms")
    kruskal = to_float_series(rows, "kruskal_time_ms")

    plt.figure(figsize=(8.5, 5.2))
    plt.plot(n, prim_heap, marker="o", linewidth=2.0, label="Prim (heap)")
    plt.plot(n, prim_matrix, marker="^", linewidth=2.0, label="Prim (matrix)")
    plt.plot(n, kruskal, marker="s", linewidth=2.0, label="Kruskal")
    plt.title("Dense Graphs: Execution Time vs Number of Nodes")
    plt.xlabel("Number of nodes (n)")
    plt.ylabel("Execution time (ms)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "dense_time_vs_nodes.png", dpi=180)
    plt.close()


def plot_sparse_vs_dense(rows_sparse: list[dict[str, str]], rows_dense: list[dict[str, str]]) -> None:
    n_sparse = to_int_series(rows_sparse, "n")
    prim_sparse = to_float_series(rows_sparse, "prim_avg_time_ms")
    kruskal_sparse = to_float_series(rows_sparse, "kruskal_avg_time_ms")

    n_dense = to_int_series(rows_dense, "n")
    prim_dense = to_float_series(rows_dense, "prim_matrix_time_ms")
    kruskal_dense = to_float_series(rows_dense, "kruskal_time_ms")

    plt.figure(figsize=(8.8, 5.4))
    plt.plot(n_sparse, prim_sparse, marker="o", linestyle="--", linewidth=1.8, label="Prim sparse")
    plt.plot(n_sparse, kruskal_sparse, marker="s", linestyle="--", linewidth=1.8, label="Kruskal sparse")
    plt.plot(n_dense, prim_dense, marker="^", linewidth=2.1, label="Prim dense (matrix)")
    plt.plot(n_dense, kruskal_dense, marker="D", linewidth=2.1, label="Kruskal dense")
    plt.yscale("log")
    plt.title("Sparse vs Dense Regimes: Execution Time Comparison")
    plt.xlabel("Number of nodes (n)")
    plt.ylabel("Execution time (ms, log scale)")
    plt.grid(alpha=0.3, which="both")
    plt.legend(ncol=2)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "sparse_vs_dense_comparison.png", dpi=180)
    plt.close()


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    sparse_rows = read_csv(RESULTS_DIR / "sparse_prim_kruskal.csv")
    dense_rows = read_csv(RESULTS_DIR / "dense_algorithms.csv")

    plot_sparse_times(sparse_rows)
    plot_dense_times(dense_rows)
    plot_sparse_vs_dense(sparse_rows, dense_rows)

    print("Generated figures:")
    print("- sparse_time_vs_nodes.png")
    print("- dense_time_vs_nodes.png")
    print("- sparse_vs_dense_comparison.png")


if __name__ == "__main__":
    main()
