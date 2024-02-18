import { test, expect } from '@playwright/test';

test('black', async ({page}) => {
  await page.goto('https://www.zara.com/nl/en/sparkly-faux-fur-sweater-p01473723.html?v1=317760429');
  await page.getByRole('button', { name: 'Accept All Cookies' }).click();
  const state = await page.locator('#product-size-selector-317760429-item-3').getAttribute('data-qa-action');
  if (state === 'size-out-of-stock') {
    console.log('OUT OF STOCK');
  } else {
    console.log('IN STOCK');
  }
});