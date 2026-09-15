# Alvos do projeto Floyd-Warshall. Use `make` ou `make help` para ver a lista.
# A esteira de evidências tem ordem obrigatória: datasets -> evaluate -> evidence.

.DEFAULT_GOAL := help
.NOTPARALLEL:
.PHONY: help install test run app datasets evaluate evidence reports check package release clean

help: ## Lista os alvos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## Instala as dependências no .venv do projeto
	poetry install

test: ## Roda a suíte de testes
	poetry run pytest -q

run: ## Executa a CLI no grafo de exemplo (A -> D)
	poetry run floyd-warshall examples/grafo_exemplo.txt --origem A --destino D

app: ## Abre a interface Streamlit
	poetry run streamlit run app.py

datasets: ## Regera as redes sintéticas em datasets/ (seeds fixas)
	poetry run python scripts/generate_datasets.py

evaluate: ## Compara as redes maiores com o baseline -> reports/comparacao_redes.csv
	poetry run python scripts/evaluate_datasets.py

evidence: ## Gera relatórios, gráfico e métricas em reports/ (exige evaluate antes)
	poetry run python scripts/generate_evidence.py

reports: datasets evaluate evidence ## Refaz toda a esteira de evidências, na ordem correta

check: ## Verifica o lock e roda os testes
	poetry check --lock
	poetry run pytest -q

package: ## Empacota a entrega em ZIP com MANIFEST.sha256
	poetry build
	poetry run python scripts/package_release.py

release: check reports package ## Verificação completa, evidências e empacotamento

clean: ## Remove caches gerados por execuções locais
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +
	rm -rf .pytest_cache
