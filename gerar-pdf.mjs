import puppeteer from 'puppeteer';
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const htmlPath = resolve(__dirname, 'manual-marca.html');
const pdfPath  = resolve(__dirname, 'Manual-Marca-AzevedoMotors.pdf');

const html = readFileSync(htmlPath, 'utf8');

// Inline the Google Fonts request with a local fallback so PDF renders correctly
const htmlPdf = html
  .replace(
    /<link href="https:\/\/fonts.googleapis.com[^"]*" rel="stylesheet">/,
    `<style>
      @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap');
    </style>`
  );

const browser = await puppeteer.launch({
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security'],
  headless: true,
});

const page = await browser.newPage();

// Set content and wait for fonts + images to load
await page.setContent(htmlPdf, { waitUntil: 'networkidle0', timeout: 60000 });

// Hide nav for PDF
await page.addStyleTag({ content: `
  nav { display: none !important; }
  main { margin-left: 0 !important; }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .capa { height: auto !important; min-height: 0 !important; padding: 100px 0; }
` });

await new Promise(r => setTimeout(r, 3000)); // let fonts render

await page.pdf({
  path: pdfPath,
  format: 'A4',
  printBackground: true,
  margin: { top: '0', right: '0', bottom: '0', left: '0' },
  displayHeaderFooter: false,
});

await browser.close();
console.log('PDF gerado:', pdfPath);
