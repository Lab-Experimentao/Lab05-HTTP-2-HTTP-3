// Abre o Chrome forçando o protocolo: 'h2' ou 'h3'.
import { chromium } from 'playwright';

export const HOST = 'caddy.test';

const FLAGS = {
  h2: ['--disable-quic'],
  h3: ['--enable-quic', `--origin-to-force-quic-on=${HOST}:443`],
};

export function abrirChrome(protocolo) {
  if (!FLAGS[protocolo]) throw new Error(`Protocolo inválido: ${protocolo}`);
  return chromium.launch({ channel: 'chrome', args: FLAGS[protocolo] });
}
