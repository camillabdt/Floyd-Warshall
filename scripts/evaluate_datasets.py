"""Compara todas as redes sintéticas maiores e registra métricas reais."""
import csv
from dataclasses import asdict
from floyd_warshall.application.comparison import compare
from floyd_warshall.application.floyd_warshall_solver import FloydWarshallSolver
from floyd_warshall.infrastructure.bellman_ford_solver import BellmanFordSolver
from floyd_warshall.infrastructure.dataset_manager import DatasetManager
from floyd_warshall.infrastructure.networkx_graph import NetworkXGraph
from floyd_warshall.config import settings


def main():
    manager = DatasetManager(settings.datasets_dir, NetworkXGraph)
    rows=[]
    for name in manager.list_datasets():
        if name.startswith('rede_') and name.endswith('.json'):
            graph=manager.load(name)
            comparison=compare(graph,FloydWarshallSolver(),BellmanFordSolver())
            assert comparison['distances_match'], name
            result=FloydWarshallSolver().solve(graph)
            row={'dataset':name,**comparison['floyd_warshall'],
                 'baseline_time_ms':comparison['bellman_ford']['execution_time_ms'],
                 'distances_match':comparison['distances_match'],
                 'query_source':result.vertices[0],'query_target':result.vertices[-1],
                 'query_distance':result.distance(result.vertices[0],result.vertices[-1]),
                 'query_path':' → '.join(result.path(result.vertices[0],result.vertices[-1]) or [])}
            rows.append(row)
    settings.reports_dir.mkdir(exist_ok=True,parents=True)
    with (settings.reports_dir/'comparacao_redes.csv').open('w',newline='') as output:
        writer=csv.DictWriter(output,fieldnames=rows[0].keys())
        writer.writeheader();writer.writerows(rows)
    for row in rows:
        print(row)


if __name__ == '__main__':
    main()
