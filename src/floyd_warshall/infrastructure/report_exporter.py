"""Serialização de relatórios portáveis, sem dependência da interface."""
from dataclasses import asdict
import csv
from html import escape
from io import StringIO
import json
from math import isfinite


ALGORITHM_RATIONALE = 'Floyd-Warshall foi escolhido por calcular todos os pares, permitir matrizes e consultas reutilizáveis e oferecer uma implementação didática com pesos negativos. É adequado à escala demonstrada, mas não é universalmente superior: tempo O(V³) e espaço O(V²) limitam redes grandes. Para poucas origens e pesos não negativos, Dijkstra pode ser mais adequado; para todos os pares em redes esparsas, Johnson merece avaliação. As redes maiores deste projeto são esparsas e positivas. A concordância com Bellman-Ford apoia a correção dos casos testados, mas medições pontuais não demonstram superioridade geral, e Dijkstra e Johnson não foram medidos.'


class ReportExporter:
    def payload(self, label, graph, evaluation, comparison=None):
        result = evaluation.result
        return {"dataset": label, "algorithm": "Floyd-Warshall próprio",
                "algorithm_rationale": ALGORITHM_RATIONALE,
                "vertices": result.vertices, "edges": list(graph.edges()),
                "metrics": asdict(evaluation.metrics), "comparison": comparison,
                "unreachable_value": None,
                "distances": [[v if isfinite(v) else None for v in row] for row in result.distances],
                "paths": [{"source": u, "target": v, "path": result.path(u, v)}
                          for u in result.vertices for v in result.vertices]}

    def to_json(self, label, graph, evaluation, comparison=None):
        return json.dumps(self.payload(label, graph, evaluation, comparison), ensure_ascii=False,
                          indent=2, allow_nan=False)

    def to_csv(self, evaluation):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["source", "target", "distance", "path"])
        r = evaluation.result
        for u in r.vertices:
            for v in r.vertices:
                # Prefixo evita interpretação de rótulos como fórmulas em planilhas.
                safe = lambda s: "'" + s if s.startswith(("=", "+", "-", "@")) else s
                distance = r.distance(u, v)
                writer.writerow([safe(u), safe(v), distance if isfinite(distance) else "",
                                 safe(" → ".join(r.path(u, v) or []))])
        return output.getvalue()

    def to_html(self, label, graph, evaluation, comparison=None):
        from floyd_warshall.infrastructure.html_report import render_report
        return render_report(self.payload(label, graph, evaluation, comparison))
