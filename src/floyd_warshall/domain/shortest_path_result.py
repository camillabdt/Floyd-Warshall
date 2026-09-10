from dataclasses import dataclass
from math import inf


@dataclass(frozen=True)
class ShortestPathResult:
    vertices: list[str]
    initial_distances: list[list[float]]
    distances: list[list[float]]
    next_vertex: list[list[int | None]]

    def distance(self, origin: str, destination: str) -> float:
        i = self._index(origin)
        j = self._index(destination)
        return self.distances[i][j]

    def path(self, origin: str, destination: str) -> list[str] | None:
        i = self._index(origin)
        j = self._index(destination)
        if i == j:
            return [origin]
        if self.next_vertex[i][j] is None:
            return None
        path = [origin]
        current = i
        while current != j:
            next_index = self.next_vertex[current][j]
            if next_index is None:
                return None
            current = next_index
            path.append(self.vertices[current])
        return path

    def reachable(self, origin: str, destination: str) -> bool:
        return self.distance(origin, destination) != inf

    def _index(self, vertex: str) -> int:
        try:
            return self.vertices.index(vertex)
        except ValueError as exc:
            raise ValueError(f"Vértice inexistente: {vertex}") from exc
