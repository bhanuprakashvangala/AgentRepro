const express = require('express');
const multer = require('multer');
const csv = require('csv-parser');
const fs = require('fs');
const { Readable } = require('stream');
const Joi = require('joi');

const app = express();
const upload = multer({ dest: 'uploads/' });

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Data type validators and transformers
const typeTransformers = {
  string: (value) => String(value),
  number: (value) => {
    const num = Number(value);
    if (isNaN(num)) throw new Error(`Cannot convert "${value}" to number`);
    return num;
  },
  boolean: (value) => {
    const lower = String(value).toLowerCase().trim();
    if (lower === 'true' || lower === '1' || lower === 'yes') return true;
    if (lower === 'false' || lower === '0' || lower === 'no') return false;
    throw new Error(`Cannot convert "${value}" to boolean`);
  },
  date: (value) => {
    const date = new Date(value);
    if (isNaN(date.getTime())) throw new Error(`Cannot convert "${value}" to date`);
    return date.toISOString();
  },
  integer: (value) => {
    const num = parseInt(value, 10);
    if (isNaN(num)) throw new Error(`Cannot convert "${value}" to integer`);
    return num;
  },
  float: (value) => {
    const num = parseFloat(value);
    if (isNaN(num)) throw new Error(`Cannot convert "${value}" to float`);
    return num;
  }
};

// Validation schema for conversion options
const conversionOptionsSchema = Joi.object({
  delimiter: Joi.string().max(5).default(','),
  headers: Joi.alternatives().try(
    Joi.array().items(Joi.string()),
    Joi.boolean()
  ).default(true),
  skipLines: Joi.number().integer().min(0).default(0),
  skipEmptyLines: Joi.boolean().default(true),
  trim: Joi.boolean().default(true),
  typeMapping: Joi.object().pattern(
    Joi.string(),
    Joi.string().valid('string', 'number', 'boolean', 'date', 'integer', 'float')
  ).default({}),
  strictValidation: Joi.boolean().default(false)
});

/**
 * Transform row data based on type mapping
 */
function transformRow(row, typeMapping, strictValidation) {
  const transformed = {};
  const errors = [];

  for (const [key, value] of Object.entries(row)) {
    const targetType = typeMapping[key];

    if (!targetType || targetType === 'string') {
      transformed[key] = value;
      continue;
    }

    try {
      transformed[key] = typeTransformers[targetType](value);
    } catch (error) {
      errors.push({ field: key, value, error: error.message });

      if (strictValidation) {
        throw new Error(`Validation error in field "${key}": ${error.message}`);
      }

      // In non-strict mode, keep original value
      transformed[key] = value;
    }
  }

  return { transformed, errors: errors.length > 0 ? errors : null };
}

/**
 * Convert CSV stream to JSON with options
 */
function convertCSVToJSON(stream, options) {
  return new Promise((resolve, reject) => {
    const results = [];
    const validationErrors = [];
    let lineNumber = 0;

    const parserOptions = {
      separator: options.delimiter,
      skipLines: options.skipLines
    };

    // Handle custom headers
    if (Array.isArray(options.headers)) {
      parserOptions.headers = options.headers;
    } else if (options.headers === false) {
      parserOptions.headers = false;
    }

    if (options.skipEmptyLines) {
      parserOptions.skipEmptyLines = true;
    }

    stream
      .pipe(csv(parserOptions))
      .on('data', (row) => {
        lineNumber++;

        // Trim values if requested
        if (options.trim) {
          for (const key in row) {
            if (typeof row[key] === 'string') {
              row[key] = row[key].trim();
            }
          }
        }

        // Transform data types
        try {
          const { transformed, errors } = transformRow(
            row,
            options.typeMapping,
            options.strictValidation
          );

          results.push(transformed);

          if (errors) {
            validationErrors.push({
              line: lineNumber,
              errors
            });
          }
        } catch (error) {
          return reject({
            error: 'Validation failed',
            line: lineNumber,
            message: error.message
          });
        }
      })
      .on('end', () => {
        resolve({
          success: true,
          rowCount: results.length,
          data: results,
          validationErrors: validationErrors.length > 0 ? validationErrors : undefined
        });
      })
      .on('error', (error) => {
        reject({
          error: 'CSV parsing failed',
          message: error.message
        });
      });
  });
}

// API Routes

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'csv-to-json-api' });
});

/**
 * Convert CSV file to JSON
 * POST /convert/file
 */
app.post('/convert/file', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Parse and validate options
    const options = JSON.parse(req.body.options || '{}');
    const { error, value } = conversionOptionsSchema.validate(options);

    if (error) {
      fs.unlinkSync(req.file.path); // Clean up uploaded file
      return res.status(400).json({
        error: 'Invalid options',
        details: error.details
      });
    }

    // Create read stream and convert
    const fileStream = fs.createReadStream(req.file.path);
    const result = await convertCSVToJSON(fileStream, value);

    // Clean up uploaded file
    fs.unlinkSync(req.file.path);

    res.json(result);
  } catch (error) {
    // Clean up uploaded file on error
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }

    res.status(400).json(error);
  }
});

/**
 * Convert CSV data (raw text) to JSON
 * POST /convert/data
 */
app.post('/convert/data', async (req, res) => {
  try {
    const { csvData, options } = req.body;

    if (!csvData) {
      return res.status(400).json({ error: 'No CSV data provided' });
    }

    // Validate options
    const { error, value } = conversionOptionsSchema.validate(options || {});

    if (error) {
      return res.status(400).json({
        error: 'Invalid options',
        details: error.details
      });
    }

    // Create stream from string data
    const dataStream = Readable.from([csvData]);
    const result = await convertCSVToJSON(dataStream, value);

    res.json(result);
  } catch (error) {
    res.status(400).json(error);
  }
});

/**
 * Get available type transformers
 * GET /types
 */
app.get('/types', (req, res) => {
  res.json({
    availableTypes: Object.keys(typeTransformers),
    examples: {
      string: 'Any value as string',
      number: '123.45',
      boolean: 'true, false, 1, 0, yes, no',
      date: '2025-01-15 or any valid date string',
      integer: '42',
      float: '3.14159'
    }
  });
});

/**
 * Example endpoint showing usage
 * GET /example
 */
app.get('/example', (req, res) => {
  res.json({
    fileUploadExample: {
      endpoint: 'POST /convert/file',
      contentType: 'multipart/form-data',
      fields: {
        file: 'CSV file',
        options: 'JSON string with conversion options'
      }
    },
    dataConversionExample: {
      endpoint: 'POST /convert/data',
      contentType: 'application/json',
      body: {
        csvData: 'name,age,active\\nJohn,25,true\\nJane,30,false',
        options: {
          delimiter: ',',
          headers: true,
          trim: true,
          typeMapping: {
            age: 'integer',
            active: 'boolean'
          },
          strictValidation: false
        }
      }
    },
    optionsDescription: {
      delimiter: 'Character(s) to use as field delimiter (default: ",")',
      headers: 'true (use first row), false (no headers), or array of header names',
      skipLines: 'Number of lines to skip at start of file',
      skipEmptyLines: 'Skip empty lines (default: true)',
      trim: 'Trim whitespace from values (default: true)',
      typeMapping: 'Object mapping field names to data types',
      strictValidation: 'Throw error on type conversion failure (default: false)'
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message
  });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`CSV to JSON API running on port ${PORT}`);
  console.log(`Visit http://localhost:${PORT}/example for usage examples`);
});

// Create uploads directory if it doesn't exist
if (!fs.existsSync('./uploads')) {
  fs.mkdirSync('./uploads');
}
