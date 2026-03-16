import csv
from typing import Any, Callable, List, Tuple

import matplotlib.pyplot as plt

from generate_bfs_results import bfs
from generate_dfs_results import dfs

EdgeCase = Tuple[str, Any, Any, str]
ResultRow = Tuple[str, str, str, str, str, str]


EDGE_CASES: List[EdgeCase] = [
    ("negative_n", -5, 0, "Invalid size handled as empty graph"),
    ("zero_n", 0, 0, "Boundary case n=0"),
    ("single_vertex", 1, 0, "Boundary case n=1"),
    ("negative_start", 5, -2, "Negative start is normalized modulo n"),
    ("start_out_of_range", 5, 7, "Out-of-range start is normalized modulo n"),
    ("very_large_start", 5, 1000000000, "Very large start is normalized modulo n"),
    ("two_vertices", 2, 1, "Repeated neighbors are filtered by visited state"),
    ("three_vertices", 3, 2, "Small dense overlap still traverses all vertices"),
    ("float_n", 10.5, 0, "Float n is supported via normalization to int"),
    ("float_start", 10, 3.7, "Float start is supported via normalization to int"),
]


def run_algorithm(algorithm: Callable[[Any, Any], int], n: Any, start: Any) -> str:
    try:
        value = algorithm(n, start)
        return str(value)
    except Exception as exc:  # pragma: no cover - explicit edge-case capture
        return type(exc).__name__


def run_edge_cases() -> List[ResultRow]:
    rows: List[ResultRow] = []
    for case_name, n, start, note in EDGE_CASES:
        bfs_result = run_algorithm(bfs, n, start)
        dfs_result = run_algorithm(dfs, n, start)
        rows.append(
            (
                case_name,
                str(n),
                str(start),
                bfs_result,
                dfs_result,
                note,
            )
        )
    return rows


def save_csv(rows: List[ResultRow], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["case", "n", "start", "bfs_result", "dfs_result", "note"])
        for row in rows:
            writer.writerow(row)


def save_table(rows: List[ResultRow], path: str) -> None:
    table_height = max(5.0, 1.8 + 0.42 * len(rows))
    fig, ax = plt.subplots(figsize=(12.5, table_height))
    ax.axis("off")

    table = ax.table(
        cellText=[list(row) for row in rows],
        colLabels=["case", "n", "start", "bfs", "dfs", "note"],
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.2)
    fig.tight_layout(pad=0.5)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    rows = run_edge_cases()
    save_csv(rows, "edge_case_results.csv")
    save_table(rows, "edge_cases_table.png")

    for case_name, n, start, bfs_result, dfs_result, note in rows:
        print(
            f"{case_name}: n={n}, start={start}, "
            f"BFS={bfs_result}, DFS={dfs_result}, note={note}"
        )


if __name__ == "__main__":
    main()
