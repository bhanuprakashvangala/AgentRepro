import fs from 'fs/promises';
import fsSync from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import pug from 'pug';
import puppeteer from 'puppeteer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const templatesDir = path.join(__dirname, '..', 'templates');

export async function renderTemplate(templateName, data = {}) {
  const possibleExtensions = ['.pug', '.html'];
  for (const ext of possibleExtensions) {
    const templatePath = path.join(templatesDir, `${templateName}${ext}`);
    if (fsSync.existsSync(templatePath)) {
      if (ext === '.pug') {
        return pug.renderFile(templatePath, data);
      }
      return fs.readFile(templatePath, 'utf-8');
    }
  }
  throw new Error(`Template ${templateName} not found`);
}

export async function generatePdfBuffer(html, options = {}) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle0' });

    const pdfOptions = {
      printBackground: true
    };
    if (options.format) pdfOptions.format = options.format;
    if (options.width) pdfOptions.width = options.width;
    if (options.height) pdfOptions.height = options.height;
    if (options.margin) pdfOptions.margin = options.margin;

    if (options.headerTemplate || options.footerTemplate) {
      pdfOptions.displayHeaderFooter = true;
      pdfOptions.headerTemplate = options.headerTemplate || '<span></span>';
      pdfOptions.footerTemplate = options.footerTemplate || '<span></span>';
    }

    const buffer = await page.pdf(pdfOptions);
    return buffer;
  } finally {
    await browser.close();
  }
}
