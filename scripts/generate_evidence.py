"""Gera exemplos reais de relatório e experimento na pasta configurada."""

import csv
import json
import platform
from datetime import date
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


def read_networks(path):
    """Lê a comparação das redes maiores gerada por evaluate_datasets.py, se existir."""
    if not path.exists():
        return None
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source))
    numeric = ["vertices", "edges", "reachable_pairs", "unreachable_pairs"]
    for row in rows:
        for key in numeric:
            row[key] = int(row[key])
        for key in ["execution_time_ms", "baseline_time_ms"]:
            row[key] = float(row[key])
        row["distances_match"] = row["distances_match"] == "True"
    return [
        {
            k: row[k]
            for k in numeric
            + ["dataset", "execution_time_ms", "baseline_time_ms", "distances_match"]
        }
        for row in rows
    ]


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
    rows = benchmark(NetworkXGraph, FloydWarshallSolver())
    with (reports / "complexidade.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    environment = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": {
            name: version(name)
            for name in ["networkx", "streamlit", "plotly", "pandas", "pytest", "python-dotenv"]
        },
    }
    (reports / "ambiente.json").write_text(json.dumps(environment, indent=2))
    exporter = ReportExporter()
    payload = exporter.payload("grafo_exemplo.csv", g, e, comparison)
    # Seções opcionais do relatório final: só entram resultados já medidos.
    payload["complexity"] = rows
    payload["networks"] = read_networks(reports / "comparacao_redes.csv")
    payload["environment"] = environment
    payload["generated_at"] = date.today().isoformat()
    (reports / "relatorio_final.json").write_text(exporter.dumps(payload))
    (reports / "relatorio_final.html").write_text(exporter.render(payload))
    (reports / "caminhos_exemplo.csv").write_text(exporter.to_csv(e))
    PlotlyGraphVisualizer().create(g, ["A", "B", "C", "D"]).write_html(
        reports / "grafo_exemplo.html", include_plotlyjs=True
    )
    print(json.dumps({"comparison": comparison, "benchmark": rows}, indent=2))


if __name__ == "__main__":
    main()
