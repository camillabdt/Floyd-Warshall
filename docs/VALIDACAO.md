# Validação da entrega

Validação realizada em 13/09/2026 com Python 3.12, Poetry 1.8.2 e as versões registradas em `reports/ambiente.json`.

## Resultados

- Instalação limpa: `poetry install --no-interaction`, concluída com o lock existente e instalação do projeto.
- Consistência de dependências: `poetry check --lock`, resultado `All set!`.
- Testes: `poetry run pytest -q`, **51 aprovados em 6,56 segundos** na execução registrada. O tempo varia entre execuções.
- Distribuição: `poetry build`, wheel e sdist gerados.
- Relatórios JSON, CSV e HTML e grafo HTML autossuficiente gerados pelo script de evidências.
- Servidor Streamlit iniciado localmente; a tela carregou 100 vértices e 430 arestas e exibiu distância 57 para P001 → P100. A prévia perdeu conexão após encerramento do servidor; não foi concluída a inspeção visual do grafo maior. O fluxo e a figura foram verificados pelos testes automatizados.

## Cobertura funcional

Exemplos conhecidos, reconstrução do caminho e soma dos pesos; 12 grafos acíclicos gerados com pesos positivos e negativos comparados com Bellman-Ford; ciclo negativo, laço negativo desconexo, vazio e vértice único; validação de entradas CSV/JSON; preservação de identificadores; arestas repetidas; métricas; serialização de infinito; escape de HTML; desenho de arestas recíprocas e laços; fluxo Streamlit, troca de dataset, descarte de resultados anteriores, baseline, ciclo negativo e visualização de caminho em rede maior.

As quatro redes maiores também foram verificadas em todos os pares. Resultados pontuais da execução registrada:

| Rede      |   V |   E | Tempo Floyd (ms) | Tempo baseline (ms) | Distâncias |
| --------- | --: | --: | ---------------: | ------------------: | ---------- |
| Logística |  30 | 106 |             1,69 |                5,42 | Coincidem  |
| Desconexa |  40 |  97 |             1,66 |                4,73 | Coincidem  |
| Urbana    |  60 | 280 |            15,45 |               25,21 | Coincidem  |
| Regional  | 100 | 430 |           108,54 |              110,03 | Coincidem  |

Esses tempos incluem a preparação interna de cada solver, excluem a leitura do dataset e não são médias de múltiplas execuções. Não estabelecem superioridade geral. Dados completos: `reports/comparacao_redes.csv`.

O experimento separado de grafos completos, com aquecimento e mediana de três execuções, registrou aproximadamente 0,13; 0,84; 5,93; 44,85; 351,57 e 2.829,37 ms para 10, 20, 40, 80, 160 e 320 vértices na execução de 13/09/2026 que gerou o relatório final. Fonte: `reports/complexidade.csv`. A razão entre medianas de tamanhos vizinhos foi 6,69; 7,04; 7,56; 7,84 e 8,05, e a inclinação log-log correspondente 2,74; 2,82; 2,92; 2,97 e 3,01. Sob tempo = c·V³, dobrar V multiplica o tempo por 8 e a inclinação vale 3; a aproximação desses valores conforme V cresce é coerente com um custo fixo por execução que pesa nos grafos pequenos. Seis pontos verificam a implementação, mas a complexidade é fundamentada na análise dos laços, não ajustada às medições.

## Limites da validação

Os testes não constituem prova formal nem cobrem todos os possíveis pesos de ponto flutuante. A instalação foi verificada neste ambiente Linux/Python 3.12, sem teste em Windows ou macOS. A interface foi testada por AppTest e no navegador; não houve ensaio com usuários ou medição de acessibilidade. Os dados maiores são sintéticos e não sustentam conclusões sobre uma rede real.
