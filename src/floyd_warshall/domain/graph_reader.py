from abc import ABC, abstractmethod
from floyd_warshall.domain.graph import Graph


class GraphReader(ABC):
    @abstractmethod
    def read(self, source: str) -> Graph:
        raise NotImplementedError
