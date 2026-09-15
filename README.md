<h1 align="center">Floyd-Warshall</h1>

<p align="center">
  <strong>Todos os pares. Todas as distâncias. Um algoritmo.</strong><br>
  Caminhos mínimos entre todos os pares de um grafo dirigido e ponderado.
</p>

<p align="center">
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&amp;logo=python&amp;logoColor=white" alt="Python 3.11+"></a>
  <a href="poetry.lock"><img src="https://img.shields.io/badge/NetworkX-3.6-2C2D72?style=for-the-badge" alt="NetworkX 3.6"></a>
  <a href="poetry.lock"><img src="https://img.shields.io/badge/Streamlit-1.63-FF4B4B?style=for-the-badge&amp;logo=streamlit&amp;logoColor=white" alt="Streamlit 1.63"></a>
  <a href="poetry.lock"><img src="https://img.shields.io/badge/Plotly-7.0-3F4F75?style=for-the-badge&amp;logo=plotly&amp;logoColor=white" alt="Plotly 7.0"></a>
  <br>
  <a href="poetry.lock"><img src="https://img.shields.io/badge/pandas-3.0-150458?style=for-the-badge&amp;logo=pandas&amp;logoColor=white" alt="pandas 3.0"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/Poetry-1.8+-60A5FA?style=for-the-badge&amp;logo=poetry&amp;logoColor=white" alt="Poetry 1.8+"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/pytest-8.3-0A9EDC?style=for-the-badge&amp;logo=pytest&amp;logoColor=white" alt="pytest 8.3"></a>
</p>

<p align="center">
  <a href="#sobre-o-projeto">Sobre</a> ·
  <a href="reports/relatorio_final.html">Relatório</a> ·
  <a href="#entregáveis">Entregáveis</a> ·
  <a href="#tecnologias">Tecnologias</a> ·
  <a href="#executar">Executar</a> ·
  <a href="#simulação-do-algoritmo">Simulação</a> ·
  <a href="#demonstração-rápida">Demonstração</a> ·
  <a href="#algoritmo-e-complexidade">Algoritmo</a> ·
  <a href="#documentação">Documentação</a>
</p>

## Sobre o projeto

O Floyd-Warshall resolve o problema dos caminhos mais curtos entre todos os pares de vértices. Em vez de partir de uma única origem, ele calcula a menor distância entre cada par (i, j) de um grafo dirigido com pesos nas arestas. Para cada vértice intermediário k, o algoritmo verifica se passar por k encurta o caminho entre i e j.

Esta aplicação acadêmica implementa o algoritmo do zero, com reconstrução de caminhos, e o apresenta em uma interface web. O NetworkX representa o grafo, calcula o layout do desenho e fornece um baseline independente com Bellman-Ford, usado para conferir os resultados.

O projeto foi desenvolvido para o seminário da disciplina de Teoria da Computação da Unipampa. O tema, a entrada e a saída esperadas estão descritos no [enunciado](docs/ENUNCIADO.md).

## Entregáveis

**Relatório principal:** [reports/relatorio_final.html](reports/relatorio_final.html). É o relatório HTML gerado pelo script de evidências, com a definição do problema (instância, entrada, saída, restrições e pertinência à classe P), o funcionamento do algoritmo (por que o laço de k é o mais externo e como o caminho é reconstruído), métricas, caminhos, comparação com o baseline nas redes maiores, experimento de complexidade e análise crítica da escolha. Abra no navegador para ler offline; a versão em JSON do mesmo relatório está em [relatorio_final.json](reports/relatorio_final.json).

Cada funcionalidade esperada no seminário tem um lugar na aplicação e uma evidência gerada em [reports/](reports/).

| Funcionalidade                   | Onde está na aplicação                                                                                                         | Evidência                                                                                                   |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| Gerenciamento de datasets        | Seleção, upload e salvamento de CSV, JSON e TXT na barra lateral. Arquivos em [datasets/](datasets/) e [examples/](examples/). | [Catálogo de datasets](docs/DATASETS.md)                                                                    |
| Avaliação com múltiplas métricas | Aba **Métricas e matrizes**: vértices, arestas, densidade, alcançabilidade, distâncias, tempo e memória.                       | [relatorio_final.json](reports/relatorio_final.json)                                                        |
| Visualização de resultados       | Desenho interativo do grafo com o caminho consultado em destaque.                                                              | [grafo_exemplo.html](reports/grafo_exemplo.html)                                                            |
| Exportação de relatórios         | Aba **Relatórios**: download em JSON, CSV e HTML.                                                                              | [relatorio_final.html](reports/relatorio_final.html) e [caminhos_exemplo.csv](reports/caminhos_exemplo.csv) |
| Bônus: comparação com baseline   | Aba **Baseline**: Bellman-Ford do NetworkX para cada origem.                                                                   | [comparacao_redes.csv](reports/comparacao_redes.csv)                                                        |
| Bônus: análise de complexidade   | Aba **Complexidade**: experimento com V de 10 a 320, dobrando a cada passo.                                                    | [complexidade.csv](reports/complexidade.csv)                                                                |

Os arquivos de `reports/` não são escritos à mão: `make reports` regera todos eles a partir do código. A ordem importa, porque `generate_evidence.py` lê o `comparacao_redes.csv` produzido por `evaluate_datasets.py`:

```
scripts/generate_datasets.py  ->  datasets/*.json e *.csv (seeds fixas)
scripts/evaluate_datasets.py  ->  reports/comparacao_redes.csv
scripts/generate_evidence.py  ->  reports/ relatorio_final.html e .json,
                                  complexidade.csv, ambiente.json,
                                  caminhos_exemplo.csv, grafo_exemplo.html
```

Os dois últimos scripts abortam com `RuntimeError` se alguma distância divergir do baseline Bellman-Ford, então um relatório só chega a existir se os números conferirem. O [relatório de validação](docs/VALIDACAO.md) registra a execução completa desses passos.

## Tecnologias

| Parte        | Tecnologia     | Uso no projeto                                                      |
| ------------ | -------------- | ------------------------------------------------------------------- |
| Algoritmo    | Python 3.11+   | Floyd-Warshall próprio em [src/floyd_warshall](src/floyd_warshall/) |
| Grafos       | NetworkX 3.6   | Representação, layout e baseline Bellman-Ford                       |
| Interface    | Streamlit 1.63 | Aplicação web em [app.py](app.py)                                   |
| Visualização | Plotly 7.0     | Desenho interativo do grafo e do caminho                            |
| Dados        | pandas 3.0     | Tabelas de métricas e exportação CSV                                |
| Configuração | python-dotenv  | Leitura opcional de `.env`                                          |
| Ambiente     | Poetry 1.8+    | Dependências fixadas em [poetry.lock](poetry.lock)                  |
| Testes       | pytest 8.3     | Suíte em [tests/](tests/)                                           |

## Executar

Todos os comandos rodam na raiz do projeto. Esta tabela é o caminho mínimo, do zero ao resultado:

| Objetivo                 | Comando                                                                       | Resultado esperado                                  |
| ------------------------ | ----------------------------------------------------------------------------- | --------------------------------------------------- |
| 1. Instalar, uma vez só  | `poetry install`                                                              | `.venv` criado dentro do projeto                    |
| 2. **Rodar o algoritmo** | `poetry run floyd-warshall datasets/grafo_exemplo.csv --origem A --destino D` | `Distância: 6` e `Caminho: A -> B -> C -> D`        |
| 3. Conferir os testes    | `make test`                                                                   | `52 passed`                                         |
| 4. Regerar os resultados | `make reports`                                                                | `datasets/` e `reports/` refeitos, em cerca de 20 s |
| 5. Abrir a interface web | `make app`                                                                    | Streamlit no navegador                              |

Depois do passo 4, o relatório completo está em [reports/relatorio_final.html](reports/relatorio_final.html) e o desenho interativo do grafo em [reports/grafo_exemplo.html](reports/grafo_exemplo.html). A saída do passo 2 está explicada em [Rodar apenas o algoritmo](#rodar-apenas-o-algoritmo).

Requisitos: Python 3.11 ou superior compatível com o lock e Poetry 1.8 ou superior. A validação desta entrega foi feita com Python 3.12 e Poetry 1.8.2. A instalação inicial precisa de acesso aos pacotes ou cache local; depois disso, a demonstração funciona sem internet. Não é necessário ativar manualmente o ambiente virtual, pois [poetry.toml](poetry.toml) configura o `.venv` dentro do projeto.

Configuração opcional: copie `.env.example` para `.env`. Caminhos relativos são resolvidos a partir da pasta de execução. Os relatórios da interface são baixados pelo navegador; a variável `REPORTS_DIR` é usada apenas pelo script de geração de evidências.

### Atalhos com make

O [Makefile](Makefile) reúne todos os comandos do projeto. `make` sozinho, ou `make help`, imprime a lista.

| Alvo            | O que faz                                                                        |
| --------------- | -------------------------------------------------------------------------------- |
| `make install`  | Instala as dependências no `.venv` do projeto                                    |
| `make test`     | Roda a suíte de testes (`pytest -q`)                                             |
| `make run`      | Executa a CLI no grafo de exemplo, de A até D                                    |
| `make app`      | Abre a interface Streamlit                                                       |
| `make datasets` | Regera as redes sintéticas em `datasets/`, com as seeds fixas                    |
| `make evaluate` | Compara as redes maiores com o baseline e escreve `reports/comparacao_redes.csv` |
| `make evidence` | Gera relatórios, métricas e o gráfico interativo em `reports/`                   |
| `make reports`  | Roda os três acima na ordem correta                                              |
| `make check`    | `poetry check --lock` e a suíte de testes                                        |
| `make package`  | `poetry build` e o ZIP de entrega com `MANIFEST.sha256`                          |
| `make release`  | `check`, `reports` e `package`, na sequência                                     |
| `make clean`    | Remove `__pycache__` e `.pytest_cache`                                           |

Reprodutibilidade verificada: após `make reports`, os arquivos de `datasets/` voltam bit a bit idênticos, porque `generate_datasets.py` usa sementes fixas. Só os relatórios mudam, nos campos de tempo e data.

### Rodar apenas o algoritmo

Só o algoritmo: um arquivo de grafo entra, as matrizes e o caminho saem no terminal. Sem interface e sem relatórios.

```sh
poetry run floyd-warshall datasets/grafo_exemplo.csv --origem A --destino D
```

Saída completa deste comando:

```text
Matriz inicial
               A       B       D       C
A              0       3      10     INF
B            INF       0     INF       2
D            INF     INF       0     INF
C            INF     INF       1       0

Matriz de menores distâncias
               A       B       D       C
A              0       3       6       5
B            INF       0       3       2
D            INF     INF       0     INF
C            INF     INF       1       0

Consulta A -> D
Distância: 6
Caminho: A -> B -> C -> D
```

Leitura da saída:

- A **matriz inicial** é o grafo como veio do arquivo: `INF` marca um par sem aresta direta.
- A **matriz de menores distâncias** é o resultado do algoritmo. A célula `A, D` caiu de 10 para 6, porque o desvio `A -> B -> C -> D` custa `3 + 2 + 1`.
- As linhas de `D` continuam `INF` porque nenhuma aresta sai de `D`: o algoritmo não inventa caminho onde não existe.
- A ordem das colunas segue a ordem em que os vértices aparecem no arquivo, não a alfabética.

`--origem` e `--destino` são opcionais, mas andam juntos: sem eles a CLI imprime apenas as duas matrizes. Os três formatos de entrada funcionam no mesmo comando:

```sh
poetry run floyd-warshall examples/grafo_exemplo.txt --origem A --destino D
poetry run floyd-warshall datasets/rede_logistica_30.json
```

`make run` é o atalho para o exemplo em TXT.

### Pesos negativos e casos sem resposta

Três comandos cobrem o que o algoritmo faz nos limites. O terceiro é o único que falha, e falha de propósito.

```sh
poetry run floyd-warshall datasets/grafo_peso_negativo.json --origem A --destino C
poetry run floyd-warshall datasets/grafo_desconexo.json --origem A --destino Z
poetry run floyd-warshall datasets/grafo_ciclo_negativo.json --origem A --destino C
```

| Grafo              | Saída esperada                                           | Por quê                                                                       |
| ------------------ | -------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Com peso negativo  | `Distância: 2`, caminho `A -> B -> C`                    | Floyd-Warshall aceita aresta de peso negativo, ao contrário de Dijkstra       |
| Desconexo          | `Não existe caminho entre os vértices.`                  | A distância fica `INF` e a consulta responde sem erro                         |
| Com ciclo negativo | `Erro: Ciclo de peso negativo detectado envolvendo 'A'.` | Não existe caminho mínimo: dar mais uma volta no ciclo sempre sai mais barato |

No terceiro caso a mensagem vai para o `stderr` e o processo termina com código de saída 1, então o erro é detectável em script.

### Usar como biblioteca

O mesmo algoritmo, chamado de dentro de um script Python, sem passar por arquivo:

```python
from floyd_warshall.application.floyd_warshall_solver import FloydWarshallSolver
from floyd_warshall.infrastructure.networkx_graph import NetworkXGraph

graph = NetworkXGraph()
for origin, destination, weight in [("A", "B", 3), ("A", "D", 10), ("B", "C", 2), ("C", "D", 1)]:
    graph.add_edge(origin, destination, weight)

result = FloydWarshallSolver().solve(graph)

print(result.distance("A", "D"))  # 6.0
print(result.path("A", "D"))      # ['A', 'B', 'C', 'D']
print(result.distance("D", "A"))  # inf
```

Rode com `poetry run python seu_script.py`. O solver recebe qualquer objeto que implemente o contrato `Graph`, então `NetworkXGraph` pode ser trocado sem alterar o algoritmo.

## Simulação do algoritmo

Gravação da execução passo a passo sobre `grafo_exemplo.csv`, com o grafo, a matriz de distâncias e a linha do algoritmo em execução lado a lado.

[funcionamento-algoritmo.webm](https://github.com/user-attachments/assets/7e4991b9-5ee2-4351-8404-4b232d0140c1)

Para conduzir a simulação você mesmo, abra `study/simulacao.html` no navegador: dá para escolher o grafo, ajustar a velocidade e andar um passo por vez. O arquivo do vídeo está em [docs/funcionamento-algoritmo.webm](docs/funcionamento-algoritmo.webm).

## Demonstração rápida

1. Selecione `grafo_exemplo.csv` e clique em **Executar análise**.
2. Consulte o par de A até D: distância **6**, caminho **A, B, C, D**. O caminho aparece em vermelho no desenho.
3. Abra **Métricas e matrizes** para conferir distâncias e pares inalcançáveis.
4. Em **Baseline**, clique em **Comparar com baseline**: todas as distâncias devem coincidir.
5. Em **Relatórios**, baixe JSON, CSV e HTML.
6. Troque para `grafo_desconexo.json`, execute e consulte o par de A até Z: não existe caminho.
7. Em `grafo_peso_negativo.json`, o par de A até C custa **2**. Em `grafo_ciclo_negativo.json`, a execução é recusada com mensagem explicativa.
8. Em **Complexidade**, execute o experimento e baixe os resultados.

O [roteiro completo](docs/ROTEIRO_SEMINARIO.md) organiza a apresentação e o [relatório de validação](docs/VALIDACAO.md) reúne as evidências da entrega.

## Datasets

A pasta [datasets/](datasets/) contém grafos pequenos para demonstrar cada situação do algoritmo e redes sintéticas maiores, com 30, 60 e 100 vértices (106, 280 e 430 arestas) e um cenário desconexo de 40 vértices. O [catálogo e método de geração](docs/DATASETS.md) descreve cada arquivo. Todas as distâncias foram verificadas contra o baseline. Para redes acima de 50 vértices, o desenho exibe somente o caminho consultado.

### Formato CSV

CSV UTF-8, com as colunas obrigatórias abaixo. Os identificadores são textos; zeros à esquerda e rótulos como `NA` são preservados.

```csv
source,target,weight
A,B,3
A,D,10
B,C,2
C,D,1
```

### Formato JSON

JSON aceita um objeto com `edges` e `vertices` opcional, ou uma lista de arestas. Para vértices isolados, use JSON:

```json
{
  "vertices": ["A", "B", "Z"],
  "edges": [{ "source": "A", "target": "B", "weight": 3 }]
}
```

Também permanece disponível a entrada TXT legada da pasta [examples/](examples/), no formato `VERTICES A B C` seguido de linhas como `A B 3`.

### Regras de entrada

- Identificadores JSON devem ser strings não vazias. Pesos devem ser numéricos finitos; pesos negativos e zero são aceitos.
- Arestas repetidas entre a mesma origem e destino conservam o menor peso, independentemente da ordem.
- O grafo é dirigido: a aresta de A para B não implica a aresta de B para A. Para ambos os sentidos, declare as duas arestas.
- Laços são aceitos. Laço negativo é ciclo negativo. O algoritmo rejeita qualquer ciclo negativo, inclusive em componente desconexa, sem produzir relatório de caminhos mínimos.
- Dataset vazio é recusado; JSON com um vértice e nenhuma aresta é válido.
- Upload pode ser analisado sem salvar. O botão de salvar não substitui um dataset existente; renomeie o arquivo para salvar outra versão.
- A interface limita análises a 200 vértices e desenho a 50; grafos densos ainda podem ficar visualmente carregados. A biblioteca e a CLI não impõem esses limites.

## Algoritmo e complexidade

Inicializamos a diagonal com zero e os pares sem aresta com infinito. A matriz `next_vertex` permite reconstruir caminhos. Para cada intermediário k, atualizamos:

```text
d[i,j] = min(d[i,j], d[i,k] + d[k,j])
```

O invariante é: ao terminar a rodada k, as distâncias usam apenas os intermediários já processados. Por isso k fica no laço externo. Após as rodadas, uma diagonal negativa identifica um ciclo negativo. Caminho de um vértice para si próprio tem custo zero quando não há ciclo negativo.

Tempo no pior caso: **O(V³)**. Matrizes: **O(V²)** de memória. A implementação pula intermediários inalcançáveis, então o tempo observado depende também da conectividade. Reconstruir um caminho custa O(V) no pior caso; exportar os caminhos de todos os pares pode custar O(V³), além do algoritmo. A busca de índice por rótulo é linear nesta implementação.

O baseline roda Bellman-Ford do NetworkX para cada origem, aceitando pesos negativos. Seu limite teórico é O(V²E), com O(V²) para guardar a saída completa. A comparação verifica distâncias, pois caminhos diferentes podem ter o mesmo custo.

O experimento usa grafos dirigidos completos com pesos positivos determinísticos, V = 10, 20, 40, 80, 160, 320, aquecimento e mediana de três execuções. A coluna `ms_per_n3` ajuda a observar a escala; `time_ratio` divide a mediana pela da linha anterior (tende a 8 quando V dobra sob c·V³) e `loglog_slope` é log(t₂/t₁) / log(V₂/V₁), o expoente estimado entre linhas vizinhas (tende a 3). O experimento verifica a implementação, não prova a complexidade e não demonstra que um algoritmo é sempre mais rápido.

Referências: [Floyd-Warshall e suas complexidades (NetworkX)](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.dense.floyd_warshall.html) e [implementação de caminhos ponderados e Bellman-Ford (NetworkX)](https://networkx.org/documentation/stable/_modules/networkx/algorithms/shortest_paths/weighted.html).

A [justificativa da escolha](docs/JUSTIFICATIVA_ESCOLHA.md) apresenta vantagens, limitações e a comparação com alternativas. Os relatórios HTML e JSON exportados também incluem um resumo dessa análise.

## Métricas e relatórios

- Quantidade de vértices e arestas; densidade dirigida em porcentagem, excluindo laços: 100 × E_sem_laços / (V × (V - 1)).
- Pares alcançáveis e inalcançáveis, excluindo origem igual ao destino.
- Média, mínimo e máximo das distâncias finitas entre vértices distintos; ausência de valores gera `null`.
- Tempo em milissegundos, medido com `perf_counter`, sem rastreamento de memória.
- Pico de alocações Python em KiB, medido com `tracemalloc` em uma segunda execução. Não equivale ao consumo total de RAM e não inclui necessariamente alocações nativas. Se já houver rastreamento externo, o pico inclui esse contexto. A medição é destinada ao uso local sequencial.

JSON e HTML incluem dataset, arestas, métricas, matriz, caminhos e comparação, quando executada. JSON representa infinito como `null`. CSV contém uma linha por par, inclusive a diagonal, com distância vazia para pares inalcançáveis; rótulos iniciados por caracteres de fórmula recebem apóstrofo para leitura em planilhas. HTML é independente de rede e apresenta o relatório textual completo. O experimento de complexidade tem CSV separado.

A exportação HTML inclui cartões de métricas, resumo de alcançabilidade, caminhos, comparação com o baseline e análise crítica da escolha do algoritmo. Matrizes e tabelas completas ficam em seções expansíveis. Abra o HTML no navegador para ler offline ou use a opção de imprimir e salvar como PDF. Para incluir apêndices na impressão, expanda-os antes; redes grandes podem gerar muitas páginas.

## Arquitetura e SOLID

| Camada         | Componentes e responsabilidade                                            |
| -------------- | ------------------------------------------------------------------------- |
| Domínio        | `Graph`, `GraphReader`, `GraphVisualizer`, `ShortestPathResult`           |
| Aplicação      | `ShortestPathSolver`, Floyd-Warshall, avaliação, comparação e experimento |
| Infraestrutura | Adaptador NetworkX, leitores TXT/CSV/JSON, Plotly, baseline e exportação  |
| Apresentação   | `app.py` (Streamlit), CLI e renderização de console                       |

| Princípio                        | Como aparece no projeto                                                                                                                                                           |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **S** (responsabilidade única)   | Algoritmo, leitura, avaliação, desenho e exportação têm responsabilidades separadas.                                                                                              |
| **O** (aberto/fechado)           | Outros solvers podem implementar `ShortestPathSolver` sem alterar `EvaluationService`. Novos formatos de dataset ainda exigem estender `DatasetManager`, uma limitação conhecida. |
| **L** (substituição de Liskov)   | Os dois solvers entregam `ShortestPathResult` e rejeitam ciclos negativos.                                                                                                        |
| **I** (segregação de interfaces) | Contratos pequenos separam leitura, representação, visualização e cálculo.                                                                                                        |
| **D** (inversão de dependência)  | Floyd-Warshall depende de `Graph`; a avaliação recebe um `ShortestPathSolver`. A montagem das dependências concretas acontece na apresentação e nos scripts.                      |

Poetry gerencia bibliotecas e ambiente; isso é distinto da injeção de dependências do código. O [pyproject.toml](pyproject.toml) declara NetworkX, Streamlit, pandas, Plotly, python-dotenv e pytest; o [poetry.lock](poetry.lock) fixa a resolução. O `requirements.txt` é apenas uma alternativa de compatibilidade, sem substituir o lock.

## Verificar e empacotar

Um comando cobre a entrega inteira:

```sh
make release
```

Ele equivale a esta sequência, que também pode ser rodada passo a passo:

```sh
poetry check --lock
poetry run pytest -q
poetry run python scripts/generate_datasets.py
poetry run python scripts/evaluate_datasets.py
poetry run python scripts/generate_evidence.py
poetry build
poetry run python scripts/package_release.py
```

O ZIP de entrega contém aplicativo, datasets, código, testes, documentação, lock, relatórios de exemplo e distribuições Python. O wheel instala a biblioteca e a CLI; use o ZIP completo para a interface Streamlit, datasets e material do seminário. `.venv`, `.env`, caches e histórico Git não fazem parte da entrega.

## Documentação

- [Enunciado do seminário](docs/ENUNCIADO.md)
- [Roteiro do seminário](docs/ROTEIRO_SEMINARIO.md)
- [Slides da apresentação](docs/apresentacao.pdf)
- [Justificativa da escolha do algoritmo](docs/JUSTIFICATIVA_ESCOLHA.md)
- [Catálogo de datasets e método de geração](docs/DATASETS.md)
- [Relatório de validação da entrega](docs/VALIDACAO.md)
- Material de estudo em `study/`: abra `study/index.html` no navegador para o caderno com animações do algoritmo, ou `study/simulacao.html` para a simulação passo a passo

## Autoras

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/amandadiasdev">
        <img src="https://github.com/amandadiasdev.png" width="100" alt="Amanda Dias"><br>
        <sub><b>Amanda Dias</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/camillabdt">
        <img src="https://github.com/camillabdt.png" width="100" alt="Camilla Borchhardt"><br>
        <sub><b>Camilla Borchhardt</b></sub>
      </a>
    </td>
  </tr>
</table>
