/* Caderno animado de Floyd-Warshall
   Motor compartilhado: grafo em SVG, matriz, trilha de passos e reprodutor.
   Sem dependências externas. Funciona abrindo o arquivo direto do disco. */
(function () {
  'use strict';

  var INF = Infinity;
  var R = 23;
  var uid = 0;

  /* ---------- utilidades ---------- */

  function fmt(v) {
    if (v === INF) return '∞';
    if (v === null || v === undefined) return '∅';
    return Number.isInteger(v) ? String(v) : String(Math.round(v * 100) / 100);
  }

  function copy(m) { return m.map(function (row) { return row.slice(); }); }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function svgEl(tag, attrs) {
    var n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (var k in attrs) if (attrs[k] !== undefined) n.setAttribute(k, attrs[k]);
    return n;
  }

  function parseVertices(str) {
    return str.trim().split(/\s+/).map(function (chunk) {
      var m = chunk.match(/^([^@]+)@(-?\d+),(-?\d+)$/);
      if (!m) throw new Error('vértice inválido: ' + chunk);
      return { id: m[1], x: +m[2], y: +m[3] };
    });
  }

  function parseEdges(str) {
    if (!str || !str.trim()) return [];
    return str.trim().split(/\s+/).map(function (chunk) {
      var m = chunk.match(/^(.+?)>(.+?):(-?\d+(?:\.\d+)?)$/);
      if (!m) throw new Error('aresta inválida: ' + chunk);
      return { from: m[1], to: m[2], w: +m[3] };
    });
  }

  /* ---------- geometria ---------- */

  function unitAdvance(from, toward, d) {
    var dx = toward[0] - from[0], dy = toward[1] - from[1];
    var L = Math.hypot(dx, dy) || 1;
    return [from[0] + (dx / L) * d, from[1] + (dy / L) * d];
  }

  function curveGeom(p1, p2, bend) {
    var dx = p2[0] - p1[0], dy = p2[1] - p1[1];
    var L = Math.hypot(dx, dy) || 1;
    var nx = -dy / L, ny = dx / L;
    var c = [(p1[0] + p2[0]) / 2 + nx * bend, (p1[1] + p2[1]) / 2 + ny * bend];
    var s = unitAdvance(p1, c, R + 3);
    var e = unitAdvance(p2, c, R + 11);
    return {
      d: 'M' + s[0] + ' ' + s[1] + ' Q' + c[0] + ' ' + c[1] + ' ' + e[0] + ' ' + e[1],
      mid: [(s[0] + 2 * c[0] + e[0]) / 4, (s[1] + 2 * c[1] + e[1]) / 4],
      normal: [nx, ny]
    };
  }

  /* ---------- desenho do grafo ---------- */

  var MARKERS = [
    ['base', '#9aa89f'], ['leg', '#a64925'], ['direct', '#1c5b93'],
    ['win', '#08685e'], ['route', '#08685e']
  ];

  function GraphView(host, vertices, edges) {
    this.vertices = vertices;
    this.edges = edges;
    this.pos = {};
    var self = this;
    vertices.forEach(function (v) { self.pos[v.id] = [v.x, v.y]; });
    this.id = 'fwg' + (++uid);
    this.build(host);
  }

  GraphView.prototype.build = function (host) {
    var xs = this.vertices.map(function (v) { return v.x; });
    var ys = this.vertices.map(function (v) { return v.y; });
    var pad = 74;
    var minX = Math.min.apply(null, xs) - pad, maxX = Math.max.apply(null, xs) + pad;
    var minY = Math.min.apply(null, ys) - pad, maxY = Math.max.apply(null, ys) + pad;
    var svg = svgEl('svg', {
      'class': 'graph', role: 'img',
      viewBox: minX + ' ' + minY + ' ' + (maxX - minX) + ' ' + (maxY - minY)
    });
    var defs = svgEl('defs');
    var self = this;
    MARKERS.forEach(function (m) {
      var mk = svgEl('marker', {
        id: self.id + '-' + m[0], viewBox: '0 0 10 10', refX: '9', refY: '5',
        markerWidth: '6', markerHeight: '6', orient: 'auto-start-reverse'
      });
      mk.appendChild(svgEl('path', { d: 'M0 0 L10 5 L0 10 z', fill: m[1] }));
      defs.appendChild(mk);
    });
    svg.appendChild(defs);

    this.gEdges = svgEl('g');
    this.gArcs = svgEl('g');
    this.gNodes = svgEl('g');
    svg.appendChild(this.gEdges);
    svg.appendChild(this.gArcs);
    svg.appendChild(this.gNodes);

    // arestas reais
    this.edgeNodes = {};
    var pairs = {};
    this.edges.forEach(function (e) { pairs[e.from + '>' + e.to] = true; });
    this.edges.forEach(function (e) {
      var bend = pairs[e.to + '>' + e.from] ? 34 : 0;
      var g = curveGeom(self.pos[e.from], self.pos[e.to], bend);
      var path = svgEl('path', {
        'class': 'edge', d: g.d, 'marker-end': 'url(#' + self.id + '-base)'
      });
      var label = svgEl('text', { 'class': 'edge-label', x: g.mid[0], y: g.mid[1] - 6, 'text-anchor': 'middle' });
      label.textContent = e.w;
      self.gEdges.appendChild(path);
      self.gEdges.appendChild(label);
      self.edgeNodes[e.from + '>' + e.to] = path;
    });

    // vértices
    this.nodeNodes = {};
    this.vertices.forEach(function (v) {
      var g = svgEl('g', { 'class': 'node' });
      g.appendChild(svgEl('circle', { cx: v.x, cy: v.y, r: R }));
      var t = svgEl('text', { x: v.x, y: v.y });
      t.textContent = v.id;
      g.appendChild(t);
      self.gNodes.appendChild(g);
      self.nodeNodes[v.id] = g;
    });

    this.title = svgEl('title');
    svg.insertBefore(this.title, svg.firstChild);
    host.appendChild(svg);
    this.svg = svg;
  };

  GraphView.prototype.update = function (state) {
    state = state || {};
    var self = this;
    Object.keys(this.nodeNodes).forEach(function (id) {
      var cls = 'node';
      if (state.pivot === id) cls += ' pivot';
      else if (state.origin === id) cls += ' origin';
      else if (state.target === id) cls += ' target';
      self.nodeNodes[id].setAttribute('class', cls);
    });
    Object.keys(this.edgeNodes).forEach(function (key) {
      var extra = state.edgeClasses && state.edgeClasses[key];
      self.edgeNodes[key].setAttribute('class', 'edge' + (extra ? ' ' + extra : ''));
      self.edgeNodes[key].setAttribute('marker-end',
        'url(#' + self.id + '-' + (extra === 'on-route' ? 'route' : 'base') + ')');
    });
    while (this.gArcs.firstChild) this.gArcs.removeChild(this.gArcs.firstChild);
    (state.arcs || []).forEach(function (arc) {
      var g = curveGeom(self.pos[arc.from], self.pos[arc.to], arc.bend || 0);
      var marker = arc.cls === 'leg' ? 'leg' : (arc.cls === 'direct' ? 'direct' : 'win');
      self.gArcs.appendChild(svgEl('path', {
        'class': 'arc ' + arc.cls, d: g.d, 'marker-end': 'url(#' + self.id + '-' + marker + ')'
      }));
      if (arc.label !== undefined && arc.label !== null) {
        var push = (arc.bend >= 0 ? 20 : -20);
        var t = svgEl('text', {
          'class': 'arc-label ' + arc.cls,
          x: g.mid[0] + g.normal[0] * push,
          y: g.mid[1] + g.normal[1] * push - 6,
          'text-anchor': 'middle'
        });
        t.textContent = arc.label;
        self.gArcs.appendChild(t);
      }
    });
    if (state.alt) this.title.textContent = state.alt;
  };

  /* ---------- matriz ---------- */

  function MatrixView(host, vertices, opts) {
    this.vertices = vertices;
    this.opts = opts || {};
    var n = vertices.length;
    var table = el('table', 'matrix');
    var cap = el('caption', null, this.opts.caption || '');
    if (this.opts.caption) table.appendChild(cap);
    this.caption = cap;
    var thead = el('thead');
    var hr = el('tr');
    hr.appendChild(el('th', null, this.opts.corner || 'de ↓ / para →'));
    this.colHeads = [];
    vertices.forEach(function (v) {
      var th = el('th', null, v.id);
      th.scope = 'col';
      hr.appendChild(th);
    });
    thead.appendChild(hr);
    table.appendChild(thead);
    this.colHeads = Array.prototype.slice.call(hr.children, 1);
    var tbody = el('tbody');
    this.cells = [];
    this.rowHeads = [];
    for (var i = 0; i < n; i++) {
      var tr = el('tr');
      var th = el('th', null, vertices[i].id);
      th.scope = 'row';
      tr.appendChild(th);
      this.rowHeads.push(th);
      var row = [];
      for (var j = 0; j < n; j++) {
        var td = el('td', null, '');
        tr.appendChild(td);
        row.push(td);
      }
      this.cells.push(row);
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    host.appendChild(table);
    this.table = table;
  }

  MatrixView.prototype.update = function (data, hl) {
    hl = hl || {};
    var n = this.vertices.length;
    for (var i = 0; i < n; i++) {
      for (var j = 0; j < n; j++) {
        var td = this.cells[i][j];
        var v = data[i][j];
        var text = this.opts.symbolic
          ? (v === null || v === undefined ? '∅' : this.vertices[v].id)
          : fmt(v);
        if (td.textContent !== text) td.textContent = text;
        var cls = (!this.opts.symbolic && v === INF) ? 'inf' : '';
        if (!this.opts.symbolic && i === j && v < 0) cls += ' danger';
        if (hl.opA && hl.opA[0] === i && hl.opA[1] === j) cls += ' op-a';
        if (hl.opB && hl.opB[0] === i && hl.opB[1] === j) cls += ' op-b';
        if (hl.target && hl.target[0] === i && hl.target[1] === j) {
          cls += hl.improved ? ' improved' : ' target';
        }
        td.className = cls.trim();
      }
      this.rowHeads[i].className = (hl.axis === i) ? 'axis-hl' : '';
    }
    for (var c = 0; c < n; c++) {
      this.colHeads[c].className = (hl.axis === c) ? 'axis-hl' : '';
    }
    if (hl.caption !== undefined && this.caption) this.caption.textContent = hl.caption;
  };

  /* ---------- trilha de execução ---------- */

  function initialMatrices(vertices, edges) {
    var n = vertices.length, idx = {};
    vertices.forEach(function (v, i) { idx[v.id] = i; });
    var dist = [], next = [];
    for (var i = 0; i < n; i++) {
      dist.push(new Array(n).fill(INF));
      next.push(new Array(n).fill(null));
    }
    for (var d = 0; d < n; d++) { dist[d][d] = 0; next[d][d] = d; }
    edges.forEach(function (e) {
      var a = idx[e.from], b = idx[e.to];
      if (e.w < dist[a][b]) { dist[a][b] = e.w; next[a][b] = b; }
    });
    return { dist: dist, next: next, idx: idx };
  }

  function buildTrace(vertices, edges, opts) {
    opts = opts || {};
    var order = opts.order || 'kij';
    var n = vertices.length;
    var start = initialMatrices(vertices, edges);
    var dist = start.dist, next = start.next;
    var init = { dist: copy(dist), next: copy(next) };
    var steps = [];
    var lastK = -1;

    function push(o) { o.index = steps.length; steps.push(o); }

    for (var a = 0; a < n; a++) {
      for (var b = 0; b < n; b++) {
        for (var c = 0; c < n; c++) {
          var v = {};
          v[order[0]] = a; v[order[1]] = b; v[order[2]] = c;
          var k = v.k, i = v.i, j = v.j;
          if (order === 'kij' && k !== lastK) {
            lastK = k;
            push({ type: 'pivot', k: k, dist: copy(dist), next: copy(next) });
          }
          var ik = dist[i][k], kj = dist[k][j], ij = dist[i][j];
          var trivial = (i === k || j === k || i === j);
          var blocked = (ik === INF || kj === INF);
          var sum = (blocked ? INF : ik + kj);
          var improved = !blocked && sum < ij;
          if (improved) { dist[i][j] = sum; next[i][j] = next[i][k]; }
          push({
            type: 'compare', k: k, i: i, j: j,
            ik: ik, kj: kj, ij: ij, sum: sum,
            trivial: trivial, blocked: blocked, improved: improved,
            dist: copy(dist), next: copy(next)
          });
        }
      }
    }
    push({ type: 'done', dist: copy(dist), next: copy(next) });
    return { vertices: vertices, steps: steps, init: init, dist: dist, next: next };
  }

  /* ---------- reprodutor ---------- */

  function Player(opts) {
    this.steps = opts.steps;
    this.render = opts.render;
    this.speed = opts.speed || 1100;
    this.pos = 0;
    this.timer = null;
    this.visible = this.steps.map(function (_, i) { return i; });
  }

  Player.prototype.setFilter = function (fn) {
    var keep = [];
    this.steps.forEach(function (s, i) { if (fn(s)) keep.push(i); });
    if (!keep.length) keep = this.steps.map(function (_, i) { return i; });
    var current = this.visible[this.pos];
    this.visible = keep;
    var nearest = 0;
    for (var i = 0; i < keep.length; i++) { if (keep[i] <= current) nearest = i; }
    this.pos = nearest;
    this.draw();
  };

  Player.prototype.draw = function () {
    this.render(this.steps[this.visible[this.pos]], this.pos, this.visible.length);
  };

  Player.prototype.goto = function (p) {
    this.pos = Math.max(0, Math.min(this.visible.length - 1, p));
    this.draw();
  };

  Player.prototype.step = function (delta) {
    if (this.pos + delta > this.visible.length - 1) { this.pause(); return false; }
    this.goto(this.pos + delta);
    return true;
  };

  Player.prototype.playing = function () { return this.timer !== null; };

  Player.prototype.play = function () {
    if (this.timer) return;
    if (this.pos >= this.visible.length - 1) this.goto(0);
    var self = this;
    this.timer = setInterval(function () {
      if (!self.step(1)) self.pause();
    }, this.speed);
    this.onState && this.onState();
  };

  Player.prototype.pause = function () {
    if (this.timer) { clearInterval(this.timer); this.timer = null; }
    this.onState && this.onState();
  };

  Player.prototype.toggle = function () { this.playing() ? this.pause() : this.play(); };

  Player.prototype.setSpeed = function (ms) {
    this.speed = ms;
    if (this.playing()) { this.pause(); this.play(); }
  };

  Player.prototype.reset = function () { this.pause(); this.goto(0); };

  /* ---------- textos em português ---------- */

  function label(vertices, i) { return vertices[i].id; }

  function narrate(step, vertices) {
    var id = function (x) { return label(vertices, x); };
    if (step.type === 'pivot') {
      var allowed = vertices.slice(0, step.k + 1).map(function (v) { return v.id; }).join(', ');
      return {
        head: 'Nova etapa: k = ' + id(step.k),
        text: 'A partir de agora, cada caminho pode fazer parada em ' + allowed +
          '. O algoritmo vai revisar todos os pares antes de liberar o próximo vértice.',
        tone: ''
      };
    }
    if (step.type === 'done') {
      return { head: 'Fim', text: 'Todos os vértices já foram testados como parada. A matriz agora guarda a menor distância de cada par.', tone: 'win' };
    }
    var i = id(step.i), j = id(step.j), k = id(step.k);
    if (step.trivial) {
      if (step.i === step.j) {
        return { head: 'Sem comparação', text: 'Origem e destino são o mesmo vértice ' + i + '. O custo continua 0.', tone: 'keep' };
      }
      return {
        head: 'Sem comparação',
        text: 'A parada proposta é ' + k + ', que já é a ponta do trecho ' + i + ' → ' + j + '. Parar onde você já está não encurta nada.',
        tone: 'keep'
      };
    }
    if (step.blocked) {
      var falta = step.ik === INF ? (i + ' → ' + k) : (k + ' → ' + j);
      return {
        head: 'Nem precisa somar',
        text: 'Ainda não existe caminho conhecido de ' + falta + ' (∞). Sem os dois pedaços, a rota por ' + k + ' não existe. O código pula com <code>continue</code>.',
        tone: 'keep'
      };
    }
    var viaTxt = fmt(step.ik) + ' + ' + fmt(step.kj) + ' = ' + fmt(step.sum);
    if (step.improved) {
      return {
        head: 'Encurtou',
        text: 'Ir de ' + i + ' até ' + j + ' custava ' + fmt(step.ij) + '. Passando por ' + k + ': ' + viaTxt +
          '. Como ' + fmt(step.sum) + ' é menor, a matriz guarda ' + fmt(step.sum) + '.',
        tone: 'win'
      };
    }
    return {
      head: 'Mantém o valor',
      text: 'Ir de ' + i + ' até ' + j + ' custa ' + fmt(step.ij) + '. Passando por ' + k + ': ' + viaTxt +
        '. Não ficou menor, então nada muda.',
      tone: 'keep'
    };
  }

  function formulaHTML(step, vertices) {
    var id = function (x) { return label(vertices, x); };
    if (step.type !== 'compare') return '';
    var i = id(step.i), j = id(step.j), k = id(step.k);
    var base = '<span class="t">dist[' + i + '][' + j + '] = ' + fmt(step.ij) + '</span>' +
      ' &nbsp;&nbsp;versus&nbsp;&nbsp; ' +
      '<span class="a">dist[' + i + '][' + k + '] = ' + fmt(step.ik) + '</span> + ' +
      '<span class="b">dist[' + k + '][' + j + '] = ' + fmt(step.kj) + '</span>';
    if (step.blocked) return base + ' <span class="verdict keep">rota inexistente</span>';
    var res = ' &nbsp;→&nbsp; <span class="r">' + fmt(step.sum) + '</span>';
    var verdict = step.improved
      ? ' <span class="verdict win">' + fmt(step.sum) + ' &lt; ' + fmt(step.ij) + ', troca</span>'
      : ' <span class="verdict keep">não é menor, mantém</span>';
    return base + res + verdict;
  }

  /* ---------- código sincronizado ---------- */

  var CODE_LINES = [
    'for k in range(n):',
    '    for i in range(n):',
    '        if dist[i][k] == inf:',
    '            continue',
    '        for j in range(n):',
    '            if dist[k][j] == inf:',
    '                continue',
    '            candidate = dist[i][k] + dist[k][j]',
    '            if candidate < dist[i][j]:',
    '                dist[i][j] = candidate',
    '                next_vertex[i][j] = next_vertex[i][k]'
  ];

  function codeFocus(step) {
    if (step.type === 'pivot') return { on: [0], fired: [] };
    if (step.type === 'done') return { on: [], fired: [] };
    if (step.ik === INF) return { on: [2, 3], fired: [1] };
    if (step.kj === INF) return { on: [5, 6], fired: [1, 4] };
    if (step.improved) return { on: [9, 10], fired: [1, 4, 7, 8] };
    return { on: [8], fired: [1, 4, 7] };
  }

  /* ---------- laboratório principal ---------- */

  function buildLabShell(host) {
    var lab = el('div', 'lab');
    var head = el('div', 'lab-title');
    var h = el('h3', null, host.dataset.title || 'Animação');
    head.appendChild(h);
    head.appendChild(el('span', 'lab-badge', host.dataset.badge || 'Animação'));
    lab.appendChild(head);
    if (host.dataset.sub) lab.appendChild(el('p', 'lab-sub', host.dataset.sub));
    return lab;
  }

  function speedSelect(onChange) {
    var wrap = el('label');
    wrap.appendChild(document.createTextNode('Ritmo'));
    var sel = document.createElement('select');
    [['Calmo', 2000], ['Normal', 1100], ['Rápido', 520]].forEach(function (o, n) {
      var opt = document.createElement('option');
      opt.textContent = o[0]; opt.value = o[1];
      if (n === 1) opt.selected = true;
      sel.appendChild(opt);
    });
    sel.addEventListener('change', function () { onChange(+sel.value); });
    wrap.appendChild(sel);
    return wrap;
  }

  function initFwLab(host) {
    var vertices = parseVertices(host.dataset.vertices);
    var edges = parseEdges(host.dataset.edges);
    var trace = buildTrace(vertices, edges, { order: host.dataset.order || 'kij' });
    var showCode = (host.dataset.show || '').indexOf('code') >= 0;
    var showNext = (host.dataset.show || '').indexOf('next') >= 0;

    var lab = buildLabShell(host);
    var stage = el('div', 'stage');

    var left = el('div');
    left.appendChild(el('p', 'panel-label', 'O grafo'));
    var gbox = el('div', 'graph-box');
    left.appendChild(gbox);
    var graph = new GraphView(gbox, vertices, edges);

    var right = el('div');
    right.appendChild(el('p', 'panel-label', 'Matriz de distâncias'));
    var mbox = el('div', 'matrix-box');
    right.appendChild(mbox);
    var matrix = new MatrixView(mbox, vertices, { caption: ' ' });
    var legend = el('div', 'matrix-legend');
    legend.innerHTML =
      '<span><i class="swatch a"></i>primeiro trecho i → k</span>' +
      '<span><i class="swatch b"></i>segundo trecho k → j</span>' +
      '<span><i class="swatch t"></i>célula testada i → j</span>' +
      '<span><i class="swatch i"></i>valor recém-melhorado</span>';
    right.appendChild(legend);

    var nextMatrix = null;
    if (showNext) {
      right.appendChild(el('p', 'panel-label', 'Matriz do próximo vértice'));
      var nbox = el('div', 'matrix-box');
      right.appendChild(nbox);
      nextMatrix = new MatrixView(nbox, vertices, { symbolic: true });
    }

    stage.appendChild(left);
    stage.appendChild(right);
    lab.appendChild(stage);

    var formula = el('div', 'formula-live');
    lab.appendChild(formula);

    var narration = el('div', 'narration');
    narration.setAttribute('role', 'status');
    lab.appendChild(narration);

    var codeBox = null;
    if (showCode) {
      lab.appendChild(el('p', 'panel-label', 'Linha em execução'));
      codeBox = el('div', 'code-sync');
      CODE_LINES.forEach(function (line) {
        codeBox.appendChild(el('span', 'line', line));
      });
      lab.appendChild(codeBox);
    }

    var counter = el('div', 'counter');
    lab.appendChild(counter);
    var track = el('div', 'progress-track');
    var bar = el('span');
    track.appendChild(bar);
    lab.appendChild(track);

    var ticks = el('div', 'ticks');
    vertices.forEach(function (v) { ticks.appendChild(el('span', 'tick', 'k = ' + v.id)); });
    lab.appendChild(ticks);

    var controls = el('div', 'controls');
    var bPrev = el('button', null, '◀ Voltar');
    var bPlay = el('button', 'primary', '▶ Tocar');
    var bNext = el('button', null, 'Avançar ▶');
    var bReset = el('button', null, 'Recomeçar');
    controls.appendChild(bPrev);
    controls.appendChild(bPlay);
    controls.appendChild(bNext);
    controls.appendChild(bReset);
    controls.appendChild(el('span', 'spacer'));

    var detailLabel = el('label');
    detailLabel.appendChild(document.createTextNode('Passos mostrados'));
    var detailSel = document.createElement('select');
    var DETAIL = [
      ['Só as melhorias', 'wins'],
      ['Comparações reais', 'real'],
      ['Execução completa', 'full']
    ];
    var wanted = host.dataset.detail || 'real';
    DETAIL.forEach(function (o) {
      var opt = document.createElement('option');
      opt.textContent = o[0]; opt.value = o[1];
      if (o[1] === wanted) opt.selected = true;
      detailSel.appendChild(opt);
    });
    detailLabel.appendChild(detailSel);
    controls.appendChild(detailLabel);
    lab.appendChild(controls);

    host.innerHTML = '';
    host.appendChild(lab);

    var player = new Player({
      steps: trace.steps,
      speed: 1100,
      render: function (step, pos, total) {
        var gState = { arcs: [] };
        if (step.type === 'compare') {
          gState.pivot = vertices[step.k].id;
          if (step.i !== step.k) gState.origin = vertices[step.i].id;
          if (step.j !== step.k) gState.target = vertices[step.j].id;
          if (!step.trivial && !step.blocked) {
            gState.arcs.push({ from: vertices[step.i].id, to: vertices[step.k].id, label: fmt(step.ik), cls: 'leg', bend: -40 });
            gState.arcs.push({ from: vertices[step.k].id, to: vertices[step.j].id, label: fmt(step.kj), cls: 'leg', bend: -40 });
            gState.arcs.push({
              from: vertices[step.i].id, to: vertices[step.j].id,
              label: step.improved ? fmt(step.sum) : fmt(step.ij),
              cls: step.improved ? 'win' : 'direct', bend: 64
            });
          }
          gState.alt = 'Etapa k = ' + vertices[step.k].id + ', par ' + vertices[step.i].id + ' para ' + vertices[step.j].id;
        } else if (step.type === 'pivot') {
          gState.pivot = vertices[step.k].id;
          gState.alt = 'Início da etapa k = ' + vertices[step.k].id;
        } else {
          gState.alt = 'Execução concluída';
        }
        graph.update(gState);

        var hl = {};
        if (step.type === 'compare' && !step.trivial) {
          hl.opA = [step.i, step.k];
          hl.opB = [step.k, step.j];
          hl.target = [step.i, step.j];
          hl.improved = step.improved;
        }
        if (step.type === 'pivot') hl.axis = step.k;
        hl.caption = step.type === 'pivot'
          ? 'Estado no início da etapa k = ' + vertices[step.k].id
          : (step.type === 'done'
            ? (host.dataset.doneCaption || 'Matriz final de distâncias mínimas')
            : 'Estado depois desta comparação');
        matrix.update(step.dist, hl);
        if (nextMatrix) {
          nextMatrix.update(step.next, step.type === 'compare' && !step.trivial
            ? { target: [step.i, step.j], improved: step.improved } : {});
        }

        formula.innerHTML = formulaHTML(step, vertices) ||
          (step.type === 'pivot'
            ? '<span class="a">Liberando o vértice ' + vertices[step.k].id + ' como parada intermediária.</span>'
            : '<span class="r">' + (host.dataset.doneFormula || 'Matriz final pronta.') + '</span>');

        var n = narrate(step, vertices);
        if (step.type === 'done' && host.dataset.doneText) {
          n = { head: host.dataset.doneHead || 'Fim', text: host.dataset.doneText, tone: host.dataset.doneTone || 'keep' };
        }
        narration.className = 'narration ' + n.tone;
        narration.innerHTML = '<span class="head">' + n.head + '</span>' + n.text;

        if (codeBox) {
          var focus = codeFocus(step);
          Array.prototype.forEach.call(codeBox.children, function (lineEl, idx) {
            var cls = 'line';
            if (focus.fired.indexOf(idx) >= 0) cls += ' fired';
            if (focus.on.indexOf(idx) >= 0) cls += ' on';
            lineEl.className = cls;
          });
        }

        counter.textContent = 'Passo ' + (pos + 1) + ' de ' + total +
          (step.type === 'compare'
            ? ' · k = ' + vertices[step.k].id + ', i = ' + vertices[step.i].id + ', j = ' + vertices[step.j].id
            : '');
        bar.style.width = (total < 2 ? 100 : (pos / (total - 1)) * 100) + '%';

        var curK = step.type === 'done' ? vertices.length : step.k;
        Array.prototype.forEach.call(ticks.children, function (t, idx) {
          t.className = 'tick' + (idx < curK ? ' done' : (idx === curK ? ' active' : ''));
        });

        bPrev.disabled = pos === 0;
        bNext.disabled = pos === total - 1;
      }
    });

    player.onState = function () {
      bPlay.textContent = player.playing() ? '⏸ Pausar' : '▶ Tocar';
    };

    function applyFilter() {
      var mode = detailSel.value;
      player.setFilter(function (s) {
        if (s.type !== 'compare') return true;
        if (mode === 'full') return true;
        if (mode === 'wins') return s.improved;
        return !s.blocked && !s.trivial;
      });
    }

    bPrev.addEventListener('click', function () { player.pause(); player.step(-1); });
    bNext.addEventListener('click', function () { player.pause(); player.step(1); });
    bPlay.addEventListener('click', function () { player.toggle(); });
    bReset.addEventListener('click', function () { player.reset(); });
    detailSel.addEventListener('change', applyFilter);
    controls.appendChild(speedSelect(function (ms) { player.setSpeed(ms); }));

    lab.tabIndex = 0;
    lab.addEventListener('keydown', function (ev) {
      if (ev.key === 'ArrowRight') { player.pause(); player.step(1); ev.preventDefault(); }
      if (ev.key === 'ArrowLeft') { player.pause(); player.step(-1); ev.preventDefault(); }
    });

    applyFilter();
  }

  /* ---------- laboratório: percorrer caminhos (capítulo 01) ---------- */

  function initWalkLab(host) {
    var vertices = parseVertices(host.dataset.vertices);
    var edges = parseEdges(host.dataset.edges);
    var routes = host.dataset.routes.split(';').map(function (r) { return r.trim().split('>'); });

    var lab = buildLabShell(host);
    var stage = el('div', 'stage');
    var left = el('div');
    left.appendChild(el('p', 'panel-label', 'O grafo'));
    var gbox = el('div', 'graph-box');
    left.appendChild(gbox);
    var graph = new GraphView(gbox, vertices, edges);

    var right = el('div');
    right.appendChild(el('p', 'panel-label', 'Rotas possíveis'));
    var list = el('div');
    var buttons = [];
    routes.forEach(function (r, n) {
      var b = el('button', null, r.join(' → '));
      b.style.marginRight = '8px';
      b.style.marginBottom = '8px';
      b.dataset.route = n;
      list.appendChild(b);
      buttons.push(b);
    });
    right.appendChild(list);
    var strip = el('div', 'path-strip');
    right.appendChild(strip);
    var narration = el('div', 'narration');
    narration.setAttribute('role', 'status');
    right.appendChild(narration);

    stage.appendChild(left);
    stage.appendChild(right);
    lab.appendChild(stage);
    host.innerHTML = '';
    host.appendChild(lab);

    var weight = {};
    edges.forEach(function (e) { weight[e.from + '>' + e.to] = e.w; });

    var timer = null;
    function walk(route) {
      if (timer) clearTimeout(timer);
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(+b.dataset.route === routes.indexOf(route))); });
      strip.innerHTML = '';
      var cost = 0, hop = 0;
      var edgeClasses = {};
      function addNode(n) {
        if (n > 0) strip.appendChild(el('span', 'path-arrow', '→'));
        strip.appendChild(el('span', 'path-node', route[n]));
      }
      function tick() {
        if (hop > 0) {
          var key = route[hop - 1] + '>' + route[hop];
          edgeClasses[key] = 'on-route';
          cost += weight[key];
        }
        addNode(hop);
        graph.update({ edgeClasses: edgeClasses, origin: route[0], target: route[hop] });
        narration.className = 'narration';
        narration.innerHTML = '<span class="head">Custo acumulado</span>' +
          (hop === 0
            ? 'Saindo de ' + route[0] + '. Ainda não gastamos nada: custo 0.'
            : 'Pegamos a aresta ' + route[hop - 1] + ' → ' + route[hop] + ', que pesa ' + weight[route[hop - 1] + '>' + route[hop]] +
              '. Total até agora: ' + cost + '.');
        if (hop === route.length - 1) {
          var pill = el('span', 'cost-pill', 'Custo do caminho: ' + cost);
          strip.appendChild(pill);
          narration.className = 'narration win';
          narration.innerHTML = '<span class="head">Caminho completo</span>O caminho ' +
            route.join(' → ') + ' custa ' + cost + '. Esse é o número que a matriz de distâncias quer minimizar.';
          return;
        }
        hop++;
        timer = setTimeout(tick, 950);
      }
      tick();
    }

    buttons.forEach(function (b) {
      b.addEventListener('click', function () { walk(routes[+b.dataset.route]); });
    });
    graph.update({});
    narration.innerHTML = '<span class="head">Escolha uma rota</span>Clique em uma das rotas acima para percorrê-la aresta por aresta e somar o custo.';
  }

  /* ---------- laboratório: montar a matriz inicial (capítulo 02) ---------- */

  function initBuildLab(host) {
    var vertices = parseVertices(host.dataset.vertices);
    var edges = parseEdges(host.dataset.edges);
    var n = vertices.length;
    var idx = {};
    vertices.forEach(function (v, i) { idx[v.id] = i; });

    var steps = [{ kind: 'empty' }];
    for (var d = 0; d < n; d++) steps.push({ kind: 'diag', i: d });
    edges.forEach(function (e) { steps.push({ kind: 'edge', e: e }); });
    steps.push({ kind: 'done' });

    var lab = buildLabShell(host);
    var stage = el('div', 'stage');
    var left = el('div');
    left.appendChild(el('p', 'panel-label', 'O grafo'));
    var gbox = el('div', 'graph-box');
    left.appendChild(gbox);
    var graph = new GraphView(gbox, vertices, edges);
    var right = el('div');
    right.appendChild(el('p', 'panel-label', 'Matriz inicial'));
    var mbox = el('div', 'matrix-box');
    right.appendChild(mbox);
    var matrix = new MatrixView(mbox, vertices, { caption: ' ' });
    stage.appendChild(left);
    stage.appendChild(right);
    lab.appendChild(stage);
    var narration = el('div', 'narration');
    narration.setAttribute('role', 'status');
    lab.appendChild(narration);
    var counter = el('div', 'counter');
    lab.appendChild(counter);
    var track = el('div', 'progress-track');
    var bar = el('span'); track.appendChild(bar); lab.appendChild(track);
    var controls = el('div', 'controls');
    var bPlay = el('button', 'primary', '▶ Tocar');
    var bNext = el('button', null, 'Avançar ▶');
    var bReset = el('button', null, 'Recomeçar');
    controls.appendChild(bPlay); controls.appendChild(bNext); controls.appendChild(bReset);
    lab.appendChild(controls);
    host.innerHTML = '';
    host.appendChild(lab);

    function stateAt(pos) {
      var dist = [];
      for (var i = 0; i < n; i++) dist.push(new Array(n).fill(INF));
      var hl = {}, gState = { arcs: [] }, text = '', head = '', tone = '';
      for (var s = 1; s <= pos; s++) {
        var st = steps[s];
        if (st.kind === 'diag') dist[st.i][st.i] = 0;
        if (st.kind === 'edge') {
          var a = idx[st.e.from], b = idx[st.e.to];
          if (st.e.w < dist[a][b]) dist[a][b] = st.e.w;
        }
      }
      var cur = steps[pos];
      if (cur.kind === 'empty') {
        head = 'Começo';
        text = 'Antes de olhar para as arestas, supomos que não sabemos chegar a lugar nenhum. Toda célula vale ∞, que significa "caminho desconhecido".';
      } else if (cur.kind === 'diag') {
        hl.target = [cur.i, cur.i]; hl.improved = true;
        gState.origin = vertices[cur.i].id;
        head = 'Diagonal';
        text = 'Ficar parado em ' + vertices[cur.i].id + ' custa 0. Por isso a diagonal recebe zero.';
      } else if (cur.kind === 'edge') {
        var ai = idx[cur.e.from], bi = idx[cur.e.to];
        hl.target = [ai, bi]; hl.improved = true;
        gState.origin = cur.e.from; gState.target = cur.e.to;
        gState.edgeClasses = {}; gState.edgeClasses[cur.e.from + '>' + cur.e.to] = 'on-route';
        head = 'Aresta ' + cur.e.from + ' → ' + cur.e.to;
        text = 'A aresta pesa ' + cur.e.w + ', então a célula da linha ' + cur.e.from +
          ' com a coluna ' + cur.e.to + ' recebe ' + cur.e.w + '. A célula oposta continua separada: o grafo é dirigido.';
      } else {
        head = 'Matriz inicial pronta';
        tone = 'win';
        text = 'As células com ∞ não significam "impossível para sempre". Significam "ainda sem caminho conhecido". O algoritmo vai preencher várias delas.';
      }
      return { dist: dist, hl: hl, gState: gState, head: head, text: text, tone: tone };
    }

    var pos = 0, timer = null;
    function draw() {
      var s = stateAt(pos);
      matrix.update(s.dist, s.hl);
      graph.update(s.gState);
      narration.className = 'narration ' + s.tone;
      narration.innerHTML = '<span class="head">' + s.head + '</span>' + s.text;
      counter.textContent = 'Passo ' + (pos + 1) + ' de ' + steps.length;
      bar.style.width = (pos / (steps.length - 1)) * 100 + '%';
      bNext.disabled = pos === steps.length - 1;
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } bPlay.textContent = '▶ Tocar'; }
    bNext.addEventListener('click', function () { stop(); if (pos < steps.length - 1) { pos++; draw(); } });
    bReset.addEventListener('click', function () { stop(); pos = 0; draw(); });
    bPlay.addEventListener('click', function () {
      if (timer) { stop(); return; }
      if (pos >= steps.length - 1) pos = 0;
      bPlay.textContent = '⏸ Pausar';
      timer = setInterval(function () {
        if (pos < steps.length - 1) { pos++; draw(); } else stop();
      }, 1300);
    });
    draw();
  }

  /* ---------- laboratório: ordem dos laços (capítulo 04) ---------- */

  function initVersusLab(host) {
    var vertices = parseVertices(host.dataset.vertices);
    var edges = parseEdges(host.dataset.edges);
    var traceA = buildTrace(vertices, edges, { order: 'kij' });
    var traceB = buildTrace(vertices, edges, { order: 'ijk' });
    var watch = host.dataset.watch.split('>');
    var wi = 0, wj = 0;
    vertices.forEach(function (v, n) { if (v.id === watch[0]) wi = n; if (v.id === watch[1]) wj = n; });

    var lab = buildLabShell(host);

    if (host.dataset.route) {
      var route = host.dataset.route.split('>');
      lab.appendChild(el('p', 'panel-label', 'O grafo do contraexemplo'));
      var gbox = el('div', 'graph-box');
      lab.appendChild(gbox);
      var gview = new GraphView(gbox, vertices, edges);
      var routeCls = {};
      for (var r = 1; r < route.length; r++) routeCls[route[r - 1] + '>' + route[r]] = 'on-route';
      gview.update({
        edgeClasses: routeCls, origin: route[0], target: route[route.length - 1],
        alt: 'O caminho mais curto de ' + route[0] + ' até ' + route[route.length - 1] + ' é ' + route.join(' para ')
      });
      var cap = el('p', 'lab-sub');
      cap.textContent = 'Em verde, o caminho mais curto de ' + route[0] + ' até ' + route[route.length - 1] +
        ': ' + route.join(' \u2192 ') + '. A aresta direta ' + route[0] + ' \u2192 ' + route[route.length - 1] + ' é bem mais cara.';
      cap.style.marginTop = '10px';
      lab.appendChild(cap);
    }

    var versus = el('div', 'versus');
    var views = [];
    [['k por fora: k → i → j', traceA, true], ['k por dentro: i → j → k', traceB, false]].forEach(function (cfg) {
      var box = el('div');
      var h = el('h4', null, cfg[0]);
      box.appendChild(h);
      var mbox = el('div', 'matrix-box');
      box.appendChild(mbox);
      var m = new MatrixView(mbox, vertices, {});
      var res = el('p', 'result');
      box.appendChild(res);
      versus.appendChild(box);
      views.push({ trace: cfg[1], matrix: m, result: res, good: cfg[2] });
    });
    lab.appendChild(versus);

    var narration = el('div', 'narration');
    narration.setAttribute('role', 'status');
    lab.appendChild(narration);
    var counter = el('div', 'counter');
    lab.appendChild(counter);
    var track = el('div', 'progress-track');
    var bar = el('span'); track.appendChild(bar); lab.appendChild(track);
    var controls = el('div', 'controls');
    var bPlay = el('button', 'primary', '▶ Tocar as duas');
    var bNext = el('button', null, 'Avançar ▶');
    var bEnd = el('button', null, 'Ir ao final');
    var bReset = el('button', null, 'Recomeçar');
    [bPlay, bNext, bEnd, bReset].forEach(function (b) { controls.appendChild(b); });
    lab.appendChild(controls);
    host.innerHTML = '';
    host.appendChild(lab);

    var comparesA = traceA.steps.filter(function (s) { return s.type === 'compare'; });
    var comparesB = traceB.steps.filter(function (s) { return s.type === 'compare'; });
    var total = Math.max(comparesA.length, comparesB.length);
    var pos = 0, timer = null;

    function draw() {
      [comparesA, comparesB].forEach(function (list, n) {
        var step = list[Math.min(pos, list.length - 1)];
        var view = views[n];
        view.matrix.update(step.dist, {
          opA: [step.i, step.k], opB: [step.k, step.j],
          target: [step.i, step.j], improved: step.improved
        });
        var value = step.dist[wi][wj];
        var ok = value === traceA.dist[wi][wj];
        view.result.className = 'result ' + (pos === total - 1 ? (ok ? 'ok' : 'bad') : '');
        view.result.textContent = watch[0] + ' → ' + watch[1] + ': ' + fmt(value) +
          (pos === total - 1 ? (ok ? '  (correto)' : '  (errado)') : '');
      });
      var a = comparesA[Math.min(pos, comparesA.length - 1)];
      counter.textContent = 'Comparação ' + (pos + 1) + ' de ' + total;
      bar.style.width = (pos / (total - 1)) * 100 + '%';
      bNext.disabled = pos === total - 1;
      if (pos === total - 1) {
        narration.className = 'narration win';
        narration.innerHTML = '<span class="head">Resultado</span>Com k por fora, ' + watch[0] + ' → ' + watch[1] +
          ' termina em ' + fmt(traceA.dist[wi][wj]) + '. Com k por dentro, uma única passagem termina em ' +
          fmt(traceB.dist[wi][wj]) + '. A célula certa foi visitada cedo demais e nunca mais foi revisitada.';
      } else {
        narration.className = 'narration';
        narration.innerHTML = '<span class="head">Mesma comparação, ordem diferente</span>' +
          'À esquerda, a etapa atual é k = ' + vertices[a.k].id +
          '. À direita, a mesma posição da contagem cai em outro trio, porque os laços giram em outra ordem.';
      }
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } bPlay.textContent = '▶ Tocar as duas'; }
    bNext.addEventListener('click', function () { stop(); if (pos < total - 1) { pos++; draw(); } });
    bEnd.addEventListener('click', function () { stop(); pos = total - 1; draw(); });
    bReset.addEventListener('click', function () { stop(); pos = 0; draw(); });
    bPlay.addEventListener('click', function () {
      if (timer) { stop(); return; }
      if (pos >= total - 1) pos = 0;
      bPlay.textContent = '⏸ Pausar';
      timer = setInterval(function () { if (pos < total - 1) { pos++; draw(); } else stop(); }, 240);
    });
    draw();
  }

  /* ---------- laboratório: reconstrução do caminho (capítulo 05) ---------- */

  function initPathLab(host) {
    var vertices = parseVertices(host.dataset.vertices);
    var edges = parseEdges(host.dataset.edges);
    var trace = buildTrace(vertices, edges, {});
    var n = vertices.length;

    var lab = buildLabShell(host);
    var picker = el('div', 'controls');
    function makeSelect(labelText, initial) {
      var wrap = el('label');
      wrap.appendChild(document.createTextNode(labelText));
      var sel = document.createElement('select');
      vertices.forEach(function (v, i) {
        var o = document.createElement('option');
        o.value = i; o.textContent = v.id;
        if (i === initial) o.selected = true;
        sel.appendChild(o);
      });
      wrap.appendChild(sel);
      picker.appendChild(wrap);
      return sel;
    }
    var selFrom = makeSelect('Origem', 0);
    var selTo = makeSelect('Destino', n - 1);
    lab.appendChild(picker);

    var stage = el('div', 'stage');
    var left = el('div');
    left.appendChild(el('p', 'panel-label', 'O grafo'));
    var gbox = el('div', 'graph-box');
    left.appendChild(gbox);
    var graph = new GraphView(gbox, vertices, edges);
    var right = el('div');
    right.appendChild(el('p', 'panel-label', 'Matriz next_vertex (próxima parada)'));
    var mbox = el('div', 'matrix-box');
    right.appendChild(mbox);
    var matrix = new MatrixView(mbox, vertices, { symbolic: true, caption: 'Cada célula guarda o primeiro vértice a visitar depois da origem.' });
    stage.appendChild(left);
    stage.appendChild(right);
    lab.appendChild(stage);

    var strip = el('div', 'path-strip');
    lab.appendChild(strip);
    var narration = el('div', 'narration');
    narration.setAttribute('role', 'status');
    lab.appendChild(narration);

    var controls = el('div', 'controls');
    var bStep = el('button', 'primary', 'Avançar um vértice ▶');
    var bAll = el('button', null, 'Mostrar o caminho inteiro');
    var bReset = el('button', null, 'Recomeçar');
    [bStep, bAll, bReset].forEach(function (b) { controls.appendChild(b); });
    lab.appendChild(controls);
    host.innerHTML = '';
    host.appendChild(lab);

    var path, cursor;

    function fullPath(a, b) {
      if (trace.next[a][b] === null) return null;
      var out = [a], cur = a, guard = 0;
      while (cur !== b && guard++ < 50) { cur = trace.next[cur][b]; out.push(cur); }
      return out;
    }

    function draw() {
      var a = +selFrom.value, b = +selTo.value;
      path = fullPath(a, b);
      var shown = path ? path.slice(0, cursor + 1) : [];
      strip.innerHTML = '';
      shown.forEach(function (v, i) {
        if (i > 0) strip.appendChild(el('span', 'path-arrow', '→'));
        strip.appendChild(el('span', 'path-node', vertices[v].id));
      });
      var edgeClasses = {};
      for (var i = 1; i < shown.length; i++) {
        edgeClasses[vertices[shown[i - 1]].id + '>' + vertices[shown[i]].id] = 'on-route';
      }
      var here = shown.length ? shown[shown.length - 1] : a;
      graph.update({ edgeClasses: edgeClasses, origin: vertices[a].id, target: vertices[b].id, pivot: (here !== a && here !== b) ? vertices[here].id : undefined });
      matrix.update(trace.next, path && here !== b ? { target: [here, b] } : {});

      if (!path) {
        narration.className = 'narration keep';
        narration.innerHTML = '<span class="head">Sem caminho</span>A célula next_vertex[' + vertices[a].id + '][' + vertices[b].id +
          '] guarda ∅. Não existe rota de ' + vertices[a].id + ' até ' + vertices[b].id + ', então a função devolve uma lista vazia.';
        bStep.disabled = true;
        return;
      }
      bStep.disabled = cursor >= path.length - 1;
      if (cursor >= path.length - 1) {
        strip.appendChild(el('span', 'cost-pill', 'Distância: ' + fmt(trace.dist[a][b])));
        narration.className = 'narration win';
        narration.innerHTML = '<span class="head">Chegamos</span>O caminho é ' +
          path.map(function (p) { return vertices[p].id; }).join(' → ') + ', com custo ' + fmt(trace.dist[a][b]) +
          '. A coluna consultada foi sempre a do destino; só a linha mudou.';
      } else {
        var nxt = trace.next[here][b];
        narration.className = 'narration';
        narration.innerHTML = '<span class="head">Próxima consulta</span>Estamos em ' + vertices[here].id +
          ' e queremos ' + vertices[b].id + '. Lendo next_vertex[' + vertices[here].id + '][' + vertices[b].id + '] encontramos ' +
          vertices[nxt].id + '. Vá para ' + vertices[nxt].id + ' e repita a consulta a partir dali.';
      }
    }

    function restart() { cursor = 0; draw(); }
    bStep.addEventListener('click', function () { if (path && cursor < path.length - 1) { cursor++; draw(); } });
    bAll.addEventListener('click', function () { if (path) { cursor = path.length - 1; draw(); } });
    bReset.addEventListener('click', restart);
    selFrom.addEventListener('change', restart);
    selTo.addEventListener('change', restart);
    restart();
  }

  /* ---------- laboratório: crescimento n ao cubo (capítulo 08) ---------- */

  function initBarsLab(host) {
    var sizes = host.dataset.sizes.split(',').map(Number);
    var lab = buildLabShell(host);
    var bars = el('div', 'bars');
    var maxV = Math.pow(Math.max.apply(null, sizes), 3);
    sizes.forEach(function (s) {
      var bar = el('div', 'bar');
      var cap = el('span', 'cap', (Math.pow(s, 3)).toLocaleString('pt-BR'));
      var fill = el('span', 'fill');
      fill.dataset.h = (Math.pow(s, 3) / maxV) * 100;
      var lbl = el('span', 'lbl', 'n = ' + s);
      bar.appendChild(cap); bar.appendChild(fill); bar.appendChild(lbl);
      bars.appendChild(bar);
    });
    lab.appendChild(bars);
    var narration = el('div', 'narration');
    narration.innerHTML = '<span class="head">Leitura das barras</span>Cada barra mostra quantas comparações <code>dist[i][k] + dist[k][j]</code> o algoritmo executa: exatamente n × n × n. Dobrar o número de vértices multiplica o trabalho por oito.';
    lab.appendChild(narration);
    var controls = el('div', 'controls');
    var bAnim = el('button', 'primary', 'Animar o crescimento');
    controls.appendChild(bAnim);
    lab.appendChild(controls);
    host.innerHTML = '';
    host.appendChild(lab);

    function run() {
      var fills = bars.querySelectorAll('.fill');
      Array.prototype.forEach.call(fills, function (f) { f.style.height = '0'; });
      Array.prototype.forEach.call(fills, function (f, i) {
        setTimeout(function () { f.style.height = f.dataset.h + '%'; }, 120 + i * 260);
      });
    }
    bAnim.addEventListener('click', run);
    setTimeout(run, 400);
  }

  /* ---------- animação do cabeçalho (índice) ---------- */

  function initHeroLab(host) {
    var vertices = parseVertices(host.dataset.vertices);
    var edges = parseEdges(host.dataset.edges);
    var gbox = el('div', 'graph-box');
    var graph = new GraphView(gbox, vertices, edges);
    var caption = el('p', 'lab-sub');
    host.innerHTML = '';
    host.appendChild(gbox);
    host.appendChild(caption);

    var frames = [
      { arcs: [{ from: 'A', to: 'D', label: '10', cls: 'direct', bend: 64 }], text: 'A rota direta de A até D custa 10.' },
      { pivot: 'B', arcs: [{ from: 'A', to: 'C', label: '5', cls: 'leg', bend: -40 }], text: 'Passando por B, o algoritmo descobre A → C por 5.' },
      { pivot: 'C', arcs: [{ from: 'A', to: 'C', label: '5', cls: 'leg', bend: -40 }, { from: 'C', to: 'D', label: '1', cls: 'leg', bend: -40 }, { from: 'A', to: 'D', label: '6', cls: 'win', bend: 64 }], text: 'Agora A → C → D soma 5 + 1 = 6, menos que 10.' },
      { arcs: [{ from: 'A', to: 'D', label: '6', cls: 'win', bend: 64 }], text: 'A menor distância de A até D é 6, e é isso que a matriz guarda.' }
    ];
    var f = 0;
    function tick() {
      var fr = frames[f];
      graph.update({ pivot: fr.pivot, arcs: fr.arcs, alt: fr.text });
      caption.textContent = fr.text;
      f = (f + 1) % frames.length;
    }
    tick();
    setInterval(tick, 2600);
  }

  /* ---------- peças reutilizáveis (usadas por simulacao.js) ---------- */

  window.FW = {
    GraphView: GraphView,
    MatrixView: MatrixView,
    Player: Player,
    buildTrace: buildTrace,
    narrate: narrate,
    formulaHTML: formulaHTML,
    parseVertices: parseVertices,
    parseEdges: parseEdges,
    CODE_LINES: CODE_LINES,
    codeFocus: codeFocus,
    fmt: fmt,
    el: el,
    INF: INF
  };

  /* ---------- inicialização ---------- */

  var INITS = {
    'fw-lab': initFwLab,
    'walk-lab': initWalkLab,
    'build-lab': initBuildLab,
    'versus-lab': initVersusLab,
    'path-lab': initPathLab,
    'bars-lab': initBarsLab,
    'hero-lab': initHeroLab
  };

  document.addEventListener('DOMContentLoaded', function () {
    Object.keys(INITS).forEach(function (key) {
      document.querySelectorAll('[data-' + key + ']').forEach(function (host) {
        try { INITS[key](host); }
        catch (err) {
          host.innerHTML = '<div class="no-js">Não foi possível montar esta animação: ' + err.message + '</div>';
        }
      });
    });
    document.querySelectorAll('[data-print]').forEach(function (b) {
      b.addEventListener('click', function () { window.print(); });
    });
    document.querySelectorAll('[data-copy]').forEach(function (button) {
      button.addEventListener('click', function () {
        var code = document.getElementById(button.dataset.copy);
        var range = document.createRange();
        range.selectNodeContents(code);
        var sel = window.getSelection();
        sel.removeAllRanges(); sel.addRange(range);
        if (navigator.clipboard) navigator.clipboard.writeText(code.textContent);
      });
    });
    var openDetails = [];
    window.addEventListener('beforeprint', function () {
      openDetails = Array.prototype.filter.call(document.querySelectorAll('details'), function (d) { return !d.open; });
      openDetails.forEach(function (d) { d.open = true; });
    });
    window.addEventListener('afterprint', function () { openDetails.forEach(function (d) { d.open = false; }); });
  });
})();
