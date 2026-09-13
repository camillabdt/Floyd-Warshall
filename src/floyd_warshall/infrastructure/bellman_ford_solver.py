"""Baseline independente: Bellman-Ford do NetworkX a partir de cada origem."""

from math import inf
import networkx as nx
from floyd_warshall.application.shortest_path_solver import ShortestPathSolver
from floyd_warshall.application.floyd_warshall_solver import NegativeCycleError
from floyd_warshall.domain.shortest_path_result import ShortestPathResult


class BellmanFordSolver(ShortestPathSolver):
    def solve(self, graph):
        vertices = graph.vertices()
        index = {v: i for i, v in enumerate(vertices)}
        n = len(vertices)
        g = nx.DiGraph()
        g.add_nodes_from(vertices)
        g.add_weighted_edges_from(graph.edges())
        distances = [[inf] * n for _ in vertices]
        initial = [[inf] * n for _ in vertices]
        next_vertex = [[None] * n for _ in vertices]
        for i in range(n):
            initial[i][i] = 0.0
        for u, v, w in graph.edges():
            initial[index[u]][index[v]] = min(initial[index[u]][index[v]], w)
        try:
            for i, origin in enumerate(vertices):
                lengths, paths = nx.single_source_bellman_ford(g, origin)
                for target, distance in lengths.items():
                    j = index[target]
                    distances[i][j] = distance
                    if len(paths[target]) > 1:
                        next_vertex[i][j] = index[paths[target][1]]
        except nx.NetworkXUnbounded as exc:
            raise NegativeCycleError("Ciclo de peso negativo detectado pelo baseline.") from exc
        return ShortestPathResult(vertices, initial, distances, next_vertex)
