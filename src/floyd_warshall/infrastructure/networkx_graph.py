from math import isfinite
import networkx as nx

from floyd_warshall.domain.graph import Graph


class NetworkXGraph(Graph):
    """
    Implementação concreta de Graph usando NetworkX.

    O NetworkX é utilizado apenas para representar o grafo.
    O cálculo de Floyd-Warshall continua sendo implementado
    pelo próprio projeto.
    """

    def __init__(self) -> None:
        self._graph = nx.DiGraph()

    def add_vertex(self, vertex: str) -> None:
        if not isinstance(vertex, str) or not vertex.strip():
            raise ValueError("Vértice deve ser texto não vazio.")
        self._graph.add_node(vertex)

    def add_edge(
        self,
        origin: str,
        destination: str,
        weight: float,
    ) -> None:
        self.add_vertex(origin)
        self.add_vertex(destination)
        if isinstance(weight, bool) or not isfinite(float(weight)):
            raise ValueError("Peso deve ser numérico e finito.")
        if self._graph.has_edge(origin, destination):
            weight = min(float(weight), self._graph[origin][destination]["weight"])
        self._graph.add_edge(
            origin,
            destination,
            weight=float(weight),
        )

    def vertices(self) -> list[str]:
        return list(self._graph.nodes)

    def edges(self) -> list[tuple[str, str, float]]:
        return [
            (
                str(origin),
                str(destination),
                float(data["weight"]),
            )
            for origin, destination, data in self._graph.edges(data=True)
        ]
