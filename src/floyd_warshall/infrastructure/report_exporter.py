"""Serialização de relatórios portáveis, sem dependência da interface."""

from dataclasses import asdict
import csv
from html import escape
from io import StringIO
import json
from math import isfinite

ALGORITHM_RATIONALE = "Floyd-Warshall foi escolhido por calcular todos os pares, permitir matrizes e consultas reutilizáveis e oferecer uma implementação didática com pesos negativos. É adequado à escala demonstrada, mas não é universalmente superior: tempo O(V³) e espaço O(V²) limitam redes grandes. Para poucas origens e pesos não negativos, Dijkstra pode ser mais adequado; para todos os pares em redes esparsas, Johnson merece avaliação. As redes maiores deste projeto são esparsas e positivas. A concordância com Bellman-Ford apoia a correção dos casos testados, mas medições pontuais não demonstram superioridade geral, e Dijkstra e Johnson não foram medidos."


def _spreadsheet_safe(text):
    """Prefixo evita interpretação de rótulos como fórmulas em planilhas."""
    return "'" + text if text.startswith(("=", "+", "-", "@")) else text


class ReportExporter:
    def payload(self, label, graph, evaluation, comparison=None):
        result = evaluation.result
        return {
            "dataset": label,
            "algorithm": "Floyd-Warshall próprio",
            "algorithm_rationale": ALGORITHM_RATIONALE,
            "vertices": result.vertices,
            "edges": list(graph.edges()),
            "metrics": asdict(evaluation.metrics),
            "comparison": comparison,
            "unreachable_value": None,
            "distances": [[v if isfinite(v) else None for v in row] for row in result.distances],
            "paths": [
                {"source": u, "target": v, "path": result.path(u, v)}
                for u in result.vertices
                for v in result.vertices
            ],
        }

    def dumps(self, payload):
        """Serializa um payload, inclusive com seções opcionais adicionadas."""
        return json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)

    def render(self, payload):
        from floyd_warshall.infrastructure.html_report import render_report

        return render_report(payload)

    def to_json(self, label, graph, evaluation, comparison=None):
        return self.dumps(self.payload(label, graph, evaluation, comparison))

    def to_csv(self, evaluation):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["source", "target", "distance", "path"])
        r = evaluation.result
        for u in r.vertices:
            for v in r.vertices:
                distance = r.distance(u, v)
                writer.writerow(
                    [
                        _spreadsheet_safe(u),
                        _spreadsheet_safe(v),
                        distance if isfinite(distance) else "",
                        _spreadsheet_safe(" → ".join(r.path(u, v) or [])),
                    ]
                )
        return output.getvalue()

    def to_html(self, label, graph, evaluation, comparison=None):
        return self.render(self.payload(label, graph, evaluation, comparison))
