"""Grafo dirigido com curvas distintas para arestas recíprocas e laços."""

from html import escape
from math import cos, sin, pi
import networkx as nx
import plotly.graph_objects as go
from floyd_warshall.domain.graph_visualizer import GraphVisualizer


class PlotlyGraphVisualizer(GraphVisualizer):
    def create(self, graph, highlighted_path=None):
        g = nx.DiGraph()
        g.add_nodes_from(graph.vertices())
        g.add_weighted_edges_from(graph.edges())
        positions = nx.spring_layout(g, seed=42, weight=None)
        highlighted = set(zip(highlighted_path or [], (highlighted_path or [])[1:]))
        figure = go.Figure()
        for u, v, weight in graph.edges():
            x0, y0 = positions[u]
            x1, y1 = positions[v]
            color = "#dc2626" if (u, v) in highlighted else "#64748b"
            width = 4 if (u, v) in highlighted else 2
            if u == v:
                xs = [x0 + 0.12 * sin(2 * pi * t / 40) for t in range(41)]
                ys = [y0 + 0.12 * (1 - cos(2 * pi * t / 40)) for t in range(41)]
            else:
                bend = 0.18 if g.has_edge(v, u) else 0
                cx, cy = (x0 + x1) / 2 - bend * (y1 - y0), (y0 + y1) / 2 + bend * (x1 - x0)
                ts = [t / 40 for t in range(41)]
                xs = [(1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1 for t in ts]
                ys = [(1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1 for t in ts]
            figure.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    line=dict(color=color, width=width),
                    hovertemplate=f"{escape(u)} → {escape(v)}: {weight:g}<extra></extra>",
                )
            )
            figure.add_annotation(
                x=xs[20],
                y=ys[20],
                text=f"{weight:g}",
                showarrow=False,
                bgcolor="white",
                font=dict(color="#0f172a"),
            )
            figure.add_annotation(
                x=xs[33],
                y=ys[33],
                ax=xs[29],
                ay=ys[29],
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                text="",
                showarrow=True,
                arrowhead=3,
                arrowwidth=width,
                arrowcolor=color,
            )
        nodes = graph.vertices()
        figure.add_trace(
            go.Scatter(
                x=[positions[v][0] for v in nodes],
                y=[positions[v][1] for v in nodes],
                mode="markers+text",
                text=[escape(v) for v in nodes],
                textposition="top center",
                marker=dict(
                    size=24,
                    color=[
                        "#dc2626" if v in (highlighted_path or []) else "#2563eb" for v in nodes
                    ],
                ),
                hovertemplate="%{text}<extra></extra>",
            )
        )
        figure.update_layout(
            showlegend=False,
            height=550,
            template="plotly_white",
            margin=dict(l=30, r=30, t=30, b=30),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
        )
        return figure
