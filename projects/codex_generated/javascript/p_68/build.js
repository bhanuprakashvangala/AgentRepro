import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import CleanCSS from 'clean-css';
import { minify } from 'terser';
import { minify as minifyHtml } from 'html-minifier';
import sharp from 'sharp';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const srcDir = path.join(__dirname, 'src');
const distDir = path.join(__dirname, 'dist');

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function buildCSS() {
  const cssDir = path.join(srcDir, 'assets/css');
  const files = await fs.readdir(cssDir);
  for (const file of files) {
    if (!file.endsWith('.css')) continue;
    const cssPath = path.join(cssDir, file);
    const css = await fs.readFile(cssPath, 'utf-8');
    const output = new CleanCSS().minify(css).styles;
    const outPath = path.join(distDir, 'css');
    await ensureDir(outPath);
    await fs.writeFile(path.join(outPath, file), output);
  }
}

async function buildJS() {
  const jsDir = path.join(srcDir, 'assets/js');
  const files = await fs.readdir(jsDir);
  for (const file of files) {
    if (!file.endsWith('.js')) continue;
    const jsPath = path.join(jsDir, file);
    const code = await fs.readFile(jsPath, 'utf-8');
    const result = await minify(code);
    const outPath = path.join(distDir, 'js');
    await ensureDir(outPath);
    await fs.writeFile(path.join(outPath, file), result.code);
  }
}

async function buildImages() {
  const imgDir = path.join(srcDir, 'assets/images');
  try {
    const files = await fs.readdir(imgDir);
    for (const file of files) {
      const imgPath = path.join(imgDir, file);
      const outDir = path.join(distDir, 'images');
      await ensureDir(outDir);
      await sharp(imgPath).resize({ width: 1024 }).jpeg({ quality: 80 }).toFile(path.join(outDir, file.replace(/\.[^.]+$/, '.jpg')));
    }
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
}

async function buildHtml() {
  const indexPath = path.join(srcDir, 'index.html');
  const html = await fs.readFile(indexPath, 'utf-8');
  const output = minifyHtml(html, {
    collapseWhitespace: true,
    removeComments: true,
    minifyCSS: true,
    minifyJS: true
  });
  await fs.writeFile(path.join(distDir, 'index.html'), output);
}

await ensureDir(distDir);
await Promise.all([buildCSS(), buildJS(), buildImages(), buildHtml()]);
console.log('Build complete.');
