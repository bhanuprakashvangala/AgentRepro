import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { renderTemplate, generatePdfBuffer } from './utils/pdf.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {};
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.substring(2);
      const value = args[i + 1];
      options[key] = value;
      i += 1;
    }
  }
  return options;
}

async function main() {
  const opts = parseArgs();
  if (!opts.template || !opts.output) {
    console.error('Usage: node generate.js --template invoice --output invoice.pdf [--data data.json]');
    process.exit(1);
  }

  const data = opts.data
    ? JSON.parse(fs.readFileSync(path.isAbsolute(opts.data) ? opts.data : path.join(__dirname, opts.data), 'utf-8'))
    : {};

  const html = await renderTemplate(opts.template, data);
  const pdfBuffer = await generatePdfBuffer(html, {
    format: opts.format,
    width: opts.width,
    height: opts.height,
    margin: opts.margin ? JSON.parse(opts.margin) : undefined,
    headerTemplate: opts.headerTemplate ? fs.readFileSync(opts.headerTemplate, 'utf-8') : undefined,
    footerTemplate: opts.footerTemplate ? fs.readFileSync(opts.footerTemplate, 'utf-8') : undefined
  });

  const outputPath = path.isAbsolute(opts.output) ? opts.output : path.join(__dirname, opts.output);
  fs.writeFileSync(outputPath, pdfBuffer);
  console.log(`PDF saved to ${outputPath}`);
}

main().catch((error) => {
  console.error('Failed to generate PDF:', error);
  process.exit(1);
});
