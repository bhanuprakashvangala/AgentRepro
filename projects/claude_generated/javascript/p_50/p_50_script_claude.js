const sharp = require('sharp');

/**
 * AWS Lambda handler for image processing
 * Supports resize, crop, and format conversion operations
 *
 * @param {Object} event - Lambda event object
 * @param {Object} context - Lambda context object
 * @returns {Object} Response with processed image or error
 */
exports.handler = async (event, context) => {
  try {
    // Parse input
    const input = parseInput(event);

    // Validate input
    validateInput(input);

    // Process image
    const processedImage = await processImage(input);

    // Return response
    return createSuccessResponse(processedImage, input.format);

  } catch (error) {
    console.error('Error processing image:', error);
    return createErrorResponse(error);
  }
};

/**
 * Parse input from Lambda event
 * Supports both API Gateway and direct invocation
 */
function parseInput(event) {
  let body;

  // Handle API Gateway proxy integration
  if (event.body) {
    body = event.isBase64Encoded
      ? JSON.parse(Buffer.from(event.body, 'base64').toString('utf-8'))
      : JSON.parse(event.body);
  } else {
    // Direct invocation
    body = event;
  }

  return {
    image: body.image, // Base64 encoded image
    operations: body.operations || [],
    format: body.format || 'jpeg',
    quality: body.quality || 80
  };
}

/**
 * Validate input parameters
 */
function validateInput(input) {
  if (!input.image) {
    throw new ValidationError('Missing required field: image');
  }

  if (!Array.isArray(input.operations)) {
    throw new ValidationError('operations must be an array');
  }

  const validFormats = ['jpeg', 'png', 'webp', 'avif', 'tiff', 'gif'];
  if (!validFormats.includes(input.format)) {
    throw new ValidationError(`Invalid format. Must be one of: ${validFormats.join(', ')}`);
  }

  if (input.quality < 1 || input.quality > 100) {
    throw new ValidationError('quality must be between 1 and 100');
  }
}

/**
 * Process image with Sharp based on operations
 */
async function processImage(input) {
  try {
    // Decode base64 image
    const imageBuffer = Buffer.from(input.image, 'base64');

    // Initialize Sharp instance
    let pipeline = sharp(imageBuffer);

    // Get metadata for validation
    const metadata = await pipeline.metadata();
    console.log('Input image metadata:', {
      format: metadata.format,
      width: metadata.width,
      height: metadata.height,
      space: metadata.space,
      channels: metadata.channels,
      depth: metadata.depth
    });

    // Apply operations in sequence
    for (const operation of input.operations) {
      pipeline = applyOperation(pipeline, operation, metadata);
    }

    // Apply format conversion and quality settings
    pipeline = applyFormatConversion(pipeline, input.format, input.quality);

    // Execute pipeline and return buffer
    const outputBuffer = await pipeline.toBuffer();

    console.log('Image processed successfully. Output size:', outputBuffer.length);

    return outputBuffer;

  } catch (error) {
    if (error.message.includes('Input buffer')) {
      throw new ValidationError('Invalid image data. Unable to decode image.');
    }
    throw new ProcessingError(`Failed to process image: ${error.message}`);
  }
}

/**
 * Apply individual operation to Sharp pipeline
 */
function applyOperation(pipeline, operation, metadata) {
  const { type, params } = operation;

  switch (type) {
    case 'resize':
      return applyResize(pipeline, params, metadata);

    case 'crop':
      return applyCrop(pipeline, params, metadata);

    case 'rotate':
      return applyRotate(pipeline, params);

    case 'flip':
      return pipeline.flip();

    case 'flop':
      return pipeline.flop();

    case 'grayscale':
      return pipeline.grayscale();

    case 'blur':
      return applyBlur(pipeline, params);

    case 'sharpen':
      return applySharpen(pipeline, params);

    case 'normalize':
      return pipeline.normalize();

    default:
      throw new ValidationError(`Unknown operation type: ${type}`);
  }
}

/**
 * Apply resize operation
 */
function applyResize(pipeline, params, metadata) {
  if (!params) {
    throw new ValidationError('resize operation requires params');
  }

  const { width, height, fit = 'cover', position = 'centre', withoutEnlargement = false } = params;

  if (!width && !height) {
    throw new ValidationError('resize requires at least width or height');
  }

  const validFits = ['cover', 'contain', 'fill', 'inside', 'outside'];
  if (!validFits.includes(fit)) {
    throw new ValidationError(`Invalid fit. Must be one of: ${validFits.join(', ')}`);
  }

  console.log(`Applying resize: ${width || 'auto'}x${height || 'auto'}, fit: ${fit}`);

  return pipeline.resize({
    width: width || null,
    height: height || null,
    fit: fit,
    position: position,
    withoutEnlargement: withoutEnlargement
  });
}

/**
 * Apply crop operation
 */
function applyCrop(pipeline, params, metadata) {
  if (!params) {
    throw new ValidationError('crop operation requires params');
  }

  const { left, top, width, height } = params;

  if (left === undefined || top === undefined || !width || !height) {
    throw new ValidationError('crop requires left, top, width, and height');
  }

  // Validate crop dimensions
  if (left < 0 || top < 0 || width <= 0 || height <= 0) {
    throw new ValidationError('crop dimensions must be positive');
  }

  if (metadata.width && metadata.height) {
    if (left + width > metadata.width || top + height > metadata.height) {
      throw new ValidationError('crop area exceeds image boundaries');
    }
  }

  console.log(`Applying crop: ${width}x${height} at (${left}, ${top})`);

  return pipeline.extract({
    left: Math.round(left),
    top: Math.round(top),
    width: Math.round(width),
    height: Math.round(height)
  });
}

/**
 * Apply rotate operation
 */
function applyRotate(pipeline, params) {
  const angle = params?.angle || 90;

  if (![90, 180, 270, -90, -180, -270].includes(angle)) {
    throw new ValidationError('rotate angle must be 90, 180, 270, or their negative equivalents');
  }

  console.log(`Applying rotate: ${angle} degrees`);

  return pipeline.rotate(angle);
}

/**
 * Apply blur operation
 */
function applyBlur(pipeline, params) {
  const sigma = params?.sigma || 3;

  if (sigma < 0.3 || sigma > 1000) {
    throw new ValidationError('blur sigma must be between 0.3 and 1000');
  }

  console.log(`Applying blur: sigma ${sigma}`);

  return pipeline.blur(sigma);
}

/**
 * Apply sharpen operation
 */
function applySharpen(pipeline, params) {
  if (!params) {
    return pipeline.sharpen();
  }

  const { sigma, m1 = 1.0, m2 = 2.0, x1 = 2.0, y2 = 10.0, y3 = 20.0 } = params;

  console.log(`Applying sharpen with custom params`);

  return pipeline.sharpen(sigma, m1, m2, x1, y2, y3);
}

/**
 * Apply format conversion with quality settings
 */
function applyFormatConversion(pipeline, format, quality) {
  console.log(`Converting to ${format} with quality ${quality}`);

  const options = { quality };

  switch (format) {
    case 'jpeg':
      return pipeline.jpeg({ quality, mozjpeg: true });

    case 'png':
      return pipeline.png({
        quality,
        compressionLevel: 9,
        adaptiveFiltering: true
      });

    case 'webp':
      return pipeline.webp({ quality, effort: 6 });

    case 'avif':
      return pipeline.avif({ quality, effort: 5 });

    case 'tiff':
      return pipeline.tiff({ quality, compression: 'lzw' });

    case 'gif':
      return pipeline.gif();

    default:
      return pipeline;
  }
}

/**
 * Create success response
 */
function createSuccessResponse(imageBuffer, format) {
  const base64Image = imageBuffer.toString('base64');

  return {
    statusCode: 200,
    headers: {
      'Content-Type': `image/${format}`,
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    },
    body: JSON.stringify({
      success: true,
      image: base64Image,
      format: format,
      size: imageBuffer.length
    }),
    isBase64Encoded: false
  };
}

/**
 * Create error response
 */
function createErrorResponse(error) {
  const statusCode = error instanceof ValidationError ? 400 : 500;

  return {
    statusCode: statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    },
    body: JSON.stringify({
      success: false,
      error: error.message,
      type: error.constructor.name
    })
  };
}

/**
 * Custom error classes
 */
class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
  }
}

class ProcessingError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ProcessingError';
  }
}

// Export for testing
module.exports.processImage = processImage;
module.exports.ValidationError = ValidationError;
module.exports.ProcessingError = ProcessingError;
