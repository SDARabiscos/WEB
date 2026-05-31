import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { consultarPlaca } from './scraper.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(join(__dirname, 'public')));

app.get('/placa/:placa', async (req, res) => {
  try {
    const dados = await consultarPlaca(req.params.placa);
    res.json({ success: true, data: dados });
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    res.status(400).json({ success: false, error: msg });
  }
});

app.get('/demo/:placa', (req, res) => {
  const placa = req.params.placa.toUpperCase().replace(/[^A-Z0-9]/g, '');
  res.json({
    success: true,
    data: {
      placa,
      marca: 'VOLKSWAGEN',
      modelo: 'GOL 1.6 MI TOTAL FLEX 8V 4P',
      generico: 'Gol',
      ano: '2019',
      cor: 'Branca',
      combustivel: 'Flex',
      potencia: '101 cv',
      chassi: '*****G123456',
      uf: 'SP',
      municipio: 'SAO PAULO',
      importado: 'Não',
      codigoFipe: '005340-6',
      modeloFipe: 'Gol 1.6 Total Flex 4p',
      valorFipe: 'R$ 52.841,00',
      fonte: `https://placafipe.com/placa/${placa}`,
    },
  });
});

app.get('/health', (_, res) => res.json({ status: 'ok', version: '1.0.0' }));

app.listen(PORT, () => {
  console.log(`PlacaFIPE UI rodando em http://localhost:${PORT}`);
});
