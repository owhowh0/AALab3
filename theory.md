# Theory Notes - BFS and DFS (Lab 3)

## 1. Goal

This lab studies two fundamental graph traversal algorithms:

- Breadth First Search (BFS)
- Depth First Search (DFS)

The objective is to compare them empirically and relate measured results to theoretical complexity.

## 2. Core Idea of Each Algorithm

### BFS

BFS explores a graph level by level from a start vertex.

- Data structure: queue
- Typical use: shortest path in unweighted graphs, level-order exploration

### DFS

DFS explores as deep as possible before backtracking.

- Data structure: stack (iterative) or recursion
- Typical use: connectivity, cycle detection, topological workflows, component exploration

## 3. Complexity (Theory)

For adjacency-style traversal in sparse graphs:

- Time complexity: `O(V + E)`
- Memory complexity: `O(V)` for `visited` plus queue/stack overhead

When average degree is constant, `E` grows linearly with `V`, so runtime trend becomes approximately linear in practice.

## 4. Input Model Used in This Lab

To scale safely up to one million vertices, the graph is represented implicitly.

- Vertices are indexed `0 ... n-1`
- For each vertex `i`, neighbors are:
  - `(i + 1) mod n`, `(i - 1) mod n`
  - `(i + 2) mod n`, `(i - 2) mod n`
  - `(i + 3) mod n`, `(i - 3) mod n`

This gives a connected undirected graph with constant degree 6 for `n > 0`.

## 5. Empirical Method

- Metric: average execution time (seconds)
- Timer: `time.perf_counter()`
- Runs per input size: `5`
- Input sizes: from `1,000` to `1,000,000`
- BFS and DFS run on the same graph model and same size list

This setup isolates traversal behavior and constant-factor differences.

## 6. Edge Cases and Input Rules

Current implementation behavior:

- `n <= 0` -> returns `0` (empty traversal)
- float `n` is supported by normalization: `int(n)`
- float `start` is supported by normalization: `int(start)`
- negative or oversized `start` is normalized with modulo `n`
- non-numeric inputs raise `TypeError`
- booleans are rejected as invalid numeric input

## 7. How to Interpret Results

- Both BFS and DFS should scale near-linearly in this model.
- BFS may be faster in Python due to different constant factors (queue/stack behavior, branch patterns, visitation order).
- The asymptotic class is still the same for both (`O(V + E)`).

## 8. Practical Conclusion

- Use BFS when level-order exploration or shortest path in unweighted graphs is needed.
- Use DFS for deep exploration and structural analyses.
- Choose based on problem goal; use empirical results to compare constant-factor performance for your environment.

## 9. References

1. https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/
2. https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/
3. https://www.youtube.com/watch?v=zaBhtODEL0w