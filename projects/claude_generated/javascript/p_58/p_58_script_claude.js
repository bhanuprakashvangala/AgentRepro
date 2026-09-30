const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// In-memory database
let database = {
  users: [
    { id: 1, name: 'John Doe', email: 'john@example.com', age: 30, active: true },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', age: 25, active: true },
    { id: 3, name: 'Bob Johnson', email: 'bob@example.com', age: 35, active: false }
  ],
  posts: [
    { id: 1, userId: 1, title: 'First Post', content: 'Hello World', published: true },
    { id: 2, userId: 1, title: 'Second Post', content: 'Learning APIs', published: true },
    { id: 3, userId: 2, title: 'Jane\'s Post', content: 'My first blog', published: false }
  ],
  comments: [
    { id: 1, postId: 1, author: 'Alice', text: 'Great post!' },
    { id: 2, postId: 1, author: 'Charlie', text: 'Thanks for sharing' },
    { id: 3, postId: 2, author: 'David', text: 'Very informative' }
  ]
};

// Configurable delay middleware
const delayMiddleware = (req, res, next) => {
  const delay = parseInt(req.query.delay) || parseInt(req.headers['x-delay']) || 0;
  if (delay > 0) {
    setTimeout(next, delay);
  } else {
    next();
  }
};

app.use(delayMiddleware);

// Utility functions
const getNextId = (collection) => {
  const items = database[collection];
  return items.length > 0 ? Math.max(...items.map(item => item.id)) + 1 : 1;
};

const filterItems = (items, query) => {
  let filtered = [...items];

  // Remove special query params
  const { delay, _sort, _order, _limit, _page, ...filters } = query;

  // Apply filters
  Object.keys(filters).forEach(key => {
    const value = filters[key];

    // Handle nested properties (e.g., ?userId=1)
    filtered = filtered.filter(item => {
      const itemValue = item[key];

      // Handle different comparison operators
      if (value.includes('>=')) {
        const compareValue = parseFloat(value.replace('>=', ''));
        return parseFloat(itemValue) >= compareValue;
      } else if (value.includes('<=')) {
        const compareValue = parseFloat(value.replace('<=', ''));
        return parseFloat(itemValue) <= compareValue;
      } else if (value.includes('>')) {
        const compareValue = parseFloat(value.replace('>', ''));
        return parseFloat(itemValue) > compareValue;
      } else if (value.includes('<')) {
        const compareValue = parseFloat(value.replace('<', ''));
        return parseFloat(itemValue) < compareValue;
      } else if (value.includes('*')) {
        // Wildcard search
        const regex = new RegExp(value.replace(/\*/g, '.*'), 'i');
        return regex.test(String(itemValue));
      } else {
        // Exact match (with type coercion)
        return String(itemValue).toLowerCase() === String(value).toLowerCase();
      }
    });
  });

  // Apply sorting
  if (_sort) {
    const sortField = _sort;
    const sortOrder = (_order || 'asc').toLowerCase();
    filtered.sort((a, b) => {
      if (a[sortField] < b[sortField]) return sortOrder === 'asc' ? -1 : 1;
      if (a[sortField] > b[sortField]) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }

  // Apply pagination
  const limit = parseInt(_limit) || filtered.length;
  const page = parseInt(_page) || 1;
  const start = (page - 1) * limit;
  const end = start + limit;

  return filtered.slice(start, end);
};

// Generic CRUD routes for any collection
const createCrudRoutes = (collectionName) => {
  // GET all items (with filtering, sorting, pagination)
  app.get(`/${collectionName}`, (req, res) => {
    const items = database[collectionName];
    if (!items) {
      return res.status(404).json({ error: `Collection '${collectionName}' not found` });
    }

    const filtered = filterItems(items, req.query);
    res.json(filtered);
  });

  // GET single item by ID
  app.get(`/${collectionName}/:id`, (req, res) => {
    const items = database[collectionName];
    if (!items) {
      return res.status(404).json({ error: `Collection '${collectionName}' not found` });
    }

    const id = parseInt(req.params.id);
    const item = items.find(i => i.id === id);

    if (!item) {
      return res.status(404).json({ error: `Item with id ${id} not found` });
    }

    res.json(item);
  });

  // POST create new item
  app.post(`/${collectionName}`, (req, res) => {
    if (!database[collectionName]) {
      database[collectionName] = [];
    }

    const newItem = {
      id: getNextId(collectionName),
      ...req.body
    };

    database[collectionName].push(newItem);
    res.status(201).json(newItem);
  });

  // PUT update entire item
  app.put(`/${collectionName}/:id`, (req, res) => {
    const items = database[collectionName];
    if (!items) {
      return res.status(404).json({ error: `Collection '${collectionName}' not found` });
    }

    const id = parseInt(req.params.id);
    const index = items.findIndex(i => i.id === id);

    if (index === -1) {
      return res.status(404).json({ error: `Item with id ${id} not found` });
    }

    const updatedItem = { id, ...req.body };
    database[collectionName][index] = updatedItem;
    res.json(updatedItem);
  });

  // PATCH update partial item
  app.patch(`/${collectionName}/:id`, (req, res) => {
    const items = database[collectionName];
    if (!items) {
      return res.status(404).json({ error: `Collection '${collectionName}' not found` });
    }

    const id = parseInt(req.params.id);
    const index = items.findIndex(i => i.id === id);

    if (index === -1) {
      return res.status(404).json({ error: `Item with id ${id} not found` });
    }

    const updatedItem = { ...items[index], ...req.body, id };
    database[collectionName][index] = updatedItem;
    res.json(updatedItem);
  });

  // DELETE item
  app.delete(`/${collectionName}/:id`, (req, res) => {
    const items = database[collectionName];
    if (!items) {
      return res.status(404).json({ error: `Collection '${collectionName}' not found` });
    }

    const id = parseInt(req.params.id);
    const index = items.findIndex(i => i.id === id);

    if (index === -1) {
      return res.status(404).json({ error: `Item with id ${id} not found` });
    }

    const deletedItem = items[index];
    database[collectionName].splice(index, 1);
    res.json(deletedItem);
  });
};

// Create routes for existing collections
Object.keys(database).forEach(collection => {
  createCrudRoutes(collection);
});

// Root endpoint - show available collections
app.get('/', (req, res) => {
  res.json({
    message: 'JSON API Mock Server',
    collections: Object.keys(database),
    endpoints: Object.keys(database).map(c => `/${c}`),
    features: [
      'Full CRUD operations (GET, POST, PUT, PATCH, DELETE)',
      'Query filtering (?key=value)',
      'Sorting (?_sort=field&_order=asc|desc)',
      'Pagination (?_page=1&_limit=10)',
      'Operators: >=, <=, >, <, * (wildcard)',
      'Response delays (?delay=1000 or header X-Delay: 1000)'
    ]
  });
});

// Custom endpoint for simulating errors
app.get('/error/:code', (req, res) => {
  const code = parseInt(req.params.code);
  res.status(code).json({
    error: true,
    code: code,
    message: `Simulated error with status code ${code}`
  });
});

// Reset database endpoint
app.post('/reset', (req, res) => {
  database = {
    users: [
      { id: 1, name: 'John Doe', email: 'john@example.com', age: 30, active: true },
      { id: 2, name: 'Jane Smith', email: 'jane@example.com', age: 25, active: true },
      { id: 3, name: 'Bob Johnson', email: 'bob@example.com', age: 35, active: false }
    ],
    posts: [
      { id: 1, userId: 1, title: 'First Post', content: 'Hello World', published: true },
      { id: 2, userId: 1, title: 'Second Post', content: 'Learning APIs', published: true },
      { id: 3, userId: 2, title: 'Jane\'s Post', content: 'My first blog', published: false }
    ],
    comments: [
      { id: 1, postId: 1, author: 'Alice', text: 'Great post!' },
      { id: 2, postId: 1, author: 'Charlie', text: 'Thanks for sharing' },
      { id: 3, postId: 2, author: 'David', text: 'Very informative' }
    ]
  };
  res.json({ message: 'Database reset successfully', collections: Object.keys(database) });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🚀 JSON API Mock Server running on http://localhost:${PORT}`);
  console.log(`\nAvailable collections:`);
  Object.keys(database).forEach(collection => {
    console.log(`  - http://localhost:${PORT}/${collection}`);
  });
  console.log(`\nFeatures:`);
  console.log(`  - Full CRUD operations (GET, POST, PUT, PATCH, DELETE)`);
  console.log(`  - Query filtering: ?key=value`);
  console.log(`  - Sorting: ?_sort=field&_order=asc|desc`);
  console.log(`  - Pagination: ?_page=1&_limit=10`);
  console.log(`  - Operators: >=, <=, >, <, * (wildcard)`);
  console.log(`  - Response delays: ?delay=1000 or header "X-Delay: 1000"`);
  console.log(`\nExamples:`);
  console.log(`  GET  http://localhost:${PORT}/users?active=true&_sort=age`);
  console.log(`  GET  http://localhost:${PORT}/posts?userId=1&delay=500`);
  console.log(`  POST http://localhost:${PORT}/users`);
  console.log(`\n`);
});
