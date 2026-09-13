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

| Rede | V | E | Tempo Floyd (ms) | Tempo baseline (ms) | Distâncias |
|---|---:|---:|---:|---:|---|
| Logística | 30 | 106 | 1,69 | 5,42 | Coincidem |
| Desconexa | 40 | 97 | 1,66 | 4,73 | Coincidem |
| Urbana | 60 | 280 | 15,45 | 25,21 | Coincidem |
| Regional | 100 | 430 | 108,54 | 110,03 | Coincidem |

Esses tempos incluem a preparação interna de cada solver, excluem a leitura do dataset e não são médias de múltiplas execuções. Não estabelecem superioridade geral. Dados completos: `reports/comparacao_redes.csv`.

O experimento separado de grafos completos, com aquecimento e mediana de três execuções, registrou aproximadamente 0,17; 1,15; 8,10 e 54,09 ms para 10, 20, 40 e 80 vértices. Fonte: `reports/complexidade.csv`. A variação de tempo normalizado por V³ mostra a influência de overhead, cache, dados e ambiente; a complexidade é fundamentada na análise dos laços, não ajustada a esses quatro pontos.

## Limites da validação

Os testes não constituem prova formal nem cobrem todos os possíveis pesos de ponto flutuante. A instalação foi verificada neste ambiente Linux/Python 3.12, sem teste em Windows ou macOS. A interface foi testada por AppTest e no navegador; não houve ensaio com usuários ou medição de acessibilidade. Os dados maiores são sintéticos e não sustentam conclusões sobre uma rede real.
