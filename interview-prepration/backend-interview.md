# Backend Interview Reference

A senior-focused reference covering API design, databases, security, caching, scalability, and reliability patterns. Concept + code snippet format.

---

## Table of Contents

### Part 1: Core Interview Topics

1. [API Performance Optimization](#1-api-performance-optimization)
2. [CORS vs CSRF](#2-cors-vs-csrf)
3. [Database at Scale](#3-database-at-scale)
4. [Caching Strategies](#4-caching-strategies)
5. [JWT & Refresh Tokens](#5-jwt--refresh-tokens)
6. [Password Security](#6-password-security)
7. [Brute Force Protection & Rate Limiting](#7-brute-force-protection--rate-limiting)
8. [Load Balancing](#8-load-balancing)
9. [SQL vs NoSQL](#9-sql-vs-nosql)
10. [REST vs WebSockets vs Data Formats](#10-rest-vs-websockets-vs-data-formats)
11. [Code Architecture — Modular vs Monolithic Files](#11-code-architecture--modular-vs-monolithic-files)
12. [Error Handling](#12-error-handling)
13. [Microservices vs Monolithic Architecture](#13-microservices-vs-monolithic-architecture)
14. [Message Queues](#14-message-queues)
33. [OAuth 2.0 / OpenID Connect / Social Login](#33-oauth-20--openid-connect--social-login)
34. [gRPC & GraphQL](#34-grpc--graphql)

### Part 2: Security Checklist

15. [Auth & OTP Security](#15-auth--otp-security)
16. [Input & Upload Security](#16-input--upload-security)
17. [API & Logging Security](#17-api--logging-security)
35. [SQL Injection & XSS Prevention](#35-sql-injection--xss-prevention)

### Part 3: API Design Best Practices

18. [Time Zones & Data Handling](#18-time-zones--data-handling)
19. [Third-Party Integrations](#19-third-party-integrations)
20. [HTTP Methods, Pagination & Sensitive Data](#20-http-methods-pagination--sensitive-data)
36. [Soft Delete vs Hard Delete](#36-soft-delete-vs-hard-delete)
37. [Database Migrations (Zero-Downtime)](#37-database-migrations-zero-downtime)

### Part 4: Reliability Patterns

21. [Rate Limiter](#21-rate-limiter)
22. [Idempotency](#22-idempotency)
23. [Request Timeout](#23-request-timeout)
24. [Outbox Pattern](#24-outbox-pattern)
25. [Retry Pattern](#25-retry-pattern)
26. [Circuit Breaker](#26-circuit-breaker)
38. [Saga Pattern / Distributed Transactions](#38-saga-pattern--distributed-transactions)
39. [Bulkhead Pattern](#39-bulkhead-pattern)
40. [Dead Letter Queue (DLQ)](#40-dead-letter-queue-dlq)

### Part 5: Advanced Topics

27. [Scaling Strategies](#27-scaling-strategies)
28. [CAP Theorem & Consistency Models](#28-cap-theorem--consistency-models)
29. [Database Internals](#29-database-internals)
30. [Observability](#30-observability)
31. [API Versioning](#31-api-versioning)
32. [Background Jobs & Queues](#32-background-jobs--queues)
41. [Event Sourcing & CQRS](#41-event-sourcing--cqrs)
42. [Deployment Strategies](#42-deployment-strategies)

---

# Part 1: Core Interview Topics

---

## 1. API Performance Optimization

API speed directly affects UX — slow APIs increase bounce rate and degrade perceived quality. A 100ms delay can reduce conversions by 1%. At scale, it compounds across millions of requests.

### Techniques

**1. Database query optimization** — the most common bottleneck:

```js
// Avoid N+1 — fetch related data in one query
// BAD: 1 query for orders + N queries for each user
const orders = await Order.findAll();
for (const order of orders) {
  order.user = await User.findById(order.userId); // N queries
}

// GOOD: single JOIN
const orders = await Order.findAll({ include: [{ model: User }] });
```

**2. Caching** — serve from memory, skip the DB entirely (see Section 4).

**3. Pagination** — never return unbounded result sets:

```js
// Always paginate
GET /api/orders?page=1&limit=20
GET /api/orders?cursor=abc123&limit=20  // cursor-based for large tables
```

**4. Async/parallel execution** — don't serialize independent operations:

```js
// BAD — sequential: total time = A + B + C
const user = await fetchUser(id);
const orders = await fetchOrders(id);
const profile = await fetchProfile(id);

// GOOD — parallel: total time = max(A, B, C)
const [user, orders, profile] = await Promise.all([fetchUser(id), fetchOrders(id), fetchProfile(id)]);
```

**5. Response compression** — gzip/brotli reduces payload size 60–80%:

```js
const compression = require('compression');
app.use(compression());
```

**6. Connection pooling** — reuse DB connections instead of opening a new one per request (see Node.js doc Section 20).

**7. Selective field fetching** — only return what the client needs:

```js
// SQL: SELECT only needed columns
SELECT id, name, email FROM users WHERE id = $1
// Not: SELECT * FROM users

// GraphQL naturally solves this problem
```

**8. HTTP caching headers** — let clients and CDNs cache responses:

```
Cache-Control: public, max-age=300, stale-while-revalidate=60
ETag: "33a64df5"
```

**9. CDN for static assets and edge caching** — serve from the closest geographic node.

**10. Async processing for heavy operations** — return 202 Accepted immediately, process in background:

```js
app.post('/api/reports', async (req, res) => {
  const jobId = await queue.add('generate-report', req.body);
  res.status(202).json({ jobId, status: 'processing' });
});

// Client polls: GET /api/reports/jobs/:jobId
```

---

## 2. CORS vs CSRF

Both relate to cross-origin requests, but they are different problems solved differently.

### CORS (Cross-Origin Resource Sharing)

CORS is a **browser mechanism** that controls which origins can read responses from your server. It is enforced by the browser — not the server.

- **Problem it solves:** Prevents malicious websites from reading your API's responses
- **Who it protects:** Your users' data from being exfiltrated by third-party sites
- **Mechanism:** Server sends `Access-Control-Allow-Origin` headers; browser blocks responses that don't match

```
# Preflight (OPTIONS) — browser asks: "can origin X use method DELETE?"
Request:  OPTIONS /api/users/1
          Origin: https://evil.com
          Access-Control-Request-Method: DELETE

Response: 403 — server doesn't allow evil.com
```

**CORS alone is NOT enough security** — it only protects against cross-origin reads. It does not prevent cross-origin writes (state-changing requests can still be sent).

### CSRF (Cross-Site Request Forgery)

CSRF tricks an authenticated user's browser into making a state-changing request to your server. The browser automatically sends cookies — CORS doesn't stop this.

- **Problem it solves:** Prevents malicious sites from making authenticated requests on behalf of your users
- **Mechanism:** Attacker's site makes a form POST to `bank.com/transfer` — browser sends session cookie automatically

```html
<!-- On evil.com — triggers a POST to bank.com with victim's cookies -->
<form action="https://bank.com/transfer" method="POST">
  <input name="amount" value="1000" />
  <input name="to" value="attacker" />
</form>
<script>
  document.forms[0].submit();
</script>
```

**Defenses:**

```js
// 1. SameSite cookies — most effective modern defense
res.cookie('session', token, {
  sameSite: 'Lax', // blocks cross-site POST/PUT/DELETE
  httpOnly: true,
  secure: true,
});

// 2. CSRF token — server issues random token, validates on state-changing requests
app.use(csrf({ cookie: true }));
app.get('/form', (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});
// <input type="hidden" name="_csrf" value="<%= csrfToken %>" />

// 3. Origin/Referer header check
app.use((req, res, next) => {
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
    const origin = req.headers.origin || req.headers.referer;
    if (!origin?.startsWith('https://myapp.com')) {
      return res.status(403).json({ error: 'Forbidden' });
    }
  }
  next();
});
```

|                               | CORS                              | CSRF                                 |
| ----------------------------- | --------------------------------- | ------------------------------------ |
| Protects against              | Unauthorized cross-origin reads   | Unauthorized state-changing requests |
| Enforced by                   | Browser                           | Server                               |
| Main defense                  | `Access-Control-Allow-Origin`     | `SameSite` cookie + CSRF token       |
| JWT in `Authorization` header | Protected (headers not auto-sent) | Protected (headers not auto-sent)    |
| Session cookies               | Not protected by CORS             | Must use CSRF token or SameSite      |

---

## 3. Database at Scale

### Indexing

An index is a separate data structure (usually a B-tree) that allows the DB to find rows without scanning the full table.

```sql
-- Without index: full table scan O(n)
SELECT * FROM orders WHERE user_id = 123;

-- With index: B-tree lookup O(log n)
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Composite index — order matters: (user_id, status) serves queries on
-- user_id alone OR user_id + status. Does NOT serve status alone.
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index — index only a subset of rows (smaller, faster)
CREATE INDEX idx_active_orders ON orders(user_id) WHERE status = 'active';

-- Covering index — index contains all columns the query needs (no heap fetch)
CREATE INDEX idx_user_email_name ON users(email) INCLUDE (name, created_at);

-- Analyze query plan
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;
-- Look for: "Index Scan" (good) vs "Seq Scan" (bad for large tables)
```

**Indexing is NOT free:**

- Every index slows down `INSERT`/`UPDATE`/`DELETE` (index must be updated)
- Indexes consume disk space and memory
- Rule: index columns used in `WHERE`, `JOIN ON`, `ORDER BY`, and foreign keys

### Beyond Indexing

```sql
-- 1. Query optimization — avoid SELECT *, use specific columns
SELECT id, name, email FROM users WHERE id = $1;

-- 2. Avoid functions on indexed columns (prevents index use)
-- BAD:
WHERE LOWER(email) = 'test@example.com'
-- GOOD: store normalized data or use a functional index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- 3. Pagination — use cursor-based for large offsets
-- BAD: OFFSET 100000 — scans and discards 100k rows
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;
-- GOOD: cursor-based
SELECT * FROM orders WHERE id > :cursor ORDER BY id LIMIT 20;

-- 4. Partitioning — split huge tables by range/list/hash
CREATE TABLE orders_2024 PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- 5. Read replicas — route read-heavy queries to replicas
const readDb  = createPool(process.env.DB_READ_REPLICA_URL);
const writeDb = createPool(process.env.DB_PRIMARY_URL);

async function getUser(id) {
  return readDb.query('SELECT * FROM users WHERE id = $1', [id]);
}
async function createUser(data) {
  return writeDb.query('INSERT INTO users ...', data);
}

-- 6. Denormalization — store precomputed aggregates for read performance
-- Instead of: SELECT COUNT(*) FROM likes WHERE post_id = $1 on every request
-- Store: posts.like_count and increment/decrement it
```

---

## 4. Caching Strategies

Caching stores computed results so future requests can be served faster. Most effective when data is read frequently and changes infrequently.

### Where to Cache

```
Client (browser)
  ↓ Cache-Control headers
CDN / Edge cache (Cloudflare, CloudFront)
  ↓ Cached full responses
API Gateway / Reverse proxy (Nginx, Varnish)
  ↓ Cached route responses
Application cache (Redis, Memcached)
  ↓ Cached DB results, sessions, computed values
Database query cache (built-in, limited)
  ↓ Raw DB
```

### Cache Patterns

```js
// Cache-aside (lazy loading) — most common
async function getUser(id) {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const user = await db.query('SELECT * FROM users WHERE id = $1', [id]);
  await redis.setex(`user:${id}`, 300, JSON.stringify(user)); // TTL: 5 min
  return user;
}

// Invalidate on update
async function updateUser(id, data) {
  await db.query('UPDATE users SET ... WHERE id = $1', [id, ...data]);
  await redis.del(`user:${id}`); // invalidate cache
}

// Write-through — write to cache and DB simultaneously
async function updateUserWriteThrough(id, data) {
  const user = await db.query('UPDATE users SET ... WHERE id = $1 RETURNING *', [id]);
  await redis.setex(`user:${id}`, 300, JSON.stringify(user));
  return user;
}

// Cache with tag-based invalidation
await redis.set(`post:${postId}`, JSON.stringify(post));
await redis.sadd(`user:${userId}:posts`, `post:${postId}`); // track which keys belong to a user

// Invalidate all posts for a user
const keys = await redis.smembers(`user:${userId}:posts`);
await redis.del(...keys, `user:${userId}:posts`);
```

### Cache Stampede Prevention

When cache expires, many requests hit the DB simultaneously:

```js
// Mutex lock — only first request rebuilds, others wait
async function getUserWithLock(id) {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const lock = await redis.set(`lock:user:${id}`, '1', 'NX', 'EX', 5);
  if (!lock) {
    // Another request is rebuilding — wait and retry
    await sleep(100);
    return getUserWithLock(id);
  }

  try {
    const user = await db.query('SELECT * FROM users WHERE id = $1', [id]);
    await redis.setex(`user:${id}`, 300, JSON.stringify(user));
    return user;
  } finally {
    await redis.del(`lock:user:${id}`);
  }
}

// Stale-while-revalidate — serve stale data while refreshing in background
async function getUserSWR(id) {
  const cached = await redis.get(`user:${id}`);
  if (cached) {
    const { data, expiresAt } = JSON.parse(cached);
    if (Date.now() > expiresAt - 30_000) {
      // within 30s of expiry
      refreshInBackground(id); // don't await
    }
    return data;
  }
  return refreshAndCache(id);
}
```

**Always set cache expiry (`TTL`)** — stale data is a bug.

---

## 5. JWT & Refresh Tokens

### JWT Structure

A JWT is a Base64-encoded JSON object: `header.payload.signature`. The signature ensures the token hasn't been tampered with.

```js
// Payload (decoded — NOT encrypted, just signed)
{
  "sub": "user_123",
  "iat": 1716000000,    // issued at
  "exp": 1716003600,    // expires at (1 hour)
  "role": "admin"
}

// Never store sensitive data in JWT payload — it's readable by anyone
```

### Access + Refresh Token Pattern

```js
const ACCESS_TTL = '15m'; // short-lived — minimizes damage if stolen
const REFRESH_TTL = '7d'; // longer-lived — stored securely

function issueTokens(userId, role) {
  const accessToken = jwt.sign({ sub: userId, role }, process.env.JWT_SECRET, {
    expiresIn: ACCESS_TTL,
  });
  const refreshToken = jwt.sign(
    { sub: userId, type: 'refresh', jti: randomUUID() }, // jti = unique ID for revocation
    process.env.JWT_REFRESH_SECRET,
    { expiresIn: REFRESH_TTL },
  );
  return { accessToken, refreshToken };
}

// Store refresh tokens in DB for revocation support
async function saveRefreshToken(userId, token, jti) {
  await db.query('INSERT INTO refresh_tokens (user_id, jti, expires_at) VALUES ($1, $2, $3)', [
    userId,
    jti,
    new Date(Date.now() + 7 * 86400 * 1000),
  ]);
}

// Refresh endpoint
app.post('/auth/refresh', async (req, res) => {
  const { refreshToken } = req.cookies; // stored in HttpOnly cookie
  if (!refreshToken) return res.status(401).json({ error: 'No refresh token' });

  const payload = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
  if (payload.type !== 'refresh') throw new Error('Invalid token type');

  // Check if revoked (password changed, logout, etc.)
  const valid = await db.query('SELECT 1 FROM refresh_tokens WHERE jti = $1 AND revoked_at IS NULL', [payload.jti]);
  if (!valid.rows.length) return res.status(401).json({ error: 'Token revoked' });

  // Rotate: revoke old token, issue new pair
  await db.query('UPDATE refresh_tokens SET revoked_at = NOW() WHERE jti = $1', [payload.jti]);
  const tokens = issueTokens(payload.sub, payload.role);
  await saveRefreshToken(payload.sub, tokens.refreshToken, newJti);

  res.cookie('refreshToken', tokens.refreshToken, { httpOnly: true, secure: true, sameSite: 'Strict' });
  res.json({ accessToken: tokens.accessToken });
});
```

### Force Token Expiry on Password Change

**Always revoke all active tokens when a user changes or resets their password.** A stolen token becomes useless immediately.

```js
async function changePassword(userId, newPassword) {
  const hash = await bcrypt.hash(newPassword, 12);
  await db.query('UPDATE users SET password_hash = $1 WHERE id = $2', [hash, userId]);

  // Revoke ALL refresh tokens for this user
  await db.query('UPDATE refresh_tokens SET revoked_at = NOW() WHERE user_id = $1', [userId]);

  // If using JWT with a per-user secret or version:
  await db.query('UPDATE users SET token_version = token_version + 1 WHERE id = $1', [userId]);
  // Access tokens validate: if payload.version !== user.token_version → reject
}
```

---

## 6. Password Security

### Hashing is NOT enough alone

Plain MD5/SHA hashing is insecure for passwords — attackers use precomputed rainbow tables. Use **adaptive hashing algorithms** specifically designed for passwords: **bcrypt**, **Argon2**, or **scrypt**.

```js
const bcrypt = require('bcrypt');
const argon2 = require('argon2');

// bcrypt — widely used, built-in salt
const SALT_ROUNDS = 12; // higher = slower = more secure (12 is recommended baseline)

async function hashPassword(plain) {
  return bcrypt.hash(plain, SALT_ROUNDS); // generates unique salt automatically
}

async function verifyPassword(plain, hash) {
  return bcrypt.compare(plain, hash); // timing-safe comparison
}

// Argon2 — winner of Password Hashing Competition, recommended for new projects
async function hashPasswordArgon2(plain) {
  return argon2.hash(plain, {
    type: argon2.argon2id, // hybrid mode — best resistance
    memoryCost: 65536, // 64 MB
    timeCost: 3, // iterations
    parallelism: 4,
  });
}

async function verifyArgon2(plain, hash) {
  return argon2.verify(hash, plain);
}
```

### What Hashing Alone Doesn't Cover

- **Credential stuffing** — users reuse passwords from other breached sites → add MFA
- **Weak passwords** — enforce minimum strength, check against known breach databases (Have I Been Pwned API)
- **Timing attacks** — always use constant-time comparison (`bcrypt.compare`, `crypto.timingSafeEqual`)
- **Storing the plaintext anywhere** — never log passwords, never store them unencrypted even temporarily

```js
// Check against known breached passwords
async function isBreachedPassword(password) {
  const { createHash } = require('crypto');
  const sha1 = createHash('sha1').update(password).digest('hex').toUpperCase();
  const prefix = sha1.slice(0, 5);
  const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`);
  const text = await response.text();
  return text.includes(sha1.slice(5));
}
```

---

## 7. Brute Force Protection & Rate Limiting

### Rate Limiting

```js
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');

// All APIs — general protection
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100, store: new RedisStore(...) }));

// Auth endpoints — strict
app.use('/api/auth/login', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  skipSuccessfulRequests: true, // only count failed attempts
  message: { error: 'Too many login attempts' },
}));

// OTP verification — very strict
app.use('/api/auth/verify-otp', rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 5,
}));
```

### Progressive Login Delay

```js
async function login(email, password, ip) {
  const key = `login_attempts:${email}`;
  const attempts = await redis.incr(key);
  await redis.expire(key, 15 * 60); // reset after 15 minutes

  if (attempts > 10) {
    return { error: 'Account temporarily locked. Try again in 15 minutes.' };
  }

  if (attempts > 5) {
    // Exponential delay: 6th=2s, 7th=4s, 8th=8s...
    await sleep(Math.pow(2, attempts - 5) * 1000);
  }

  const user = await db.query('SELECT * FROM users WHERE email = $1', [email]);
  if (!user || !(await bcrypt.compare(password, user.password_hash))) {
    return { error: 'Invalid credentials' };
  }

  await redis.del(key); // reset on successful login
  return { user };
}
```

### Email Enumeration Prevention

**Never confirm whether an email exists** when handling password reset or registration. Always return the same response:

```js
app.post('/api/auth/forgot-password', async (req, res) => {
  const { email } = req.body;
  const user = await db.query('SELECT id FROM users WHERE email = $1', [email]);

  // Send email only if user exists, but ALWAYS return success
  if (user) {
    await sendPasswordResetEmail(user.id, email);
  }

  // Same response regardless of whether email exists — prevents enumeration
  res.json({ message: 'If that email exists, a reset link has been sent.' });
});
```

---

## 8. Load Balancing

A load balancer distributes incoming requests across multiple server instances, preventing any single server from being overwhelmed.

### Algorithms

| Algorithm         | How it works                               | Best for                         |
| ----------------- | ------------------------------------------ | -------------------------------- |
| Round Robin       | Each server in order                       | Equal capacity servers           |
| Least Connections | Server with fewest active connections      | Variable request duration        |
| IP Hash           | Same client → same server                  | Stateful apps (session affinity) |
| Weighted          | Servers get traffic proportional to weight | Mixed capacity servers           |
| Random            | Random selection                           | Stateless, homogeneous servers   |

```nginx
# Nginx load balancer config
upstream api_servers {
  least_conn; # algorithm

  server api1:3000 weight=3;
  server api2:3000 weight=1; # gets 25% of traffic
  server api3:3000 backup;   # only used if others are down

  keepalive 32; # reuse connections to upstream servers
}

server {
  listen 80;
  location /api {
    proxy_pass http://api_servers;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_connect_timeout 5s;
    proxy_read_timeout 30s;
  }
}
```

### Health Checks

Load balancers periodically check if servers are healthy and remove failed ones:

```js
// Health endpoint — check all dependencies
app.get('/health', async (req, res) => {
  const [db, cache] = await Promise.allSettled([pool.query('SELECT 1'), redis.ping()]);
  const healthy = db.status === 'fulfilled' && cache.status === 'fulfilled';
  res.status(healthy ? 200 : 503).json({ healthy, db: db.status, cache: cache.status });
});
```

### Session Affinity vs Stateless

Load balancers work best with **stateless APIs** — any server can handle any request. If you store session state in memory, you need sticky sessions (same client → same server) or — better — move state to Redis:

```js
// Store sessions in Redis — any server can read them
app.use(session({ store: new RedisStore({ client: redis }) }));
```

---

## 9. SQL vs NoSQL

### SQL (Relational)

Structured data with defined schema. ACID transactions. Powerful joins. Scales vertically by default; horizontal sharding is complex.

**Best for:** financial systems, e-commerce orders, any domain with complex relationships and strict consistency requirements.

```sql
-- Strong consistency: all or nothing
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

### NoSQL

Flexible schema, horizontal scaling built-in. Trade consistency for availability/partition tolerance. Many types:

| Type        | Examples           | Best for                           |
| ----------- | ------------------ | ---------------------------------- |
| Document    | MongoDB, Firestore | User profiles, CMS, catalogs       |
| Key-Value   | Redis, DynamoDB    | Sessions, caching, leaderboards    |
| Wide-column | Cassandra, HBase   | Time-series, IoT, write-heavy logs |
| Graph       | Neo4j, Neptune     | Social networks, recommendations   |

### Decision Guide

| Factor         | Choose SQL               | Choose NoSQL                    |
| -------------- | ------------------------ | ------------------------------- |
| Schema         | Fixed, well-defined      | Flexible, evolving              |
| Relationships  | Complex joins needed     | Minimal joins                   |
| Consistency    | ACID required            | Eventual consistency acceptable |
| Scale          | Moderate, vertical       | Massive, horizontal             |
| Query patterns | Ad-hoc queries           | Known access patterns           |
| Transactions   | Multi-table transactions | Single-document operations      |

**Practical rule:** Start with PostgreSQL unless you have a specific reason for NoSQL. PostgreSQL supports JSON, full-text search, and scales well enough for most applications.

---

## 10. REST vs WebSockets vs Data Formats

### When to Use WebSockets

| Use REST when            | Use WebSockets when                     |
| ------------------------ | --------------------------------------- |
| Request/response model   | Bidirectional, real-time updates        |
| Cacheable responses      | Server needs to push data               |
| Stateless operations     | Low-latency chat, gaming, collaboration |
| CRUD operations          | Live dashboards, notifications          |
| Client polls for updates | Many updates per second                 |

```js
// REST — client pulls data
const response = await fetch('/api/notifications'); // client initiates

// WebSocket — server pushes data
const ws = new WebSocket('wss://api.example.com/ws');
ws.onmessage = (e) => displayNotification(JSON.parse(e.data)); // server initiates
```

**Server-Sent Events (SSE)** — a middle ground: server pushes, client listens, but only server → client:

```js
app.get('/api/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const interval = setInterval(() => {
    res.write(`data: ${JSON.stringify({ time: Date.now() })}\n\n`);
  }, 1000);

  req.on('close', () => clearInterval(interval));
});

// Client
const events = new EventSource('/api/events');
events.onmessage = (e) => console.log(JSON.parse(e.data));
```

### JSON vs XML

|                   | JSON                        | XML                            |
| ----------------- | --------------------------- | ------------------------------ |
| Verbosity         | Compact                     | Verbose                        |
| Parsing           | Native in JS/most languages | Requires parser                |
| Data types        | Supports arrays, null       | Everything is a string/element |
| Schema validation | JSON Schema                 | XSD, DTD                       |
| Use today         | Universal for REST APIs     | Legacy systems, SOAP, RSS/Atom |

**Use JSON for all new APIs.** XML is only relevant when integrating with legacy systems that require it (banks, government APIs, SOAP services).

---

## 11. Code Architecture — Modular vs Monolithic Files

**Never put all code in one file.** Separate concerns into layers.

```
src/
├── controllers/     ← HTTP layer: parse request, validate, call service, return response
│   └── users.controller.ts
├── services/        ← Business logic: the "what" of the application
│   └── users.service.ts
├── repositories/    ← Data access: all DB queries live here
│   └── users.repository.ts
├── middlewares/     ← Cross-cutting: auth, logging, validation, rate limiting
│   ├── auth.middleware.ts
│   └── validate.middleware.ts
├── models/          ← DB models / entities
│   └── user.model.ts
├── dtos/            ← Input/output shapes and validation schemas
│   └── create-user.dto.ts
├── utils/           ← Pure helper functions (no side effects)
├── config/          ← Environment config, constants
└── integrations/    ← Third-party API clients (see Section 19)
    └── stripe/
        └── stripe.client.ts
```

**Why this matters for scalability:**

- Each layer can be tested independently
- Business logic doesn't depend on Express — you can swap frameworks
- Repository pattern means you can swap databases without touching services
- New developers understand where things go

---

## 12. Error Handling

### Centralized Error Handling

```js
// Custom error classes
class AppError extends Error {
  constructor(message, statusCode, code) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true; // expected error — don't crash
  }
}

class NotFoundError extends AppError {
  constructor(resource) {
    super(`${resource} not found`, 404, 'NOT_FOUND');
  }
}

class ValidationError extends AppError {
  constructor(field, message) {
    super(message, 400, 'VALIDATION_ERROR');
    this.field = field;
  }
}

class UnauthorizedError extends AppError {
  constructor() {
    super('Unauthorized', 401, 'UNAUTHORIZED');
  }
}

// Global error handler (Express)
app.use((err, req, res, next) => {
  const requestId = req.headers['x-request-id'];

  // Log all errors
  logger.error({ err, requestId, url: req.url, method: req.method });

  if (err.isOperational) {
    // Known, expected error — safe to expose message
    return res.status(err.statusCode).json({
      error: { code: err.code, message: err.message, requestId },
    });
  }

  // Unknown error — don't expose internals
  res.status(500).json({
    error: { code: 'INTERNAL_ERROR', message: 'Something went wrong', requestId },
  });
});

// Unhandled rejections — catch async errors that escaped try/catch
process.on('unhandledRejection', (reason) => {
  logger.error({ reason }, 'Unhandled rejection');
  process.exit(1); // let process manager restart
});
```

### Error Handling and UX

Good error responses help frontend show meaningful messages:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is invalid",
    "field": "email",
    "requestId": "req_abc123"
  }
}
```

- `code` — machine-readable for frontend to show the right UI
- `message` — human-readable for display
- `requestId` — correlation ID for debugging (user can report it)
- Never expose stack traces, SQL errors, or internal paths in production

---

## 13. Microservices vs Monolithic Architecture

### Monolith First

A monolith deploys as a single unit. Simpler to develop, test, and debug. Start here.

```
Monolith: one codebase → one deployment → one DB
Pros: simple, fast development, easy debugging, single transaction boundary
Cons: as it grows — slow deploys, hard to scale individual parts, tech stack locked in
```

### Microservices

Split by business domain. Each service owns its data and deploys independently.

```
Order Service  → orders DB
User Service   → users DB
Payment Service → payments DB

Pros: independent deployments, teams can choose their stack, scale individual services
Cons: distributed system complexity, network latency, eventual consistency, harder debugging
```

### When to Split

Don't split prematurely. Good signals that a service should be extracted:

- The component needs to scale independently (e.g., image processing is CPU-heavy)
- The component is owned by a separate team
- The component has a genuinely different technology requirement
- The monolith's deploy time is impacting team velocity

**The Strangler Fig pattern** — gradually extract services from a monolith without a big-bang rewrite:

```
Phase 1: Route /api/payments through a proxy → monolith handles it
Phase 2: New Payment Service deployed → proxy routes /api/payments to it
Phase 3: Remove payment code from monolith
```

### Microservice Communication

```js
// Synchronous — HTTP/gRPC for real-time needs
const user = await fetch('http://user-service/users/' + userId).then((r) => r.json());

// Asynchronous — message queue for decoupled operations
await queue.publish('order.placed', { orderId, userId, items });
// Email service subscribes and sends confirmation asynchronously

// Service discovery with Consul or Kubernetes DNS
const USER_SERVICE = process.env.USER_SERVICE_URL || 'http://user-service:3001';
```

---

## 14. Message Queues

Message queues decouple services — the producer sends a message and continues without waiting for the consumer. Essential for reliability and scalability.

### When to Use

- **Email/notification sending** — don't block the API response
- **Image processing** — CPU-heavy, process asynchronously
- **Cross-service communication** — order placed → inventory, billing, email all react
- **Traffic spike buffering** — queue absorbs bursts, consumers process at sustainable rate
- **Guaranteed delivery** — retries until consumer acknowledges

### RabbitMQ

```js
const amqp = require('amqplib');

// Producer
async function publishEvent(exchange, event, data) {
  const conn = await amqp.connect(process.env.RABBITMQ_URL);
  const channel = await conn.createChannel();
  await channel.assertExchange(exchange, 'topic', { durable: true });
  channel.publish(exchange, event, Buffer.from(JSON.stringify(data)), {
    persistent: true, // survive broker restart
  });
  await channel.close();
  await conn.close();
}

await publishEvent('orders', 'order.placed', { orderId: 123 });

// Consumer
async function consumeOrders() {
  const conn = await amqp.connect(process.env.RABBITMQ_URL);
  const channel = await conn.createChannel();
  await channel.assertQueue('email-notifications', { durable: true });
  channel.prefetch(1); // process one message at a time

  channel.consume('email-notifications', async (msg) => {
    const data = JSON.parse(msg.content);
    try {
      await sendOrderConfirmation(data.orderId);
      channel.ack(msg); // acknowledge — message removed from queue
    } catch (err) {
      channel.nack(msg, false, true); // negative ack — requeue for retry
    }
  });
}
```

### Kafka

Kafka is a distributed log — messages are retained and consumers can replay from any offset. Better for high throughput and event sourcing.

```js
const { Kafka } = require('kafkajs');

const kafka = new Kafka({ brokers: [process.env.KAFKA_BROKER] });
const producer = kafka.producer();
const consumer = kafka.consumer({ groupId: 'notification-service' });

// Produce
await producer.connect();
await producer.send({
  topic: 'order-events',
  messages: [{ key: String(orderId), value: JSON.stringify({ type: 'ORDER_PLACED', orderId }) }],
});

// Consume
await consumer.connect();
await consumer.subscribe({ topic: 'order-events', fromBeginning: false });
await consumer.run({
  eachMessage: async ({ message }) => {
    const event = JSON.parse(message.value.toString());
    await handleEvent(event);
  },
});
```

|            | RabbitMQ                  | Kafka                              |
| ---------- | ------------------------- | ---------------------------------- |
| Model      | Message broker (push)     | Distributed log (pull)             |
| Retention  | Message deleted after ack | Retained for configurable period   |
| Throughput | Moderate                  | Very high (millions/sec)           |
| Use case   | Task queues, RPC          | Event streaming, audit log, replay |

---

# Part 2: Security Checklist

---

## 15. Auth & OTP Security

### ✅ Force Token Expiry on Password Change/Reset

When a user changes or resets their password, invalidate all existing tokens immediately. A stolen token becomes useless.

```js
// Bump token version — all tokens with old version are rejected
await db.query('UPDATE users SET token_version = token_version + 1 WHERE id = $1', [userId]);

// In JWT middleware
const user = await db.query('SELECT token_version FROM users WHERE id = $1', [payload.sub]);
if (payload.version !== user.token_version) throw new UnauthorizedError();
```

### ✅ OTP Expiry on New Request

When a user requests a new OTP, expire the previous one immediately:

```js
async function requestOTP(userId) {
  // Expire all existing OTPs for this user
  await db.query('UPDATE otps SET expires_at = NOW() WHERE user_id = $1 AND used = false', [userId]);

  const otp = generateOTP();
  await db.query("INSERT INTO otps (user_id, code, expires_at) VALUES ($1, $2, NOW() + INTERVAL '5 minutes')", [
    userId,
    otp,
  ]);
  await sendOTP(userId, otp);
}
```

### ✅ OTP Column Must Be `CHAR`, Not `INT`

If your OTP is `123456` it's fine, but if it's `012345`, an `INT` column silently drops the leading zero → stored as `12345` → verification always fails.

```sql
-- WRONG
otp_code INT

-- CORRECT
otp_code CHAR(6) NOT NULL
-- Or VARCHAR(6) if length varies
```

### ✅ OTP Verification Must Be Authenticated

The OTP verification API should require a short-lived token tied to the OTP request — not just the OTP code alone. Otherwise anyone who guesses the OTP can verify any account.

```js
// On OTP request — issue a verification token
async function requestOTP(userId) {
  const verificationToken = randomUUID();
  await db.query(
    "INSERT INTO otps (user_id, code, verification_token, expires_at) VALUES ($1, $2, $3, NOW() + INTERVAL '5 minutes')",
    [userId, generateOTP(), verificationToken],
  );
  return verificationToken; // returned to client, stored in session/cookie
}

// On OTP verify — require BOTH the code AND the verification token
async function verifyOTP(verificationToken, code) {
  const otp = await db.query(
    'SELECT * FROM otps WHERE verification_token = $1 AND code = $2 AND expires_at > NOW() AND used = false',
    [verificationToken, code],
  );
  if (!otp) throw new UnauthorizedError();
  await db.query('UPDATE otps SET used = true WHERE id = $1', [otp.id]);
}
```

### ✅ Notification Deduplication

For social features like likes/comments, don't create a new notification per event. Update the existing one:

```js
// Instead of inserting a new notification for every like
// Find existing unread notification of the same type and update it
async function notifyLike(postOwnerId, actorId, postId) {
  const existing = await db.query(
    `SELECT id, actor_ids FROM notifications
     WHERE user_id = $1 AND post_id = $2 AND type = 'like' AND read = false`,
    [postOwnerId, postId],
  );

  if (existing) {
    // Add actor to list and re-send
    const actors = [...new Set([...existing.actor_ids, actorId])];
    await db.query('UPDATE notifications SET actor_ids = $1, updated_at = NOW() WHERE id = $2', [actors, existing.id]);
  } else {
    await db.query('INSERT INTO notifications (user_id, post_id, type, actor_ids) VALUES ($1, $2, $3, $4)', [
      postOwnerId,
      postId,
      'like',
      [actorId],
    ]);
  }
}
```

### ✅ Use UUIDs (or ULIDs) for IDs

Sequential integer IDs expose information: `GET /orders/1` reveals this is the first order. Attackers can enumerate all resources.

```sql
-- UUID — random, unpredictable
id UUID DEFAULT gen_random_uuid() PRIMARY KEY

-- ULID — sortable (time-ordered), URL-safe, avoids UUID index fragmentation
-- Better performance on large tables due to sequential writes
id TEXT DEFAULT generate_ulid() PRIMARY KEY
```

### ✅ Select for Update for Concurrent Modifications

When multiple requests might update the same row simultaneously, use `SELECT FOR UPDATE` to lock the row and prevent race conditions:

```js
async function deductBalance(userId, amount) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const {
      rows: [account],
    } = await client.query(
      'SELECT balance FROM accounts WHERE user_id = $1 FOR UPDATE', // lock this row
      [userId],
    );

    if (account.balance < amount) throw new Error('Insufficient balance');

    await client.query('UPDATE accounts SET balance = balance - $1 WHERE user_id = $2', [amount, userId]);
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}
```

---

## 16. Input & Upload Security

### ✅ Max Input Length on All Inputs

Without limits, an attacker can send a 1GB string to cause memory exhaustion or crash:

```js
// Express — limit JSON body size
app.use(express.json({ limit: '10kb' }));
app.use(express.urlencoded({ limit: '10kb', extended: true }));

// Per-field validation
const schema = z.object({
  name: z.string().max(100),
  bio: z.string().max(500),
  email: z.string().email().max(254),
  message: z.string().max(2000),
});
```

### ✅ File Upload Security

```js
const multer = require('multer');
const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

const upload = multer({
  storage: multer.memoryStorage(), // buffer in memory, upload to S3 — never write to disk on server
  limits: { fileSize: MAX_SIZE, files: 5 },
  fileFilter: (req, file, cb) => {
    // Check MIME type
    if (!ALLOWED_TYPES.includes(file.mimetype)) {
      return cb(new ValidationError('file', 'File type not allowed'));
    }
    cb(null, true);
  },
});

async function uploadFile(file) {
  // Check file extension too — mimetype can be spoofed in the header
  const ext = path.extname(file.originalname).toLowerCase();
  if (!['.jpg', '.jpeg', '.png', '.webp', '.pdf'].includes(ext)) {
    throw new ValidationError('file', 'Invalid file extension');
  }

  // Scan for malware — never scan ON the server, use a service
  // await clamav.scan(file.buffer); ← runs on server — bad
  // Use: VirusTotal API, ClamAV on a separate scanning service, or S3 + Lambda

  // Store on S3/R2, never on the application server's disk
  const key = `uploads/${randomUUID()}${ext}`;
  await s3.send(
    new PutObjectCommand({
      Bucket: process.env.S3_BUCKET,
      Key: key,
      Body: file.buffer,
      ContentType: file.mimetype,
    }),
  );

  return `https://${process.env.CDN_DOMAIN}/${key}`;
}
```

### ✅ Max Rows for CSV/Excel Uploads

```js
const csv = require('csv-parser');

const MAX_ROWS = 10_000;

async function parseCSV(buffer) {
  return new Promise((resolve, reject) => {
    const rows = [];
    const stream = Readable.from(buffer.toString());

    stream
      .pipe(csv())
      .on('data', (row) => {
        if (rows.length >= MAX_ROWS) {
          stream.destroy(new ValidationError('file', `Max ${MAX_ROWS} rows allowed`));
          return;
        }
        rows.push(row);
      })
      .on('end', () => resolve(rows))
      .on('error', reject);
  });
}
```

---

## 17. API & Logging Security

### ✅ Never Pass Tokens in URL Parameters

If a token is in the URL, it appears in:

- Server access logs
- Browser history
- Referrer headers to third-party sites
- Network sniffing

```js
// BAD
GET /reset-password?token=abc123
GET /webhooks/callback?api_key=secret

// GOOD — tokens in headers or request body (POST)
POST /reset-password
Authorization: Bearer abc123
// or
{ "token": "abc123" }

// GOOD — for webhooks, validate a signature instead
const sig = crypto
  .createHmac('sha256', process.env.WEBHOOK_SECRET)
  .update(rawBody)
  .digest('hex');
if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(req.headers['x-signature']))) {
  throw new UnauthorizedError();
}
```

### ✅ Never Log Sensitive Data

```js
const logger = pino({
  redact: ['req.headers.authorization', 'req.headers.cookie', 'body.password', 'body.creditCard', 'body.ssn'],
});

// Manual sanitization
function sanitizeForLog(obj) {
  const SENSITIVE = ['password', 'token', 'secret', 'creditCard', 'ssn'];
  return JSON.parse(JSON.stringify(obj, (key, val) => (SENSITIVE.includes(key.toLowerCase()) ? '[REDACTED]' : val)));
}
```

### ✅ Use Sentry for Exception Monitoring

```js
const Sentry = require('@sentry/node');

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1, // 10% of requests for performance tracing
});

// Capture errors
app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.errorHandler()); // must be before your error handler

// Add user context
Sentry.setUser({ id: req.user.id, email: req.user.email });
```

### ✅ Low-Level Logging / Request Journey

Log at each significant decision point so you can reconstruct what happened during a bug:

```js
async function processPayment(orderId, userId, amount) {
  logger.info({ orderId, userId, amount }, 'Payment processing started');

  const order = await getOrder(orderId);
  if (!order) {
    logger.warn({ orderId }, 'Payment failed: order not found');
    throw new NotFoundError('Order');
  }

  logger.info({ orderId, condition: 'order_found', status: order.status }, 'Order retrieved');

  if (order.status !== 'pending') {
    logger.warn({ orderId, status: order.status }, 'Payment failed: order not in pending state');
    throw new ValidationError('order', 'Order is not in pending state');
  }

  const result = await chargeCard(userId, amount);
  logger.info({ orderId, chargeId: result.id }, 'Card charged successfully');

  await updateOrderStatus(orderId, 'paid');
  logger.info({ orderId }, 'Payment processing complete');
}
```

---

# Part 3: API Design Best Practices

---

## 18. Time Zones & Data Handling

### Always Store UTC, Display in User's Time Zone

```js
// Store — always UTC
await db.query(
  'INSERT INTO events (title, starts_at) VALUES ($1, $2)',
  [title, new Date(isoString)], // JS Date is always UTC internally
);

// Retrieve and convert for the user
const {
  rows: [event],
} = await db.query('SELECT * FROM events WHERE id = $1', [id]);

// Convert to user's time zone
const { formatInTimeZone } = require('date-fns-tz');
const localTime = formatInTimeZone(event.starts_at, userTimezone, 'yyyy-MM-dd HH:mm:ss');

// Or return UTC and let frontend handle display
res.json({ ...event, starts_at: event.starts_at.toISOString() });
```

```sql
-- PostgreSQL: store as TIMESTAMPTZ (includes time zone awareness)
-- It stores UTC internally and can convert on query
CREATE TABLE events (
  starts_at TIMESTAMPTZ NOT NULL
);

-- Query in a specific timezone
SELECT starts_at AT TIME ZONE 'Africa/Cairo' AS local_time FROM events;
```

---

## 19. Third-Party Integrations

### ✅ Integration Checklist

```js
// integrations/stripe/stripe.client.ts — isolated module
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2023-10-16',
  timeout: 10_000, // 10 second timeout — always set one
  maxNetworkRetries: 2, // built-in retry for network errors
});

export async function chargeCustomer(customerId: string, amount: number, currency: string) {
  let response;
  try {
    response = await stripe.paymentIntents.create({
      amount,
      currency,
      customer: customerId,
    });
  } catch (err) {
    if (err instanceof Stripe.errors.StripeConnectionError) {
      // handle timeout/connection drop
      throw new ServiceUnavailableError('Payment service unavailable');
    }
    throw err;
  }

  // Validate response shape before using it
  if (!response?.id || !response?.status) {
    // Provider changed their response — alert immediately
    logger.error({ response }, 'Unexpected Stripe response shape');
    Sentry.captureException(new Error('Stripe response schema changed'));
    throw new Error('Unexpected payment provider response');
  }

  // Check it's JSON (for providers that sometimes return HTML error pages)
  // fetch: always check res.ok and Content-Type before res.json()

  return response;
}
```

**Checklist for every third-party integration:**

- Store credentials in env vars / secrets manager — never in code
- Isolated module/class — business logic never calls provider APIs directly
- Always set `timeout` — a provider outage shouldn't hang your server forever
- Handle connection drops and retry (with exponential backoff)
- Validate response shape before accessing keys — alert if it changes
- Open one session/connection per request lifecycle (connection pooling)

---

## 20. HTTP Methods, Pagination & Sensitive Data

### ✅ Use the Correct HTTP Method

```
GET    /api/users         → list users (no side effects, safe to cache)
GET    /api/users/123     → get user by id
POST   /api/users         → create new user
PUT    /api/users/123     → replace user entirely (full update)
PATCH  /api/users/123     → partial update (only provided fields)
DELETE /api/users/123     → delete user
```

### ✅ Always Paginate

```js
// Even if you only have 10 records today — you'll have 10 million tomorrow
app.get('/api/users', async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 20, 100);
  const cursor = req.query.cursor;

  const users = await db.query(
    `SELECT id, name, email FROM users
     WHERE ($1::uuid IS NULL OR id > $1)
     ORDER BY id LIMIT $2`,
    [cursor || null, limit + 1],
  );

  const hasMore = users.length > limit;
  const data = hasMore ? users.slice(0, limit) : users;

  res.json({
    data,
    nextCursor: hasMore ? data.at(-1).id : null,
    hasMore,
  });
});
```

### ✅ Encrypt Sensitive Data Before Storing

```js
const { createCipheriv, createDecipheriv, randomBytes } = require('crypto');

const ALGORITHM = 'aes-256-gcm';
const KEY = Buffer.from(process.env.ENCRYPTION_KEY, 'hex'); // 32 bytes

function encrypt(text) {
  const iv = randomBytes(16);
  const cipher = createCipheriv(ALGORITHM, KEY, iv);
  const encrypted = Buffer.concat([cipher.update(text, 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();
  return `${iv.toString('hex')}:${encrypted.toString('hex')}:${tag.toString('hex')}`;
}

function decrypt(stored) {
  const [ivHex, encHex, tagHex] = stored.split(':');
  const decipher = createDecipheriv(ALGORITHM, KEY, Buffer.from(ivHex, 'hex'));
  decipher.setAuthTag(Buffer.from(tagHex, 'hex'));
  return decipher.update(Buffer.from(encHex, 'hex')) + decipher.final('utf8');
}

// Store encrypted sensitive data
await db.query('INSERT INTO payment_methods (user_id, card_last4, card_token_encrypted) VALUES ($1, $2, $3)', [
  userId,
  last4,
  encrypt(cardToken),
]);
```

---

# Part 4: Reliability Patterns

---

## 21. Rate Limiter

Rate limiting ensures no single consumer can overwhelm your service, maintains fair access across consumers, and extends service availability.

```js
const { RateLimiterRedis } = require('rate-limiter-flexible');

const rateLimiter = new RateLimiterRedis({
  storeClient: redisClient,
  keyPrefix: 'rl',
  points: 100, // requests allowed
  duration: 60, // per 60 seconds
  blockDuration: 60, // block for 60s if exceeded
});

async function rateLimitMiddleware(req, res, next) {
  try {
    const key = req.user?.id ?? req.ip; // per-user if authenticated, per-IP otherwise
    await rateLimiter.consume(key);
    next();
  } catch (err) {
    res.status(429).json({
      error: 'Too many requests',
      retryAfter: Math.ceil(err.msBeforeNext / 1000),
    });
  }
}
```

### Distributed Rate Limiting

In a cluster, rate limits must be enforced across all instances — use Redis (shared state), not in-process counters.

```js
// Token bucket algorithm — allows brief bursts
const limiter = new RateLimiterRedis({
  storeClient: redis,
  points: 10, // burst capacity
  duration: 1, // refill 10 tokens per second
  execEvenly: true, // smooth out requests
});
```

---

## 22. Idempotency

An idempotent request produces the same result whether executed once or many times. Critical for payment processing, order creation, and any state-changing operation.

**Problem:** client sends a POST to create an order. Network fails before getting response. Client retries. Two orders created.

```js
// Client sends a unique idempotency key with every state-changing request
const idempotencyKey = crypto.randomUUID(); // generated client-side, stored locally
await fetch('/api/orders', {
  method: 'POST',
  headers: { 'Idempotency-Key': idempotencyKey },
  body: JSON.stringify(orderData),
});

// Server stores results by idempotency key
app.post('/api/orders', async (req, res) => {
  const key = req.headers['idempotency-key'];
  if (!key) return res.status(400).json({ error: 'Idempotency-Key header required' });

  // Check if we've already processed this request
  const cached = await redis.get(`idem:${key}`);
  if (cached) {
    return res.status(200).json(JSON.parse(cached)); // return stored result
  }

  // Lock to prevent race condition (two concurrent requests with same key)
  const lock = await redis.set(`idem_lock:${key}`, '1', 'NX', 'EX', 30);
  if (!lock) return res.status(409).json({ error: 'Request in progress' });

  try {
    const order = await createOrder(req.body);

    // Store result with TTL
    await redis.setex(`idem:${key}`, 86400, JSON.stringify(order)); // keep 24h
    res.status(201).json(order);
  } catch (err) {
    await redis.del(`idem_lock:${key}`);
    throw err;
  }
});
```

---

## 23. Request Timeout

Every outbound request must have a timeout. Without it, a slow dependency can hold connections open indefinitely, exhausting your connection pool and bringing down your service.

```js
// fetch with AbortController timeout
async function fetchWithTimeout(url, options = {}, timeoutMs = 5000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    return response;
  } catch (err) {
    if (err.name === 'AbortError') {
      logger.warn({ url, timeoutMs }, 'Request timed out');
      throw new ServiceUnavailableError(`Request to ${url} timed out after ${timeoutMs}ms`);
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

// axios timeout
const axios = require('axios');
const client = axios.create({ timeout: 5000 });

// Kill a request that vastly exceeds its budget — free server resources
// Log it — slow requests are signals of a problem to investigate
app.use((req, res, next) => {
  const HARD_LIMIT = 30_000; // 30s absolute max
  const timer = setTimeout(() => {
    if (!res.headersSent) {
      logger.error({ url: req.url, duration: HARD_LIMIT }, 'Request killed — exceeded hard limit');
      res.status(503).json({ error: 'Request timeout' });
    }
  }, HARD_LIMIT);
  res.on('finish', () => clearTimeout(timer));
  next();
});
```

---

## 24. Outbox Pattern

Ensures a message is reliably delivered even if the broker is temporarily unavailable. Solves the dual-write problem: writing to DB and publishing to a queue in the same atomic operation.

**Problem:** update DB → publish event → DB succeeds but queue fails → event lost forever.

```js
// Outbox table — messages stored alongside business data in same transaction
await db.query('BEGIN');
await db.query('INSERT INTO orders (id, user_id, total) VALUES ($1, $2, $3)', [orderId, userId, total]);
await db.query(
  'INSERT INTO outbox (id, aggregate_type, aggregate_id, event_type, payload, created_at) VALUES ($1, $2, $3, $4, $5, NOW())',
  [randomUUID(), 'Order', orderId, 'ORDER_PLACED', JSON.stringify({ orderId, userId, total })],
);
await db.query('COMMIT'); // DB write + outbox write are atomic

// Background job — reads outbox and publishes to queue
async function processOutbox() {
  const { rows: messages } = await db.query(
    'SELECT * FROM outbox WHERE published_at IS NULL ORDER BY created_at LIMIT 100 FOR UPDATE SKIP LOCKED',
  );

  for (const msg of messages) {
    try {
      await queue.publish(msg.event_type, msg.payload);
      await db.query('UPDATE outbox SET published_at = NOW() WHERE id = $1', [msg.id]);
    } catch (err) {
      logger.error({ msgId: msg.id, err }, 'Failed to publish outbox message');
      // Leave it — will be retried on next run
    }
  }
}

// Run every 5 seconds
setInterval(processOutbox, 5000);
```

---

## 25. Retry Pattern

Transient failures (network hiccup, brief overload) should be retried automatically before reporting failure. Use **exponential backoff with jitter** to avoid thundering herd.

```js
async function retryWithBackoff(fn, options = {}) {
  const {
    maxAttempts = 3,
    baseDelayMs = 500,
    maxDelayMs = 10_000,
    shouldRetry = (err) => err.code === 'ECONNRESET' || err.statusCode >= 500,
  } = options;

  let lastError;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;

      if (attempt === maxAttempts || !shouldRetry(err)) {
        throw err;
      }

      // Exponential backoff: 500ms, 1000ms, 2000ms...
      // + jitter: random 0-500ms — prevents all retries firing simultaneously
      const delay = Math.min(baseDelayMs * 2 ** (attempt - 1), maxDelayMs) + Math.random() * 500;

      logger.warn({ attempt, delay, error: err.message }, 'Retrying after failure');
      await sleep(delay);
    }
  }

  throw lastError;
}

// Usage
const user = await retryWithBackoff(() => fetchFromUserService(userId));
```

---

## 26. Circuit Breaker

Without a circuit breaker: 10 requests × 30s timeout = 5 minutes of wasted resources to reach the same conclusion that a service is down.

**States:**

- **Closed** — normal operation, requests flow through
- **Open** — service is down, requests fail immediately (no timeouts wasted)
- **Half-Open** — after recovery timeout, allow one probe request; if it succeeds, close the circuit

```js
class CircuitBreaker {
  constructor(fn, options = {}) {
    this.fn = fn;
    this.failureThreshold = options.failureThreshold ?? 5;
    this.recoveryTimeout = options.recoveryTimeout ?? 30_000;
    this.state = 'closed';
    this.failures = 0;
    this.lastFailureTime = null;
  }

  async call(...args) {
    if (this.state === 'open') {
      const elapsed = Date.now() - this.lastFailureTime;
      if (elapsed < this.recoveryTimeout) {
        throw new Error('Circuit open — service unavailable');
      }
      // Recovery timeout passed — try half-open
      this.state = 'half-open';
    }

    try {
      const result = await this.fn(...args);
      this.#onSuccess();
      return result;
    } catch (err) {
      this.#onFailure();
      throw err;
    }
  }

  #onSuccess() {
    this.failures = 0;
    this.state = 'closed';
  }

  #onFailure() {
    this.failures++;
    this.lastFailureTime = Date.now();
    if (this.failures >= this.failureThreshold) {
      this.state = 'open';
      logger.error({ failures: this.failures }, 'Circuit breaker opened');
    }
  }
}

// Usage
const userServiceBreaker = new CircuitBreaker((id) => fetch(`http://user-service/users/${id}`).then((r) => r.json()), {
  failureThreshold: 5,
  recoveryTimeout: 30_000,
});

const user = await userServiceBreaker.call(userId);
// If user-service is down: fails fast after 5 failures — no 30s timeout waits
```

---

# Part 5: Advanced Topics

---

## 27. Scaling Strategies

### Vertical vs Horizontal Scaling

|            | Vertical (Scale Up)           | Horizontal (Scale Out)                   |
| ---------- | ----------------------------- | ---------------------------------------- |
| Method     | Bigger machine (more CPU/RAM) | More machines                            |
| Complexity | Simple                        | Requires load balancer, stateless design |
| Limit      | Physical hardware limit       | Almost unlimited                         |
| Cost       | Expensive at high end         | More flexible                            |
| Failure    | Single point of failure       | Redundant                                |

**Stateless design is the prerequisite for horizontal scaling** — sessions in Redis, no local file storage, shared cache.

### Database Scaling

```
Vertical → Read Replicas → Sharding → Distributed DB

Read replicas: separate read/write workloads
  - primary handles writes
  - replicas handle reads (possibly slightly stale)

Sharding: partition data across multiple DBs by key (user_id % n)
  - very complex — avoid until necessary
  - PlanetScale, Vitess, Citus handle this automatically

Connection pooling: PgBouncer pools connections at the DB level
  - allows thousands of app connections with a fixed number of DB connections
```

---

## 28. CAP Theorem & Consistency Models

**CAP Theorem:** In a distributed system, you can only guarantee two of three:

- **Consistency** — every read returns the most recent write
- **Availability** — every request gets a response (not necessarily the latest data)
- **Partition Tolerance** — system works even if network between nodes fails

In practice, partition tolerance is required in any distributed system — so the real tradeoff is **CP vs AP**:

|                           | CP (Consistency + Partition)   | AP (Availability + Partition)       |
| ------------------------- | ------------------------------ | ----------------------------------- |
| Behavior during partition | Refuses to serve stale data    | Serves potentially stale data       |
| Examples                  | PostgreSQL, HBase, Zookeeper   | DynamoDB, Cassandra, CouchDB        |
| Use when                  | Correctness critical (finance) | Availability critical (social feed) |

### Eventual Consistency

Most distributed systems choose AP — the system will **eventually** converge to a consistent state, but reads may return stale data temporarily.

```js
// Example: counter that's eventually consistent
// Each node increments locally, CRDT merges later
// Reads may return slightly stale count — acceptable for a "likes" counter
// NOT acceptable for a bank balance — use strong consistency there
```

---

## 29. Database Internals

### Transactions & ACID

```js
// Wrap related operations in a transaction — all succeed or all fail
async function transferFunds(fromId, toId, amount) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query('UPDATE accounts SET balance = balance - $1 WHERE id = $2 AND balance >= $1', [amount, fromId]);
    if (result.rowCount === 0) throw new Error('Insufficient funds');
    await client.query('UPDATE accounts SET balance = balance + $1 WHERE id = $2', [amount, toId]);
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}
```

### N+1 Problem

```js
// N+1: 1 query + N queries = terrible performance
const posts = await db.query('SELECT * FROM posts'); // 1 query
for (const post of posts) {
  post.author = await db.query('SELECT * FROM users WHERE id = $1', [post.user_id]); // N queries
}

// Fix 1: JOIN
const posts = await db.query(`
  SELECT p.*, u.name AS author_name FROM posts p
  JOIN users u ON u.id = p.user_id
`);

// Fix 2: batch load (DataLoader pattern — useful in GraphQL)
const authorIds = [...new Set(posts.map((p) => p.user_id))];
const authors = await db.query('SELECT * FROM users WHERE id = ANY($1)', [authorIds]);
const authorsMap = Object.fromEntries(authors.map((a) => [a.id, a]));
posts.forEach((p) => {
  p.author = authorsMap[p.user_id];
});
```

---

## 30. Observability

### Three Pillars

| Pillar      | Purpose                          | Tools                         |
| ----------- | -------------------------------- | ----------------------------- |
| **Logs**    | What happened                    | Pino, Winston, CloudWatch     |
| **Metrics** | How is the system performing     | Prometheus + Grafana, Datadog |
| **Traces**  | Where did the request spend time | OpenTelemetry, Jaeger, Zipkin |

```js
// Structured logging with correlation ID
const { AsyncLocalStorage } = require('async_hooks');
const storage = new AsyncLocalStorage();

app.use((req, res, next) => {
  const requestId = req.headers['x-request-id'] ?? randomUUID();
  res.setHeader('x-request-id', requestId);
  storage.run({ requestId, userId: req.user?.id }, next);
});

const logger = {
  info: (msg, data = {}) => {
    const ctx = storage.getStore() ?? {};
    console.log(JSON.stringify({ level: 'info', msg, ...ctx, ...data, ts: Date.now() }));
  },
};

// Key metrics to track
const requestDuration = new Histogram({ name: 'http_request_duration_seconds', ... });
const activeConnections = new Gauge({ name: 'db_pool_active_connections', ... });
const queueDepth = new Gauge({ name: 'queue_depth', ... });
const errorRate = new Counter({ name: 'http_errors_total', labelNames: ['code'] });
```

---

## 31. API Versioning

Version APIs from day one — changing a public API without versioning breaks clients.

```js
// URL versioning (most common, most explicit)
app.use('/api/v1', v1Router);
app.use('/api/v2', v2Router);

// Header versioning (cleaner URLs, harder to test in browser)
app.use((req, res, next) => {
  req.apiVersion = req.headers['api-version'] ?? 'v1';
  next();
});

// Deprecation headers — warn clients before removing old versions
app.use('/api/v1', (req, res, next) => {
  res.setHeader('Deprecation', 'true');
  res.setHeader('Sunset', 'Sat, 01 Jan 2026 00:00:00 GMT');
  res.setHeader('Link', '</api/v2>; rel="successor-version"');
  next();
});
```

**Semantic versioning for APIs:**

- **Major** (`v1` → `v2`) — breaking changes (removed fields, changed types)
- **Minor/patch** — additive changes (new optional fields) — no version bump needed if backwards compatible

---

## 32. Background Jobs & Queues

### Queue-Based Processing for Side Effects

Any operation that doesn't need to complete before the HTTP response should be queued: emails, notifications, webhooks, report generation.

```js
// BullMQ (Redis-backed job queue)
const { Queue, Worker } = require('bullmq');

const emailQueue = new Queue('emails', { connection: redisConfig });

// Producer — fire and forget
await emailQueue.add(
  'welcome-email',
  { userId, email },
  {
    attempts: 3,
    backoff: { type: 'exponential', delay: 2000 },
    removeOnComplete: 100, // keep last 100 completed jobs
    removeOnFail: 500,
  },
);

// API returns immediately
res.status(202).json({ message: 'Account created. Welcome email sending.' });

// Consumer — runs separately (separate process or worker thread)
const worker = new Worker(
  'emails',
  async (job) => {
    const { userId, email } = job.data;

    if (job.name === 'welcome-email') {
      await emailService.sendWelcome(email, userId);
    }
  },
  { connection: redisConfig, concurrency: 5 },
);

worker.on('failed', (job, err) => {
  logger.error({ jobId: job.id, err }, 'Email job failed');
  Sentry.captureException(err);
});
```

### Scheduled Jobs (Cron)

```js
const cron = require('node-cron');

// Clean up expired OTPs every hour
cron.schedule('0 * * * *', async () => {
  await db.query('DELETE FROM otps WHERE expires_at < NOW()');
});

// Process outbox every 5 seconds
cron.schedule('*/5 * * * * *', processOutbox);

// Generate daily report at 2am
cron.schedule('0 2 * * *', generateDailyReport);
```

---

# Part 1 Additions: Core Interview Topics

---

## 33. OAuth 2.0 / OpenID Connect / Social Login

### OAuth 2.0 vs OpenID Connect

| | OAuth 2.0 | OpenID Connect (OIDC) |
|-|-----------|----------------------|
| Purpose | **Authorization** — grants access to resources | **Authentication** — verifies who the user is |
| Token issued | Access token | Access token + **ID token** (JWT with user info) |
| Answers | "Can app X access resource Y?" | "Who is this user?" |
| Built on | — | OAuth 2.0 |

OAuth 2.0 alone does not tell you who the user is. OIDC adds the identity layer on top.

### Authorization Code Flow + PKCE (Most Common for Web/Mobile)

```
User clicks "Login with Google"
  → App redirects to Google with client_id, redirect_uri, scope, state, code_challenge
  → User authenticates at Google
  → Google redirects back with ?code=AUTH_CODE&state=...
  → App exchanges code for tokens (POST to /token with code_verifier)
  → Google returns access_token + id_token + refresh_token
  → App verifies id_token signature, reads user info
```

**PKCE (Proof Key for Code Exchange)** — prevents authorization code interception attacks. Required for public clients (SPAs, mobile apps) that can't keep a client secret.

```js
const crypto = require('crypto');

// Step 1: Generate code verifier + challenge (client-side, before redirect)
function generatePKCE() {
  const verifier = crypto.randomBytes(32).toString('base64url'); // 43-128 chars
  const challenge = crypto.createHash('sha256').update(verifier).digest('base64url');
  return { verifier, challenge };
}

// Step 2: Redirect to provider
app.get('/auth/google', (req, res) => {
  const { verifier, challenge } = generatePKCE();
  const state = crypto.randomBytes(16).toString('hex'); // CSRF protection

  // Store verifier and state in session (server-side) or encrypted cookie
  req.session.pkceVerifier = verifier;
  req.session.oauthState = state;

  const params = new URLSearchParams({
    client_id: process.env.GOOGLE_CLIENT_ID,
    redirect_uri: process.env.GOOGLE_REDIRECT_URI,
    response_type: 'code',
    scope: 'openid email profile',
    state,
    code_challenge: challenge,
    code_challenge_method: 'S256',
  });

  res.redirect(`https://accounts.google.com/o/oauth2/v2/auth?${params}`);
});

// Step 3: Handle callback
app.get('/auth/google/callback', async (req, res) => {
  const { code, state } = req.query;

  // Validate state to prevent CSRF
  if (state !== req.session.oauthState) {
    return res.status(400).json({ error: 'Invalid state' });
  }

  // Exchange code for tokens
  const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      code,
      client_id: process.env.GOOGLE_CLIENT_ID,
      client_secret: process.env.GOOGLE_CLIENT_SECRET,
      redirect_uri: process.env.GOOGLE_REDIRECT_URI,
      grant_type: 'authorization_code',
      code_verifier: req.session.pkceVerifier, // PKCE
    }),
  });

  const { access_token, id_token } = await tokenRes.json();

  // Verify and decode ID token (use a library — never decode without verification)
  const { OAuth2Client } = require('google-auth-library');
  const client = new OAuth2Client(process.env.GOOGLE_CLIENT_ID);
  const ticket = await client.verifyIdToken({ idToken: id_token, audience: process.env.GOOGLE_CLIENT_ID });
  const { sub: googleId, email, name, picture } = ticket.getPayload();

  // Upsert user in your DB
  let user = await db.query('SELECT * FROM users WHERE google_id = $1', [googleId]);
  if (!user) {
    user = await db.query(
      'INSERT INTO users (google_id, email, name, avatar_url) VALUES ($1, $2, $3, $4) RETURNING *',
      [googleId, email, name, picture],
    );
  }

  // Issue your own session/JWT
  const { accessToken, refreshToken } = issueTokens(user.id, user.role);
  res.cookie('refreshToken', refreshToken, { httpOnly: true, secure: true, sameSite: 'Strict' });
  res.json({ accessToken });
});
```

### Client Credentials Flow (Machine-to-Machine)

Used when a server talks to another server — no user involved.

```js
// Service A gets an access token to call Service B
async function getMachineToken() {
  const res = await fetch('https://auth.example.com/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: process.env.CLIENT_ID,
      client_secret: process.env.CLIENT_SECRET,
      scope: 'read:orders write:shipments',
    }),
  });
  const { access_token, expires_in } = await res.json();
  return access_token;
}

// Cache and reuse the token until near expiry
let cachedToken = null;
let tokenExpiry = 0;

async function getToken() {
  if (cachedToken && Date.now() < tokenExpiry - 30_000) return cachedToken;
  const token = await getMachineToken();
  cachedToken = token;
  tokenExpiry = Date.now() + 3600 * 1000;
  return token;
}
```

### Flow Comparison

| Flow | Use Case | User Involved |
|------|----------|---------------|
| Authorization Code + PKCE | Web apps, mobile apps (social login) | Yes |
| Client Credentials | Service-to-service, background workers | No |
| Device Flow | Smart TVs, CLI tools | Yes (on another device) |
| Implicit (deprecated) | — replaced by PKCE | — |

---

## 34. gRPC & GraphQL

### gRPC

gRPC is a high-performance RPC framework using **Protocol Buffers** (binary serialization) over HTTP/2. Faster and more type-safe than REST+JSON.

**When to use gRPC:**
- Internal service-to-service communication (microservices)
- Need for bidirectional streaming
- Strongly typed contracts across polyglot services
- Mobile clients where bandwidth matters (binary payload 3-10x smaller than JSON)

```protobuf
// user.proto — the contract
syntax = "proto3";

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User); // server streaming
  rpc CreateUser (CreateUserRequest) returns (User);
}

message GetUserRequest { string id = 1; }
message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}
message ListUsersRequest { int32 limit = 1; }
message CreateUserRequest {
  string name = 1;
  string email = 2;
}
```

```js
// Server (Node.js)
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const packageDef = protoLoader.loadSync('user.proto');
const proto = grpc.loadPackageDefinition(packageDef);

const server = new grpc.Server();
server.addService(proto.UserService.service, {
  async getUser(call, callback) {
    const user = await db.findUser(call.request.id);
    if (!user) return callback({ code: grpc.status.NOT_FOUND });
    callback(null, user);
  },

  async listUsers(call) {
    const users = await db.listUsers({ limit: call.request.limit });
    for (const user of users) {
      call.write(user); // stream each user
    }
    call.end();
  },
});

server.bindAsync('0.0.0.0:50051', grpc.ServerCredentials.createInsecure(), () => server.start());

// Client
const client = new proto.UserService('localhost:50051', grpc.credentials.createInsecure());

// Unary call
client.getUser({ id: 'usr_123' }, (err, user) => console.log(user));

// Streaming call
const stream = client.listUsers({ limit: 100 });
stream.on('data', (user) => console.log(user));
stream.on('end', () => console.log('done'));
```

**REST vs gRPC:**

| | REST + JSON | gRPC |
|-|------------|------|
| Protocol | HTTP/1.1 | HTTP/2 |
| Format | JSON (text) | Protobuf (binary) |
| Contract | OpenAPI (optional) | `.proto` (required) |
| Browser support | Native | Needs grpc-web proxy |
| Streaming | SSE / WebSocket | Native (4 types) |
| Performance | Baseline | 5-10x faster |
| Use case | Public APIs, browser clients | Internal microservices |

---

### GraphQL

GraphQL is a query language where the client specifies exactly what data it needs. The server exposes a single `/graphql` endpoint.

**When to use GraphQL:**
- Client has varying data requirements (mobile vs web)
- Multiple clients need different shapes of the same data
- Rapidly evolving APIs where adding fields doesn't break clients
- Aggregating data from multiple services (GraphQL as BFF)

```js
// Schema definition
const typeDefs = `
  type User {
    id: ID!
    name: String!
    email: String!
    orders(limit: Int = 10): [Order!]!
  }

  type Order {
    id: ID!
    total: Float!
    status: String!
    createdAt: String!
  }

  type Query {
    user(id: ID!): User
    users(limit: Int, cursor: String): UserConnection!
  }

  type Mutation {
    createUser(name: String!, email: String!): User!
    updateUser(id: ID!, name: String): User!
  }

  type UserConnection {
    edges: [User!]!
    nextCursor: String
    hasMore: Boolean!
  }
`;

// Resolvers
const resolvers = {
  Query: {
    user: (_, { id }) => userService.findById(id),
    users: (_, { limit = 20, cursor }) => userService.list({ limit, cursor }),
  },
  Mutation: {
    createUser: (_, args, ctx) => {
      if (!ctx.user) throw new AuthenticationError('Not authenticated');
      return userService.create(args);
    },
  },
  User: {
    // This resolver runs only when orders field is requested
    orders: (user, { limit }, ctx) => ctx.orderLoader.load({ userId: user.id, limit }),
  },
};
```

**N+1 in GraphQL — solve with DataLoader:**

```js
const DataLoader = require('dataloader');

// Create per-request loaders (never share across requests)
function createLoaders() {
  return {
    orderLoader: new DataLoader(async (keys) => {
      // keys = [{ userId: '1', limit: 10 }, { userId: '2', limit: 10 }, ...]
      const userIds = keys.map(k => k.userId);
      const orders = await db.query('SELECT * FROM orders WHERE user_id = ANY($1)', [userIds]);

      // Group by userId and return in same order as keys
      const map = orders.reduce((acc, o) => {
        acc[o.userId] = acc[o.userId] || [];
        acc[o.userId].push(o);
        return acc;
      }, {});

      return keys.map(k => (map[k.userId] || []).slice(0, k.limit));
    }),
  };
}

// Pass loaders in context — available to all resolvers
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: ({ req }) => ({
    user: req.user,
    ...createLoaders(), // fresh loaders per request
  }),
});
```

**REST vs GraphQL:**

| | REST | GraphQL |
|-|------|---------|
| Endpoints | Many (`/users`, `/orders`, ...) | One (`/graphql`) |
| Over/under-fetching | Common | Eliminated (client asks for what it needs) |
| Versioning | Required (`/v1`, `/v2`) | Add fields; deprecate old ones |
| Caching | HTTP cache works naturally | Requires custom (persisted queries) |
| File uploads | Simple | Requires `graphql-upload` |
| Learning curve | Low | Higher |

---

# Part 2 Additions: Security

---

## 35. SQL Injection & XSS Prevention

### SQL Injection

SQL injection occurs when user input is concatenated into a SQL query. The attacker injects SQL syntax to read, modify, or delete arbitrary data.

```js
// VULNERABLE — never do this
const userId = req.params.id; // attacker sends: "1 OR 1=1"
const query = `SELECT * FROM users WHERE id = ${userId}`;
// Becomes: SELECT * FROM users WHERE id = 1 OR 1=1 — returns ALL users

// Also vulnerable to data extraction:
// userId = "1 UNION SELECT username, password FROM admin_users--"

// SAFE — parameterized queries (always)
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);

// Sequelize ORM — safe by default
const user = await User.findOne({ where: { id: userId } });

// Knex — safe
const user = await knex('users').where({ id: userId }).first();

// If you MUST build dynamic queries, use the query builder's identifier quoting
const column = 'name'; // from user input
// NEVER: `ORDER BY ${column}`
// SAFE: validate against allowlist first
const ALLOWED_SORT_COLUMNS = ['name', 'created_at', 'email'];
if (!ALLOWED_SORT_COLUMNS.includes(column)) throw new ValidationError('sort', 'Invalid sort column');
const users = await knex('users').orderBy(column, 'asc');
```

**Second-order injection** — data is stored safely but later used unsafely in another query:

```js
// Step 1: User registers with name: "admin'--"
// Stored safely in DB (parameterized)

// Step 2: Later, some code does:
const name = user.name; // "admin'--" from DB
await db.query(`UPDATE logs SET message = 'User ${name} logged in'`); // VULNERABLE
// Always use parameterized queries even for data that came FROM your own DB
```

---

### XSS (Cross-Site Scripting)

XSS injects malicious scripts into pages viewed by other users. The script runs in the victim's browser — can steal cookies, hijack sessions, redirect to phishing pages.

**Types:**

| Type | How | Example |
|------|-----|---------|
| Stored (Persistent) | Malicious input saved in DB, rendered to other users | Comment with `<script>` tag |
| Reflected | Malicious input in URL, reflected immediately in response | `?name=<script>alert(1)</script>` |
| DOM-based | Malicious data read from DOM (URL hash) and injected without server | JS reads `location.hash` and writes to `innerHTML` |

```js
// VULNERABLE — setting innerHTML with user content
element.innerHTML = userInput; // XSS

// SAFE — use textContent for plain text
element.textContent = userInput;

// SAFE — DOMPurify for cases where you need to render HTML (e.g., rich text editor output)
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput, { USE_PROFILES: { html: true } });

// SAFE — React escapes by default
return <div>{userInput}</div>; // safe
// UNSAFE in React — only use with trusted content
return <div dangerouslySetInnerHTML={{ __html: userInput }} />; // XSS risk

// Server-side: sanitize before storing
import { sanitize } from 'isomorphic-dompurify';
const clean = sanitize(req.body.content);
await db.query('INSERT INTO posts (content) VALUES ($1)', [clean]);
```

**Content Security Policy (CSP)** — the last line of defense. Tells the browser which sources are allowed to execute scripts:

```js
// Helmet.js sets CSP headers
const helmet = require('helmet');

app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'nonce-RANDOM_NONCE'"], // only scripts with the right nonce
    styleSrc: ["'self'", 'https://fonts.googleapis.com'],
    imgSrc: ["'self'", 'data:', 'https://cdn.example.com'],
    connectSrc: ["'self'", 'https://api.example.com'],
    fontSrc: ["'self'", 'https://fonts.gstatic.com'],
    objectSrc: ["'none'"],  // no plugins
    upgradeInsecureRequests: [],
  },
}));

// Per-request nonce for inline scripts (safer than 'unsafe-inline')
app.use((req, res, next) => {
  res.locals.nonce = crypto.randomBytes(16).toString('base64');
  next();
});
// Then in HTML: <script nonce="<%= nonce %>">...</script>
```

**Security headers summary:**

```js
app.use(helmet()); // sets all of the below with sane defaults
// X-Content-Type-Options: nosniff       — prevent MIME sniffing
// X-Frame-Options: DENY                 — prevent clickjacking
// Strict-Transport-Security             — force HTTPS
// X-XSS-Protection: 0                  — disable broken legacy XSS filter (use CSP instead)
```

---

# Part 3 Additions: API Design Best Practices

---

## 36. Soft Delete vs Hard Delete

### Hard Delete

Row is permanently removed from the database. Simple, clean, no data retention.

```sql
DELETE FROM users WHERE id = $1;
-- Row is gone. FK references will fail if not cascaded.
```

**Problems with hard delete:**
- Cascading FK deletes can be dangerous and unexpected
- No audit trail — can't see who deleted what or when
- Can't recover accidentally deleted data
- Referenced in other tables (orders referencing deleted users)

---

### Soft Delete

Row is kept but marked as deleted via a `deleted_at` timestamp. The app filters out deleted records in queries.

```sql
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMPTZ;

-- Soft delete
UPDATE users SET deleted_at = NOW() WHERE id = $1;

-- Query — must always exclude deleted rows
SELECT * FROM users WHERE deleted_at IS NULL AND id = $1;

-- Partial index for performance (only indexes non-deleted rows)
CREATE INDEX idx_users_active ON users(id) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_email_active ON users(email) WHERE deleted_at IS NULL;
-- UNIQUE constraint on active rows only:
CREATE UNIQUE INDEX idx_users_email_unique ON users(email) WHERE deleted_at IS NULL;
```

```js
// Sequelize: built-in paranoid mode
const User = sequelize.define('User', { ... }, { paranoid: true }); // adds deletedAt column
await user.destroy(); // sets deletedAt, doesn't delete
User.findAll();       // automatically adds WHERE "deletedAt" IS NULL
User.findAll({ paranoid: false }); // includes deleted rows

// Mongoose: mongoose-delete plugin
const mongooseDelete = require('mongoose-delete');
userSchema.plugin(mongooseDelete, { deletedAt: true, overrideMethods: true });
await User.delete({ _id: id });
User.find();           // excludes deleted
User.findWithDeleted() // includes deleted
```

**FK implications with soft delete:**

```sql
-- User is soft-deleted but their orders still reference users.id
-- Hard delete would cascade-delete orders or fail; soft delete avoids this
-- But you must decide: should a soft-deleted user's data still be accessible?

-- Option 1: allow FK references to soft-deleted rows (usually fine)
-- Option 2: on soft-delete, also soft-delete dependent records
UPDATE orders SET deleted_at = NOW() WHERE user_id = $1 AND deleted_at IS NULL;
UPDATE sessions SET deleted_at = NOW() WHERE user_id = $1 AND deleted_at IS NULL;
```

### When to Use Each

| Use Soft Delete | Use Hard Delete |
|-----------------|-----------------|
| Data has audit/compliance requirements | Personal data that must be purged (GDPR right to erasure) |
| Other records reference this record | Truly temporary data (sessions, OTPs, temp files) |
| "Recycle bin" / undo functionality | Data with no business value after deletion |
| Need to understand deletion history | Storage cost is a concern |

**GDPR + soft delete:** soft delete alone is NOT sufficient for GDPR erasure requests. Anonymize PII on deletion:

```js
async function gdprDelete(userId) {
  await db.query(`
    UPDATE users SET
      email = 'deleted_' || id || '@deleted.invalid',
      name = 'Deleted User',
      phone = NULL,
      deleted_at = NOW()
    WHERE id = $1
  `, [userId]);
  // Data is "deleted" from user's perspective; row kept for FK integrity
}
```

---

## 37. Database Migrations (Zero-Downtime)

Schema changes on a live database can lock tables, break running queries, or cause downtime. Safe migrations require planning for the current and next version of the app running simultaneously during deploy.

### Safe vs Unsafe Operations

| Operation | Safe? | Notes |
|-----------|-------|-------|
| `ADD COLUMN` nullable | ✓ Safe | Instant in PostgreSQL |
| `ADD COLUMN` with DEFAULT (PG 11+) | ✓ Safe | Stored as table-level default, no rewrite |
| `ADD COLUMN NOT NULL` without default | ✗ Unsafe | Full table scan to validate |
| `DROP COLUMN` | ✓ Safe* | Safe at DB level — verify no code references it first |
| `CREATE INDEX` | ✗ Unsafe | Locks table — use `CONCURRENTLY` |
| `CREATE INDEX CONCURRENTLY` | ✓ Safe | No lock, but slower; can't run in transaction |
| `ALTER COLUMN TYPE` | ✗ Unsafe | Full table rewrite + lock |
| `ADD CONSTRAINT` (FK, UNIQUE) | ✗ Unsafe | Full table scan + lock |
| `ADD CONSTRAINT NOT VALID` then `VALIDATE` | ✓ Safe | Splits into two non-blocking steps |
| `RENAME COLUMN` | ✗ Unsafe | Breaks existing queries immediately |

### Expand/Contract Pattern (Zero-Downtime Rename/Restructure)

Never rename a column or change its type in one step. Use three deployment phases:

```
Phase 1 — Expand
  Migration: add new column
  App v1: writes to old column only (reads old column)
  App v2: writes to BOTH columns (reads old column)
  Deploy app v2

Phase 2 — Backfill
  Migration: copy data from old to new column (in batches)
  Migration: validate constraint on new column

Phase 3 — Contract
  App v3: writes to new column only (reads new column)
  Deploy app v3
  Migration: drop old column
```

```sql
-- Phase 1: Add new column (non-breaking)
ALTER TABLE users ADD COLUMN full_name TEXT;

-- Phase 2: Backfill in batches (never a single UPDATE on large table)
DO $$
DECLARE last_id BIGINT := 0;
BEGIN
  LOOP
    UPDATE users
    SET full_name = first_name || ' ' || last_name
    WHERE id > last_id AND full_name IS NULL
    ORDER BY id LIMIT 5000
    RETURNING id INTO last_id;
    EXIT WHEN NOT FOUND;
    PERFORM pg_sleep(0.1); -- brief pause between batches
  END LOOP;
END $$;

-- Add NOT NULL constraint safely (check, then validate — no full lock)
ALTER TABLE users ADD CONSTRAINT users_full_name_not_null
  CHECK (full_name IS NOT NULL) NOT VALID;
-- Later (after backfill complete):
ALTER TABLE users VALIDATE CONSTRAINT users_full_name_not_null;

-- Phase 3: Drop old columns (after app v3 is fully deployed)
ALTER TABLE users DROP COLUMN first_name;
ALTER TABLE users DROP COLUMN last_name;

-- Always create indexes CONCURRENTLY
CREATE INDEX CONCURRENTLY idx_users_full_name ON users(full_name);
-- Note: CONCURRENTLY cannot run inside a transaction block
```

```js
// node-pg-migrate example (migration file)
exports.up = async (pgm) => {
  // Add column safely
  pgm.addColumn('users', {
    full_name: { type: 'text' }  // nullable first
  });
};

exports.down = async (pgm) => {
  pgm.dropColumn('users', 'full_name');
};
// Always write a down migration — ability to roll back is a safety net
```

### Migration Checklist

```
Before running in production:
□ Test migration on staging with production-sized data
□ Measure migration time on representative data volume
□ Verify app works with both old and new schema simultaneously (during deploy window)
□ Confirm index creation uses CONCURRENTLY
□ Have a rollback plan (down migration tested)
□ Lock version in migration file (tie migration to app version that requires it)
```

---

# Part 4 Additions: Reliability Patterns

---

## 38. Saga Pattern / Distributed Transactions

In a microservices architecture, a single business operation may span multiple services, each with its own database. You can't use a DB transaction across service boundaries. The **Saga pattern** manages this with a sequence of local transactions and compensating actions on failure.

### Choreography vs Orchestration

| | Choreography | Orchestration |
|-|-------------|---------------|
| Control | Distributed — each service reacts to events | Central — a saga orchestrator directs steps |
| Coupling | Loose | Services coupled to orchestrator |
| Visibility | Hard to see the overall flow | Easy to see and debug overall flow |
| Failure handling | Each service must emit failure events | Orchestrator handles failure centrally |
| Best for | Simple flows with few steps | Complex flows, many steps, clear rollback logic |

### Choreography-based Saga

Each service listens for events and emits its own events. No central coordinator.

```
OrderService        InventoryService      PaymentService        NotificationService
    │                     │                    │                       │
    │─── order.created ──►│                    │                       │
    │                     │─── stock.reserved ►│                       │
    │                     │                    │─── payment.charged ──►│
    │◄────────────────────────────────────────── order.confirmed ──────│

On failure:
    │                     │◄── payment.failed ─│
    │◄── stock.released ──│
    │ (emit order.cancelled)
```

```js
// OrderService — publishes event after creating order
async function placeOrder(userId, items) {
  const order = await db.transaction(async (trx) => {
    const order = await trx('orders').insert({ userId, status: 'pending', items }).returning('*');
    await trx('outbox').insert({
      event: 'order.created',
      payload: JSON.stringify({ orderId: order[0].id, userId, items }),
    });
    return order[0];
  });
  return order;
}

// InventoryService — listens for order.created, reserves stock
consumer.subscribe('order.created', async (event) => {
  const { orderId, items } = event;
  try {
    await reserveStock(items);
    await publish('stock.reserved', { orderId });
  } catch (err) {
    await publish('stock.reservation.failed', { orderId, reason: err.message });
  }
});

// OrderService — listens for failure, compensates
consumer.subscribe('stock.reservation.failed', async (event) => {
  const { orderId } = event;
  await db('orders').where({ id: orderId }).update({ status: 'cancelled' });
  await publish('order.cancelled', { orderId, reason: 'stock unavailable' });
});
```

### Orchestration-based Saga

A central orchestrator (state machine) drives the workflow, calling services and handling failures.

```js
class OrderSaga {
  constructor(orderId) {
    this.orderId = orderId;
    this.state = 'started';
  }

  async execute() {
    try {
      // Step 1: Reserve inventory
      this.state = 'reserving_stock';
      await inventoryService.reserveStock(this.orderId);

      // Step 2: Charge payment
      this.state = 'charging_payment';
      await paymentService.charge(this.orderId);

      // Step 3: Confirm order
      this.state = 'confirming';
      await orderService.confirm(this.orderId);

      this.state = 'completed';
      await notificationService.sendConfirmation(this.orderId);
    } catch (err) {
      await this.compensate(err);
    }
  }

  async compensate(err) {
    logger.error({ orderId: this.orderId, state: this.state, err }, 'Saga failed, compensating');

    // Roll back each completed step in reverse order
    if (this.state === 'confirming' || this.state === 'charging_payment') {
      await paymentService.refund(this.orderId).catch(logger.error); // compensating transaction
    }
    if (this.state === 'charging_payment' || this.state === 'reserving_stock') {
      await inventoryService.releaseStock(this.orderId).catch(logger.error);
    }

    await orderService.cancel(this.orderId, err.message);
    this.state = 'failed';
  }
}

// Persist saga state for crash recovery
class PersistentOrderSaga extends OrderSaga {
  async updateState(newState) {
    this.state = newState;
    await db.query('UPDATE sagas SET state = $1, updated_at = NOW() WHERE id = $2', [newState, this.orderId]);
  }
}
```

**Key rule:** compensating transactions must be idempotent — if a compensation runs twice (due to retry), the outcome must be the same.

---

## 39. Bulkhead Pattern

Named after the watertight compartments in a ship — if one compartment floods, the others stay dry. In software: isolate failures so one degraded dependency doesn't bring down the whole service.

**Problem without bulkheads:** your service calls User API, Payment API, and Inventory API. Payment API becomes slow (30s responses). All 100 connection pool threads are tied up waiting for Payment. User API and Inventory API calls also start failing — they have no threads available.

```js
// Without bulkhead — one slow dependency consumes all resources
const sharedPool = createPool({ max: 100 });
// If payment is slow: all 100 connections waiting on payment
// User and inventory queries queued, timing out

// With bulkhead — dedicated resource pools per dependency
const paymentPool  = createPool({ max: 20 });  // payment gets max 20 threads
const userPool     = createPool({ max: 40 });  // user service gets max 40
const inventoryPool = createPool({ max: 40 });

// Now payment slowness only affects its own 20 slots
// User and inventory continue operating normally
```

**Bulkhead with semaphore (concurrent request limit):**

```js
class Bulkhead {
  constructor(maxConcurrent) {
    this.maxConcurrent = maxConcurrent;
    this.activeCount = 0;
    this.queue = [];
  }

  async execute(fn) {
    if (this.activeCount >= this.maxConcurrent) {
      if (this.queue.length >= this.maxConcurrent) {
        throw new Error('Bulkhead queue full — rejecting request');
      }
      // Wait for a slot to free up
      await new Promise((resolve, reject) => {
        this.queue.push({ resolve, reject });
      });
    }

    this.activeCount++;
    try {
      return await fn();
    } finally {
      this.activeCount--;
      const next = this.queue.shift();
      if (next) next.resolve();
    }
  }
}

const paymentBulkhead  = new Bulkhead(20); // max 20 concurrent payment calls
const userBulkhead     = new Bulkhead(40);

// Usage
async function chargeUser(userId, amount) {
  return paymentBulkhead.execute(() =>
    paymentService.charge(userId, amount)
  );
  // If >20 concurrent calls: new requests wait in queue or are rejected
  // Either way, user and inventory calls are never affected
}
```

**Combine with Circuit Breaker for defense in depth:**

```
Request
  → Bulkhead (limits concurrency to dependency)
    → Circuit Breaker (stops calling if dependency is failing)
      → Retry (retries transient errors)
        → Timeout (gives up after N ms)
          → Dependency
```

```js
class ResilientClient {
  constructor(name, options = {}) {
    this.bulkhead = new Bulkhead(options.maxConcurrent ?? 20);
    this.breaker  = new CircuitBreaker(options.failureThreshold ?? 5);
    this.timeout  = options.timeoutMs ?? 5000;
  }

  async call(fn) {
    return this.bulkhead.execute(() =>
      this.breaker.call(() =>
        fetchWithTimeout(fn, this.timeout)
      )
    );
  }
}

const paymentClient = new ResilientClient('payment', { maxConcurrent: 20, timeoutMs: 3000 });
const result = await paymentClient.call(() => paymentService.charge(userId, amount));
```

---

## 40. Dead Letter Queue (DLQ)

A DLQ is a queue where messages that could not be successfully processed are sent after exhausting retries. It prevents poison pill messages (messages that always fail) from blocking the entire queue.

**Without DLQ:** a malformed message retries indefinitely, blocking other messages in the queue.

### RabbitMQ DLQ

```js
const amqp = require('amqplib');

async function setupQueues(channel) {
  // DLQ — where failed messages go
  await channel.assertQueue('orders.dlq', { durable: true });

  // Main queue — configure dead letter exchange
  await channel.assertExchange('dlx', 'direct', { durable: true });
  await channel.bindQueue('orders.dlq', 'dlx', 'orders');

  await channel.assertQueue('orders', {
    durable: true,
    arguments: {
      'x-dead-letter-exchange': 'dlx',
      'x-dead-letter-routing-key': 'orders',
      'x-message-ttl': 30_000,  // message expires after 30s if not acked
    },
  });
}

// Consumer — failed messages auto-routed to DLQ after nack with requeue=false
channel.consume('orders', async (msg) => {
  const data = JSON.parse(msg.content);
  try {
    await processOrder(data);
    channel.ack(msg);
  } catch (err) {
    logger.error({ err, data }, 'Order processing failed');

    const attempts = (msg.properties.headers['x-death']?.[0]?.count ?? 0) + 1;

    if (attempts >= 3) {
      // Exhausted retries — send to DLQ (no requeue)
      channel.nack(msg, false, false); // requeue=false → goes to DLX → DLQ
    } else {
      channel.nack(msg, false, true);  // requeue=true → try again
    }
  }
});

// DLQ consumer — monitor, alert, and handle manually or retry selectively
channel.consume('orders.dlq', async (msg) => {
  const data = JSON.parse(msg.content);
  const deathInfo = msg.properties.headers['x-death']?.[0];

  logger.error({
    data,
    reason: deathInfo?.reason,      // 'rejected' | 'expired' | 'maxlen'
    count: deathInfo?.count,
    queue: deathInfo?.queue,
    time: deathInfo?.time,
  }, 'Message in DLQ');

  await alerting.notify('DLQ message received', { data, deathInfo });

  channel.ack(msg); // acknowledge DLQ message to prevent infinite loop
});
```

### BullMQ DLQ (failed jobs)

```js
const { Queue, Worker, QueueEvents } = require('bullmq');

const queue = new Queue('orders', {
  connection: redisConfig,
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: 'exponential', delay: 2000 },
    removeOnComplete: { count: 100 },
    removeOnFail: false, // keep failed jobs — this IS the DLQ in BullMQ
  },
});

const worker = new Worker('orders', async (job) => {
  await processOrder(job.data);
}, { connection: redisConfig });

// Monitor failed jobs
const queueEvents = new QueueEvents('orders', { connection: redisConfig });
queueEvents.on('failed', async ({ jobId, failedReason }) => {
  const job = await queue.getJob(jobId);
  logger.error({ jobId, data: job.data, reason: failedReason }, 'Job failed');
  await alerting.notify('Job failed after all retries', { jobId, data: job.data });
});

// Retry specific failed jobs manually
async function retryDLQJob(jobId) {
  const job = await queue.getJob(jobId);
  if (!job) throw new NotFoundError('Job');
  await job.retry();
}

// Retry all failed jobs (use carefully)
async function retryAllFailed() {
  const failed = await queue.getFailed(0, 100); // get up to 100 failed jobs
  await Promise.all(failed.map(job => job.retry()));
}

// Inspect DLQ
async function inspectDLQ() {
  const failed = await queue.getFailed(0, 50);
  return failed.map(job => ({
    id: job.id,
    name: job.name,
    data: job.data,
    failedReason: job.failedReason,
    attemptsMade: job.attemptsMade,
    timestamp: job.timestamp,
  }));
}
```

**DLQ monitoring checklist:**
- Alert on DLQ size threshold (e.g., > 10 messages)
- Log full message content + failure reason + attempt count
- Build an admin UI to inspect, retry, or discard DLQ messages
- Set a retention policy — don't let DLQ grow unboundedly

---

# Part 5 Additions: Advanced Topics

---

## 41. Event Sourcing & CQRS

### Event Sourcing

Instead of storing the current state of an entity, store the **sequence of events** that led to it. Current state is derived by replaying events.

```
Traditional (state): users table → { id: 1, balance: 850, status: 'active' }

Event Sourcing:
  event_store table:
  1. AccountOpened   { userId: 1, initialBalance: 1000 }
  2. MoneyDeposited  { userId: 1, amount: 500 }
  3. MoneyWithdrawn  { userId: 1, amount: 200 }
  4. MoneyWithdrawn  { userId: 1, amount: 450 }

  Current balance = 1000 + 500 - 200 - 450 = 850  (replay)
```

```js
// Event store table
// CREATE TABLE events (
//   id          BIGSERIAL PRIMARY KEY,
//   stream_id   TEXT NOT NULL,        -- e.g., 'account-123'
//   event_type  TEXT NOT NULL,
//   payload     JSONB NOT NULL,
//   version     INT NOT NULL,         -- sequence number per stream
//   created_at  TIMESTAMPTZ DEFAULT NOW()
// );
// UNIQUE(stream_id, version)          -- prevent concurrent write conflicts

class EventStore {
  async append(streamId, events, expectedVersion) {
    const client = await pool.connect();
    try {
      await client.query('BEGIN');

      // Optimistic concurrency — prevent lost updates
      const { rows } = await client.query(
        'SELECT MAX(version) AS version FROM events WHERE stream_id = $1',
        [streamId],
      );
      const currentVersion = rows[0].version ?? 0;
      if (currentVersion !== expectedVersion) {
        throw new ConcurrencyError(`Expected version ${expectedVersion}, got ${currentVersion}`);
      }

      let version = expectedVersion;
      for (const event of events) {
        version++;
        await client.query(
          'INSERT INTO events (stream_id, event_type, payload, version) VALUES ($1, $2, $3, $4)',
          [streamId, event.type, JSON.stringify(event.payload), version],
        );
      }

      await client.query('COMMIT');
      return version;
    } catch (err) {
      await client.query('ROLLBACK');
      throw err;
    } finally {
      client.release();
    }
  }

  async load(streamId) {
    const { rows } = await pool.query(
      'SELECT * FROM events WHERE stream_id = $1 ORDER BY version',
      [streamId],
    );
    return rows;
  }
}

// Rebuild current state from events
class Account {
  constructor() {
    this.balance = 0;
    this.status = 'inactive';
    this.version = 0;
  }

  static fromEvents(events) {
    const account = new Account();
    for (const event of events) {
      account.apply(event);
    }
    return account;
  }

  apply(event) {
    switch (event.event_type) {
      case 'AccountOpened':
        this.balance = event.payload.initialBalance;
        this.status = 'active';
        break;
      case 'MoneyDeposited':
        this.balance += event.payload.amount;
        break;
      case 'MoneyWithdrawn':
        this.balance -= event.payload.amount;
        break;
    }
    this.version = event.version;
  }

  withdraw(amount) {
    if (amount > this.balance) throw new Error('Insufficient funds');
    // Return new events to append — don't mutate state directly
    return [{ type: 'MoneyWithdrawn', payload: { amount } }];
  }
}

// Usage
const store = new EventStore();
const events = await store.load('account-123');
const account = Account.fromEvents(events);

const newEvents = account.withdraw(200);
await store.append('account-123', newEvents, account.version); // optimistic locking
```

**Snapshots** — for long event streams, periodically snapshot current state to avoid replaying thousands of events:

```js
// Load from snapshot + events after snapshot
async function loadWithSnapshot(streamId) {
  const snapshot = await getLatestSnapshot(streamId);
  const events = await store.loadFrom(streamId, (snapshot?.version ?? 0) + 1);

  const account = snapshot ? Account.fromSnapshot(snapshot) : new Account();
  events.forEach(e => account.apply(e));
  return account;
}
```

### CQRS with Event Sourcing

Projections listen to the event stream and build denormalized read models optimized for queries.

```js
// Projection: maintain a read-optimized account_balances table
async function handleEvent(event) {
  switch (event.event_type) {
    case 'AccountOpened':
      await db.query(
        'INSERT INTO account_balances (account_id, balance, status, last_updated) VALUES ($1, $2, $3, $4)',
        [event.stream_id.replace('account-', ''), event.payload.initialBalance, 'active', event.created_at],
      );
      break;
    case 'MoneyWithdrawn':
    case 'MoneyDeposited':
      const delta = event.event_type === 'MoneyDeposited' ? event.payload.amount : -event.payload.amount;
      await db.query(
        'UPDATE account_balances SET balance = balance + $1, last_updated = $2 WHERE account_id = $3',
        [delta, event.created_at, event.stream_id.replace('account-', '')],
      );
      break;
  }
}

// Read model queries are fast — no event replay needed
async function getBalance(accountId) {
  return db.query('SELECT balance FROM account_balances WHERE account_id = $1', [accountId]);
}

// Rebuild projection from scratch (e.g., after adding new read model field)
async function rebuildProjection() {
  await db.query('TRUNCATE account_balances');
  const events = await db.query('SELECT * FROM events ORDER BY id');
  for (const event of events.rows) {
    await handleEvent(event);
  }
}
```

**When to use Event Sourcing:**
- Complete audit trail is required (finance, healthcare, legal)
- Need to reconstruct state at any point in time
- Multiple consumers need the same data in different shapes
- Event-driven architecture where other services react to state changes

**When NOT to use:**
- Simple CRUD apps — massive overhead for little benefit
- Small teams unfamiliar with the pattern — steep learning curve
- When query performance on the read side is simple

---

## 42. Deployment Strategies

Deployment strategies control how a new version of your application is rolled out, balancing risk (a bad deploy affects users) against deployment velocity.

### Blue-Green Deployment

Maintain two identical production environments. Switch traffic from blue (current) to green (new) atomically.

```
Traffic → Load Balancer → [Blue: v1]  [Green: v2 — staging]

Deploy v2 to green → test green → switch LB to green:
Traffic → Load Balancer → [Blue: v1 — standby]  [Green: v2 — live]

On failure: instant rollback by switching LB back to blue
```

```nginx
# Nginx upstream switch (blue-green)
upstream app {
  # Switch between blue and green by commenting/uncommenting
  server blue-app:3000;   # Blue (v1)
  # server green-app:3000; # Green (v2)
}

# Or: use environment variable + template
server app_${ACTIVE_COLOR}:3000;
```

```bash
# Kubernetes: blue-green via label selector
kubectl patch service my-app -p '{"spec":{"selector":{"version":"green"}}}'
# Rollback:
kubectl patch service my-app -p '{"spec":{"selector":{"version":"blue"}}}'
```

**Pros:** instant rollback, zero-downtime, full environment available for testing before switch
**Cons:** requires 2x infrastructure cost during deploy; DB migrations must be backward compatible

---

### Canary Deployment

Route a small percentage of traffic to the new version, gradually increase as confidence grows.

```
Traffic → Load Balancer:
  95% → v1 (stable)
   5% → v2 (canary)

Monitor error rate, latency on v2
If healthy: 10% → 50% → 100%
If degraded: rollback to 0% on v2
```

```yaml
# Kubernetes: canary via replica count ratio
# v1: 19 replicas, v2: 1 replica = 5% canary
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-v2-canary
spec:
  replicas: 1  # 5% of 20 total
  selector:
    matchLabels: { app: my-app, version: v2 }
  template:
    metadata:
      labels: { app: my-app, version: v2 }
    spec:
      containers:
        - name: app
          image: my-app:v2
```

```js
// Feature flag canary — route specific users to new version (ring-based)
function shouldUseNewVersion(userId) {
  // 5% of users get new version based on user ID hash
  return parseInt(userId, 36) % 100 < 5;
}

app.get('/api/checkout', (req, res) => {
  if (shouldUseNewVersion(req.user.id)) {
    return checkoutV2Handler(req, res);
  }
  return checkoutV1Handler(req, res);
});
```

**Canary monitoring — auto-rollback:**

```js
// Watch error rate on canary; auto-rollback if threshold exceeded
async function monitorCanary() {
  const canaryErrorRate = await metrics.getErrorRate('v2', '5m');
  const stableErrorRate = await metrics.getErrorRate('v1', '5m');

  if (canaryErrorRate > stableErrorRate * 2 || canaryErrorRate > 0.05) {
    logger.error({ canaryErrorRate, stableErrorRate }, 'Canary degraded — rolling back');
    await rollbackCanary();
    await alerting.page('Canary auto-rollback triggered');
  }
}
setInterval(monitorCanary, 30_000);
```

**Pros:** real user traffic testing, gradual risk exposure, easy rollback
**Cons:** requires good observability to detect degradation; complex to manage DB schema during canary

---

### Rolling Update

Replace instances one at a time (or in small batches). No duplicate environment needed.

```
v1 v1 v1 v1 v1   (initial)
v2 v1 v1 v1 v1   (rolling update starts)
v2 v2 v1 v1 v1
v2 v2 v2 v1 v1
v2 v2 v2 v2 v2   (complete)
```

```yaml
# Kubernetes rolling update (default strategy)
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # allow 1 extra pod during update
      maxUnavailable: 0  # keep all existing pods running
  template:
    spec:
      containers:
        - name: app
          image: my-app:v2
          readinessProbe:
            httpGet: { path: /health, port: 3000 }
            initialDelaySeconds: 10
            periodSeconds: 5
          # Pod only receives traffic after readiness probe passes
```

**Pros:** no extra infrastructure, Kubernetes default, gradual rollout
**Cons:** slower than blue-green; both v1 and v2 run simultaneously (schema must be backward compatible); rollback requires another rolling update

---

### Strategy Comparison

| Strategy | Rollback Speed | Infrastructure Cost | Traffic During Deploy | Complexity |
|----------|---------------|--------------------|-----------------------|------------|
| Recreate (stop all, start new) | Slow (downtime) | Low | Interrupted | Simple |
| Rolling Update | Slow (another rolling deploy) | None extra | Live | Medium |
| Blue-Green | Instant (LB switch) | 2x during deploy | Uninterrupted | Medium |
| Canary | Fast (reduce %) | ~5% extra | Uninterrupted | High |

**DB migrations during any zero-downtime deploy:** the new and old app version run simultaneously during the transition. Schema changes must be backward compatible — use the expand/contract pattern (see Section 37).

---

_Last updated: 2026-06-04_
