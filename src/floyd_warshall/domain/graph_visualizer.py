from abc import ABC, abstractmethod

from floyd_warshall.domain.graph import Graph


class GraphVisualizer(ABC):
    """
    Contrato para componentes responsáveis
    pela visualização de grafos.
    """

    @abstractmethod
    def create(
        self,
        graph: Graph,
        highlighted_path: list[str] | None = None,
    ):
        raise NotImplementedError
