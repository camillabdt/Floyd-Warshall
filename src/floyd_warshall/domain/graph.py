from abc import ABC, abstractmethod
from collections.abc import Iterable


class Graph(ABC):
    """Abstração mínima de um grafo dirigido e ponderado."""

    @abstractmethod
    def vertices(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def edges(self) -> Iterable[tuple[str, str, float]]:
        raise NotImplementedError

    @abstractmethod
    def add_vertex(self, vertex: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_edge(self, origin: str, destination: str, weight: float) -> None:
        raise NotImplementedError
