# Floyd-Warshall com SOLID e gerenciamento de dependências

Projeto acadêmico em Python para resolver **caminhos mais curtos entre todos os pares** com uma implementação própria do algoritmo **Floyd-Warshall**.

O projeto foi organizado para atender quatro objetivos:

1. implementar Floyd-Warshall sem usar uma função pronta de caminho mínimo;
2. permitir diferentes grafos de entrada sem alterar o código;
3. aplicar princípios SOLID;
4. usar **Poetry** para gerenciamento de dependências.

## O que o programa faz

A entrada é um arquivo de texto com uma declaração opcional de vértices e arestas no formato:

```text
VERTICES A B C D
origem destino peso
```

Exemplo:

```text
VERTICES A B C D
A B 3
A D 10
B C 2
C D 1
```

O programa lê o arquivo, cria o grafo, constrói a matriz inicial, executa Floyd-Warshall, imprime a matriz final, reconstrói um caminho solicitado e detecta ciclos negativos.

## Exemplo visual

```text
A --3--> B --2--> C --1--> D
 \----------------10------> D
```

Direto, `A -> D = 10`. Pelo caminho `A -> B -> C -> D`, o custo é `3 + 2 + 1 = 6`. Portanto, o algoritmo atualiza a menor distância para `6`.

## Estrutura

```text
floyd_warshall_solid_poetry/
├── pyproject.toml
├── requirements.txt
├── Makefile
├── README.md
├── examples/
│   ├── grafo_exemplo.txt
│   ├── grafo_peso_negativo.txt
│   └── grafo_ciclo_negativo.txt
├── src/
│   └── floyd_warshall/
│       ├── domain/
│       │   ├── graph.py
│       │   ├── graph_reader.py
│       │   └── shortest_path_result.py
│       ├── application/
│       │   ├── shortest_path_solver.py
│       │   └── floyd_warshall_solver.py
│       ├── infrastructure/
│       │   ├── networkx_graph.py
│       │   └── text_graph_reader.py
│       └── presentation/
│           ├── console_renderer.py
│           └── cli.py
└── tests/
    ├── test_floyd_warshall.py
    └── test_text_graph_reader.py
```

## Como o Floyd-Warshall funciona

A atualização central é:

```text
dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

O algoritmo percorre:

```python
for k in range(V):
    for i in range(V):
        for j in range(V):
            ...
```

- `i`: origem;
- `j`: destino;
- `k`: vértice intermediário permitido naquela rodada.

O `k` precisa estar no laço externo porque cada rodada amplia o conjunto de vértices que podem ser usados como intermediários. Isso preserva a recorrência da programação dinâmica.

## Complexidade

Com `V` vértices:

```text
Tempo:  O(V³)
Espaço: O(V²)
```

Como `V³` é polinomial, o algoritmo executa em tempo polinomial.

## NetworkX: o que ele faz aqui?

NetworkX é usado **somente para representar o grafo**. O projeto não chama:

```python
nx.floyd_warshall(...)
nx.shortest_path(...)
```

para resolver o problema.

A construção da matriz, os três laços, a atualização das distâncias, a matriz `next`, a reconstrução do caminho e a detecção de ciclo negativo são implementadas pelo próprio projeto.

## SOLID

### S — Single Responsibility Principle

Cada classe tem uma responsabilidade principal:

- `TextGraphReader`: lê arquivo;
- `NetworkXGraph`: representa o grafo;
- `FloydWarshallSolver`: executa o algoritmo;
- `ShortestPathResult`: guarda e consulta o resultado;
- `ConsoleRenderer`: imprime no terminal.

### O — Open/Closed Principle

É possível adicionar `JsonGraphReader`, `CsvGraphReader` ou outro algoritmo sem alterar o núcleo existente.

### L — Liskov Substitution Principle

`FloydWarshallSolver` trabalha com a abstração `Graph`. Uma implementação válida de `Graph` pode substituir `NetworkXGraph` sem quebrar o solver.

### I — Interface Segregation Principle

As abstrações são pequenas e específicas: `Graph`, `GraphReader` e `ShortestPathSolver`.

### D — Dependency Inversion Principle

O solver depende da abstração `Graph`, e não de `networkx.DiGraph`. NetworkX fica restrito à infraestrutura.

## Gerenciamento de dependências

O projeto usa **Poetry** para dependências externas e **injeção manual de dependências** no `cli.py` (Composition Root). Assim, `TextGraphReader`, `FloydWarshallSolver` e `ConsoleRenderer` são conectados em um único ponto da aplicação, sem acoplar o solver ao NetworkX ou à interface de terminal.

O projeto usa **Poetry** para pacotes e ambiente virtual.

Dependências de execução:

```text
networkx
```

Dependências de desenvolvimento:

```text
pytest
```

Tudo é declarado em `pyproject.toml`.

### Instalar dependências

Na raiz do projeto:

```bash
poetry install
```

### Executar

```bash
poetry run floyd-warshall examples/grafo_exemplo.txt --origem A --destino D
```

Ou:

```bash
poetry run python -m floyd_warshall.presentation.cli examples/grafo_exemplo.txt --origem A --destino D
```

### Executar testes

```bash
poetry run pytest
```

## Saída esperada do exemplo principal

```text
Matriz inicial
         A        B        D        C
A        0        3       10      INF
B      INF        0      INF        2
D      INF      INF        0      INF
C      INF      INF        1        0

Matriz de menores distâncias
         A        B        D        C
A        0        3        6        5
B      INF        0        3        2
D      INF      INF        0      INF
C      INF      INF        1        0

Consulta A -> D
Distância: 6
Caminho: A -> B -> C -> D
```

> A ordem das colunas segue a ordem em que os vértices aparecem no grafo.

## Pesos negativos

Floyd-Warshall aceita arestas de peso negativo, desde que não exista ciclo de peso negativo.

Exemplo:

```text
A B 4
A C 5
B C -2
```

O menor caminho de `A` para `C` passa por `B` e custa `2`.

## Ciclos de peso negativo

Ao final, se `dist[i][i] < 0` para algum vértice, existe ciclo de peso negativo. Nesse caso o programa interrompe a execução com uma mensagem clara.

## Entrada genérica

Para testar outro grafo, não é necessário alterar o código. Basta criar outro `.txt`:

```text
A B 7
B D 2
A C 4
C D 1
```

E executar:

```bash
poetry run floyd-warshall meu_grafo.txt --origem A --destino D
```

## Perguntas comuns do professor

**Por que NetworkX?**  
Para representar o grafo sem amarrar o algoritmo a uma matriz criada manualmente.

**NetworkX calcula os caminhos?**  
Não. A implementação do Floyd-Warshall é nossa.

**Por que `k` fica por fora?**  
Porque cada iteração libera um novo vértice intermediário e depende dos resultados consolidados das iterações anteriores.

**Onde está SOLID?**  
Na separação de responsabilidades e no uso de abstrações entre domínio, aplicação, infraestrutura e apresentação.

**Onde está o gerenciamento de dependências?**  
No `pyproject.toml`, com Poetry.

## Arquitetura resumida

```text
arquivo .txt
     |
     v
TextGraphReader
     |
     v
Graph (abstração)
     ^
     |
NetworkXGraph
     |
     v
FloydWarshallSolver
     |
     v
ShortestPathResult
     |
     v
ConsoleRenderer
```

O ponto principal é: **o algoritmo depende da abstração do grafo, não do NetworkX nem da forma de entrada**.
