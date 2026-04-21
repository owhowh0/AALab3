"""
Main experiment runner for MST algorithms lab.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import math

from algorithms import prims_algorithm, kruskal_algorithm, prims_adjacency_matrix
from graph_generation import (
    generate_sparse_graph,
    generate_dense_graph,
    graph_to_adjacency_matrix,
    graph_stats,
)
from benchmark import benchmark_repeated, loglog_slope
from ascii_visualization import (
    draw_algorithm_diagram,
    print_metrics_summary,
    visualize_prim_step,
)


def format_number(n: float) -> str:
    """Format a number with appropriate units."""
    if n < 1000:
        return f"{n:.2f}"
    elif n < 1e6:
        return f"{n/1000:.2f}K"
    elif n < 1e9:
        return f"{n/1e6:.2f}M"
    else:
        return f"{n/1e9:.2f}B"


def run_experiments(
    output_dir: Path = Path("results"),
    verbose: bool = False
) -> Dict:
    """Run all experiments and collect results."""
    
    output_dir.mkdir(exist_ok=True)
    
    # Test configurations
    sizes_sparse = [10, 20, 30, 50, 75, 100, 150, 200, 300, 400, 500]
    sizes_dense = [10, 20, 30, 50, 75, 100, 150, 200, 250, 300, 350]
    repeats = 3
    
    all_results = {
        "sparse": {
            "prim_adj_list": [],
            "kruskal": [],
        },
        "dense": {
            "prim_heap": [],
            "prim_matrix": [],
            "kruskal": [],
        },
    }
    
    print("\n" + "=" * 70)
    print("MINIMUM SPANNING TREE ALGORITHMS - EXPERIMENTAL ANALYSIS")
    print("=" * 70)
    
    print("\n" + draw_algorithm_diagram("prim"))
    print("\n" + draw_algorithm_diagram("kruskal"))
    
    # ========== SPARSE GRAPHS ==========
    print("\n" + "=" * 70)
    print("SPARSE GRAPHS EXPERIMENTS")
    print("=" * 70)
    
    for n in sizes_sparse:
        seed = n * 100
        adj_list, edge_list = generate_sparse_graph(n, seed=seed, avg_degree=4)
        stats = graph_stats(n, edge_list)
        
        if verbose:
            print(f"\n→ n={n}, m={len(edge_list)}, density={stats['density']:.4f}")
        
        # Prim with adjacency list
        result_prim = benchmark_repeated(
            prims_algorithm, repeats, n=n, adj_list=adj_list
        )
        result_prim["n"] = n
        result_prim["m"] = len(edge_list)
        result_prim["density"] = stats["density"]
        all_results["sparse"]["prim_adj_list"].append(result_prim)
        
        # Kruskal
        result_kruskal = benchmark_repeated(
            kruskal_algorithm, repeats, n=n, edges=edge_list
        )
        result_kruskal["n"] = n
        result_kruskal["m"] = len(edge_list)
        result_kruskal["density"] = stats["density"]
        all_results["sparse"]["kruskal"].append(result_kruskal)
        
        if verbose:
            prim_time = result_prim["avg_elapsed_s"]
            kruskal_time = result_kruskal["avg_elapsed_s"]
            prim_ops = result_prim["runs"][0]["result"].metrics.get("edges_considered", 0)
            kruskal_ops = result_kruskal["runs"][0]["result"].metrics.get("edges_considered", 0)
            print(f"  Prim:    {prim_time*1000:.3f}ms ({prim_ops} edges considered)")
            print(f"  Kruskal: {kruskal_time*1000:.3f}ms ({kruskal_ops} edges considered)")
    
    # ========== DENSE GRAPHS ==========
    print("\n" + "=" * 70)
    print("DENSE GRAPHS EXPERIMENTS")
    print("=" * 70)
    
    for n in sizes_dense:
        seed = n * 200
        adj_list, edge_list = generate_dense_graph(n, seed=seed, edge_prob=0.65)
        matrix = graph_to_adjacency_matrix(n, edge_list)
        stats = graph_stats(n, edge_list)
        
        if verbose:
            print(f"\n→ n={n}, m={len(edge_list)}, density={stats['density']:.4f}")
        
        # Prim with heap (adjacency list)
        result_prim_heap = benchmark_repeated(
            prims_algorithm, repeats, n=n, adj_list=adj_list
        )
        result_prim_heap["n"] = n
        result_prim_heap["m"] = len(edge_list)
        result_prim_heap["density"] = stats["density"]
        all_results["dense"]["prim_heap"].append(result_prim_heap)
        
        # Prim with matrix
        result_prim_matrix = benchmark_repeated(
            prims_adjacency_matrix, repeats, n=n, matrix=matrix
        )
        result_prim_matrix["n"] = n
        result_prim_matrix["m"] = len(edge_list)
        result_prim_matrix["density"] = stats["density"]
        all_results["dense"]["prim_matrix"].append(result_prim_matrix)
        
        # Kruskal
        result_kruskal = benchmark_repeated(
            kruskal_algorithm, repeats, n=n, edges=edge_list
        )
        result_kruskal["n"] = n
        result_kruskal["m"] = len(edge_list)
        result_kruskal["density"] = stats["density"]
        all_results["dense"]["kruskal"].append(result_kruskal)
        
        if verbose:
            prim_heap_time = result_prim_heap["avg_elapsed_s"]
            prim_matrix_time = result_prim_matrix["avg_elapsed_s"]
            kruskal_time = result_kruskal["avg_elapsed_s"]
            print(f"  Prim (heap):   {prim_heap_time*1000:.3f}ms")
            print(f"  Prim (matrix): {prim_matrix_time*1000:.3f}ms")
            print(f"  Kruskal:       {kruskal_time*1000:.3f}ms")
    
    return all_results


def save_csv_results(results: Dict, output_dir: Path):
    """Save benchmark results to CSV files."""
    output_dir.mkdir(exist_ok=True)
    
    # Sparse graphs
    with open(output_dir / "sparse_prim_kruskal.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "n", "m", "density",
            "prim_avg_time_ms", "prim_memory_kib", "prim_edges_considered",
            "kruskal_avg_time_ms", "kruskal_memory_kib", "kruskal_uf_ops"
        ])
        writer.writeheader()
        
        for prim_data, kruskal_data in zip(
            results["sparse"]["prim_adj_list"],
            results["sparse"]["kruskal"]
        ):
            prim_metrics = prim_data["runs"][0]["result"].metrics
            kruskal_metrics = kruskal_data["runs"][0]["result"].metrics
            
            writer.writerow({
                "n": prim_data["n"],
                "m": prim_data["m"],
                "density": f"{prim_data['density']:.4f}",
                "prim_avg_time_ms": f"{prim_data['avg_elapsed_s'] * 1000:.3f}",
                "prim_memory_kib": f"{prim_data['avg_peak_memory_kib']:.2f}",
                "prim_edges_considered": prim_metrics.get("edges_considered", 0),
                "kruskal_avg_time_ms": f"{kruskal_data['avg_elapsed_s'] * 1000:.3f}",
                "kruskal_memory_kib": f"{kruskal_data['avg_peak_memory_kib']:.2f}",
                "kruskal_uf_ops": kruskal_metrics.get("uf_operations", 0),
            })
    
    # Dense graphs
    with open(output_dir / "dense_algorithms.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "n", "m", "density",
            "prim_heap_time_ms", "prim_matrix_time_ms", "kruskal_time_ms",
            "prim_heap_edges_considered", "prim_matrix_key_updates",
            "kruskal_edges_considered", "kruskal_uf_ops"
        ])
        writer.writeheader()
        
        for prim_h, prim_m, kruskal in zip(
            results["dense"]["prim_heap"],
            results["dense"]["prim_matrix"],
            results["dense"]["kruskal"]
        ):
            prim_h_metrics = prim_h["runs"][0]["result"].metrics
            prim_m_metrics = prim_m["runs"][0]["result"].metrics
            kruskal_metrics = kruskal["runs"][0]["result"].metrics
            
            writer.writerow({
                "n": prim_h["n"],
                "m": prim_h["m"],
                "density": f"{prim_h['density']:.4f}",
                "prim_heap_time_ms": f"{prim_h['avg_elapsed_s'] * 1000:.3f}",
                "prim_matrix_time_ms": f"{prim_m['avg_elapsed_s'] * 1000:.3f}",
                "kruskal_time_ms": f"{kruskal['avg_elapsed_s'] * 1000:.3f}",
                "prim_heap_edges_considered": prim_h_metrics.get("edges_considered", 0),
                "prim_matrix_key_updates": prim_m_metrics.get("key_updates", 0),
                "kruskal_edges_considered": kruskal_metrics.get("edges_considered", 0),
                "kruskal_uf_ops": kruskal_metrics.get("uf_operations", 0),
            })
    
    # Summary with complexity analysis
    with open(output_dir / "complexity_analysis.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "regime", "algorithm", "num_points", "avg_loglog_slope",
            "interpretation"
        ])
        writer.writeheader()
        
        # Sparse Prim slope
        sparse_prim_points = [
            (d["n"], d["avg_elapsed_s"]) for d in results["sparse"]["prim_adj_list"]
        ]
        slope_sparse_prim = loglog_slope(sparse_prim_points)
        
        # Sparse Kruskal slope
        sparse_kruskal_points = [
            (d["n"], d["avg_elapsed_s"]) for d in results["sparse"]["kruskal"]
        ]
        slope_sparse_kruskal = loglog_slope(sparse_kruskal_points)
        
        # Dense slopes
        dense_prim_heap_points = [
            (d["n"], d["avg_elapsed_s"]) for d in results["dense"]["prim_heap"]
        ]
        slope_dense_prim_heap = loglog_slope(dense_prim_heap_points)
        
        dense_kruskal_points = [
            (d["n"], d["avg_elapsed_s"]) for d in results["dense"]["kruskal"]
        ]
        slope_dense_kruskal = loglog_slope(dense_kruskal_points)
        
        writer.writerow({
            "regime": "Sparse",
            "algorithm": "Prim (adj list)",
            "num_points": len(sparse_prim_points),
            "avg_loglog_slope": f"{slope_sparse_prim:.2f}",
            "interpretation": "O(E log V) ≈ O(V log V) when E ≈ V"
        })
        writer.writerow({
            "regime": "Sparse",
            "algorithm": "Kruskal",
            "num_points": len(sparse_kruskal_points),
            "avg_loglog_slope": f"{slope_sparse_kruskal:.2f}",
            "interpretation": "O(E log E) ≈ O(V log V) when E ≈ V"
        })
        writer.writerow({
            "regime": "Dense",
            "algorithm": "Prim (heap)",
            "num_points": len(dense_prim_heap_points),
            "avg_loglog_slope": f"{slope_dense_prim_heap:.2f}",
            "interpretation": "O((E + V) log V) ≈ O(V² log V) when E ≈ V²"
        })
        writer.writerow({
            "regime": "Dense",
            "algorithm": "Kruskal",
            "num_points": len(dense_kruskal_points),
            "avg_loglog_slope": f"{slope_dense_kruskal:.2f}",
            "interpretation": "O(E log E) ≈ O(V² log V) when E ≈ V²"
        })


def generate_latex_tables(results: Dict, output_dir: Path):
    """Generate LaTeX table files."""
    output_dir.mkdir(exist_ok=True)
    
    # Sparse comparison table
    table_lines = [
        "\\begin{table}[H]",
        "    \\centering",
        "    \\small",
        "    \\begin{tabular}{|c|c|c|c|c|}",
        "    \\hline",
        "    \\textbf{n} & \\textbf{m} & \\textbf{Prim (ms)} & "
        "\\textbf{Kruskal (ms)} & \\textbf{Speedup} \\\\",
        "    \\hline",
    ]
    
    for prim_data, kruskal_data in zip(
        results["sparse"]["prim_adj_list"],
        results["sparse"]["kruskal"]
    ):
        n = prim_data["n"]
        m = prim_data["m"]
        prim_time = prim_data["avg_elapsed_s"] * 1000
        kruskal_time = kruskal_data["avg_elapsed_s"] * 1000
        speedup = kruskal_time / prim_time if prim_time > 0 else 0
        
        table_lines.append(
            f"    {n:3d} & {m:5d} & {prim_time:7.3f} & {kruskal_time:7.3f} & "
            f"{speedup:5.2f}x \\\\"
        )
    
    table_lines.extend([
        "    \\hline",
        "    \\end{tabular}",
        "    \\caption{Sparse Graphs: Prim vs Kruskal Execution Time}",
        "    \\label{tab:sparse_comparison}",
        "\\end{table}",
    ])
    
    with open(output_dir / "sparse_comparison.tex", "w") as f:
        f.write("\n".join(table_lines))
    
    # Dense comparison table
    table_lines = [
        "\\begin{table}[H]",
        "    \\centering",
        "    \\small",
        "    \\begin{tabular}{|c|c|c|c|c|c|}",
        "    \\hline",
        "    \\textbf{n} & \\textbf{m} & \\textbf{Prim Heap} & "
        "\\textbf{Prim Matrix} & \\textbf{Kruskal} & \\textbf{Best} \\\\",
        "    \\hline",
    ]
    
    for prim_h, prim_m, kruskal in zip(
        results["dense"]["prim_heap"],
        results["dense"]["prim_matrix"],
        results["dense"]["kruskal"]
    ):
        n = prim_h["n"]
        m = prim_h["m"]
        prim_h_time = prim_h["avg_elapsed_s"] * 1000
        prim_m_time = prim_m["avg_elapsed_s"] * 1000
        kruskal_time = kruskal["avg_elapsed_s"] * 1000
        best = min(prim_h_time, prim_m_time, kruskal_time)
        best_alg = (
            "PH" if best == prim_h_time else
            "PM" if best == prim_m_time else
            "K"
        )
        
        table_lines.append(
            f"    {n:3d} & {m:5d} & {prim_h_time:7.3f} & {prim_m_time:7.3f} & "
            f"{kruskal_time:7.3f} & {best_alg} \\\\"
        )
    
    table_lines.extend([
        "    \\hline",
        "    \\end{tabular}",
        "    \\caption{Dense Graphs: Algorithm Comparison "
        "(PH=Prim Heap, PM=Prim Matrix, K=Kruskal)}",
        "    \\label{tab:dense_comparison}",
        "\\end{table}",
    ])
    
    with open(output_dir / "dense_comparison.tex", "w") as f:
        f.write("\n".join(table_lines))
    
    # Complexity analysis table
    table_lines = [
        "\\begin{table}[H]",
        "    \\centering",
        "    \\small",
        "    \\begin{tabular}{|l|l|c|c|}",
        "    \\hline",
        "    \\textbf{Regime} & \\textbf{Algorithm} & "
        "\\textbf{Log-Log Slope} & \\textbf{Theoretical} \\\\",
        "    \\hline",
    ]
    
    sparse_prim_points = [
        (d["n"], d["avg_elapsed_s"]) for d in results["sparse"]["prim_adj_list"]
    ]
    slope_sparse_prim = loglog_slope(sparse_prim_points)
    
    sparse_kruskal_points = [
        (d["n"], d["avg_elapsed_s"]) for d in results["sparse"]["kruskal"]
    ]
    slope_sparse_kruskal = loglog_slope(sparse_kruskal_points)
    
    dense_prim_heap_points = [
        (d["n"], d["avg_elapsed_s"]) for d in results["dense"]["prim_heap"]
    ]
    slope_dense_prim_heap = loglog_slope(dense_prim_heap_points)
    
    dense_kruskal_points = [
        (d["n"], d["avg_elapsed_s"]) for d in results["dense"]["kruskal"]
    ]
    slope_dense_kruskal = loglog_slope(dense_kruskal_points)
    
    table_lines.extend([
        f"    Sparse & Prim (adj list) & {slope_sparse_prim:.2f} & "
        "$O(V \\log V)$ ≈ 1.0 \\\\",
        f"    Sparse & Kruskal & {slope_sparse_kruskal:.2f} & "
        "$O(V \\log V)$ ≈ 1.0 \\\\",
        f"    Dense & Prim (heap) & {slope_dense_prim_heap:.2f} & "
        "$O(V^2 \\log V)$ ≈ 2.0 \\\\",
        f"    Dense & Kruskal & {slope_dense_kruskal:.2f} & "
        "$O(V^2 \\log V)$ ≈ 2.0 \\\\",
        "    \\hline",
        "    \\end{tabular}",
        "    \\caption{Log-Log Slopes for Complexity Analysis}",
        "    \\label{tab:complexity}",
        "\\end{table}",
    ])
    
    with open(output_dir / "complexity_analysis.tex", "w") as f:
        f.write("\n".join(table_lines))


def main():
    """Main entry point."""
    output_dir = Path(__file__).parent.parent / "results"
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print("\n[Running MST Algorithm Experiments]")
    results = run_experiments(output_dir, verbose=verbose)
    
    print("\n[Saving results to CSV]")
    save_csv_results(results, output_dir)
    
    print("[Generating LaTeX tables]")
    generate_latex_tables(results, output_dir)
    
    print(f"\n✓ Experiments completed. Results saved to {output_dir}/")
    print(f"  - sparse_prim_kruskal.csv")
    print(f"  - dense_algorithms.csv")
    print(f"  - complexity_analysis.csv")
    print(f"  - sparse_comparison.tex")
    print(f"  - dense_comparison.tex")
    print(f"  - complexity_analysis.tex")


if __name__ == "__main__":
    main()
