// DGAL model (same formulation as scripts/dgal_model.py) solved exactly in-browser with HiGHS (WASM).
// maximize  sum(demand_i * x_i) + w * sum(y_j)
// s.t.      sum(x_i) <= N;  sum_{i in covers[j]} x_i >= y_j;  x_i + x_k <= 1 for pairs closer than minDist
(function (root) {
  function closePairs(cands, minDist) {
    const pairs = [];
    if (minDist <= 0) return pairs;
    const cell = Math.max(minDist, 1), grid = new Map(), r2 = minDist * minDist;
    const k = (a, b) => a + ',' + b;
    cands.forEach((c, i) => {
      const gx = Math.floor(c[0] / cell), gy = Math.floor(c[1] / cell);
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
        const arr = grid.get(k(gx + dx, gy + dy));
        if (arr) for (const j of arr) {
          const ex = c[0] - cands[j][0], ey = c[1] - cands[j][1];
          if (ex * ex + ey * ey <= r2) pairs.push([j, i]);
        }
      }
      const key = k(gx, gy);
      if (!grid.has(key)) grid.set(key, []);
      grid.get(key).push(i);
    });
    return pairs;
  }

  function buildLP(data, p) {
    const { candidates: cands, tracts } = data;
    const rule = p.rule || 'r50';
    const pairs = closePairs(cands, p.minDist);
    const lines = ['Maximize', ' obj: ' + cands.map((c, i) => `${c[2]} x${i}`).join(' + ')];
    const live = tracts.map((t, j) => t.covers[rule].length ? j : -1).filter(j => j >= 0);
    if (p.weight > 0 && live.length) lines[1] += ' + ' + live.map(j => `${p.weight} y${j}`).join(' + ');
    lines.push('Subject To', ' limit: ' + cands.map((_, i) => `x${i}`).join(' + ') + ` <= ${p.n}`);
    live.forEach(j => lines.push(` c${j}: ` + tracts[j].covers[rule].map(i => `x${i}`).join(' + ') + ` - y${j} >= 0`));
    pairs.forEach(([a, b], n) => lines.push(` p${n}: x${a} + x${b} <= 1`));
    lines.push('Binary', ' ' + cands.map((_, i) => `x${i}`).join(' ') + ' ' + live.map(j => `y${j}`).join(' '), 'End');
    return { lp: lines.join('\n'), pairs: pairs.length };
  }

  async function solve(highs, data, p) {
    const { lp, pairs } = buildLP(data, p);
    const t0 = performance.now();
    const res = await highs.solve(lp, { time_limit: p.timeLimit || 25, mip_rel_gap: 0 });
    const sel = [];
    for (const [name, col] of Object.entries(res.Columns || {}))
      if (name[0] === 'x' && col.Primal > 0.5) sel.push(+name.slice(1));
    sel.sort((a, b) => a - b);
    return { selected: sel, objective: res.ObjectiveValue, status: res.Status, pairs, ms: performance.now() - t0 };
  }

  function stats(data, sel, rule) {
    rule = rule || 'inside';
    const s = new Set(sel);
    let covered = 0, pop = 0, popAll = 0, demand = 0;
    data.tracts.forEach(t => {
      popAll += t.pop || 0;
      if (t.covers[rule].some(i => s.has(i))) { covered++; pop += t.pop || 0; }
    });
    sel.forEach(i => demand += data.candidates[i][2]);
    return { covered, tracts: data.tracts.length, pop, popAll, demand };
  }

  root.EVOpt = { solve, stats, buildLP, closePairs };
})(typeof window !== 'undefined' ? window : globalThis);
