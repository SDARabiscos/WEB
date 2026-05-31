import express from 'express';
import { consultarPlaca } from './scraper.js';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get('/placa/:placa', async (req, res) => {
  try {
    const dados = await consultarPlaca(req.params.placa);
    res.json({ success: true, data: dados });
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    res.status(400).json({ success: false, error: msg });
  }
});

app.get('/health', (_, res) => res.json({ status: 'ok', version: '1.0.0' }));

app.listen(PORT, () => {
  console.log(`PlacaFIPE API rodando na porta ${PORT}`);
});
