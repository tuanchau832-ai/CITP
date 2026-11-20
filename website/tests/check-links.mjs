import assert from 'node:assert/strict';
import { stat } from 'node:fs/promises';
import { createServer } from 'vite';

const expected = [
  '/', '/pages/background', '/pages/problem-criteria', '/pages/design-options',
  '/pages/detailed-design', '/pages/prototyping', '/pages/implementation',
  '/pages/cost-analysis', '/pages/considerations', '/pages/recommendations',
  '/pages/references', '/pages/appendices', '/simulator', '/station',
];

const server = await createServer({ server: { middlewareMode: true }, appType: 'custom' });
try {
  const { renderReport } = await server.ssrLoadModule('/tests/render-report.tsx');
  const pages = new Map();
  for (const path of expected) {
    const html = renderReport(path);
    assert.equal([...html.matchAll(/<h1[ >]/g)].length, 1, path);
    assert.match(html, /DRAFT — content pending verification/);
    assert.match(html, /href="#report-main"/);
    assert.match(html, /aria-current="page"/);
    assert.match(html, /Explore Hanoi WaterWatch/);
    pages.set(path, html);
  }

  for (const [path, html] of pages) {
    for (const [, href] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
      const origin = 'https://citp.test';
      const target = new URL(href, `${origin}${path}`);
      if (target.origin !== origin) continue;
      const destination = pages.get(target.pathname);
      if (!destination) {
        const asset = new URL(`../public${target.pathname}`, import.meta.url);
        const file = await stat(asset).catch(() => undefined);
        assert.ok(file?.isFile(), `${path} links to missing page or file ${href}`);
        continue;
      }
      if (target.hash) {
        assert.ok(destination.includes(`id="${target.hash.slice(1)}"`), `${path} links to missing anchor ${href}`);
      }
    }
  }

  assert.match(renderReport('/missing'), /Report page unavailable/);
  console.log(`Verified ${pages.size} report routes, internal links, and the missing-page view.`);
} finally {
  await server.close();
}
