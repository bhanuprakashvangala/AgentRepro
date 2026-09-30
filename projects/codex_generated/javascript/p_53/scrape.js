import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function scrapeListings(targetUrl, maxPages = 3) {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();

  const results = [];

  try {
    for (let pageNumber = 1; pageNumber <= maxPages; pageNumber += 1) {
      const url = `${targetUrl}?page=${pageNumber}`;
      console.log(`Navigating to ${url}`);
      await page.goto(url, { waitUntil: 'networkidle0' });

      await page.waitForSelector('.listing-card, .result-item', { timeout: 5000 }).catch(() => {
        console.warn('No listing elements found on this page.');
      });

      const items = await page.evaluate(() => {
        const nodes = document.querySelectorAll('.listing-card, .result-item');
        return Array.from(nodes).map((node) => ({
          title: node.querySelector('.title, .item-title')?.textContent?.trim() || 'Untitled',
          price: node.querySelector('.price, .item-price')?.textContent?.trim() || 'N/A',
          link: node.querySelector('a')?.href || null,
          description: node.querySelector('.description, .item-description')?.textContent?.trim() || ''
        }));
      });

      if (!items.length) {
        console.log('No items extracted; stopping early.');
        break;
      }

      results.push(...items);

      const nextButtonDisabled = await page.$('[aria-label="Next"][disabled], .pagination-next.disabled');
      if (nextButtonDisabled) {
        console.log('Reached last page.');
        break;
      }
    }
  } finally {
    await browser.close();
  }

  return results;
}

async function main() {
  const targetUrl = process.env.TARGET_URL || 'https://example.com/listings';
  const maxPages = Number(process.env.MAX_PAGES || 3);

  const data = await scrapeListings(targetUrl, maxPages);
  const outputPath = path.join(__dirname, 'results.json');
  await fs.writeFile(outputPath, JSON.stringify({ scrapedAt: new Date().toISOString(), data }, null, 2));
  console.log(`Saved ${data.length} records to ${outputPath}`);
}

main().catch((error) => {
  console.error('Scraping failed:', error);
  process.exit(1);
});
