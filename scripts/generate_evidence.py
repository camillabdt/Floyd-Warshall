"""Gera exemplos reais de relatório e experimento na pasta configurada."""

import csv
import json
import platform
from pathlib import Path
from importlib.metadata import version
from floyd_warshall.config import settings
from floyd_warshall.application.comparison import benchmark, compare
from floyd_warshall.application.evaluation import EvaluationService
from floyd_warshall.application.floyd_warshall_solver import FloydWarshallSolver
from floyd_warshall.infrastructure.bellman_ford_solver import BellmanFordSolver
from floyd_warshall.infrastructure.dataset_manager import DatasetManager
from floyd_warshall.infrastructure.networkx_graph import NetworkXGraph
from floyd_warshall.infrastructure.report_exporter import ReportExporter
from floyd_warshall.infrastructure.plotly_graph_visualizer import PlotlyGraphVisualizer


def main():
    reports = settings.reports_dir
    reports.mkdir(parents=True, exist_ok=True)
    g = DatasetManager(settings.datasets_dir, NetworkXGraph).load("grafo_exemplo.csv")
    e = EvaluationService(FloydWarshallSolver()).evaluate(g)
    comparison = compare(g, FloydWarshallSolver(), BellmanFordSolver())
    if not comparison["distances_match"]:
        raise RuntimeError("Distâncias divergem do baseline em grafo_exemplo.csv.")
    if e.result.distance("A", "D") != 6:
        raise RuntimeError("Distância A -> D deveria ser 6 em grafo_exemplo.csv.")
    exporter = ReportExporter()
    (reports / "relatorio_final.json").write_text(
        exporter.to_json("grafo_exemplo.csv", g, e, comparison)
    )
    (reports / "relatorio_final.html").write_text(
        exporter.to_html("grafo_exemplo.csv", g, e, comparison)
    )
    (reports / "caminhos_exemplo.csv").write_text(exporter.to_csv(e))
    PlotlyGraphVisualizer().create(g, ["A", "B", "C", "D"]).write_html(
        reports / "grafo_exemplo.html", include_plotlyjs=True
    )
    rows = benchmark(NetworkXGraph, FloydWarshallSolver())
    with (reports / "complexidade.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    (reports / "ambiente.json").write_text(
        json.dumps(
            {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "packages": {
                    name: version(name)
                    for name in [
                        "networkx",
                        "streamlit",
                        "plotly",
                        "pandas",
                        "pytest",
                        "python-dotenv",
                    ]
                },
            },
            indent=2,
        )
    )
    print(json.dumps({"comparison": comparison, "benchmark": rows}, indent=2))


if __name__ == "__main__":
    main()
