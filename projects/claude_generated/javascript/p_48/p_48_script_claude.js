import puppeteer from 'puppeteer';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * PDF Generation Service
 * Converts HTML content to PDF with customizable options
 */
class PDFGenerationService {
  constructor() {
    this.browser = null;
  }

  /**
   * Initialize the browser instance
   */
  async initialize() {
    if (!this.browser) {
      this.browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      });
    }
    return this.browser;
  }

  /**
   * Close the browser instance
   */
  async close() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }

  /**
   * Generate PDF from HTML content
   * @param {Object} options - PDF generation options
   * @param {string} options.html - HTML content as string
   * @param {string} options.templatePath - Path to HTML template file (alternative to html)
   * @param {string} options.outputPath - Output PDF file path
   * @param {Object} options.pageSize - Page size configuration
   * @param {string} options.pageSize.format - Page format (A4, Letter, Legal, etc.)
   * @param {string} options.pageSize.width - Custom width (e.g., '210mm')
   * @param {string} options.pageSize.height - Custom height (e.g., '297mm')
   * @param {Object} options.margins - Page margins
   * @param {string} options.margins.top - Top margin (e.g., '20mm')
   * @param {string} options.margins.right - Right margin
   * @param {string} options.margins.bottom - Bottom margin
   * @param {string} options.margins.left - Left margin
   * @param {Object} options.header - Header configuration
   * @param {string} options.header.template - HTML template for header
   * @param {string} options.header.height - Header height (e.g., '10mm')
   * @param {Object} options.footer - Footer configuration
   * @param {string} options.footer.template - HTML template for footer
   * @param {string} options.footer.height - Footer height (e.g., '10mm')
   * @param {boolean} options.landscape - Landscape orientation (default: false)
   * @param {boolean} options.printBackground - Print background graphics (default: true)
   * @param {string} options.scale - Scale of the webpage rendering (default: 1)
   * @param {boolean} options.displayHeaderFooter - Display header and footer (default: false)
   * @returns {Promise<Buffer>} PDF buffer
   */
  async generatePDF(options = {}) {
    await this.initialize();

    // Get HTML content
    let htmlContent = options.html;
    if (options.templatePath) {
      htmlContent = readFileSync(resolve(__dirname, options.templatePath), 'utf-8');
    }

    if (!htmlContent) {
      throw new Error('Either html or templatePath must be provided');
    }

    // Create a new page
    const page = await this.browser.newPage();

    try {
      // Set content
      await page.setContent(htmlContent, {
        waitUntil: 'networkidle0'
      });

      // Build PDF options
      const pdfOptions = {
        path: options.outputPath,
        printBackground: options.printBackground !== false,
        landscape: options.landscape || false,
        displayHeaderFooter: options.displayHeaderFooter || false
      };

      // Page size configuration
      if (options.pageSize) {
        if (options.pageSize.format) {
          pdfOptions.format = options.pageSize.format;
        } else if (options.pageSize.width && options.pageSize.height) {
          pdfOptions.width = options.pageSize.width;
          pdfOptions.height = options.pageSize.height;
        }
      } else {
        pdfOptions.format = 'A4'; // Default
      }

      // Margins configuration
      if (options.margins) {
        pdfOptions.margin = {
          top: options.margins.top || '0mm',
          right: options.margins.right || '0mm',
          bottom: options.margins.bottom || '0mm',
          left: options.margins.left || '0mm'
        };
      }

      // Header configuration
      if (options.header) {
        pdfOptions.displayHeaderFooter = true;
        pdfOptions.headerTemplate = options.header.template || '';
        if (options.header.height) {
          if (!pdfOptions.margin) pdfOptions.margin = {};
          pdfOptions.margin.top = options.header.height;
        }
      }

      // Footer configuration
      if (options.footer) {
        pdfOptions.displayHeaderFooter = true;
        pdfOptions.footerTemplate = options.footer.template || '';
        if (options.footer.height) {
          if (!pdfOptions.margin) pdfOptions.margin = {};
          pdfOptions.margin.bottom = options.footer.height;
        }
      }

      // Scale
      if (options.scale) {
        pdfOptions.scale = parseFloat(options.scale);
      }

      // Generate PDF
      const pdfBuffer = await page.pdf(pdfOptions);

      return pdfBuffer;
    } finally {
      await page.close();
    }
  }

  /**
   * Generate PDF from URL
   * @param {string} url - URL to convert to PDF
   * @param {Object} options - Same options as generatePDF (except html and templatePath)
   * @returns {Promise<Buffer>} PDF buffer
   */
  async generatePDFFromURL(url, options = {}) {
    await this.initialize();

    const page = await this.browser.newPage();

    try {
      await page.goto(url, {
        waitUntil: 'networkidle0'
      });

      // Build PDF options (similar to generatePDF)
      const pdfOptions = {
        path: options.outputPath,
        printBackground: options.printBackground !== false,
        landscape: options.landscape || false,
        displayHeaderFooter: options.displayHeaderFooter || false
      };

      if (options.pageSize) {
        if (options.pageSize.format) {
          pdfOptions.format = options.pageSize.format;
        } else if (options.pageSize.width && options.pageSize.height) {
          pdfOptions.width = options.pageSize.width;
          pdfOptions.height = options.pageSize.height;
        }
      } else {
        pdfOptions.format = 'A4';
      }

      if (options.margins) {
        pdfOptions.margin = {
          top: options.margins.top || '0mm',
          right: options.margins.right || '0mm',
          bottom: options.margins.bottom || '0mm',
          left: options.margins.left || '0mm'
        };
      }

      if (options.header) {
        pdfOptions.displayHeaderFooter = true;
        pdfOptions.headerTemplate = options.header.template || '';
      }

      if (options.footer) {
        pdfOptions.displayHeaderFooter = true;
        pdfOptions.footerTemplate = options.footer.template || '';
      }

      if (options.scale) {
        pdfOptions.scale = parseFloat(options.scale);
      }

      const pdfBuffer = await page.pdf(pdfOptions);

      return pdfBuffer;
    } finally {
      await page.close();
    }
  }
}

export default PDFGenerationService;
