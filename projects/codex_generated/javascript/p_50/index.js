import sharp from 'sharp';

const ALLOWED_FORMATS = new Set(['jpeg', 'png', 'webp', 'avif']);

function parseEvent(event) {
  let payload;
  if (event.body) {
    try {
      payload = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
    } catch (error) {
      throw new BadRequestError('Invalid JSON body');
    }
  } else {
    payload = event;
  }

  if (!payload.image) {
    throw new BadRequestError('`image` (base64 string) is required');
  }

  const buffer = Buffer.from(payload.image, 'base64');
  if (!buffer.length) {
    throw new BadRequestError('Image data could not be decoded');
  }

  return {
    buffer,
    operations: payload.operations || {},
    outputFormat: payload.format || null
  };
}

async function processImage(buffer, operations, outputFormat) {
  let transformer = sharp(buffer, { failOn: 'none' });

  if (operations.resize) {
    const { width, height, fit, position } = operations.resize;
    transformer = transformer.resize({
      width: width ? Number(width) : undefined,
      height: height ? Number(height) : undefined,
      fit: fit || 'cover',
      position: position || 'center'
    });
  }

  if (operations.crop) {
    const { left, top, width, height } = operations.crop;
    if ([left, top, width, height].some((value) => typeof value !== 'number')) {
      throw new BadRequestError('Crop requires numeric left, top, width, height');
    }
    transformer = transformer.extract({ left, top, width, height });
  }

  if (operations.rotate) {
    transformer = transformer.rotate(Number(operations.rotate));
  }

  if (outputFormat) {
    const format = outputFormat.toLowerCase();
    if (!ALLOWED_FORMATS.has(format)) {
      throw new BadRequestError(`Unsupported format: ${format}`);
    }
    transformer = transformer.toFormat(format);
  }

  return transformer.toBuffer({ resolveWithObject: true });
}

function response(statusCode, body, headers = {}, isBase64Encoded = false) {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      ...headers
    },
    body: isBase64Encoded ? body : JSON.stringify(body),
    isBase64Encoded
  };
}

class BadRequestError extends Error {
  constructor(message) {
    super(message);
    this.name = 'BadRequestError';
    this.statusCode = 400;
  }
}

export const handler = async (event) => {
  try {
    const { buffer, operations, outputFormat } = parseEvent(event);
    const { data, info } = await processImage(buffer, operations, outputFormat);
    const base64 = data.toString('base64');
    return {
      statusCode: 200,
      headers: {
        'Content-Type': `image/${info.format}`,
        'Content-Disposition': `inline; filename="output.${info.format}"`
      },
      body: base64,
      isBase64Encoded: true
    };
  } catch (error) {
    console.error('Processing error:', error);
    if (error instanceof BadRequestError) {
      return response(error.statusCode, { message: error.message });
    }
    return response(500, { message: 'Internal server error' });
  }
};
