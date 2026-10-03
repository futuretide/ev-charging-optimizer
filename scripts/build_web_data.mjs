// Builds compact JSON for the static browser demo (docs/).
// Usage: node scripts/build_web_data.mjs
import fs from 'fs';
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const cands = read('data/processed/candidate_sites_prepped.geojson').features;
const tracts = read('data/cleaned/merged_data.geojson').features;
const opt = read('data/processed/optimal_sites_dgal.geojson').features;
const stations = read('data/raw/dc_stations.geojson').features;

const R = 6378137;
const toLL = (x, y) => [x / R * 180 / Math.PI, (2 * Math.atan(Math.exp(y / R)) - Math.PI / 2) * 180 / Math.PI];
const r5 = v => Math.round(v * 1e5) / 1e5;

// point-in-polygon (ray casting, with holes)
const inRing = (pt, ring) => {
  let c = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i], [xj, yj] = ring[j];
    if ((yi > pt[1]) !== (yj > pt[1]) && pt[0] < (xj - xi) * (pt[1] - yi) / (yj - yi) + xi) c = !c;
  }
  return c;
};
const inPoly = (pt, rings) => inRing(pt, rings[0]) && !rings.slice(1).some(h => inRing(pt, h));

const ll = cands.map(f => toLL(...f.geometry.coordinates));
const covers = tracts.map(t => {
  const out = [];
  ll.forEach((p, i) => { if (inPoly(p, t.geometry.coordinates)) out.push(i); });
  return out;
});

const key = f => f.geometry.coordinates.join(',');
const optKeys = new Set(opt.map(key));

const out = {
  candidates: cands.map(f => [f.geometry.coordinates[0], f.geometry.coordinates[1],
    Math.round(f.properties.demand_score * 1e4) / 1e4, f.properties.population, f.properties.median_income]),
  tracts: tracts.map((t, i) => ({
    id: t.properties.GEOID, pop: t.properties.population, inc: t.properties.median_income,
    poly: t.geometry.coordinates.map(r => r.map(([x, y]) => [r5(x), r5(y)])), covers: covers[i]
  })),
  baseline: cands.map((f, i) => optKeys.has(key(f)) ? i : -1).filter(i => i >= 0),
  stations: stations.map(f => f.geometry.coordinates.map(r5))
};
fs.writeFileSync('docs/data/data.json', JSON.stringify(out));
console.log('candidates', out.candidates.length, 'tracts', out.tracts.length, 'baseline', out.baseline.length,
  'stations', out.stations.length, 'tracts w/o cover', covers.filter(c => !c.length).length);
