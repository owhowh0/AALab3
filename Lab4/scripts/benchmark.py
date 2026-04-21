from __future__ import annotations

import gc
import time
import tracemalloc
from statistics import mean
from typing import Any, Callable, Dict, List


def benchmark_single_run(fn: Callable[..., Dict[str, Any]], *args: Any, **kwargs: Any) -> Dict[str, Any]:
    gc.collect()
    tracemalloc.start()
    start = time.perf_counter()
    metrics = fn(*args, **kwargs)
    elapsed_s = time.perf_counter() - start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "elapsed_s": elapsed_s,
        "peak_memory_kib": peak_bytes / 1024.0,
        "relax_attempts": metrics.get("relax_attempts", 0),
        "successful_relaxations": metrics.get("successful_relaxations", 0),
        "iterations": metrics.get("iterations", 0),
        "extra": metrics,
    }


def benchmark_repeated(
    fn: Callable[..., Dict[str, Any]], repeats: int, *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    runs: List[Dict[str, Any]] = []

    for _ in range(repeats):
        runs.append(benchmark_single_run(fn, *args, **kwargs))

    return {
        "avg_elapsed_s": mean(run["elapsed_s"] for run in runs),
        "avg_peak_memory_kib": mean(run["peak_memory_kib"] for run in runs),
        "avg_relax_attempts": mean(run["relax_attempts"] for run in runs),
        "avg_successful_relaxations": mean(run["successful_relaxations"] for run in runs),
        "avg_iterations": mean(run["iterations"] for run in runs),
        "runs": runs,
    }


def loglog_slope(points: List[tuple[int, float]]) -> float | None:
    filtered = [(x, y) for x, y in points if x > 0 and y > 0]
    if len(filtered) < 2:
        return None

    xs = [float(__import__("math").log(x)) for x, _ in filtered]
    ys = [float(__import__("math").log(y)) for _, y in filtered]

    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = sum((x - x_mean) ** 2 for x in xs)

    if denominator == 0:
        return None
    return numerator / denominator
