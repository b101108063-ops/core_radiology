// 桌面 + 行動截圖驗證
const { chromium } = require('playwright-core');
const path = require('path');

const BASE = 'http://localhost:1319/core_radiology';
const OUT = '/home/node/.openclaw/workspace/core_radiology_hugo/docs/screenshots';

const SHOTS = [
  { name: '01-home-desktop',   url: '/',                        vp: { width: 1440, height: 900 } },
  { name: '02-chapter-desktop',url: '/docs/thoracic/',          vp: { width: 1440, height: 900 } },
  { name: '03-chapter-scrolled', url: '/docs/thoracic/',        vp: { width: 1440, height: 900 }, scroll: 2200 },
  { name: '04-home-mobile',    url: '/',                        vp: { width: 390, height: 844 }, mobile: true },
  { name: '05-chapter-mobile', url: '/docs/thoracic/',          vp: { width: 390, height: 844 }, mobile: true },
  { name: '06-narrow-desktop', url: '/docs/msk/',               vp: { width: 1180, height: 800 } },
];

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const results = [];

  for (const s of SHOTS) {
    const ctx = await browser.newContext({
      viewport: s.vp,
      deviceScaleFactor: 2,
      isMobile: !!s.mobile,
      hasTouch: !!s.mobile,
    });
    const page = await ctx.newPage();
    const errors = [];
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', e => errors.push('pageerror: ' + e.message));

    await page.goto(BASE + s.url, { waitUntil: 'networkidle', timeout: 60000 });
    if (s.scroll) {
      await page.evaluate(y => window.scrollTo(0, y), s.scroll);
      await page.waitForTimeout(700);
    }
    await page.waitForTimeout(500);

    // 量測：水平溢出
    const metrics = await page.evaluate(() => {
      const de = document.documentElement;
      const overflow = de.scrollWidth - de.clientWidth;
      // 找出溢出的元素
      const offenders = [];
      if (overflow > 1) {
        document.querySelectorAll('*').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.right > de.clientWidth + 1 && r.width > 0) {
            offenders.push(el.tagName + '.' + (el.className || '').toString().split(' ').slice(0,2).join('.') + ' right=' + Math.round(r.right));
          }
        });
      }
      const figs = document.querySelectorAll('.atlas-figure').length;
      const tables = document.querySelectorAll('.atlas-table-wrap').length;
      const tocLinks = document.querySelectorAll('#TableOfContents a').length;
      const sidebarChapters = document.querySelectorAll('.atlas-chapter').length;
      const activeToc = document.querySelectorAll('#TableOfContents a.is-active').length;
      const progress = (document.getElementById('atlas-progress-pct') || {}).textContent;
      const imgs = Array.from(document.querySelectorAll('.atlas-figure img'));
      // 只檢查視窗內的圖片（lazy-load 造成視窗外圖片 naturalWidth=0 屬正常）
      const inView = imgs.filter(i => {
        const r = i.getBoundingClientRect();
        return r.top < window.innerHeight && r.bottom > 0;
      });
      const brokenImgs = inView.filter(i => i.complete && i.naturalWidth === 0).length;
      return { overflow, offenders: offenders.slice(0, 5), figs, tables, tocLinks, sidebarChapters, activeToc, progress, totalImgs: imgs.length, brokenImgs };
    });

    await page.screenshot({ path: path.join(OUT, s.name + '.png'), fullPage: false });
    results.push({ shot: s.name, ...metrics, consoleErrors: errors.slice(0, 5) });
    await ctx.close();
  }

  // 影像檢視器互動測試
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push(e.message));
    await page.goto(BASE + '/docs/thoracic/', { waitUntil: 'networkidle' });
    await page.locator('.atlas-figure-frame').first().click();
    await page.waitForTimeout(900);
    const opened = await page.locator('#atlas-viewer.is-open').count();
    const imgSrc = await page.locator('#atlas-viewer-img-a').getAttribute('src');
    // 縮放
    await page.locator('[data-viewer-action="zoom-in"]').click();
    await page.waitForTimeout(300);
    const zoom = await page.locator('#atlas-viewer-zoom').textContent();
    // 對比模式
    await page.locator('[data-viewer-action="compare"]').click();
    await page.waitForTimeout(600);
    const cmpOpen = await page.locator('#atlas-viewer-pane-b.is-visible').count();
    const thumbs = await page.locator('#atlas-viewer-thumbs .atlas-viewer-thumb').count();
    await page.screenshot({ path: path.join(OUT, '07-viewer-desktop.png') });
    results.push({ shot: 'viewer', opened, imgSrc, zoom, cmpOpen, thumbs, consoleErrors: errs });
    await ctx.close();
  }

  // 行動版影像檢視器
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const page = await ctx.newPage();
    await page.goto(BASE + '/docs/thoracic/', { waitUntil: 'networkidle' });
    await page.locator('.atlas-figure-frame').first().click();
    await page.waitForTimeout(900);
    const opened = await page.locator('#atlas-viewer.is-open').count();
    await page.screenshot({ path: path.join(OUT, '08-viewer-mobile.png') });
    results.push({ shot: 'viewer-mobile', opened });
    await ctx.close();
  }

  // 搜尋測試
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await ctx.newPage();
    await page.goto(BASE + '/', { waitUntil: 'networkidle' });
    await page.fill('#atlas-search-input', 'atelectasis');
    await page.waitForTimeout(1200);
    const hits = await page.locator('#atlas-search-results li').count();
    const open = await page.locator('#atlas-search-results.is-open').count();
    await page.screenshot({ path: path.join(OUT, '09-search-desktop.png') });
    results.push({ shot: 'search', hits, open });
    await ctx.close();
  }

  console.log(JSON.stringify(results, null, 2));
  await browser.close();
})();
