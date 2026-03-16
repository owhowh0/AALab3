# Lab 3 - DFS and BFS Empirical Analysis

This lab contains Python implementations and empirical analysis scripts for:

- Breadth First Search (BFS)
- Depth First Search (DFS)

The scripts generate PNG tables and graphs used by `main.tex`.

## Scripts

- `generate_bfs_results.py`
- `generate_dfs_results.py`
- `generate_comparison_results.py`
- `generate_edge_case_results.py`

Run them in this order:

```bash
python generate_bfs_results.py
python generate_dfs_results.py
python generate_comparison_results.py
python generate_edge_case_results.py
```

Generated assets:

- `bfs_table.png`, `bfs_graph.png`
- `dfs_table.png`, `dfs_graph.png`
- `comparison_table.png`, `comparison_graph.png`
- `edge_cases_table.png`

## Report

After generating PNG assets, compile the report:

```bash
pdflatex main.tex
pdflatex main.tex
```

## Theory Links

1. https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/
2. https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/
3. https://www.youtube.com/watch?v=zaBhtODEL0w