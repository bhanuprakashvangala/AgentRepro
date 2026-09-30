# Serverless Image Processing Function

This project is a serverless image processing function using the Sharp library, designed for deployment on AWS Lambda.

## Requirements

- Node.js
- npm
- AWS Account

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Deployment to AWS Lambda

1.  Create a new Lambda function in the AWS console.
2.  Choose the "Author from scratch" option.
3.  Select the Node.js runtime.
4.  Create a deployment package by zipping the `index.js` file and the `node_modules` directory.
5.  Upload the zip file to the Lambda function.
6.  Set the handler to `index.handler`.
7.  Create an API Gateway trigger for the Lambda function to make it accessible via HTTP.

## Usage

Send a POST request to the API Gateway endpoint with a JSON payload containing the image and the desired operations.

### Example Payload

```json
{
    "image": "<base64-encoded-image>",
    "operations": {
        "resize": {
            "width": 200,
            "height": 200
        },
        "crop": {
            "left": 10,
            "top": 10,
            "width": 50,
            "height": 50
        },
        "format": {
            "type": "png"
        }
    }
}
```
