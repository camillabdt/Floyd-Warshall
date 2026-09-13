import json
import random
from math import inf, isclose
import pytest
from streamlit.testing.v1 import AppTest
from floyd_warshall.application.floyd_warshall_solver import FloydWarshallSolver, NegativeCycleError
from floyd_warshall.application.evaluation import EvaluationService
from floyd_warshall.application.comparison import compare, benchmark
from floyd_warshall.infrastructure.bellman_ford_solver import BellmanFordSolver
from floyd_warshall.infrastructure.networkx_graph import NetworkXGraph
from floyd_warshall.infrastructure.report_exporter import ReportExporter
from floyd_warshall.infrastructure.plotly_graph_visualizer import PlotlyGraphVisualizer


@pytest.mark.parametrize("seed", range(12))
def test_random_graphs_against_independent_baseline(seed):
    rng = random.Random(seed)
    graph = NetworkXGraph()
    for i in range(8):
        graph.add_vertex(str(i))
    # DAG permite pesos negativos sem criar ciclos negativos.
    for i in range(8):
        for j in range(i + 1, 8):
            if rng.random() < 0.5:
                graph.add_edge(str(i), str(j), rng.randint(-5, 9))
    a, b = FloydWarshallSolver().solve(graph), BellmanFordSolver().solve(graph)
    edges = {(u, v): w for u, v, w in graph.edges()}
    for u in a.vertices:
        for v in a.vertices:
            assert isclose(a.distance(u, v), b.distance(u, v))
            path = a.path(u, v)
            if path:
                assert sum(edges[x, y] for x, y in zip(path, path[1:])) == a.distance(u, v)
            else:
                assert a.distance(u, v) == inf


def test_metrics_reports_and_visualizer():
    g = NetworkXGraph()
    g.add_edge("<script>", "B", -2)
    g.add_vertex("Z")
    e = EvaluationService(FloydWarshallSolver()).evaluate(g)
    assert e.metrics.reachable_pairs == 1
    assert e.metrics.unreachable_pairs == 5
    assert e.metrics.minimum_distance == -2
    assert compare(g, FloydWarshallSolver(), BellmanFordSolver())["distances_match"]
    exporter = ReportExporter()
    data = json.loads(exporter.to_json("example", g, e))
    assert data["distances"][0][2] is None
    assert "<script>" not in exporter.to_html("example", g, e)
    assert len(exporter.to_csv(e).splitlines()) == 10
    assert len(PlotlyGraphVisualizer().create(g, ["<script>", "B"]).data) > 0


@pytest.mark.parametrize("solver", [FloydWarshallSolver(), BellmanFordSolver()])
def test_negative_self_loop_and_disconnected_cycle(solver):
    g = NetworkXGraph()
    g.add_vertex("A")
    g.add_edge("Z", "Z", -1)
    with pytest.raises(NegativeCycleError):
        solver.solve(g)


def test_empty_and_single_vertex():
    g = NetworkXGraph()
    assert FloydWarshallSolver().solve(g).vertices == []
    g.add_vertex("A")
    e = EvaluationService(FloydWarshallSolver()).evaluate(g)
    assert e.result.path("A", "A") == ["A"]
    assert e.metrics.average_distance is None


def test_benchmark():
    rows = benchmark(NetworkXGraph, FloydWarshallSolver(), sizes=(3, 6), repeats=2)
    assert [r["edges"] for r in rows] == [6, 30]
    assert all(r["median_ms"] > 0 for r in rows)


def test_app_flow_and_dataset_change():
    app = AppTest.from_file("../app.py", default_timeout=30).run()
    app.sidebar.selectbox[0].select("grafo_exemplo.csv").run()
    next(b for b in app.button if b.label == "Executar análise").click().run()
    assert not app.exception
    assert app.session_state["evaluation"].result.distance("A", "D") == 6
    next(b for b in app.button if b.label == "Comparar com baseline").click().run()
    assert app.session_state["comparison"]["distances_match"]
    app.sidebar.selectbox[0].select("grafo_desconexo.json").run()
    assert "evaluation" not in app.session_state
    next(b for b in app.button if b.label == "Executar análise").click().run()
    assert not app.exception
    assert "Z" in app.session_state["evaluation"].result.vertices


def test_app_negative_cycle_clears_previous_result():
    app = AppTest.from_file("../app.py", default_timeout=30).run()
    app.sidebar.selectbox[0].select("grafo_peso_negativo.json").run()
    next(b for b in app.button if b.label == "Executar análise").click().run()
    assert app.session_state["evaluation"].result.distance("A", "C") == 2
    app.sidebar.selectbox[0].select("grafo_ciclo_negativo.json").run()
    next(b for b in app.button if b.label == "Executar análise").click().run()
    assert "evaluation" not in app.session_state
    assert any("negativo" in e.value for e in app.error)
    assert not app.exception


def test_reciprocal_edges_and_self_loop_are_drawn():
    g = NetworkXGraph()
    g.add_edge("A", "B", 2)
    g.add_edge("B", "A", 3)
    g.add_edge("B", "B", 1)
    fig = PlotlyGraphVisualizer().create(g)
    assert len(fig.data) == 4
    assert len(set(fig.data[2].x)) > 1
    assert list(fig.data[0].y) != list(reversed(fig.data[1].y))


@pytest.mark.parametrize(
    "name,n",
    [
        ("rede_logistica_30.json", 30),
        ("rede_urbana_60.json", 60),
        ("rede_regional_100.json", 100),
        ("rede_desconexa_40.json", 40),
    ],
)
def test_larger_datasets(name, n):
    from floyd_warshall.infrastructure.dataset_manager import DatasetManager

    graph = DatasetManager("datasets", NetworkXGraph).load(name)
    assert len(graph.vertices()) == n
    assert compare(graph, FloydWarshallSolver(), BellmanFordSolver())["distances_match"]


def test_app_large_network_path_view():
    app = AppTest.from_file("../app.py", default_timeout=30).run()
    app.sidebar.selectbox[0].select("rede_urbana_60.json").run()
    next(b for b in app.button if b.label == "Executar análise").click().run()
    assert not app.exception
    assert app.session_state["evaluation"].result.path("P001", "P060")


def test_html_report_sections_and_missing_baseline():
    g = NetworkXGraph()
    g.add_vertex("A")
    e = EvaluationService(FloydWarshallSolver()).evaluate(g)
    html = ReportExporter().to_html("<img src=x onerror=alert(1)>", g, e)
    assert "<img src=x" not in html
    assert "Comparação não executada" in html
    assert "Não há pares distintos" in html
    assert "Onde a escolha ajuda" in html
    assert "@media print" in html


def test_large_html_has_all_pairs_and_limited_matrix():
    g = NetworkXGraph()
    for i in range(14):
        g.add_vertex(f"V{i}")
    e = EvaluationService(FloydWarshallSolver()).evaluate(g)
    html = ReportExporter().to_html("rede.json", g, e)
    assert "196 pares" in html
    assert "Prévia dos primeiros 12" in html
    assert "<td>V13</td>" in html
