# Floyd-Warshall — versão final de entrega

Aplicação acadêmica para caminhos mínimos entre todos os pares de um grafo dirigido e ponderado. O Floyd-Warshall é implementado pelo projeto; NetworkX representa o grafo, calcula o layout e fornece um baseline independente Bellman-Ford.

## Executar

Requisitos: Python 3.11 ou superior compatível com o lock e Poetry 1.8 ou superior. A validação desta entrega foi feita com Python 3.12 e Poetry 1.8.2. Na pasta extraída `Floyd-Warshall`:

```bash
poetry install
poetry run pytest -q
poetry run streamlit run app.py
```

A instalação inicial precisa de acesso aos pacotes ou cache local. Depois de instaladas as dependências, a demonstração funciona sem internet. Não é necessário ativar manualmente o ambiente virtual. `poetry.toml` configura `.venv` dentro do projeto.

Configuração opcional: copie `.env.example` para `.env`. Caminhos relativos são resolvidos a partir da pasta de execução. Execute os comandos na raiz do projeto. Os relatórios da interface são baixados pelo navegador; `REPORTS_DIR` é usado pelo script de geração de evidências.

## Demonstração em cinco minutos

1. Selecione `grafo_exemplo.csv` e clique em **Executar análise**.
2. Consulte A → D: distância **6**, caminho **A → B → C → D**. O caminho aparece em vermelho.
3. Abra **Métricas e matrizes** para conferir distâncias e pares inalcançáveis.
4. Em **Baseline**, clique em **Comparar com baseline**: todas as distâncias devem coincidir.
5. Em **Relatórios**, baixe JSON, CSV e HTML.
6. Troque para `grafo_desconexo.json`, execute e consulte A → Z: não existe caminho.
7. Em `grafo_peso_negativo.json`, A → C custa **2**. Em `grafo_ciclo_negativo.json`, a execução é recusada com mensagem explicativa.
8. Em **Complexidade**, execute o experimento e baixe os resultados.

Leia [o roteiro completo](docs/ROTEIRO_SEMINARIO.md) para a apresentação e [o relatório de validação](docs/VALIDACAO.md) para as evidências da entrega.

## Redes maiores para a entrega

Incluímos redes sintéticas de 30, 60 e 100 vértices, com 106, 280 e 430 arestas, além de um cenário desconexo de 40 vértices. Consulte o [catálogo e método de geração](docs/DATASETS.md). Todas as distâncias foram verificadas contra o baseline. Para redes acima de 50 vértices, o desenho exibe somente o caminho consultado.

## Datasets e regras de entrada

CSV UTF-8, com as colunas obrigatórias abaixo. Os identificadores são textos; zeros à esquerda e rótulos como `NA` são preservados.

```csv
source,target,weight
A,B,3
A,D,10
B,C,2
C,D,1
```

JSON aceita objeto com `edges` e `vertices` opcional, ou uma lista de arestas. Para vértices isolados, use JSON:

```json
{"vertices":["A","B","Z"],"edges":[{"source":"A","target":"B","weight":3}]}
```

- Identificadores JSON devem ser strings não vazias. Pesos devem ser numéricos finitos; pesos negativos e zero são aceitos.
- Arestas repetidas entre a mesma origem e destino conservam o menor peso, independentemente da ordem.
- Grafo dirigido: A → B não implica B → A. Para ambos os sentidos, declare as duas arestas.
- Laços são aceitos. Laço negativo é ciclo negativo. O algoritmo rejeita qualquer ciclo negativo, inclusive em componente desconexa, sem produzir relatório de caminhos mínimos.
- Dataset vazio é recusado; JSON com um vértice e nenhuma aresta é válido.
- Upload pode ser analisado sem salvar. O botão de salvar não substitui um dataset existente; renomeie o arquivo para salvar outra versão.
- A interface limita análises a 200 vértices e desenho a 50; grafos densos ainda podem ficar visualmente carregados. A biblioteca e CLI não impõem esses limites.

Também permanece disponível a entrada TXT legada (`VERTICES A B C`, seguida de `A B 3`).

```bash
poetry run floyd-warshall datasets/grafo_exemplo.csv --origem A --destino D
poetry run floyd-warshall examples/grafo_exemplo.txt --origem A --destino D
```

## Algoritmo e complexidade

Inicializamos a diagonal com zero e os pares sem aresta com infinito. A matriz `next_vertex` permite reconstruir caminhos. Para cada intermediário k, atualizamos:

```text
d[i,j] = min(d[i,j], d[i,k] + d[k,j])
```

O invariante é: ao terminar a rodada k, as distâncias permitem apenas os intermediários já processados. Por isso k fica no laço externo. Após as rodadas, uma diagonal negativa identifica um ciclo negativo. Caminho de um vértice para si próprio tem custo zero quando não há ciclo negativo.

Tempo no pior caso: **O(V³)**. Matrizes: **O(V²)** de memória. A implementação pula intermediários inalcançáveis, então o tempo observado depende também da conectividade. Reconstruir um caminho custa O(V) no pior caso; exportar os caminhos de todos os pares pode custar O(V³), além do algoritmo. A busca de índice por rótulo é linear nesta implementação.

O baseline roda Bellman-Ford do NetworkX para cada origem, aceitando pesos negativos. Seu limite teórico é O(V²E), com O(V²) para guardar a saída completa. A comparação verifica distâncias, pois caminhos diferentes podem ter o mesmo custo.

O experimento usa grafos dirigidos completos com pesos positivos determinísticos, V = 10, 20, 40, 80, aquecimento e mediana de três execuções. A coluna `ms_per_n3` ajuda a observar a escala. O experimento não prova a complexidade e não demonstra que um algoritmo é sempre mais rápido.

Referências: [Floyd-Warshall e suas complexidades — NetworkX](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.dense.floyd_warshall.html) e [implementação de caminhos ponderados e Bellman-Ford — NetworkX](https://networkx.org/documentation/stable/_modules/networkx/algorithms/shortest_paths/weighted.html).

## Métricas e relatórios

- Quantidade de vértices e arestas; densidade dirigida em porcentagem, excluindo laços: 100 × E_sem_laços / (V × (V−1)).
- Pares alcançáveis e inalcançáveis, excluindo origem igual ao destino.
- Média, mínimo e máximo das distâncias finitas entre vértices distintos; ausência de valores gera `null`.
- Tempo em milissegundos, medido com `perf_counter`, sem rastreamento de memória.
- Pico de alocações Python em KiB, medido com `tracemalloc` em uma segunda execução. Não equivale ao consumo total de RAM e não inclui necessariamente alocações nativas. Se já houver rastreamento externo, o pico inclui esse contexto. A medição é destinada ao uso local sequencial.

JSON e HTML incluem dataset, arestas, métricas, matriz, caminhos e comparação, quando executada. JSON representa infinito como `null`. CSV contém uma linha por par, inclusive a diagonal, com distância vazia para pares inalcançáveis; rótulos iniciados por caracteres de fórmula recebem apóstrofo para leitura em planilhas. HTML é independente de rede e apresenta o relatório textual completo. O experimento de complexidade tem CSV separado.

## Arquitetura e SOLID

| Camada | Componentes e responsabilidade |
|---|---|
| Domínio | `Graph`, `GraphReader`, `GraphVisualizer`, `ShortestPathResult` |
| Aplicação | `ShortestPathSolver`, Floyd-Warshall, avaliação, comparação e experimento |
| Infraestrutura | Adaptador NetworkX, leitores TXT/CSV/JSON, Plotly, baseline e exportação |
| Apresentação | `app.py` (Streamlit), CLI e renderização de console |

**S:** algoritmo, leitura, avaliação, desenho e exportação têm responsabilidades separadas. **O:** outros solvers podem implementar `ShortestPathSolver` sem alterar `EvaluationService`; novos formatos de dataset ainda exigem estender `DatasetManager`, uma limitação conhecida. **L:** os dois solvers entregam `ShortestPathResult` e rejeitam ciclos negativos. **I:** contratos pequenos separam leitura, representação, visualização e cálculo. **D:** Floyd-Warshall depende de `Graph`; avaliação recebe um `ShortestPathSolver`. A montagem das dependências concretas acontece na apresentação e nos scripts.

Poetry gerencia bibliotecas e ambiente; isso é distinto da injeção de dependências do código. `pyproject.toml` declara NetworkX, Streamlit, pandas, Plotly, python-dotenv e pytest; `poetry.lock` fixa a resolução. `requirements.txt` é apenas alternativa de compatibilidade, sem substituir o lock.

## Verificar e empacotar

```bash
poetry check --lock
poetry run pytest -q
poetry run python scripts/generate_evidence.py
poetry run python scripts/evaluate_datasets.py
poetry build
```

O ZIP de entrega contém aplicativo, datasets, código, testes, documentação, lock, relatórios de exemplo e distribuições Python. O wheel instala a biblioteca e a CLI; use o ZIP completo para a interface Streamlit, datasets e material do seminário. `.venv`, `.env`, caches e histórico Git não fazem parte da entrega. A versão foi consolidada a partir do repositório original de Downloads, preservando-o.

## Por que escolhemos este algoritmo?

Leia a [justificativa, vantagens, limitações e comparação com alternativas](docs/JUSTIFICATIVA_ESCOLHA.md). Os relatórios HTML e JSON exportados também incluem um resumo dessa análise.
