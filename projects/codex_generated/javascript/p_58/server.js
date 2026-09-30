import express from 'express';
import bodyParser from 'body-parser';
import { nanoid } from 'nanoid';
import { get, set } from 'lodash';

const app = express();
const PORT = process.env.PORT || 4000;
const DEFAULT_DELAY = Number(process.env.RESPONSE_DELAY || 0);

app.use(bodyParser.json());
app.use((req, res, next) => {
  const delay = Number(req.query.delay ?? DEFAULT_DELAY);
  if (delay > 0) {
    setTimeout(next, delay);
  } else {
    next();
  }
});

const db = {
  posts: [
    { id: '1', title: 'Hello World', author: 'Alice', published: true },
    { id: '2', title: 'Mock APIs', author: 'Bob', published: false }
  ]
};

function findCollection(name) {
  if (!db[name]) {
    db[name] = [];
  }
  return db[name];
}

app.get('/api/:collection', (req, res) => {
  const collection = findCollection(req.params.collection);
  let results = [...collection];
  Object.entries(req.query).forEach(([key, value]) => {
    if (['limit', 'offset', 'delay'].includes(key)) return;
    results = results.filter((item) => String(get(item, key)) === value);
  });

  const offset = Number(req.query.offset || 0);
  const limit = Number(req.query.limit || results.length);
  res.json(results.slice(offset, offset + limit));
});

app.get('/api/:collection/:id', (req, res) => {
  const collection = findCollection(req.params.collection);
  const record = collection.find((item) => item.id === req.params.id);
  if (!record) {
    return res.status(404).json({ message: 'Not found' });
  }
  return res.json(record);
});

app.post('/api/:collection', (req, res) => {
  const collection = findCollection(req.params.collection);
  const record = { ...req.body, id: nanoid(8) };
  collection.push(record);
  res.status(201).json(record);
});

app.put('/api/:collection/:id', (req, res) => {
  const collection = findCollection(req.params.collection);
  const index = collection.findIndex((item) => item.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ message: 'Not found' });
  }
  collection[index] = { ...collection[index], ...req.body };
  res.json(collection[index]);
});

app.delete('/api/:collection/:id', (req, res) => {
  const collection = findCollection(req.params.collection);
  const index = collection.findIndex((item) => item.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ message: 'Not found' });
  }
  const deleted = collection.splice(index, 1)[0];
  res.json(deleted);
});

app.listen(PORT, () => {
  console.log(`Mock API server running on http://localhost:${PORT}`);
});
