import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { consultarPlaca } from './scraper.js';

const server = new McpServer({ name: 'placafipe-mcp', version: '1.0.0' });

server.tool(
  'consultar_placa',
  'Consulta dados completos de veiculo pela placa brasileira. Retorna marca, modelo, ano, cor, chassi, UF, municipio e valor da Tabela FIPE.',
  { placa: z.string().describe('Placa sem traco: ABC1234 (antiga) ou ABC1D23 (Mercosul)') },
  async ({ placa }) => {
    try {
      const { veiculo: d, ipva, estados } = await consultarPlaca(placa);
      const sep = '-'.repeat(40);
      const txt = [
        `CONSULTA VEICULAR --- ${d.placa}`,
        sep,
        `Marca:        ${d.marca}`,
        `Modelo:       ${d.modelo}`,
        `Generico:     ${d.generico}`,
        `Ano:          ${d.ano}${d.anoModelo ? ' / Modelo ' + d.anoModelo : ''}`,
        `Cor:          ${d.cor}`,
        `Combustivel:  ${d.combustivel}`,
        `Potencia:     ${d.potencia}`,
        `Chassi:       ${d.chassi}`,
        `UF:           ${d.uf}`,
        `Municipio:    ${d.municipio}`,
        `Importado:    ${d.importado}`,
        sep,
        'TABELA FIPE',
        `Codigo:       ${d.codigoFipe}`,
        `Modelo FIPE:  ${d.modeloFipe}`,
        `Valor:        ${d.valorFipe}`,
        sep,
        'IPVA',
        `Valor Venal:  ${ipva.valorVenal}`,
        `Aliquota:     ${ipva.aliquota}`,
        `Valor IPVA:   ${ipva.valorIpva}`,
        `Estados:      ${estados.length} estados disponíveis`,
        sep,
        `Fonte: ${d.fonte}`,
      ].join('\n');

      return { content: [{ type: 'text', text: txt }] };
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      return { content: [{ type: 'text', text: `Erro: ${msg}` }], isError: true };
    }
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
