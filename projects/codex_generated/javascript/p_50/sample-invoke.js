import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { handler } from './index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function run() {
  const inputPath = path.join(__dirname, 'sample-input.jpg');
  if (!fs.existsSync(inputPath)) {
    console.error('sample-input.jpg not found. Place an image in the project root to run this demo.');
    process.exit(1);
  }

  const imageBase64 = fs.readFileSync(inputPath).toString('base64');
  const event = {
    body: JSON.stringify({
      image: imageBase64,
      format: 'webp',
      operations: {
        resize: { width: 600, height: 400, fit: 'contain', position: 'center' },
        rotate: 0
      }
    })
  };

  const result = await handler(event);
  if (result.statusCode === 200) {
    const outputBuffer = Buffer.from(result.body, 'base64');
    const outputPath = path.join(__dirname, `output.${result.headers['Content-Type'].split('/')[1]}`);
    fs.writeFileSync(outputPath, outputBuffer);
    console.log(`Saved processed image to ${outputPath}`);
  } else {
    console.error('Request failed:', result);
  }
}

run();
