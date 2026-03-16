import csv
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt


def load_results(path: str) -> Dict[int, float]:
    data: Dict[int, float] = {}
    with open(path, "r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            n = int(row["n"])
            avg_time = float(row["avg_time_s"])
            data[n] = avg_time
    return data


def format_time(value: float) -> str:
    return f"{value:.6f}"


def faster_label(bfs_time: float, dfs_time: float) -> str:
    if bfs_time < dfs_time:
        return "BFS"
    if dfs_time < bfs_time:
        return "DFS"
    return "Equal"


def save_table(rows: List[Tuple[int, float, float]], path: str) -> None:
    table_height = max(6.5, 2.0 + 0.35 * len(rows))
    fig, ax = plt.subplots(figsize=(8.5, table_height))
    ax.axis("off")

    cell_text = [
        [
            str(n),
            format_time(bfs_time),
            format_time(dfs_time),
            faster_label(bfs_time, dfs_time),
        ]
        for n, bfs_time, dfs_time in rows
    ]

    table = ax.table(
        cellText=cell_text,
        colLabels=["n", "bfs_avg_time_s", "dfs_avg_time_s", "faster"],
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.1, 1.2)
    fig.tight_layout(pad=0.5)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def save_graph(rows: List[Tuple[int, float, float]], path: str) -> None:
    xs = [n for n, _, _ in rows]
    bfs_ys = [bfs_time for _, bfs_time, _ in rows]
    dfs_ys = [dfs_time for _, _, dfs_time in rows]

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(xs, bfs_ys, marker="o", linewidth=1.5, label="BFS")
    ax.plot(xs, dfs_ys, marker="s", linewidth=1.5, label="DFS")
    ax.set_xlabel("Number of vertices (n)")
    ax.set_ylabel("Average time (s)")
    ax.set_title("BFS vs DFS Performance")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    ax.legend()
    fig.tight_layout(pad=0.5)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    bfs_data = load_results("bfs_results.csv")
    dfs_data = load_results("dfs_results.csv")

    common_sizes = sorted(set(bfs_data.keys()) & set(dfs_data.keys()))
    if not common_sizes:
        raise ValueError("No common input sizes found between BFS and DFS results.")

    rows = [(n, bfs_data[n], dfs_data[n]) for n in common_sizes]

    save_table(rows, "comparison_table.png")
    save_graph(rows, "comparison_graph.png")

    for n, bfs_time, dfs_time in rows:
        label = faster_label(bfs_time, dfs_time)
        print(
            f"{n}: BFS={format_time(bfs_time)} s, "
            f"DFS={format_time(dfs_time)} s, faster={label}"
        )


if __name__ == "__main__":
    main()
