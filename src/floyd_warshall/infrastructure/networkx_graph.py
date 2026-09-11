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
        self._graph.add_node(vertex)

    def add_edge(
        self,
        origin: str,
        destination: str,
        weight: float,
    ) -> None:
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
            for origin, destination, data
            in self._graph.edges(data=True)
        ]
