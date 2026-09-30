const express = require('express');
const multer = require('multer');
const csv = require('csv-parser');
const { Readable } = require('stream');

const app = express();
const upload = multer();

app.post('/convert', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file uploaded.');
    }

    const results = [];
    const stream = Readable.from(req.file.buffer.toString());

    stream
        .pipe(csv({
            separator: req.body.delimiter || ',',
            headers: req.body.headers ? req.body.headers.split(',') : true,
            mapValues: ({ header, index, value }) => {
                // Example of data transformation: convert age to a number
                if (header === 'age') {
                    return parseInt(value, 10);
                }
                return value;
            }
        }))
        .on('data', (data) => results.push(data))
        .on('end', () => {
            res.json(results);
        });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
