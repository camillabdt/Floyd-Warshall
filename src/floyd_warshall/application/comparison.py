from dataclasses import asdict
from math import isclose, log
from statistics import median
from time import perf_counter
from floyd_warshall.application.evaluation import EvaluationService


def compare(graph, primary, baseline):
    first = EvaluationService(primary).evaluate(graph)
    second = EvaluationService(baseline).evaluate(graph)
    a, b = first.result, second.result
    matches = all(
        isclose(a.distance(u, v), b.distance(u, v), rel_tol=1e-9, abs_tol=1e-9)
        for u in a.vertices
        for v in a.vertices
    )
    return {
        "distances_match": matches,
        "floyd_warshall": asdict(first.metrics),
        "bellman_ford": asdict(second.metrics),
    }


def scaling_columns(rows):
    """Compara cada linha com a anterior: razão de tempo e expoente log-log.

    Para tempo ~ c·V^k, a razão entre tamanhos dobrados tende a 2^k e a
    inclinação log(t2/t1)/log(n2/n1) tende a k. Ambas ficam None na primeira linha.
    """
    previous = None
    for row in rows:
        row["time_ratio"] = row["loglog_slope"] = None
        if previous and previous["median_ms"] > 0:
            row["time_ratio"] = row["median_ms"] / previous["median_ms"]
            row["loglog_slope"] = log(row["time_ratio"]) / log(
                row["vertices"] / previous["vertices"]
            )
        previous = row
    return rows


def benchmark(graph_factory, solver, sizes=(10, 20, 40, 80, 160, 320), repeats=3):
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
        rows.append(
            {
                "vertices": n,
                "edges": n * (n - 1),
                "median_ms": ms,
                "ms_per_n3": ms / n**3,
                "repeats": repeats,
            }
        )
    return scaling_columns(rows)
