"""Relatório HTML autossuficiente, responsivo e preparado para impressão.

O texto fixo descreve o problema, o algoritmo e as decisões do trabalho conforme
o enunciado. As tabelas são preenchidas somente com dados presentes no payload;
seções opcionais (redes maiores, complexidade, ambiente) aparecem apenas quando
os resultados correspondentes foram medidos e registrados.
"""

from html import escape
from math import isfinite

STYLE = """
:root{--ink:#172b3a;--muted:#526678;--blue:#153e58;--teal:#087f83;--amber:#ce9252;--line:#dae4e9;--paper:#fff;--soft:#fafcfd}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:#edf2f5;color:var(--ink);font:15px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1120px;margin:32px auto;background:var(--paper);box-shadow:0 16px 60px #17364d12}
header{padding:48px 56px 40px;background:var(--blue);color:#fff;border-top:7px solid #2bc4b3}
.eyebrow{text-transform:uppercase;letter-spacing:.18em;font-size:11px;font-weight:750;color:#a8e5e0}
h1{font:700 clamp(32px,5vw,48px)/1.1 Georgia,"Times New Roman",serif;letter-spacing:-.02em;margin:18px 0}
header p{color:#d5e4ec;max-width:730px;margin:0 0 20px}
.meta{display:flex;flex-wrap:wrap;gap:10px}
.meta span{display:inline-block;border:1px solid #80b7c077;border-radius:7px;padding:7px 12px;font-size:13px;overflow-wrap:anywhere}
nav{padding:16px 56px;border-bottom:1px solid var(--line);background:var(--soft)}
nav ol{margin:0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:6px 22px;font-size:13px}
nav a{color:var(--blue);text-decoration:none;font-weight:600}nav a:hover{text-decoration:underline}
.body{padding:36px 56px}section{margin:0 0 44px}
h2{font:700 24px/1.2 Georgia,"Times New Roman",serif;letter-spacing:-.01em;margin:0 0 18px}h3{font-size:16px;margin:0 0 10px}
.number{color:var(--teal);font-size:12px;letter-spacing:.1em;display:block;margin-bottom:6px;font-weight:750}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.card{border:1px solid var(--line);border-radius:9px;padding:18px;background:var(--soft)}
.label{font-size:12px;color:var(--muted)}.value{font-size:29px;font-weight:700;line-height:1.25;margin:8px 0}
.unit{font-size:13px;font-weight:500;color:var(--muted)}
.define{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.define .card h3{color:var(--teal);font-size:12px;letter-spacing:.1em;text-transform:uppercase;margin:0 0 8px}
.define .card p{margin:0;font-size:14px}
.note{font-size:12px;color:var(--muted);margin:12px 0}
.callout{border-left:4px solid var(--teal);background:#eff9f7;padding:16px 20px;border-radius:0 8px 8px 0;margin:14px 0}
.callout.amber{border-color:var(--amber);background:#fdf6ee}
.columns{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.panel{border:1px solid var(--line);padding:22px;border-radius:9px}.panel.warn{border-top:4px solid var(--amber)}.panel.good{border-top:4px solid var(--teal)}
ul,ol.steps{padding-left:20px;margin:0}li{margin:7px 0}
pre{margin:14px 0;padding:16px 20px;background:#0f2a3c;color:#e6f1f5;border-radius:9px;font:13px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;overflow-x:auto}
pre .c{color:#8fc7c2}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:8px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:11px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}
thead{background:#eff4f7}th{font-weight:650}tbody tr:nth-child(even){background:var(--soft)}tbody tr:last-child td{border-bottom:0}
.num td:not(:first-child),.num th:not(:first-child){text-align:right;font-variant-numeric:tabular-nums}
.badge{font-size:12px;padding:5px 10px;border-radius:20px;background:#e3f5ed;color:#185d47;display:inline-block;font-weight:650}
.badge.fail{background:#fdebea;color:#963a32}
.bar{height:12px;border-radius:8px;background:#dbe4ec;overflow:hidden;margin:14px 0 6px}.bar span{display:block;height:100%;background:var(--teal)}
summary{cursor:pointer;padding:15px 0;font-weight:650}details{margin-top:12px}
.matrix td{text-align:right;font-variant-numeric:tabular-nums}.matrix th{white-space:nowrap}.muted{color:var(--muted)}
footer{padding:22px 56px;border-top:1px solid var(--line);color:var(--muted);font-size:12px}a{color:var(--teal)}
@media(max-width:700px){main{margin:0}.body,header,footer,nav{padding-left:22px;padding-right:22px}.grid,.define{grid-template-columns:repeat(2,1fr)}.columns{grid-template-columns:1fr}}
@media print{@page{size:A4;margin:15mm}body{background:#fff;font-size:11px}main{margin:0;max-width:none;box-shadow:none}
header{padding:24px;color:#172b3a;background:#edf4f7}header p,.eyebrow{color:#365766}nav{display:none}
.body{padding:24px 0}footer{padding:15px 0}h1{font-size:32px}h2{font-size:19px}h2,h3,summary{break-after:avoid}
.card,.panel,.callout,pre,tr{break-inside:avoid}.value{font-size:23px}th,td{padding:7px}.scroll{overflow:visible}
.matrix{font-size:8px}.matrix th,.matrix td{padding:4px}.screen{display:none}a{color:inherit}thead{display:table-header-group}
pre{background:#f1f5f7;color:#172b3a}pre .c{color:#526678}}
"""

SECTIONS = [
    ("problema", "01", "O problema"),
    ("algoritmo", "02", "O algoritmo"),
    ("rede", "03", "A rede em números"),
    ("resultados", "04", "Custos e caminhos"),
    ("verificacao", "05", "Verificação"),
    ("complexidade", "06", "Complexidade"),
    ("analise", "07", "Análise crítica"),
    ("metodo", "08", "Método"),
]

REFERENCES = (
    '<a href="https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html">'
    "NetworkX · caminhos mínimos</a> e "
    '<a href="https://networkx.org/documentation/stable/reference/algorithms/generated/'
    'networkx.algorithms.shortest_paths.dense.floyd_warshall.html">Floyd-Warshall e complexidade</a>.'
)


def fmt(value, digits=2):
    if value is None or not isfinite(value):
        return "—"
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def table(headers, rows, cls=""):
    head = "".join(f'<th scope="col">{escape(str(x))}</th>' for x in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(x))}</td>" for x in row) + "</tr>" for row in rows
    )
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def heading(key):
    anchor, number, title = next(s for s in SECTIONS if s[0] == key)
    return f'<span class="number">{number} / {escape(title.upper())}</span><h2 id="{anchor}">{escape(title)}</h2>'


def nav():
    items = "".join(f'<li><a href="#{a}">{n} · {escape(t)}</a></li>' for a, n, t in SECTIONS)
    return f'<nav class="screen" aria-label="Sumário"><ol>{items}</ol></nav>'


def cards(items):
    return (
        '<div class="grid">'
        + "".join(
            f'<div class="card"><div class="label">{label}</div><div class="value">{value}</div><div class="unit">{unit}</div></div>'
            for label, value, unit in items
        )
        + "</div>"
    )


def section_problem():
    definitions = [
        ("Instância", "Um grafo dirigido G = (V, E) com um peso numérico em cada aresta."),
        (
            "Entrada",
            "A lista de vértices e as arestas (origem, destino, peso), sem ciclos de peso negativo.",
        ),
        (
            "Saída",
            "A menor distância entre cada par de vértices (i, j) e um caminho que realiza essa distância.",
        ),
        (
            "Restrições",
            "Pesos podem ser negativos; ciclos negativos são rejeitados, pois tornam a distância dos pares afetados ilimitada.",
        ),
    ]
    define = (
        '<div class="define">'
        + "".join(
            f'<div class="card"><h3>{escape(t)}</h3><p>{escape(d)}</p></div>'
            for t, d in definitions
        )
        + "</div>"
    )
    return f"""<section>{heading("problema")}
<p>Em vez de partir de uma única origem, o problema dos <strong>caminhos mais curtos entre todos os pares</strong> pede a distância mínima de cada vértice para cada outro vértice do grafo.</p>
{define}
<h3 style="margin-top:22px">Por que o problema pertence à classe P</h3>
<p>A classe P reúne os problemas que um algoritmo determinístico resolve em tempo polinomial no tamanho da entrada. Floyd-Warshall executa três laços aninhados sobre os V vértices, o que dá no máximo V³ atualizações, e guarda duas matrizes V × V. Tempo O(V³) e espaço O(V²) são polinômios em V; portanto, o problema está em P. Esse argumento vem da estrutura dos laços, e as medições da seção 06 servem apenas para ilustrá-lo.</p>
</section>"""


def section_algorithm():
    return f"""<section>{heading("algoritmo")}
<p>A ideia é liberar um vértice intermediário por vez. Antes da rodada k, a matriz d guarda a menor distância entre cada par usando apenas os k − 1 primeiros vértices como paradas intermediárias. Na rodada k, cada par (i, j) testa se passar por k encurta o caminho:</p>
<pre><span class="c"># d[i][i] = 0; d[i][j] = peso da aresta ou infinito; next[i][j] = j quando há aresta</span>
para k em vértices:            <span class="c"># laço externo: libera o intermediário k</span>
    para i em vértices:
        para j em vértices:
            se d[i][k] + d[k][j] &lt; d[i][j]:
                d[i][j] = d[i][k] + d[k][j]
                next[i][j] = next[i][k]  <span class="c"># o caminho para j começa como o caminho para k</span></pre>
<div class="columns">
<div class="panel good"><h3>Por que k precisa ser o laço mais externo</h3>
<p>Quando k está por fora, ao terminar a rodada k <em>todos</em> os pares já conhecem o melhor caminho com intermediários entre os k primeiros vértices. A rodada k + 1 parte dessa base completa. Se k fosse o laço interno, cada par (i, j) seria visitado uma única vez e testaria todos os intermediários de uma só vez; um caminho que precise de dois ou mais intermediários (i → a → b → j) poderia ser perdido, porque d[i][b] ainda não teria absorvido a passagem por a quando (i, j) fosse avaliado.</p></div>
<div class="panel good"><h3>Como reconstruir o caminho, não só a distância</h3>
<p>A matriz next guarda, para cada par (i, j), o primeiro vértice depois de i no melhor caminho até j. Sempre que passar por k melhora (i, j), o primeiro passo de i até j passa a ser o mesmo primeiro passo de i até k. Para listar o caminho, basta partir de i e seguir next[atual][j] até chegar em j. Se next[i][j] estiver vazio, não existe caminho.</p></div>
</div>
<p class="note">Detecção de ciclo negativo: ao final, se algum d[i][i] ficar menor que zero, existe um ciclo de peso negativo passando por i, e a análise é recusada. A implementação também pula pares com d[i][k] ou d[k][j] infinitos, um atalho que não altera o limite O(V³).</p>
</section>"""


def section_network(data):
    m = data["metrics"]
    reachable, unreachable = m["reachable_pairs"], m["unreachable_pairs"]
    total = reachable + unreachable
    percentage = 100 * reachable / total if total else 0
    metrics = cards(
        [
            ("Vértices", str(m["vertices"]), "pontos da rede"),
            ("Arestas", str(m["edges"]), "conexões dirigidas"),
            ("Tempo de execução", fmt(m["execution_time_ms"], 3), "ms · sem instrumentação"),
            ("Pico de memória Python", fmt(m["peak_memory_kb"]), "KiB · execução separada"),
        ]
    )
    overview = table(
        ["Indicador", "Resultado", "Interpretação"],
        [
            ["Densidade", fmt(m["density"]) + "%", "Conexões existentes entre vértices distintos."],
            [
                "Distância média",
                fmt(m["average_distance"]),
                "Média dos custos mínimos finitos; exclui a diagonal.",
            ],
            [
                "Menor / maior distância",
                fmt(m["minimum_distance"]) + " / " + fmt(m["maximum_distance"]),
                "Extremos entre pares distintos alcançáveis.",
            ],
        ],
    )
    empty = " Não há pares distintos neste dataset." if not total else ""
    return f"""<section>{heading("rede")}{metrics}
<p class="note">Tempo em milissegundos. Pico de alocações Python em outra execução; não representa a RAM total do processo.</p>
<div class="callout">A análise identificou <strong>{reachable:,} pares alcançáveis</strong> e <strong>{unreachable:,} inalcançáveis</strong>, excluindo consultas de um vértice para ele mesmo.</div>
<div class="bar" role="img" aria-label="{fmt(percentage)} por cento dos pares alcançáveis"><span style="width:{percentage:.2f}%"></span></div>
<p class="note">{fmt(percentage)}% dos pares distintos são alcançáveis.{empty}</p>{overview}</section>"""


def path_rows(data):
    vertices = data["vertices"]
    index = {v: i for i, v in enumerate(vertices)}
    rows = []
    for item in data["paths"]:
        u, v, path = item["source"], item["target"], item["path"]
        distance = data["distances"][index[u]][index[v]]
        rows.append([u, v, fmt(distance), " → ".join(path) if path else "Sem caminho"])
    return rows


def section_results(data):
    vertices = data["vertices"]
    n = len(vertices)
    rows = path_rows(data)
    sample = [row for row in rows if row[0] != row[1] and row[3] != "Sem caminho"][:8]
    headers = ["Origem", "Destino", "Custo mínimo", "Caminho"]
    summary = (
        table(headers, sample)
        if sample
        else "<p>Nenhum par de vértices distintos possui caminho.</p>"
    )
    limit = min(n, 12)
    matrix = table(
        ["Origem / destino"] + vertices[:limit],
        [[vertices[i]] + [fmt(x) for x in data["distances"][i][:limit]] for i in range(limit)],
        "matrix",
    )
    matrix_note = (
        "Prévia dos primeiros 12 vértices. A tabela completa de pares abaixo abrange todos os vértices."
        if n > 12
        else "Matriz completa. A diagonal representa custo zero; “—” indica ausência de caminho."
    )
    return f"""<section>{heading("resultados")}{summary}
<p class="note">Até oito pares alcançáveis, na ordem dos vértices de entrada. Custos com duas casas decimais; os arquivos JSON e CSV preservam a precisão exportada. Cada caminho listado foi reconstruído pela matriz next descrita na seção 02.</p>
<details><summary>Matriz de distâncias · {n} vértices</summary><p class="note">{matrix_note}</p>{matrix}</details>
<details><summary>Consultar todos os {len(rows):,} pares, incluindo a diagonal</summary>{table(headers, rows)}</details>
<p class="note screen">Para imprimir ou salvar em PDF, use a opção de impressão do navegador. Expanda os apêndices antes de imprimir se quiser incluí-los; em redes grandes, eles podem ocupar muitas páginas.</p></section>"""


def comparison_block(comparison):
    if not comparison:
        return '<div class="callout">Comparação não executada nesta análise. Na aplicação, execute “Comparar com baseline” antes de exportar para incluir os resultados.</div>'
    matches = comparison["distances_match"]
    status = "Todas as distâncias coincidem" if matches else "Foram encontradas divergências"
    fw, bf = comparison["floyd_warshall"], comparison["bellman_ford"]
    return (
        f'<p><span class="badge {"" if matches else "fail"}">{status}</span></p>'
        + table(
            ["Algoritmo", "Tempo (ms)", "Pico Python (KiB)"],
            [
                [
                    "Floyd-Warshall próprio",
                    fmt(fw["execution_time_ms"], 3),
                    fmt(fw["peak_memory_kb"]),
                ],
                [
                    "Bellman-Ford por origem",
                    fmt(bf["execution_time_ms"], 3),
                    fmt(bf["peak_memory_kb"]),
                ],
            ],
            "num",
        )
        + '<p class="note">Medições pontuais da comparação, distintas da execução principal da seção 03. Incluem a preparação interna de cada solver. Não demonstram superioridade estatística ou universal. A verificação usa tolerância de 1e-9; caminhos diferentes podem ter o mesmo custo.</p>'
    )


def networks_block(networks):
    if not networks:
        return ""
    rows = [
        [
            r["dataset"],
            r["vertices"],
            r["edges"],
            f'{r["reachable_pairs"]:,} / {r["unreachable_pairs"]:,}',
            fmt(r["execution_time_ms"]),
            fmt(r["baseline_time_ms"]),
            "Coincidem" if r["distances_match"] else "Divergem",
        ]
        for r in networks
    ]
    return f"""<h3 style="margin-top:26px">Redes maiores verificadas em todos os pares</h3>
<p>As mesmas distâncias foram conferidas nas redes sintéticas maiores do projeto. Tempos em milissegundos de uma execução registrada; não são médias.</p>
{table(["Rede", "V", "E", "Pares alcançáveis / inalcançáveis", "Floyd-Warshall (ms)", "Bellman-Ford (ms)", "Distâncias"], rows, "num")}
<p class="note">Fonte: reports/comparacao_redes.csv, gerado por scripts/evaluate_datasets.py. As redes são sintéticas e reproduzíveis com as sementes descritas em docs/DATASETS.md.</p>"""


def section_verification(data):
    return f"""<section>{heading("verificacao")}
<p>Bellman-Ford do NetworkX é executado a partir de cada origem, e cada distância é comparada com a matriz calculada pela implementação própria. O baseline foi escolhido porque também aceita pesos negativos.</p>
{comparison_block(data.get("comparison"))}{networks_block(data.get("networks"))}</section>"""


def section_complexity(data):
    rows = data.get("complexity")
    if not rows:
        body = '<div class="callout">Experimento de escala não incluído nesta exportação. Na aplicação, a aba <strong>Complexidade</strong> executa o experimento com grafos completos de 10 a 80 vértices.</div>'
    else:
        first = rows[0]
        ratio = rows[-1]["median_ms"] / first["median_ms"] if first["median_ms"] else 0
        growth = (rows[-1]["vertices"] / first["vertices"]) ** 3
        body = table(
            ["Vértices", "Arestas", "Mediana (ms)", "ms / V³ (×10⁻⁴)", "Repetições"],
            [
                [
                    r["vertices"],
                    r["edges"],
                    fmt(r["median_ms"], 3),
                    fmt(r["ms_per_n3"] * 1e4, 3),
                    r["repeats"],
                ]
                for r in rows
            ],
            "num",
        )
        body += f"""<div class="callout">De {first["vertices"]} para {rows[-1]["vertices"]} vértices, V³ cresce {fmt(growth, 0)} vezes e o tempo medido cresceu <strong>{fmt(ratio, 0)} vezes</strong>. O crescimento fica abaixo de V³, e a coluna ms / V³ diminui com o tamanho: há um custo fixo por execução que pesa mais nos grafos pequenos. Isso é compatível com O(V³) como limite superior.</div>
<p class="note">Grafos dirigidos completos, gerados de forma determinística, com aquecimento e mediana de {first["repeats"]} execuções sem instrumentação de memória. Quatro tamanhos ilustram a tendência, mas não provam a lei assintótica: o limite O(V³) é fundamentado na análise dos laços da seção 02. A variação de ms / V³ reflete overhead fixo, cache e ambiente.</p>"""
    return f"""<section>{heading("complexidade")}
<p>Tempo <strong>O(V³)</strong>: para cada um dos V intermediários, todos os V² pares são examinados. Espaço <strong>O(V²)</strong>: duas matrizes V × V, uma de distâncias e uma de próximos vértices. O baseline Bellman-Ford custa O(V · E) por origem, logo O(V² · E) para todas as origens; em grafos densos, com E próximo de V², esse limite chega a O(V⁴).</p>{body}</section>"""


def section_analysis(data):
    negative = any(w < 0 for _, _, w in data["edges"])
    weight_note = (
        "Este dataset contém pesos negativos, um requisito que o Dijkstra convencional não atende."
        if negative
        else "Este dataset não contém pesos negativos: Dijkstra também é uma alternativa válida a avaliar."
    )
    return f"""<section>{heading("analise")}
<h3>Relação com situações reais</h3>
<p>O problema modela qualquer rede em que se queira o menor custo entre todos os pares de pontos: uma tabela de rotas com custos entre localidades, por exemplo. Neste trabalho, essa relação é ilustrada por redes sintéticas com cenários nomeados como logístico, urbano e regional, nas quais P001, P002 etc. são pontos e os pesos são unidades abstratas de custo. Os dados foram gerados para o seminário e não representam medições de uma rede real.</p>
<h3 style="margin-top:22px">Por que escolher Floyd-Warshall?</h3>
<div class="columns"><div class="panel good"><h3>Onde a escolha ajuda</h3><ul><li>Calcula todos os pares de uma vez e permite reutilizar a matriz em muitas consultas.</li><li>Aceita pesos negativos quando não há ciclos negativos.</li><li>A recorrência única e as matrizes facilitam explicar, verificar e reconstruir caminhos.</li></ul></div>
<div class="panel warn"><h3>Onde a escolha limita</h3><ul><li>Tempo O(V³) e memória O(V²) restringem a escala.</li><li>Para poucas consultas, calcular todos os pares pode ser desnecessário.</li><li>Em redes esparsas, Dijkstra ou Johnson merecem comparação; não foram medidos neste trabalho.</li></ul></div></div>
<p>{weight_note}</p><p>A escolha atende aos objetivos funcionais e didáticos do projeto, mas não estabelece vantagem universal de desempenho. Ciclos negativos impedem mínimos finitos para os pares afetados; a aplicação rejeita a análise inteira quando detecta um deles.</p></section>"""


def environment_block(env):
    if not env:
        return ""
    packages = ", ".join(f"{name} {version}" for name, version in env.get("packages", {}).items())
    return f'<p class="note">Ambiente registrado: Python {escape(str(env.get("python", "")))} em {escape(str(env.get("platform", "")))}. Pacotes: {escape(packages)}.</p>'


def section_method(data):
    edges = table(["Origem", "Destino", "Peso"], [[u, v, fmt(w)] for u, v, w in data["edges"]])
    return f"""<section>{heading("metodo")}
<p>A densidade exclui laços. Média e extremos consideram somente pares distintos com distância finita. Tempo e pico de memória são medidos em execuções separadas, porque a instrumentação de memória altera o tempo. Os arquivos JSON e CSV exportados junto deste relatório contêm a matriz completa e todos os caminhos.</p>
<details><summary>Dados de entrada · {len(data['edges'])} arestas</summary>{edges}</details>
{environment_block(data.get("environment"))}
<p class="note">Referências: {REFERENCES}</p></section>"""


def render_report(data):
    label = escape(str(data["dataset"]))
    generated = data.get("generated_at")
    meta = f"<span>Dataset · {label}</span>"
    if generated:
        meta += f"<span>Gerado em · {escape(str(generated))}</span>"
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relatório • {label} • Floyd-Warshall</title><style>{STYLE}</style></head>
<body><main><header><div class="eyebrow">Teoria da Computação · seminário sobre um problema da classe P</div>
<h1>Caminhos mais curtos entre todos os pares</h1><p>Definição do problema, funcionamento do algoritmo Floyd-Warshall, resultados sobre o dataset analisado, verificação contra um baseline independente e análise crítica da escolha.</p>
<div class="meta">{meta}</div></header>{nav()}<div class="body">
{section_problem()}{section_algorithm()}{section_network(data)}{section_results(data)}{section_verification(data)}{section_complexity(data)}{section_analysis(data)}{section_method(data)}
</div><footer>Floyd-Warshall · Projeto acadêmico<br>Relatório autossuficiente: leitura sem internet. Resultados referentes ao dataset indicado; medições podem variar entre execuções.</footer></main></body></html>"""
