from pathlib import Path
import pytest
from floyd_warshall.infrastructure.text_graph_reader import TextGraphReader


def test_reads_valid_file(tmp_path: Path) -> None:
    file = tmp_path / 'grafo.txt'
    file.write_text('VERTICES A B C\nA B 3\nB C 2\n', encoding='utf-8')
    graph = TextGraphReader().read(str(file))
    assert graph.vertices() == ['A', 'B', 'C']
    assert ('A', 'B', 3.0) in graph.edges()
    assert ('B', 'C', 2.0) in graph.edges()


def test_supports_isolated_vertex(tmp_path: Path) -> None:
    file = tmp_path / 'grafo.txt'
    file.write_text('VERTICES A B C D\nA B 3\n', encoding='utf-8')
    graph = TextGraphReader().read(str(file))
    assert 'D' in graph.vertices()


def test_ignores_comments_and_blank_lines(tmp_path: Path) -> None:
    file = tmp_path / 'grafo.txt'
    file.write_text('# comentário\n\nVERTICES A B\nA B 3\n', encoding='utf-8')
    graph = TextGraphReader().read(str(file))
    assert graph.vertices() == ['A', 'B']


def test_rejects_invalid_line(tmp_path: Path) -> None:
    file = tmp_path / 'grafo.txt'
    file.write_text('VERTICES A B\nA B\n', encoding='utf-8')
    with pytest.raises(ValueError):
        TextGraphReader().read(str(file))
