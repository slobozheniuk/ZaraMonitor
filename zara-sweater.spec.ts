import { test, expect } from '@playwright/test';
import { chromium } from 'playwright';

test('sweater', async ({page}) => {
  await page.goto('https://www.zara.com/nl/en/100-cashmere-wraparound-sweater-p03039104.html?v1=310223065');
  await page.getByRole('button', { name: 'Accept All Cookies' }).click();
  await expect(page.getByRole('article')).toContainText('OUT OF STOCK', {timeout: 500});
});