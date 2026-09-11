import networkx as nx
import plotly.graph_objects as go

from floyd_warshall.domain.graph import Graph
from floyd_warshall.domain.graph_visualizer import (
    GraphVisualizer,
)


class PlotlyGraphVisualizer(GraphVisualizer):
    """
    Visualizador interativo de grafos usando Plotly.

    NetworkX é utilizado somente para calcular
    a disposição visual dos vértices.
    """

    def create(
        self,
        graph: Graph,
        highlighted_path: list[str] | None = None,
    ) -> go.Figure:

        nx_graph = nx.DiGraph()

        for vertex in graph.vertices():
            nx_graph.add_node(vertex)

        for origin, destination, weight in graph.edges():
            nx_graph.add_edge(
                origin,
                destination,
                weight=weight,
            )

        positions = nx.spring_layout(
            nx_graph,
            seed=42,
        )

        highlighted_edges = set()

        if highlighted_path:
            highlighted_edges = {
                (
                    highlighted_path[i],
                    highlighted_path[i + 1],
                )
                for i in range(
                    len(highlighted_path) - 1
                )
            }

        figure = go.Figure()

        # =========================
        # ARESTAS NORMAIS
        # =========================

        for origin, destination, weight in graph.edges():

            x0, y0 = positions[origin]
            x1, y1 = positions[destination]

            is_highlighted = (
                origin,
                destination,
            ) in highlighted_edges

            figure.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line=dict(
                        width=(
                            5
                            if is_highlighted
                            else 2
                        ),
                        color=(
                            "#e74c3c"
                            if is_highlighted
                            else "#7f8c8d"
                        ),
                    ),
                    hoverinfo="none",
                    showlegend=False,
                )
            )

            # Peso da aresta
            middle_x = (
                x0 + x1
            ) / 2

            middle_y = (
                y0 + y1
            ) / 2

            figure.add_annotation(
                x=middle_x,
                y=middle_y,
                text=str(
                    int(weight)
                    if float(weight).is_integer()
                    else weight
                ),
                showarrow=False,
                font=dict(
                    size=14,
                ),
                bgcolor="white",
                bordercolor="#cccccc",
                borderwidth=1,
            )

            # Pequena seta indicando direção
            figure.add_annotation(
                x=x1,
                y=y1,
                ax=x0,
                ay=y0,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=3,
                arrowsize=1.2,
                arrowwidth=(
                    3
                    if is_highlighted
                    else 1.5
                ),
                arrowcolor=(
                    "#e74c3c"
                    if is_highlighted
                    else "#7f8c8d"
                ),
                opacity=0.8,
            )

        # =========================
        # VÉRTICES
        # =========================

        node_x = []
        node_y = []
        labels = []
        node_colors = []

        highlighted_nodes = set(
            highlighted_path or []
        )

        for vertex in graph.vertices():

            x, y = positions[vertex]

            node_x.append(x)
            node_y.append(y)
            labels.append(vertex)

            if vertex in highlighted_nodes:
                node_colors.append(
                    "#e74c3c"
                )
            else:
                node_colors.append(
                    "#3498db"
                )

        figure.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                text=labels,
                textposition="top center",
                hovertext=[
                    f"Vértice: {label}"
                    for label in labels
                ],
                hoverinfo="text",
                marker=dict(
                    size=28,
                    color=node_colors,
                    line=dict(
                        width=2,
                        color="white",
                    ),
                ),
                textfont=dict(
                    size=15,
                ),
                showlegend=False,
            )
        )

        figure.update_layout(
            title="Visualização do grafo",
            showlegend=False,
            hovermode="closest",
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20,
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
            ),
            height=550,
        )

        return figure
