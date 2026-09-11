from math import inf

import pandas as pd
import streamlit as st

from floyd_warshall.application.evaluation import (
    EvaluationService,
)

from floyd_warshall.application.floyd_warshall_solver import (
    FloydWarshallSolver,
    NegativeCycleError,
)

from floyd_warshall.config import settings

from floyd_warshall.infrastructure.dataset_manager import (
    DatasetManager,
)

from floyd_warshall.infrastructure.networkx_graph import (
    NetworkXGraph,
)

from floyd_warshall.infrastructure.plotly_graph_visualizer import (
    PlotlyGraphVisualizer,
)

@st.cache_resource
def build_dataset_manager() -> DatasetManager:
    return DatasetManager(
        settings.datasets_dir,
        NetworkXGraph,
    )


def matrix_to_dataframe(
    vertices,
    matrix,
):
    formatted = []

    for row in matrix:
        formatted.append(
            [
                "∞" if value == inf
                else round(value, 3)
                for value in row
            ]
        )

    return pd.DataFrame(
        formatted,
        index=vertices,
        columns=vertices,
    )


def format_metric(
    value,
):
    if value is None:
        return "-"

    return f"{value:.3f}"


def run() -> None:

    st.set_page_config(
        page_title="Floyd-Warshall",
        page_icon="🧭",
        layout="wide",
    )

    st.title(
        "Floyd-Warshall"
    )

    st.caption(
        "Caminhos mais curtos entre todos os pares"
    )

    manager = (
        build_dataset_manager()
    )

    # =========================
    # SIDEBAR
    # =========================

    with st.sidebar:

        st.header(
            "Dataset"
        )

        saved = (
            manager.list_datasets()
        )

        selected = st.selectbox(
            "Dataset salvo",
            ["Selecione..."] + saved,
        )

        uploaded = st.file_uploader(
            "Ou envie um CSV/JSON",
            type=[
                "csv",
                "json",
            ],
        )

        save_upload = st.checkbox(
            "Salvar upload em datasets/"
        )

    graph = None
    label = None

    try:

        if uploaded is not None:

            content = (
                uploaded.getvalue()
            )

            graph = (
                manager.load_bytes(
                    uploaded.name,
                    content,
                )
            )

            label = uploaded.name

            if save_upload:

                path = manager.save(
                    uploaded.name,
                    content,
                )

                st.sidebar.success(
                    f"Salvo: {path.name}"
                )

        elif (
            selected
            != "Selecione..."
        ):

            graph = manager.load(
                selected
            )

            label = selected

    except (
        ValueError,
        FileNotFoundError,
    ) as exc:

        st.error(str(exc))
        return

    if graph is None:

        st.info(
            "Selecione um dataset "
            "ou envie um CSV/JSON."
        )

        return

    # =========================
    # DATASET
    # =========================

    st.success(
        f"Dataset carregado: {label}"
    )

    vertices = graph.vertices()

    edges = list(
        graph.edges()
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Vértices",
        len(vertices),
    )

    col2.metric(
        "Arestas",
        len(edges),
    )

    with st.expander(
        "Visualizar dados do grafo"
    ):

        st.subheader(
            "Vértices"
        )

        st.write(
            vertices
        )

        st.subheader(
            "Arestas"
        )

        edge_dataframe = (
            pd.DataFrame(
                edges,
                columns=[
                    "source",
                    "target",
                    "weight",
                ],
            )
        )

        st.dataframe(
            edge_dataframe,
            use_container_width=True,
            hide_index=True,
        )


        st.subheader(
            "Visualização do grafo"
        )   
        visualizer = (
            PlotlyGraphVisualizer()
        )

        graph_figure = (
            visualizer.create(
                graph
            )
        )

        st.plotly_chart(
            graph_figure,
            use_container_width=True,
        )

        
    st.divider()

    # =========================
    # FLOYD-WARSHALL
    # =========================

    st.header(
        "Executar Floyd-Warshall"
    )

    st.write(
        "O algoritmo calcula os menores "
        "caminhos entre todos os pares "
        "de vértices."
    )

    if st.button(
        "Executar análise",
        type="primary",
    ):

        solver = (
            FloydWarshallSolver()
        )

        evaluator = (
            EvaluationService(
                solver
            )
        )

        try:

            evaluation = (
                evaluator.evaluate(
                    graph
                )
            )

        except NegativeCycleError as exc:

            st.error(
                str(exc)
            )

            return

        result = (
            evaluation.result
        )

        metrics = (
            evaluation.metrics
        )

        st.session_state[
            "evaluation"
        ] = evaluation

    # =========================
    # RESULTADOS
    # =========================

    if "evaluation" not in st.session_state:
        return

    evaluation = (
        st.session_state[
            "evaluation"
        ]
    )

    result = (
        evaluation.result
    )

    metrics = (
        evaluation.metrics
    )

    st.success(
        "Floyd-Warshall executado com sucesso!"
    )

    # =========================
    # MÉTRICAS
    # =========================

    st.header(
        "Métricas"
    )

    row1 = st.columns(4)

    row1[0].metric(
        "Vértices",
        metrics.vertices,
    )

    row1[1].metric(
        "Arestas",
        metrics.edges,
    )

    row1[2].metric(
        "Densidade",
        f"{metrics.density:.2f}%",
    )

    row1[3].metric(
        "Tempo",
        f"{metrics.execution_time_ms:.4f} ms",
    )

    row2 = st.columns(4)

    row2[0].metric(
        "Memória máxima",
        f"{metrics.peak_memory_kb:.2f} KB",
    )

    row2[1].metric(
        "Pares alcançáveis",
        metrics.reachable_pairs,
    )

    row2[2].metric(
        "Pares não alcançáveis",
        metrics.unreachable_pairs,
    )

    row2[3].metric(
        "Distância média",
        format_metric(
            metrics.average_distance
        ),
    )

    row3 = st.columns(2)

    row3[0].metric(
        "Menor distância",
        format_metric(
            metrics.minimum_distance
        ),
    )

    row3[1].metric(
        "Maior distância",
        format_metric(
            metrics.maximum_distance
        ),
    )

    # =========================
    # MATRIZES
    # =========================

    st.header(
        "Matrizes de distância"
    )

    tab1, tab2 = st.tabs(
        [
            "Matriz inicial",
            "Menores distâncias",
        ]
    )

    with tab1:

        st.dataframe(
            matrix_to_dataframe(
                result.vertices,
                result.initial_distances,
            ),
            use_container_width=True,
        )

    with tab2:

        st.dataframe(
            matrix_to_dataframe(
                result.vertices,
                result.distances,
            ),
            use_container_width=True,
        )

    # =========================
    # CONSULTA DE CAMINHO
    # =========================

    st.header(
        "Consultar caminho"
    )

    col_origin, col_destination = (
        st.columns(2)
    )

    origin = (
        col_origin.selectbox(
            "Origem",
            result.vertices,
        )
    )

    destination = (
        col_destination.selectbox(
            "Destino",
            result.vertices,
        )
    )
    if st.button(
        "Consultar menor caminho"
    ):

        distance = (
            result.distance(
                origin,
                destination,
            )
        )

        path = (
            result.path(
                origin,
                destination,
            )
        )

        if (
            distance == inf
            or path is None
        ):

            st.warning(
                f"Não existe caminho "
                f"de {origin} para "
                f"{destination}."
            )

        else:

            st.metric(
                "Distância mínima",
                format_metric(
                    distance
                ),
            )

            st.write(
                "**Caminho encontrado:**"
            )

            st.code(
                " → ".join(path)
            )

            st.subheader(
                "Caminho destacado no grafo"
            )

            visualizer = (
                PlotlyGraphVisualizer()
            )

            highlighted_figure = (
                visualizer.create(
                    graph,
                    highlighted_path=path,
                )
            )

            st.plotly_chart(
                highlighted_figure,
                use_container_width=True,
            )


if __name__ == "__main__":
    run()
