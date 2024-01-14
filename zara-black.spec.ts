import { test, expect } from '@playwright/test';
import { chromium } from 'playwright';

test('black', async ({page}) => {
  await page.goto('https://www.zara.com/nl/en/cashmere-scarf-p03887202.html?v1=310627495');
  await page.getByRole('button', { name: 'Accept All Cookies' }).click();
  await expect(page.getByRole('article')).toContainText('OUT OF STOCK', {timeout: 500});
});