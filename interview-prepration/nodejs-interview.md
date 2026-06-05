# Node.js Interview Reference

A senior-focused reference covering Node.js core, Express, Fastify, NestJS, database patterns, and production/DevOps. Concept + code snippet format.

---

## Table of Contents

### Part 1: Node.js Core
1. [Architecture & Internals](#1-architecture--internals)
2. [Module System](#2-module-system)
3. [File System & Path](#3-file-system--path)
4. [Streams](#4-streams)
5. [Buffers & Encoding](#5-buffers--encoding)
6. [Networking](#6-networking)
7. [Child Processes](#7-child-processes)
8. [Worker Threads](#8-worker-threads)
9. [Cluster Module](#9-cluster-module)
10. [Events & EventEmitter](#10-events--eventemitter)

### Part 2: Express & Fastify
11. [Express Fundamentals](#11-express-fundamentals)
12. [Fastify](#12-fastify)
13. [REST API Patterns](#13-rest-api-patterns)
14. [Authentication](#14-authentication)
15. [Security](#15-security)

### Part 3: NestJS
16. [Core Concepts](#16-core-concepts)
17. [Guards, Interceptors, Pipes, Filters](#17-guards-interceptors-pipes-filters)
18. [Database Integration](#18-database-integration)
19. [Microservices](#19-microservices)

### Part 4: Database Patterns
20. [Connection Pooling](#20-connection-pooling)
21. [Query Patterns](#21-query-patterns)
22. [Transactions](#22-transactions)
23. [Migrations](#23-migrations)

### Part 5: Production & DevOps
24. [Environment & Config](#24-environment--config)
25. [Logging](#25-logging)
26. [Graceful Shutdown](#26-graceful-shutdown)
27. [Process Management](#27-process-management)
28. [Docker](#28-docker)
29. [CI/CD](#29-cicd)
30. [Health Checks & Observability](#30-health-checks--observability)
31. [Performance Tuning](#31-performance-tuning)
32. [Secrets Management](#32-secrets-management)

### Part 1 (continued): Node.js Core
33. [Crypto Module](#33-crypto-module)
34. [DNS Module](#34-dns-module)
35. [node: Protocol Imports](#35-node-protocol-imports)

### Part 2 (continued): Express & Fastify
36. [File Uploads](#36-file-uploads)

### Part 6: Testing & Development Workflow
37. [Testing Node.js](#37-testing-nodejs)
38. [Package Managers & Workspaces](#38-package-managers--workspaces)
39. [Development Workflow](#39-development-workflow)
40. [dependencies vs devDependencies](#40-dependencies-vs-devdependencies)

### Part 3 (continued): NestJS
41. [Dependency Injection](#41-dependency-injection)

---

# Part 1: Node.js Core

---

## 1. Architecture & Internals

### libuv & the Thread Pool

Node.js is a single-threaded JavaScript runtime built on V8 (JS engine) and **libuv** (async I/O library). libuv provides:

- The **event loop** — coordinates async work
- A **thread pool** (default size: 4) — handles blocking operations that the OS can't do asynchronously: file system, DNS lookups (`dns.lookup`), crypto, zlib

Network I/O (TCP, UDP, HTTP) uses the OS's non-blocking I/O (epoll/kqueue/IOCP) and does **not** use the thread pool.

```
┌─────────────────────────────────────┐
│           Node.js Process           │
│                                     │
│  ┌──────────┐   ┌─────────────────┐ │
│  │  V8 JS   │   │     libuv       │ │
│  │  Engine  │   │                 │ │
│  └──────────┘   │  ┌───────────┐  │ │
│                 │  │Event Loop │  │ │
│                 │  └───────────┘  │ │
│                 │  ┌───────────┐  │ │
│                 │  │Thread Pool│  │ │
│                 │  │(4 threads)│  │ │
│                 │  └───────────┘  │ │
│                 └─────────────────┘ │
└─────────────────────────────────────┘
```

**Thread pool size** can be tuned via `UV_THREADPOOL_SIZE` env var (max 1024):

```bash
UV_THREADPOOL_SIZE=16 node server.js
```

---

### Event Loop Phases

The event loop processes callbacks in a fixed order of phases:

```
┌──────────────────────────────┐
│           timers             │  setTimeout / setInterval
├──────────────────────────────┤
│       pending callbacks      │  I/O errors from prev tick
├──────────────────────────────┤
│       idle / prepare         │  internal only
├──────────────────────────────┤
│            poll              │  retrieve I/O events, execute callbacks
│                              │  (blocks here when queue empty)
├──────────────────────────────┤
│            check             │  setImmediate
├──────────────────────────────┤
│       close callbacks        │  socket.on('close')
└──────────────────────────────┘
```

Between each phase, Node.js drains two microtask queues (in order):
1. `process.nextTick` callbacks
2. Promise microtasks (`.then`, `await`)

```js
setTimeout(() => console.log('setTimeout'), 0);
setImmediate(() => console.log('setImmediate'));
Promise.resolve().then(() => console.log('Promise'));
process.nextTick(() => console.log('nextTick'));
console.log('sync');

// Output:
// sync
// nextTick
// Promise
// setTimeout  (or setImmediate first — order not guaranteed outside I/O)
// setImmediate
```

**Inside an I/O callback**, `setImmediate` always fires before `setTimeout`:

```js
const fs = require('fs');
fs.readFile(__filename, () => {
  setTimeout(() => console.log('timeout'), 0);
  setImmediate(() => console.log('immediate'));
  // Always: immediate → timeout
});
```

---

### `process.nextTick` vs `setImmediate` vs `queueMicrotask`

| | When it runs | Use case |
|---|---|---|
| `process.nextTick` | Before next event loop phase (before Promises) | Emit events after current call stack clears |
| `queueMicrotask` / Promise | After `nextTick`, before next phase | Async-like behavior without the overhead |
| `setImmediate` | Check phase (after I/O callbacks) | Defer work to after I/O is processed |
| `setTimeout(fn, 0)` | Timers phase | Minimum ~1ms delay, less predictable than `setImmediate` |

**`process.nextTick` can starve the event loop** — recursive calls prevent I/O callbacks from ever running:

```js
// Dangerous — starves I/O
function recursiveTick() {
  process.nextTick(recursiveTick);
}
```

---

## 2. Module System

### CommonJS (`require`)

CommonJS modules are **synchronous**, **cached** after first load, and evaluated at runtime.

```js
// math.js
function add(a, b) { return a + b; }
module.exports = { add };

// main.js
const { add } = require('./math');  // .js extension optional
const path = require('path');       // built-in
const lodash = require('lodash');   // node_modules
```

**`require` resolution algorithm:**
1. If starts with `./`, `../`, `/` — load as file/directory
2. Otherwise — search `node_modules` up the directory tree
3. File lookup order: exact path → `.js` → `.json` → `.node` → `index.js`

**Module caching** — `require` returns the same object on repeated calls:

```js
// Both files get the same cached object
const a = require('./config');
const b = require('./config');
a === b; // true
```

**Circular dependencies** — Node.js handles them by returning a partially constructed export:

```js
// a.js
const b = require('./b');
console.log('a loaded, b.value =', b.value);
exports.value = 'a';

// b.js
const a = require('./a');
console.log('b loaded, a.value =', a.value); // undefined — a not finished yet
exports.value = 'b';
```

---

### ES Modules in Node.js

Use `.mjs` extension or `"type": "module"` in `package.json`. ESM is **async**, **static**, and uses **live bindings**.

```js
// math.mjs
export const add = (a, b) => a + b;
export default function multiply(a, b) { return a * b; }

// main.mjs
import multiply, { add } from './math.mjs';
import { readFile } from 'fs/promises';   // built-in ESM
```

**Top-level `await`** — available in ESM only:

```js
// config.mjs
const config = await fetch('/api/config').then(r => r.json());
export { config };
```

**Interop:**

```js
// ESM importing CJS — default import gets module.exports
import cjsModule from './legacy.cjs';

// CJS importing ESM — must use dynamic import
async function load() {
  const { add } = await import('./math.mjs');
}
```

---

## 3. File System & Path

### Async vs Sync I/O

Always prefer async I/O in servers — sync calls block the event loop for all concurrent requests.

```js
const fs = require('fs');
const fsp = require('fs/promises');

// Callback API (legacy)
fs.readFile('data.json', 'utf8', (err, data) => {
  if (err) throw err;
  console.log(JSON.parse(data));
});

// Promise API (modern — prefer this)
const data = await fsp.readFile('data.json', 'utf8');

// Sync — only acceptable in startup scripts, CLI tools, or tests
const data = fs.readFileSync('data.json', 'utf8');
```

**Common fs operations:**

```js
// Write (overwrites)
await fsp.writeFile('output.txt', content, 'utf8');

// Append
await fsp.appendFile('log.txt', `${line}\n`);

// Check existence (avoid TOCTOU — just try and catch ENOENT)
try {
  await fsp.access('file.txt');
} catch { /* doesn't exist */ }

// Directory operations
await fsp.mkdir('dir/sub', { recursive: true });
const entries = await fsp.readdir('dir', { withFileTypes: true });
entries.filter(e => e.isFile()).map(e => e.name);

// Copy, rename, delete
await fsp.copyFile('a.txt', 'b.txt');
await fsp.rename('old.txt', 'new.txt');
await fsp.rm('dir', { recursive: true, force: true });

// File metadata
const stat = await fsp.stat('file.txt');
stat.size;  stat.mtime;  stat.isDirectory();

// Watch for changes
const watcher = fsp.watch('src', { recursive: true });
for await (const { eventType, filename } of watcher) {
  console.log(eventType, filename);
}
```

---

### `path` Module

```js
const path = require('path');

path.join('src', 'utils', 'helpers.js');   // 'src/utils/helpers.js'
path.resolve('src', '../lib');             // absolute path
path.dirname('/src/utils/helpers.js');     // '/src/utils'
path.basename('/src/utils/helpers.js');    // 'helpers.js'
path.extname('helpers.js');               // '.js'
path.parse('/src/utils/helpers.js');
// { root: '/', dir: '/src/utils', base: 'helpers.js', ext: '.js', name: 'helpers' }

// __dirname is not available in ESM — use this instead:
import { fileURLToPath } from 'url';
import { dirname } from 'path';
const __dirname = dirname(fileURLToPath(import.meta.url));
```

---

## 4. Streams

Streams process data in chunks — memory usage stays constant regardless of data size. Essential for large files, HTTP request/response bodies, and real-time data pipelines.

### Four Stream Types

| Type | Description | Example |
|---|---|---|
| `Readable` | Source of data | `fs.createReadStream`, `http.IncomingMessage` |
| `Writable` | Destination | `fs.createWriteStream`, `http.ServerResponse` |
| `Duplex` | Both readable and writable | TCP socket |
| `Transform` | Duplex that transforms data | `zlib.createGzip`, `crypto.createCipheriv` |

---

### Backpressure

Backpressure prevents a fast Readable from overwhelming a slow Writable. `pipe` and `pipeline` handle this automatically.

```js
const { pipeline } = require('stream/promises');
const { createReadStream, createWriteStream } = require('fs');
const { createGzip } = require('zlib');

// pipeline handles backpressure and error propagation automatically
await pipeline(
  createReadStream('large.csv'),
  createGzip(),
  createWriteStream('large.csv.gz')
);
```

**Manual backpressure** — when `write()` returns `false`, pause the source:

```js
readable.on('data', (chunk) => {
  const canContinue = writable.write(chunk);
  if (!canContinue) {
    readable.pause();
    writable.once('drain', () => readable.resume());
  }
});
```

---

### Custom Streams

```js
const { Readable, Transform } = require('stream');

// Custom Readable — push data on demand
class CounterStream extends Readable {
  constructor(max) {
    super({ objectMode: true });
    this.current = 0;
    this.max = max;
  }

  _read() {
    if (this.current < this.max) {
      this.push(this.current++);
    } else {
      this.push(null); // signal end
    }
  }
}

// Custom Transform
class DoubleTransform extends Transform {
  constructor() { super({ objectMode: true }); }

  _transform(chunk, _encoding, callback) {
    this.push(chunk * 2);
    callback();
  }
}

await pipeline(
  new CounterStream(5),
  new DoubleTransform(),
  async function* (source) {
    for await (const val of source) console.log(val); // 0,2,4,6,8
  }
);
```

---

### Async Iteration over Streams

```js
const { createReadStream } = require('fs');
const readline = require('readline');

const rl = readline.createInterface({
  input: createReadStream('large.log'),
  crlfDelay: Infinity,
});

for await (const line of rl) {
  if (line.includes('ERROR')) console.log(line);
}
```

---

## 5. Buffers & Encoding

A `Buffer` is a fixed-length allocation of raw memory outside the V8 heap. Used for binary data: file I/O, TCP streams, cryptography.

```js
// Create
const buf1 = Buffer.alloc(10);                  // 10 zeroed bytes
const buf2 = Buffer.allocUnsafe(10);            // 10 uninitialized bytes (faster)
const buf3 = Buffer.from('hello', 'utf8');
const buf4 = Buffer.from([0x68, 0x65, 0x6c]);   // from byte array

// Convert
buf3.toString('utf8');    // 'hello'
buf3.toString('hex');     // '68656c6c6f'
buf3.toString('base64');  // 'aGVsbG8='

// Operations
const combined = Buffer.concat([buf3, buf4]);
buf3.slice(1, 3);          // deprecated — use subarray
buf3.subarray(1, 3);       // 'el'
buf3.equals(buf4);         // false
buf3.indexOf('ll');        // 2

// JSON serialization
JSON.stringify(buf3);      // {"type":"Buffer","data":[104,101,108,108,111]}
Buffer.from(JSON.parse(json).data); // restore

// Safe allocation — always prefer alloc over allocUnsafe unless benchmarked
// allocUnsafe may contain sensitive data from previously deallocated memory
```

---

## 6. Networking

### HTTP Server

```js
const http = require('http');

const server = http.createServer((req, res) => {
  const { method, url, headers } = req;

  let body = '';
  req.on('data', (chunk) => { body += chunk; });
  req.on('end', () => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ method, url, body }));
  });
});

server.listen(3000, () => console.log('Listening on :3000'));
```

### HTTP Client with Keep-Alive

```js
const http = require('http');

// Reuse TCP connections — critical for performance under load
const agent = new http.Agent({
  keepAlive: true,
  maxSockets: 50,       // per host
  maxFreeSockets: 10,
});

function get(url) {
  return new Promise((resolve, reject) => {
    http.get(url, { agent }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}
```

### TCP Socket

```js
const net = require('net');

// Server
const server = net.createServer((socket) => {
  console.log('client connected');
  socket.on('data', (data) => {
    socket.write(`echo: ${data}`);
  });
  socket.on('end', () => console.log('client disconnected'));
});
server.listen(8080);

// Client
const client = net.connect({ port: 8080 }, () => {
  client.write('hello');
});
client.on('data', (data) => console.log(data.toString()));
```

---

## 7. Child Processes

Node.js can spawn child processes to run shell commands, scripts, or other Node programs.

| Method | Use case | Shell | Buffered |
|---|---|---|---|
| `spawn` | Long-running, streamed output | No | No |
| `exec` | Short commands, captured output | Yes | Yes |
| `execFile` | Executable without shell | No | Yes |
| `fork` | Another Node.js script with IPC | No | No |

```js
const { spawn, exec, fork } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

// spawn — streaming output (good for large output)
const ls = spawn('ls', ['-la', '/tmp']);
ls.stdout.on('data', (data) => process.stdout.write(data));
ls.on('close', (code) => console.log(`exited ${code}`));

// exec — buffered output (easy for small output)
const { stdout } = await execAsync('git log --oneline -5');
console.log(stdout);

// fork — Node.js child with IPC channel
const child = fork('./worker.js');
child.send({ type: 'START', payload: data });
child.on('message', (msg) => console.log('from child:', msg));
child.on('exit', (code) => console.log('worker exited:', code));

// worker.js
process.on('message', (msg) => {
  if (msg.type === 'START') {
    const result = heavyComputation(msg.payload);
    process.send({ type: 'RESULT', result });
  }
});
```

---

## 8. Worker Threads

Worker threads run JavaScript in parallel OS threads. Use for CPU-bound work (image processing, encryption, parsing) to avoid blocking the event loop.

```js
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

// main.js
if (isMainThread) {
  function runWorker(data) {
    return new Promise((resolve, reject) => {
      const worker = new Worker(__filename, { workerData: data });
      worker.on('message', resolve);
      worker.on('error', reject);
      worker.on('exit', (code) => {
        if (code !== 0) reject(new Error(`Worker exited with code ${code}`));
      });
    });
  }

  const result = await runWorker({ numbers: [1, 2, 3, 4, 5] });
  console.log(result); // 15
} else {
  // worker code — runs in a separate thread
  const { numbers } = workerData;
  const sum = numbers.reduce((a, b) => a + b, 0);
  parentPort.postMessage(sum);
}
```

### SharedArrayBuffer — Zero-Copy Shared Memory

```js
// Share memory between threads without copying
const shared = new SharedArrayBuffer(4);
const arr = new Int32Array(shared);

const worker = new Worker('./worker.js', {
  workerData: { buffer: shared }
});

// Atomic operations prevent race conditions
Atomics.add(arr, 0, 1);
Atomics.load(arr, 0); // read safely
Atomics.wait(arr, 0, 0); // block until arr[0] !== 0
Atomics.notify(arr, 0, 1); // wake one waiting thread
```

### Worker Pool Pattern

```js
const { Worker } = require('worker_threads');
const os = require('os');

class WorkerPool {
  constructor(script, size = os.cpus().length) {
    this.workers = Array.from({ length: size }, () => ({
      worker: new Worker(script),
      busy: false,
    }));
    this.queue = [];
  }

  run(data) {
    return new Promise((resolve, reject) => {
      const free = this.workers.find((w) => !w.busy);
      if (free) {
        this.#dispatch(free, data, resolve, reject);
      } else {
        this.queue.push({ data, resolve, reject });
      }
    });
  }

  #dispatch(entry, data, resolve, reject) {
    entry.busy = true;
    entry.worker.once('message', (result) => {
      entry.busy = false;
      resolve(result);
      if (this.queue.length) {
        const next = this.queue.shift();
        this.#dispatch(entry, next.data, next.resolve, next.reject);
      }
    });
    entry.worker.once('error', reject);
    entry.worker.postMessage(data);
  }
}
```

---

## 9. Cluster Module

The cluster module forks multiple Node.js processes sharing the same server port, distributing incoming connections across all workers (round-robin on most platforms).

```js
const cluster = require('cluster');
const http = require('http');
const os = require('os');

if (cluster.isPrimary) {
  const numCPUs = os.cpus().length;
  console.log(`Primary ${process.pid} starting ${numCPUs} workers`);

  for (let i = 0; i < numCPUs; i++) cluster.fork();

  // Auto-restart crashed workers
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died (${signal || code}). Restarting...`);
    cluster.fork();
  });

  // Zero-downtime restart — kill workers one by one
  process.on('SIGUSR2', () => {
    const workers = Object.values(cluster.workers);
    let i = 0;
    function restartNext() {
      if (i >= workers.length) return;
      const worker = workers[i++];
      worker.once('exit', () => {
        cluster.fork().once('listening', restartNext);
      });
      worker.kill('SIGTERM');
    }
    restartNext();
  });
} else {
  http.createServer((req, res) => {
    res.end(`Hello from worker ${process.pid}`);
  }).listen(3000);
}
```

**Cluster vs Worker Threads:**
- **Cluster** — multiple Node.js processes, each with its own V8 and event loop. Better isolation, suited for I/O-heavy workloads. No shared memory.
- **Worker Threads** — multiple threads in one process, shared memory via `SharedArrayBuffer`. Suited for CPU-heavy work.

---

## 10. Events & EventEmitter

`EventEmitter` is the backbone of Node.js's async model. Streams, HTTP servers, and most core APIs extend it.

```js
const { EventEmitter } = require('events');

class OrderService extends EventEmitter {
  async placeOrder(order) {
    const saved = await saveToDb(order);
    this.emit('order:placed', saved);
    return saved;
  }
}

const service = new OrderService();

// on — persistent listener
service.on('order:placed', (order) => sendConfirmationEmail(order));

// once — fires once then auto-removes
service.once('order:placed', (order) => console.log('First order!', order.id));

// off / removeListener
const handler = (order) => notifyWarehouse(order);
service.on('order:placed', handler);
service.off('order:placed', handler); // remove specific listener

// Error events — MUST have a listener or Node throws
service.on('error', (err) => console.error('OrderService error:', err));
service.emit('error', new Error('DB connection lost'));
```

### Memory Leak Warning

`EventEmitter` warns (but doesn't throw) if more than 10 listeners are added to the same event — usually indicates a leaked listener in a loop.

```js
emitter.setMaxListeners(50);    // increase limit
emitter.setMaxListeners(0);     // disable warning

// Check current listeners
emitter.listenerCount('data');
emitter.listeners('data');
emitter.eventNames();
```

### `EventEmitter` as a Pub/Sub bus

```js
const bus = new EventEmitter();
bus.setMaxListeners(100);

// Any module can publish/subscribe without direct coupling
bus.on('user:created', async ({ id }) => {
  await sendWelcomeEmail(id);
});

bus.on('user:created', async ({ id }) => {
  await createDefaultSettings(id);
});

// Publisher doesn't know who is listening
bus.emit('user:created', { id: 42, email: 'alice@example.com' });
```

---

# Part 2: Express & Fastify

---

## 11. Express Fundamentals

### Routing & Middleware

Express middleware are functions with signature `(req, res, next)`. They run in order — call `next()` to pass to the next middleware, `next(err)` to jump to error middleware.

```js
const express = require('express');
const app = express();

// Built-in middleware
app.use(express.json());                          // parse JSON body
app.use(express.urlencoded({ extended: true })); // parse form body
app.use(express.static('public'));               // serve static files

// Custom middleware — logging
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
});

// Route handlers
app.get('/users', async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const users = await userService.findAll({ page: +page, limit: +limit });
    res.json(users);
  } catch (err) {
    next(err); // pass to error middleware
  }
});

app.get('/users/:id', async (req, res, next) => {
  try {
    const user = await userService.findById(req.params.id);
    if (!user) return res.status(404).json({ error: 'Not found' });
    res.json(user);
  } catch (err) {
    next(err);
  }
});

app.post('/users', async (req, res, next) => {
  try {
    const user = await userService.create(req.body);
    res.status(201).json(user);
  } catch (err) {
    next(err);
  }
});
```

### Router

```js
// routes/users.js
const router = express.Router();

router.use(authenticate); // middleware scoped to this router

router
  .route('/')
  .get(listUsers)
  .post(createUser);

router
  .route('/:id')
  .get(getUser)
  .put(updateUser)
  .delete(deleteUser);

module.exports = router;

// app.js
app.use('/api/users', require('./routes/users'));
```

### Error Middleware

Error middleware has **4 parameters** — Express identifies it by arity.

```js
// 404 handler — must be after all routes
app.use((req, res) => {
  res.status(404).json({ error: `Route ${req.method} ${req.url} not found` });
});

// Error handler — must be last, must have 4 params
app.use((err, req, res, next) => {
  console.error(err);

  if (err.name === 'ValidationError') {
    return res.status(400).json({ error: err.message });
  }
  if (err.name === 'UnauthorizedError') {
    return res.status(401).json({ error: 'Invalid token' });
  }

  res.status(err.statusCode ?? 500).json({
    error: process.env.NODE_ENV === 'production' ? 'Internal error' : err.message,
  });
});
```

---

## 12. Fastify

Fastify is a high-performance alternative to Express. Key advantages: schema-based validation/serialization (JSON Schema → Ajv), plugin encapsulation, built-in TypeScript support, ~2x faster than Express.

```js
const fastify = require('fastify')({ logger: true });

// Schema-based route — validates input, serializes output faster
fastify.post('/users', {
  schema: {
    body: {
      type: 'object',
      required: ['name', 'email'],
      properties: {
        name: { type: 'string', minLength: 1 },
        email: { type: 'string', format: 'email' },
      },
    },
    response: {
      201: {
        type: 'object',
        properties: {
          id: { type: 'integer' },
          name: { type: 'string' },
          email: { type: 'string' },
        },
      },
    },
  },
  handler: async (request, reply) => {
    const user = await userService.create(request.body);
    reply.status(201).send(user);
  },
});

await fastify.listen({ port: 3000 });
```

### Plugins & Encapsulation

Fastify uses a plugin system where each plugin gets its own encapsulated scope. Decorators, hooks, and routes registered in a plugin are scoped unless explicitly exposed.

```js
// Database plugin
fastify.register(async (instance) => {
  const pool = createPool(config.database);
  instance.decorate('db', pool);
  instance.addHook('onClose', async () => pool.end());
});

// Routes plugin — has access to fastify.db via closure
fastify.register(async (instance) => {
  instance.get('/users', async (req) => {
    return instance.db.query('SELECT * FROM users');
  });
}, { prefix: '/api' });
```

### Hooks

```js
fastify.addHook('onRequest', async (request, reply) => {
  // authenticate before handler
});

fastify.addHook('preHandler', async (request, reply) => {
  // runs after parsing, before route handler
});

fastify.addHook('onSend', async (request, reply, payload) => {
  // transform response payload
  return payload;
});

fastify.addHook('onError', async (request, reply, error) => {
  // log errors
});
```

---

## 13. REST API Patterns

### Request Validation

Always validate at the boundary. Never trust `req.body`.

```js
const { z } = require('zod');

const createUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(0).max(150).optional(),
});

function validate(schema) {
  return (req, res, next) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({
        error: 'Validation failed',
        issues: result.error.issues,
      });
    }
    req.body = result.data; // replace with parsed (coerced) data
    next();
  };
}

app.post('/users', validate(createUserSchema), createUserHandler);
```

### Pagination

```js
// Cursor-based (recommended for large datasets — stable, no skipped/duplicate rows)
app.get('/posts', async (req, res) => {
  const { cursor, limit = 20 } = req.query;
  const posts = await db.query(
    `SELECT * FROM posts WHERE id > $1 ORDER BY id LIMIT $2`,
    [cursor ?? 0, Math.min(+limit, 100)]
  );
  res.json({
    data: posts,
    nextCursor: posts.at(-1)?.id ?? null,
    hasMore: posts.length === +limit,
  });
});

// Offset-based (simpler, but inconsistent if rows added/removed mid-pagination)
app.get('/users', async (req, res) => {
  const page = Math.max(1, +req.query.page || 1);
  const limit = Math.min(100, +req.query.limit || 20);
  const offset = (page - 1) * limit;

  const [rows, [{ count }]] = await Promise.all([
    db.query('SELECT * FROM users LIMIT $1 OFFSET $2', [limit, offset]),
    db.query('SELECT COUNT(*) FROM users'),
  ]);

  res.json({
    data: rows,
    pagination: { page, limit, total: +count, pages: Math.ceil(count / limit) },
  });
});
```

### API Versioning

```js
// URL versioning (most common, explicit)
app.use('/api/v1', v1Router);
app.use('/api/v2', v2Router);

// Header versioning
app.use((req, res, next) => {
  req.apiVersion = req.headers['api-version'] ?? 'v1';
  next();
});
```

---

## 14. Authentication

### JWT

```js
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET;
const JWT_EXPIRES_IN = '15m';
const REFRESH_EXPIRES_IN = '7d';

// Issue tokens
function issueTokens(userId) {
  const accessToken = jwt.sign({ sub: userId }, JWT_SECRET, {
    expiresIn: JWT_EXPIRES_IN,
  });
  const refreshToken = jwt.sign({ sub: userId, type: 'refresh' }, JWT_SECRET, {
    expiresIn: REFRESH_EXPIRES_IN,
  });
  return { accessToken, refreshToken };
}

// Middleware
function authenticate(req, res, next) {
  const header = req.headers.authorization;
  if (!header?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing token' });
  }
  try {
    const payload = jwt.verify(header.slice(7), JWT_SECRET);
    req.user = payload;
    next();
  } catch (err) {
    const msg = err.name === 'TokenExpiredError' ? 'Token expired' : 'Invalid token';
    res.status(401).json({ error: msg });
  }
}

// Refresh endpoint
app.post('/auth/refresh', async (req, res) => {
  const { refreshToken } = req.body;
  try {
    const payload = jwt.verify(refreshToken, JWT_SECRET);
    if (payload.type !== 'refresh') throw new Error('Not a refresh token');

    // Check token hasn't been revoked (store revoked tokens in Redis/DB)
    const isRevoked = await tokenStore.isRevoked(refreshToken);
    if (isRevoked) return res.status(401).json({ error: 'Token revoked' });

    res.json(issueTokens(payload.sub));
  } catch {
    res.status(401).json({ error: 'Invalid refresh token' });
  }
});
```

### Sessions

```js
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const { createClient } = require('redis');

const redisClient = createClient({ url: process.env.REDIS_URL });
await redisClient.connect();

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production', // HTTPS only in prod
    httpOnly: true,   // no JS access — prevents XSS token theft
    sameSite: 'lax',  // CSRF protection
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  },
}));
```

---

## 15. Security

### Helmet

Sets security-relevant HTTP headers.

```js
const helmet = require('helmet');
app.use(helmet()); // sets CSP, HSTS, X-Frame-Options, etc.

// Custom CSP
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", 'cdn.example.com'],
    styleSrc: ["'self'", "'unsafe-inline'"],
  },
}));
```

### Rate Limiting

```js
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');

// Global rate limit
app.use(rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  store: new RedisStore({ client: redisClient }), // distributed — works across cluster
}));

// Stricter limit on auth endpoints
app.use('/api/auth', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  message: { error: 'Too many auth attempts' },
}));
```

### CORS

```js
const cors = require('cors');

app.use(cors({
  origin: (origin, callback) => {
    const allowed = ['https://app.example.com', 'https://admin.example.com'];
    if (!origin || allowed.includes(origin)) callback(null, true);
    else callback(new Error('Not allowed by CORS'));
  },
  credentials: true,      // allow cookies/auth headers cross-origin
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
```

### OWASP Top 10 in Node.js

| Vulnerability | Prevention |
|---|---|
| Injection (SQL, NoSQL, command) | Parameterized queries, never concatenate user input into queries/commands |
| Broken Authentication | Short-lived JWTs, secure session config, MFA |
| Sensitive Data Exposure | HTTPS, encrypt at rest, never log passwords/tokens |
| XSS | CSP header, sanitize HTML output, `httpOnly` cookies |
| CSRF | `sameSite` cookies, CSRF tokens for non-GET state changes |
| Security Misconfiguration | `helmet`, disable `X-Powered-By`, least-privilege file perms |
| Insecure Deserialization | Validate/schema-check all deserialized data |
| Known Vulnerabilities | `npm audit`, `npm audit fix`, dependency scanning in CI |
| Prototype Pollution | Avoid `merge(obj, userInput)`, use `Object.create(null)` for dicts |
| Path Traversal | `path.resolve` + check result stays within allowed directory |

---

# Part 3: NestJS

---

## 16. Core Concepts

NestJS is an opinionated Node.js framework built on top of Express (or Fastify), using TypeScript and heavy decorator usage for structuring applications.

### Modules

Modules organize the application. Every app has at least one root module.

```ts
@Module({
  imports: [TypeOrmModule.forFeature([User])], // import other modules
  controllers: [UsersController],              // handle incoming requests
  providers: [UsersService, UsersRepository],  // injectable services
  exports: [UsersService],                     // expose to importing modules
})
export class UsersModule {}

// Root module
@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    DatabaseModule,
    UsersModule,
    AuthModule,
  ],
})
export class AppModule {}
```

### Controllers

```ts
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll(@Query() query: PaginationDto): Promise<User[]> {
    return this.usersService.findAll(query);
  }

  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number): Promise<User> {
    return this.usersService.findOne(id);
  }

  @Post()
  @HttpCode(201)
  create(@Body() dto: CreateUserDto): Promise<User> {
    return this.usersService.create(dto);
  }

  @Patch(':id')
  update(
    @Param('id', ParseIntPipe) id: number,
    @Body() dto: UpdateUserDto,
  ): Promise<User> {
    return this.usersService.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(204)
  remove(@Param('id', ParseIntPipe) id: number): Promise<void> {
    return this.usersService.remove(id);
  }
}
```

### Providers & Dependency Injection

```ts
@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly repo: Repository<User>,
    private readonly config: ConfigService,
    private readonly mailer: MailService,
  ) {}

  async create(dto: CreateUserDto): Promise<User> {
    const user = this.repo.create(dto);
    await this.repo.save(user);
    await this.mailer.sendWelcome(user.email);
    return user;
  }
}
```

**Custom providers** for factory logic, existing values, or conditional implementations:

```ts
@Module({
  providers: [
    // Factory provider
    {
      provide: 'CACHE_CLIENT',
      useFactory: (config: ConfigService) =>
        createClient({ url: config.get('REDIS_URL') }),
      inject: [ConfigService],
    },
    // Value provider
    {
      provide: 'APP_VERSION',
      useValue: process.env.npm_package_version,
    },
    // Class provider — swap implementations per env
    {
      provide: PaymentService,
      useClass: process.env.NODE_ENV === 'test' ? MockPaymentService : StripePaymentService,
    },
  ],
})
export class AppModule {}
```

---

## 17. Guards, Interceptors, Pipes, Filters

The NestJS request lifecycle:

```
Incoming request
  → Middleware
  → Guards          (can/cannot access this route?)
  → Interceptors     (pre-handler)
  → Pipes            (transform/validate params)
  → Route Handler
  → Interceptors     (post-handler — transform response)
  → Exception Filters (if exception thrown)
→ Outgoing response
```

### Guards

```ts
@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private jwtService: JwtService) {}

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const token = request.headers.authorization?.split(' ')[1];
    if (!token) throw new UnauthorizedException();

    try {
      request.user = this.jwtService.verify(token);
      return true;
    } catch {
      throw new UnauthorizedException('Invalid token');
    }
  }
}

// Apply to a single route
@UseGuards(JwtAuthGuard)
@Get('profile')
getProfile(@Request() req) { return req.user; }

// Apply globally
app.useGlobalGuards(new JwtAuthGuard(jwtService));
```

### Interceptors

```ts
@Injectable()
export class TransformInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      map((data) => ({ success: true, data, timestamp: new Date().toISOString() }))
    );
  }
}

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const req = context.switchToHttp().getRequest();
    const start = Date.now();
    return next.handle().pipe(
      tap(() => console.log(`${req.method} ${req.url} — ${Date.now() - start}ms`))
    );
  }
}
```

### Pipes

```ts
// Built-in pipes: ValidationPipe, ParseIntPipe, ParseBoolPipe, ParseUUIDPipe

// Global validation pipe — apply at bootstrap
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,        // strip unknown properties
  forbidNonWhitelisted: true,
  transform: true,        // auto-transform payloads to DTO types
  transformOptions: { enableImplicitConversion: true },
}));

// DTO with class-validator
import { IsEmail, IsString, MinLength, IsOptional, IsInt, Min } from 'class-validator';

export class CreateUserDto {
  @IsString()
  @MinLength(1)
  name: string;

  @IsEmail()
  email: string;

  @IsInt()
  @Min(0)
  @IsOptional()
  age?: number;
}
```

### Exception Filters

```ts
@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();
    const status = exception.getStatus();

    response.status(status).json({
      statusCode: status,
      timestamp: new Date().toISOString(),
      path: request.url,
      message: exception.message,
    });
  }
}

// Catch everything
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const status = exception instanceof HttpException
      ? exception.getStatus()
      : HttpStatus.INTERNAL_SERVER_ERROR;
    // ...
  }
}
```

---

## 18. Database Integration

### TypeORM with NestJS

```ts
// app.module.ts
TypeOrmModule.forRootAsync({
  inject: [ConfigService],
  useFactory: (config: ConfigService) => ({
    type: 'postgres',
    url: config.get('DATABASE_URL'),
    entities: [__dirname + '/**/*.entity{.ts,.js}'],
    migrations: [__dirname + '/migrations/*{.ts,.js}'],
    migrationsRun: true,
    ssl: config.get('NODE_ENV') === 'production',
  }),
})

// user.entity.ts
@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  email: string;

  @Column()
  name: string;

  @CreateDateColumn()
  createdAt: Date;

  @OneToMany(() => Post, (post) => post.author)
  posts: Post[];
}
```

### Prisma with NestJS

```ts
// prisma.service.ts
@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  async onModuleInit() { await this.$connect(); }
}

// users.service.ts
@Injectable()
export class UsersService {
  constructor(private prisma: PrismaService) {}

  findAll(params: { page: number; limit: number }) {
    return this.prisma.user.findMany({
      skip: (params.page - 1) * params.limit,
      take: params.limit,
      orderBy: { createdAt: 'desc' },
      include: { posts: { take: 3 } },
    });
  }
}
```

---

## 19. Microservices

NestJS supports multiple transport layers for microservice communication.

```ts
// TCP transport
const app = await NestFactory.createMicroservice<MicroserviceOptions>(AppModule, {
  transport: Transport.TCP,
  options: { port: 3001 },
});

// Message handler
@MessagePattern('users.findOne')
findOne(@Payload() data: { id: number }) {
  return this.usersService.findOne(data.id);
}

// Client in another service
@Client({ transport: Transport.TCP, options: { port: 3001 } })
private client: ClientProxy;

async getUser(id: number) {
  return this.client.send('users.findOne', { id }).toPromise();
}
```

**Redis Pub/Sub transport** — for event-driven communication:

```ts
{ transport: Transport.REDIS, options: { url: process.env.REDIS_URL } }

// Event pattern — fire and forget
@EventPattern('user.created')
handleUserCreated(@Payload() event: UserCreatedEvent) {
  return this.emailService.sendWelcome(event.email);
}

this.client.emit('user.created', { id: user.id, email: user.email });
```

---

# Part 4: Database Patterns

---

## 20. Connection Pooling

Opening a database connection is expensive (TCP handshake, auth, memory). A **connection pool** maintains a set of open connections that requests borrow and return.

```js
// pg (node-postgres)
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,              // maximum pool size
  min: 2,               // keep at least 2 connections open
  idleTimeoutMillis: 30_000,  // close idle connections after 30s
  connectionTimeoutMillis: 2_000, // fail fast if no connection available
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Pool handles connection lifecycle automatically
const { rows } = await pool.query('SELECT * FROM users WHERE id = $1', [id]);

// Explicit client — for transactions
const client = await pool.connect();
try {
  await client.query('BEGIN');
  // ... queries
  await client.query('COMMIT');
} catch (err) {
  await client.query('ROLLBACK');
  throw err;
} finally {
  client.release(); // return to pool
}
```

**Pool sizing rule of thumb:** `pool_size = num_cores * 2 + effective_spindle_count`. For Postgres, the server's `max_connections` is the hard ceiling — divide it across all app instances.

---

## 21. Query Patterns

### The N+1 Problem

```js
// BAD — N+1: 1 query for posts, N queries for each author
const posts = await db.query('SELECT * FROM posts');
for (const post of posts) {
  post.author = await db.query('SELECT * FROM users WHERE id = $1', [post.userId]);
}

// GOOD — 2 queries: 1 for posts, 1 for all authors
const posts = await db.query('SELECT * FROM posts');
const authorIds = [...new Set(posts.map((p) => p.userId))];
const authors = await db.query('SELECT * FROM users WHERE id = ANY($1)', [authorIds]);
const authorsById = Object.fromEntries(authors.map((a) => [a.id, a]));
posts.forEach((p) => { p.author = authorsById[p.userId]; });

// BEST — single JOIN query
const posts = await db.query(`
  SELECT p.*, u.name AS author_name, u.email AS author_email
  FROM posts p
  JOIN users u ON u.id = p.user_id
`);
```

### Eager vs Lazy Loading

- **Eager loading** — fetch related data in the same query (JOIN or `include` in ORM). Use when you know you'll always need the relation.
- **Lazy loading** — fetch related data only when accessed. Use for optional relations or when relations are rarely needed.

```ts
// TypeORM eager
@OneToMany(() => Post, (post) => post.author, { eager: true })
posts: Post[];

// Prisma explicit include (always eager — Prisma has no lazy loading)
const user = await prisma.user.findUnique({
  where: { id },
  include: { posts: true },
});

// TypeORM lazy — returns a Promise
@OneToMany(() => Post, (post) => post.author, { lazy: true })
posts: Promise<Post[]>;
const posts = await user.posts; // fetches on first access
```

---

## 22. Transactions

### ACID Properties

| Property | Meaning |
|---|---|
| **Atomicity** | All operations succeed or all are rolled back |
| **Consistency** | DB moves from one valid state to another |
| **Isolation** | Concurrent transactions don't interfere |
| **Durability** | Committed data survives crashes |

### Isolation Levels

| Level | Dirty Reads | Non-Repeatable Reads | Phantom Reads |
|---|---|---|---|
| Read Uncommitted | Possible | Possible | Possible |
| Read Committed (default PG) | No | Possible | Possible |
| Repeatable Read | No | No | Possible |
| Serializable | No | No | No |

```js
// Set isolation level
await client.query('BEGIN ISOLATION LEVEL SERIALIZABLE');
```

### Deadlock Prevention

A deadlock occurs when two transactions each hold a lock the other needs.

```js
// BAD — transaction A locks users then orders; B locks orders then users
// → deadlock

// GOOD — always acquire locks in the same order
async function transfer(fromId, toId, amount) {
  const [id1, id2] = [fromId, toId].sort(); // consistent order
  await client.query('BEGIN');
  await client.query('SELECT * FROM accounts WHERE id = $1 FOR UPDATE', [id1]);
  await client.query('SELECT * FROM accounts WHERE id = $1 FOR UPDATE', [id2]);
  // ... debit/credit
  await client.query('COMMIT');
}
```

---

## 23. Migrations

Database migrations version-control schema changes so they can be applied and rolled back in sequence.

```js
// Knex migration
exports.up = async (knex) => {
  await knex.schema.createTable('users', (table) => {
    table.increments('id').primary();
    table.string('email').notNullable().unique();
    table.string('name').notNullable();
    table.timestamps(true, true);
  });
};

exports.down = async (knex) => {
  await knex.schema.dropTable('users');
};
```

**Best practices:**
- Migrations are **append-only** — never edit a migration that has been run in production
- Each migration should be **idempotent** where possible (`CREATE TABLE IF NOT EXISTS`)
- Large table changes (adding NOT NULL columns, building indexes) need **online/concurrent** DDL to avoid table locks:

```sql
-- Add a nullable column first, backfill, then add NOT NULL constraint
ALTER TABLE users ADD COLUMN score INTEGER;
UPDATE users SET score = 0 WHERE score IS NULL;
ALTER TABLE users ALTER COLUMN score SET NOT NULL;

-- Build index without locking table (Postgres)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

---

# Part 5: Production & DevOps

---

## 24. Environment & Config

### 12-Factor App Config

Store config in environment variables, not in code. Never commit `.env` files to git.

```js
// config.js — validate at startup with Zod
const { z } = require('zod');

const schema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  REDIS_URL: z.string().url().optional(),
});

const result = schema.safeParse(process.env);
if (!result.success) {
  console.error('Invalid environment variables:');
  console.error(result.error.format());
  process.exit(1);
}

module.exports = result.data;
```

**Load order:**
1. `process.env` (set by OS/Docker/K8s)
2. `.env.local` (local overrides, gitignored)
3. `.env.{NODE_ENV}` (environment-specific defaults)
4. `.env` (base defaults)

```js
require('dotenv').config({ path: `.env.${process.env.NODE_ENV}` });
require('dotenv').config(); // base defaults
```

---

## 25. Logging

### Structured Logging with Pino

Pino is the fastest Node.js logger. Always log JSON in production for log aggregator compatibility.

```js
const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  // Pretty-print in dev, JSON in production
  transport: process.env.NODE_ENV !== 'production'
    ? { target: 'pino-pretty' }
    : undefined,
  base: { service: 'api', version: process.env.npm_package_version },
  redact: ['req.headers.authorization', 'body.password'], // never log secrets
});

// Child loggers — inherit parent config, add context
const requestLogger = logger.child({ requestId: req.id });
requestLogger.info({ userId: req.user.id }, 'User profile fetched');
```

### Correlation IDs

Trace a request across services by propagating a unique ID through every log entry.

```js
const { AsyncLocalStorage } = require('async_hooks');
const { randomUUID } = require('crypto');

const storage = new AsyncLocalStorage();

// Middleware — assign request ID
app.use((req, res, next) => {
  const requestId = req.headers['x-request-id'] ?? randomUUID();
  res.setHeader('x-request-id', requestId);
  storage.run({ requestId }, next);
});

// Logger that picks up the current request context
function log(level, message, data = {}) {
  const ctx = storage.getStore() ?? {};
  logger[level]({ ...ctx, ...data }, message);
}

// In any service — no need to pass requestId manually
log('info', 'Sending email', { to: user.email });
```

### Log Levels

| Level | Use case |
|---|---|
| `fatal` | App is about to crash |
| `error` | Unexpected error, needs attention |
| `warn` | Degraded state, not an error yet |
| `info` | Normal operational events |
| `debug` | Diagnostic, disable in production |
| `trace` | Very verbose, per-request detail |

---

## 26. Graceful Shutdown

A graceful shutdown lets in-flight requests complete before the process exits. Critical for zero-downtime deploys.

```js
const server = app.listen(3000);

let shuttingDown = false;

async function shutdown(signal) {
  if (shuttingDown) return;
  shuttingDown = true;

  console.log(`Received ${signal}. Shutting down gracefully...`);

  // Stop accepting new connections
  server.close(async () => {
    try {
      // Close resources in reverse order of acquisition
      await dbPool.end();
      await redisClient.quit();
      console.log('Shutdown complete');
      process.exit(0);
    } catch (err) {
      console.error('Error during shutdown:', err);
      process.exit(1);
    }
  });

  // Force exit if shutdown takes too long
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 30_000);
}

// Kubernetes sends SIGTERM before killing the pod
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));   // Ctrl+C in dev

// Health check — report unhealthy immediately on SIGTERM
// so load balancer stops sending traffic
app.get('/health', (req, res) => {
  if (shuttingDown) return res.status(503).json({ status: 'shutting_down' });
  res.json({ status: 'ok' });
});
```

---

## 27. Process Management

### PM2

PM2 is a production process manager for Node.js: clustering, auto-restart, log management.

```js
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'api',
    script: 'dist/main.js',
    instances: 'max',          // one per CPU core
    exec_mode: 'cluster',      // cluster mode — share port
    max_memory_restart: '512M',
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000,
    },
    // Graceful shutdown
    kill_timeout: 30000,
    listen_timeout: 5000,
    // Log rotation
    error_file: 'logs/error.log',
    out_file: 'logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
  }],
};
```

```bash
pm2 start ecosystem.config.js --env production
pm2 reload api          # zero-downtime reload
pm2 logs api --lines 100
pm2 monit               # real-time CPU/memory
pm2 save && pm2 startup # persist across reboots
```

### Zero-Downtime Deploys with Cluster

```bash
# With PM2
pm2 reload api  # sends SIGUSR2 to each worker, waits for new workers to be ready

# Manually with cluster
kill -SIGUSR2 <primary_pid>  # triggers the rolling restart logic from section 9
```

---

## 28. Docker

### Optimized Node.js Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first — layer caches npm install unless deps change
COPY package*.json ./
RUN npm ci --only=production

COPY tsconfig*.json ./
COPY src/ ./src/
RUN npm run build

# Production stage — smallest possible image
FROM node:20-alpine AS production

# Don't run as root
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

WORKDIR /app

COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --chown=nodejs:nodejs package.json ./

USER nodejs

EXPOSE 3000

# Use exec form (not shell form) — signal forwarded to Node, not sh
CMD ["node", "dist/main.js"]
```

**.dockerignore:**

```
node_modules
dist
.env*
*.log
.git
coverage
.nyc_output
```

**docker-compose for local dev:**

```yaml
services:
  api:
    build: .
    ports: ["3000:3000"]
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    volumes:
      - ./src:/app/src   # hot reload in dev
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

---

## 29. CI/CD

### GitHub Actions Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      - name: Type check
        run: npx tsc --noEmit

      - name: Lint
        run: npm run lint

      - name: Test
        run: npm test -- --coverage
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test
          JWT_SECRET: test-secret-at-least-32-chars-long!!

      - name: Upload coverage
        uses: codecov/codecov-action@v4

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Push to registry
        run: |
          echo ${{ secrets.REGISTRY_PASSWORD }} | docker login -u ${{ secrets.REGISTRY_USER }} --password-stdin
          docker push myapp:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Deploy to production
        run: |
          # e.g. update K8s deployment image
          kubectl set image deployment/api api=myapp:${{ github.sha }}
          kubectl rollout status deployment/api
```

---

## 30. Health Checks & Observability

### Health Check Endpoint

```js
app.get('/health', async (req, res) => {
  const checks = await Promise.allSettled([
    pool.query('SELECT 1'),           // database
    redisClient.ping(),               // cache
  ]);

  const [db, cache] = checks;
  const healthy = checks.every((c) => c.status === 'fulfilled');

  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'ok' : 'degraded',
    checks: {
      database: db.status === 'fulfilled' ? 'ok' : db.reason?.message,
      cache: cache.status === 'fulfilled' ? 'ok' : cache.reason?.message,
    },
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    timestamp: new Date().toISOString(),
  });
});

// Readiness probe — is the app ready to serve traffic?
app.get('/ready', (req, res) => {
  if (shuttingDown) return res.status(503).send('shutting down');
  res.send('ok');
});

// Liveness probe — is the app alive? (basic — no external deps)
app.get('/live', (req, res) => res.send('ok'));
```

### Metrics with `prom-client`

```js
const client = require('prom-client');

// Default metrics: CPU, memory, GC, event loop lag
client.collectDefaultMetrics({ prefix: 'api_' });

// Custom metrics
const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
});

const activeConnections = new client.Gauge({
  name: 'active_connections',
  help: 'Number of active connections',
});

// Middleware
app.use((req, res, next) => {
  const end = httpRequestDuration.startTimer();
  res.on('finish', () => {
    end({ method: req.method, route: req.route?.path ?? req.path, status_code: res.statusCode });
  });
  next();
});

// Expose metrics endpoint for Prometheus scraping
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.send(await client.register.metrics());
});
```

### Distributed Tracing

```js
// OpenTelemetry — instrument once, export to Jaeger/Zipkin/Datadog/etc.
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT }),
  instrumentations: [getNodeAutoInstrumentations()], // auto-instruments HTTP, Express, pg, etc.
});

sdk.start(); // must be called before require('express')
```

---

## 31. Performance Tuning

### Profiling with `--inspect`

```bash
# Start with inspector
node --inspect dist/main.js

# Profile CPU (open chrome://inspect in Chrome → click "inspect")
# Take heap snapshot or CPU profile from DevTools

# For automated profiling
node --prof dist/main.js     # generates isolate-*.log
node --prof-process isolate-*.log > processed.txt
```

### Event Loop Lag

High event loop lag means the event loop is busy — I/O callbacks queue up and response times spike.

```js
const { monitorEventLoopDelay } = require('perf_hooks');

// Histogram-based measurement (V8 native — low overhead)
const histogram = monitorEventLoopDelay({ resolution: 10 });
histogram.enable();

setInterval(() => {
  const lagMs = histogram.mean / 1e6; // nanoseconds → milliseconds
  if (lagMs > 50) logger.warn({ lagMs }, 'High event loop lag');
  histogram.reset();
}, 10_000);
```

### Memory Leak Detection

```js
// Heap snapshots — take two, compare in Chrome DevTools Memory tab
const v8 = require('v8');
const { writeFileSync } = require('fs');

app.get('/admin/heap-snapshot', (req, res) => {
  const snapshot = v8.writeHeapSnapshot();
  res.download(snapshot);
});

// Monitor memory growth over time
const used = process.memoryUsage();
logger.info({
  rss: Math.round(used.rss / 1024 / 1024),        // total process memory
  heapUsed: Math.round(used.heapUsed / 1024 / 1024),
  heapTotal: Math.round(used.heapTotal / 1024 / 1024),
  external: Math.round(used.external / 1024 / 1024), // C++ objects (Buffers)
}, 'Memory usage (MB)');
```

### Common Performance Tips

- **Avoid synchronous operations** in request path (`fs.readFileSync`, `crypto` sync methods)
- **Increase UV_THREADPOOL_SIZE** if CPU profiling shows threads waiting (e.g., heavy fs/crypto)
- **Stream large responses** instead of buffering in memory
- **Cache aggressively** — Redis for DB query results, in-process LRU for hot config
- **Enable HTTP keep-alive** on both server and outbound clients
- **Use `compression` middleware** for text responses over ~1KB

```js
const compression = require('compression');
app.use(compression({ level: 6, threshold: 1024 }));
```

---

## 32. Secrets Management

### Never Commit Secrets

```bash
# .gitignore
.env
.env.*
!.env.example   # commit a template with no real values
*.pem
*.key
```

### Environment Variables vs Vault

| Approach | Use case | Risk |
|---|---|---|
| `.env` file | Local dev only | Accidentally committed |
| OS env vars (Docker/K8s) | Containers | Visible in process list |
| AWS Secrets Manager / GCP Secret Manager | Production | Rotation built-in |
| HashiCorp Vault | Multi-cloud, dynamic secrets | Operational overhead |
| Kubernetes Secrets | K8s workloads | Base64-encoded (not encrypted by default — enable etcd encryption) |

### Secrets at Runtime

```js
// AWS Secrets Manager — fetch at startup, cache in memory
const { SecretsManagerClient, GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');

async function getSecret(name) {
  const client = new SecretsManagerClient({ region: process.env.AWS_REGION });
  const response = await client.send(new GetSecretValueCommand({ SecretId: name }));
  return JSON.parse(response.SecretString);
}

// Bootstrap — fetch secrets before starting server
const secrets = await getSecret('prod/api/database');
process.env.DATABASE_URL = secrets.connectionString;
process.env.JWT_SECRET = secrets.jwtSecret;

// Then start the app
await app.listen(3000);
```

### Rotation Pattern

```js
// Use connection pools that lazily reconnect — when secrets rotate,
// new connections pick up the new credentials without restart

// Detect auth failures and re-fetch secrets
pool.on('error', async (err, client) => {
  if (err.code === '28P01') { // invalid password
    const newSecrets = await getSecret('prod/api/database');
    pool.options.connectionString = newSecrets.connectionString;
  }
});
```

---

# Part 1 (continued): Node.js Core

---

## 33. Crypto Module

The built-in `node:crypto` module covers token generation, hashing, HMAC signing, and symmetric encryption.

```js
import { randomBytes, createHash, createHmac, createCipheriv, createDecipheriv, timingSafeEqual } from 'node:crypto';

// Secure random tokens — use for session IDs, password-reset links
const token = randomBytes(32).toString('hex'); // 64-char hex string
const urlSafeToken = randomBytes(32).toString('base64url'); // URL-safe base64

// Hashing — SHA-256 digest (one-way, deterministic)
const hash = createHash('sha256').update('hello world').digest('hex');
// '...' — 64-char hex

// Chain multiple updates for streaming input
const fileHash = createHash('sha256');
for await (const chunk of readableStream) fileHash.update(chunk);
const digest = fileHash.digest('hex');

// HMAC — keyed hash for webhook signature verification
const secret = process.env.WEBHOOK_SECRET;
const sig = createHmac('sha256', secret).update(rawBody).digest('hex');
const expected = `sha256=${sig}`;

// Verify webhook signature — timingSafeEqual prevents timing attacks
function verifyWebhook(rawBody, headerSig, secret) {
  const expected = 'sha256=' + createHmac('sha256', secret).update(rawBody).digest('hex');
  const a = Buffer.from(expected);
  const b = Buffer.from(headerSig);
  if (a.length !== b.length) return false;
  return timingSafeEqual(a, b); // constant-time comparison
}

// Symmetric encryption — AES-256-GCM (authenticated encryption)
const KEY = randomBytes(32); // 256-bit key — store in secrets manager
const IV_LENGTH = 12;         // GCM standard IV size

function encrypt(plaintext) {
  const iv = randomBytes(IV_LENGTH);
  const cipher = createCipheriv('aes-256-gcm', KEY, iv);
  const encrypted = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag(); // authentication tag — detects tampering
  return { iv: iv.toString('hex'), data: encrypted.toString('hex'), tag: tag.toString('hex') };
}

function decrypt({ iv, data, tag }) {
  const decipher = createDecipheriv('aes-256-gcm', KEY, Buffer.from(iv, 'hex'));
  decipher.setAuthTag(Buffer.from(tag, 'hex'));
  return Buffer.concat([
    decipher.update(Buffer.from(data, 'hex')),
    decipher.final(),
  ]).toString('utf8');
}
```

**Key rules:**
- Never use `createCipher` / `createDecipher` (no IV — deprecated and insecure); always use `createCipheriv`
- Use `timingSafeEqual` for any security-sensitive comparison — regular `===` leaks timing information
- Prefer `aes-256-gcm` over `aes-256-cbc`: GCM provides authentication built-in; CBC requires a separate HMAC
- `randomBytes` is cryptographically secure; `Math.random()` is not — never use it for tokens or IVs

---

## 34. DNS Module

The classic Node.js trivia question: `dns.lookup` and `dns.resolve` look similar but use completely different code paths.

```js
import dns from 'node:dns/promises';

// dns.lookup — uses the OS resolver (getaddrinfo via thread pool)
// - Respects /etc/hosts, system DNS cache, nsswitch.conf
// - Runs on the libuv thread pool — blocks a thread while resolving
// - Returns one address (same as what your OS gives to connect())
const { address, family } = await dns.lookup('example.com');
// address: '93.184.216.34', family: 4

// Force IPv4 or IPv6
await dns.lookup('example.com', { family: 4 }); // IPv4 only
await dns.lookup('example.com', { family: 6 }); // IPv6 only

// dns.resolve — uses c-ares (Node's own async DNS client, NOT the thread pool)
// - Bypasses /etc/hosts and system DNS cache
// - Non-blocking — goes directly to the DNS server specified in resolv.conf
// - Returns all records of the requested type
const addresses = await dns.resolve4('example.com');  // all IPv4 A records
const mx = await dns.resolveMx('example.com');        // MX records
const txt = await dns.resolveTxt('example.com');       // TXT records (e.g. SPF)
const srv = await dns.resolveSrv('_http._tcp.example.com');

// dns.resolve vs dns.lookup — which to use?
// dns.lookup   — when you need what connect() / http.get() will get (consistent behavior)
// dns.resolve  — when you need raw DNS records, multiple addresses, or specific record types

// Reverse lookup
const hostnames = await dns.reverse('8.8.8.8'); // ['dns.google']

// Check DNS availability during health checks
async function checkDns(hostname) {
  try {
    await dns.resolve4(hostname);
    return true;
  } catch {
    return false;
  }
}
```

**The interview-critical distinction:**

| | `dns.lookup` | `dns.resolve` |
|---|---|---|
| Implementation | OS `getaddrinfo` | c-ares (async) |
| Thread pool | Yes — blocks a thread | No |
| Respects `/etc/hosts` | Yes | No |
| Returns | One address | All records |
| Use case | What `http.get` uses | Raw DNS queries |

Saturating the thread pool with many concurrent `dns.lookup` calls can cause delays — prefer `dns.resolve` for high-volume lookups when `/etc/hosts` consistency isn't needed.

---

## 35. `node:` Protocol Imports

Modern Node.js (v14.18+/v16+) supports the `node:` prefix for built-in modules. It's now the recommended style.

```js
// Old style — ambiguous: is 'fs' a built-in or an npm package named 'fs'?
import fs from 'fs';
const { readFile } = require('fs');

// New style — unambiguous, explicit, zero resolution cost
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { createServer } from 'node:http';
import { Worker } from 'node:worker_threads';
import { randomBytes } from 'node:crypto';

// Benefits of node: prefix:
// 1. Explicit — reader immediately knows it's a built-in, not a package
// 2. Faster — Node skips the node_modules lookup entirely
// 3. Safe — cannot be shadowed by an npm package with the same name
// 4. Required for some newer APIs (e.g. node:test built-in test runner)

// Built-in test runner (Node 18+ stable) — requires node: prefix
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

describe('add', () => {
  it('sums two numbers', () => {
    assert.equal(1 + 1, 2);
  });
});
// Run: node --test src/**/*.test.js

// ESM-only note: the node: prefix is required in some ESM contexts
// (e.g., when importing from a package with "type": "module" that
// also happens to have a dep with the same name as a built-in)
```

**Migration:** Prefer `node:` for all new code. ESLint rule `unicorn/prefer-node-protocol` enforces it automatically.

---

# Part 2 (continued): Express & Fastify

---

## 36. File Uploads

Multipart form uploads require a dedicated parser. Three common approaches: multer (Express middleware), formidable (lower-level), or streaming directly to object storage.

```js
// multer — most common Express middleware for multipart/form-data
import multer from 'multer';
import path from 'node:path';

// Memory storage — file in req.file.buffer (good for small files / S3 upload)
const memUpload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024 }, // 5 MB limit
  fileFilter(req, file, cb) {
    const allowed = ['.jpg', '.jpeg', '.png', '.webp'];
    const ext = path.extname(file.originalname).toLowerCase();
    cb(null, allowed.includes(ext)); // cb(null, false) rejects the file
  },
});

// Disk storage — streams directly to disk (good for large files)
const diskUpload = multer({
  storage: multer.diskStorage({
    destination: 'uploads/',
    filename(req, file, cb) {
      const unique = `${Date.now()}-${Math.round(Math.random() * 1e9)}`;
      cb(null, `${unique}${path.extname(file.originalname)}`);
    },
  }),
  limits: { fileSize: 100 * 1024 * 1024 }, // 100 MB
});

// Route handlers
app.post('/avatar', memUpload.single('avatar'), async (req, res) => {
  const { buffer, mimetype, originalname } = req.file;
  const key = `avatars/${req.user.id}/${Date.now()}-${originalname}`;
  await s3.putObject({ Bucket: 'my-bucket', Key: key, Body: buffer, ContentType: mimetype }).promise();
  res.json({ url: `https://cdn.example.com/${key}` });
});

app.post('/documents', diskUpload.array('files', 10), (req, res) => {
  // req.files = array of { fieldname, originalname, path, size, ... }
  res.json({ uploaded: req.files.map(f => f.filename) });
});

// Stream directly to S3 without buffering in memory (best for large files)
import { PassThrough } from 'node:stream';
import { Upload } from '@aws-sdk/lib-storage';

app.post('/video', (req, res) => {
  const contentType = req.headers['content-type'];
  const pass = new PassThrough();

  const upload = new Upload({
    client: s3Client,
    params: { Bucket: 'videos', Key: `raw/${Date.now()}.mp4`, Body: pass, ContentType: contentType },
  });

  req.pipe(pass); // pipe raw body directly to S3 multipart upload
  upload.done().then(() => res.json({ ok: true })).catch(err => res.status(500).json({ error: err.message }));
});

// Fastify — use @fastify/multipart
import multipart from '@fastify/multipart';
fastify.register(multipart, { limits: { fileSize: 10 * 1024 * 1024 } });

fastify.post('/upload', async (req, reply) => {
  const data = await req.file();
  const buffer = await data.toBuffer();
  // or: await pump(data.file, fs.createWriteStream(`uploads/${data.filename}`));
  return { name: data.filename };
});
```

**Production checklist:**
- Always set `limits.fileSize` — without it, clients can exhaust server memory
- Validate MIME type **and** file extension — `file.mimetype` can be spoofed by the client; also read the magic bytes for critical security checks
- For large files, stream directly to object storage (S3/GCS) — never buffer a 500 MB video in RAM
- Clean up disk storage on error — multer leaves partial files if your handler throws

---

# Part 6: Testing & Development Workflow

---

## 37. Testing Node.js

Three layers: unit tests (fast, isolated), integration tests (real DB/deps), E2E/API tests (full HTTP stack).

```js
// Unit tests with Vitest (or Jest — identical API)
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { UserService } from './user-service.js';

const mockRepo = {
  findById: vi.fn(),
  save: vi.fn(),
};

describe('UserService', () => {
  let service;

  beforeEach(() => {
    vi.clearAllMocks();
    service = new UserService(mockRepo);
  });

  it('throws when user not found', async () => {
    mockRepo.findById.mockResolvedValue(null);
    await expect(service.getUser('123')).rejects.toThrow('User not found');
  });

  it('returns user when found', async () => {
    mockRepo.findById.mockResolvedValue({ id: '123', name: 'Alice' });
    const user = await service.getUser('123');
    expect(user.name).toBe('Alice');
  });
});

// API tests with supertest — no server needed, hits in-process
import request from 'supertest';
import { app } from './app.js'; // Express/Fastify app (not .listen())

describe('POST /users', () => {
  it('creates a user and returns 201', async () => {
    const res = await request(app)
      .post('/users')
      .send({ name: 'Bob', email: 'bob@example.com' })
      .expect(201)
      .expect('Content-Type', /json/);

    expect(res.body).toMatchObject({ name: 'Bob' });
    expect(res.body.id).toBeDefined();
  });

  it('returns 400 for missing email', async () => {
    await request(app).post('/users').send({ name: 'Bob' }).expect(400);
  });
});

// Integration tests with Testcontainers — real Postgres, no mocks
import { PostgreSqlContainer } from '@testcontainers/postgresql';
import { Pool } from 'pg';

describe('UserRepository (integration)', () => {
  let container;
  let pool;
  let repo;

  beforeAll(async () => {
    container = await new PostgreSqlContainer('postgres:16-alpine').start();
    pool = new Pool({ connectionString: container.getConnectionUri() });
    await runMigrations(pool); // apply schema
    repo = new UserRepository(pool);
  }, 60_000); // containers take time

  afterAll(async () => {
    await pool.end();
    await container.stop();
  });

  it('saves and retrieves a user', async () => {
    const id = await repo.save({ name: 'Alice', email: 'alice@example.com' });
    const user = await repo.findById(id);
    expect(user.name).toBe('Alice');
  });
});

// vitest.config.ts
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: { provider: 'v8', thresholds: { lines: 80 } },
    // Separate pool per test file — important for Testcontainers isolation
    pool: 'forks',
    poolOptions: { forks: { singleFork: false } },
  },
});
```

**Strategy:**
- Unit tests: mock at the repository layer, test service/domain logic in isolation — fast, hundreds per second
- API tests (supertest): test the full middleware stack without spawning a real server
- Integration tests (Testcontainers): test DB queries with a real engine; run in CI with Docker — catches schema mismatches that mocks hide
- Avoid mocking the DB in integration tests — that's the lesson from production incidents where mock/prod divergence masked broken migrations

---

## 38. Package Managers & Workspaces

```bash
# npm — default, ships with Node
npm install          # installs from package.json + package-lock.json
npm ci               # clean install (CI) — faster, fails if lock file is out of sync
npm install --save-exact react@18.3.0  # pin exact version in package.json

# pnpm — disk-efficient, strict
pnpm install         # symlinks from a global content-addressable store
pnpm add lodash      # adds to dependencies
pnpm dlx tsx index.ts  # run without installing (like npx)

# bun — fast JavaScript runtime + package manager
bun install          # installs from bun.lockb (binary lock file)
bun add hono         # adds dependency
bun run src/index.ts # runs TypeScript directly (no transpilation step)

# Lock file comparison
# package-lock.json (npm) — JSON, large, human-readable diffs
# pnpm-lock.yaml (pnpm)   — YAML, readable, content-addressed
# bun.lockb (bun)          — binary, fast to parse, not human-readable
# yarn.lock (yarn)          — text, reproducible
```

```jsonc
// package.json — npm/pnpm workspaces (monorepo)
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": ["packages/*", "apps/*"]
}

// pnpm-workspace.yaml — pnpm workspaces
// packages:
//   - 'packages/*'
//   - 'apps/*'
```

```bash
# Running commands across workspaces
npm run build --workspaces          # all workspaces
npm run test -w packages/auth       # single workspace
pnpm --filter @myapp/auth build     # pnpm filter syntax
pnpm --filter '...[main]' test      # only workspaces changed since main

# Adding a dependency to a specific workspace
npm install zod -w packages/auth
pnpm add zod --filter @myapp/auth

# Internal cross-workspace dependency
# packages/auth/package.json:
# "dependencies": { "@myapp/shared": "workspace:*" }
# pnpm resolves workspace:* to the local package; npm/bun use "*" or "file:../shared"
```

**Choosing a package manager:**
- **npm** — zero setup, already installed, good enough for most projects
- **pnpm** — disk-efficient (one copy per version in global store), strict (no phantom deps), best for monorepos
- **bun** — fastest install + script execution, built-in TypeScript runner, growing ecosystem

**Lock file discipline:** Always commit lock files. `npm ci` / `pnpm install --frozen-lockfile` in CI guarantees exact same versions as local dev. Never run `npm install` in CI — it can silently upgrade packages.

---

## 39. Development Workflow

Running TypeScript in Node.js locally without a build step.

```bash
# ts-node — TypeScript execution for Node (slower start, stable)
npx ts-node src/server.ts
npx ts-node --esm src/server.ts  # ESM mode

# tsx — faster alternative (uses esbuild under the hood, recommended)
npx tsx src/server.ts
npx tsx watch src/server.ts  # built-in watch mode — restarts on file change

# bun — runs TypeScript natively, no config needed
bun run src/server.ts
bun --watch src/server.ts    # watch mode
```

```bash
# nodemon — watches files and restarts the process
npx nodemon src/server.js               # watch .js files
npx nodemon --exec tsx src/server.ts    # use tsx as the runner
npx nodemon --ext ts,json src/server.ts # watch .ts and .json changes
```

```jsonc
// nodemon.json — config file
{
  "watch": ["src"],
  "ext": "ts,json",
  "ignore": ["src/**/*.test.ts"],
  "exec": "tsx src/server.ts"
}
```

```jsonc
// package.json scripts
{
  "scripts": {
    "dev": "tsx watch src/server.ts",             // tsx built-in watch (preferred)
    "dev:nodemon": "nodemon",                      // nodemon with nodemon.json
    "start": "node dist/server.js",               // production (compiled)
    "build": "tsc --outDir dist",
    "typecheck": "tsc --noEmit"
  }
}
```

```js
// Node.js 18+ built-in watch mode — no extra tooling
// node --watch src/server.js
// node --watch --experimental-strip-types src/server.ts  (Node 22+)
```

**Node 22+ native TypeScript:** `--experimental-strip-types` lets Node run `.ts` files directly by stripping type annotations (no type-checking). Fast, zero-dependency alternative to tsx for scripts.

**Comparison:**

| Tool | Speed | Type-checks on run? | Watch mode | Notes |
|---|---|---|---|---|
| `ts-node` | Slow | Yes (optional) | Via nodemon | Mature, stable |
| `tsx` | Fast (esbuild) | No | Built-in `tsx watch` | Recommended for DX |
| `bun run` | Fastest | No | `bun --watch` | Bun runtime only |
| `node --watch` + strip-types | Fast | No | Built-in | Node 22+, no deps |

Always run `tsc --noEmit` as a separate CI step — hot-reload tools that skip type-checking can hide type errors that only surface at build time.

---

## 40. dependencies vs devDependencies

`package.json` separates packages by **when they're needed**: at runtime in production vs only during development/build.

```jsonc
{
  "dependencies": {
    "express": "^4.19.0",        // imported by code that runs in production
    "pg": "^8.11.0",
    "zod": "^3.23.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",      // only needed to build, never at runtime
    "vitest": "^2.0.0",          // tests don't run in production
    "@types/express": "^4.17.0", // type definitions — compile-time only
    "eslint": "^9.0.0",
    "tsx": "^4.16.0"
  }
}
```

**How they're installed:**

```bash
npm install express        # adds to "dependencies"
npm install -D typescript  # adds to "devDependencies" (--save-dev)

# Production install — skips devDependencies entirely
npm install --omit=dev     # (npm 8+; older: --production)
NODE_ENV=production npm ci  # CI: clean install, respects NODE_ENV
```

**The distinction matters because:**

| Concern | Why the split helps |
|---------|--------------------|
| Image size | `--omit=dev` in production Docker images drops TypeScript, test runners, linters — smaller, faster deploys |
| Security surface | Fewer installed packages in production = smaller attack surface, fewer CVEs to patch |
| Install speed | Production/CI deploy installs only what runs |
| Intent / documentation | Clearly signals which packages ship vs which are tooling |

**The key rule:** if `import`/`require` of the package executes when your app runs in production, it's a **dependency**. If it's only used to build, test, lint, or type-check, it's a **devDependency**.

**Common mistakes:**

```jsonc
// ❌ TypeScript types in dependencies — they're erased at compile time, never run
"dependencies": { "@types/node": "^20.0.0" }

// ❌ A build-time tool that the runtime actually imports — must be a real dependency
//    e.g. if you import a helper from a "dev" package at runtime, prod install breaks

// ⚠️ Compiled output gotcha: if you build to JS and ship dist/, the BUILD happens
//    where devDependencies ARE installed (CI), so tsc being a devDependency is fine.
//    But if you ship .ts and run with tsx in prod, tsx must be a dependency.
```

**Two other categories:**

```jsonc
{
  // peerDependencies — "I need this, but the HOST app provides it" (libraries/plugins)
  "peerDependencies": { "react": ">=18" },
  // A React component library declares react as a peer so it uses the app's single copy

  // optionalDependencies — install failure is non-fatal (e.g. platform-specific binaries)
  "optionalDependencies": { "fsevents": "^2.3.0" }  // macOS-only file watcher
}
```

**Interview gotcha:** *"Where do `@types/*` packages go?"* → devDependencies. They exist only for the TypeScript compiler; the emitted JavaScript contains no trace of them. The exception is when you publish a library whose **public types** reference another package's types — then it may need to be a regular dependency so consumers get the types.

---

## Part 3 (continued): NestJS

---

## 41. Dependency Injection

Dependency Injection (DI) is a pattern where a class receives its dependencies from the outside instead of creating them itself. The "inversion of control" is that the class no longer controls *how* its collaborators are built.

### The problem with `new`

```ts
// ❌ Tight coupling — UserService creates its own dependencies
class UserService {
  private db = new PostgresDatabase('postgres://localhost/mydb'); // hard-coded
  private mailer = new SmtpMailer('smtp.gmail.com');              // hard-coded

  async register(email: string) {
    const user = await this.db.insert('users', { email });
    await this.mailer.send(email, 'Welcome!');
    return user;
  }
}
```

What's wrong:
- **Untestable** — you can't swap `PostgresDatabase` for a fake. Every test hits a real DB and sends real email.
- **Rigid** — switching to `MySqlDatabase` means editing `UserService`'s internals.
- **Hidden dependencies** — you can't tell what `UserService` needs without reading its body.
- **Duplicated wiring** — the connection string is buried here instead of configured once centrally.

### The DI version

```ts
interface Database { insert(table: string, data: object): Promise<any>; }
interface Mailer { send(to: string, body: string): Promise<void>; }

// ✓ Dependencies are passed IN via the constructor
class UserService {
  constructor(
    private readonly db: Database,    // depends on an abstraction, not a concrete class
    private readonly mailer: Mailer,
  ) {}

  async register(email: string) {
    const user = await this.db.insert('users', { email });
    await this.mailer.send(email, 'Welcome!');
    return user;
  }
}

// Composition root — wiring happens in ONE place
const db = new PostgresDatabase(process.env.DATABASE_URL);
const mailer = new SmtpMailer(process.env.SMTP_HOST);
const userService = new UserService(db, mailer);

// In a test — inject fakes, no real DB or email
const fakeDb = { insert: async () => ({ id: 1, email: 'a@b.com' }) };
const fakeMailer = { send: async () => {} };
const service = new UserService(fakeDb, fakeMailer);
```

### `new` vs DI — what actually changes

| | `new` inside the class | Dependency Injection |
|--|------------------------|----------------------|
| Who creates dependencies | The class itself | The caller / DI container |
| Coupling | To concrete classes | To interfaces/abstractions |
| Testing | Must use real implementations | Inject mocks/fakes freely |
| Swapping implementations | Edit the class | Change the wiring only |
| Visibility of needs | Hidden in the body | Explicit in the constructor signature |
| Lifecycle control | Per-instance, ad hoc | Centralized (singleton/scoped/transient) |

**Key insight:** DI doesn't eliminate `new` — *something* still constructs the objects. It **moves** the `new` to a single composition root (or a container), so business-logic classes depend on abstractions and stay testable and reconfigurable.

### DI containers (NestJS)

For small apps, manual wiring (passing constructor args yourself) is enough. As the graph grows — service A needs B needs C needs D — wiring by hand becomes tedious. A **DI container** resolves the whole graph automatically.

```ts
// NestJS — @Injectable marks a class as available for injection
@Injectable()
export class UserService {
  // Nest reads the constructor types and injects matching providers
  constructor(
    private readonly db: DatabaseService,
    private readonly mailer: MailerService,
  ) {}

  async register(email: string) {
    const user = await this.db.insert('users', { email });
    await this.mailer.send(email, 'Welcome!');
    return user;
  }
}

@Module({
  providers: [UserService, DatabaseService, MailerService], // registered in the container
  controllers: [UserController],
})
export class UserModule {}
```

**Interface-based injection via tokens** (TS interfaces don't exist at runtime, so use a token):

```ts
export const MAILER = Symbol('MAILER');

@Module({
  providers: [
    {
      provide: MAILER,
      // swap SmtpMailer ↔ SesMailer ↔ FakeMailer without touching UserService
      useClass: process.env.NODE_ENV === 'test' ? FakeMailer : SmtpMailer,
    },
  ],
})
export class AppModule {}

@Injectable()
export class UserService {
  constructor(@Inject(MAILER) private readonly mailer: Mailer) {}
}
```

**Provider scopes:**

```ts
@Injectable({ scope: Scope.DEFAULT })   // singleton — one instance app-wide (default)
@Injectable({ scope: Scope.REQUEST })   // new instance per incoming request
@Injectable({ scope: Scope.TRANSIENT }) // new instance every time it's injected
```

### When DI is overkill

For a one-off script or a class with no external collaborators, plain `new` is fine — DI adds indirection for no benefit. Reach for DI (and especially a container) when you have: multiple implementations to swap, a need to unit-test in isolation, or a deep dependency graph that's painful to wire by hand.

---

*Last updated: 2026-06-05*
