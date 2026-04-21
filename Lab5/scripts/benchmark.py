"""
Benchmarking utilities for MST algorithms.
"""

import gc
import time
import tracemalloc
from statistics import mean, stdev
from typing import Any, Callable, Dict, List
import math


def benchmark_single_run(
    fn: Callable[..., Any], *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    """Run a function once with timing and memory measurements."""
    gc.collect()
    tracemalloc.start()
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed_s = time.perf_counter() - start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return {
        "elapsed_s": elapsed_s,
        "peak_memory_kib": peak_bytes / 1024.0,
        "result": result,
    }


def benchmark_repeated(
    fn: Callable[..., Any],
    repeats: int,
    *args: Any,
    **kwargs: Any
) -> Dict[str, Any]:
    """Run a function multiple times and collect statistics."""
    runs: List[Dict[str, Any]] = []
    
    for _ in range(repeats):
        runs.append(benchmark_single_run(fn, *args, **kwargs))
    
    times = [run["elapsed_s"] for run in runs]
    memories = [run["peak_memory_kib"] for run in runs]
    
    return {
        "avg_elapsed_s": mean(times),
        "avg_peak_memory_kib": mean(memories),
        "min_elapsed_s": min(times),
        "max_elapsed_s": max(times),
        "stdev_elapsed_s": stdev(times) if len(times) > 1 else 0.0,
        "runs": runs,
    }


def loglog_slope(points: List[tuple[int, float]]) -> float:
    """
    Calculate the slope of a log-log fit.
    
    Useful for determining algorithmic complexity from measured data.
    Slope of 1 ≈ O(n), slope of 2 ≈ O(n²), slope of 3 ≈ O(n³), etc.
    """
    filtered = [(x, y) for x, y in points if x > 0 and y > 0]
    if len(filtered) < 2:
        return 0.0
    
    xs = [math.log(x) for x, _ in filtered]
    ys = [math.log(y) for _, y in filtered]
    
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = sum((x - x_mean) ** 2 for x in xs)
    
    if denominator == 0:
        return 0.0
    return numerator / denominator
