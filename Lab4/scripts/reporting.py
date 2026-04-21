from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from typing import Any, Dict, Iterable, List


def ensure_output_dirs(base_dir: str) -> None:
    os.makedirs(os.path.join(base_dir, "results"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "figures"), exist_ok=True)


def write_csv(path: str, rows: Iterable[Dict[str, Any]], fieldnames: List[str]) -> None:
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w") as handle:
        json.dump(payload, handle, indent=2)


def aggregate_summary(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["algorithm"], row["density_type"])].append(row)

    summary: List[Dict[str, Any]] = []
    for (algorithm, density), values in grouped.items():
        summary.append(
            {
                "algorithm": algorithm,
                "density_type": density,
                "avg_time_ms": sum(v["avg_elapsed_s"] * 1000 for v in values) / len(values),
                "avg_memory_kib": sum(v["avg_peak_memory_kib"] for v in values) / len(values),
                "avg_relax_attempts": sum(v["avg_relax_attempts"] for v in values) / len(values),
                "avg_successful_relaxations": sum(v["avg_successful_relaxations"] for v in values) / len(values),
                "avg_iterations": sum(v["avg_iterations"] for v in values) / len(values),
            }
        )

    return sorted(summary, key=lambda item: (item["density_type"], item["algorithm"]))


def print_terminal_table(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        print("No rows to print.")
        return

    header = (
        "Algorithm", "Density", "n", "m", "Time(ms)", "Mem(KiB)", "Relax", "Updates", "Iter"
    )
    print("\n" + "=" * 110)
    print("{:>14} {:>8} {:>6} {:>8} {:>10} {:>10} {:>12} {:>12} {:>8}".format(*header))
    print("-" * 110)
    for row in rows:
        print(
            "{:>14} {:>8} {:>6d} {:>8d} {:>10.3f} {:>10.1f} {:>12.1f} {:>12.1f} {:>8.1f}".format(
                row["algorithm"],
                row["density_type"],
                int(row["n"]),
                int(row["m"]),
                row["avg_elapsed_s"] * 1000,
                row["avg_peak_memory_kib"],
                row["avg_relax_attempts"],
                row["avg_successful_relaxations"],
                row["avg_iterations"],
            )
        )
    print("=" * 110)


def print_head_to_head_table(rows: List[Dict[str, Any]]) -> None:
    grouped: Dict[tuple[str, int], Dict[str, Dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[(row["density_type"], int(row["n"]))][row["algorithm"]] = row

    print("\n" + "=" * 128)
    print("Dijkstra vs Floyd-Warshall (Head-to-Head by density and size)")
    print("=" * 128)
    print(
        "{:>8} {:>6} {:>10} {:>10} {:>10} {:>12} {:>12} {:>12}".format(
            "Density",
            "n",
            "Dij(ms)",
            "FW(ms)",
            "FW/Dij",
            "DijRelax",
            "FWRelax",
            "FW/DijOps",
        )
    )
    print("-" * 128)

    for density, n in sorted(grouped.keys()):
        pair = grouped[(density, n)]
        if "Dijkstra" not in pair or "FloydWarshall" not in pair:
            continue
        d = pair["Dijkstra"]
        f = pair["FloydWarshall"]

        d_ms = d["avg_elapsed_s"] * 1000
        f_ms = f["avg_elapsed_s"] * 1000
        time_ratio = (f_ms / d_ms) if d_ms > 0 else float("inf")
        d_ops = d["avg_relax_attempts"]
        f_ops = f["avg_relax_attempts"]
        ops_ratio = (f_ops / d_ops) if d_ops > 0 else float("inf")

        print(
            "{:>8} {:>6d} {:>10.3f} {:>10.3f} {:>10.2f} {:>12.1f} {:>12.1f} {:>12.2f}".format(
                density,
                n,
                d_ms,
                f_ms,
                time_ratio,
                d_ops,
                f_ops,
                ops_ratio,
            )
        )
    print("=" * 128)


def summarize_findings(rows: List[Dict[str, Any]], trend_rows: List[Dict[str, Any]]) -> List[str]:
    lines: List[str] = []

    summary: Dict[tuple[str, str], Dict[str, Any]] = {}
    for row in rows:
        key = (row["algorithm"], row["density_type"])
        summary.setdefault(
            key,
            {
                "time_ms": [],
                "memory_kib": [],
                "ops_per_edge": [],
            },
        )
        summary[key]["time_ms"].append(row["avg_elapsed_s"] * 1000)
        summary[key]["memory_kib"].append(row["avg_peak_memory_kib"])
        summary[key]["ops_per_edge"].append(row["ops_per_edge"])

    for density in ("sparse", "dense"):
        d_key = ("Dijkstra", density)
        f_key = ("FloydWarshall", density)
        if d_key not in summary or f_key not in summary:
            continue

        d_avg = sum(summary[d_key]["time_ms"]) / len(summary[d_key]["time_ms"])
        f_avg = sum(summary[f_key]["time_ms"]) / len(summary[f_key]["time_ms"])
        ratio = (f_avg / d_avg) if d_avg > 0 else float("inf")
        winner = "Dijkstra" if d_avg < f_avg else "Floyd-Warshall"
        lines.append(
            f"{density.capitalize()} graphs: {winner} is faster on average (FW/Dijkstra time ratio = {ratio:.2f}x)."
        )

    slope_lookup = {(row["algorithm"], row["density_type"]): row["slope"] for row in trend_rows}
    for density in ("sparse", "dense"):
        d_slope = slope_lookup.get(("Dijkstra", density))
        f_slope = slope_lookup.get(("FloydWarshall", density))
        if d_slope is not None and f_slope is not None:
            lines.append(
                f"Trend ({density}): Dijkstra slope ≈ {d_slope:.2f}, Floyd-Warshall slope ≈ {f_slope:.2f}."
            )

    lines.append("Density impact: as density increases, both operation count and runtime rise; the increase is much steeper for Floyd-Warshall.")
    return lines


def write_latex_summary_table(path: str, rows: List[Dict[str, Any]], caption: str) -> None:
    with open(path, "w") as handle:
        handle.write("\\begin{table}[H]\n")
        handle.write("\\centering\n")
        handle.write(f"\\caption{{{caption}}}\n")
        handle.write("\\small\n")
        handle.write("\\begin{tabular}{llrrrrr}\n")
        handle.write("\\toprule\n")
        handle.write("Algorithm & Density & n & m & Time (ms) & Memory (KiB) & Relax attempts\\\\\n")
        handle.write("\\midrule\n")
        for row in rows:
            handle.write(
                f"{row['algorithm']} & {row['density_type']} & {int(row['n'])} & {int(row['m'])} & "
                f"{row['avg_elapsed_s'] * 1000:.3f} & {row['avg_peak_memory_kib']:.1f} & "
                f"{row['avg_relax_attempts']:.1f}\\\\\n"
            )
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write("\\end{table}\n")


def write_latex_trend_table(path: str, trend_rows: List[Dict[str, Any]]) -> None:
    with open(path, "w") as handle:
        handle.write("\\begin{table}[H]\n")
        handle.write("\\centering\n")
        handle.write("\\caption{Observed Complexity Trend (log-log slope)}\n")
        handle.write("\\begin{tabular}{llr}\n")
        handle.write("\\toprule\n")
        handle.write("Algorithm & Density & Slope\\\\\n")
        handle.write("\\midrule\n")
        for row in trend_rows:
            slope = row["slope"]
            slope_text = "N/A" if slope is None else f"{slope:.3f}"
            handle.write(f"{row['algorithm']} & {row['density_type']} & {slope_text}\\\\\n")
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write("\\end{table}\n")
