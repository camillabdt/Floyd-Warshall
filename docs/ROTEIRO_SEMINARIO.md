# Roteiro do seminário — 12 a 15 minutos

## Preparação

Abra o aplicativo antes da apresentação. Execute os testes e mantenha os relatórios de exemplo em `reports/` disponíveis para uma demonstração alternativa. O projeto é local; depois da instalação, não depende de conexão. Ajuste nomes da equipe e disciplina nos materiais institucionais antes de enviar, se forem exigidos.

## 0–2 min — Problema e exemplo

“Queremos calcular os menores caminhos entre todos os pares de vértices de um grafo dirigido e ponderado. Isso se aplica, por exemplo, a uma rede de rotas com custos. Implementamos Floyd-Warshall e construímos um laboratório para carregar dados, avaliar e exportar resultados.”

Mostre `grafo_exemplo.csv`. Compare A → D direto, custo 10, com A → B → C → D, custo 3 + 2 + 1 = 6. Explique que pesos são custos; valores negativos são abstratos e não representam necessariamente distâncias físicas.

## 2–5 min — Implementação própria

Abra `src/floyd_warshall/application/floyd_warshall_solver.py`.

Explique diagonal zero, infinito para ausência de caminho e matriz do próximo vértice. Mostre a recorrência e os três laços. Cada rodada libera um intermediário; k fica por fora para preservar o invariante. Depois de considerar B, A → C melhora para 5; considerando C, A → D melhora para 6. A ordem concreta de vértices segue a entrada, sem alterar o resultado final.

“O cálculo principal não chama o Floyd-Warshall do NetworkX. O NetworkX serve de representação e layout, e Bellman-Ford é chamado separadamente como baseline.”

## 5–8 min — Demonstração funcional

Execute a análise e consulte A → D. Mostre o caminho vermelho e as duas matrizes. Explique pares alcançáveis, densidade e distâncias média, mínima e máxima. Tempo e memória são medidos em execuções separadas; o pico Python não é RAM total.

Troque para `grafo_desconexo.json`; os resultados anteriores são descartados. Execute e consulte A → Z. Depois execute `grafo_peso_negativo.json`, demonstrando A → C = 2. Por último, `grafo_ciclo_negativo.json` deve gerar uma mensagem de ciclo negativo. Retorne ao exemplo principal para continuar.

## 8–10 min — Baseline e complexidade

Clique em comparar. A comparação confere todos os pares com tolerância numérica, não exige caminhos idênticos em empates. Bellman-Ford foi escolhido porque aceita pesos negativos.

Floyd-Warshall: O(V³) em tempo e O(V²) em espaço. Bellman-Ford por origem: O(VE); para V origens, O(V²E). Execute o experimento de 10 a 320 vértices (o último tamanho leva alguns segundos). Aponte as colunas de razão e inclinação log-log: se o tempo fosse c·V³, dobrar V multiplicaria o tempo por 8 e a inclinação seria 3; os valores medidos se aproximam de 8 e 3 conforme V cresce. Diga que mediana e aquecimento reduzem ruído, mas medições não provam uma lei assintótica nem uma vantagem universal: quem prova O(V³) é a contagem dos três laços.

## 10–12 min — Engenharia e entrega

Use a tabela SOLID do README para mostrar exemplos concretos. Destaque `EvaluationService(ShortestPathSolver)` e a separação da infraestrutura. Reconheça que novos formatos ainda exigem alterar o gerenciador de datasets.

Mostre `pyproject.toml` e `poetry.lock`: dependências declaradas e resolução reproduzível. Diferencie isso da injeção de dependências. Mostre o resultado dos testes e baixe JSON, CSV e HTML. Explique `null` ou campo vazio para inalcançáveis.

## 12–15 min — Perguntas

**Por que não Dijkstra?** Esta versão aceita pesos negativos, portanto escolhemos Bellman-Ford como baseline.

**O que acontece com ciclo negativo?** Não existe mínimo finito para os pares afetados; a aplicação rejeita a análise inteira, inclusive se o ciclo estiver em componente desconexa.

**Por que O(V³)?** No pior caso, cada um dos V intermediários considera os V² pares. Há atalhos para infinito, mas eles não mudam esse limite.

**O grafo é não dirigido?** Não; é preciso declarar ambos os sentidos quando essa for a intenção.

**Como sabem que está correto?** Exemplos com resposta conhecida, casos extremos, comparação independente e reconstrução de caminhos em grafos gerados, além de teste do fluxo Streamlit.

**Quais são as limitações?** A interface limita tamanhos; desempenho depende da entrada e da máquina; pesos usam ponto flutuante; o relatório de todos os caminhos pode crescer cubicamente; o gerenciador concentra os formatos CSV/JSON.

## Se a demonstração falhar

Use `reports/relatorio_final.html` para mostrar a saída calculada. Pelo terminal, execute `poetry run floyd-warshall datasets/grafo_exemplo.csv --origem A --destino D`. Não improvise resultados de tempo: apresente apenas os medidos e registrados.

## Ampliação da demonstração com as redes maiores

Após explicar o exemplo de quatro vértices, carregue `rede_logistica_30.json` e consulte P001 → P030: custo 74. Mostre que agora há 106 arestas e várias alternativas de rota. Em seguida, use `rede_regional_100.json`: são 100 vértices, 430 arestas e 9.900 pares distintos. P001 → P100 custa 57. Acima de 50 vértices, o desenho mostra só o caminho consultado para manter a leitura; a matriz continua completa.

Deixe claro que são dados sintéticos reproduzíveis, com sementes e método descritos em `docs/DATASETS.md`. Mostre `reports/comparacao_redes.csv` para comprovar que a validação também abrangeu as redes maiores. Se o tempo for curto, substitua parte da navegação pelas matrizes pequenas por essa demonstração.

## Como defender a escolha

“Escolhemos Floyd-Warshall porque precisamos de todos os pares e de uma implementação clara para demonstrar programação dinâmica. Ele aceita pesos negativos, mas custa O(V³) em tempo e O(V²) em memória. Para redes grandes e esparsas, ou poucas consultas, outras opções podem ser melhores. Nossos testes demonstram concordância com Bellman-Ford; não provam superioridade universal. As redes maiores têm pesos positivos, então Dijkstra também seria uma comparação importante em trabalhos futuros.”

A análise completa está em `docs/JUSTIFICATIVA_ESCOLHA.md`.
