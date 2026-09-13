from math import inf
from floyd_warshall.domain.shortest_path_result import ShortestPathResult


class ConsoleRenderer:
    def render(self, result: ShortestPathResult) -> None:
        self._print_matrix("Matriz inicial", result.vertices, result.initial_distances)
        print()
        self._print_matrix("Matriz de menores distâncias", result.vertices, result.distances)

    def render_query(self, result: ShortestPathResult, origin: str, destination: str) -> None:
        print()
        print(f"Consulta {origin} -> {destination}")
        distance = result.distance(origin, destination)
        path = result.path(origin, destination)
        if distance == inf or path is None:
            print("Não existe caminho entre os vértices.")
            return
        print(f"Distância: {self._format_number(distance)}")
        print("Caminho: " + " -> ".join(path))

    def _print_matrix(self, title: str, vertices: list[str], matrix: list[list[float]]) -> None:
        print(title)
        width = max(8, max((len(v) for v in vertices), default=1) + 2)
        print("".ljust(width), end="")
        for vertex in vertices:
            print(vertex.rjust(width), end="")
        print()
        for vertex, row in zip(vertices, matrix):
            print(vertex.ljust(width), end="")
            for value in row:
                text = "INF" if value == inf else self._format_number(value)
                print(text.rjust(width), end="")
            print()

    @staticmethod
    def _format_number(value: float) -> str:
        return str(int(value)) if value.is_integer() else str(value)
