from pathlib import Path
from floyd_warshall.domain.graph import Graph
from floyd_warshall.domain.graph_reader import GraphReader
from floyd_warshall.infrastructure.networkx_graph import NetworkXGraph


class TextGraphReader(GraphReader):
    """
    Lê um grafo de texto.

    Formatos aceitos:
      VERTICES A B C D
      A B 3
      B C 2

    A linha VERTICES é opcional, mas permite declarar vértices isolados.
    """

    def read(self, source: str) -> Graph:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {source}")

        graph = NetworkXGraph()
        with path.open("r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split()

                if parts[0].upper() == "VERTICES":
                    if len(parts) < 2:
                        raise ValueError(f"Linha {line_number}: declare ao menos um vértice.")
                    for vertex in parts[1:]:
                        graph.add_vertex(vertex)
                    continue

                if len(parts) != 3:
                    raise ValueError(f"Linha {line_number}: esperado 'origem destino peso'.")

                origin, destination, raw_weight = parts
                try:
                    weight = float(raw_weight)
                except ValueError as exc:
                    raise ValueError(f"Linha {line_number}: peso inválido '{raw_weight}'.") from exc

                graph.add_edge(origin, destination, weight)

        if not graph.vertices():
            raise ValueError("O arquivo não contém vértices.")

        return graph
