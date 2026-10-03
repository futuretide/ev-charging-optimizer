importScripts('lib/highs.js', 'optimizer.js');
let highs, data;
const ready = (async () => {
  highs = await Module({ locateFile: f => 'lib/' + f });
  data = await (await fetch('data/data.json')).json();
  return data;
})();
ready.then(d => postMessage({ type: 'ready', data: d })).catch(e => postMessage({ type: 'error', message: String(e) }));
onmessage = async e => {
  try {
    await ready;
    const r = await EVOpt.solve(highs, data, e.data);
    r.stats = EVOpt.stats(data, r.selected);
    postMessage({ type: 'result', result: r });
  } catch (err) { postMessage({ type: 'error', message: String(err) }); }
};
