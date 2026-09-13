from dataclasses import asdict
from math import isclose
from statistics import median
from time import perf_counter
from floyd_warshall.application.evaluation import EvaluationService


def compare(graph, primary, baseline):
    first = EvaluationService(primary).evaluate(graph)
    second = EvaluationService(baseline).evaluate(graph)
    a, b = first.result, second.result
    matches = all(isclose(a.distance(u, v), b.distance(u, v), rel_tol=1e-9, abs_tol=1e-9)
                  for u in a.vertices for v in a.vertices)
    return {"distances_match": matches, "floyd_warshall": asdict(first.metrics),
            "bellman_ford": asdict(second.metrics)}


def benchmark(graph_factory, solver, sizes=(10, 20, 40, 80), repeats=3):
    """Grafos dirigidos completos determinísticos; mediana sem tracemalloc."""
    rows = []
    for n in sizes:
        graph = graph_factory()
        for i in range(n):
            graph.add_vertex(str(i))
        for i in range(n):
            for j in range(n):
                if i != j:
                    graph.add_edge(str(i), str(j), float(1 + (i * 17 + j * 13) % 20))
        solver.solve(graph)  # aquecimento
        times = []
        for _ in range(repeats):
            start = perf_counter()
            solver.solve(graph)
            times.append((perf_counter() - start) * 1000)
        ms = median(times)
        rows.append({"vertices": n, "edges": n*(n-1), "median_ms": ms,
                     "ms_per_n3": ms / n**3, "repeats": repeats})
    return rows
