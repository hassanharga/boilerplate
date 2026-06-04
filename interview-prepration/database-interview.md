# Database Interview Reference

Senior-focused. Every section: concept explanation + code/config example.

---

## Table of Contents

**Part 1 — Relational Fundamentals**
1. [Relational Model & Normalization](#1-relational-model--normalization)
2. [ACID Properties](#2-acid-properties)
3. [Transaction Isolation Levels](#3-transaction-isolation-levels)
4. [Indexes](#4-indexes)
5. [Query Execution & EXPLAIN](#5-query-execution--explain)
6. [Joins & Execution Strategies](#6-joins--execution-strategies)
7. [Window Functions](#7-window-functions)
8. [CTEs & Recursive Queries](#8-ctes--recursive-queries)

**Part 2 — PostgreSQL Deep Dive**
9. [JSONB, Arrays & Full-Text Search](#9-jsonb-arrays--full-text-search)
10. [Connection Pooling (PgBouncer)](#10-connection-pooling-pgbouncer)
11. [Partitioning](#11-partitioning)
12. [Replication](#12-replication)
13. [Autovacuum & Bloat](#13-autovacuum--bloat)

**Part 3 — SQL vs NoSQL**
14. [SQL vs NoSQL Decision Guide](#14-sql-vs-nosql-decision-guide)
15. [CAP Theorem in Practice](#15-cap-theorem-in-practice)
16. [Consistency Models](#16-consistency-models)

**Part 4 — MongoDB**
17. [Documents, Collections & Schema Design](#17-documents-collections--schema-design)
18. [Embedding vs Referencing](#18-embedding-vs-referencing)
19. [Aggregation Pipeline](#19-aggregation-pipeline)
20. [MongoDB Indexes](#20-mongodb-indexes)
21. [Multi-Document Transactions](#21-multi-document-transactions)
22. [Change Streams](#22-change-streams)

**Part 5 — Redis**
23. [Data Structures & Use Cases](#23-data-structures--use-cases)
24. [Pub/Sub vs Streams](#24-pubsub-vs-streams)
25. [Persistence: RDB vs AOF](#25-persistence-rdb-vs-aof)
26. [Cluster vs Sentinel](#26-cluster-vs-sentinel)

**Part 6 — Patterns & Production**
27. [N+1 Problem & Fixes](#27-n1-problem--fixes)
28. [Database Migrations (Expand/Contract)](#28-database-migrations-expandcontract)
29. [Sharding Strategies](#29-sharding-strategies)
30. [CQRS & Read Replicas](#30-cqrs--read-replicas)

**Part 1 (continued): Relational Fundamentals**
31. [Deadlocks](#31-deadlocks)
32. [Optimistic vs Pessimistic Locking](#32-optimistic-vs-pessimistic-locking)
33. [Data Types & Their Impact](#33-data-types--their-impact)

**Part 2 (continued): PostgreSQL Deep Dive**
34. [Stored Procedures, Functions & Triggers](#34-stored-procedures-functions--triggers)
35. [Views vs Materialized Views](#35-views-vs-materialized-views)
36. [Database Backup & Recovery](#36-database-backup--recovery)

**Part 4 (continued): MongoDB**
37. [Managed Databases (Atlas & RDS)](#37-managed-databases-atlas--rds)

**Part 6 (continued): Patterns & Production**
38. [Database Connection Lifecycle](#38-database-connection-lifecycle)
39. [Soft Delete Patterns](#39-soft-delete-patterns)

**Part 7 — Search Engines**
40. [Elasticsearch & Full-Text Search at Scale](#40-elasticsearch--full-text-search-at-scale)

---

## Part 1 — Relational Fundamentals

---

### 1. Relational Model & Normalization

**Relational model** organizes data into tables (relations) with rows (tuples) and columns (attributes). Relations are linked via foreign keys.

**Normal Forms** — goal: eliminate redundancy and update anomalies.

| Form | Rule | Violation Example |
|------|------|-------------------|
| 1NF | Atomic values, no repeating groups | `tags = "js,ts,node"` in one column |
| 2NF | No partial dependency on composite PK | `order_items(order_id, product_id, product_name)` — `product_name` depends only on `product_id` |
| 3NF | No transitive dependency | `employees(id, dept_id, dept_name)` — `dept_name` depends on `dept_id`, not `id` |
| BCNF | Every determinant is a candidate key | Rare — stricter than 3NF |

**When to denormalize:** read-heavy analytics tables, pre-aggregated reporting, or when joins become a bottleneck. Always normalize first, denormalize with a measured reason.

```sql
-- Normalized: 3NF
CREATE TABLE departments (
  id   SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE employees (
  id         SERIAL PRIMARY KEY,
  name       TEXT NOT NULL,
  dept_id    INT REFERENCES departments(id)
  -- no dept_name here — that's a transitive dependency
);

-- Denormalized (for analytics): pre-joined snapshot table
CREATE TABLE employee_report AS
  SELECT e.id, e.name, d.name AS dept_name
  FROM employees e
  JOIN departments d ON d.id = e.dept_id;
```

---

### 2. ACID Properties

ACID is the guarantee that database transactions are processed reliably. Each property prevents a specific class of failure.

#### Atomicity — all or nothing

A transaction either commits fully or rolls back completely. No partial writes.

**Implementation:** write-ahead log (WAL). Changes are written to the log before the data pages. On crash, uncommitted transactions are rolled back from the log.

```sql
BEGIN;
  UPDATE accounts SET balance = balance - 500 WHERE id = 1;
  UPDATE accounts SET balance = balance + 500 WHERE id = 2;
  -- if the second UPDATE fails, the first is rolled back
COMMIT;

-- Demonstrating the guarantee:
BEGIN;
  UPDATE accounts SET balance = balance - 500 WHERE id = 1;
  -- simulate error
  UPDATE accounts SET balance = balance + 500 WHERE id = 999; -- id doesn't exist
  -- ERROR: both updates are rolled back. Account 1 keeps its balance.
ROLLBACK; -- or the DB does it automatically on error
```

#### Consistency — valid state to valid state

A transaction brings the DB from one valid state to another. All constraints (FK, UNIQUE, CHECK, triggers) must hold after commit.

```sql
ALTER TABLE orders ADD CONSTRAINT chk_amount CHECK (amount > 0);

BEGIN;
  INSERT INTO orders (user_id, amount) VALUES (1, -50); -- violates CHECK
  -- ERROR: new row violates check constraint "chk_amount"
  -- transaction is aborted; DB remains consistent
COMMIT;
```

Consistency is the only ACID property partially enforced by the **application** — referential integrity, business rules in code, etc.

#### Isolation — concurrent transactions don't interfere

Concurrent transactions behave as if they executed serially. The degree of isolation is configurable (see Section 3).

```sql
-- Session A                          -- Session B
BEGIN;                                BEGIN;
SELECT balance FROM accounts          
WHERE id = 1; -- returns 1000

                                      UPDATE accounts
                                      SET balance = 800
                                      WHERE id = 1;
                                      COMMIT;

SELECT balance FROM accounts
WHERE id = 1;
-- READ COMMITTED: sees 800 (non-repeatable read)
-- REPEATABLE READ: still sees 1000 (snapshot)
COMMIT;
```

#### Durability — committed data survives crashes

Once `COMMIT` returns, data is persisted even if the server crashes immediately after.

**Implementation:** WAL (write-ahead log) is fsynced to disk before `COMMIT` returns. On recovery, the DB replays the WAL to restore committed state.

```
Timeline:
  BEGIN → write WAL → fsync WAL → COMMIT ack → (crash here is safe)
                                              → update data pages (async)
```

**Tunable durability (PostgreSQL):**
```sql
-- Faster writes, slight durability risk on OS crash (not DB crash)
SET synchronous_commit = off;

-- Per-transaction durability override (e.g. for bulk loads)
BEGIN;
  SET LOCAL synchronous_commit = off;
  INSERT INTO bulk_data SELECT * FROM staging;
COMMIT;
```

#### ACID in NoSQL

Most NoSQL databases sacrifice some ACID properties for availability/performance. MongoDB offers multi-document ACID transactions since v4.0, but single-document operations have always been atomic.

---

### 3. Transaction Isolation Levels

Isolation levels trade consistency guarantees for concurrency performance. Higher isolation = fewer anomalies, more locking/blocking.

#### Anomalies

| Anomaly | Description |
|---------|-------------|
| Dirty Read | Read uncommitted data from another transaction |
| Non-Repeatable Read | Same row returns different values within one transaction |
| Phantom Read | Same query returns different rows (new rows inserted by another tx) |
| Serialization Anomaly | Result differs from any serial execution of the transactions |

#### Isolation Level Comparison

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | PG Default |
|-------|-----------|---------------------|--------------|------------|
| Read Uncommitted | Possible | Possible | Possible | (treated as RC) |
| Read Committed | No | Possible | Possible | ✓ Default |
| Repeatable Read | No | No | No* | |
| Serializable | No | No | No | |

*PostgreSQL's Repeatable Read also prevents phantoms (unlike SQL standard).

```sql
-- Set isolation level for a transaction
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
  SELECT * FROM inventory WHERE product_id = 42;
  -- ... do work ...
  SELECT * FROM inventory WHERE product_id = 42; -- always same result
COMMIT;

-- Serializable — SSI (Serializable Snapshot Isolation) in PostgreSQL
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
  SELECT SUM(amount) FROM orders WHERE user_id = 1;
  INSERT INTO orders (user_id, amount) VALUES (1, 100);
COMMIT;
-- If another concurrent serializable tx conflicts, one gets:
-- ERROR: could not serialize access due to read/write dependencies
-- App must retry the transaction
```

**Choosing a level:**
- Default `READ COMMITTED` is fine for most CRUD
- `REPEATABLE READ` for reports/analytics that need a consistent snapshot
- `SERIALIZABLE` for financial operations, inventory deductions, or any "check then write" logic

---

### 4. Indexes

An index is a separate data structure that speeds up lookups at the cost of write overhead and storage.

#### Index Types

| Type | Best For | Notes |
|------|----------|-------|
| B-tree | `=`, `<`, `>`, `BETWEEN`, `LIKE 'prefix%'` | Default in PostgreSQL |
| Hash | `=` only | Faster than B-tree for equality, not WAL-logged before PG10 |
| GIN | Arrays, JSONB, full-text | Multi-key entries; slower writes |
| GiST | Geometric, range, full-text | Lossy; requires recheck |
| BRIN | Sequential data (timestamps, IDs) | Tiny size; good for append-only tables |

```sql
-- Basic B-tree
CREATE INDEX idx_orders_user ON orders(user_id);

-- Composite index — column order matters: most selective first,
-- then by query patterns (equality before range)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index — index only active users (smaller, faster)
CREATE INDEX idx_users_active ON users(email) WHERE active = true;

-- Covering index — avoids heap fetch (index-only scan)
CREATE INDEX idx_orders_covering ON orders(user_id) INCLUDE (created_at, total);

-- Expression index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
-- Requires query to match: WHERE LOWER(email) = 'foo@bar.com'
```

#### Index Pitfalls

```sql
-- NEVER: leading wildcard kills the index
SELECT * FROM users WHERE email LIKE '%@gmail.com'; -- full seq scan

-- NEVER: function on indexed column
SELECT * FROM users WHERE UPPER(name) = 'ALICE'; -- use expression index instead

-- NEVER: implicit cast
-- If user_id is INT but you pass a string, the index may not be used
SELECT * FROM orders WHERE user_id = '123'; -- '123' is text, causes cast

-- Check for unused indexes (they still cost on every write):
SELECT indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

---

### 5. Query Execution & EXPLAIN

The query planner chooses between seq scan, index scan, bitmap scan, etc. `EXPLAIN ANALYZE` shows the actual plan with timing.

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.name, COUNT(o.id)
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.id;
```

**Reading EXPLAIN output:**

```
Hash Join  (cost=125.00..980.00 rows=5000 width=40) (actual time=12.3..45.6 rows=4821 loops=1)
  Hash Cond: (o.user_id = u.id)
  Buffers: shared hit=320 read=45          <-- cache hits vs disk reads
  ->  Seq Scan on orders o                 <-- no index used on orders
        Filter: (created_at > ...)
        Rows Removed by Filter: 95000
  ->  Hash  (cost=55.00..55.00 rows=1000)
        ->  Seq Scan on users u

Planning Time: 1.2 ms
Execution Time: 47.8 ms
```

**Key signals:**
- `Seq Scan` on large tables → missing index
- `Rows Removed by Filter: 95000` → index would help
- `Buffers: read=N` (disk reads) → table not in cache, or missing index
- `Hash Join` vs `Nested Loop` → planner choice based on row estimates; wrong row estimates (stale statistics) cause bad plans

```sql
-- Fix stale statistics
ANALYZE orders;
-- Or configure autovacuum to analyze more frequently
```

---

### 6. Joins & Execution Strategies

```sql
-- INNER JOIN: only matching rows
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON o.user_id = u.id;

-- LEFT JOIN: all users, nulls for users with no orders
SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;

-- Self-join: employees and their managers
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;
```

**Join Execution Strategies** (planner picks based on row counts and indexes):

| Strategy | When Used | Cost Profile |
|----------|-----------|--------------|
| Nested Loop | Small outer set + index on inner | O(N * index_lookup) |
| Hash Join | Large tables, no useful index | O(N+M), uses memory |
| Merge Join | Both sides pre-sorted | O(N log N + M log M) |

```sql
-- Force a specific join strategy (for testing)
SET enable_hashjoin = off;
EXPLAIN SELECT ...;
SET enable_hashjoin = on;
```

---

### 7. Window Functions

Window functions compute values across a set of rows related to the current row — without collapsing rows like `GROUP BY` does.

```sql
-- ROW_NUMBER, RANK, DENSE_RANK
SELECT
  name,
  salary,
  dept_id,
  ROW_NUMBER()  OVER (PARTITION BY dept_id ORDER BY salary DESC) AS row_num,
  RANK()        OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rank,
  DENSE_RANK()  OVER (PARTITION BY dept_id ORDER BY salary DESC) AS dense_rank
FROM employees;
-- RANK skips numbers after ties (1,1,3); DENSE_RANK doesn't (1,1,2)

-- Running total
SELECT
  id,
  amount,
  SUM(amount) OVER (ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM orders;

-- LEAD / LAG — access adjacent rows
SELECT
  id,
  amount,
  LAG(amount)  OVER (ORDER BY created_at) AS prev_amount,
  LEAD(amount) OVER (ORDER BY created_at) AS next_amount
FROM orders;

-- NTILE — divide into N buckets
SELECT name, salary,
  NTILE(4) OVER (ORDER BY salary) AS quartile
FROM employees;

-- FIRST_VALUE / LAST_VALUE
SELECT
  name,
  salary,
  FIRST_VALUE(salary) OVER (PARTITION BY dept_id ORDER BY salary DESC) AS top_salary
FROM employees;
```

---

### 8. CTEs & Recursive Queries

**CTE (Common Table Expression)** — named subquery, improves readability. In PostgreSQL, CTEs are an "optimization fence" by default (materialized); use `NOT MATERIALIZED` to let the planner inline it.

```sql
-- Basic CTE
WITH recent_orders AS (
  SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '7 days'
),
order_totals AS (
  SELECT user_id, SUM(total) AS week_total FROM recent_orders GROUP BY user_id
)
SELECT u.name, ot.week_total
FROM users u
JOIN order_totals ot ON ot.user_id = u.id;

-- NOT MATERIALIZED: let planner optimize (PostgreSQL 12+)
WITH active_users AS NOT MATERIALIZED (
  SELECT * FROM users WHERE active = true
)
SELECT * FROM active_users WHERE email LIKE '%@example.com';
```

**Recursive CTE** — for tree/graph structures (org charts, categories, file systems):

```sql
-- Org chart: find all reports under employee id=5
WITH RECURSIVE org_tree AS (
  -- Base case: the root employee
  SELECT id, name, manager_id, 0 AS depth
  FROM employees
  WHERE id = 5

  UNION ALL

  -- Recursive case: their direct reports
  SELECT e.id, e.name, e.manager_id, ot.depth + 1
  FROM employees e
  JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT * FROM org_tree ORDER BY depth;

-- Prevent infinite loops (cycles in graph)
WITH RECURSIVE graph_traversal AS (
  SELECT id, ARRAY[id] AS visited
  FROM nodes WHERE id = 1

  UNION ALL

  SELECT n.id, gt.visited || n.id
  FROM nodes n
  JOIN edges e ON e.to_id = n.id
  JOIN graph_traversal gt ON gt.id = e.from_id
  WHERE NOT n.id = ANY(gt.visited)  -- cycle guard
)
SELECT * FROM graph_traversal;
```

---

## Part 2 — PostgreSQL Deep Dive

---

### 9. JSONB, Arrays & Full-Text Search

**JSONB** — binary JSON. Indexed, faster to query than `JSON` (which stores raw text).

```sql
-- JSONB column
CREATE TABLE products (
  id       SERIAL PRIMARY KEY,
  name     TEXT,
  metadata JSONB
);

INSERT INTO products VALUES (1, 'Laptop', '{"brand": "Dell", "specs": {"ram": 16, "cpu": "i7"}}');

-- Query operators
SELECT * FROM products WHERE metadata->>'brand' = 'Dell';
SELECT * FROM products WHERE metadata @> '{"specs": {"ram": 16}}'; -- containment
SELECT metadata#>>'{specs,cpu}' FROM products WHERE id = 1;        -- path access

-- GIN index on JSONB (enables @>, ?, ?|, ?& operators)
CREATE INDEX idx_products_meta ON products USING GIN (metadata);

-- Specific path index (smaller, faster for known keys)
CREATE INDEX idx_products_brand ON products ((metadata->>'brand'));
```

**Arrays:**

```sql
CREATE TABLE posts (id SERIAL, tags TEXT[]);
INSERT INTO posts VALUES (1, ARRAY['postgres', 'sql', 'performance']);

SELECT * FROM posts WHERE tags @> ARRAY['sql'];      -- contains
SELECT * FROM posts WHERE tags && ARRAY['sql','redis']; -- overlaps
SELECT * FROM posts WHERE 'sql' = ANY(tags);

-- GIN index for array operations
CREATE INDEX idx_posts_tags ON posts USING GIN (tags);
```

**Full-Text Search:**

```sql
-- tsvector (document) and tsquery (search)
SELECT to_tsvector('english', 'PostgreSQL is a powerful relational database')
  @@ to_tsquery('english', 'powerful & database'); -- true

-- Stored tsvector column with GIN index (fast)
ALTER TABLE articles ADD COLUMN search_vector tsvector;

UPDATE articles
SET search_vector = to_tsvector('english', title || ' ' || body);

CREATE INDEX idx_articles_fts ON articles USING GIN (search_vector);

-- Search with ranking
SELECT title,
  ts_rank(search_vector, query) AS rank
FROM articles, to_tsquery('english', 'postgresql & performance') query
WHERE search_vector @@ query
ORDER BY rank DESC;

-- Auto-update with trigger
CREATE TRIGGER update_search_vector
  BEFORE INSERT OR UPDATE ON articles
  FOR EACH ROW EXECUTE FUNCTION
    tsvector_update_trigger(search_vector, 'pg_catalog.english', title, body);
```

---

### 10. Connection Pooling (PgBouncer)

PostgreSQL creates a new OS process per connection (~5MB RAM). At 1000 connections = 5GB RAM just for connections. PgBouncer sits between app and DB, multiplexing many app connections onto fewer DB connections.

**Pooling modes:**

| Mode | Connection held until... | Safe for... |
|------|--------------------------|-------------|
| Session | Client disconnects | All SQL (SET, prepared stmts) |
| Transaction | Transaction ends | Most apps (no session-level state) |
| Statement | Statement ends | Simple queries only (no multi-statement tx) |

```ini
# pgbouncer.ini
[databases]
mydb = host=localhost dbname=mydb

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000   ; app connections to PgBouncer
default_pool_size = 25   ; connections PgBouncer keeps to PostgreSQL
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
server_idle_timeout = 600
```

```javascript
// Application: connect to PgBouncer port (5432 → 6432)
const pool = new Pool({
  host: 'localhost',
  port: 6432,          // PgBouncer port
  database: 'mydb',
  max: 100,            // PgBouncer handles the real multiplexing
});

// Avoid session-level features in transaction mode:
// ❌ SET search_path = myschema  (session-scoped)
// ❌ LISTEN / NOTIFY             (session-scoped)
// ❌ Advisory locks              (session-scoped)
// ✓ Everything else
```

---

### 11. Partitioning

Splits a large table into smaller physical pieces (partitions) while appearing as one logical table. Improves query performance via partition pruning and simplifies data lifecycle management (drop old partitions instead of DELETE).

```sql
-- Range partitioning (e.g., time-series data)
CREATE TABLE orders (
  id          BIGSERIAL,
  user_id     INT,
  created_at  TIMESTAMPTZ NOT NULL,
  total       NUMERIC
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024_q1 PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
  FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Indexes on partitioned table apply to all partitions
CREATE INDEX ON orders(user_id);

-- PostgreSQL prunes partitions automatically:
SELECT * FROM orders WHERE created_at BETWEEN '2024-01-01' AND '2024-03-31';
-- Only scans orders_2024_q1

-- Dropping old data is instant (vs slow DELETE)
DROP TABLE orders_2023_q1;

-- List partitioning (e.g., by region)
CREATE TABLE events (
  id      BIGSERIAL,
  region  TEXT NOT NULL,
  data    JSONB
) PARTITION BY LIST (region);

CREATE TABLE events_us PARTITION OF events FOR VALUES IN ('us-east', 'us-west');
CREATE TABLE events_eu PARTITION OF events FOR VALUES IN ('eu-west', 'eu-central');

-- Hash partitioning (even distribution, no natural key)
CREATE TABLE sessions (
  id      UUID NOT NULL,
  data    JSONB
) PARTITION BY HASH (id);

CREATE TABLE sessions_0 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sessions_1 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE sessions_2 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE sessions_3 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

---

### 12. Replication

**Streaming Replication** (physical) — WAL bytes streamed to standby. Exact byte-level copy of primary. Used for HA failover.

```
Primary ──WAL stream──► Standby (hot standby, read-only queries allowed)
```

```ini
# postgresql.conf (primary)
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1GB

# pg_hba.conf (primary) — allow standby to connect
host replication replicator standby_ip/32 scram-sha-256
```

```ini
# recovery.conf or postgresql.conf (standby, PG12+)
primary_conninfo = 'host=primary_ip user=replicator password=secret'
hot_standby = on
```

**Logical Replication** — replicates changes at row level. Allows replicating to different PG versions, selective tables, or external systems (Kafka via Debezium).

```sql
-- Primary: create publication
CREATE PUBLICATION orders_pub FOR TABLE orders, order_items;

-- Standby/subscriber: create subscription
CREATE SUBSCRIPTION orders_sub
  CONNECTION 'host=primary dbname=mydb user=replicator password=secret'
  PUBLICATION orders_pub;
```

**Synchronous vs Asynchronous:**
- Async (default): `COMMIT` returns before standby confirms — fast, tiny data loss window on failover
- Sync: `COMMIT` waits for standby confirmation — zero data loss, latency penalty

```ini
# Sync replication (primary)
synchronous_standby_names = 'FIRST 1 (standby1, standby2)'
synchronous_commit = on
```

---

### 13. Autovacuum & Bloat

PostgreSQL uses MVCC (Multi-Version Concurrency Control) — instead of overwriting rows, it marks old versions as dead and inserts new ones. Autovacuum reclaims dead row space and updates statistics.

**Bloat** — dead rows accumulate, wasting disk space and slowing queries.

```sql
-- Check table bloat
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
  n_dead_tup,
  n_live_tup,
  ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- Manual VACUUM on a bloated table
VACUUM (VERBOSE, ANALYZE) orders;

-- VACUUM FULL — reclaims all space but locks the table (use pg_repack instead)
-- VACUUM FULL orders; ← avoid in production

-- Tune autovacuum for high-churn tables
ALTER TABLE orders SET (
  autovacuum_vacuum_scale_factor = 0.01,    -- vacuum when 1% rows are dead (default 20%)
  autovacuum_analyze_scale_factor = 0.005,  -- analyze when 0.5% rows change
  autovacuum_vacuum_cost_delay = 2          -- ms delay between I/O bursts (default 20ms)
);
```

---

## Part 3 — SQL vs NoSQL

---

### 14. SQL vs NoSQL Decision Guide

| Factor | SQL | NoSQL |
|--------|-----|-------|
| Data structure | Fixed schema, structured | Flexible / schemaless |
| Relationships | Strong FK + JOIN | Embedding or manual references |
| ACID | Native | Varies (MongoDB: multi-doc ACID since v4.0) |
| Scaling | Vertical + read replicas | Horizontal sharding |
| Query language | Standard SQL | DB-specific APIs |
| Best for | Financial, ERP, CRM, anything relational | Catalogs, logs, caches, user profiles, real-time feeds |

**Choose SQL (PostgreSQL) when:**
- Data has relationships that you query across
- Consistency and integrity constraints matter (finance, healthcare, e-commerce inventory)
- Schema is relatively stable
- You need complex ad-hoc queries

**Choose MongoDB when:**
- Document-centric data with variable shape (product catalogs, CMS)
- You need horizontal scale out of the box
- Rapid iteration / schema evolution
- Geo queries, full-text search within the same DB

**Choose Redis when:**
- Caching
- Sessions, rate limiting counters
- Pub/Sub or job queues
- Leaderboards, real-time analytics

**Polyglot persistence** — use multiple databases, each for its strength. A typical stack:
```
PostgreSQL (source of truth) + Redis (cache/sessions) + Elasticsearch (search)
```

---

### 15. CAP Theorem in Practice

In a distributed system, you can only guarantee **2 of 3**:
- **C**onsistency — every read sees the most recent write
- **A**vailability — every request gets a (non-error) response
- **P**artition Tolerance — system works despite network splits

Network partitions are unavoidable in distributed systems, so the real choice is **CP vs AP** during a partition.

| Database | CAP Classification | Behavior on Partition |
|----------|-------------------|----------------------|
| PostgreSQL (single) | CA (non-distributed) | N/A |
| PostgreSQL + streaming replication | CP | Standby may refuse reads (stale) |
| MongoDB (replica set) | CP | Primary stays up, secondaries stale |
| MongoDB (sharded) | CP | |
| Cassandra | AP | All nodes respond, may return stale data |
| DynamoDB | AP (default) / CP (strong reads) | Available but potentially stale |
| Redis (cluster) | AP | Continues with stale data on partition |
| Zookeeper / etcd | CP | Refuses reads if no quorum |

```
Practical implication for interviews:
"We use eventual consistency for user feeds (AP) but strong consistency
for payments (CP) — we'd rather fail than show a stale balance."
```

---

### 16. Consistency Models

| Model | Guarantee | Example |
|-------|-----------|---------|
| Strong / Linearizable | Every read sees the latest write | PostgreSQL SERIALIZABLE, etcd |
| Sequential | All nodes see same order, not necessarily latest | Single-leader replication |
| Causal | Causally related ops seen in order | MongoDB causal sessions |
| Eventual | Replicas converge eventually | DNS, Cassandra, DynamoDB default |
| Read-your-writes | You always see your own writes | MongoDB primary reads, sticky sessions |

```javascript
// MongoDB: causal consistency session
const session = client.startSession({ causalConsistency: true });
await collection.insertOne({ _id: 1, status: 'active' }, { session });
// Guaranteed to see the insert in subsequent reads within same session
const doc = await collection.findOne({ _id: 1 }, { session });
```

---

## Part 4 — MongoDB

---

### 17. Documents, Collections & Schema Design

MongoDB stores documents (BSON) in collections. No fixed schema required, but you should design intentionally.

```javascript
// Document example
{
  _id: ObjectId("..."),
  userId: "usr_123",
  name: "Alice",
  email: "alice@example.com",
  createdAt: ISODate("2024-01-01T00:00:00Z"),
  address: {                         // embedded sub-document
    street: "123 Main St",
    city: "Cairo",
    country: "EG"
  },
  tags: ["premium", "verified"]      // array field
}
```

**Schema validation (JSON Schema):**

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "createdAt"],
      properties: {
        email: { bsonType: "string", pattern: "^.+@.+$" },
        age:   { bsonType: "int", minimum: 0, maximum: 150 },
        status: { enum: ["active", "suspended", "deleted"] }
      }
    }
  },
  validationAction: "error"  // or "warn"
});
```

---

### 18. Embedding vs Referencing

The central schema design decision in MongoDB.

| | Embedding | Referencing |
|-|-----------|-------------|
| Access pattern | Always fetch together | Often fetch separately |
| Relationship | One-to-few | One-to-many / many-to-many |
| Update frequency | Updated together | Updated independently |
| Document size | Stays small | Large sub-document |
| Query | Single read | Multiple reads or $lookup |

```javascript
// Embedding — user with address (always accessed together)
{
  _id: "usr_1",
  name: "Alice",
  address: { city: "Cairo", country: "EG" }   // embedded
}

// Referencing — orders reference user (orders grow unboundedly)
// users collection
{ _id: "usr_1", name: "Alice" }

// orders collection
{ _id: "ord_1", userId: "usr_1", total: 150, items: [...] }

// JOIN equivalent: $lookup
db.orders.aggregate([
  { $match: { userId: "usr_1" } },
  { $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "user"
  }},
  { $unwind: "$user" }
]);

// Hybrid — embed a bounded list, reference the rest
// Post with first 3 comments embedded, reference collection for the rest
{
  _id: "post_1",
  title: "...",
  commentCount: 142,
  recentComments: [   // only last 3 — bounded
    { author: "Bob", text: "..." },
    { author: "Carol", text: "..." }
  ]
}
```

---

### 19. Aggregation Pipeline

The aggregation pipeline processes documents through stages, each transforming the data.

```javascript
// Sales report: top 5 products last 30 days by revenue
db.orders.aggregate([
  // Stage 1: filter
  { $match: {
    createdAt: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) },
    status: "completed"
  }},

  // Stage 2: flatten array of items
  { $unwind: "$items" },

  // Stage 3: group by product
  { $group: {
    _id: "$items.productId",
    revenue:  { $sum: { $multiply: ["$items.price", "$items.qty"] } },
    unitsSold: { $sum: "$items.qty" }
  }},

  // Stage 4: sort
  { $sort: { revenue: -1 } },

  // Stage 5: limit
  { $limit: 5 },

  // Stage 6: join product details
  { $lookup: {
    from: "products",
    localField: "_id",
    foreignField: "_id",
    as: "product"
  }},
  { $unwind: "$product" },

  // Stage 7: reshape output
  { $project: {
    _id: 0,
    productName: "$product.name",
    revenue: 1,
    unitsSold: 1
  }}
]);

// $facet — multiple aggregations in one pass
db.products.aggregate([
  { $match: { active: true } },
  { $facet: {
    byCategory: [
      { $group: { _id: "$category", count: { $sum: 1 } } }
    ],
    priceStats: [
      { $group: { _id: null, avg: { $avg: "$price" }, max: { $max: "$price" } } }
    ]
  }}
]);
```

---

### 20. MongoDB Indexes

```javascript
// Single field
db.users.createIndex({ email: 1 }, { unique: true });

// Compound index (order matters: equality fields first, then sort, then range)
db.orders.createIndex({ userId: 1, status: 1, createdAt: -1 });

// Text index (full-text search)
db.articles.createIndex(
  { title: "text", body: "text" },
  { weights: { title: 10, body: 1 } }  // title matches count 10x more
);
db.articles.find({ $text: { $search: "mongodb performance" } },
                 { score: { $meta: "textScore" } })
           .sort({ score: { $meta: "textScore" } });

// TTL index — auto-delete documents after N seconds
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 });

// Sparse index — only indexes documents that have the field
db.users.createIndex({ phoneNumber: 1 }, { sparse: true });

// Partial index — index only matching documents (smaller, faster)
db.orders.createIndex(
  { userId: 1 },
  { partialFilterExpression: { status: "pending" } }
);

// Geospatial
db.stores.createIndex({ location: "2dsphere" });
db.stores.find({
  location: {
    $near: { $geometry: { type: "Point", coordinates: [31.2, 30.0] }, $maxDistance: 5000 }
  }
});

// Check index usage
db.orders.find({ userId: "usr_1" }).explain("executionStats");
// Look for: IXSCAN (good) vs COLLSCAN (bad), nReturned vs totalDocsExamined
```

---

### 21. Multi-Document Transactions

Single-document operations in MongoDB are always atomic. For operations spanning multiple documents/collections, use transactions (requires replica set or sharded cluster).

```javascript
const session = client.startSession();

try {
  await session.withTransaction(async () => {
    // Deduct from sender
    await accounts.updateOne(
      { _id: senderId, balance: { $gte: amount } },
      { $inc: { balance: -amount } },
      { session }
    );

    // Add to receiver
    await accounts.updateOne(
      { _id: receiverId },
      { $inc: { balance: amount } },
      { session }
    );

    // Log the transfer
    await transfers.insertOne(
      { from: senderId, to: receiverId, amount, createdAt: new Date() },
      { session }
    );
  }, {
    readConcern: { level: "snapshot" },
    writeConcern: { w: "majority" },
    readPreference: "primary"
  });
} finally {
  await session.endSession();
}

// Mongoose equivalent
const session = await mongoose.startSession();
session.startTransaction();
try {
  await Account.updateOne({ _id: senderId }, { $inc: { balance: -amount } }, { session });
  await Account.updateOne({ _id: receiverId }, { $inc: { balance: amount } }, { session });
  await session.commitTransaction();
} catch (err) {
  await session.abortTransaction();
  throw err;
} finally {
  session.endSession();
}
```

**When NOT to use transactions:** if you can design your schema to make the operation single-document, you don't need a transaction (and it'll be faster).

---

### 22. Change Streams

Change streams let you subscribe to real-time data changes using MongoDB's oplog. Useful for event-driven architectures, cache invalidation, audit logs.

```javascript
// Watch all changes on a collection
const changeStream = db.collection("orders").watch([
  { $match: { "operationType": { $in: ["insert", "update"] } } }
], {
  fullDocument: "updateLookup"  // include the full updated document
});

changeStream.on("change", (event) => {
  if (event.operationType === "insert") {
    console.log("New order:", event.fullDocument);
    // trigger order confirmation email
  }
  if (event.operationType === "update") {
    console.log("Updated:", event.fullDocument);
    // invalidate cache
  }
});

// Resume after restart using resumeToken
let resumeToken;

changeStream.on("change", (event) => {
  resumeToken = event._id;  // save this to persistent storage
  processEvent(event);
});

// On restart:
const resumedStream = collection.watch(pipeline, { resumeAfter: resumeToken });
```

---

## Part 5 — Redis

---

### 23. Data Structures & Use Cases

| Structure | Commands | Use Cases |
|-----------|----------|-----------|
| String | `GET`, `SET`, `INCR`, `EXPIRE` | Cache, counters, session tokens |
| Hash | `HGET`, `HSET`, `HGETALL` | User sessions, config objects |
| List | `LPUSH`, `RPOP`, `LRANGE` | Task queues, activity feeds |
| Set | `SADD`, `SMEMBERS`, `SINTERSTORE` | Tags, unique visitors, online users |
| Sorted Set | `ZADD`, `ZRANGE`, `ZRANK` | Leaderboards, rate limiting, delayed queues |
| Stream | `XADD`, `XREAD`, `XACK` | Event log, message bus |
| Bitmap | `SETBIT`, `BITCOUNT` | Feature flags, daily active users |
| HyperLogLog | `PFADD`, `PFCOUNT` | Approximate unique count (0.81% error) |

```javascript
const redis = require("ioredis");
const client = new redis();

// String: cache with TTL
await client.set("user:123", JSON.stringify(user), "EX", 3600);
const cached = JSON.parse(await client.get("user:123"));

// Hash: session
await client.hset("session:abc", { userId: "123", role: "admin", createdAt: Date.now() });
const session = await client.hgetall("session:abc");

// Sorted Set: leaderboard
await client.zadd("leaderboard", 9800, "alice", 8500, "bob", 7200, "carol");
const top3 = await client.zrevrange("leaderboard", 0, 2, "WITHSCORES");

// Sorted Set: rate limiting (sliding window with score = timestamp)
const now = Date.now();
const windowStart = now - 60_000;
const key = `ratelimit:${userId}`;
const pipeline = client.pipeline();
pipeline.zremrangebyscore(key, 0, windowStart);       // remove old entries
pipeline.zadd(key, now, `${now}-${Math.random()}`);   // add current request
pipeline.zcard(key);                                   // count requests in window
pipeline.expire(key, 60);
const results = await pipeline.exec();
const requestCount = results[2][1];
if (requestCount > 100) throw new Error("Rate limit exceeded");

// Bitmap: track daily active users (bit per user ID per day)
const today = new Date().toISOString().split("T")[0];
await client.setbit(`dau:${today}`, userId, 1);
const dauCount = await client.bitcount(`dau:${today}`);
```

---

### 24. Pub/Sub vs Streams

**Pub/Sub** — fire-and-forget. No persistence, no acknowledgement. Subscribers must be connected.

```javascript
// Publisher
const pub = new Redis();
await pub.publish("notifications", JSON.stringify({ userId: 123, message: "Order shipped" }));

// Subscriber
const sub = new Redis();
await sub.subscribe("notifications");
sub.on("message", (channel, message) => {
  const data = JSON.parse(message);
  sendPushNotification(data);
});
// If subscriber is offline, message is lost
```

**Streams** — persistent, ordered log with consumer groups. Messages survive subscriber downtime. Acknowledgement required.

```javascript
// Producer
await client.xadd("orders:stream", "*",
  "orderId", "ord_123",
  "userId", "usr_456",
  "total", "150.00"
);

// Consumer group — multiple consumers, each gets different messages
await client.xgroup("CREATE", "orders:stream", "processors", "$", "MKSTREAM");

// Worker process
async function processOrders() {
  while (true) {
    const messages = await client.xreadgroup(
      "GROUP", "processors", "worker-1",
      "COUNT", 10,
      "BLOCK", 5000,
      "STREAMS", "orders:stream", ">"  // ">" = new, undelivered messages
    );

    for (const [stream, entries] of messages ?? []) {
      for (const [id, fields] of entries) {
        const data = Object.fromEntries(
          fields.reduce((acc, v, i) => i % 2 === 0 ? [...acc, [v]] : [...acc.slice(0,-1), [...acc.at(-1), v]], [])
        );
        await processOrder(data);
        await client.xack("orders:stream", "processors", id); // acknowledge
      }
    }
  }
}

// Reclaim unacknowledged (crashed worker) messages
const pending = await client.xpending("orders:stream", "processors", "-", "+", 10);
// Claim messages idle > 30s
await client.xclaim("orders:stream", "processors", "worker-2", 30000, ...pendingIds);
```

**When to use which:**
- Pub/Sub: real-time notifications where loss is acceptable (chat typing indicators, live scores)
- Streams: job queues, event sourcing, audit logs, anything that needs durability or acknowledgement

---

### 25. Persistence: RDB vs AOF

| | RDB (Snapshot) | AOF (Append-Only File) |
|-|----------------|------------------------|
| How | Point-in-time snapshot | Log every write command |
| Recovery | Last snapshot (data loss possible) | Replays all commands |
| Performance | Fast (async fork) | Slight write overhead |
| File size | Small | Large (compact with BGREWRITEAOF) |
| Best for | Backups, disaster recovery | Durability guarantee |

```ini
# redis.conf

# RDB — save if N changes in M seconds
save 900 1     # save after 900s if at least 1 key changed
save 300 10
save 60 10000

# AOF
appendonly yes
appendfsync everysec   # fsync every second (good balance)
# appendfsync always   # fsync every write (slowest, most durable)
# appendfsync no       # OS decides (fastest, least durable)

# Use both for maximum durability
# Redis will use AOF for recovery if enabled (more up-to-date than RDB)
aof-use-rdb-preamble yes  # AOF starts with RDB snapshot then appends
```

---

### 26. Cluster vs Sentinel

**Redis Sentinel** — HA for a single shard. Monitors master/replicas, performs automatic failover, provides service discovery.

```
Sentinel 1
Sentinel 2  →  monitors →  Master ──replicates──► Replica 1
Sentinel 3                                       ► Replica 2

On master failure: sentinels vote, promote a replica, update clients
```

```javascript
// ioredis Sentinel client
const client = new Redis({
  sentinels: [
    { host: "sentinel1", port: 26379 },
    { host: "sentinel2", port: 26379 },
    { host: "sentinel3", port: 26379 },
  ],
  name: "mymaster",  // master name configured in sentinel.conf
});
```

**Redis Cluster** — horizontal sharding + HA. Data split across 16384 hash slots across N primary nodes, each with replicas.

```
Node A (slots 0–5460)      ──► Replica A
Node B (slots 5461–10922)  ──► Replica B
Node C (slots 10923–16383) ──► Replica C
```

```javascript
// ioredis Cluster client
const cluster = new Redis.Cluster([
  { host: "node1", port: 7001 },
  { host: "node2", port: 7002 },
  { host: "node3", port: 7003 },
], {
  redisOptions: { password: "secret" },
  scaleReads: "slave",  // read from replicas
});

// Multi-key ops must be on the same slot — use hash tags
await cluster.mset("{user:123}.name", "Alice", "{user:123}.email", "alice@example.com");
// {} hash tag ensures both keys go to the same slot
```

**Choose:**
- Sentinel: single shard up to ~100GB, you need HA but not horizontal scale
- Cluster: data > single node capacity, or need to scale writes

---

## Part 6 — Patterns & Production

---

### 27. N+1 Problem & Fixes

N+1: fetching a list of N items, then running 1 query per item to fetch related data = N+1 total queries.

```javascript
// ❌ N+1
const orders = await Order.findAll({ limit: 100 });
for (const order of orders) {
  order.user = await User.findByPk(order.userId); // 100 separate queries
}

// ✓ Fix 1: JOIN (SQL — single query)
const orders = await Order.findAll({
  include: [{ model: User }],  // Sequelize: generates LEFT JOIN
  limit: 100
});

// ✓ Fix 2: DataLoader (batches + deduplicates within a tick)
const userLoader = new DataLoader(async (userIds) => {
  const users = await User.findAll({ where: { id: userIds } });
  const userMap = Object.fromEntries(users.map(u => [u.id, u]));
  return userIds.map(id => userMap[id]);
});

// Per request: all .load() calls within the same tick are batched
const orders = await Order.findAll({ limit: 100 });
const usersPromises = orders.map(o => userLoader.load(o.userId));
const users = await Promise.all(usersPromises);  // 1 query total

// ✓ Fix 3: Raw SQL — fetch related in bulk
const orders = await db.query("SELECT * FROM orders LIMIT 100");
const userIds = [...new Set(orders.map(o => o.userId))];
const users = await db.query("SELECT * FROM users WHERE id = ANY($1)", [userIds]);
const userMap = Object.fromEntries(users.map(u => [u.id, u]));
orders.forEach(o => { o.user = userMap[o.userId]; });
```

**MongoDB N+1:**
```javascript
// ❌ N+1 in MongoDB
const posts = await Post.find({}).limit(100);
for (const post of posts) {
  post.author = await User.findById(post.authorId); // 100 queries
}

// ✓ Fix: $lookup in aggregation (single query)
const posts = await Post.aggregate([
  { $limit: 100 },
  { $lookup: {
    from: "users",
    localField: "authorId",
    foreignField: "_id",
    as: "author"
  }},
  { $unwind: "$author" }
]);

// ✓ Or: batch fetch
const posts = await Post.find({}).limit(100);
const authorIds = [...new Set(posts.map(p => p.authorId.toString()))];
const authors = await User.find({ _id: { $in: authorIds } });
const authorMap = Object.fromEntries(authors.map(a => [a._id.toString(), a]));
posts.forEach(p => { p.author = authorMap[p.authorId.toString()]; });
```

---

### 28. Database Migrations (Expand/Contract)

Running migrations on live databases without downtime requires the **expand/contract pattern** — never break the current version while deploying the next.

**Anti-pattern:** rename a column in one step → old code breaks.

**Expand/Contract:**

```
Phase 1 — Expand (backward compatible):
  Add new column alongside old one
  Deploy app that writes to BOTH columns

Phase 2 — Migrate data:
  Backfill new column from old column
  (run in batches to avoid locking)

Phase 3 — Contract (after old version fully gone):
  Deploy app that reads from new column only
  Drop old column
```

```sql
-- Phase 1: Add column (non-breaking)
ALTER TABLE users ADD COLUMN full_name TEXT;

-- Trigger to keep both in sync during transition
CREATE OR REPLACE FUNCTION sync_name_columns()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.full_name IS NULL THEN
    NEW.full_name := NEW.first_name || ' ' || NEW.last_name;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_names BEFORE INSERT OR UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION sync_name_columns();
```

```javascript
// Phase 2: Backfill in batches (never lock the table)
async function backfill() {
  let lastId = 0;
  while (true) {
    const updated = await db.query(`
      UPDATE users
      SET full_name = first_name || ' ' || last_name
      WHERE id > $1 AND full_name IS NULL
      ORDER BY id
      LIMIT 1000
      RETURNING id
    `, [lastId]);

    if (updated.rows.length === 0) break;
    lastId = updated.rows.at(-1).id;
    await new Promise(r => setTimeout(r, 100)); // brief pause between batches
  }
}
```

```sql
-- Phase 3: After old app version is gone, drop old columns
ALTER TABLE users DROP COLUMN first_name;
ALTER TABLE users DROP COLUMN last_name;
DROP TRIGGER sync_names ON users;
```

**Other safe migration rules:**
- ✓ Add column with DEFAULT (Postgres 11+: instant, no table rewrite)
- ✓ Add nullable column without default
- ✓ Create index `CONCURRENTLY` (no lock)
- ✗ `ALTER COLUMN TYPE` — table rewrite, long lock
- ✗ Add `NOT NULL` without default on existing table — table scan
- ✗ Drop column — safe but verify no code references it

---

### 29. Sharding Strategies

Sharding (horizontal partitioning) distributes data across multiple DB nodes. Each node owns a subset of the data.

**Shard key selection** — the most important decision. A bad shard key causes hot spots.

| Strategy | How | Pros | Cons |
|----------|-----|------|------|
| Range | Shard by value range (e.g., userId 1–1M on shard 1) | Range queries on shard key efficient | Hot spots if writes concentrate on one range |
| Hash | `hash(shardKey) % numShards` | Even distribution | Range queries require scatter-gather |
| Directory | Lookup table maps key to shard | Flexible | Lookup table is a bottleneck/SPOF |
| Geo | Shard by geography | Data locality, compliance | Uneven if some regions larger |

```javascript
// MongoDB sharding
use admin
db.adminCommand({ enableSharding: "mydb" });

// Hash sharding — even distribution, good for high-cardinality IDs
db.adminCommand({
  shardCollection: "mydb.orders",
  key: { userId: "hashed" }
});

// Range sharding — good if queries always filter by date range
db.adminCommand({
  shardCollection: "mydb.events",
  key: { createdAt: 1 }
  // Downside: all new writes go to the "max" chunk = hot spot
  // Fix: pre-split chunks or use compound shard key
});

// Compound shard key — avoid hot spots on time-series data
db.adminCommand({
  shardCollection: "mydb.events",
  key: { tenantId: 1, createdAt: 1 }  // distribute by tenant first
});
```

**Application-level sharding (when not using MongoDB/Vitess):**

```javascript
function getShard(userId) {
  return `db_${parseInt(userId, 36) % NUM_SHARDS}`;
}

async function getOrder(orderId, userId) {
  const shard = getShard(userId);
  const db = connections[shard];
  return db.query("SELECT * FROM orders WHERE id = $1", [orderId]);
}

// Cross-shard queries (expensive — scatter-gather)
async function getAllUserOrders(userId) {
  // userId is the shard key — only one shard needed
  const shard = getShard(userId);
  return connections[shard].query("SELECT * FROM orders WHERE user_id = $1", [userId]);
}

async function getOrdersByDate(date) {
  // date is not the shard key — must query all shards
  const results = await Promise.all(
    Object.values(connections).map(db =>
      db.query("SELECT * FROM orders WHERE created_at::date = $1", [date])
    )
  );
  return results.flat().sort((a, b) => a.created_at - b.created_at);
}
```

---

### 30. CQRS & Read Replicas

**CQRS (Command Query Responsibility Segregation)** — separate the read model from the write model. Commands mutate state, queries read a separate (possibly denormalized) read model.

```
Write path:  Client → API → Command Handler → Primary DB
                                              ↓ (replication / events)
Read path:   Client → API → Query Handler  → Read Replica / Read Model
```

**Read Replicas** — the simplest form of CQRS. Route reads to replicas, writes to primary.

```javascript
// PostgreSQL with two pools
const writePool = new Pool({ host: "primary.db.internal", max: 20 });
const readPool  = new Pool({ host: "replica.db.internal", max: 50 });

class OrderRepository {
  async create(order) {
    return writePool.query(
      "INSERT INTO orders (user_id, total) VALUES ($1, $2) RETURNING *",
      [order.userId, order.total]
    );
  }

  async findByUser(userId) {
    // Read from replica — may be slightly stale (replication lag)
    return readPool.query(
      "SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC",
      [userId]
    );
  }

  async findById(id) {
    // Read-your-writes: use primary for immediately-after-write reads
    return writePool.query("SELECT * FROM orders WHERE id = $1", [id]);
  }
}
```

**Full CQRS with event-driven read model:**

```javascript
// Write side: normalized, consistent
class OrderCommandHandler {
  async placeOrder(cmd) {
    const order = await db.transaction(async (trx) => {
      const order = await trx("orders").insert(cmd).returning("*");
      await trx("order_items").insert(cmd.items.map(i => ({ ...i, orderId: order.id })));
      return order;
    });

    // Publish event
    await eventBus.publish("order.placed", order);
    return order;
  }
}

// Read side: denormalized, optimized for queries
eventBus.subscribe("order.placed", async (order) => {
  // Build/update a denormalized read model (could be Redis, Elasticsearch, etc.)
  await readDb.upsert("order_summaries", {
    id: order.id,
    userId: order.userId,
    userName: order.user.name,     // denormalized
    itemCount: order.items.length, // pre-aggregated
    total: order.total,
    createdAt: order.createdAt
  });
});

// Query side: fast, no joins
class OrderQueryHandler {
  async getOrderSummaries(userId) {
    return readDb.find("order_summaries", { userId }); // no joins, pre-computed
  }
}
```

**Trade-offs:**
- Eventual consistency between write and read models (usually milliseconds, acceptable for most UIs)
- More infrastructure complexity
- Read model can be rebuilt from event log if it gets out of sync

---

## Part 1 (continued): Relational Fundamentals

---

### 31. Deadlocks

A deadlock occurs when two transactions each hold a lock the other needs — neither can proceed. PostgreSQL detects and resolves them automatically (one transaction is killed), but they indicate a schema or application design problem.

```sql
-- Classic deadlock scenario
-- Session A: locks row 1, then tries to lock row 2
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- acquires lock on row 1
-- (pauses here while Session B runs)
UPDATE accounts SET balance = balance + 100 WHERE id = 2;  -- blocks: Session B holds row 2

-- Session B: locks row 2, then tries to lock row 1
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 2;  -- acquires lock on row 2
UPDATE accounts SET balance = balance + 100 WHERE id = 1;  -- deadlock: waits for Session A

-- PostgreSQL detects after deadlock_timeout (default 1s) and kills one:
-- ERROR: deadlock detected
-- DETAIL: Process 12345 waits for ShareLock on transaction 789; blocked by process 67890.
-- The killed transaction must be retried by the application.
```

**Detection:**

```sql
-- Queries currently waiting for a lock
SELECT pid, wait_event_type, wait_event, state, query,
       now() - query_start AS duration
FROM pg_stat_activity
WHERE wait_event IS NOT NULL AND state != 'idle';

-- What's blocking what (blocker → blocked relationship)
SELECT
  blocking.pid   AS blocking_pid,
  blocking.query AS blocking_query,
  blocked.pid    AS blocked_pid,
  blocked.query  AS blocked_query
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking
  ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
WHERE cardinality(pg_blocking_pids(blocked.pid)) > 0;

-- Relevant settings
SHOW deadlock_timeout;  -- default 1s — how long before deadlock detection runs
SHOW lock_timeout;      -- 0 = wait forever (set per transaction to avoid hung queries)
```

**Prevention — always acquire locks in consistent order:**

```javascript
// ❌ Can deadlock: A locks (1,2), B locks (2,1)
async function transfer(fromId, toId, amount) {
  await db.query('UPDATE accounts SET balance = balance - $1 WHERE id = $2', [amount, fromId]);
  await db.query('UPDATE accounts SET balance = balance + $1 WHERE id = $2', [amount, toId]);
}

// ✓ Sort IDs before locking — consistent order prevents deadlock
async function transfer(fromId, toId, amount, db) {
  const [first, second] = [fromId, toId].sort((a, b) => a - b);
  await db.transaction(async (trx) => {
    // Lock both rows in a consistent order before mutating
    await trx.raw('SELECT 1 FROM accounts WHERE id = ANY(?) FOR UPDATE', [[first, second]]);
    await trx.raw('UPDATE accounts SET balance = balance - ? WHERE id = ?', [amount, fromId]);
    await trx.raw('UPDATE accounts SET balance = balance + ? WHERE id = ?', [amount, toId]);
  });
}
```

**Fail-fast alternatives:**

```sql
-- NOWAIT: error immediately if lock unavailable (don't queue)
SELECT * FROM jobs WHERE id = 1 FOR UPDATE NOWAIT;
-- ERROR: could not obtain lock on row in relation "jobs"

-- SKIP LOCKED: skip rows held by other transactions (worker queue pattern)
SELECT * FROM jobs WHERE status = 'pending' LIMIT 1 FOR UPDATE SKIP LOCKED;

-- Per-transaction lock timeout
BEGIN;
SET LOCAL lock_timeout = '5s';  -- error if waiting > 5s for any lock
UPDATE ...;
COMMIT;
```

**Best practices summary:**
- Keep transactions short — the shorter the lock hold time, the less contention
- Access tables in the same order across all code paths
- Use `SKIP LOCKED` for queue-style processing
- Set `lock_timeout` in application transactions to avoid indefinite hangs
- Log and alert on deadlock errors; retry at the application layer

---

### 32. Optimistic vs Pessimistic Locking

Two strategies for handling concurrent updates to the same row.

**Pessimistic locking** — acquire the lock before reading; assume conflicts are common.

```sql
-- SELECT FOR UPDATE: lock the row until transaction ends
BEGIN;
SELECT * FROM inventory WHERE product_id = 42 FOR UPDATE;
-- other sessions attempting FOR UPDATE on this row will block until COMMIT/ROLLBACK
UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 42;
COMMIT;

-- FOR SHARE: allows concurrent reads, blocks writes
SELECT * FROM products WHERE id = 42 FOR SHARE;

-- FOR NO KEY UPDATE: lighter lock, doesn't block foreign key checks
SELECT * FROM orders WHERE id = $1 FOR NO KEY UPDATE;
```

```javascript
// Node.js — pessimistic lock with Knex
const result = await db.transaction(async (trx) => {
  const [item] = await trx('inventory')
    .where('product_id', productId)
    .forUpdate()
    .select();

  if (item.quantity < requestedQty) throw new Error('Out of stock');

  await trx('inventory')
    .where('product_id', productId)
    .decrement('quantity', requestedQty);

  return item;
});
```

**Optimistic locking** — don't lock at read time; detect conflicts at write time via a version column.

```sql
-- Add version column
ALTER TABLE inventory ADD COLUMN version INT NOT NULL DEFAULT 0;

-- Read row — remember version
SELECT quantity, version FROM inventory WHERE product_id = 42;
-- returns: quantity=10, version=5

-- Write: only update if version hasn't changed since we read
UPDATE inventory
SET quantity = quantity - 1, version = version + 1
WHERE product_id = 42 AND version = 5;
-- rowsAffected = 0 means another transaction updated first → retry
```

```javascript
async function decrementInventory(productId, qty, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const { rows: [item] } = await db.query(
      'SELECT quantity, version FROM inventory WHERE product_id = $1', [productId]
    );

    if (item.quantity < qty) throw new Error('Out of stock');

    const { rowCount } = await db.query(
      `UPDATE inventory
       SET quantity = quantity - $1, version = version + 1
       WHERE product_id = $2 AND version = $3`,
      [qty, productId, item.version]
    );

    if (rowCount === 1) return;  // success
    // rowCount === 0: conflict — another transaction won the race, retry
    await new Promise(r => setTimeout(r, 10 * (attempt + 1)));
  }
  throw new Error('Optimistic lock conflict — max retries exceeded');
}
```

**Comparison:**

| | Pessimistic | Optimistic |
|--|-------------|------------|
| Lock acquired | At read time | At write time (version check) |
| Blocking | Yes — other writers queue | No — all reads proceed freely |
| Throughput | Lower under contention | Higher under low contention |
| Conflict handling | Prevention | Detection + retry |
| Best for | High contention, short transactions | Low contention, long checkout flows |
| DB support | Native (`FOR UPDATE`) | Version column in schema |

**Mongoose / ORM:**

```javascript
// Sequelize: built-in optimistic locking via version field
const Product = sequelize.define('Product', {
  quantity: DataTypes.INTEGER,
  version: { type: DataTypes.INTEGER, defaultValue: 0 }
}, { version: true });  // auto-increments version, throws OptimisticLockError on conflict

// Mongoose: __v field is automatic, throw VersionError on conflict
const doc = await Product.findById(id);
doc.quantity -= 1;
await doc.save();  // includes version check internally
```

---

### 33. Data Types & Their Impact

Choosing the right type affects storage size, index performance, query correctness, and schema portability.

**Integer types:**

```sql
SMALLINT  -- 2 bytes, –32,768 to 32,767        (status codes, lookup table IDs)
INT       -- 4 bytes, ±2.1 billion              (general-purpose IDs, counters)
BIGINT    -- 8 bytes, ±9.2 × 10¹⁸              (high-volume tables: events, logs, orders)

-- Modern auto-increment syntax (prefer over SERIAL)
CREATE TABLE users (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
);

-- When does INT overflow?
-- ~2.1B rows. Use BIGINT for high-write tables as a precaution.
-- Changing INT → BIGINT on a live table with 500M rows requires a full rewrite.
```

**String types:**

```sql
TEXT        -- variable length, no limit. Preferred in PostgreSQL.
VARCHAR(n)  -- variable length, max n chars. No performance benefit over TEXT in PG.
CHAR(n)     -- fixed length, padded with spaces. Almost never correct.

-- VARCHAR(255) is a MySQL habit. In PostgreSQL, use TEXT.
-- If you need a length limit, use a CHECK constraint (more flexible):
ALTER TABLE users ADD CONSTRAINT chk_name_len CHECK (char_length(name) <= 255);
```

**Numeric types:**

```sql
-- NUMERIC / DECIMAL — exact arithmetic. Use for money, tax, anything rounding-sensitive.
price NUMERIC(10, 2)  -- up to 10 total digits, 2 decimal places

-- FLOAT / DOUBLE PRECISION — IEEE 754 approximation.
-- Use for scientific measurements, ML scores, geospatial — never for money.

SELECT 0.1::float + 0.2::float;    -- 0.30000000000000004  ← float trap
SELECT 0.1::numeric + 0.2::numeric; -- 0.3                 ← exact
```

**Timestamps:**

```sql
TIMESTAMP    -- no timezone info; stored as-is. Ambiguous across timezones.
TIMESTAMPTZ  -- stored as UTC internally, displayed in session timezone. Always use this.

SET timezone = 'Africa/Cairo';
SELECT '2024-01-15 12:00:00+00'::timestamptz;
-- Returns: 2024-01-15 14:00:00+02  (Cairo = UTC+2)

-- created_at TIMESTAMP is a common bug. Always:
created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

**UUID:**

```sql
-- UUID vs BIGINT for primary keys
-- UUID: globally unique, safe to generate client-side, hard to enumerate
-- Cost: 16 bytes vs 8, random UUIDv4 fragments B-tree indexes at scale

-- UUIDv4: fully random — index fragmentation on high-write tables
-- UUIDv7: time-sorted — sequential like BIGINT, globally unique like UUID

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
SELECT gen_random_uuid();  -- UUIDv4 (PG core)

-- UUIDv7 via pg_uuidv7 extension or PostgreSQL 17 native support
-- Prefer UUIDv7 or ULIDs for primary keys on high-volume tables
```

**JSON types:**

```sql
JSON   -- stores raw text; preserves key order and whitespace. Use for write-once audit logs.
JSONB  -- binary, deduplicates keys, supports GIN indexing. Use for everything else.
```

**Summary:**

| Use case | Recommended type |
|----------|-----------------|
| Primary key (high volume) | `BIGINT GENERATED ALWAYS AS IDENTITY` or UUIDv7 |
| General strings | `TEXT` (with CHECK if length limit needed) |
| Money / exact decimals | `NUMERIC(precision, scale)` — never FLOAT |
| Timestamps | `TIMESTAMPTZ` always |
| Flags | `BOOLEAN` |
| Schema-flexible data | `JSONB` |
| Enumerations | PostgreSQL `ENUM` type or `TEXT` with CHECK constraint |

---

## Part 2 (continued): PostgreSQL Deep Dive

---

### 34. Stored Procedures, Functions & Triggers

**Functions** — return a value, callable in SQL expressions. Can be SQL, PL/pgSQL, or other languages.

```sql
-- Immutable SQL function (can be used in indexes)
CREATE OR REPLACE FUNCTION full_name(first_name TEXT, last_name TEXT)
RETURNS TEXT LANGUAGE sql IMMUTABLE AS $$
  SELECT first_name || ' ' || last_name;
$$;

SELECT full_name('Hassan', 'Harga');
CREATE INDEX idx_users_full_name ON users(full_name(first_name, last_name));

-- PL/pgSQL function with logic
CREATE OR REPLACE FUNCTION calculate_discount(total NUMERIC, user_tier TEXT)
RETURNS NUMERIC LANGUAGE plpgsql IMMUTABLE AS $$
BEGIN
  RETURN CASE user_tier
    WHEN 'premium'  THEN total * 0.90
    WHEN 'standard' THEN total * 0.95
    ELSE total
  END;
END;
$$;

-- Set-returning function (returns table)
CREATE OR REPLACE FUNCTION get_user_orders(p_user_id INT)
RETURNS TABLE(order_id INT, total NUMERIC, created_at TIMESTAMPTZ)
LANGUAGE sql STABLE AS $$
  SELECT id, total, created_at FROM orders WHERE user_id = p_user_id;
$$;

SELECT * FROM get_user_orders(123);
```

**Stored Procedures** (PostgreSQL 11+) — like functions but support `COMMIT`/`ROLLBACK` inside the body.

```sql
CREATE OR REPLACE PROCEDURE process_pending_orders(batch_size INT DEFAULT 1000)
LANGUAGE plpgsql AS $$
DECLARE
  processed INT;
BEGIN
  LOOP
    UPDATE orders SET status = 'processing'
    WHERE id IN (
      SELECT id FROM orders WHERE status = 'pending'
      LIMIT batch_size FOR UPDATE SKIP LOCKED
    );

    GET DIAGNOSTICS processed = ROW_COUNT;
    EXIT WHEN processed = 0;

    COMMIT;  -- commit each batch to avoid a long-running transaction
    PERFORM pg_sleep(0.01);
  END LOOP;
END;
$$;

CALL process_pending_orders(500);
```

**Triggers** — execute automatically on INSERT / UPDATE / DELETE.

```sql
-- Audit log trigger
CREATE TABLE audit_log (
  id         BIGSERIAL PRIMARY KEY,
  table_name TEXT,
  operation  TEXT,           -- INSERT, UPDATE, DELETE
  old_data   JSONB,
  new_data   JSONB,
  changed_at TIMESTAMPTZ DEFAULT NOW(),
  changed_by TEXT DEFAULT current_user
);

CREATE OR REPLACE FUNCTION audit_trigger_fn()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO audit_log (table_name, operation, old_data, new_data)
  VALUES (
    TG_TABLE_NAME,
    TG_OP,
    CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE to_jsonb(OLD) END,
    CASE WHEN TG_OP = 'DELETE' THEN NULL ELSE to_jsonb(NEW) END
  );
  RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER audit_orders
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION audit_trigger_fn();

-- Derived column trigger (keep denormalized field in sync)
CREATE OR REPLACE FUNCTION sync_full_name()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.full_name := NEW.first_name || ' ' || NEW.last_name;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_sync_full_name
BEFORE INSERT OR UPDATE OF first_name, last_name ON users
FOR EACH ROW EXECUTE FUNCTION sync_full_name();
```

**DB logic vs application logic — when to choose which:**

| Use the database | Use the application |
|-----------------|---------------------|
| Audit logging (guaranteed even from psql/migrations) | Business logic that changes frequently |
| Derived columns that must stay in sync | Logic requiring external API calls |
| Cross-table constraints CHECK can't express | Multi-step workflows with compensating actions |
| Performance-critical data-local operations | Anything you want to unit test in isolation |

**Pitfalls:**
- Triggers are invisible when reading application code — they cause confusion when debugging unexpected behavior
- Stored procedure logic is harder to version-control, test, and deploy than application code
- Heavy business logic in the DB couples your stack to PostgreSQL specifically
- Sweet spot for triggers: audit logging and derived columns only

---

### 35. Views vs Materialized Views

**Views** — virtual tables; the underlying query re-executes on every access.

```sql
-- Simple view (security/column filtering)
CREATE VIEW active_users AS
  SELECT id, name, email, created_at
  FROM users
  WHERE active = true;

SELECT * FROM active_users WHERE email LIKE '%@example.com';
-- Expands to: SELECT ... FROM users WHERE active = true AND email LIKE '%@example.com'

-- WITH CHECK OPTION: prevents inserting rows that wouldn't appear in the view
CREATE VIEW active_users WITH CHECK OPTION AS
  SELECT * FROM users WHERE active = true;

INSERT INTO active_users (name, email, active) VALUES ('Alice', 'a@b.com', false);
-- ERROR: new row violates check option for view "active_users"

-- NOT MATERIALIZED hint (PG12+): allow planner to inline the CTE/view
WITH active AS NOT MATERIALIZED (SELECT * FROM users WHERE active = true)
SELECT * FROM active WHERE email LIKE '%@example.com';
```

**Materialized Views** — query result stored on disk; must be refreshed explicitly.

```sql
-- Create with pre-computed data
CREATE MATERIALIZED VIEW monthly_revenue AS
  SELECT
    DATE_TRUNC('month', created_at) AS month,
    SUM(total)                       AS revenue,
    COUNT(*)                         AS order_count
  FROM orders
  WHERE status = 'completed'
  GROUP BY 1
WITH DATA;

-- Indexes are possible (unlike regular views)
CREATE UNIQUE INDEX idx_monthly_revenue_month ON monthly_revenue(month);

-- Query: reads pre-computed rows — instant
SELECT * FROM monthly_revenue WHERE month >= '2024-01-01' ORDER BY month;

-- Refresh (blocks reads during refresh)
REFRESH MATERIALIZED VIEW monthly_revenue;

-- Non-blocking refresh (requires unique index on the MV)
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
-- Reads continue; new snapshot swapped in atomically at the end

-- Automate with pg_cron
SELECT cron.schedule('0 * * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue');
```

**Decision guide:**

| | View | Materialized View |
|-|------|-------------------|
| Data freshness | Always current | Stale until refreshed |
| Query speed | Depends on base query cost | Fast (pre-computed) |
| Storage | None | Disk space required |
| Index support | Via base table only | Own indexes possible |
| Best for | Security filtering, simple queries | Expensive aggregations, dashboards |

**Tip:** run `EXPLAIN` on the view query — if it scans large tables or does complex joins, materialize it. If it's cheap and freshness matters, keep it as a view.

---

### 36. Database Backup & Recovery

**pg_dump** — logical backup of a single database (schema + data as SQL or binary).

```bash
# Custom format (compressed, supports parallel restore)
pg_dump -h localhost -U postgres -d mydb -Fc -f mydb.dump

# Parallel dump using directory format (-j = number of CPU cores)
pg_dump -h localhost -U postgres -d mydb -Fd -j 4 -f mydb_dir/

# Restore (parallel -j speeds up large restores significantly)
pg_restore -h localhost -U postgres -d mydb -Fc -j 4 mydb.dump

# Dump all databases + global objects (roles, tablespaces)
pg_dumpall -h localhost -U postgres -f all_databases.sql

# Exclude large noisy tables
pg_dump -d mydb --exclude-table=audit_log -Fc -f mydb_no_audit.dump
```

**Continuous Archiving + Point-in-Time Recovery (PITR)**

Take a base backup, then archive WAL files. Recover to any second within the WAL stream.

```ini
# postgresql.conf — enable WAL archiving
wal_level = replica
archive_mode = on
archive_command = 'aws s3 cp %p s3://my-wal-archive/%f'
# %p = full path to WAL file, %f = filename only
```

```bash
# Base backup (needed as the starting point for PITR)
pg_basebackup -h localhost -U replicator -D /var/backups/base -Ft -z -Xs -P
# -Ft: tar format, -z: compress, -Xs: include WAL, -P: progress
```

```ini
# Restore to a specific point in time:
# 1. Restore base backup to target directory
# 2. Set in postgresql.conf (PG12+):
restore_command = 'aws s3 cp s3://my-wal-archive/%f %p'
recovery_target_time = '2024-06-01 14:30:00 UTC'
recovery_target_action = 'promote'  # or 'pause' to inspect before promoting
```

**pgBackRest** — production-grade backup tool (incremental, S3-native, parallel).

```ini
# /etc/pgbackrest/pgbackrest.conf
[global]
repo1-type=s3
repo1-s3-bucket=my-pg-backups
repo1-s3-region=us-east-1
repo1-path=/pgbackrest
repo1-retention-full=2      # keep 2 full backups
repo1-retention-diff=7      # keep 7 differential backups

[mydb]
pg1-path=/var/lib/postgresql/data
pg1-port=5432
```

```bash
pgbackrest --stanza=mydb backup --type=full   # weekly full
pgbackrest --stanza=mydb backup --type=diff   # daily differential
pgbackrest --stanza=mydb backup --type=incr   # hourly incremental
pgbackrest --stanza=mydb restore              # restore latest
pgbackrest --stanza=mydb restore --target="2024-06-01 14:30:00"  # PITR
```

**Production backup strategy:**

```
Continuous: WAL archiving → S3 (RPO = seconds)
Daily:      Full backup via pgBackRest → S3 (retained 2 weeks)
Weekly:     Restore test — actually restore to a staging server and verify data integrity

RTO (Recovery Time Objective): 15–60 min depending on DB size and restore parallelism
RPO (Recovery Point Objective): seconds (continuous WAL archiving)
```

---

## Part 4 (continued): MongoDB

---

### 37. Managed Databases (Atlas & RDS)

**Self-hosted vs managed:**

| | Self-Hosted | Managed (Atlas / RDS) |
|--|-------------|----------------------|
| Cost | Cheaper at scale | Higher but predictable |
| Ops burden | Full DBA responsibility | Backups, patching, HA automated |
| Customization | Full control (extensions, config, superuser) | Limited — no superuser, some extensions blocked |
| Compliance | You own it | SOC2 / PCI / HIPAA usually covered |
| Best for | Large teams, cost optimization, custom requirements | Startups, teams without dedicated DBA |

**MongoDB Atlas:**

```javascript
// Atlas connection string — SRV format handles host discovery automatically
const client = new MongoClient(
  'mongodb+srv://user:pass@cluster0.abc.mongodb.net/mydb?retryWrites=true&w=majority'
);

// Atlas Search (Lucene-based — richer than MongoDB $text)
db.products.aggregate([
  { $search: {
    index: 'default',
    text: { query: 'wireless headphones', path: ['name', 'description'] },
    highlight: { path: 'description' }
  }},
  { $limit: 10 },
  { $project: { name: 1, price: 1, highlights: { $meta: 'searchHighlights' } } }
]);

// Atlas Vector Search (semantic search / RAG)
db.embeddings.aggregate([
  { $vectorSearch: {
    index: 'vector_index',
    path: 'embedding',
    queryVector: [0.1, 0.2, /* ... */],
    numCandidates: 100,
    limit: 10
  }}
]);
```

**AWS RDS / Aurora PostgreSQL:**

```
RDS PostgreSQL:    Managed PG, multi-AZ HA, automated backups up to 35 days PITR
Aurora PostgreSQL: Distributed storage layer, 5× throughput vs standard RDS PG
Aurora Serverless v2: Scales 0.5 → 128 ACUs in seconds, pay-per-ACU-second
RDS Proxy:         Managed connection pooling (like PgBouncer), integrates with IAM auth

Common managed DB limits:
  - No superuser — use rds_superuser role instead
  - Extension whitelist — enable via parameter group (rds.force_ssl, etc.)
  - Can't modify kernel params — shared_buffers determined by instance class
  - No custom pg_hba.conf — use security groups + SSL enforcement
```

```javascript
// RDS IAM authentication — no password in config, uses temporary tokens
import { Signer } from '@aws-sdk/rds-signer';

const signer = new Signer({
  region: 'us-east-1',
  hostname: 'mydb.abc123.us-east-1.rds.amazonaws.com',
  port: 5432,
  username: 'myapp',
});

const token = await signer.getAuthToken();  // valid 15 minutes
const pool = new Pool({
  host: 'mydb.abc123.us-east-1.rds.amazonaws.com',
  user: 'myapp',
  password: token,
  ssl: { rejectUnauthorized: true, ca: fs.readFileSync('rds-ca-2019-root.pem') },
});
```

---

## Part 6 (continued): Patterns & Production

---

### 38. Database Connection Lifecycle

Understanding what happens at connection time explains why connection pooling matters.

**What happens when a client connects to PostgreSQL:**

```
1. TCP 3-way handshake (SYN → SYN-ACK → ACK)           ~0.1–1ms LAN
2. Startup message (protocol version, database, username)
3. Authentication challenge/response (SCRAM-SHA-256)
4. PostgreSQL forks a backend OS process (~5MB RAM)
5. TLS handshake (if SSL enabled)
6. Session state initialized (search_path, timezone, application_name)
7. Connection ready — idle, consuming RAM, waiting for queries
```

PostgreSQL uses **one OS process per connection**, not threads:

```
 100 connections  →   500MB RAM (process overhead alone)
1000 connections  → 5,000MB RAM
+ each backend has its own: local buffer cache, lock table, background overhead
```

**The cost of connecting per request:**

```javascript
// ❌ New connection per query — catastrophic at any real traffic level
app.get('/users/:id', async (req, res) => {
  const client = new Client({ host: 'db', database: 'mydb' });
  await client.connect();  // TCP + auth + fork = 5–50ms + 5MB RAM
  const { rows } = await client.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
  await client.end();
  res.json(rows[0]);
});

// ✓ Pool created once at app startup — connections reused
const pool = new Pool({ host: 'db', database: 'mydb', max: 20 });

app.get('/users/:id', async (req, res) => {
  // acquire idle connection (<1ms) → query → return to pool
  const { rows } = await pool.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
  res.json(rows[0]);
});
```

**Connection lifecycle in a pool:**

```
App startup    → pool creates idleTimeoutMillis connections (warm-up optional)
Request arrives → borrow idle connection (<1ms)
Query executes  → connection returned to pool (even on error, if using pool.query)
Idle connection → closed after idleTimeoutMillis (default 10s in node-postgres)
Pool exhausted  → request waits in queue up to connectionTimeoutMillis
Queue full      → Error: timeout exceeded when trying to connect
```

**Sizing the pool:**

```
Rule of thumb: connections_per_instance = total_db_connections / num_app_instances

Example:
  PostgreSQL max_connections = 200
  PgBouncer default_pool_size = 25  (PgBouncer → Postgres)
  5 app instances, each → PgBouncer
  Per-instance pool max: 25 / 5 = 5  (but app can have 100+ logical connections to PgBouncer)

For CPU-bound PG workloads: num_cores × 2 is a common starting point for total DB connections
For I/O-bound: can go higher — experiment with pg_stat_activity to find saturation point
```

**Session state pitfalls with pooling:**

```sql
-- Session state persists between queries on the same connection
SET search_path = myschema;   -- sticks until session ends
SET timezone = 'US/Eastern';
PREPARE my_stmt AS SELECT * FROM users WHERE id = $1;  -- scoped to session

-- In PgBouncer transaction mode: session state is LOST between transactions
-- Safe pattern: use SET LOCAL (scoped to current transaction only)
BEGIN;
SET LOCAL search_path = myschema;  -- resets at COMMIT/ROLLBACK
SELECT * FROM users;
COMMIT;
```

---

### 39. Soft Delete Patterns

Soft delete marks records as deleted without physically removing them, preserving history and allowing recovery.

```sql
-- Basic pattern: nullable deleted_at timestamp
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMPTZ;

-- "Delete" a user
UPDATE users SET deleted_at = NOW() WHERE id = 123;

-- Every query must filter
SELECT * FROM users WHERE deleted_at IS NULL;
-- Problem: forgetting this filter leaks deleted records
```

**Enforcing the filter — three approaches:**

```sql
-- Option 1: Partial index (index only active rows — smaller, faster)
CREATE INDEX idx_users_email_active ON users(email) WHERE deleted_at IS NULL;
-- Queries with WHERE deleted_at IS NULL use this index automatically

-- Option 2: View (force the filter via a layer)
CREATE VIEW active_users AS SELECT * FROM users WHERE deleted_at IS NULL;
-- App queries active_users for all normal operations

-- Option 3: Row Level Security (enforce at DB, transparent to ORM)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY hide_deleted ON users
  FOR SELECT USING (
    deleted_at IS NULL
    OR current_setting('app.include_deleted', true) = 'true'
  );

-- Admin override to see deleted records:
SET app.include_deleted = 'true';
SELECT * FROM users;
RESET app.include_deleted;
```

**Unique constraints with soft delete:**

```sql
-- Problem: UNIQUE on email blocks re-registration after soft delete
-- ❌ Regular unique index: alice@example.com can't be reused after deletion
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- ✓ Partial unique index: unique only among active records
CREATE UNIQUE INDEX idx_users_email_active
  ON users(email) WHERE deleted_at IS NULL;
-- Same email can appear in deleted rows; unique constraint only applies to active
```

**Foreign key and cascade implications:**

```sql
-- Option A: cascade soft delete via trigger
CREATE OR REPLACE FUNCTION cascade_soft_delete_orders()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL THEN
    UPDATE order_items SET deleted_at = NOW()
    WHERE order_id IN (SELECT id FROM orders WHERE user_id = NEW.id);
    UPDATE orders SET deleted_at = NOW() WHERE user_id = NEW.id;
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_cascade_soft_delete
AFTER UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION cascade_soft_delete_orders();

-- Option B: archive table (move deleted rows out of main table)
INSERT INTO users_deleted SELECT *, NOW() AS deleted_at FROM users WHERE id = 123;
DELETE FROM users WHERE id = 123;
-- Benefit: main table and its indexes stay lean
-- Cost: UNION queries needed to search across active + archived
```

**Trade-off summary:**

| Pattern | Pros | Cons |
|---------|------|------|
| `deleted_at` column | Simple, reversible | All queries need filter; table bloat over time |
| Partial index | Index stays small | Filter still required in queries |
| View | Single place to enforce filter | Complex queries may not use the view |
| Row Level Security | Transparent to application | PostgreSQL-specific; harder to test |
| Archive table | Main table stays lean | Cross-table queries for historical data |

---

## Part 7 — Search Engines

---

### 40. Elasticsearch & Full-Text Search at Scale

**When PostgreSQL FTS isn't enough:**

| | PostgreSQL FTS | Elasticsearch |
|--|----------------|---------------|
| Relevance ranking | Basic `ts_rank` | Advanced BM25, field boosting, custom scoring |
| Fuzzy matching | Limited | Built-in (edit distance, auto-complete) |
| Facets / aggregations | Expensive, requires query rewrite | Native, real-time |
| Synonyms | Requires custom dictionary | Configurable per analyzer |
| Horizontal scale | Vertical only | Sharding built in |
| Operational cost | Zero (same DB) | Separate cluster to manage |
| Data freshness | Synchronous | Near-real-time (~1s refresh interval) |

**Core concepts:**

```
Index      = like a table (collection of documents)
Document   = JSON object stored in an index
Shard      = horizontal partition of an index (default: 1 primary)
Replica    = copy of a shard (HA + read scaling)
Mapping    = schema (field types, analyzers) — analogous to CREATE TABLE
Analyzer   = tokenizer + token filters (lowercasing, stemming, synonyms)
```

**Indexing and searching:**

```javascript
import { Client } from '@elastic/elasticsearch';

const client = new Client({ node: 'http://localhost:9200' });

// Create index with custom mapping and analyzer
await client.indices.create({
  index: 'products',
  body: {
    settings: {
      analysis: {
        filter: {
          synonym_filter: { type: 'synonym', synonyms: ['laptop, notebook', 'phone, mobile'] }
        },
        analyzer: {
          product_analyzer: {
            type: 'custom',
            tokenizer: 'standard',
            filter: ['lowercase', 'asciifolding', 'synonym_filter']
          }
        }
      }
    },
    mappings: {
      properties: {
        name:        { type: 'text', analyzer: 'product_analyzer', boost: 3 },
        description: { type: 'text', analyzer: 'product_analyzer' },
        price:       { type: 'float' },
        category:    { type: 'keyword' },  // keyword = exact match, aggregations
        createdAt:   { type: 'date' }
      }
    }
  }
});

// Index a document
await client.index({
  index: 'products',
  id: 'prod_123',
  body: { name: 'Wireless Headphones', description: 'Noise cancelling...', price: 99.99, category: 'audio' }
});

// Search with bool query + facets
const result = await client.search({
  index: 'products',
  body: {
    query: {
      bool: {
        must: [
          { multi_match: {
            query: 'wireless headphones',
            fields: ['name^3', 'description'],  // name weighted 3×
            fuzziness: 'AUTO'                   // typo tolerance
          }}
        ],
        filter: [
          { range: { price: { lte: 200 } } },
          { term: { category: 'audio' } }
        ]
      }
    },
    aggs: {
      by_category:  { terms: { field: 'category', size: 10 } },
      price_ranges: { range: { field: 'price', ranges: [
        { to: 50 }, { from: 50, to: 100 }, { from: 100 }
      ]}}
    },
    highlight: {
      fields: { name: {}, description: { fragment_size: 150, number_of_fragments: 1 } }
    },
    from: 0, size: 20
  }
});
```

**Keeping Elasticsearch in sync with PostgreSQL:**

```javascript
// Pattern 1: Dual write — simple but risky (ES write can fail after DB commit)
async function createProduct(data) {
  const product = await db.query('INSERT INTO products ... RETURNING *');
  await esClient.index({ index: 'products', id: product.id, body: product.rows[0] });
  return product.rows[0];
}

// Pattern 2: Outbox — guaranteed delivery
await db.transaction(async (trx) => {
  const [product] = await trx('products').insert(data).returning('*');
  await trx('outbox').insert({ type: 'product.created', payload: product, processed: false });
  return product;
});

// Worker polls outbox → indexes to ES → marks processed
const pending = await db.query("SELECT * FROM outbox WHERE NOT processed LIMIT 100");
for (const event of pending.rows) {
  await esClient.index({ index: 'products', id: event.payload.id, body: event.payload });
  await db.query('UPDATE outbox SET processed = true WHERE id = $1', [event.id]);
}

// Pattern 3: CDC (production scale) — Debezium monitors PostgreSQL WAL → Kafka → ES connector
// Guaranteed at-least-once delivery, no application code changes
```

**Common interview questions:**

```
Q: Why not just use PostgreSQL FTS for everything?
A: PostgreSQL FTS is excellent for most applications. Use Elasticsearch when you need:
   complex relevance tuning (BM25, field boosting), real-time faceted navigation,
   fuzzy search / typo tolerance, or scale beyond what single-node PG handles for search.

Q: What's the main downside of Elasticsearch?
A: Near-real-time (not immediately consistent — ~1s delay), data duplication
   (PostgreSQL stays the source of truth), sync complexity, and operational overhead
   (JVM memory tuning, shard sizing, cluster management).

Q: How do you keep ES in sync with your primary DB?
A: CDC via Debezium → Kafka → Elasticsearch Sink Connector is the most robust.
   Outbox pattern for simpler setups. Avoid dual-write without compensation.
```
