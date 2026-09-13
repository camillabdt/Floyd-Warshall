"""Grafo dirigido com curvas distintas para arestas recíprocas e laços.

O caminho consultado recebe destaque; as demais arestas ficam em segundo plano
para que a leitura em redes maiores continue possível.
"""

from html import escape
from math import cos, pi, sin, sqrt

import networkx as nx
import plotly.graph_objects as go

from floyd_warshall.domain.graph_visualizer import GraphVisualizer

PATH_COLOR = "#dc2626"
NODE_COLOR = "#2563eb"
EDGE_COLOR = "#64748b"
FADED_EDGE_COLOR = "#94a3b8"
# Até este número de vértices o layout circular é mais legível que o de molas.
CIRCULAR_LAYOUT_LIMIT = 8
# Acima deste número de arestas, pesos fora do caminho só aparecem ao passar o mouse.
WEIGHT_LABEL_LIMIT = 40
CURVE_STEPS = 40


class PlotlyGraphVisualizer(GraphVisualizer):
    def create(self, graph, highlighted_path=None):
        g = nx.DiGraph()
        g.add_nodes_from(graph.vertices())
        g.add_weighted_edges_from(graph.edges())
        positions = _layout(g)
        path = highlighted_path or []
        highlighted = set(zip(path, path[1:]))
        show_all_weights = len(g.edges) <= WEIGHT_LABEL_LIMIT
        figure = go.Figure()
        for u, v, weight in graph.edges():
            on_path = (u, v) in highlighted
            xs, ys = _edge_curve(positions, u, v, g.has_edge(v, u))
            style = _edge_style(on_path, faded=bool(path) and not on_path)
            figure.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    line=dict(color=style["color"], width=style["width"]),
                    hovertemplate=f"{escape(u)} → {escape(v)}: {weight:g}<extra></extra>",
                )
            )
            if on_path or show_all_weights:
                _add_weight_label(figure, xs, ys, weight, style)
            _add_arrowhead(figure, xs, ys, style)
        _add_nodes(figure, positions, graph.vertices(), set(path))
        _apply_layout(figure, bool(path), show_all_weights)
        return figure


def _layout(g):
    if len(g) <= CIRCULAR_LAYOUT_LIMIT:
        return nx.circular_layout(g)
    spacing = 1.8 / sqrt(len(g))
    return nx.spring_layout(g, seed=42, weight=None, k=spacing, iterations=100)


def _edge_curve(positions, u, v, reciprocal):
    """Pontos de uma curva de Bézier; laços viram círculos e recíprocas se afastam."""
    x0, y0 = positions[u]
    x1, y1 = positions[v]
    ts = [t / CURVE_STEPS for t in range(CURVE_STEPS + 1)]
    if u == v:
        xs = [x0 + 0.12 * sin(2 * pi * t) for t in ts]
        ys = [y0 + 0.12 * (1 - cos(2 * pi * t)) for t in ts]
        return xs, ys
    bend = 0.18 if reciprocal else 0
    cx, cy = (x0 + x1) / 2 - bend * (y1 - y0), (y0 + y1) / 2 + bend * (x1 - x0)
    xs = [(1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1 for t in ts]
    ys = [(1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1 for t in ts]
    return xs, ys


def _edge_style(on_path, faded):
    if on_path:
        return {"color": PATH_COLOR, "width": 4, "arrow": 1.6}
    if faded:
        return {"color": FADED_EDGE_COLOR, "width": 1.5, "arrow": 1.1}
    return {"color": EDGE_COLOR, "width": 2, "arrow": 1.3}


def _add_weight_label(figure, xs, ys, weight, style):
    # Fora do meio da curva, rótulos de arestas que se cruzam não coincidem.
    at = int(CURVE_STEPS * 0.4)
    figure.add_annotation(
        x=xs[at],
        y=ys[at],
        text=f"<b>{weight:g}</b>",
        showarrow=False,
        bgcolor="white",
        bordercolor=style["color"],
        borderwidth=1,
        borderpad=2,
        font=dict(color="#0f172a", size=12),
    )


def _add_arrowhead(figure, xs, ys, style):
    tip, tail = int(CURVE_STEPS * 0.82), int(CURVE_STEPS * 0.72)
    figure.add_annotation(
        x=xs[tip],
        y=ys[tip],
        ax=xs[tail],
        ay=ys[tail],
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        text="",
        showarrow=True,
        arrowhead=3,
        arrowsize=style["arrow"],
        arrowwidth=style["width"],
        arrowcolor=style["color"],
    )


def _add_nodes(figure, positions, nodes, path_nodes):
    figure.add_trace(
        go.Scatter(
            x=[positions[v][0] for v in nodes],
            y=[positions[v][1] for v in nodes],
            mode="markers+text",
            text=[escape(v) for v in nodes],
            textposition="middle center",
            textfont=dict(color="white", size=11, family="Arial Black, Arial, sans-serif"),
            marker=dict(
                size=34,
                color=[PATH_COLOR if v in path_nodes else NODE_COLOR for v in nodes],
                line=dict(color="white", width=2),
            ),
            hovertemplate="%{text}<extra></extra>",
        )
    )


def _apply_layout(figure, has_path, weights_visible):
    figure.update_layout(
        showlegend=False,
        height=600,
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
    )
    if not has_path:
        return
    hint = "" if weights_visible else " (peso ao passar o mouse)"
    figure.add_annotation(
        xref="paper",
        yref="paper",
        x=0,
        y=1.04,
        xanchor="left",
        showarrow=False,
        align="left",
        text=(
            f"<span style='color:{PATH_COLOR}'>■</span> caminho mínimo consultado  "
            f"<span style='color:{FADED_EDGE_COLOR}'>■</span> demais arestas{hint}"
        ),
        font=dict(size=12, color="#334155"),
    )
