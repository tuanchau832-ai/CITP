import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const station = '/stations/HWW-KNG-001';

test.beforeEach(async ({ page }) => {
  // The station directory remains usable without network imagery.
  await page.route('https://tile.openstreetmap.org/**', route => route.abort());
});

test('renders the three stations and the simulated-data notice on every public page', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.station-row')).toHaveCount(3);
  await expect(page.locator('.station-row').filter({ hasText: 'HWW-NHU-001' })).toContainText('Planned station');
  for (const path of ['/', `${station}/dashboard`, `${station}/model`, '/alerts', '/simulation', '/login']) {
    await page.goto(path);
    await expect(page.getByRole('note')).toContainText('All readings on this site');
    await expect(page.locator('main h1')).toBeVisible();
  }
  await page.goto('/simulation');
  await expect(page.getByRole('button', { name: 'Start replay' })).toHaveCount(0);
});

test('keeps sensor selection keyboard-accessible when the 3D asset is unavailable', async ({ page }) => {
  await page.route('**/models/station-v1.glb', route => route.fulfill({ status: 404 }));
  await page.goto(`${station}/model`);
  const temperature = page.getByRole('button', { name: 'Select temp sensor', exact: true });
  await temperature.focus();
  await temperature.press('Enter');
  await expect(page).toHaveURL(/sensor=temp/);
  await expect(page.locator('.model-aside .reading')).toContainText('—');
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
  const serious = results.violations.filter(violation => ['serious', 'critical'].includes(violation.impact ?? ''));
  expect(serious.flatMap(violation => violation.nodes.map(node => `${violation.id}: ${node.target.join(' ')}`))).toEqual([]);
});

test('staff can run a replay, see the resulting alert, and stop the replay', async ({ page }) => {
  test.setTimeout(45_000);
  await page.goto('/login?returnTo=%2Fsimulation');
  await page.getByLabel('Username').fill(process.env.HWW_E2E_USERNAME!);
  await page.getByLabel('Password').fill(process.env.HWW_E2E_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page).toHaveURL(/\/simulation$/);
  await page.getByLabel('Playback speed').selectOption('5');
  const start = page.getByRole('button', { name: 'Start replay' });
  await start.click();
  await expect(page.locator('.payload')).toContainText('hww.frames.v1');
  await expect(page.getByRole('link', { name: 'Review alert' })).toBeVisible({ timeout: 25_000 });
  await page.getByRole('button', { name: 'Stop replay' }).click();
  await expect(start).toBeEnabled();
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible();
});
