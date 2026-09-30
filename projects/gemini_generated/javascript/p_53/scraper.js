const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        const url = 'http://quotes.toscrape.com/js/';

        let quotes = [];
        let hasNextPage = true;

        while (hasNextPage) {
            await page.goto(url, { waitUntil: 'networkidle2' });

            const pageQuotes = await page.evaluate(() => {
                const quoteElements = document.querySelectorAll('.quote');
                const quotes = [];
                quoteElements.forEach(quoteElement => {
                    const text = quoteElement.querySelector('.text').innerText;
                    const author = quoteElement.querySelector('.author').innerText;
                    quotes.push({ text, author });
                });
                return quotes;
            });

            quotes = quotes.concat(pageQuotes);

            const nextPageButton = await page.$('.next > a');
            if (nextPageButton) {
                await Promise.all([
                    page.waitForNavigation({ waitUntil: 'networkidle2' }),
                    nextPageButton.click(),
                ]);
            } else {
                hasNextPage = false;
            }
        }

        fs.writeFileSync('quotes.json', JSON.stringify(quotes, null, 2));
        console.log('Scraping complete. Quotes saved to quotes.json');

        await browser.close();
    } catch (error) {
        console.error('Error during scraping:', error);
    }
})();
