# Serverless Image Processing Function

AWS Lambda-friendly handler that uses [Sharp](https://sharp.pixelplumbing.com/) to resize, crop, rotate, and convert images. Returns the processed image as a base64 payload for API Gateway integrations.

## Setup
```bash
npm install
```

### Local Test
Place an image named `sample-input.jpg` in the project root and run:
```bash
npm test
```
Outputs a processed file (`output.webp`) demonstrating the handler.

## Lambda Handler
`index.js` exports `handler(event)` expecting a JSON body with:
```json
{
  "image": "<base64 string>",
  "format": "png|jpeg|webp|avif",
  "operations": {
    "resize": { "width": 800, "height": 600, "fit": "cover", "position": "center" },
    "crop": { "left": 0, "top": 0, "width": 400, "height": 300 },
    "rotate": 90
  }
}
```
- `image` (required): base64-encoded binary.
- `format` (optional): output format; defaults to source format.
- `operations.resize` (optional): pass width/height/fitting strategy.
- `operations.crop` (optional): rectangular crop with numeric dimensions.
- `operations.rotate` (optional): rotation degrees.

### Response
On success returns `statusCode 200` with headers (`Content-Type`, `Content-Disposition`) and `body` containing the base64 encoded image (`isBase64Encoded: true`). Errors are surfaced with appropriate HTTP codes.

## Deployment Tips
- Bundle dependencies using `npm install --arch=x64 --platform=linux` for Lambda.
- Adjust memory to ≥ 512 MB for larger images.
- When fronted by API Gateway, ensure binary support is enabled for image media types.
