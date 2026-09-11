from abc import ABC, abstractmethod
from collections.abc import Iterable


class Graph(ABC):
    """Abstração de um grafo dirigido e ponderado."""

    @abstractmethod
    def add_vertex(self, vertex: str) -> None:
        """Adiciona um vértice ao grafo."""
        raise NotImplementedError

    @abstractmethod
    def add_edge(
        self,
        origin: str,
        destination: str,
        weight: float,
    ) -> None:
        """Adiciona uma aresta ponderada."""
        raise NotImplementedError

    @abstractmethod
    def vertices(self) -> list[str]:
        """Retorna os vértices do grafo."""
        raise NotImplementedError

    @abstractmethod
    def edges(self) -> Iterable[tuple[str, str, float]]:
        """Retorna arestas no formato origem, destino e peso."""
        raise NotImplementedError
