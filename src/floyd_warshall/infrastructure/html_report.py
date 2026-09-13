"""Relatório HTML autossuficiente, responsivo e preparado para impressão."""
from html import escape
from math import isfinite


STYLE = '''
:root{--ink:#172b3a;--muted:#526678;--blue:#153e58;--teal:#087f83;--line:#dae4e9;--paper:#fff}
*{box-sizing:border-box}body{margin:0;background:#edf2f5;color:var(--ink);font:15px/1.65 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1120px;margin:32px auto;background:var(--paper);box-shadow:0 16px 60px #17364d12}
header{padding:48px 56px;background:var(--blue);color:white;border-top:7px solid #2bc4b3}
.eyebrow{text-transform:uppercase;letter-spacing:.18em;font-size:11px;font-weight:750;color:#a8e5e0}
h1{font-size:clamp(32px,5vw,48px);line-height:1.1;letter-spacing:-.04em;margin:18px 0}header p{color:#d5e4ec;max-width:730px}
.dataset{display:inline-block;border:1px solid #80b7c077;border-radius:7px;padding:7px 12px;font-size:13px;overflow-wrap:anywhere}
.body{padding:36px 56px}section{margin:0 0 36px}h2{font-size:23px;letter-spacing:-.025em;margin:0 0 18px}h3{font-size:16px;margin:0 0 10px}
.number{color:var(--teal);font-size:12px;letter-spacing:.1em;display:block;margin-bottom:6px;font-weight:750}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.card{border:1px solid var(--line);border-radius:9px;padding:18px;background:#fafcfd}
.label{font-size:12px;color:var(--muted)}.value{font-size:29px;font-weight:700;line-height:1.25;margin:8px 0}.unit{font-size:13px;font-weight:500;color:var(--muted)}
.note{font-size:12px;color:var(--muted);margin:12px 0}.callout{border-left:4px solid var(--teal);background:#eff9f7;padding:16px 20px;border-radius:0 8px 8px 0}
.columns{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{border:1px solid var(--line);padding:22px;border-radius:9px}.panel.warn{border-top:4px solid #ce9252}.panel.good{border-top:4px solid var(--teal)}
ul{padding-left:20px;margin:0}li{margin:7px 0}.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:8px}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:11px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}thead{background:#eff4f7}th{font-weight:650}tbody tr:nth-child(even){background:#fafcfd}tbody tr:last-child td{border-bottom:0}
.badge{font-size:12px;padding:5px 10px;border-radius:20px;background:#e3f5ed;color:#185d47;display:inline-block;font-weight:650}.badge.fail{background:#fdebea;color:#963a32}
.bar{height:12px;border-radius:8px;background:#dbe4ec;overflow:hidden;margin:14px 0 6px}.bar span{display:block;height:100%;background:var(--teal)}
summary{cursor:pointer;padding:15px 0;font-weight:650}details{margin-top:12px}.route{max-width:460px}.matrix td{text-align:right;font-variant-numeric:tabular-nums}.matrix th{white-space:nowrap}.muted{color:var(--muted)}
footer{padding:22px 56px;border-top:1px solid var(--line);color:var(--muted);font-size:12px}a{color:var(--teal)}
@media(max-width:700px){main{margin:0}.body,header,footer{padding:26px 22px}.grid{grid-template-columns:repeat(2,1fr)}.columns{grid-template-columns:1fr}}
@media print{@page{size:A4;margin:15mm}body{background:white;font-size:11px}main{margin:0;max-width:none;box-shadow:none}header{padding:24px;color:#172b3a;background:#edf4f7}header p,.eyebrow{color:#365766}.body{padding:24px 0}footer{padding:15px 0}h1{font-size:32px}h2{font-size:19px}h2,h3,summary{break-after:avoid}.card,.panel,.callout,tr{break-inside:avoid}.value{font-size:23px}th,td{padding:7px}.scroll{overflow:visible}.matrix{font-size:8px}.matrix th,.matrix td{padding:4px}.screen{display:none}a{color:inherit}thead{display:table-header-group}}
'''


def fmt(value, digits=2):
    if value is None or not isfinite(value):
        return '—'
    return f'{value:,.{digits}f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def table(headers, rows, cls=''):
    head = ''.join(f'<th scope="col">{escape(str(x))}</th>' for x in headers)
    body = ''.join('<tr>' + ''.join(f'<td>{escape(str(x))}</td>' for x in row) + '</tr>' for row in rows)
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def render_report(data):
    m = data['metrics']
    vertices = data['vertices']
    n = len(vertices)
    reachable, unreachable = m['reachable_pairs'], m['unreachable_pairs']
    total = reachable + unreachable
    percentage = 100 * reachable / total if total else 0
    cards = [('Vértices', str(m['vertices']), 'pontos da rede'),
             ('Arestas', str(m['edges']), 'conexões dirigidas'),
             ('Tempo de execução', fmt(m['execution_time_ms'], 3), 'ms · sem instrumentação'),
             ('Pico de memória Python', fmt(m['peak_memory_kb']), 'KiB · execução separada')]
    metrics = ''.join(f'<div class="card"><div class="label">{label}</div><div class="value">{value}</div><div class="unit">{unit}</div></div>' for label,value,unit in cards)
    overview = table(['Indicador', 'Resultado', 'Interpretação'], [
        ['Densidade', fmt(m['density'])+'%', 'Conexões existentes entre vértices distintos.'],
        ['Distância média', fmt(m['average_distance']), 'Média dos custos mínimos finitos; exclui a diagonal.'],
        ['Menor / maior distância', fmt(m['minimum_distance'])+' / '+fmt(m['maximum_distance']), 'Extremos entre pares distintos alcançáveis.']])
    comparison = data.get('comparison')
    if comparison:
        matches = comparison['distances_match']
        status = 'Todas as distâncias coincidem' if matches else 'Foram encontradas divergências'
        comparison_html = f'<p><span class="badge {"" if matches else "fail"}">{status}</span></p>'
        comparison_html += table(['Algoritmo', 'Tempo (ms)', 'Pico Python (KiB)'], [
            ['Floyd-Warshall próprio', fmt(comparison['floyd_warshall']['execution_time_ms'],3),fmt(comparison['floyd_warshall']['peak_memory_kb'])],
            ['Bellman-Ford por origem',fmt(comparison['bellman_ford']['execution_time_ms'],3),fmt(comparison['bellman_ford']['peak_memory_kb'])]])
        comparison_html += '<p class="note">Medições pontuais da comparação, distintas da execução principal acima. Incluem a preparação interna de cada solver. Não demonstram superioridade estatística ou universal. A verificação usa tolerância de 1e-9; caminhos diferentes podem ter o mesmo custo.</p>'
    else:
        comparison_html = '<div class="callout">Comparação não executada nesta análise. Na aplicação, execute “Comparar com baseline” antes de exportar para incluir os resultados.</div>'
    # Resumo legível; todos os pares continuam disponíveis no apêndice HTML.
    index = {v:i for i,v in enumerate(vertices)}
    path_rows = []
    for item in data['paths']:
        u,v,path = item['source'],item['target'],item['path']
        distance = data['distances'][index[u]][index[v]]
        path_rows.append([u,v,fmt(distance),' → '.join(path) if path else 'Sem caminho'])
    sample = [row for row in path_rows if row[0] != row[1] and row[3] != 'Sem caminho'][:8]
    path_summary = table(['Origem','Destino','Custo mínimo','Caminho'], sample) if sample else '<p>Nenhum par de vértices distintos possui caminho.</p>'
    all_paths = table(['Origem','Destino','Custo mínimo','Caminho'],path_rows)
    # Matriz prévia evita tabelas de 100 colunas no corpo principal.
    limit = min(n, 12)
    matrix_rows = [[vertices[i]]+[fmt(x) for x in data['distances'][i][:limit]] for i in range(limit)]
    matrix = table(['Origem / destino']+vertices[:limit],matrix_rows,'matrix')
    matrix_note = ('Prévia dos primeiros 12 vértices. A tabela completa de pares abaixo abrange todos os vértices.' if n > 12 else 'Matriz completa. A diagonal representa custo zero; “—” indica ausência de caminho.')
    edges = table(['Origem','Destino','Peso'],[[u,v,fmt(w)] for u,v,w in data['edges']])
    negative = any(w < 0 for _,_,w in data['edges'])
    weight_note = ('Este dataset contém pesos negativos, um requisito que o Dijkstra convencional não atende.' if negative else 'Este dataset não contém pesos negativos: Dijkstra também é uma alternativa válida a avaliar.')
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relatório • {escape(str(data['dataset']))} • Floyd-Warshall</title><style>{STYLE}</style></head>
<body><main><header><div class="eyebrow">Laboratório de grafos · relatório de análise</div>
<h1>Caminhos mínimos.<br>Resultados e decisões.</h1><p>Uma análise de conectividade, custos e desempenho com implementação própria do algoritmo Floyd-Warshall.</p>
<div class="dataset">Dataset · {escape(str(data['dataset']))}</div></header><div class="body">
<section><span class="number">01 / VISÃO GERAL</span><h2>A rede em números</h2><div class="grid">{metrics}</div>
<p class="note">Tempo em milissegundos. Pico de alocações Python em outra execução; não representa a RAM total do processo.</p>
<div class="callout">A análise identificou <strong>{reachable:,} pares alcançáveis</strong> e <strong>{unreachable:,} inalcançáveis</strong>, excluindo consultas de um vértice para ele mesmo.</div>
<div class="bar" role="img" aria-label="{fmt(percentage)} por cento dos pares alcançáveis"><span style="width:{percentage:.2f}%"></span></div>
<p class="note">{fmt(percentage)}% dos pares distintos são alcançáveis.{ ' Não há pares distintos neste dataset.' if not total else ''}</p>{overview}</section>
<section><span class="number">02 / RESULTADOS</span><h2>Custos e caminhos encontrados</h2>{path_summary}
<p class="note">Até oito pares alcançáveis, na ordem dos vértices de entrada. Custos são apresentados com duas casas decimais; os arquivos JSON e CSV preservam a precisão numérica exportada.</p>
<details><summary>Matriz de distâncias · {n} vértices</summary><p class="note">{matrix_note}</p>{matrix}</details>
<details><summary>Consultar todos os {len(path_rows):,} pares, incluindo a diagonal</summary>{all_paths}</details>
<p class="note screen">Para imprimir ou salvar em PDF, use a opção de impressão do navegador. Expanda os apêndices antes de imprimir se quiser incluí-los; em redes grandes, eles podem ocupar muitas páginas.</p></section>
<section><span class="number">03 / VERIFICAÇÃO</span><h2>Comparação com o baseline</h2><p>Bellman-Ford do NetworkX é executado a partir de cada origem para verificar as distâncias calculadas.</p>{comparison_html}</section>
<section><span class="number">04 / ANÁLISE CRÍTICA</span><h2>Por que escolher Floyd-Warshall?</h2>
<div class="columns"><div class="panel good"><h3>Onde a escolha ajuda</h3><ul><li>Calcula todos os pares e permite reutilizar resultados nas consultas.</li><li>Aceita pesos negativos quando não há ciclos negativos.</li><li>A recorrência e as matrizes facilitam explicar e verificar a implementação.</li></ul></div>
<div class="panel warn"><h3>Onde a escolha limita</h3><ul><li>Tempo O(V³) e memória O(V²) restringem a escala.</li><li>Para poucas consultas, calcular todos os pares pode ser desnecessário.</li><li>Em redes esparsas, Dijkstra ou Johnson merecem comparação; não foram medidos neste trabalho.</li></ul></div></div>
<p>{weight_note}</p><p>A escolha atende aos objetivos funcionais e didáticos do projeto, mas não estabelece vantagem universal de desempenho. Ciclos negativos impedem mínimos finitos para os pares afetados; a aplicação rejeita a análise inteira quando detecta um deles.</p></section>
<section><span class="number">05 / MÉTODO E RASTREABILIDADE</span><h2>Como interpretar este relatório</h2>
<p>O algoritmo aplica d[i,j] = min(d[i,j], d[i,k] + d[k,j]), permitindo novos intermediários a cada rodada. A densidade exclui laços. Média e extremos consideram somente pares distintos com distância finita.</p>
<details><summary>Dados de entrada · {len(data['edges'])} arestas</summary>{edges}</details>
<p class="note">Referências: <a href="https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html">NetworkX · caminhos mínimos</a> e <a href="https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.dense.floyd_warshall.html">Floyd-Warshall e complexidade</a>.</p></section>
</div><footer>Floyd-Warshall · Projeto acadêmico<br>Relatório autossuficiente: leitura sem internet. Resultados referentes ao dataset indicado; medições podem variar entre execuções.</footer></main></body></html>'''
