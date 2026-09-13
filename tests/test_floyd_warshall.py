import pytest
from floyd_warshall.application.floyd_warshall_solver import FloydWarshallSolver, NegativeCycleError
from floyd_warshall.infrastructure.networkx_graph import NetworkXGraph


def build_example_graph() -> NetworkXGraph:
    graph = NetworkXGraph()
    graph.add_edge("A", "B", 3)
    graph.add_edge("A", "D", 10)
    graph.add_edge("B", "C", 2)
    graph.add_edge("C", "D", 1)
    return graph


def test_shortest_distance_a_to_d() -> None:
    result = FloydWarshallSolver().solve(build_example_graph())
    assert result.distance("A", "D") == 6


def test_reconstructs_path_a_to_d() -> None:
    result = FloydWarshallSolver().solve(build_example_graph())
    assert result.path("A", "D") == ["A", "B", "C", "D"]


def test_unreachable_vertex_returns_none_path() -> None:
    result = FloydWarshallSolver().solve(build_example_graph())
    assert result.path("D", "A") is None


def test_accepts_negative_edge_without_negative_cycle() -> None:
    graph = NetworkXGraph()
    graph.add_edge("A", "B", 4)
    graph.add_edge("A", "C", 5)
    graph.add_edge("B", "C", -2)
    result = FloydWarshallSolver().solve(graph)
    assert result.distance("A", "C") == 2
    assert result.path("A", "C") == ["A", "B", "C"]


def test_detects_negative_cycle() -> None:
    graph = NetworkXGraph()
    graph.add_edge("A", "B", 1)
    graph.add_edge("B", "C", -3)
    graph.add_edge("C", "A", 1)
    with pytest.raises(NegativeCycleError):
        FloydWarshallSolver().solve(graph)
