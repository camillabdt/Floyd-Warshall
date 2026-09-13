# Justificativa da escolha do Floyd-Warshall

## Adequação ao objetivo do trabalho

Escolhemos o algoritmo Floyd-Warshall porque o projeto exige calcular caminhos mínimos entre todos os pares, exibir uma matriz completa de distâncias e permitir consultas entre diferentes origens e destinos. Sua formulação por programação dinâmica é adequada para demonstrar a evolução das distâncias, implementar a reconstrução dos caminhos e discutir complexidade. A implementação também aceita pesos negativos, desde que não existam ciclos de peso negativo.

A escolha prioriza a adequação funcional e didática ao trabalho. Não significa que Floyd-Warshall seja o algoritmo mais rápido para qualquer rede.

## Em quais situações a escolha é melhor

Para muitas consultas sobre um mesmo grafo, calcular previamente todas as distâncias permite reutilizar o resultado. Isso atende diretamente à interface e aos relatórios do projeto, que abrangem todos os pares. Comparado a executar Bellman-Ford para cada origem, Floyd-Warshall tem limite de tempo O(V³), enquanto o baseline tem O(V²E). Em grafos densos, com E proporcional a V², essa diferença favorece o limite teórico do Floyd-Warshall.

A recorrência única e as matrizes tornam a implementação relativamente simples de inspecionar e explicar. O suporte a pesos negativos amplia o conjunto de entradas em relação ao Dijkstra convencional. Essa vantagem funcional é demonstrada pelo dataset com aresta negativa; as redes sintéticas maiores usam apenas pesos positivos e, portanto, não precisam desse recurso.

## Em quais situações a escolha é pior

O custo O(V³) cresce rapidamente com a quantidade de vértices, e a memória O(V²) exige armazenar pares mesmo quando há poucas arestas. Para uma única origem ou poucas consultas, calcular a matriz inteira pode desperdiçar processamento. Nesse cenário, Dijkstra é uma alternativa quando os pesos são não negativos, e Bellman-Ford quando há pesos negativos.

Para redes grandes e esparsas, Dijkstra a partir das origens necessárias, ou Johnson para todos os pares com possíveis pesos negativos, são alternativas a avaliar. As redes maiores deste projeto são esparsas e têm pesos positivos: logo, não devemos afirmar que Floyd-Warshall seja a melhor escolha de desempenho para esses dados sem compará-lo também com essas alternativas.

Mudanças no grafo exigem uma nova análise nesta implementação. Além disso, ciclos negativos impedem mínimos finitos para os pares afetados; a aplicação rejeita toda a execução quando encontra um desses ciclos. Essa impossibilidade matemática não é resolvida simplesmente trocando o algoritmo por Bellman-Ford ou Johnson.

## Comparação das opções

| Opção | Quando considerar | Limitação em relação ao objetivo do projeto |
|---|---|---|
| Floyd-Warshall | Todos os pares, matrizes completas, escala moderada, apresentação de programação dinâmica | Tempo cúbico e memória quadrática |
| Dijkstra | Pesos não negativos, uma origem ou origens selecionadas | Não atende diretamente aos exemplos com pesos negativos |
| Bellman-Ford | Uma origem com pesos negativos; validação independente | Repetir para todas as origens pode ser caro, especialmente em grafos densos |
| Johnson | Todos os pares em redes esparsas, inclusive com pesos negativos | Maior complexidade de implementação; não foi medido neste trabalho |

## O que os resultados permitem concluir

Na execução registrada, a rede de 100 vértices e 430 arestas levou aproximadamente 108,54 ms com Floyd-Warshall e 110,03 ms com Bellman-Ford por origem. A diferença é pequena e deriva de uma medição pontual, sem repetições suficientes para estabelecer superioridade estatística. Nas quatro redes maiores, todas as distâncias coincidiram com o baseline, o que fornece evidência de correção para os casos avaliados.

A medição inclui a preparação interna de cada solver, inclusive a construção do grafo do baseline. Portanto, compara as implementações entregues, não apenas as operações centrais dos algoritmos. Dijkstra e Johnson não foram medidos. Não há evidência experimental para declarar vantagem sobre eles.

Concluímos que Floyd-Warshall é uma escolha adequada para os objetivos funcionais e didáticos deste projeto e para a escala demonstrada. Sua principal desvantagem é a escalabilidade. Em uma aplicação com redes muito maiores, poucas consultas ou alterações frequentes, a escolha deveria ser reavaliada com benchmarks representativos.

## Referências

- [NetworkX — visão geral de caminhos mínimos](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html).
- [NetworkX — Floyd-Warshall, tempo O(V³) e espaço O(V²)](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.dense.floyd_warshall.html).
- [NetworkX — Johnson e suporte a pesos negativos](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.johnson.html).
