from dataclasses import dataclass
from math import inf
from time import perf_counter
import tracemalloc

from floyd_warshall.application.shortest_path_solver import ShortestPathSolver
from floyd_warshall.domain.graph import Graph
from floyd_warshall.domain.shortest_path_result import ShortestPathResult


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


@dataclass(frozen=True)
class DistanceSummary:
    """Agregados sobre os pares de vértices distintos."""

    reachable_pairs: int
    unreachable_pairs: int
    average: float | None
    minimum: float | None
    maximum: float | None


class EvaluationService:
    """Executa um algoritmo de caminhos mínimos e calcula métricas sobre sua execução."""

    def __init__(self, solver: ShortestPathSolver) -> None:
        self.solver = solver

    def evaluate(self, graph: Graph) -> EvaluationResult:
        vertices = graph.vertices()
        edges = list(graph.edges())
        # Tempo sem instrumentação; memória em uma segunda execução.
        result, execution_time_ms = self._timed_solve(graph)
        peak_memory = self._peak_memory(graph)
        summary = summarize_distances(result.distances)
        metrics = EvaluationMetrics(
            vertices=len(vertices),
            edges=len(edges),
            density=directed_density(len(vertices), edges),
            execution_time_ms=execution_time_ms,
            peak_memory_kb=peak_memory / 1024,
            reachable_pairs=summary.reachable_pairs,
            unreachable_pairs=summary.unreachable_pairs,
            average_distance=summary.average,
            minimum_distance=summary.minimum,
            maximum_distance=summary.maximum,
        )
        return EvaluationResult(result=result, metrics=metrics)

    def _timed_solve(self, graph: Graph) -> tuple[ShortestPathResult, float]:
        start = perf_counter()
        result = self.solver.solve(graph)
        return result, (perf_counter() - start) * 1000

    def _peak_memory(self, graph: Graph) -> int:
        """Pico de alocações Python em bytes; respeita um rastreamento já ativo."""
        owns_trace = not tracemalloc.is_tracing()
        if owns_trace:
            tracemalloc.start()
        try:
            self.solver.solve(graph)
            _, peak_memory = tracemalloc.get_traced_memory()
        finally:
            if owns_trace:
                tracemalloc.stop()
        return peak_memory


def directed_density(number_of_vertices: int, edges: list[tuple[str, str, float]]) -> float:
    """Densidade dirigida em porcentagem, excluindo laços."""
    if number_of_vertices <= 1:
        return 0.0
    edges_without_loops = sum(u != v for u, v, _ in edges)
    return edges_without_loops / (number_of_vertices * (number_of_vertices - 1)) * 100


def summarize_distances(distances: list[list[float]]) -> DistanceSummary:
    """Conta pares alcançáveis e resume as distâncias finitas, ignorando a diagonal."""
    finite_distances = [
        distance
        for i, row in enumerate(distances)
        for j, distance in enumerate(row)
        if i != j and distance != inf
    ]
    number_of_vertices = len(distances)
    total_pairs = number_of_vertices * (number_of_vertices - 1)
    reachable_pairs = len(finite_distances)
    if not finite_distances:
        return DistanceSummary(reachable_pairs, total_pairs - reachable_pairs, None, None, None)
    return DistanceSummary(
        reachable_pairs=reachable_pairs,
        unreachable_pairs=total_pairs - reachable_pairs,
        average=sum(finite_distances) / reachable_pairs,
        minimum=min(finite_distances),
        maximum=max(finite_distances),
    )
