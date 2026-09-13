1. Objetivo
O Seminário tem como propósito estudar e explicar um problema computacional pertencente à classe P. Cada grupo escolherá um problema, explicará sua complexidade, mostrará aplicações e implementará em Python um algoritmo que o resolve.

Ao final, cada estudante deverá ser capaz de descrever o problema em termos de instância, entrada, saída e restrições, justificar sua pertinência à classe P, relacionar o problema a situações reais e explicar o funcionamento do algoritmo implementado.

2. Organização
Grupos: até 5 estudantes, com formação livre.
Escolha do tema: cada grupo escolhe um tema da lista da Seção 3. Cada tema pode ser escolhido por apenas um grupo.
Anúncio, formação dos grupos e escolha dos temas: Aula 06 (03/09/2026).
Tira-dúvidas: Aulas 07 (08/09/2026) e 08 (10/09/2026).
Apresentações: Aulas 09 (15/09/2026) e 10 (17/09/2026).
Prazo para formar os grupos: 08/09/2026 às 23h59.

3. Tema do grupo (Floyd-Warshall)
	
Caminhos mais curtos entre todos os pares.

Descrição: Em vez de uma única origem, o problema pede a distância entre todos os pares de vértices. Floyd-Warshall usa uma matriz de distâncias e, para cada vértice intermediário k, verifica se passar por k encurta o caminho entre cada par (i, j). O grupo deve explicar por que o laço do vértice intermediário precisa ser o mais externo e mostrar como reconstruir o caminho, não só a distância.

Entrada: um grafo dirigido com pesos nas arestas e sem ciclos de peso negativo.
Saída: a menor distância entre cada par de vértices.
