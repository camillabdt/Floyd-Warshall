from dataclasses import asdict
from hashlib import sha256
from math import inf

import pandas as pd
import streamlit as st

from floyd_warshall.application.comparison import benchmark, compare
from floyd_warshall.application.evaluation import EvaluationService
from floyd_warshall.application.floyd_warshall_solver import FloydWarshallSolver, NegativeCycleError
from floyd_warshall.config import settings
from floyd_warshall.infrastructure.bellman_ford_solver import BellmanFordSolver
from floyd_warshall.infrastructure.dataset_manager import DatasetManager
from floyd_warshall.infrastructure.networkx_graph import NetworkXGraph
from floyd_warshall.infrastructure.plotly_graph_visualizer import PlotlyGraphVisualizer
from floyd_warshall.infrastructure.report_exporter import ReportExporter

# Limites da interface; a biblioteca e a CLI não os impõem.
MAX_VERTICES_ANALYSIS = 200
MAX_VERTICES_DRAWING = 50
NO_SELECTION = "Selecione..."


def run():
    st.set_page_config(page_title="Floyd-Warshall • Laboratório", page_icon="🧭", layout="wide")
    st.title("Floyd-Warshall")
    st.caption("Laboratório de caminhos mínimos • implementação própria • grafos dirigidos")
    manager = DatasetManager(settings.datasets_dir, NetworkXGraph)
    loaded = _select_dataset(manager)
    if loaded is None:
        return
    label, content, graph = loaded
    _reset_state_on_new_dataset(label, content)
    _show_input(label, graph)
    if len(graph.vertices()) > MAX_VERTICES_ANALYSIS:
        st.warning(
            f"Esta interface aceita até {MAX_VERTICES_ANALYSIS} vértices por análise. Use a biblioteca para estudos maiores."
        )
        return
    if st.button("Executar análise", type="primary") and not _run_analysis(graph):
        return
    if "evaluation" not in st.session_state:
        if len(graph.vertices()) <= MAX_VERTICES_DRAWING:
            st.plotly_chart(PlotlyGraphVisualizer().create(graph))
        return
    evaluation = st.session_state.evaluation
    tabs = st.tabs(
        ["Caminhos e grafo", "Métricas e matrizes", "Baseline", "Complexidade", "Relatórios"]
    )
    with tabs[0]:
        _render_paths_tab(graph, evaluation.result)
    with tabs[1]:
        _render_metrics_tab(evaluation)
    with tabs[2]:
        _render_baseline_tab(graph)
    with tabs[3]:
        _render_complexity_tab()
    with tabs[4]:
        _render_reports_tab(label, graph, evaluation)


def _select_dataset(manager):
    """Barra lateral: devolve (rótulo, bytes, grafo) ou None quando não há dataset válido."""
    with st.sidebar:
        st.header("Dataset")
        saved = manager.list_datasets()
        selected = st.selectbox("Dataset salvo", [NO_SELECTION] + saved)
        uploaded = st.file_uploader("Ou envie um CSV/JSON", type=["csv", "json"])
        save = st.button("Salvar upload")
        st.caption(
            "CSV: source,target,weight. JSON aceita vertices e edges, incluindo vértices isolados."
        )
    try:
        if uploaded is not None:
            label, content = uploaded.name, uploaded.getvalue()
            graph = manager.load_bytes(label, content)
            if save:
                _save_upload(manager, saved, label, content)
            return label, content, graph
        if selected != NO_SELECTION:
            content = (manager.base_dir / selected).read_bytes()
            return selected, content, manager.load_bytes(selected, content)
    except (ValueError, OSError) as exc:
        st.session_state.pop("evaluation", None)
        st.error(str(exc))
        return None
    st.session_state.pop("evaluation", None)
    st.info("Selecione um dataset ou envie um CSV/JSON para começar.")
    return None


def _save_upload(manager, saved, label, content):
    if label in saved:
        st.sidebar.error("Nome já existente. Renomeie o arquivo antes de salvar.")
    else:
        manager.save(label, content)
        st.sidebar.success("Dataset salvo.")


def _reset_state_on_new_dataset(label, content):
    """Descarta resultados antigos quando o dataset (nome ou conteúdo) muda."""
    fingerprint = sha256(label.encode() + content).hexdigest()
    if st.session_state.get("fingerprint") != fingerprint:
        for key in ("evaluation", "comparison"):
            st.session_state.pop(key, None)
        st.session_state.fingerprint = fingerprint


def _show_input(label, graph):
    st.subheader(label)
    cols = st.columns(2)
    cols[0].metric("Vértices", len(graph.vertices()))
    cols[1].metric("Arestas", len(graph.edges()))
    with st.expander("Dados de entrada"):
        st.write("Vértices:", graph.vertices())
        st.dataframe(pd.DataFrame(graph.edges(), columns=["source", "target", "weight"]))


def _run_analysis(graph):
    """Executa o Floyd-Warshall; devolve False quando há ciclo negativo."""
    st.session_state.pop("evaluation", None)
    st.session_state.pop("comparison", None)
    try:
        with st.spinner("Calculando caminhos mínimos..."):
            st.session_state.evaluation = EvaluationService(FloydWarshallSolver()).evaluate(graph)
    except NegativeCycleError as exc:
        st.error(str(exc))
        return False
    return True


def _render_paths_tab(graph, result):
    cols = st.columns(2)
    origin = cols[0].selectbox("Origem", result.vertices)
    destination = cols[1].selectbox("Destino", result.vertices, index=len(result.vertices) - 1)
    path = result.path(origin, destination)
    if path is None:
        st.warning(f"Não existe caminho de {origin} para {destination}.")
    else:
        st.metric("Distância mínima", f"{result.distance(origin, destination):g}")
        st.write(" → ".join(path))
    if len(result.vertices) <= MAX_VERTICES_DRAWING:
        st.plotly_chart(PlotlyGraphVisualizer().create(graph, highlighted_path=path))
        return
    st.info(
        f"Para redes acima de {MAX_VERTICES_DRAWING} vértices, o desenho mostra apenas o caminho consultado. Matrizes e relatórios abrangem a rede completa."
    )
    if path:
        st.plotly_chart(
            PlotlyGraphVisualizer().create(_route_subgraph(graph, path), highlighted_path=path)
        )


def _route_subgraph(graph, path):
    """Grafo contendo apenas os vértices e arestas do caminho consultado."""
    route_graph = NetworkXGraph()
    for vertex in path:
        route_graph.add_vertex(vertex)
    weights = {(u, v): w for u, v, w in graph.edges()}
    for u, v in zip(path, path[1:]):
        route_graph.add_edge(u, v, weights[u, v])
    return route_graph


def _render_metrics_tab(evaluation):
    result = evaluation.result
    st.dataframe(pd.DataFrame([asdict(evaluation.metrics)]))
    st.caption(
        "Tempo em ms sem instrumentação. Pico em KiB de alocações Python, medido em outra execução; não é memória total do processo. Pares e densidade excluem a diagonal."
    )
    for title, matrix in [
        ("Matriz inicial", result.initial_distances),
        ("Menores distâncias", result.distances),
    ]:
        st.subheader(title)
        st.dataframe(
            pd.DataFrame(
                [["∞" if v == inf else str(v) for v in row] for row in matrix],
                index=result.vertices,
                columns=result.vertices,
            )
        )


def _render_baseline_tab(graph):
    st.write(
        "Baseline: Bellman-Ford do NetworkX executado para cada origem. Aceita pesos negativos e compara todas as distâncias com tolerância de 1e-9."
    )
    if st.button("Comparar com baseline"):
        st.session_state.comparison = compare(graph, FloydWarshallSolver(), BellmanFordSolver())
    comparison = st.session_state.get("comparison")
    if not comparison:
        return
    if comparison["distances_match"]:
        st.success("Todas as distâncias coincidem com o baseline.")
    else:
        st.error("Foram encontradas divergências nas distâncias.")
    st.dataframe(pd.DataFrame({k: comparison[k] for k in ("floyd_warshall", "bellman_ford")}))
    st.caption("Medição pontual: não permite concluir superioridade geral de desempenho.")


def _render_complexity_tab():
    st.markdown(
        "**Floyd-Warshall:** tempo O(V³), espaço O(V²). A recorrência é d[i,j] = min(d[i,j], d[i,k] + d[k,j]). A ordem externa de k é essencial.\n\n**Bellman-Ford para todas as origens:** O(V²E), com O(V²) para armazenar o resultado completo."
    )
    st.write(
        "Experimento: grafos completos de 10 a 320 vértices, dobrando a cada passo; pesos positivos determinísticos, aquecimento e mediana de três execuções. Se o tempo fosse c·V³, cada dobra multiplicaria o tempo por 8 e a inclinação log-log seria 3. O experimento verifica a implementação, sem provar a complexidade."
    )
    if st.button("Executar experimento de complexidade"):
        st.session_state.benchmark = benchmark(NetworkXGraph, FloydWarshallSolver())
    if "benchmark" in st.session_state:
        frame = pd.DataFrame(st.session_state.benchmark)
        st.dataframe(frame)
        st.line_chart(frame.set_index("vertices")[["median_ms"]])
        st.download_button(
            "Baixar experimento CSV", frame.to_csv(index=False), "complexidade.csv", "text/csv"
        )


def _render_reports_tab(label, graph, evaluation):
    exporter = ReportExporter()
    comparison = st.session_state.get("comparison")
    st.download_button(
        "Baixar JSON",
        exporter.to_json(label, graph, evaluation, comparison),
        "relatorio.json",
        "application/json",
    )
    st.download_button("Baixar CSV", exporter.to_csv(evaluation), "caminhos.csv", "text/csv")
    st.download_button(
        "Baixar HTML",
        exporter.to_html(label, graph, evaluation, comparison),
        "relatorio.html",
        "text/html",
    )


if __name__ == "__main__":
    run()
