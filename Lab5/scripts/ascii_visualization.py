"""
ASCII visualization utilities for MST algorithms.
"""

from typing import List, Tuple, Dict, Set


def visualize_prim_step(
    n: int,
    in_mst: List[bool],
    edges: List[Tuple[int, int, float]],
    title: str = ""
) -> str:
    """
    Visualize a step of Prim's algorithm.
    
    Shows which nodes are in the MST and the edges connecting them.
    """
    lines = []
    if title:
        lines.append(f"  {title}")
        lines.append("  " + "=" * (len(title)))
    
    mst_nodes = set(i for i in range(n) if in_mst[i])
    
    # Show nodes
    lines.append("  Nodes in MST: ", end="")
    lines[-1] += " ".join(str(i) for i in sorted(mst_nodes)) if mst_nodes else "(none)"
    
    # Show MST edges
    if edges:
        lines.append("  MST edges so far:")
        for u, v, w in edges:
            lines.append(f"    ({u}, {v}) weight={w:.1f}")
    else:
        lines.append("  (No edges yet)")
    
    return "\n".join(lines)


def visualize_kruskal_step(
    edges_considered: int,
    edges_selected: int,
    total_edges: int,
    mst_edges: List[Tuple[int, int, float]],
    components_remaining: int,
    title: str = ""
) -> str:
    """
    Visualize a step of Kruskal's algorithm.
    
    Shows progress through edge sorting and selection.
    """
    lines = []
    if title:
        lines.append(f"  {title}")
        lines.append("  " + "=" * (len(title)))
    
    progress = (edges_selected / max(1, total_edges - 1)) * 100 if total_edges > 1 else 0
    lines.append(f"  Edges considered: {edges_considered}/{total_edges}")
    lines.append(f"  Edges selected: {edges_selected}/{total_edges - 1} ({progress:.0f}%)")
    lines.append(f"  Components remaining: {components_remaining}")
    
    if mst_edges:
        lines.append("  Latest MST edges:")
        for u, v, w in mst_edges[-3:]:  # Show last 3
            lines.append(f"    ({u}, {v}) weight={w:.1f}")
    
    return "\n".join(lines)


def draw_algorithm_diagram(algorithm_name: str) -> str:
    """Draw a simple flowchart diagram for an algorithm."""
    diagrams = {
        "prim": """
  Prim's Algorithm - Greedy Edge Selection
  =========================================
  
  1. Start with arbitrary node
       ↓
  2. Maintain set of nodes in MST
       ↓
  3. Find lightest edge from MST to outside
       ↓
  4. Add that edge and node to MST
       ↓
  5. Repeat until all nodes added
       ↓
  Result: Minimum Spanning Tree
  
  Key Insight: Grows the MST one node at a time,
  always choosing the cheapest option at each step.
        """,
        "kruskal": """
  Kruskal's Algorithm - Greedy Edge Selection
  ============================================
  
  1. Sort all edges by weight (ascending)
       ↓
  2. Initialize union-find structure
       ↓
  3. For each edge in sorted order:
       ├─ If endpoints in different components
       │    ├─ Add edge to MST
       │    └─ Merge components
       └─ Otherwise skip (would create cycle)
       ↓
  4. Repeat until n-1 edges selected
       ↓
  Result: Minimum Spanning Tree
  
  Key Insight: Processes edges globally by weight,
  avoiding cycles using union-find.
        """
    }
    return diagrams.get(algorithm_name, "").strip()


def simple_graph_visualization(
    n: int,
    edges: List[Tuple[int, int, float]],
    mst_edges_set: Set[Tuple[int, int]] = None
) -> str:
    """
    Create a simple ASCII representation of a graph.
    Works well for small graphs (n <= 10).
    """
    if n > 10:
        return f"[Graph with {n} nodes and {len(edges)} edges - too large for ASCII display]"
    
    lines = []
    lines.append("  Graph structure:")
    lines.append("")
    
    # Simple node representation in a circle/line
    positions = [(i, 0) for i in range(n)]
    
    # List edges
    for u, v, w in edges:
        if mst_edges_set and (min(u, v), max(u, v)) in mst_edges_set:
            marker = "*"  # Mark MST edges
        else:
            marker = " "
        lines.append(f"  {marker}({u}--{v}) w={w:.1f}")
    
    return "\n".join(lines)


def print_metrics_summary(
    algorithm_name: str,
    metrics: Dict,
    n: int,
    m: int
) -> str:
    """Print a human-readable summary of algorithm metrics."""
    lines = [f"\n  {algorithm_name.upper()} ALGORITHM METRICS"]
    lines.append("  " + "=" * 40)
    
    if algorithm_name.lower() == "prim":
        if "key_updates" in metrics:
            lines.append(f"  Key updates:       {metrics.get('key_updates', 0)}")
        if "edges_considered" in metrics:
            lines.append(f"  Edges considered:  {metrics.get('edges_considered', 0)}")
        if "nodes_added" in metrics:
            lines.append(f"  Nodes added:       {metrics.get('nodes_added', 0)}/{n}")
        if "heap_operations" in metrics:
            lines.append(f"  Heap operations:   {metrics.get('heap_operations', 0)}")
    
    elif algorithm_name.lower() == "kruskal":
        if "edges_considered" in metrics:
            lines.append(f"  Edges considered:  {metrics.get('edges_considered', 0)}/{m}")
        if "edges_selected" in metrics:
            lines.append(f"  Edges selected:    {metrics.get('edges_selected', 0)}/{n-1}")
        if "uf_operations" in metrics:
            lines.append(f"  UF operations:     {metrics.get('uf_operations', 0)}")
    
    return "\n".join(lines)
