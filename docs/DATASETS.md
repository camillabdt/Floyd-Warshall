# Catálogo de datasets

As redes maiores são **sintéticas**, geradas para este trabalho. Os nomes logístico, urbano e regional indicam cenários ilustrativos; não correspondem a cidades, empresas ou medições reais. P001, P002 etc. representam pontos de uma rede; os pesos são unidades abstratas de custo.

| Dataset | Vértices | Arestas | Uso |
|---|---:|---:|---|
| grafo_exemplo.csv | 4 | 4 | Explicação manual e resposta conhecida |
| grafo_desconexo.json | 5 | 3 | Vértice isolado e ausência de caminho |
| grafo_peso_negativo.json | 3 | 3 | Pesos negativos sem ciclo negativo |
| grafo_ciclo_negativo.json | 3 | 3 | Rejeição de ciclo negativo |
| grafo_reciproco.csv | 3 | 4 | Dois sentidos, peso zero e laço |
| rede_logistica_30.json / .csv | 30 | 106 | Demonstração de rotas alternativas |
| rede_urbana_60.json / .csv | 60 | 280 | Rede intermediária e desenho do caminho |
| rede_regional_100.json / .csv | 100 | 430 | 9.900 consultas entre vértices distintos |
| rede_desconexa_40.json | 40 | 97 | Dois componentes com 25 e 13 vértices e dois isolados |

## Geração e reprodução

Execute `poetry run python scripts/generate_datasets.py` na raiz para reproduzir os arquivos sintéticos. As sementes são 2026, 2027, 2028 e 2029, respectivamente. Em cada componente com mais de um vértice, um anel dirigido com pesos inteiros de 2 a 25 garante alcançabilidade. Arestas adicionais têm pesos de 2 a 50, com probabilidades 0,10, 0,065, 0,035 e 0,08. Arestas já presentes no anel são preservadas. Nenhuma aresta conecta os componentes do cenário desconexo.

Os CSV e JSON de uma mesma rede conectada representam exatamente as mesmas arestas. A versão desconexa usa somente JSON para preservar os dois vértices isolados.

## Consultas verificadas

- Rede de 30: P001 → P030 custa **74**, por P001 → P009 → P024 → P025 → P029 → P030.
- Rede de 60: P001 → P060 custa **36**, por P001 → P019 → P059 → P060.
- Rede de 100: P001 → P100 custa **57**, por P001 → P044 → P050 → P058 → P100.
- Rede desconexa: P001 → P040 não tem caminho; há **756 pares alcançáveis e 804 inalcançáveis**, excluindo a diagonal.

Todas as distâncias das quatro redes foram comparadas com Bellman-Ford. Os resultados medidos estão em `reports/comparacao_redes.csv`; gere-os novamente com `poetry run python scripts/evaluate_datasets.py`.

Para o seminário, comece pelo exemplo de quatro vértices para explicar a conta, passe à rede de 30 para mostrar uma análise menos trivial e use a rede de 100 para discutir escala. Isso combina verificabilidade manual e volume de dados.
