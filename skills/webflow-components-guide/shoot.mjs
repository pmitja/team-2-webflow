// Posname posamezne komponente z objavljene strani prek Chrome DevTools Protocol.
// Uporaba: node shoot.mjs <shots.json> <izhodna-mapa>
// shots.json: [{ "id": "button", "url": "https://site.com/", "selector": ".button", "index": 0, "pad": 24 }]
// Brez odvisnosti: rabi Google Chrome in Node 22+ (vgrajen WebSocket).
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [, , shotsPath, outDir] = process.argv;
if (!shotsPath || !outDir) { console.error('Uporaba: node shoot.mjs <shots.json> <izhodna-mapa>'); process.exit(1); }
const shots = JSON.parse(readFileSync(shotsPath, 'utf8'));
mkdirSync(outDir, { recursive: true });

const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = mkdtempSync(join(tmpdir(), 'wf-guide-'));
const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
  '--hide-scrollbars', '--no-first-run', '--window-size=1440,900', 'about:blank'], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));
let port;
for (let i = 0; i < 100 && !port; i++) {
  const f = join(profile, 'DevToolsActivePort');
  if (existsSync(f)) port = readFileSync(f, 'utf8').split('\n')[0];
  else await sleep(100);
}
if (!port) { console.error('Chrome se ni zagnal.'); chrome.kill(); process.exit(1); }

const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let seq = 0; const pending = new Map(); const waiters = [];
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  else if (m.method) waiters.filter(w => w.method === m.method).forEach(w => { w.fn(m); waiters.splice(waiters.indexOf(w), 1); });
});
const send = (method, params = {}) => new Promise(r => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const once = method => new Promise(fn => waiters.push({ method, fn }));
const evaluate = async expr => (await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })).result?.result?.value;

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 2, mobile: false });

// Scroll čez stran (lazy slike, IX), nato prikaži elemente, ki jih Webflow IX skrije do scrolla.
const PREP = `(async () => {
  const s = ms => new Promise(r => setTimeout(r, ms));
  document.documentElement.style.scrollBehavior = 'auto'; document.body.style.scrollBehavior = 'auto';
  for (let y = 0; y < document.body.scrollHeight; y += 700) { window.scrollTo(0, y); await s(120); }
  window.scrollTo(0, 0); await s(300);
  document.querySelectorAll('[data-w-id], [style*="opacity: 0"], [style*="opacity:0"]').forEach(el => {
    if (getComputedStyle(el).opacity === '0') el.style.opacity = '1';
    if (/translate|scale|rotate/.test(el.style.transform || '')) el.style.transform = 'none';
  });
  document.querySelectorAll('img[loading="lazy"]').forEach(i => i.loading = 'eager');
  await document.fonts.ready; await s(600);
  return document.body.scrollHeight;
})()`;

const results = [];
let currentUrl = null;
for (const shot of shots) {
  try {
    if (shot.url !== currentUrl) {
      const loaded = once('Page.loadEventFired');
      await send('Page.navigate', { url: shot.url });
      await Promise.race([loaded, sleep(20000)]);
      await sleep(800);
      await evaluate(PREP);
      currentUrl = shot.url;
    }
    const box = await evaluate(`(() => {
      const el = document.querySelectorAll(${JSON.stringify(shot.selector)})[${shot.index || 0}];
      if (!el) return null;
      // skrij fixed/sticky elemente, ki niso del komponente, da ne prekrivajo posnetka
      document.querySelectorAll('body *').forEach(n => {
        const p = getComputedStyle(n).position;
        if ((p === 'fixed' || p === 'sticky') && !n.contains(el) && !el.contains(n)) { n.dataset.wfgHidden = '1'; n.style.visibility = 'hidden'; }
      });
      const r = el.getBoundingClientRect();
      return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height };
    })()`);
    if (!box || box.w < 4 || box.h < 4) { results.push({ id: shot.id, ok: false, error: 'element ni najden ali je prazen' }); continue; }
    const pad = shot.pad ?? 24;
    const clip = { x: Math.max(0, box.x - pad), y: Math.max(0, box.y - pad), width: Math.min(1440, box.w + pad * 2), height: Math.min(1800, box.h + pad * 2), scale: 1 };
    const shotRes = await send('Page.captureScreenshot', { format: 'png', clip, captureBeyondViewport: true });
    const file = join(outDir, `${shot.id}.png`);
    writeFileSync(file, Buffer.from(shotRes.result.data, 'base64'));
    results.push({ id: shot.id, ok: true, file, width: Math.round(clip.width), height: Math.round(clip.height), cut: box.h + pad * 2 > 1800 });
    await evaluate(`document.querySelectorAll('[data-wfg-hidden]').forEach(n => { n.style.visibility = ''; delete n.dataset.wfgHidden; })`);
  } catch (e) {
    results.push({ id: shot.id, ok: false, error: String(e) });
  }
}

ws.close(); chrome.kill();
await sleep(300);
try { rmSync(profile, { recursive: true, force: true }); } catch {}
console.log(JSON.stringify(results, null, 2));
