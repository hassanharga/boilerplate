# System Design Reference

A senior-focused reference for system design interviews. Framework + core building blocks + worked examples.

---

## Table of Contents

### Part 1: Interview Framework
1. [How to Answer System Design Questions](#1-how-to-answer-system-design-questions)
2. [Back-of-Envelope Estimation](#2-back-of-envelope-estimation)

### Part 2: Core Building Blocks
3. [DNS & CDN](#3-dns--cdn)
4. [Load Balancers](#4-load-balancers)
5. [API Gateway](#5-api-gateway)
6. [Databases](#6-databases)
7. [Caching Layer](#7-caching-layer)
8. [Message Queues](#8-message-queues)
9. [Object Storage](#9-object-storage)
10. [Search](#10-search)
25. [WebSockets vs SSE vs Long Polling](#25-websockets-vs-sse-vs-long-polling)
26. [Security Basics at Scale](#26-security-basics-at-scale)
27. [Microservices vs Monolith](#27-microservices-vs-monolith)

### Part 3: Scalability Concepts
11. [CAP Theorem & Consistency Models](#11-cap-theorem--consistency-models)
12. [Sharding & Partitioning](#12-sharding--partitioning)
13. [Replication](#13-replication)
14. [Consistent Hashing](#14-consistent-hashing)
15. [Rate Limiting at Scale](#15-rate-limiting-at-scale)
28. [Idempotency](#28-idempotency)
29. [Distributed Transactions](#29-distributed-transactions)
30. [Observability](#30-observability)
31. [Multi-Region / Global Distribution](#31-multi-region--global-distribution)

### Part 4: Common Interview Problems
16. [URL Shortener](#16-url-shortener)
17. [Social Media Feed (Twitter/Instagram)](#17-social-media-feed-twitterinstagram)
18. [Chat System (WhatsApp)](#18-chat-system-whatsapp)
19. [Notification System](#19-notification-system)
20. [Search Autocomplete](#20-search-autocomplete)
21. [Ride-Sharing (Uber)](#21-ride-sharing-uber)
22. [Video Streaming (YouTube/Netflix)](#22-video-streaming-youtubeNetflix)
32. [Design a Distributed Cache](#32-design-a-distributed-cache)
33. [Design Google Drive / Dropbox](#33-design-google-drive--dropbox)
34. [Design a Web Crawler](#34-design-a-web-crawler)
35. [Design a Ticket Booking System](#35-design-a-ticket-booking-system)
36. [Design a Rate Limiter (Standalone)](#36-design-a-rate-limiter-standalone)

### Part 5: Reference
23. [Database Selection Guide](#23-database-selection-guide)
24. [Trade-offs Cheat Sheet](#24-trade-offs-cheat-sheet)

---

# Part 1: Interview Framework

---

## 1. How to Answer System Design Questions

System design interviews test your ability to think at scale and communicate trade-offs. They rarely have a single correct answer — the interviewer wants to see your thought process.

### The SCALE Framework

**S — Scope the requirements (5–10 min)**

Ask clarifying questions before drawing anything:

- What are the core features? (read-heavy vs write-heavy?)
- How many users? DAU? Requests per second?
- Is this global or single-region?
- What consistency guarantees are needed?
- What's the expected data size? Growth rate?
- Any SLA requirements (latency, uptime)?

**C — Capacity estimation**

Do back-of-envelope math before designing (see Section 2). This drives architecture decisions.

**A — API design**

Define the core APIs before the architecture. This anchors the conversation.

```
POST /shorten     { url: "https://..." }  → { shortCode: "abc123" }
GET  /:shortCode                          → 302 redirect
```

**L — Layout the high-level design**

Draw the major components with data flowing between them. Start simple:
- Client → Load Balancer → App Servers → Database
- Add components only when you can justify them.

**E — Evolve and address bottlenecks**

Walk through failure modes and scale problems:
- "At 10k RPS, the DB becomes the bottleneck → add read replicas + cache"
- "Single region is a risk → add multi-region with CDN"

### What Interviewers Penalize

- Jumping to a complex solution before understanding requirements
- Adding components (Kafka, Redis, etc.) without explaining why
- Not discussing trade-offs ("I chose X because...")
- Ignoring failure modes and edge cases
- Never estimating scale

---

## 2. Back-of-Envelope Estimation

Quick math helps you justify architecture decisions. Memorize these numbers.

### Latency Numbers

| Operation | Approximate Latency |
|-----------|-------------------|
| L1 cache reference | 0.5 ns |
| L2 cache reference | 7 ns |
| RAM access | 100 ns |
| SSD sequential read (1 MB) | 1 ms |
| HDD sequential read (1 MB) | 20 ms |
| Round trip same datacenter | 0.5 ms |
| Round trip cross-region | 150 ms |

**Rule of thumb:** Memory is fast, disk is slow, network is in between. Avoid cross-region synchronous calls.

### Throughput Ballparks

| System | Approximate RPS |
|--------|----------------|
| Single app server (simple API) | 1,000–10,000 RPS |
| Single PostgreSQL (indexed reads) | 10,000–100,000 QPS |
| Single Redis | 100,000–1,000,000 ops/s |
| Single Kafka partition | 10,000–100,000 msg/s |

### Storage Estimation Template

```
Daily writes: 1M users × 1 post/day = 1M writes/day
Avg post size: 1 KB text + 500 KB image = ~500 KB
Daily storage: 1M × 500 KB = 500 GB/day
3-year storage: 500 GB × 365 × 3 ≈ 550 TB
```

### Traffic Estimation Template

```
100M DAU, each opens app 5×/day, reads 20 posts per session
Read QPS = 100M × 5 × 20 / 86,400 ≈ 115,000 QPS
Write QPS = 100M × 1 post/day / 86,400 ≈ 1,200 QPS
→ Read:write ratio ≈ 100:1 — heavily read-biased
```

---

# Part 2: Core Building Blocks

---

## 3. DNS & CDN

### DNS (Domain Name System)

Translates domain names to IP addresses. Relevant in system design for:
- **Geographic routing** — route users to the nearest datacenter
- **TTL tuning** — low TTL enables fast failover but increases DNS query load
- **Health-based routing** — AWS Route 53 can stop routing to an unhealthy region

### CDN (Content Delivery Network)

Caches static content (images, JS, CSS, video) at edge nodes close to users.

**When to use:**
- Any content that doesn't change per-user (static assets, pre-rendered pages, public API responses)
- Video streaming — CDNs can serve 90%+ of video traffic without hitting origin

**Push vs Pull CDN:**
- **Pull**: CDN fetches content from origin on first request, caches it. Simple; cold start latency.
- **Push**: You upload content to CDN. Ideal for known large assets (video, software releases).

**Cache invalidation:** Hard to purge CDN cache. Use content-addressed URLs (`/assets/logo.a1b2c3.png`) so a new file = new URL — old URL still cached, new URL served fresh.

---

## 4. Load Balancers

Distributes incoming requests across multiple servers.

### Load Balancing Algorithms

| Algorithm | Description | Best For |
|-----------|-------------|----------|
| Round Robin | Requests cycled evenly | Stateless, homogeneous servers |
| Least Connections | Send to server with fewest active connections | Long-lived connections (WebSockets) |
| IP Hash | Hash client IP to consistent server | Session stickiness without shared session store |
| Weighted Round Robin | Weight servers by capacity | Heterogeneous server fleet |

### Layer 4 vs Layer 7

- **L4 (TCP)**: Routes based on IP/port. Extremely fast, no HTTP awareness. Good for raw throughput.
- **L7 (HTTP)**: Routes based on URL path, headers, cookies. Enables path-based routing, A/B testing, canary deploys.

### Health Checks

Load balancers probe backend servers periodically. Failed health checks remove the server from rotation. Two types:
- **Passive**: Detect failures from real request errors
- **Active**: Send probe requests (GET /health) independently

### Horizontal vs Vertical Scaling

| | Vertical (Scale Up) | Horizontal (Scale Out) |
|--|---------------------|----------------------|
| Method | Bigger machine | More machines |
| Limit | Physical hardware ceiling | Practically unlimited |
| Cost | Expensive at high end | Linear with load |
| Failure | Single point of failure | Redundant |
| Complexity | Simple — no distribution | Requires load balancer + stateless app |

---

## 5. API Gateway

A single entry point in front of your microservices. Handles cross-cutting concerns so individual services don't have to.

**Responsibilities:**
- Authentication / authorization (validate JWT before forwarding)
- Rate limiting per client
- Request routing to the correct service
- SSL termination
- Request/response transformation
- Observability (centralized access logging)

**Trade-off:** The gateway is a potential single point of failure and a bottleneck. Run multiple instances behind a load balancer.

```
Client → [API Gateway] → /users/* → User Service
                       → /orders/* → Order Service
                       → /products/* → Product Service
```

---

## 6. Databases

### Relational (SQL) — PostgreSQL, MySQL

- Strong ACID guarantees
- Complex queries with JOINs
- Schema enforced at the DB level
- Vertical scaling + read replicas; sharding is painful

**Use when:** data relationships are complex, transactions span multiple entities, consistency is required.

### Document (NoSQL) — MongoDB, DynamoDB

- Flexible schema
- Horizontal sharding built in
- Best for hierarchical/nested data
- Limited JOIN support
- Eventual consistency by default (configurable)

**Use when:** schema evolves rapidly, data is document-like, read patterns are known and uniform.

### Wide-Column — Cassandra, HBase

- Optimized for massive write throughput
- Distributed by design — no single point of failure
- Query patterns must be known at design time (queries drive schema)
- No JOINs, no ad-hoc queries

**Use when:** time-series data, IoT, activity logs, billions of rows.

### Key-Value — Redis, DynamoDB (simple use)

- O(1) reads/writes
- Data must fit a flat key → value model
- Redis supports rich data types: lists, sets, sorted sets, hashes

**Use when:** sessions, caching, rate limiting counters, leaderboards.

### Graph — Neo4j, Amazon Neptune

- First-class relationship traversal
- No JOIN overhead for multi-hop queries

**Use when:** social networks, recommendation engines, fraud detection.

### Read Replicas

Route all reads to replicas, all writes to the primary. Provides horizontal read scaling and HA.

```
Write → Primary DB
Reads → Replica 1, Replica 2, Replica 3
```

**Lag:** Async replication means replicas may be slightly behind. Don't route writes followed immediately by reads to a replica.

---

## 7. Caching Layer

### Where to Cache

| Layer | Examples | Latency | Notes |
|-------|----------|---------|-------|
| Client-side | Browser cache, HTTP cache headers | 0 ms | `Cache-Control`, `ETag` |
| CDN | Cloudflare, CloudFront | 5–50 ms | Static + public dynamic content |
| Application | Redis, Memcached | 0.1–1 ms | Session data, computed results |
| Database | Query cache, buffer pool | — | Built-in to DB engine |

### Cache Strategies

**Cache-Aside (Lazy Loading):** App checks cache first; on miss, loads from DB and populates cache.
```
result = cache.get(key)
if not result:
    result = db.query(...)
    cache.set(key, result, ttl=300)
return result
```
Pro: Only caches data that's actually requested. Con: Cache miss always means a DB hit.

**Write-Through:** On every write, update both DB and cache atomically.
Pro: Cache always fresh. Con: Writes are slower; wastes space on infrequently-read data.

**Write-Behind (Write-Back):** Write to cache immediately; flush to DB asynchronously.
Pro: Very fast writes. Con: Risk of data loss if cache crashes before flush.

**Read-Through:** Cache sits in front of DB; cache layer handles DB reads automatically.

### Cache Eviction Policies

- **LRU** (Least Recently Used): Evict the item not accessed longest. Most common.
- **LFU** (Least Frequently Used): Evict items accessed fewest times.
- **TTL**: Every item expires after a fixed duration.

### Cache Invalidation Problems

**Cache stampede:** Many requests hit the DB simultaneously on a popular cache expiry. Fix: use a lock or probabilistic early expiration.

**Thundering herd:** Cache warms up after a restart — all misses hit the DB at once. Fix: stagger TTLs, pre-warm cache.

**Stale data:** Cache serves outdated data. Fix: short TTLs, event-driven invalidation (publish a "user updated" event → clear that user's cache).

---

## 8. Message Queues

Decouples producers from consumers. Enables async processing, load leveling, and retry.

### Kafka vs RabbitMQ vs SQS

| | Kafka | RabbitMQ | AWS SQS |
|--|-------|----------|---------|
| Model | Log (consumers pull, retain messages) | Queue (broker pushes, deletes on ack) | Queue (pull-based, managed) |
| Throughput | Very high (millions/s) | High | High |
| Ordering | Per-partition | Per-queue | FIFO queues available |
| Replay | Yes (retain log for days/weeks) | No | No |
| Consumer groups | Yes — multiple groups each get all messages | Competing consumers share messages | Competing consumers |
| Complexity | High (ops overhead) | Medium | Low (managed) |

**Use Kafka when:** event streaming, audit log, replay needed, high throughput.
**Use RabbitMQ when:** task queues, routing/filtering, complex patterns.
**Use SQS when:** AWS environment, minimal ops overhead, simple task queue.

### Patterns

**Work queue (competing consumers):** Multiple workers consume from a single queue, each message processed once. Good for background jobs.

**Pub/Sub:** One producer, many subscribers — each subscriber receives every message. Good for notifications, cache invalidation, event fan-out.

**Dead Letter Queue (DLQ):** Messages that fail repeatedly are routed to a DLQ for manual inspection. Prevents poison pills from blocking a queue forever.

---

## 9. Object Storage

Stores unstructured binary data (images, video, backups) at massive scale.

**Examples:** AWS S3, Google Cloud Storage, Azure Blob Storage.

**Key properties:**
- Virtually unlimited capacity
- Strong eventual consistency (most clouds now offer strong consistency for S3)
- Globally durable (11 nines)
- Accessed via HTTP, not a filesystem

**Common patterns:**
- **Pre-signed URLs:** Generate a time-limited URL that lets a client upload/download directly to S3, bypassing your server. Avoids routing large files through app servers.
- **Multi-part upload:** For files > 100 MB, split into chunks and upload in parallel. Resumes on failure.

```
Client → POST /get-upload-url → App Server → S3 pre-sign → returns URL
Client → PUT https://s3.../key?signature=... (direct to S3)
App Server → POST /confirm-upload → updates DB with S3 key
```

---

## 10. Search

### Full-Text Search

**Elasticsearch / OpenSearch:** Inverted index over documents. Near-real-time search, rich query DSL, faceted search, autocomplete.

**Architecture:**
- DB is the source of truth
- Index is updated asynchronously (via CDC or message queue)
- Search queries go to Elasticsearch, not the DB

```
DB write → Kafka event → Consumer → Elasticsearch index update
```

**Why not search directly in the DB?** `LIKE '%term%'` can't use an index. Full-text search in Postgres (`tsvector`) works at moderate scale but lacks Elasticsearch's relevance scoring and horizontal scalability.

---

## 25. WebSockets vs SSE vs Long Polling

Three techniques for pushing data from server to client. The right choice depends on directionality and latency requirements.

### Long Polling

Client sends a request; server holds it open until there's new data (or a timeout), then responds. Client immediately sends another request.

```
Client          Server
  │──── GET /events ────►│
  │                      │  (holds request, waiting for data)
  │◄──── response ───────│  (data available)
  │──── GET /events ────►│  (immediately re-connects)
```

**Pro:** Works everywhere — no special protocol, passes through proxies.  
**Con:** High overhead — one HTTP request per message cycle; server holds many open connections.  
**Use when:** You can't use WebSockets (legacy infra), or message frequency is low (< 1/sec).

### Server-Sent Events (SSE)

Client opens a single HTTP connection; server streams events indefinitely using `text/event-stream` format. Unidirectional: server → client only.

```
Client          Server
  │──── GET /stream ────►│
  │◄──── event: msg1 ────│
  │◄──── event: msg2 ────│
  │◄──── event: msg3 ────│  (connection stays open)
```

**Pro:** Built-in reconnection, event IDs for resumption, simple protocol over plain HTTP/2.  
**Con:** Server → client only; doesn't work for bidirectional messaging.  
**Use when:** Live feed updates (sports scores, stock ticker, notifications), dashboards — anything server-pushes to many clients without needing client replies.

### WebSockets

Full-duplex persistent connection over a single TCP connection, upgraded from HTTP.

```
Client          Server
  │── HTTP Upgrade ────►│
  │◄── 101 Switching ───│
  │◄──── frame ─────────│   bidirectional, any time
  │───── frame ────────►│
```

**Pro:** Bidirectional, low latency, efficient framing (no HTTP headers per message).  
**Con:** Stateful — load balancers must use sticky sessions or a shared pub/sub layer (Redis) to route messages to the right server; harder to scale horizontally; doesn't cache well.  
**Use when:** Chat, collaborative editing, gaming, live auctions — anything requiring low-latency bidirectional communication.

### Comparison

| | Long Polling | SSE | WebSocket |
|--|-------------|-----|-----------|
| Direction | Server → Client | Server → Client | Bidirectional |
| Protocol | HTTP | HTTP | WS (upgraded HTTP) |
| Reconnection | Manual | Automatic | Manual |
| Load balancer friendly | Yes | Yes | Needs sticky sessions |
| Browser support | Universal | Universal (IE needs polyfill) | Universal |
| Overhead per message | High | Low | Very low |

---

## 26. Security Basics at Scale

### Authentication vs Authorization

- **AuthN (who are you?):** Verify identity — JWT, session cookies, API keys
- **AuthZ (what can you do?):** Verify permissions — RBAC, ABAC, ACLs

### JWT at Scale

```
Header.Payload.Signature
       ↑ base64 encoded, not encrypted — never put secrets here

Verification: server validates signature with the secret/public key
No DB lookup required — stateless. But: can't revoke before expiry.
```

**Revocation:** JWTs can't be invalidated before expiry without a blocklist (Redis set of revoked JIDs). Short-lived tokens (15 min) + refresh tokens mitigate the risk.

### OAuth 2.0 Flows

- **Authorization Code** (most secure — for user-facing apps): Auth code exchanged server-side for access token. Never exposes token to browser URL.
- **Client Credentials** (machine-to-machine): Service authenticates with `client_id + client_secret`. No user involved.
- **Implicit** (deprecated): Avoid — tokens leaked in browser history.

### Encryption

| Where | What | How |
|-------|------|-----|
| In transit | All HTTP traffic | TLS 1.2+ (enforce at load balancer) |
| At rest — DB | PII, payment data | Column-level encryption (AES-256) or full-disk |
| At rest — files | Object storage | SSE-S3 (S3 manages keys) or SSE-KMS (your keys) |
| Passwords | User passwords | bcrypt/Argon2 — never MD5/SHA1 |
| Secrets | API keys, DB passwords | Secrets manager (AWS Secrets Manager, Vault) — never in env vars or code |

### DDoS Protection

- **CDN/WAF layer:** Absorb volumetric attacks at the edge (Cloudflare, AWS Shield). Filter malicious patterns before traffic reaches your servers.
- **Rate limiting:** Per-IP and per-user limits at the API gateway layer.
- **Connection limits:** Limit open TCP connections per IP at the load balancer.
- **Anycast routing:** CDNs spread traffic across PoPs globally — no single point absorbs the full attack.

### Input Validation at Scale

- **Validate at the boundary** (API layer) — not in business logic. Reject malformed input early.
- **Schema validation:** Use a schema library (Zod, Joi, class-validator) — don't write manual if/else validation.
- **File uploads:** Verify MIME type server-side (not just client-side Content-Type). Scan with antivirus before processing. Store in object storage, never on the app server.
- **Rate limit sensitive endpoints:** Login, password reset, OTP verification — brute-force targets.

---

## 27. Microservices vs Monolith

### Monolith First

Start with a monolith. It's faster to build, easier to test, simpler to deploy, and trivial to refactor. Extract services only when you have a proven reason (scaling bottleneck, team autonomy, independent deploy cycles).

**Distributed monolith** (the worst outcome): You split into microservices, but every deploy still requires coordinating 5 services because they share a database or have tight runtime coupling. You get all the complexity of microservices with none of the benefits.

### When to Extract a Service

A good candidate for extraction has **all three**:
1. A well-defined, stable API boundary (changes rarely)
2. A different scaling profile than the rest of the app (e.g., image processing is CPU-heavy, everything else is I/O-bound)
3. A team that owns it end-to-end

### Service Decomposition Strategies

- **By business capability:** User Service, Order Service, Payment Service. Aligns with Conway's Law.
- **By data ownership:** Each service owns its data store. No shared DB (that creates coupling).
- **Strangler Fig:** Gradually extract functionality from a monolith behind a façade/proxy, one piece at a time. Least risky migration strategy.

### Inter-Service Communication

**Synchronous (REST / gRPC):**
```
Service A ──HTTP/gRPC──► Service B ──HTTP/gRPC──► Service C
```
- Simple, immediate feedback
- Chain of failures: if C is slow, B is slow, A is slow (cascading)
- Requires circuit breakers + timeouts

**Asynchronous (events via message queue):**
```
Service A → Kafka → Service B
                  → Service C
```
- Decoupled: A doesn't know or care if B/C are slow
- Harder to trace, eventual consistency only
- Use for: notifications, analytics, anything that doesn't need immediate acknowledgment

### Trade-offs

| | Monolith | Microservices |
|--|----------|--------------|
| Deploy | Single binary | Independent per service |
| Scaling | Scale everything together | Scale services independently |
| Debugging | Easy — single process, one log | Hard — distributed tracing required |
| Data consistency | ACID transactions trivial | Requires Saga or eventual consistency |
| Team scale | Works for ≤ 10 engineers | Necessary for 50+ engineers with multiple teams |
| Latency | In-process calls (nanoseconds) | Network calls (milliseconds) |

---

# Part 3: Scalability Concepts

---

## 11. CAP Theorem & Consistency Models

Any distributed system can guarantee at most 2 of 3:

- **Consistency:** Every read receives the most recent write (or an error)
- **Availability:** Every request receives a response (possibly stale)
- **Partition Tolerance:** System continues operating despite network partitions

**Network partitions always happen** in real distributed systems. So the real choice is **CP vs AP**.

| System | Choice | Reasoning |
|--------|--------|-----------|
| PostgreSQL (single node) | CA | Not distributed — no partition by definition |
| Zookeeper, etcd | CP | Used for coordination; stale data is dangerous |
| Cassandra, DynamoDB | AP | Prioritize availability; allow stale reads |
| MongoDB (w:majority) | CP | Sacrifices availability for strong consistency |

### Consistency Models (weak → strong)

**Eventual consistency:** All replicas will converge eventually. Reads may be stale. Used in: Cassandra, DNS, shopping carts.

**Read-your-writes:** You always see your own writes immediately. Others may not. Used in: user profile systems.

**Monotonic reads:** If you read version N, you'll never read an older version. Prevents "going back in time."

**Causal consistency:** Causally related writes are seen in order by all clients. A reply is always seen after the post it replies to.

**Strong consistency (linearizability):** Every read reflects the most recent write. Reads look like a single sequential history. Most expensive.

---

## 12. Sharding & Partitioning

Splitting data across multiple DB instances to scale writes and storage beyond a single machine.

### Sharding Strategies

**Range-based:** Split by value range (user IDs 1–1M on shard 1, 1M–2M on shard 2).
- Pro: Range queries are efficient (all data for a time range on one shard).
- Con: Hotspots if one range has most traffic.

**Hash-based:** `shard = hash(key) % num_shards`.
- Pro: Even distribution, no hotspots.
- Con: Range queries require scanning all shards. Adding shards requires resharding.

**Directory-based:** A lookup table maps each key to its shard.
- Pro: Flexible, easy to rebalance.
- Con: Lookup table is a bottleneck and single point of failure.

### Problems Introduced by Sharding

- **Cross-shard JOINs:** Must be done in the application layer.
- **Cross-shard transactions:** Requires distributed transactions (2PC) — complex and slow.
- **Resharding:** Adding shards means moving data — use consistent hashing to minimize movement.
- **Celebrity/hotspot problem:** A single entity (viral post, famous user) gets disproportionate traffic on one shard.

---

## 13. Replication

Copying data to multiple nodes for fault tolerance and read scaling.

### Leader-Follower (Primary-Replica)

- All writes go to the leader
- Followers replicate and serve reads
- If leader fails, a follower is promoted (election)

**Replication lag:** Async replication means followers may be seconds behind. Read-after-write consistency requires routing the read back to the leader.

### Multi-Leader

- Multiple nodes accept writes
- Each node replicates to others
- Conflict resolution required (last-write-wins, CRDTs, application-level merge)
- Used in: active-active multi-region setups

### Leaderless (Quorum-Based)

Used by Cassandra, DynamoDB. Writes go to N nodes, considered successful when W nodes acknowledge. Reads go to N nodes, considered correct when R nodes agree.

`W + R > N` guarantees you read at least one node with the latest write.

Typical: N=3, W=2, R=2 — tolerates 1 node failure.

---

## 14. Consistent Hashing

Solves the resharding problem. Instead of `hash(key) % N`, map both keys and nodes onto a ring.

**How it works:**
1. Hash each server to a point on a 0–2^32 ring.
2. Hash each key to a point on the ring.
3. Each key is owned by the first server clockwise from its position.

```
                    A (pos=0)
                       │
          ┌────────────┼────────────┐
         /             │             \
        /    k4(300°)──┼──►A wraps    \
  C(240°)              │              B(120°)
        \              │  k1(50°)──►B /
         \             │             /
          └────────────┼────────────┘
                       │
           k2(170°)──►C    k3(200°)──►C

  Servers:  A @ 0°    B @ 120°    C @ 240°
  k1 @ 50°  → B  (next clockwise after 50°)
  k2 @ 170° → C  (next clockwise after 170°)
  k3 @ 200° → C  (next clockwise after 200°)
  k4 @ 300° → A  (next clockwise after 300°, wraps to 0°)
```

**Adding a node:** Only the keys between the new node and its predecessor move — O(K/N) keys, not O(K).

**Removing a node:** Its keys are taken by the next node clockwise.

**Virtual nodes:** Each physical server is represented by multiple virtual nodes on the ring for more even distribution. Without virtual nodes, uneven hashing leaves some servers handling far more keys than others.

```
  Without virtual nodes:    With virtual nodes (3 vnodes each):
  A handles 33% of keys     A1 @ 10°  A2 @ 130°  A3 @ 250°
  B handles 33% of keys     B1 @ 50°  B2 @ 170°  B3 @ 290°
  C handles 33% of keys     C1 @ 80°  C2 @ 200°  C3 @ 330°
  (ideal but unlikely)      → keys spread more evenly across ring
```

**Used by:** Amazon DynamoDB, Apache Cassandra, Memcached (ketama), CDN request routing.

---

## 15. Rate Limiting at Scale

### Algorithms

**Fixed Window Counter:** Count requests per minute per user. Cheap but allows burst at window boundary (100 at :59, 100 at :00 = 200 in 2 seconds).

**Sliding Window Log:** Store timestamp of every request. Count requests in the last 60 seconds. Accurate but memory-intensive.

**Sliding Window Counter:** Hybrid. Approximate sliding window using two fixed windows and a weighted formula. Good balance of accuracy and memory.

**Token Bucket:** Each user has a bucket refilled at a constant rate. Requests consume a token. Burst allowed up to bucket capacity. Used by AWS API Gateway.

**Leaky Bucket:** Requests drain from a queue at a constant rate. Smooths bursts entirely. Good for outbound rate limiting.

### Distributed Rate Limiting

In a multi-server setup, each server can't track state alone. Options:

- **Centralized store (Redis):** `INCR key` + `EXPIRE` for fixed window. Atomic increment via Lua script or Redis commands for accuracy. Slight latency overhead.
- **Local + sync:** Each server tracks locally, syncs with Redis periodically. Less accurate but lower latency.

```
-- Redis Lua script for atomic sliding window
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], tonumber(ARGV[1]))
end
return current
```

---

## 28. Idempotency

An operation is idempotent if performing it multiple times produces the same result as performing it once.

**Why it matters:** In distributed systems, you can't know if a request succeeded when the network fails. The safe default is to retry — but retrying a non-idempotent operation causes duplicates (charge the card twice, send the email twice, create the order twice).

### Idempotency Keys

Client generates a unique key (UUID) per logical operation and sends it with every request. Server stores the result against the key. On retry with the same key, return the cached result instead of re-executing.

```
Client → POST /payments
         {idempotency_key: "uuid-abc123", amount: 100}

Server:
  1. Check: has "uuid-abc123" been processed?
  2a. No → process, store result under "uuid-abc123", return result
  2b. Yes → return stored result (skip processing)
```

**Storage:** Redis with a TTL (24h–7d) works well. Key = `idempotency:{client_id}:{key}`, value = serialized response.

**Scope:** The key should be scoped to the operation type and user — the same UUID should not be reusable across different endpoints.

### At-Least-Once vs At-Most-Once vs Exactly-Once

| Guarantee | Meaning | How |
|-----------|---------|-----|
| At-most-once | Sent once, may be lost | Fire and forget — no retries |
| At-least-once | Delivered, may be duplicate | Retry on failure — consumer must be idempotent |
| Exactly-once | No loss, no duplicates | Expensive — requires distributed coordination (Kafka transactions, 2PC) |

**Practical rule:** Design consumers to be idempotent and use at-least-once delivery. Exactly-once is usually not worth the complexity.

### Making Operations Idempotent

- **Inserts:** Use `INSERT ... ON CONFLICT DO NOTHING` with a natural unique key
- **Updates:** Use absolute values (`SET balance = 100`) not relative (`SET balance = balance + 10`)
- **Deletes:** Deleting something that's already gone is a no-op — naturally idempotent
- **Payment charges:** Store charge result by idempotency key; never charge without checking

---

## 29. Distributed Transactions

When a write must span multiple services or databases, you can't use a local ACID transaction.

### Why 2PC (Two-Phase Commit) Is Avoided

2PC is the classic protocol: coordinator asks all participants to "prepare" (lock resources), then "commit" if all agreed.

**Problems:**
- Blocking: if the coordinator crashes after prepare, all participants are locked indefinitely
- Synchronous coupling: all services must be available simultaneously
- Performance: 2 round trips with locks across network — slow

**When it's acceptable:** Within a single database cluster (Postgres distributed transactions) or when you control all participants (same team/codebase).

### Saga Pattern

Break a distributed transaction into a sequence of local transactions, each with a compensating action to undo it.

**Choreography (event-driven):** Each service publishes an event after its local transaction; other services react.

```
Order Service ──► "OrderCreated" event
                      │
              Payment Service ──► "PaymentCompleted" event
                                      │
                              Inventory Service ──► "StockReserved"
                              
On failure: each service listens for failure events and publishes its own compensating event
```

Pro: Loosely coupled, no central coordinator.  
Con: Hard to debug — no single place showing the saga's state; complex failure flows.

**Orchestration (coordinator-driven):** A central saga orchestrator calls each service in sequence and handles failures.

```
Saga Orchestrator
  1. Call Order Service     → success
  2. Call Payment Service   → success
  3. Call Inventory Service → FAIL
  4. Compensate: call Payment Service to refund
  5. Compensate: call Order Service to cancel
```

Pro: Explicit state machine, easy to observe.  
Con: Orchestrator can become a single point of failure; creates coupling to orchestrator.

### Outbox Pattern

Guarantees that a database write and a message publish happen atomically, without distributed transactions.

**Problem:** If you write to the DB then publish to Kafka, the write can succeed but the publish can fail — your DB and event stream are now inconsistent.

**Solution:** Write the event to an `outbox` table in the **same** DB transaction as the business write. A separate relay process polls the outbox and publishes events to Kafka, then marks them as published.

```
BEGIN TRANSACTION
  INSERT INTO orders (...)
  INSERT INTO outbox (event_type, payload, published=false)
COMMIT

Outbox Worker (runs continuously):
  SELECT * FROM outbox WHERE published = false
  publish to Kafka
  UPDATE outbox SET published = true
```

**Guarantee:** Either both the order and the outbox row are written (one commit), or neither is. The outbox worker retries until Kafka acknowledges — at-least-once delivery.

---

## 30. Observability

Observability is the ability to understand the internal state of a system from its external outputs. Three pillars: **logs, metrics, traces**.

### Logs

Discrete timestamped records of events. Good for debugging specific incidents.

**Structured logging:** JSON-formatted logs (not plain text) so they're machine-searchable.

```json
{"level":"error","time":"2024-01-15T10:30:00Z","service":"order-svc",
 "trace_id":"abc123","user_id":42,"error":"payment timeout","latency_ms":5003}
```

**Levels:** DEBUG (dev only) → INFO (normal operations) → WARN (degraded but not broken) → ERROR (failure, needs investigation) → FATAL (crash).

**Aggregation:** Ship logs to a central store (Elasticsearch, CloudWatch, Datadog). Never log to local disk only — servers are ephemeral.

**What not to log:** Passwords, tokens, full credit card numbers, PII (unless required and protected).

### Metrics

Numeric measurements over time. Good for alerting and dashboards.

**Types (Prometheus model):**
| Type | Description | Example |
|------|-------------|---------|
| Counter | Ever-increasing count (reset on restart) | HTTP requests total, errors total |
| Gauge | Current value (can go up or down) | Active connections, memory usage |
| Histogram | Distribution of values | Request latency (p50, p95, p99) |
| Summary | Like histogram, but computed on client | Request duration quantiles |

**The Four Golden Signals (Google SRE):**
1. **Latency** — how long requests take (distinguish successful from failed)
2. **Traffic** — request rate (RPS)
3. **Errors** — rate of failed requests (5xx, timeouts)
4. **Saturation** — how full is the system? (CPU %, queue depth, connection pool usage)

**Alert on SLOs, not raw metrics.** Example: "p99 latency > 500ms for 5 minutes" rather than "CPU > 80%".

### Distributed Tracing

A single user request often touches 10+ services. Tracing shows the full path of a request across services with timing for each span.

```
Request: GET /checkout
  └─ Order Service (12ms)
       └─ User Service (3ms)
       └─ Payment Service (450ms)
            └─ Fraud Check (200ms)
            └─ Stripe API (230ms)
       └─ Inventory Service (8ms)
```

**Trace ID:** Generated at the entry point (load balancer or API gateway), propagated via HTTP headers (`X-Trace-ID` or OpenTelemetry's `traceparent`) through every service call.

**Tools:** OpenTelemetry (standard SDK), Jaeger (open-source backend), Zipkin, Datadog APM, AWS X-Ray.

### Alerting & SLOs

**SLI (Service Level Indicator):** What you measure (e.g., "fraction of requests served < 200ms").

**SLO (Service Level Objective):** The target (e.g., "99% of requests < 200ms over a rolling 30-day window").

**SLA (Service Level Agreement):** The contract with consequences (e.g., "if we breach 99.9% uptime, customer gets a credit").

**Error budget:** If your SLO is 99.9% uptime, you have 0.1% downtime budget = ~43 minutes/month. Spend it on risky deploys or absorb it in incidents.

---

## 31. Multi-Region / Global Distribution

### Why Multi-Region?

- **Latency:** Serve users from the nearest region (Europe gets EU servers, not US)
- **Disaster recovery:** One entire region goes down; traffic shifts to another
- **Data sovereignty:** GDPR requires EU user data to stay in the EU

### Active-Passive (Warm Standby)

One primary region handles all traffic. A secondary region replicates data but handles no traffic. On primary failure, DNS is updated to point to the secondary.

**Pros:** Simple, no conflict resolution needed.  
**Cons:** Users far from the primary have high latency; failover takes time (DNS TTL, warm-up).  
**RTO/RPO:** Recovery Time Objective (minutes for DNS to propagate) / Recovery Point Objective (seconds of replication lag).

### Active-Active

All regions accept reads and writes simultaneously. Traffic is routed to the nearest region.

**Challenge:** Concurrent writes to different regions on the same data create conflicts.

**Strategies:**
- **Partition by user geography:** EU users always write to EU region; US users write to US. No cross-region write conflicts (but user travel creates edge cases).
- **Last-write-wins (LWW):** Timestamp-based conflict resolution — risk of losing legitimate writes.
- **CRDTs:** Conflict-free Replicated Data Types — data structures that merge automatically (counters, sets).

### Cross-Region Replication Lag

Async replication between regions typically introduces 50–200ms lag. Implications:
- A user writes in US-East, immediately reads in EU — may get stale data
- Solution: route reads for the same user session back to the write region for a short window (session affinity)

### Data Sovereignty

Certain data must not leave a region:
- EU: GDPR mandates EU resident data stays in the EU
- China: data must be stored on servers in China (ICP license required)

Implement with: row-level metadata flagging data residency, query routing rules in the API layer, separate database clusters per region.

---

# Part 4: Common Interview Problems

---

## 16. URL Shortener

**Requirements:**
- Shorten a long URL → short code (e.g., bit.ly/abc123)
- Redirect short code → original URL
- 100M URLs stored, 10:1 read:write ratio
- Low latency redirects (< 10ms p99)

### Design

**Short code generation:**
- Option 1: Base62 encode an auto-increment ID. Simple, sequential (guessable).
- Option 2: Hash the URL (MD5/SHA-256), take first 7 chars. Risk of collision → check and retry.
- Option 3: Pre-generate random codes and store them (ID pool). Eliminates collision at insert time.

**Database:** One table: `{code, original_url, created_at, user_id, expires_at}`. Primary key on `code`. This is a simple key-value lookup — Redis or a KV store is ideal for the read path.

**Redirect flow:**
1. Request hits CDN — if cached, 302 immediately (no origin hit)
2. Cache miss → app server → Redis lookup
3. Redis miss → PostgreSQL
4. Cache in Redis with TTL
5. Return 301 (permanent, cached by browser) or 302 (temporary, always hits server for analytics)

```
Client → CDN → Load Balancer → App Server → Redis → PostgreSQL
                                    ↓
                               Analytics queue (async)
```

**Scale numbers:**
- Write QPS: 100M URLs / 30 days / 86400s ≈ 40 QPS
- Read QPS: 40 × 10 = 400 QPS (very manageable)
- Storage: 100M × 500 bytes ≈ 50 GB over 10 years

---

## 17. Social Media Feed (Twitter/Instagram)

**Requirements:**
- Users can post tweets/photos
- Followers see a feed of posts from people they follow
- 300M DAU, 100M tweets/day
- Feed latency < 500ms

### Feed Generation Approaches

**Pull model (Fan-out on Read):**
At feed load time, query posts from all followed users, merge and sort.
```
SELECT * FROM tweets WHERE user_id IN (:followed_ids)
ORDER BY created_at DESC LIMIT 20;
```
- Pro: No work at write time
- Con: Slow for users following thousands; can't use cache easily

**Push model (Fan-out on Write):**
When a user tweets, push it to every follower's feed (materialized timeline).
```
on tweet(user_id, tweet_id):
  for follower in get_followers(user_id):
    timeline[follower].prepend(tweet_id)
```
- Pro: Feed reads are O(1) — just read pre-built list from Redis
- Con: Celebrity problem — Lady Gaga has 200M followers → 200M writes per tweet

**Hybrid:**
- Regular users: fan-out on write (push)
- Celebrities (>1M followers): fan-out on read
- At feed load time: merge pre-built timeline + real-time celebrity posts

### Storage

- **Tweets:** Cassandra (write-heavy, time-ordered, no joins needed)
- **User graph (following/followers):** Graph DB or adjacency list in Redis
- **Feed cache:** Redis sorted sets, key = user_id, member = tweet_id, score = timestamp

---

## 18. Chat System (WhatsApp)

**Requirements:**
- 1:1 and group messaging
- 500M DAU, 60B messages/day
- Messages delivered in order
- Offline delivery (message stored until recipient is online)
- Read receipts

### Architecture

**Connection layer:** Clients maintain persistent WebSocket connections to chat servers. WebSockets are needed because the server must push messages without polling.

**Service discovery:** Client connects to the chat server responsible for their shard (consistent hashing on user_id).

**Message flow (1:1):**
```
Alice → WebSocket → Chat Server A → Message Queue → Chat Server B → WebSocket → Bob
                        ↓
                    Message DB (Cassandra)
```

**Offline delivery:** If Bob is offline, Chat Server B stores the message. On reconnect, Bob's server sends all undelivered messages.

**Group messages:** Message → fan-out to each group member's chat server (via message queue). For large groups, this is expensive — use a group message service.

### Message Storage

Cassandra with partition key = `conversation_id`, clustering key = `message_id` (time-ordered). Append-only; never update or delete a message in-place.

Message ID: Use Snowflake ID (timestamp + datacenter ID + sequence) — globally unique, time-sortable.

### Read Receipts

- Delivered: client ACKs receipt of message → server marks `delivered_at`
- Read: client sends read event when user sees message → server marks `read_at`, notifies sender

---

## 19. Notification System

**Requirements:**
- Send push, SMS, and email notifications
- 10M DAU, 1M notifications/day
- Reliable delivery (at-least-once)
- Rate limiting (don't spam users)

### Architecture

```
Event Source → Notification Service → [Kafka] → Workers
                                                  ├─ Push (FCM/APNs)
                                                  ├─ SMS (Twilio)
                                                  └─ Email (SendGrid)
```

**Components:**

**Notification Service:**
- Validates event
- Checks user preferences (opted in? notification type enabled?)
- Rate limits per user
- Publishes to Kafka topic per channel type

**Workers (per channel):**
- Consume from Kafka
- Call third-party provider (FCM, Twilio, SendGrid)
- Retry on failure (exponential backoff)
- Dead-letter failed notifications

**Device token registry:** Store FCM/APNs tokens per user (Redis hash or DB table). Tokens expire and must be refreshed.

### Reliability

- Use Kafka for durability — notifications survive worker crashes
- At-least-once delivery: retry until provider ACKs
- Idempotency key per notification — prevents duplicate sends on retry
- DLQ for notifications that fail after N retries → alert on-call

---

## 20. Search Autocomplete

**Requirements:**
- Return top 5 suggestions as user types
- < 100ms latency
- 10M queries/day

### Trie (Prefix Tree)

Classic data structure: each node is a character, path from root = prefix, leaf stores frequency.

**Problem:** At scale, trie fits in RAM for a single server but can't be horizontally sharded easily, and updates require rebuilding the trie.

### Practical Approach: Redis Sorted Set

Store every possible prefix as a key; value is a sorted set of (term, frequency) pairs.

```
ZADD "se"    100 "search"
ZADD "se"     80 "seattle"
ZADD "sea"   100 "search"
ZADD "sea"    80 "seattle"

ZREVRANGE "sea" 0 4 WITHSCORES  → top 5 completions
```

**Build:** Offline MapReduce/Spark job over query logs → compute term frequencies → populate Redis.
**Update:** Run rebuild weekly (or incrementally with a streaming job).

### Caching

Autocomplete is heavily read-biased. Cache popular prefixes at the CDN or in a local cache. Cache the top 1000 most typed prefixes — covers ~80% of traffic.

---

## 21. Ride-Sharing (Uber)

**Requirements:**
- Match riders to nearby drivers in real time
- Show driver location on map, updating every 4 seconds
- Handle 1M concurrent drivers

### Location Storage

Drivers update their GPS every 4s: 1M drivers × 1 write/4s = 250K writes/s. Too fast for Postgres.

**Redis GEO:** Built-in geospatial commands. `GEOADD drivers lon lat driver_id`. Find nearby drivers with `GEOSEARCH` (use `GEOSEARCH` — `GEORADIUS` was deprecated in Redis 6.2). Fast O(N+log(N)) for radius queries.

**Cassandra:** For persisting location history (time-series writes). Redis is for current positions.

### Matching

When rider requests a ride:
1. Find drivers within 2km using `GEOSEARCH drivers FROMLONLAT lon lat BYRADIUS 2 km ASC`
2. Filter: available, correct vehicle type
3. Score by ETA (need map routing service)
4. Offer to top candidate; if no accept in 10s, move to next

### Map & Routing

Can't do turn-by-turn routing in-house cheaply. Use Google Maps API or HERE Maps. Cache routes for common paths.

### WebSockets for Real-Time Updates

Rider and driver both maintain WebSocket connection. Location updates and match events are pushed via WebSocket.

---

## 22. Video Streaming (YouTube/Netflix)

**Requirements:**
- Upload video → process → stream globally
- Handle 100M viewers, 500 hours of video uploaded per minute

### Upload & Processing Pipeline

```
Client → Upload Service → Raw Video (S3) → Transcoding Queue → Transcoding Workers
                                                                       ↓
                                                    Multiple formats: 360p, 720p, 1080p, 4K
                                                                       ↓
                                                              CDN (per-region)
```

**Transcoding:** CPU-intensive. Run on auto-scaling worker fleet. Use job queue (SQS/Kafka) to distribute work. Each resolution is a separate job.

**Adaptive Bitrate Streaming (ABR):** Video is split into 5-10 second segments at multiple quality levels. Player selects quality based on current bandwidth. Standards: HLS (Apple), MPEG-DASH.

### Streaming Architecture

- Videos served entirely through CDN edge nodes (never from origin after initial cache fill)
- CDN nodes closest to user serve segments
- On cache miss: CDN fetches from origin S3, caches for subsequent viewers

### Metadata

Video metadata (title, description, tags, views) → PostgreSQL.
View counts → eventually consistent counter (Redis INCR, batched flush to DB).
Comments → Cassandra (append-heavy, no complex queries needed).

---

## 32. Design a Distributed Cache

**Requirements:**
- Store key-value data with TTL
- Sub-millisecond reads, handle millions of ops/s
- Cache survives individual node failures
- Nodes can be added/removed without downtime

### Single Node → Cluster

A single Redis node hits a ceiling (~100GB RAM, ~1M ops/s). At scale, you need a cache cluster.

**Sharding:** Use consistent hashing to distribute keys across nodes. Adding a node moves only 1/N of the keys.

**Redis Cluster:** Built-in sharding across 16,384 hash slots. Each node owns a range of slots. Clients are slot-aware — they route requests directly to the correct node.

```
Key → CRC16(key) % 16384 → hash slot → assigned node
```

### Replication for Fault Tolerance

Each primary node has one or more replica nodes. On primary failure, the replica is promoted (automatic with Redis Sentinel or Redis Cluster).

```
Primary A ──replicates──► Replica A1, Replica A2
Primary B ──replicates──► Replica B1, Replica B2
```

### Eviction

When cache is full, old entries must be evicted:

- **allkeys-lru:** Evict least-recently used keys (good default for general caches)
- **volatile-lru:** Only evict keys that have a TTL set
- **allkeys-lfu:** Evict least-frequently used (better for non-uniform access patterns)
- **noeviction:** Return error when full (good for session stores — don't silently drop sessions)

### Adding/Removing Nodes

With consistent hashing, adding a node only requires migrating ~K/N keys (not all of them).

**Migration process:**
1. Add new node to the cluster
2. Cluster migrates slots (and their keys) to the new node
3. During migration, both old and new node serve reads for the slot
4. Once complete, new node is the owner

### Cache Stampede Prevention

When a popular key expires, thousands of requests hit the DB simultaneously.

- **Mutex/lock:** First request acquires a lock, fetches from DB, populates cache; other requests wait
- **Probabilistic early expiration:** Before a key expires, some fraction of requests proactively refresh it
- **Staggered TTLs:** Add random jitter (`TTL ± 10%`) so keys don't all expire simultaneously

---

## 33. Design Google Drive / Dropbox

**Requirements:**
- Upload, store, sync files across devices
- Files up to 50 GB
- 500M users, 10M files uploaded/day
- Detect and sync changes across devices

### Upload Flow

Large files are chunked (5–10 MB chunks) client-side before upload.

```
Client: split file into chunks → hash each chunk (SHA-256)
Client → API Server: "I want to upload file, here are chunk hashes"
API Server → DB: check which chunks already exist (deduplication)
API Server → Client: "upload these missing chunks"
Client → S3: upload chunks directly (pre-signed URLs)
Client → API Server: "all chunks uploaded, here is the manifest"
API Server → DB: save file metadata + chunk list
```

**Deduplication:** If the same chunk exists (same hash), don't store it twice. Two users uploading the same file → only one copy stored.

**Delta sync:** On modification, only the changed chunks are re-uploaded — not the whole file.

### Metadata

```
files:     {file_id, user_id, name, size, version, created_at}
chunks:    {chunk_id, hash, size, s3_key}
file_chunks: {file_id, chunk_id, sequence}
```

### Sync Across Devices

**Change notification:** When a file changes, the server pushes a notification via WebSocket or SSE to all connected devices for that user.

**Conflict resolution:** Two devices edit the same file offline:
- Create two versions (both are valid)
- User sees "conflicted copy" in the UI — same strategy as Dropbox

### Storage

Files → S3. Metadata → PostgreSQL. Active sync state → Redis.

---

## 34. Design a Web Crawler

**Requirements:**
- Crawl 1B URLs, refresh popular pages frequently
- Respect robots.txt and crawl rate limits
- Don't crawl the same page twice
- Distributed across many machines

### Architecture

```
URL Frontier (priority queue) → Fetcher Workers → Parser → Link Extractor
                                                        → Content Store (S3)
                                                        → Back to Frontier (new URLs)
```

### URL Frontier

A prioritized queue of URLs to crawl. Key properties:
- **Deduplication:** Don't enqueue a URL that's already been crawled or is already in the queue
- **Politeness:** Don't crawl the same host more than once per second (avoid hammering servers)
- **Priority:** Popular or recently updated pages crawled more often

**Implementation:** Priority queue per host (ensures politeness per domain). Redis sorted sets with score = next_crawl_time.

### Deduplication

Seen URLs stored in a **Bloom filter** (probabilistic) — accepts some false positives (skip a URL we haven't crawled) but never false negatives (won't recrawl something we've seen). For exact deduplication, store hashes in a distributed key-value store.

### Robots.txt

Before crawling any domain, fetch and cache `robots.txt`. Respect `Disallow:` rules and `Crawl-delay:` directives. Cache for 24 hours.

### Distributed Crawling

Multiple fetcher machines pull URLs from the frontier. Each machine processes its batch, extracts links, and pushes them back. Coordination via Kafka (URLs as messages) or a distributed queue (SQS).

**Politeness:** Ensure all requests to a given host route through a single machine (or are rate-limited per host in Redis) to avoid parallel hammering.

---

## 35. Design a Ticket Booking System

**Requirements:**
- Browse events, see seat availability
- Reserve seats; payment completes the booking
- No double-booking: two users cannot book the same seat
- 100k concurrent users for a major event

### The Core Problem: Inventory Contention

A seat can only be reserved once. Under high concurrency, multiple users may read "seat available" simultaneously and both try to book.

### Solution 1: Optimistic Locking

```sql
-- Read seat with version
SELECT id, status, version FROM seats WHERE id = :seat_id;

-- Try to reserve — only if version hasn't changed
UPDATE seats
SET status = 'reserved', version = version + 1
WHERE id = :seat_id AND status = 'available' AND version = :version;

-- If rows_affected == 0: someone else booked it first → show error
```

Good when contention is moderate. Doesn't hold locks — fails fast.

### Solution 2: Pessimistic Locking (SELECT FOR UPDATE)

```sql
BEGIN;
SELECT * FROM seats WHERE id = :seat_id FOR UPDATE; -- acquires row lock
-- Only one transaction can hold this lock at a time
UPDATE seats SET status = 'reserved' WHERE id = :seat_id;
COMMIT;
```

Guarantees no double-booking. Higher throughput cost due to locks.

### Seat Hold with Expiry

Don't require payment before showing confirmation — that frustrates users. Instead:

1. Reserve the seat for 10 minutes (hold)
2. User completes payment
3. If payment succeeds → mark seat as sold
4. If 10-minute timer expires → release seat back to available

**Implementation:** Redis sorted set `holds` with score = expiry timestamp. A background job scans for expired holds and releases them.

### Read Availability at Scale

Seat inventory is read by millions but written infrequently. Cache available seat counts in Redis. Invalidate on every booking. Show inventory from cache; only lock DB rows on actual checkout.

### Flash Sale (100k concurrent users)

- **Queue inbound requests:** Put users in a virtual queue. Process N bookings/second. Show users their queue position.
- **Pre-generate seat inventory in Redis:** Decrement a counter in Redis (atomic DECR) before hitting the DB. Redis is the fast gate; DB is the source of truth.

---

## 36. Design a Rate Limiter (Standalone)

**Requirements:**
- Limit each user to 100 requests/minute
- Works across a cluster of app servers
- < 5ms overhead per request
- Support multiple rate limit tiers (free vs paid)

### Where to Place It

- **API Gateway:** Centralized, no per-service work. Best for cross-cutting limits.
- **Sidecar / service mesh:** Limits enforced per service independently. Good for internal microservice rate limits.
- **Application middleware:** Simple but requires shared state store.

### Algorithm Choice

**Token Bucket** (recommended for most use cases):
- Each user has a bucket with capacity C tokens, refilled at rate R tokens/second
- Each request consumes 1 token; excess requests are rejected
- Allows short bursts up to capacity, then enforces average rate

```
user_bucket:{user_id} = {tokens: 100, last_refill: timestamp}

On request:
  elapsed = now - last_refill
  new_tokens = min(capacity, tokens + elapsed * refill_rate)
  if new_tokens >= 1:
    store {tokens: new_tokens - 1, last_refill: now}
    allow request
  else:
    reject with 429
```

**Implementation in Redis (atomic Lua script):**

```lua
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1]) or capacity
local last_refill = tonumber(bucket[2]) or now

local elapsed = now - last_refill
local new_tokens = math.min(capacity, tokens + elapsed * refill_rate)

if new_tokens >= 1 then
  redis.call('HMSET', key, 'tokens', new_tokens - 1, 'last_refill', now)
  redis.call('EXPIRE', key, 3600)
  return 1  -- allowed
else
  return 0  -- rejected
end
```

### Response Headers

Return rate limit state in response headers — clients can adapt:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 43
X-RateLimit-Reset: 1705000000   (Unix timestamp of next full bucket)
Retry-After: 17                  (seconds until tokens available, on 429)
```

### Multi-Tier Limits

Store tier in user record. Fetch tier once (cache in Redis for 5 min) and use tier-specific config:

```
free:    100 req/min
pro:     1000 req/min
api_key: 10000 req/min
```

Key: `rate:{tier}:{user_id}` — different bucket params per tier.

### Handling Distributed Inaccuracy

Redis is centralized — all app servers write to one Redis. Slight network delay means two near-simultaneous requests might both see N tokens available. The Lua script's atomicity prevents this: the script runs as a single Redis operation.

For very high throughput, local token bucket + periodic Redis sync (every 100ms): accept slight over-admission in exchange for dramatically lower Redis traffic.

---

# Part 5: Reference

---

## 23. Database Selection Guide

| Use Case | Best Choice | Why |
|----------|------------|-----|
| User profiles, orders, transactions | PostgreSQL | Relational integrity, complex queries |
| Product catalog (flexible attributes) | MongoDB | Dynamic schema per product category |
| Sessions, real-time leaderboards | Redis | Sub-millisecond, sorted sets, TTL |
| Activity logs, time-series | Cassandra, InfluxDB | Append-only, time-ordered, huge write throughput |
| Full-text search | Elasticsearch | Inverted index, relevance scoring |
| Social graph, recommendations | Neo4j | Graph traversal is first-class |
| File/blob storage | S3 + CDN | Cheap, durable, globally distributed |
| Chat messages | Cassandra | Time-ordered, partition by conversation |
| Analytics / data warehouse | BigQuery, Redshift, ClickHouse | Columnar storage, OLAP queries |

---

## 24. Trade-offs Cheat Sheet

| Decision | Option A | Option B | Choose A when | Choose B when |
|----------|---------|---------|---------------|---------------|
| Sync vs Async | Synchronous | Message queue | Response needed immediately | Decoupling / resilience more important |
| SQL vs NoSQL | PostgreSQL | MongoDB/Cassandra | Complex relations, strict consistency | Horizontal scale, flexible schema |
| Push vs Pull feed | Fan-out on write | Fan-out on read | Users follow ≤ 1000 accounts | Celebrity accounts with huge follower counts |
| Cache consistency | Write-through | Cache-aside | Cache must always be fresh | Cache only hot data |
| Monolith vs Microservices | Monolith | Microservices | Early stage, small team | Independent scale, multiple teams |
| Strong vs Eventual consistency | Strong | Eventual | Financial transactions, inventory | Social feeds, counters, DNS |
| 301 vs 302 redirect | 301 Permanent | 302 Temporary | URL never changes (CDN-cached) | Want to control redirects / track clicks |
| Polling vs WebSocket vs SSE | Polling | WebSocket | Simple one-way updates (notifications) | Bidirectional real-time (chat, gaming) |
| Horizontal sharding | Hash sharding | Range sharding | Even distribution needed | Range queries are common |
