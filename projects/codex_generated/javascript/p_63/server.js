import 'dotenv/config';
import express from 'express';
import bodyParser from 'body-parser';
import bcrypt from 'bcrypt';

const SALT_ROUNDS = Number(process.env.SALT_ROUNDS || 12);
const PORT = process.env.PORT || 5000;

const app = express();
app.use(bodyParser.json());

app.post('/hash', async (req, res) => {
  const { password } = req.body || {};
  if (!password) {
    return res.status(400).json({ message: '`password` is required' });
  }
  try {
    const hash = await bcrypt.hash(password, SALT_ROUNDS);
    return res.json({ hash, saltRounds: SALT_ROUNDS });
  } catch (error) {
    return res.status(500).json({ message: 'Failed to hash password' });
  }
});

app.post('/compare', async (req, res) => {
  const { password, hash } = req.body || {};
  if (!password || !hash) {
    return res.status(400).json({ message: '`password` and `hash` are required' });
  }
  try {
    const match = await bcrypt.compare(password, hash);
    return res.json({ match });
  } catch (error) {
    return res.status(500).json({ message: 'Comparison failed' });
  }
});

app.get('/', (req, res) => {
  res.json({ status: 'bcrypt service', saltRounds: SALT_ROUNDS });
});

app.listen(PORT, () => {
  console.log(`Password service running on http://localhost:${PORT}`);
});
