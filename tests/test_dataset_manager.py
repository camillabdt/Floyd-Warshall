import json
import pytest
from floyd_warshall.infrastructure.dataset_manager import DatasetManager
from floyd_warshall.infrastructure.networkx_graph import NetworkXGraph


@pytest.fixture
def manager(tmp_path):
    return DatasetManager(tmp_path, NetworkXGraph)


def test_csv_preserves_labels_and_duplicate_minimum(manager):
    g = manager.load_bytes("x.csv", b"source,target,weight\n001,NA,8\n001,NA,2\n001,NA,9\n")
    assert g.vertices() == ["001", "NA"]
    assert g.edges() == [("001", "NA", 2.0)]


def test_save_reload_and_isolated_vertex(manager):
    content = b'{"vertices":["Z"],"edges":[]}'
    manager.save("isolated.json", content)
    assert manager.list_datasets() == ["isolated.json"]
    assert manager.load("isolated.json").vertices() == ["Z"]


@pytest.mark.parametrize(
    "content",
    [
        b"{}",
        b"{",
        b'{"edges":null}',
        b'{"vertices":"A","edges":[]}',
        b'{"edges":[{}]}',
        b'{"edges":[{"source":null,"target":"A","weight":1}]}',
    ],
)
def test_invalid_json(manager, content):
    with pytest.raises(ValueError):
        manager.load_bytes("bad.json", content)


@pytest.mark.parametrize("weight", ["nan", "inf", "-inf", "abc", ""])
def test_invalid_csv_weights(manager, weight):
    with pytest.raises(ValueError):
        manager.load_bytes("bad.csv", f"source,target,weight\nA,B,{weight}\n".encode())


def test_invalid_save_does_not_write(manager):
    with pytest.raises(ValueError):
        manager.save("bad.csv", b"wrong,header\n")
    assert manager.list_datasets() == []


def test_constructor_does_not_create_directory(tmp_path):
    target = tmp_path / "novo"
    manager = DatasetManager(target, NetworkXGraph)
    assert not target.exists()
    assert manager.list_datasets() == []
    manager.save("a.json", b'{"vertices":["A"],"edges":[]}')
    assert target.is_dir()
