# Rate Limiting Patterns & Implementation

## Algorithm Comparison

| Algorithm | Mechanism | Memory | Burst Behavior | Best For |
|-----------|-----------|--------|----------------|----------|
| **Token Bucket** | Bucket holds N tokens, refills at fixed rate, each request consumes 1 | O(1) per client | Allows bursts up to capacity | General-purpose, user-facing APIs |
| **Sliding Window Log** | Stores timestamp of every request in sorted set, counts within window | O(N) per client | Exact enforcement, no boundary effects | Low-volume financial/compliance APIs |
| **Sliding Window Counter** | Weighted combination of current + previous fixed-window counters | O(1) per client | Approximate (0.003% error), smooth | High-throughput production systems (recommended default) |
| **Fixed Window** | Simple counter per time interval, resets at boundary | O(1) per client | 2x burst at window boundaries | Internal services, simple fallback |

**Token bucket pseudocode** (the most commonly implemented):
```
tokens = min(capacity, tokens + (now - last_refill) * refill_rate)
last_refill = now
if tokens >= 1:
    tokens -= 1
    allow()
else:
    reject(retry_after = (1 - tokens) / refill_rate)
```

**Sliding window counter formula:** At second 45 of a 1-minute window: `count = current_window_count * (15/60) + previous_window_count * (45/60)`. Approximates a true sliding window with two fixed-window counters.

---

## Redis Implementation Patterns

### Atomic Rate Limiting with Lua

Redis operations must be atomic to prevent race conditions. Two concurrent requests checking the same counter can both see "under limit" and both proceed, exceeding the actual limit. Lua scripts execute atomically in Redis.

**Sliding window counter in Redis Lua:**
```lua
-- KEYS[1] = rate limit key
-- ARGV[1] = window size (seconds)
-- ARGV[2] = max requests
-- ARGV[3] = current timestamp

local key = KEYS[1]
local window = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local current_window = math.floor(now / window)
local previous_window = current_window - 1

local curr_key = key .. ":" .. current_window
local prev_key = key .. ":" .. previous_window

local curr_count = tonumber(redis.call("GET", curr_key) or "0")
local prev_count = tonumber(redis.call("GET", prev_key) or "0")

local elapsed = now % window
local weight = (window - elapsed) / window
local count = math.floor(prev_count * weight) + curr_count

if count >= limit then
    return {0, limit - count, window - elapsed}
end

redis.call("INCR", curr_key)
redis.call("EXPIRE", curr_key, window * 2)

return {1, limit - count - 1, 0}
```

**Key expiry strategy:** Set TTL to 2x the window size. This ensures the previous window's counter is available for the weighted calculation but does not accumulate indefinitely.

### Distributed Rate Limiting Challenges

**Clock skew:** Redis instances in different availability zones may have clocks that differ by milliseconds to seconds. For token bucket, clock skew causes inconsistent refill calculations. Mitigation: use Redis server time (`redis.call("TIME")`) instead of client-supplied timestamps.

**Partition tolerance:** If the Redis cluster partitions, clients connecting to different partitions see different counters. A client hitting partition A and partition B gets 2x the rate limit. Mitigation: accept this as a trade-off. Rate limiting is best-effort, not transactional. Over-limit by 2x during a partition is acceptable for most systems. For critical limits (billing, abuse prevention), use a single-leader Redis instance (accepting the availability trade-off).

**Multi-region:** For global APIs with region-local Redis instances, rate limits are per-region by default. If a global limit is needed, synchronize counters asynchronously with eventual consistency. Global exact limiting requires a single coordination point -- which defeats the purpose of multi-region deployment. Accept per-region limits for latency-sensitive APIs.

---

## Cost-Based Rate Limiting

Not all endpoints are equal. A `GET /users/{id}` costs 1 database query. A `POST /reports/generate` triggers a 30-second computation with multiple joins. Flat per-request rate limiting undertreats expensive endpoints and overtreats cheap ones.

### Endpoint Weight Scoring

Assign a cost weight to each endpoint based on resource consumption:

| Endpoint Category | Weight | Example |
|------------------|--------|---------|
| Simple read (cached) | 1 | `GET /config`, `GET /status` |
| Simple read (DB) | 2 | `GET /users/{id}` |
| List with pagination | 5 | `GET /orders?page=1` |
| Write operation | 5 | `POST /users`, `PUT /orders/{id}` |
| Search / filtered query | 10 | `GET /products?q=widget&category=tools` |
| Report generation | 25 | `POST /reports/generate` |
| Bulk operations | 50 | `POST /users/import` |

**Rate limit deduction:** Instead of "100 requests per minute," enforce "1000 cost units per minute." A client can make 1000 simple reads, 200 list queries, or 40 report generations -- but not all three at full rate.

**Communicating cost:** Include cost information in rate limit headers: `X-RateLimit-Cost: 10` alongside `X-RateLimit-Remaining: 450`. Clients can budget their usage.

---

## Rate Limit Response Headers

Every rate-limited API must communicate limits to clients. Standardize on these headers:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-RateLimit-Limit` | Maximum requests (or cost units) per window | Client knows their ceiling |
| `X-RateLimit-Remaining` | Remaining requests in current window | Client can pace usage |
| `X-RateLimit-Reset` | Unix timestamp when window resets | Client knows when to retry |
| `Retry-After` | Seconds until retry is safe (on 429 only) | Machine-readable backoff |

**Include these headers on EVERY response, not just 429s.** Clients need remaining-count to implement proactive backoff before hitting the limit.

### Tiered Rate Limits by Auth Level

| Tier | Identification | Limit | Use Case |
|------|---------------|-------|----------|
| Anonymous | IP address | 60/hour | Public endpoint browsing |
| API key (free) | Key hash | 1,000/hour | Development, evaluation |
| API key (paid) | Key hash + plan | 10,000/hour | Production workloads |
| OAuth2 user | User ID + client ID | Per-user sublimit within app quota | User-facing applications |
| Internal service | mTLS certificate | 100,000/hour or exempt | Service-to-service |

**Health check exemption:** Exclude health check endpoints (`/health`, `/ready`) from rate limiting entirely. Load balancers and orchestrators poll these continuously -- rate limiting them causes false-positive instance removal.

---

## Retry Strategies for Clients

**Exponential backoff with jitter:** `delay = min(base * 2^attempt + random(0, jitter), max_delay)`. Without jitter, all clients retry simultaneously after a rate limit window reset (thundering herd). Jitter spreads retries across the window.

**Circuit breaker integration:** After N consecutive 429 responses, stop sending requests entirely for a cooldown period. This prevents wasting client resources on requests that will be rejected and reduces load on the server during overload.

**Retry budget:** Limit retries to 10-20% of total request volume. If more than 20% of requests are retries, the system is in a degraded state -- retrying makes it worse. Shed load instead.
