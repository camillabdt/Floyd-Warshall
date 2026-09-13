/* Simulação do Floyd-Warshall para gravação de tela.
   Reaproveita o motor de assets/fw.js através de window.FW. */
(function () {
  'use strict';

  var E = window.FW;
  if (!E) return;
  var INF = E.INF, fmt = E.fmt;

  /* ---------- grafos disponíveis ---------- */

  var DATASETS = [
    {
      id: 'exemplo',
      nome: 'grafo_exemplo.csv  ·  4 vértices',
      vertices: 'A@110,80 B@400,80 C@400,300 D@110,300',
      edges: 'A>B:3 A>D:10 B>C:2 C>D:1',
      nota: 'O dataset principal do projeto. A distância de A até D cai de 10 para 6, pelo caminho A → B → C → D.'
    },
    {
      id: 'mantem',
      nome: 'variação com A → C de peso 4  ·  4 vértices',
      vertices: 'A@110,80 B@400,80 C@400,300 D@110,300',
      edges: 'A>B:3 A>C:4 A>D:10 B>C:2 C>D:1',
      nota: 'Variação feita para a aula: aqui aparece uma comparação que termina em "mantém", porque 3 + 2 não é menor que 4.'
    },
    {
      id: 'negativo',
      nome: 'grafo_peso_negativo.json  ·  3 vértices',
      vertices: 'A@110,90 B@390,90 C@250,320',
      edges: 'A>B:4 A>C:5 B>C:-2',
      nota: 'Peso negativo é permitido. Na etapa k = B, a soma 4 + (−2) = 2 vence a aresta direta de peso 5.'
    },
    {
      id: 'ordem',
      nome: 'contraexemplo da ordem dos laços  ·  4 vértices',
      vertices: 'A@110,80 B@400,80 C@400,300 D@110,300',
      edges: 'A>B:10 A>D:1 D>C:1 C>B:1',
      nota: 'A aresta direta A → B custa 10, mas o desvio A → D → C → B custa 3. O valor certo só aparece na etapa k = D.'
    },
    {
      id: 'desconexo',
      nome: 'grafo_desconexo.json  ·  5 vértices',
      vertices: 'A@100,90 B@330,90 C@330,310 D@100,310 Z@540,200',
      edges: 'A>B:3 B>C:2 C>D:1',
      nota: 'O vértice Z não tem nenhuma aresta. A linha e a coluna de Z terminam em ∞, que é uma resposta válida.'
    },
    {
      id: 'ciclo',
      nome: 'grafo_ciclo_negativo.json  ·  3 vértices',
      vertices: 'A@120,90 B@390,90 C@255,320',
      edges: 'A>B:1 B>C:-3 C>A:1',
      nota: 'A volta A → B → C → A soma −1. Não existe distância mínima aqui, e a diagonal denuncia isso ao ficar negativa.',
      cicloNegativo: true
    }
  ];

  /* ---------- listagens do algoritmo ---------- */

  var LISTAGENS = {
    py: {
      rotulo: 'Python do projeto',
      linhas: E.CODE_LINES,
      foco: E.codeFocus
    },
    pt: {
      rotulo: 'Resumo em português',
      linhas: [
        'para cada parada k:',
        '    para cada origem i:',
        '        se não sei ir de i até k: pule',
        '        para cada destino j:',
        '            se não sei ir de k até j: pule',
        '            soma = dist[i][k] + dist[k][j]',
        '            se soma < dist[i][j]:',
        '                dist[i][j] = soma',
        '                next[i][j] = next[i][k]'
      ],
      foco: function (step) {
        if (step.type === 'pivot') return { on: [0], fired: [] };
        if (step.type === 'done') return { on: [], fired: [] };
        if (step.ik === INF) return { on: [2], fired: [1] };
        if (step.kj === INF) return { on: [4], fired: [1, 3] };
        if (step.improved) return { on: [7, 8], fired: [1, 3, 5, 6] };
        return { on: [6], fired: [1, 3, 5] };
      }
    }
  };

  /* ---------- atalhos de DOM ---------- */

  function $(sel) { return document.querySelector(sel); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  /* ---------- estado da página ---------- */

  var atual = null;      // { dataset, vertices, edges, trace, graph, matrix, player }
  var listagem = 'py';
  var velocidade = 1200; // milissegundos por passo

  var nodes = {
    intro: $('#intro'),
    sim: $('#sim'),
    introGraph: $('#intro-graph'),
    graph: $('#graph-host'),
    matrix: $('#matrix-host'),
    code: $('#code-list'),
    readout: $('#readout'),
    verdict: $('#verdict'),
    narration: $('#narration'),
    counter: $('#counter'),
    progress: $('#progress-bar'),
    stages: $('#stages'),
    alerta: $('#alerta'),
    nota: $('#dataset-note'),
    dataset: $('#dataset'),
    detalhe: $('#detalhe'),
    velocidade: $('#velocidade'),
    velocidadeTexto: $('#velocidade-texto'),
    btnPlay: $('#btn-play'),
    btnPrev: $('#btn-prev'),
    btnNext: $('#btn-next'),
    btnReset: $('#btn-reset'),
    btnComecar: $('#btn-comecar'),
    btnIntro: $('#btn-intro'),
    btnTela: $('#btn-tela'),
    switchPy: $('#switch-py'),
    switchPt: $('#switch-pt')
  };

  /* ---------- montagem de um grafo ---------- */

  function montar(dataset) {
    var vertices = E.parseVertices(dataset.vertices);
    var edges = E.parseEdges(dataset.edges);
    var trace = E.buildTrace(vertices, edges, {});

    nodes.graph.innerHTML = '';
    nodes.matrix.innerHTML = '';
    var graph = new E.GraphView(nodes.graph, vertices, edges);
    var matrix = new E.MatrixView(nodes.matrix, vertices, { caption: ' ' });

    nodes.nota.textContent = dataset.nota;
    nodes.alerta.hidden = true;

    nodes.stages.innerHTML = '';
    vertices.forEach(function (v) { nodes.stages.appendChild(el('span', 'stage', 'k = ' + v.id)); });

    nodes.code.innerHTML = '';
    LISTAGENS[listagem].linhas.forEach(function (linha) {
      nodes.code.appendChild(el('span', 'line', linha));
    });

    var player = new E.Player({
      steps: trace.steps,
      speed: velocidade,
      render: function (step, pos, total) { desenhar(step, pos, total); }
    });
    player.onState = function () {
      nodes.btnPlay.textContent = player.playing() ? '⏸  Pausar' : '▶  Tocar';
      nodes.btnPlay.setAttribute('aria-label', player.playing() ? 'Pausar a simulação' : 'Tocar a simulação');
    };

    atual = {
      dataset: dataset, vertices: vertices, edges: edges,
      trace: trace, graph: graph, matrix: matrix, player: player
    };
    aplicarFiltro();
    return atual;
  }

  /* ---------- desenho de um passo ---------- */

  function desenhar(step, pos, total) {
    var v = atual.vertices;

    // grafo
    var g = { arcs: [] };
    if (step.type === 'compare') {
      g.pivot = v[step.k].id;
      if (step.i !== step.k) g.origin = v[step.i].id;
      if (step.j !== step.k) g.target = v[step.j].id;
      if (!step.trivial && !step.blocked) {
        g.arcs.push({ from: v[step.i].id, to: v[step.k].id, label: fmt(step.ik), cls: 'leg', bend: -40 });
        g.arcs.push({ from: v[step.k].id, to: v[step.j].id, label: fmt(step.kj), cls: 'leg', bend: -40 });
        g.arcs.push({
          from: v[step.i].id, to: v[step.j].id,
          label: step.improved ? fmt(step.sum) : fmt(step.ij),
          cls: step.improved ? 'win' : 'direct', bend: 64
        });
      }
      g.alt = 'Etapa k = ' + v[step.k].id + ', testando o par ' + v[step.i].id + ' para ' + v[step.j].id;
    } else if (step.type === 'pivot') {
      g.pivot = v[step.k].id;
      g.alt = 'Início da etapa k = ' + v[step.k].id;
    } else {
      g.alt = 'Execução concluída';
    }
    atual.graph.update(g);

    // matriz
    var hl = {};
    if (step.type === 'compare' && !step.trivial) {
      hl.opA = [step.i, step.k];
      hl.opB = [step.k, step.j];
      hl.target = [step.i, step.j];
      hl.improved = step.improved;
    }
    if (step.type === 'pivot') hl.axis = step.k;
    hl.caption = step.type === 'pivot'
      ? 'Estado no início da etapa k = ' + v[step.k].id
      : (step.type === 'done'
        ? (atual.dataset.cicloNegativo
          ? 'Estes números não são distâncias mínimas: o grafo tem ciclo negativo'
          : 'Matriz final de distâncias mínimas')
        : 'Estado depois desta comparação');
    atual.matrix.update(step.dist, hl);

    // algoritmo ao lado
    var foco = LISTAGENS[listagem].foco(step);
    Array.prototype.forEach.call(nodes.code.children, function (linha, idx) {
      var cls = 'line';
      if (foco.fired.indexOf(idx) >= 0) cls += ' fired';
      if (foco.on.indexOf(idx) >= 0) cls += ' on';
      linha.className = cls;
    });

    desenharLeitura(step);
    desenharNarracao(step);

    // contador, barra e etapas
    nodes.counter.textContent = 'Passo ' + (pos + 1) + ' de ' + total;
    nodes.progress.style.width = (total < 2 ? 100 : (pos / (total - 1)) * 100) + '%';
    var etapaAtual = step.type === 'done' ? atual.vertices.length : step.k;
    Array.prototype.forEach.call(nodes.stages.children, function (s, idx) {
      s.className = 'stage' + (idx < etapaAtual ? ' done' : (idx === etapaAtual ? ' active' : ''));
    });

    // alerta de ciclo negativo
    if (atual.dataset.cicloNegativo) {
      var negativa = step.dist.some(function (row, idx) { return row[idx] < 0; });
      nodes.alerta.hidden = !negativa;
    }

    nodes.btnPrev.disabled = pos === 0;
    nodes.btnNext.disabled = pos === total - 1;
  }

  function linhaLeitura(rotulo, valor, cls) {
    var dt = el('dt', null, rotulo);
    var dd = el('dd', cls || null, valor);
    return [dt, dd];
  }

  function desenharLeitura(step) {
    var v = atual.vertices;
    nodes.readout.innerHTML = '';
    var dl = el('dl');

    if (step.type === 'pivot') {
      var permitidas = v.slice(0, step.k + 1).map(function (x) { return x.id; }).join(', ');
      linhaLeitura('k', v[step.k].id, 'a').forEach(function (n) { dl.appendChild(n); });
      linhaLeitura('paradas liberadas', permitidas).forEach(function (n) { dl.appendChild(n); });
      nodes.readout.appendChild(dl);
      nodes.verdict.className = 'verdict keep';
      nodes.verdict.textContent = 'Começando uma etapa';
      return;
    }
    if (step.type === 'done') {
      linhaLeitura('etapas', v.length + ' de ' + v.length, 'r').forEach(function (n) { dl.appendChild(n); });
      linhaLeitura('comparações', String(Math.pow(v.length, 3)), 'r').forEach(function (n) { dl.appendChild(n); });
      nodes.readout.appendChild(dl);
      if (atual.dataset.cicloNegativo) {
        nodes.verdict.className = 'verdict skip';
        nodes.verdict.textContent = 'Entrada recusada: ciclo negativo';
      } else {
        nodes.verdict.className = 'verdict win';
        nodes.verdict.textContent = 'Execução concluída';
      }
      return;
    }

    var i = v[step.i].id, j = v[step.j].id, k = v[step.k].id;

    var chips = el('div', 'chips');
    [['k', k, 'parada'], ['i', i, 'origem'], ['j', j, 'destino']].forEach(function (c) {
      var chip = el('span', 'chip ' + c[0]);
      chip.title = c[2];
      chip.innerHTML = c[0] + ' = <b>' + c[1] + '</b>';
      chips.appendChild(chip);
    });
    nodes.readout.appendChild(chips);

    linhaLeitura('dist[' + i + '][' + k + ']', fmt(step.ik), 'a').forEach(function (n) { dl.appendChild(n); });
    linhaLeitura('dist[' + k + '][' + j + ']', fmt(step.kj), 'b').forEach(function (n) { dl.appendChild(n); });
    linhaLeitura('soma', step.blocked ? 'não somou' : fmt(step.sum), 'r').forEach(function (n) { dl.appendChild(n); });
    linhaLeitura('dist[' + i + '][' + j + ']', fmt(step.ij), 't').forEach(function (n) { dl.appendChild(n); });
    nodes.readout.appendChild(dl);

    if (step.blocked) {
      nodes.verdict.className = 'verdict skip';
      nodes.verdict.textContent = 'Trecho em ∞: o código pula';
    } else if (step.trivial) {
      nodes.verdict.className = 'verdict keep';
      nodes.verdict.textContent = 'Parada na própria ponta: nada muda';
    } else if (step.improved) {
      nodes.verdict.className = 'verdict win';
      nodes.verdict.textContent = fmt(step.sum) + ' < ' + fmt(step.ij) + ' → troca';
    } else {
      nodes.verdict.className = 'verdict keep';
      nodes.verdict.textContent = fmt(step.sum) + ' não é menor que ' + fmt(step.ij) + ' → mantém';
    }
  }

  function desenharNarracao(step) {
    var n = E.narrate(step, atual.vertices);
    if (step.type === 'done' && atual.dataset.cicloNegativo) {
      n = {
        head: 'Fim da execução, com um alerta',
        text: 'As células da diagonal ficaram negativas. Isso prova que existe ciclo de peso negativo, e o projeto recusa esta entrada com <code>NegativeCycleError</code>. Os números acima não são distâncias mínimas, porque elas não existem neste grafo.',
        tone: 'keep'
      };
    }
    nodes.narration.className = 'narration ' + n.tone;
    nodes.narration.innerHTML = '<span class="head">' + n.head + '</span>' + n.text;
  }

  /* ---------- filtro de detalhe ---------- */

  function aplicarFiltro() {
    var modo = nodes.detalhe.value;
    atual.player.setFilter(function (s) {
      if (s.type !== 'compare') return true;
      if (modo === 'full') return true;
      if (modo === 'wins') return s.improved;
      return !s.blocked && !s.trivial;
    });
  }

  /* ---------- velocidade ---------- */

  /* O controle guarda o tempo por passo em milissegundos, com sinal negativo.
     Assim, arrastar para a direita sempre significa "mais rápido". */
  function aplicarVelocidade() {
    var bruto = +nodes.velocidade.value;
    velocidade = -bruto;
    var segundos = (velocidade / 1000).toFixed(1).replace('.', ',');
    nodes.velocidadeTexto.textContent = segundos + ' s / passo';
    var min = +nodes.velocidade.min, max = +nodes.velocidade.max;
    var pct = ((bruto - min) / (max - min)) * 100;
    nodes.velocidade.style.setProperty('--pct', pct + '%');
    if (atual) atual.player.setSpeed(velocidade);
  }

  function mudarVelocidade(passo) {
    var v = +nodes.velocidade.value + passo;
    v = Math.max(+nodes.velocidade.min, Math.min(+nodes.velocidade.max, v));
    nodes.velocidade.value = v;
    aplicarVelocidade();
  }

  /* ---------- telas ---------- */

  function mostrarSimulacao() {
    nodes.intro.hidden = true;
    nodes.sim.hidden = false;
    if (atual) atual.player.goto(0);
  }

  function mostrarIntro() {
    if (atual) atual.player.pause();
    nodes.sim.hidden = true;
    nodes.intro.hidden = false;
  }

  /* ---------- introdução ---------- */

  function desenharIntro() {
    var d = DATASETS[0];
    nodes.introGraph.innerHTML = '';
    var g = new E.GraphView(nodes.introGraph, E.parseVertices(d.vertices), E.parseEdges(d.edges));
    var quadros = [
      { arcs: [{ from: 'A', to: 'D', label: '10', cls: 'direct', bend: 64 }] },
      { pivot: 'B', arcs: [{ from: 'A', to: 'C', label: '5', cls: 'leg', bend: -40 }] },
      {
        pivot: 'C', arcs: [
          { from: 'A', to: 'C', label: '5', cls: 'leg', bend: -40 },
          { from: 'C', to: 'D', label: '1', cls: 'leg', bend: -40 },
          { from: 'A', to: 'D', label: '6', cls: 'win', bend: 64 }
        ]
      }
    ];
    var f = 0;
    function tick() {
      g.update(quadros[f]);
      f = (f + 1) % quadros.length;
    }
    tick();
    setInterval(tick, 2600);
  }

  /* ---------- ligações ---------- */

  function trocarListagem(qual) {
    listagem = qual;
    nodes.switchPy.setAttribute('aria-pressed', String(qual === 'py'));
    nodes.switchPt.setAttribute('aria-pressed', String(qual === 'pt'));
    nodes.code.innerHTML = '';
    LISTAGENS[qual].linhas.forEach(function (linha) {
      nodes.code.appendChild(el('span', 'line', linha));
    });
    if (atual) atual.player.draw();
  }

  DATASETS.forEach(function (d, n) {
    var o = document.createElement('option');
    o.value = d.id; o.textContent = d.nome;
    if (n === 0) o.selected = true;
    nodes.dataset.appendChild(o);
  });

  nodes.dataset.addEventListener('change', function () {
    var d = DATASETS.filter(function (x) { return x.id === nodes.dataset.value; })[0];
    if (atual) atual.player.pause();
    montar(d);
  });

  nodes.detalhe.addEventListener('change', aplicarFiltro);
  nodes.velocidade.addEventListener('input', aplicarVelocidade);

  nodes.btnPlay.addEventListener('click', function () { atual.player.toggle(); });
  nodes.btnNext.addEventListener('click', function () { atual.player.pause(); atual.player.step(1); });
  nodes.btnPrev.addEventListener('click', function () { atual.player.pause(); atual.player.step(-1); });
  nodes.btnReset.addEventListener('click', function () { atual.player.reset(); });
  nodes.btnComecar.addEventListener('click', mostrarSimulacao);
  nodes.btnIntro.addEventListener('click', mostrarIntro);
  nodes.switchPy.addEventListener('click', function () { trocarListagem('py'); });
  nodes.switchPt.addEventListener('click', function () { trocarListagem('pt'); });

  nodes.btnTela.addEventListener('click', function () {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen();
  });
  document.addEventListener('fullscreenchange', function () {
    nodes.btnTela.textContent = document.fullscreenElement ? 'Sair da tela cheia' : 'Tela cheia';
  });

  document.addEventListener('keydown', function (ev) {
    var alvo = ev.target.tagName;
    if (alvo === 'INPUT' || alvo === 'SELECT' || alvo === 'TEXTAREA') return;
    // com o foco em um botão, espaço e Enter já o acionam: não duplicar
    if (alvo === 'BUTTON' && (ev.key === ' ' || ev.key === 'Enter')) return;
    if (nodes.sim.hidden) {
      if (ev.key === 'Enter' || ev.key === ' ') { mostrarSimulacao(); ev.preventDefault(); }
      return;
    }
    if (ev.key === ' ') { atual.player.toggle(); ev.preventDefault(); }
    if (ev.key === 'ArrowRight') { atual.player.pause(); atual.player.step(1); ev.preventDefault(); }
    if (ev.key === 'ArrowLeft') { atual.player.pause(); atual.player.step(-1); ev.preventDefault(); }
    if (ev.key === 'r' || ev.key === 'R') { atual.player.reset(); }
    if (ev.key === 'f' || ev.key === 'F') { nodes.btnTela.click(); }
    if (ev.key === '+' || ev.key === '=') { mudarVelocidade(200); ev.preventDefault(); }
    if (ev.key === '-' || ev.key === '_') { mudarVelocidade(-200); ev.preventDefault(); }
  });

  desenharIntro();
  montar(DATASETS[0]);
  aplicarVelocidade();
  trocarListagem('py');
})();
