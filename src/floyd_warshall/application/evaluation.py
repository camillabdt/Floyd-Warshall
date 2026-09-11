from dataclasses import dataclass
from math import inf
from time import perf_counter
import tracemalloc

from floyd_warshall.application.shortest_path_solver import (
    ShortestPathSolver,
)
from floyd_warshall.domain.graph import Graph
from floyd_warshall.domain.shortest_path_result import (
    ShortestPathResult,
)


@dataclass(frozen=True)
class EvaluationMetrics:
    vertices: int
    edges: int
    density: float
    execution_time_ms: float
    peak_memory_kb: float
    reachable_pairs: int
    unreachable_pairs: int
    average_distance: float | None
    minimum_distance: float | None
    maximum_distance: float | None


@dataclass(frozen=True)
class EvaluationResult:
    result: ShortestPathResult
    metrics: EvaluationMetrics


class EvaluationService:
    """
    Executa um algoritmo de caminhos mínimos
    e calcula métricas sobre sua execução.
    """

    def __init__(
        self,
        solver: ShortestPathSolver,
    ) -> None:
        self.solver = solver

    def evaluate(
        self,
        graph: Graph,
    ) -> EvaluationResult:

        number_of_vertices = len(
            graph.vertices()
        )

        number_of_edges = len(
            list(graph.edges())
        )

        # Mede memória usada durante a execução.
        tracemalloc.start()

        start = perf_counter()

        result = self.solver.solve(
            graph
        )

        end = perf_counter()

        _, peak_memory = (
            tracemalloc.get_traced_memory()
        )

        tracemalloc.stop()

        execution_time_ms = (
            (end - start) * 1000
        )

        # Densidade de grafo dirigido.
        if number_of_vertices > 1:
            density = (
                number_of_edges
                / (
                    number_of_vertices
                    * (
                        number_of_vertices
                        - 1
                    )
                )
            ) * 100
        else:
            density = 0.0

        finite_distances = []

        reachable_pairs = 0
        unreachable_pairs = 0

        for i in range(
            number_of_vertices
        ):
            for j in range(
                number_of_vertices
            ):

                # Não contamos o caminho
                # do vértice para ele mesmo.
                if i == j:
                    continue

                distance = (
                    result.distances[i][j]
                )

                if distance == inf:
                    unreachable_pairs += 1
                else:
                    reachable_pairs += 1
                    finite_distances.append(
                        distance
                    )

        if finite_distances:

            average_distance = (
                sum(finite_distances)
                / len(finite_distances)
            )

            minimum_distance = min(
                finite_distances
            )

            maximum_distance = max(
                finite_distances
            )

        else:

            average_distance = None
            minimum_distance = None
            maximum_distance = None

        metrics = EvaluationMetrics(
            vertices=number_of_vertices,
            edges=number_of_edges,
            density=density,
            execution_time_ms=execution_time_ms,
            peak_memory_kb=(
                peak_memory / 1024
            ),
            reachable_pairs=reachable_pairs,
            unreachable_pairs=unreachable_pairs,
            average_distance=average_distance,
            minimum_distance=minimum_distance,
            maximum_distance=maximum_distance,
        )

        return EvaluationResult(
            result=result,
            metrics=metrics,
        )
