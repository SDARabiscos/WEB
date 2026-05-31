import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { consultarPlaca } from './scraper.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(join(__dirname, 'public')));

// CORS para o dashboard local
app.use((_, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  next();
});

app.get('/placa/:placa', async (req, res) => {
  try {
    const { veiculo, ipva, estados } = await consultarPlaca(req.params.placa);
    res.json({ success: true, data: veiculo, ipva, estados });
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    res.status(400).json({ success: false, error: msg });
  }
});

app.get('/health', (_, res) => res.json({ status: 'ok', version: '1.0.0' }));

app.listen(PORT, () => {
  console.log(`PlacaFIPE API rodando em http://localhost:${PORT}`);
});
