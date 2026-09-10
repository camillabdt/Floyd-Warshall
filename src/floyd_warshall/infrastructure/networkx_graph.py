import networkx as nx
from floyd_warshall.domain.graph import Graph


class NetworkXGraph(Graph):
    """Adapter: NetworkX é usado somente para representar o grafo."""

    def __init__(self) -> None:
        self._graph = nx.DiGraph()

    def vertices(self) -> list[str]:
        return [str(v) for v in self._graph.nodes]

    def edges(self) -> list[tuple[str, str, float]]:
        return [
            (str(origin), str(destination), float(data['weight']))
            for origin, destination, data in self._graph.edges(data=True)
        ]

    def add_vertex(self, vertex: str) -> None:
        self._graph.add_node(vertex)

    def add_edge(self, origin: str, destination: str, weight: float) -> None:
        self._graph.add_edge(origin, destination, weight=float(weight))
