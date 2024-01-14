import { test, expect } from '@playwright/test';
import { chromium } from 'playwright';

test('test', async ({page}) => {
  await page.goto('https://www.zara.com/nl/en/steven-meisel-cashmere-scarf-p03039304.html?v1=274475161');
  await page.getByRole('button', { name: 'Accept All Cookies' }).click();
  await expect(page.getByRole('article')).toContainText('OUT OF STOCK', {timeout: 500});
});