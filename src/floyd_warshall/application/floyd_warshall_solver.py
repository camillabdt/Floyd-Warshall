from math import inf
from floyd_warshall.application.shortest_path_solver import ShortestPathSolver
from floyd_warshall.domain.graph import Graph
from floyd_warshall.domain.shortest_path_result import ShortestPathResult


class NegativeCycleError(RuntimeError):
    pass


class FloydWarshallSolver(ShortestPathSolver):
    """Implementação própria do algoritmo Floyd-Warshall."""

    def solve(self, graph: Graph) -> ShortestPathResult:
        vertices = graph.vertices()
        n = len(vertices)
        index = {vertex: i for i, vertex in enumerate(vertices)}

        dist = [[inf] * n for _ in range(n)]
        next_vertex: list[list[int | None]] = [[None] * n for _ in range(n)]

        for i in range(n):
            dist[i][i] = 0.0

        for origin, destination, weight in graph.edges():
            i = index[origin]
            j = index[destination]
            if weight < dist[i][j]:
                dist[i][j] = float(weight)
                next_vertex[i][j] = j

        initial_distances = [row[:] for row in dist]

        for k in range(n):
            for i in range(n):
                if dist[i][k] == inf:
                    continue
                for j in range(n):
                    if dist[k][j] == inf:
                        continue
                    candidate = dist[i][k] + dist[k][j]
                    if candidate < dist[i][j]:
                        dist[i][j] = candidate
                        next_vertex[i][j] = next_vertex[i][k]

        for i in range(n):
            if dist[i][i] < 0:
                raise NegativeCycleError(
                    f"Ciclo de peso negativo detectado envolvendo '{vertices[i]}'."
                )

        return ShortestPathResult(
            vertices=vertices,
            initial_distances=initial_distances,
            distances=dist,
            next_vertex=next_vertex,
        )
