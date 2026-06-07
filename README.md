# Boilerplate

A personal developer toolkit with ready-to-use configurations for local infrastructure, AI assistants, and interview preparation materials.

## Contents

### Docker Compose (`docker-compose/`)

Ready-to-use Docker Compose files for spinning up local databases:

| File | Description |
|------|-------------|
| `mongo.yml` | MongoDB 8 standalone with health checks and persistent volume |
| `mongo-replica.yaml` | MongoDB 8 with a single-node replica set (`rs0`) — required for transactions |
| `postgres.yml` | PostgreSQL (latest) with env-var-based credentials |
| `redis.yml` | Redis 8.2 with custom config and health checks |

**Usage:**

```bash
# Start MongoDB
docker compose -f docker-compose/mongo.yml up -d

# Start MongoDB with replica set (needed for Mongoose transactions)
docker compose -f docker-compose/mongo-replica.yaml up -d

# Start PostgreSQL (requires DB_USER, DB_PASSWORD, DB_NAME env vars)
DB_USER=admin DB_PASSWORD=secret DB_NAME=mydb \
  docker compose -f docker-compose/postgres.yml up -d

# Start Redis
docker compose -f docker-compose/redis.yml up -d
```

### AI Configurations (`AI/`)

Configuration files for AI coding assistants:

- **`AI/claude/`** — Claude Code settings, custom agents, skills, and CLAUDE.md rules
- **`AI/agents/`** — OpenCode agent definitions and notifier config

Copy the relevant folder to your project to get consistent AI assistant behavior across projects.

### Interview Preparation (`interview-prepration/`)

Reference documents for technical interviews:

| File | Topics |
|------|--------|
| `DDD_HEXAGONAL_REFERENCE.md` | Domain-Driven Design + Hexagonal Architecture |
| `backend-interview.md` | General backend concepts, reliability patterns, senior PR review |
| `database-interview.md` | SQL, NoSQL, indexing, transactions |
| `frontend-interview.md` | Browser, CSS, performance |
| `javascript-typescript-interview.md` | JS/TS language internals |
| `nodejs-interview.md` | Node.js runtime, event loop, streams |
| `react-interview.md` | React patterns, hooks, rendering |
| `system-design.md` | System design interview framework, building blocks, worked examples |
| `golang.md` | Comprehensive Go learning reference — language, concurrency, stdlib, patterns |
