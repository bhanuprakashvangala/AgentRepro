import { chromium } from 'playwright';
import fs from 'fs/promises';
import path from 'path';

/**
 * Web Scraper Configuration
 */
const CONFIG = {
  // Target website to scrape (example: quotes website)
  baseUrl: 'https://quotes.toscrape.com',

  // Number of pages to scrape
  maxPages: 3,

  // Output file path
  outputFile: 'scraped_data.json',

  // Delay between page loads (milliseconds)
  pageDelay: 1000,

  // Browser options
  headless: true,

  // Timeout for page loads (milliseconds)
  timeout: 30000
};

/**
 * Main scraper class
 */
class WebScraper {
  constructor(config) {
    this.config = config;
    this.browser = null;
    this.page = null;
    this.data = [];
  }

  /**
   * Initialize browser and page
   */
  async initialize() {
    console.log('🚀 Launching browser...');
    this.browser = await chromium.launch({
      headless: this.config.headless
    });

    this.page = await this.browser.newPage();
    this.page.setDefaultTimeout(this.config.timeout);

    console.log('✅ Browser initialized');
  }

  /**
   * Extract data from current page
   * Customize this method based on your target website structure
   */
  async extractPageData() {
    console.log(`📄 Extracting data from: ${this.page.url()}`);

    // Wait for dynamic content to load
    await this.page.waitForSelector('.quote', { timeout: 10000 }).catch(() => {
      console.log('⚠️  No quotes found on page');
    });

    // Extract data using page.evaluate to run code in browser context
    const pageData = await this.page.evaluate(() => {
      const quotes = [];
      const quoteElements = document.querySelectorAll('.quote');

      quoteElements.forEach((element) => {
        const text = element.querySelector('.text')?.textContent?.trim() || '';
        const author = element.querySelector('.author')?.textContent?.trim() || '';
        const tags = Array.from(element.querySelectorAll('.tag'))
          .map(tag => tag.textContent.trim());

        quotes.push({
          text,
          author,
          tags,
          scrapedAt: new Date().toISOString()
        });
      });

      return quotes;
    });

    console.log(`✅ Extracted ${pageData.length} items from current page`);
    return pageData;
  }

  /**
   * Navigate to next page if available
   * Returns true if next page exists, false otherwise
   */
  async goToNextPage() {
    const hasNextPage = await this.page.evaluate(() => {
      const nextButton = document.querySelector('.next > a');
      return nextButton !== null;
    });

    if (!hasNextPage) {
      console.log('📍 No more pages to scrape');
      return false;
    }

    console.log('➡️  Navigating to next page...');

    await Promise.all([
      this.page.waitForNavigation({ waitUntil: 'networkidle' }),
      this.page.click('.next > a')
    ]);

    // Add delay between pages to be respectful
    await this.page.waitForTimeout(this.config.pageDelay);

    return true;
  }

  /**
   * Main scraping logic
   */
  async scrape() {
    try {
      await this.initialize();

      console.log(`🎯 Starting scrape of: ${this.config.baseUrl}`);
      await this.page.goto(this.config.baseUrl, {
        waitUntil: 'networkidle'
      });

      let currentPage = 1;

      // Scrape multiple pages
      while (currentPage <= this.config.maxPages) {
        console.log(`\n📖 Scraping page ${currentPage}/${this.config.maxPages}`);

        const pageData = await this.extractPageData();
        this.data.push(...pageData);

        if (currentPage < this.config.maxPages) {
          const hasNext = await this.goToNextPage();
          if (!hasNext) {
            console.log('⚠️  Reached last page before max pages');
            break;
          }
        }

        currentPage++;
      }

      console.log(`\n✅ Scraping complete! Total items: ${this.data.length}`);

    } catch (error) {
      console.error('❌ Error during scraping:', error.message);
      throw error;
    }
  }

  /**
   * Save scraped data to JSON file
   */
  async saveData() {
    const outputPath = path.resolve(this.config.outputFile);

    const output = {
      metadata: {
        scrapedAt: new Date().toISOString(),
        totalItems: this.data.length,
        source: this.config.baseUrl,
        pagesScraped: Math.min(this.config.maxPages, this.data.length)
      },
      data: this.data
    };

    await fs.writeFile(
      outputPath,
      JSON.stringify(output, null, 2),
      'utf-8'
    );

    console.log(`💾 Data saved to: ${outputPath}`);
  }

  /**
   * Clean up resources
   */
  async close() {
    if (this.browser) {
      await this.browser.close();
      console.log('🔒 Browser closed');
    }
  }

  /**
   * Run the complete scraping process
   */
  async run() {
    try {
      await this.scrape();
      await this.saveData();
    } catch (error) {
      console.error('❌ Scraper failed:', error);
      process.exit(1);
    } finally {
      await this.close();
    }
  }
}

/**
 * Execute scraper
 */
(async () => {
  const scraper = new WebScraper(CONFIG);
  await scraper.run();
})();
