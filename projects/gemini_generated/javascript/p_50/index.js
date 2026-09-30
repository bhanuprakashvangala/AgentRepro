const sharp = require('sharp');

exports.handler = async (event) => {
    try {
        const { image, operations } = JSON.parse(event.body);

        if (!image) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Image data is required.' })
            };
        }

        const imageBuffer = Buffer.from(image, 'base64');
        let imageProcessor = sharp(imageBuffer);

        if (operations.resize) {
            imageProcessor = imageProcessor.resize(operations.resize.width, operations.resize.height);
        }

        if (operations.crop) {
            imageProcessor = imageProcessor.extract(operations.crop);
        }

        if (operations.format) {
            imageProcessor = imageProcessor.toFormat(operations.format.type, operations.format.options);
        }

        const processedImageBuffer = await imageProcessor.toBuffer();

        return {
            statusCode: 200,
            headers: {
                'Content-Type': `image/${operations.format ? operations.format.type : 'jpeg'}`
            },
            body: processedImageBuffer.toString('base64'),
            isBase64Encoded: true
        };

    } catch (error) {
        console.error(error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Error processing image.' })
        };
    }
};
