// Mede as cargas da página num nível de perda e acrescenta as linhas ao CSV (issue #8).
// A perda já deve estar aplicada (make rede PERDA=...); o make coleta faz isso.
//
// Uso: node medir.js --perda 2 --reps 90 [--saida /dados/coleta.csv] [--semente 42] [--timeout 60000]
import { appendFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { parseArgs } from 'node:util';
import { abrirChrome, HOST } from './browser.js';

const { values: op } = parseArgs({
  options: {
    perda: { type: 'string' },
    reps: { type: 'string', default: '90' },
    saida: { type: 'string', default: '/dados/coleta.csv' },
    semente: { type: 'string', default: '42' },
    timeout: { type: 'string', default: '60000' },
  },
});

const PERDA = Number(op.perda);
const REPS = Number(op.reps);
const TIMEOUT = Number(op.timeout);
const MAX_FALLBACKS = 3; // refeitas seguidas da mesma carga antes de desistir
if (![0, 1, 2, 3, 5].includes(PERDA) || op.perda === undefined) {
  throw new Error(`--perda inválida: '${op.perda}' (use 0, 1, 2, 3 ou 5)`);
}
if (!Number.isInteger(REPS) || REPS < 1) throw new Error(`--reps inválido: '${op.reps}'`);

const COLUNAS = [
  'protocolo_pedido', 'protocolo_usado', 'perda_pct', 'repeticao', 'tempo_carga_ms',
  'ttfb_ms', 'falhou', 'fallback', 'recursos', 'ordem', 'inicio', 'erro',
];

// PRNG com semente (mulberry32): mesma semente e mesma perda, mesma ordem.
function gerador(semente) {
  let a = semente >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 2 ** 32;
  };
}

// REPS cargas de cada protocolo, em ordem aleatória.
function plano(rng) {
  const cargas = [];
  for (const p of ['h2', 'h3']) for (let r = 1; r <= REPS; r++) cargas.push([p, r]);
  for (let i = cargas.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [cargas[i], cargas[j]] = [cargas[j], cargas[i]];
  }
  return cargas;
}

// Uma carga num Chrome novo: sem cache, conexões, sessão TLS nem Alt-Svc da carga anterior.
async function carregar(protocolo) {
  const linha = { protocolo_usado: '', tempo_carga_ms: '', ttfb_ms: '', falhou: 0, recursos: '', erro: '' };
  const browser = await abrirChrome(protocolo);
  try {
    const page = await browser.newPage();
    await page.goto(`https://${HOST}/`, { waitUntil: 'load', timeout: TIMEOUT });
    // loadEventEnd só é preenchido depois que os handlers de load terminam.
    await page.waitForFunction(
      () => performance.getEntriesByType('navigation')[0]?.loadEventEnd > 0,
      null,
      { timeout: TIMEOUT },
    );
    const m = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      const res = performance.getEntriesByType('resource');
      return {
        usado: nav.nextHopProtocol,
        outros: [...new Set(res.map((e) => e.nextHopProtocol))].filter((p) => p !== nav.nextHopProtocol),
        carga: nav.loadEventEnd - nav.startTime,
        ttfb: nav.responseStart - nav.startTime,
        recursos: res.length,
      };
    });
    // Se algum recurso veio por outro protocolo, a carga não é "pura": conta como fallback.
    linha.protocolo_usado = m.outros.length ? [m.usado, ...m.outros].join('+') : m.usado;
    linha.tempo_carga_ms = m.carga.toFixed(1);
    linha.ttfb_ms = m.ttfb.toFixed(1);
    linha.recursos = m.recursos;
  } catch (e) {
    linha.falhou = 1;
    linha.erro = e.message.split('\n')[0].replaceAll('"', "'");
  } finally {
    await browser.close().catch(() => {});
  }
  return linha;
}

function csv(linha) {
  return COLUNAS.map((c) => {
    const v = String(linha[c] ?? '');
    return /[",\n]/.test(v) ? `"${v}"` : v;
  }).join(',') + '\n';
}

mkdirSync(dirname(op.saida), { recursive: true });
if (!existsSync(op.saida)) appendFileSync(op.saida, COLUNAS.join(',') + '\n');

const cargas = plano(gerador(Number(op.semente) * 100 + PERDA));
let ordem = 0;
let fallbacks = 0;
for (const [i, [protocolo, repeticao]] of cargas.entries()) {
  for (let tentativa = 0; ; tentativa++) {
    const inicio = new Date().toISOString();
    const linha = await carregar(protocolo);
    // Regra 2 do plano de análise: fallback é registrado, contado e refeito.
    const fallback = !linha.falhou && linha.protocolo_usado !== protocolo;
    Object.assign(linha, {
      protocolo_pedido: protocolo, perda_pct: PERDA, repeticao,
      fallback: fallback ? 1 : 0, ordem: ++ordem, inicio,
    });
    appendFileSync(op.saida, csv(linha));
    const status = linha.falhou ? `FALHOU (${linha.erro})` : `${linha.tempo_carga_ms} ms${fallback ? ' FALLBACK' : ''}`;
    console.log(`[perda ${PERDA}%] ${i + 1}/${cargas.length} ${protocolo} rep ${repeticao}: ${status}`);
    if (!fallback) break;
    fallbacks++;
    if (tentativa + 1 >= MAX_FALLBACKS) {
      console.error(`Aviso: ${protocolo} rep ${repeticao} teve fallback ${MAX_FALLBACKS} vezes seguidas; seguindo.`);
      break;
    }
  }
}
console.log(`[perda ${PERDA}%] fim: ${cargas.length} cargas, ${fallbacks} fallbacks refeitos -> ${op.saida}`);
