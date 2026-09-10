from abc import ABC, abstractmethod
from floyd_warshall.domain.graph import Graph
from floyd_warshall.domain.shortest_path_result import ShortestPathResult


class ShortestPathSolver(ABC):
    @abstractmethod
    def solve(self, graph: Graph) -> ShortestPathResult:
        raise NotImplementedError
