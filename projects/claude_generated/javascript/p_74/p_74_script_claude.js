const PDFDocument = require('pdfkit');
const fs = require('fs');

class PDFReportGenerator {
  constructor() {
    this.doc = null;
  }

  /**
   * Create a new PDF document
   */
  createDocument(options = {}) {
    this.doc = new PDFDocument({
      size: options.size || 'A4',
      margins: options.margins || { top: 50, bottom: 50, left: 50, right: 50 },
      info: {
        Title: options.title || 'Report',
        Author: options.author || 'PDF Generator',
        Subject: options.subject || 'Generated Report'
      }
    });

    return this.doc;
  }

  /**
   * Add header to document
   */
  addHeader(title, subtitle) {
    this.doc
      .fontSize(20)
      .text(title, { align: 'center' })
      .fontSize(12)
      .text(subtitle, { align: 'center' })
      .moveDown();

    return this;
  }

  /**
   * Add table to document
   */
  addTable(headers, rows, options = {}) {
    const startX = options.startX || 50;
    const startY = options.startY || this.doc.y;
    const colWidth = options.colWidth || 120;
    const rowHeight = options.rowHeight || 25;

    // Draw headers
    this.doc.font('Helvetica-Bold').fontSize(10);
    headers.forEach((header, i) => {
      this.doc.text(header, startX + (i * colWidth), startY, {
        width: colWidth,
        align: 'left'
      });
    });

    // Draw horizontal line
    this.doc
      .moveTo(startX, startY + 15)
      .lineTo(startX + (headers.length * colWidth), startY + 15)
      .stroke();

    // Draw rows
    this.doc.font('Helvetica').fontSize(9);
    rows.forEach((row, rowIndex) => {
      const y = startY + rowHeight + (rowIndex * rowHeight);

      row.forEach((cell, colIndex) => {
        this.doc.text(String(cell), startX + (colIndex * colWidth), y, {
          width: colWidth,
          align: 'left'
        });
      });
    });

    this.doc.moveDown(rows.length + 2);
    return this;
  }

  /**
   * Add simple bar chart
   */
  addBarChart(data, options = {}) {
    const startX = options.startX || 100;
    const startY = options.startY || this.doc.y;
    const maxBarWidth = options.maxBarWidth || 300;
    const barHeight = options.barHeight || 30;
    const spacing = options.spacing || 10;

    const maxValue = Math.max(...data.map(d => d.value));

    this.doc.fontSize(10).font('Helvetica-Bold');
    this.doc.text(options.title || 'Chart', startX, startY - 20);

    data.forEach((item, index) => {
      const y = startY + (index * (barHeight + spacing));
      const barWidth = (item.value / maxValue) * maxBarWidth;

      // Draw bar
      this.doc
        .rect(startX + 100, y, barWidth, barHeight)
        .fillAndStroke('#4CAF50', '#333');

      // Draw label
      this.doc
        .fillColor('#000')
        .fontSize(9)
        .text(item.label, startX, y + 10, { width: 90, align: 'right' });

      // Draw value
      this.doc
        .text(item.value, startX + 100 + barWidth + 5, y + 10);
    });

    this.doc.moveDown(data.length + 2);
    return this;
  }

  /**
   * Add page numbers
   */
  addPageNumbers() {
    const range = this.doc.bufferedPageRange();

    for (let i = 0; i < range.count; i++) {
      this.doc.switchToPage(i);

      this.doc
        .fontSize(9)
        .text(
          `Page ${i + 1} of ${range.count}`,
          0,
          this.doc.page.height - 50,
          { align: 'center' }
        );
    }

    return this;
  }

  /**
   * Generate invoice PDF
   */
  createInvoice(invoiceData, outputPath) {
    this.createDocument({ title: 'Invoice' });

    // Header
    this.addHeader('INVOICE', `Invoice #${invoiceData.number}`);

    // Invoice details
    this.doc
      .fontSize(10)
      .text(`Date: ${invoiceData.date}`, { align: 'right' })
      .text(`Due Date: ${invoiceData.dueDate}`, { align: 'right' })
      .moveDown();

    // Bill to
    this.doc
      .fontSize(12)
      .text('Bill To:', { underline: true })
      .fontSize(10)
      .text(invoiceData.customer.name)
      .text(invoiceData.customer.address)
      .moveDown();

    // Items table
    const headers = ['Item', 'Quantity', 'Price', 'Total'];
    const rows = invoiceData.items.map(item => [
      item.description,
      item.quantity,
      `$${item.price.toFixed(2)}`,
      `$${(item.quantity * item.price).toFixed(2)}`
    ]);

    this.addTable(headers, rows);

    // Total
    this.doc
      .fontSize(12)
      .text(`Total: $${invoiceData.total.toFixed(2)}`, { align: 'right' })
      .moveDown();

    this.addPageNumbers();

    // Save to file
    this.doc.pipe(fs.createWriteStream(outputPath));
    this.doc.end();

    console.log(`Invoice saved to ${outputPath}`);
  }

  /**
   * Generate sales report
   */
  createSalesReport(reportData, outputPath) {
    this.createDocument({ title: 'Sales Report' });

    this.addHeader('SALES REPORT', reportData.period);

    // Summary
    this.doc
      .fontSize(11)
      .text(`Total Sales: $${reportData.totalSales.toFixed(2)}`)
      .text(`Total Orders: ${reportData.totalOrders}`)
      .text(`Average Order Value: $${reportData.averageOrderValue.toFixed(2)}`)
      .moveDown();

    // Sales chart
    this.addBarChart(reportData.salesByCategory, {
      title: 'Sales by Category'
    });

    // Top products table
    this.doc.addPage();
    this.doc.fontSize(14).text('Top Products', { underline: true }).moveDown();

    const headers = ['Product', 'Units Sold', 'Revenue'];
    const rows = reportData.topProducts.map(p => [
      p.name,
      p.unitsSold,
      `$${p.revenue.toFixed(2)}`
    ]);

    this.addTable(headers, rows);

    this.addPageNumbers();

    this.doc.pipe(fs.createWriteStream(outputPath));
    this.doc.end();

    console.log(`Sales report saved to ${outputPath}`);
  }
}

module.exports = PDFReportGenerator;

// Example usage
if (require.main === module) {
  const generator = new PDFReportGenerator();

  // Example invoice
  const invoiceData = {
    number: 'INV-001',
    date: new Date().toLocaleDateString(),
    dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString(),
    customer: {
      name: 'John Doe',
      address: '123 Main St, City, State 12345'
    },
    items: [
      { description: 'Web Development', quantity: 1, price: 1500 },
      { description: 'Consulting', quantity: 3, price: 200 }
    ],
    total: 2100
  };

  generator.createInvoice(invoiceData, 'invoice.pdf');
}
