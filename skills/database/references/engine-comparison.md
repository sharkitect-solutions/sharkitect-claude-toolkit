# Database Engine Comparison

## Full Decision Matrix

### PostgreSQL

**Architecture:** Process-per-connection with MVCC. Write-ahead logging (WAL) for durability. Shared buffer pool with OS page cache cooperation.

**Strengths:** Richest SQL dialect (CTEs, window functions, LATERAL joins, recursive queries). Extension ecosystem unmatched: PostGIS (spatial), pg_trgm (fuzzy text), timescaledb (time-series), pgvector (embeddings), pg_cron (scheduling). JSONB with GIN indexes gives you 80% of a document database within a relational engine. Partitioning (declarative since v10) handles multi-TB tables. Logical replication enables zero-downtime major version upgrades.

**Weaknesses:** Vacuum overhead for write-heavy workloads (autovacuum tuning is a skill in itself). No native multi-master replication (requires Patroni, Citus, or managed service). Connection overhead is higher than MySQL -- PgBouncer is nearly always needed in production.

**Best for:** Complex queries, data integrity requirements, geospatial, full-text search, mixed OLTP/OLAP, any workload where you are unsure what you will need next.

**Cost model:** Self-hosted on commodity hardware handles 10K+ TPS. Managed services (RDS, Cloud SQL, Supabase) add 30-50% cost premium but eliminate operational burden.

### MySQL (InnoDB)

**Architecture:** Thread-per-connection with InnoDB's clustered index storage. Data is stored in primary key order (clustered index), which means PK choice directly affects I/O patterns.

**Strengths:** Mature replication (async, semi-sync, group replication). ProxySQL and MySQL Router handle connection pooling and read/write splitting natively. Excellent tooling ecosystem (pt-online-schema-change, gh-ost for zero-downtime DDL). WordPress, Drupal, and most PHP frameworks assume MySQL.

**Weaknesses:** Weaker SQL dialect than Postgres (no LATERAL, limited CTE optimization, partial window function support pre-8.0). InnoDB's clustered index means secondary indexes carry the PK value (larger than Postgres heap TID). Online DDL has improved but still lags Postgres for complex operations.

**Best for:** Read-heavy web applications, WordPress/PHP ecosystems, when operational MySQL expertise already exists on the team.

### SQLite

**Architecture:** Embedded, serverless, single-file. WAL mode allows concurrent readers with a single writer. The entire database is one file -- deploy by copying a file.

**Strengths:** Zero configuration, zero administration, zero network overhead. Reads are faster than any client-server database because there is no serialization/deserialization or network round trip. Perfect for edge computing (Cloudflare D1, Turso/libSQL), mobile apps, desktop apps, and test fixtures.

**Weaknesses:** Single writer (WAL mode mitigates but does not eliminate). No built-in replication. Limited ALTER TABLE (cannot drop columns pre-3.35, cannot rename columns pre-3.25). No role-based access control.

**Scaling thresholds:** Comfortable up to 100 concurrent writers, 1TB database size, and 50K reads/second. Beyond these, consider Postgres or a distributed SQLite layer (Turso, LiteFS).

**Best for:** Embedded/edge/mobile, development/testing, low-traffic web apps, configuration stores, read-heavy workloads with infrequent writes.

### MongoDB

**Architecture:** Document-oriented with BSON storage. WiredTiger engine with document-level locking. Sharding via mongos router distributes data across shards by shard key.

**Strengths:** Schema flexibility (each document can have different fields). Aggregation pipeline is powerful for document transformations. Horizontal scaling via sharding is a first-class feature. Change streams provide real-time event notification.

**Weaknesses:** No cross-document transactions until 4.0 (and they add latency). No JOINs -- if your data is relational, you will either denormalize (consistency risk) or do application-side joins (performance risk). Shard key selection is irreversible and determines performance forever. Memory-mapped storage engine (pre-WiredTiger) was notorious for memory issues.

**Best for:** Content management with highly variable schemas, IoT event ingestion, catalog data where each product has different attributes, rapid prototyping when schema is genuinely unknown.

**Do NOT use for:** Financial transactions, anything requiring multi-collection consistency, data with many cross-references.

### Redis

**Architecture:** In-memory, single-threaded command execution with I/O multiplexing (io-threads in 6.0+). Data structures (strings, hashes, sorted sets, streams, HyperLogLog) are first-class citizens, not bolted on.

**Strengths:** Sub-millisecond latency for all operations. Rich data structures solve specific problems elegantly: sorted sets for leaderboards/rate limiting, streams for event logs, HyperLogLog for cardinality estimation at 0.81% error with 12KB memory. Pub/sub and Streams for messaging. Lua scripting for atomic multi-step operations.

**Weaknesses:** Dataset must fit in RAM (plus replication overhead). Persistence options (RDB snapshots, AOF) are best-effort -- not a primary data store for data you cannot regenerate. Single-threaded means one slow command blocks everything.

**Best for:** Caching, session storage, rate limiting, real-time leaderboards, pub/sub, job queues (with Streams or lists), ephemeral data with sub-ms latency requirements.

### DynamoDB

**Architecture:** Fully managed, distributed key-value/document store. Single-digit millisecond P99 at any scale. Provisioned or on-demand capacity modes. Single-table design pattern maximizes efficiency.

**Strengths:** Predictable latency regardless of dataset size. Zero operational overhead (no servers, no patching, no vacuum). Global tables for multi-region replication. DynamoDB Streams for event-driven processing. On-demand mode handles unpredictable traffic without capacity planning.

**Weaknesses:** Single-table design requires upfront access pattern modeling (you cannot ad-hoc query). No server-side JOINs. Scan operations are expensive and slow. 400KB item size limit. Provisioned mode requires capacity planning or auto-scaling configuration. Costs can surprise you at scale if access patterns are not optimized.

**Best for:** Serverless architectures (Lambda + DynamoDB), applications with known access patterns, session stores, user profiles, gaming leaderboards, any workload where predictable latency at scale matters more than query flexibility.

## Engine Selection Flowchart

```
Is the application embedded/edge/mobile?
  YES -> SQLite (or Turso for distributed edge)
  NO  -> Continue

Is sub-millisecond latency required for key lookups?
  YES -> Redis (cache/ephemeral) or DynamoDB (durable)
  NO  -> Continue

Are access patterns fully known and fixed?
  YES -> DynamoDB (if scale > 10K TPS or serverless architecture)
  NO  -> Continue

Is the data fundamentally document-shaped with variable schemas?
  YES -> MongoDB (if no cross-document transactions needed)
  NO  -> Continue

Does the team have MySQL expertise and a PHP/WordPress stack?
  YES -> MySQL
  NO  -> PostgreSQL (default for everything else)
```
