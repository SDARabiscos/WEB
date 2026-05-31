import * as cheerio from 'cheerio';
import type { DadosVeiculo } from './types.js';

const BASE_URL = 'https://placafipe.com/placa';
const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
  'Accept-Encoding': 'gzip, deflate, br',
  'Cache-Control': 'no-cache',
};

export async function consultarPlaca(placa: string): Promise<DadosVeiculo> {
  const p = placa.toUpperCase().replace(/[^A-Z0-9]/g, '');

  const RE_ANTIGA = /^[A-Z]{3}[0-9]{4}$/;
  const RE_MERCOSUL = /^[A-Z]{3}[0-9][A-Z][0-9]{2}$/;

  if (!RE_ANTIGA.test(p) && !RE_MERCOSUL.test(p)) {
    throw new Error(`Placa invalida: ${placa}. Use ABC1234 ou ABC1D23`);
  }

  const url = `${BASE_URL}/${p}`;
  const res = await fetch(url, { headers: HEADERS });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ao consultar ${url}`);
  }

  const html = await res.text();
  const $ = cheerio.load(html);

  // Extrai texto limpo da pagina
  const txt = $('body').text().replace(/\s+/g, ' ');

  const get = (label: string): string => {
    const rx = new RegExp(`${label}[:\\s]+([^\\n\\t|]+)`, 'i');
    return txt.match(rx)?.[1]?.trim() ?? 'N/D';
  };

  // Tenta capturar o valor FIPE de células de tabela
  const valorFipe =
    $('td, th, span, p, div')
      .filter((_, el) => $(el).text().trim().startsWith('R$'))
      .first()
      .text()
      .trim() || get('Valor');

  return {
    placa: p,
    marca: get('Marca'),
    modelo: get('Modelo'),
    generico: get('Generico'),
    ano: get('Ano'),
    cor: get('Cor'),
    combustivel: get('Combustivel|Combustível'),
    potencia: get('Potencia|Potência'),
    chassi: get('Chassi'),
    uf: get('UF'),
    municipio: get('Municipio|Município'),
    importado: get('Importado'),
    codigoFipe: get('Codigo FIPE|Código FIPE|FIPE:'),
    modeloFipe: get('Modelo FIPE|Modelo:'),
    valorFipe,
    fonte: url,
  };
}
