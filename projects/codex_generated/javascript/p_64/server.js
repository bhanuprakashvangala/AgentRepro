import 'dotenv/config';
import express from 'express';
import multer from 'multer';
import fs from 'fs';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import csvParser from 'csv-parser';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const uploadDir = path.join(__dirname, 'uploads');

const unlinkAsync = promisify(fs.unlink);

const storage = multer.diskStorage({
  destination: uploadDir,
  filename: (req, file, cb) => {
    const unique = `${Date.now()}-${Math.round(Math.random() * 1e9)}`;
    cb(null, `${unique}-${file.originalname}`);
  }
});

const upload = multer({ storage });

const app = express();
const PORT = process.env.PORT || 4000;
const PORT = process.env.PORT || 4000;

app.get('/', (req, res) => {
  res.json({ status: 'CSV to JSON converter ready', endpoint: '/convert' });
});

app.post('/convert', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: 'CSV file is required with field name `file`' });
  }

  const delimiter = req.body.delimiter || ',';
  const headersOption = parseHeaders(req.body.headers);
  const types = parseTypes(req.body.types);
  const skipLines = Number(req.body.skipLines || 0);

  res.setHeader('Content-Type', 'application/json');
  res.write('[');
  let firstRow = true;
  let finished = false;

  const stream = fs
    .createReadStream(req.file.path)
    .pipe(
      csvParser({
        separator: delimiter,
        headers: headersOption,
        skipLines: Number.isNaN(skipLines) ? 0 : skipLines
      })
    );

  stream.on('data', (row) => {
    try {
      const transformed = transformRow(row, types);
      if (!firstRow) {
        res.write(',');
      }
      res.write(JSON.stringify(transformed));
      firstRow = false;
    } catch (error) {
      stream.destroy(error);
    }
  });

  stream.on('error', (error) => {
    if (!finished) {
      finished = true;
      console.error('Parsing error:', error.message);
      if (!res.headersSent || res.writableFinished) {
        res.status(400).json({ message: error.message });
      } else {
        res.destroy();
      }
      cleanup(req.file.path);
    }
  });

  stream.on('end', async () => {
    if (!finished) {
      finished = true;
      res.write(']');
      res.end();
      await cleanup(req.file.path);
    }
  });
});

function parseHeaders(value) {
  if (value === undefined || value === '') return true;
  if (value === 'false') return false;
  if (value === 'true') return true;
  try {
    const parsed = JSON.parse(value);
    if (Array.isArray(parsed)) return parsed;
  } catch (error) {
    return value.split(',').map((h) => h.trim());
  }
  return true;
}

function parseTypes(value) {
  if (!value) return {};
  try {
    const parsed = JSON.parse(value);
    return typeof parsed === 'object' && parsed !== null ? parsed : {};
  } catch (error) {
    return {};
  }
}

function transformRow(row, types) {
  const record = Array.isArray(row) ? [...row] : { ...row };
  Object.entries(types).forEach(([field, type]) => {
    if (Array.isArray(record)) {
      const index = Number(field);
      if (Number.isNaN(index) || index < 0 || index >= record.length) return;
      record[index] = castValue(record[index], type, field);
    } else if (record[field] !== undefined) {
      record[field] = castValue(record[field], type, field);
    }
  });
  return record;
}

function castValue(value, type, field) {
  if (value === null || value === undefined || value === '') return value;
  switch (type) {
    case 'number': {
      const num = Number(value);
      if (Number.isNaN(num)) {
        throw new Error(`Invalid number for field ${field}`);
      }
      return num;
    }
    case 'boolean': {
      if (['true', '1', 'yes'].includes(String(value).toLowerCase())) return true;
      if (['false', '0', 'no'].includes(String(value).toLowerCase())) return false;
      throw new Error(`Invalid boolean for field ${field}`);
    }
    case 'date': {
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) {
        throw new Error(`Invalid date for field ${field}`);
      }
      return date.toISOString();
    }
    case 'string':
    default:
      return String(value);
  }
}

async function cleanup(filePath) {
  try {
    await unlinkAsync(filePath);
  } catch (error) {
    // ignore
  }
}

app.listen(PORT, () => {
  console.log(`CSV to JSON API running on http://localhost:${PORT}`);
});
