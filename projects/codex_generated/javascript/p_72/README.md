# Redis Cluster Cache Service

Express API using `ioredis` to connect to a Redis cluster for get/set operations with TTL and failover handling.

## Setup
Ensure Redis cluster nodes are available. Define env var:
```
REDIS_CLUSTER_NODES=127.0.0.1:7000,127.0.0.1:7001,127.0.0.1:7002
```

Then:
```bash
npm install
npm start
```

## API
- `POST /cache`
  ```json
  { "key": "user:1", "value": {"name": "Alice"}, "ttl": 600 }
  ```
- `GET /cache/:key`

Connections automatically handle node failover (`ioredis` cluster client). TTL defaults to 300 seconds.
