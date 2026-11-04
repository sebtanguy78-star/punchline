// Render overlay frames (transparent PNG, 1920x1080) with headless Chromium.
// usage (run from <workdir>/render):  node render.js <outdir> <startFrame> <endFrame>
//                                     node render.js <outdir> t=1.2,3.4      (stills named t<sec>.png)
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [out, a, b] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error('PAGEERR', e); process.exit(1); });
  await page.goto('file://' + path.resolve('overlay.html'));
  await page.evaluate(() => window.ready);
  const fps = await page.evaluate(() => window.PLAN.fps);
  let list;
  if (a.startsWith('t=')) list = a.slice(2).split(',').map(s => ({ name: 't' + s, t: +s }));
  else { list = []; for (let i = +a; i < +b; i++) list.push({ name: String(i).padStart(5, '0'), t: i / fps }); }
  for (const f of list) {
    await page.evaluate(t => window.render(t), f.t);
    await page.screenshot({ path: path.join(out, f.name + '.png'), omitBackground: true, type: 'png' });
  }
  await browser.close();
})();
