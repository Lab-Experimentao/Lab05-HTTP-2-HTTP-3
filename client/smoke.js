// Verifica se o Chrome do container consegue abrir a página do Caddy.
import { chromium } from 'playwright';

const browser = await chromium.launch({ channel: 'chrome' });
try {
  const page = await browser.newPage({ ignoreHTTPSErrors: true });
  const response = await page.goto('https://caddy.test/');
  if (!response.ok()) throw new Error(`HTTP ${response.status()}`);
  console.log(`OK: Chrome ${browser.version()}, HTTP ${response.status()}, título "${await page.title()}"`);
} finally {
  await browser.close();
}
