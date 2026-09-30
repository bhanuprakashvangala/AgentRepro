import 'dotenv/config';
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import bodyParser from 'body-parser';
import { generatePdfBuffer, renderTemplate } from './utils/pdf.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5000;

app.use(bodyParser.json({ limit: '5mb' }));

app.post('/generate', async (req, res) => {
  try {
    const { templateName, data = {}, page = {}, headerTemplate, footerTemplate } = req.body;
    if (!templateName) {
      return res.status(400).json({ message: 'templateName is required' });
    }

    const html = await renderTemplate(templateName, data);
    const pdfBuffer = await generatePdfBuffer(html, {
      format: page.format,
      width: page.width,
      height: page.height,
      margin: page.margin,
      headerTemplate,
      footerTemplate
    });

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="${templateName}.pdf"`);
    return res.send(pdfBuffer);
  } catch (error) {
    console.error('PDF generation failed:', error);
    return res.status(500).json({ message: 'Failed to generate PDF', error: error.message });
  }
});

app.get('/', (req, res) => {
  res.json({ status: 'PDF generation service ready', endpoint: '/generate' });
});

app.listen(PORT, () => {
  console.log(`PDF service running on http://localhost:${PORT}`);
});
