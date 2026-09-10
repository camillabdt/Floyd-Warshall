install:
	poetry install

run:
	poetry run floyd-warshall examples/grafo_exemplo.txt --origem A --destino D

test:
	poetry run pytest
