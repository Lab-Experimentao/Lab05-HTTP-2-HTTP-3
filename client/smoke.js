// Confere se o Chrome usa o protocolo pedido (h2 e h3) em todas as respostas.
import { abrirChrome, HOST } from './browser.js';

for (const pedido of ['h2', 'h3']) {
  const browser = await abrirChrome(pedido);
  try {
    const page = await browser.newPage();

    // Mesmo valor da coluna "Protocol" do DevTools.
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('Network.enable');
    const devtools = [];
    cdp.on('Network.responseReceived', (e) => devtools.push(e.response.protocol));

    const response = await page.goto(`https://${HOST}/`);
    const usado = await page.evaluate(
      () => performance.getEntriesByType('navigation')[0].nextHopProtocol,
    );

    console.log(`pedido=${pedido} nextHopProtocol=${usado} devtools=${[...new Set(devtools)]} HTTP ${response.status()} Chrome ${browser.version()}`);
    if (!response.ok() || usado !== pedido || !devtools.length || devtools.some((p) => p !== pedido)) {
      process.exitCode = 1;
    }
  } finally {
    await browser.close();
  }
}
