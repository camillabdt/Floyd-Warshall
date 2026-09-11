from __future__ import annotations

from collections.abc import Callable
from io import BytesIO
import json
from pathlib import Path

import pandas as pd

from floyd_warshall.domain.graph import Graph


class DatasetManager:
    """Gerencia listagem, validação, carregamento e salvamento de datasets."""

    ALLOWED_SUFFIXES = {".csv", ".json"}

    def __init__(
        self,
        base_dir: str | Path,
        graph_factory: Callable[[], Graph],
    ) -> None:
        self.base_dir = Path(base_dir)
        self.graph_factory = graph_factory

        self.base_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def list_datasets(self) -> list[str]:
        return sorted(
            path.name
            for path in self.base_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() in self.ALLOWED_SUFFIXES
        )

    def save(
        self,
        filename: str,
        content: bytes,
    ) -> Path:

        safe_name = Path(filename).name
        suffix = Path(safe_name).suffix.lower()

        if suffix not in self.ALLOWED_SUFFIXES:
            raise ValueError(
                "Formato não suportado. Use CSV ou JSON."
            )

        # Valida antes de salvar
        self.load_bytes(
            safe_name,
            content,
        )

        destination = (
            self.base_dir / safe_name
        )

        destination.write_bytes(content)

        return destination

    def load(
        self,
        name: str,
    ) -> Graph:

        path = (
            self.base_dir
            / Path(name).name
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Dataset não encontrado: {name}"
            )

        return self.load_bytes(
            path.name,
            path.read_bytes(),
        )

    def load_bytes(
        self,
        filename: str,
        content: bytes,
    ) -> Graph:

        suffix = (
            Path(filename)
            .suffix
            .lower()
        )

        if suffix == ".csv":
            return self._load_csv(content)

        if suffix == ".json":
            return self._load_json(content)

        raise ValueError(
            "Formato não suportado. Use CSV ou JSON."
        )

    def _load_csv(
        self,
        content: bytes,
    ) -> Graph:

        dataframe = pd.read_csv(
            BytesIO(content)
        )

        required = {
            "source",
            "target",
            "weight",
        }

        if not required.issubset(
            dataframe.columns
        ):
            raise ValueError(
                "CSV deve conter as colunas: "
                "source,target,weight"
            )

        graph = self.graph_factory()

        for row in dataframe.itertuples(
            index=False
        ):

            try:
                graph.add_edge(
                    str(row.source),
                    str(row.target),
                    float(row.weight),
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    "O campo weight deve ser numérico."
                ) from exc

        if not graph.vertices():
            raise ValueError(
                "O dataset não contém vértices."
            )

        return graph

    def _load_json(
        self,
        content: bytes,
    ) -> Graph:

        try:
            payload = json.loads(
                content.decode("utf-8")
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:

            raise ValueError(
                "JSON inválido."
            ) from exc

        if isinstance(payload, list):
            payload = {
                "edges": payload
            }

        if (
            not isinstance(payload, dict)
            or "edges" not in payload
        ):
            raise ValueError(
                "JSON deve conter "
                "a chave 'edges'."
            )

        graph = self.graph_factory()

        for vertex in payload.get(
            "vertices",
            [],
        ):
            graph.add_vertex(
                str(vertex)
            )

        for edge in payload["edges"]:

            try:
                graph.add_edge(
                    str(edge["source"]),
                    str(edge["target"]),
                    float(edge["weight"]),
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    "Cada aresta JSON deve ter "
                    "source, target e weight numérico."
                ) from exc

        if not graph.vertices():
            raise ValueError(
                "O dataset não contém vértices."
            )

        return graph