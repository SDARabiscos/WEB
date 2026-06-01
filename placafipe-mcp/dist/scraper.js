import { execSync } from 'child_process';
import * as cheerio from 'cheerio';
const BASE_URL = 'https://placafipe.com/placa';
function fetchHtml(url) {
    return execSync(`curl -s -L --max-time 15 \
      -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" \
      -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
      -H "Accept-Language: pt-BR,pt;q=0.9" \
      "${url}"`, { maxBuffer: 5 * 1024 * 1024 }).toString();
}
export async function consultarPlaca(placa) {
    const p = placa.toUpperCase().replace(/[^A-Z0-9]/g, '');
    const RE_ANTIGA = /^[A-Z]{3}[0-9]{4}$/;
    const RE_MERCOSUL = /^[A-Z]{3}[0-9][A-Z][0-9]{2}$/;
    if (!RE_ANTIGA.test(p) && !RE_MERCOSUL.test(p)) {
        throw new Error(`Placa inválida: ${placa}. Use ABC1234 ou ABC1D23`);
    }
    const url = `${BASE_URL}/${p}`;
    const html = fetchHtml(url);
    const $ = cheerio.load(html);
    // --- Dados do veículo via tabela estruturada ---
    const campo = {};
    $('table.fipeTablePriceDetail tr').each((_, row) => {
        const label = $(row).find('td:first-child b').text().replace(':', '').trim();
        const value = $(row).find('td:last-child').text().trim();
        if (label)
            campo[label] = value;
    });
    // Tabela 2: Código FIPE | Modelo | Valor
    const fipeTable = $('table').eq(2);
    const fipeRow = fipeTable.find('tr').eq(1).find('td');
    const codigoFipe = fipeRow.eq(0).text().trim() || 'N/D';
    const modeloFipe = fipeRow.eq(1).text().trim() || 'N/D';
    const valorFipe = fipeRow.eq(2).text().trim() || 'N/D';
    // Placa antiga
    const bodyTxt = $('body').text();
    const placaAntiga = bodyTxt.match(/sistema antigo era ([A-Z]{3}-\d{4})/i)?.[1] ?? '';
    const veiculo = {
        placa: p,
        marca: campo['Marca'] ?? 'N/D',
        modelo: campo['Modelo'] ?? 'N/D',
        generico: campo['Genérico'] ?? campo['Generico'] ?? 'N/D',
        ano: campo['Ano'] ?? 'N/D',
        anoModelo: campo['Ano Modelo'] ?? '',
        cor: campo['Cor'] ?? 'N/D',
        combustivel: campo['Combustível'] ?? campo['Combustivel'] ?? 'N/D',
        potencia: campo['Potência'] ?? campo['Potencia'] ?? 'N/D',
        chassi: campo['Chassi'] ?? 'N/D',
        uf: campo['UF'] ?? 'N/D',
        municipio: campo['Município'] ?? campo['Municipio'] ?? 'N/D',
        importado: campo['Importado'] ?? 'N/D',
        codigoFipe,
        modeloFipe,
        valorFipe,
        placaAntiga,
        fonte: url,
    };
    // --- IPVA ---
    const ipvaTxt = bodyTxt.replace(/\s+/g, ' ');
    const valorVenal = ipvaTxt.match(/Valor Venal:\s*(R\$\s*[\d\.,]+)/i)?.[1] ?? 'N/D';
    const aliquota = ipvaTxt.match(/Aliquota:\s*([\d\.,]+\s*%)/i)?.[1] ?? '';
    const valorIpva = ipvaTxt.match(/Valor IPVA:\s*(R\$\s*[\d\.,]+)/i)?.[1] ?? 'N/D';
    // Tabela 5: Histórico IPVA (Ano | Valor Venal | Valor IPVA)
    const historico = [];
    $('table').eq(5).find('tr').slice(1).each((_, row) => {
        const cols = $(row).find('td').map((_, td) => $(td).text().trim()).get();
        if (cols.length >= 3 && /^\d{4}$/.test(cols[0])) {
            historico.push({ ano: cols[0], valorVenal: cols[1], valorIpva: cols[2] });
        }
    });
    const ipva = { valorVenal, aliquota, valorIpva, historico };
    // Tabela 4: IPVA por estado (Estado | Valor Venal | Taxa | Valor IPVA)
    const estados = [];
    $('table').eq(4).find('tr').slice(1).each((_, row) => {
        const cols = $(row).find('td').map((_, td) => $(td).text().trim()).get();
        if (cols.length >= 4 && /^[A-Z]{2}$/.test(cols[0])) {
            estados.push({ estado: cols[0], valorVenal: cols[1], taxa: cols[2], valorIpva: cols[3] });
        }
    });
    return { veiculo, ipva, estados };
}
