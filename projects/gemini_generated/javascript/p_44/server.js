require('dotenv').config();
const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

// AWS S3 configuration
const s3 = new AWS.S3({
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
});

// Upload a file to S3
app.post('/upload', upload.single('file'), (req, res) => {
    const params = {
        Bucket: process.env.AWS_S3_BUCKET_NAME,
        Key: Date.now().toString() + '-' + req.file.originalname,
        Body: req.file.buffer
    };

    s3.upload(params, (err, data) => {
        if (err) {
            console.error(err);
            return res.status(500).send('Error uploading file');
        }
        res.status(200).send({ message: 'File uploaded successfully', location: data.Location });
    });
});

// Get a presigned URL for a file
app.get('/download/:key', (req, res) => {
    const params = {
        Bucket: process.env.AWS_S3_BUCKET_NAME,
        Key: req.params.key,
        Expires: 60 // URL expires in 60 seconds
    };

    s3.getSignedUrl('getObject', params, (err, url) => {
        if (err) {
            console.error(err);
            return res.status(500).send('Error generating download link');
        }
        res.status(200).send({ url });
    });
});

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
