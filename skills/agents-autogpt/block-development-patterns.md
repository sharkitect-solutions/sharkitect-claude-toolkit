# Block Development Patterns for AutoGPT

## Block Anatomy

Every AutoGPT block has the same structure. Understanding the execution lifecycle prevents the most common development mistakes.

### Execution Lifecycle

| Phase | What Happens | Common Mistake |
|---|---|---|
| **1. Schema validation** | Pydantic validates input_data against `input_schema` | Using `dict` or `Any` types. Validation passes everything, errors surface at runtime |
| **2. Credential injection** | Platform provides credentials listed in `credentials_required` | Requesting credentials that aren't configured. Results in `CredentialsNotFoundError` at runtime, not at graph validation |
| **3. Execute method called** | Your `execute()` runs with validated inputs | Assuming execute runs only once. Platform may retry on transient failures |
| **4. Output yielding** | Each `yield "name", value` sends output to downstream nodes | Yielding the same output name twice. Second yield OVERWRITES the first. Downstream nodes only see the last value |
| **5. Error handling** | Unhandled exceptions mark node as FAILED | Catching all exceptions silently. Node appears "completed" with no output. Downstream nodes get no input |
| **6. Completion** | When execute() returns (after all yields), node is marked COMPLETED | Long-running blocks that never return. They hold executor resources and eventually timeout |

---

## Block Design Patterns

### Pattern 1: Transform Block (Most Common)

Takes input, processes it, yields output. No external calls.

| Aspect | Guideline |
|---|---|
| **When to use** | Data transformation, formatting, filtering, computation |
| **Schema** | Strict input and output types. No optional fields unless truly optional |
| **Error handling** | Validate edge cases in execute(), not in schema (schema can't express "positive integer") |
| **Testing** | Pure function testing. No mocks needed. Test edge cases (empty input, max values, unicode) |

### Pattern 2: API Integration Block

Makes external API calls. Most complex and most error-prone.

| Aspect | Guideline |
|---|---|
| **When to use** | Any external service call (LLM, REST API, database, file system) |
| **Rate limiting** | Implement per-block rate limiter. External APIs have limits; AutoGPT doesn't enforce any |
| **Timeout** | Set explicit timeout shorter than the node-level timeout. If node timeout is 120s, set API timeout to 90s so you can yield a meaningful error |
| **Retry logic** | Retry on 429 (rate limit) and 503 (service unavailable). Do NOT retry on 400 (bad request) or 401 (auth) |
| **Credential handling** | Always use `get_credentials()`. Never accept API keys as block input parameters |
| **Cost tracking** | Set `cost_config` for every block that incurs external costs. Users need visibility |
| **Idempotency** | External calls may be retried. Use idempotency keys where the API supports them |

### Pattern 3: Branching Block

Routes execution based on conditions. Controls graph flow.

| Aspect | Guideline |
|---|---|
| **When to use** | Conditional logic, routing, decision points |
| **Output naming** | Use descriptive output names: `yield "high_priority", data` not `yield "output_a", data` |
| **Exhaustive branches** | Always include a default/fallback branch. If no condition matches, the block should still yield something |
| **No side effects** | Branching blocks should evaluate conditions only. Don't mix branching with data transformation |

### Pattern 4: Aggregation Block

Collects outputs from multiple upstream nodes.

| Aspect | Guideline |
|---|---|
| **When to use** | Combining results from parallel branches, merging data streams |
| **Input schema** | Use `list` types to accept multiple inputs. Schema should declare what it expects from each source |
| **Partial results** | If one upstream node fails, the aggregation block receives partial input. Handle missing data explicitly |
| **Ordering** | Parallel upstream nodes complete in any order. Do not assume ordering in aggregation |

---

## Common Block Anti-Patterns

| Anti-Pattern | What Developers Do | What Goes Wrong | Better Approach |
|---|---|---|---|
| **God Block** | Single block that fetches data, processes with LLM, formats output, and sends email | Untestable, unreusable, impossible to debug. If the LLM call fails, the entire block fails including the parts that worked | Split into 4 blocks: Fetch, LLM Process, Format, Send. Each can be tested, retried, and reused independently |
| **Silent Swallower** | `try: ... except: pass` around the entire execute method | Block always "succeeds" but yields nothing. Downstream nodes get no input and the graph silently produces empty output | Catch specific exceptions. For expected failures, yield an error output. For unexpected failures, let them propagate |
| **Schema Liar** | Schema says `output: str` but block yields `output: dict` or `output: None` | Downstream blocks receive wrong type. Error surfaces far from the cause. Debugging requires tracing through multiple nodes | Schema must match actual output types exactly. If output is optional, use `Optional[str]` in schema |
| **Credential Leaker** | API key passed as block input parameter instead of using credential system | Key visible in graph configuration, execution logs, and to anyone with graph read access | Always use `credentials_required` and `get_credentials()`. Never accept secrets as regular input |
| **Infinite Yielder** | Block in a loop that yields thousands of outputs | Executor memory grows, downstream nodes overwhelmed, execution slows to crawl | Batch results. Yield a list of results, not individual items. If streaming is needed, use a fixed buffer size |
| **Time Bomb** | Block works in dev but depends on specific environment (file paths, env vars, timezone, locale) | Breaks in production. Works on developer's machine, fails in Docker | Use platform-provided configuration only. No filesystem access. No env var reads (use credentials). Assume UTC |

---

## Testing Blocks

### Unit Testing Pattern

| Test Category | What to Test | Example |
|---|---|---|
| **Happy path** | Valid input produces expected output | Input: `{"query": "test"}` -> Output: `{"results": [...], "count": 3}` |
| **Edge cases** | Empty input, max-length input, special characters | Input: `{"query": ""}` -> Should yield empty results, not error |
| **Schema validation** | Invalid input types rejected before execute() runs | Input: `{"query": 123}` -> Pydantic validation error (not a runtime error in execute) |
| **Error scenarios** | External API failures, timeouts, rate limits | Mock API to return 500 -> Block should yield error output or raise meaningful exception |
| **Idempotency** | Running execute() twice with same input produces consistent results | Call execute() twice -> Same output both times (no duplicate side effects) |

### Integration Testing Pattern

| Test Type | What It Validates | Gotcha |
|---|---|---|
| **Block-to-block** | Output schema of Block A matches input schema of Block B | Schema compatibility isn't checked at graph save time. Only discovered at runtime |
| **Credential flow** | Block correctly retrieves and uses credentials | Test credentials must be configured in test environment. Mock credentials have different behavior than real ones |
| **Graph execution** | End-to-end graph produces expected output | Graph tests are slow (queue latency). Use direct block execution for most testing. Graph tests only for critical paths |

---

## Performance Optimization

| Optimization | When to Apply | Impact |
|---|---|---|
| **Reduce LLM calls** | Block makes multiple LLM calls when one suffices | Each LLM call adds 1-5 seconds and costs per token. Combine prompts where possible |
| **Cache external API responses** | Block calls same API with same parameters across executions | Implement block-level cache with TTL. Redis is already available in the platform stack |
| **Batch API calls** | Block processes items one-by-one via API | Many APIs support batch endpoints. 1 batch call vs 100 individual calls can be 10-50x faster |
| **Minimize yield size** | Block yields large objects (full API responses, base64 images) | Large yields consume executor memory and slow graph edge transmission. Extract only what downstream needs |
| **Async where possible** | Block makes multiple independent external calls sequentially | Use `asyncio.gather()` for independent API calls. AutoGPT blocks are async by default |

---

## Block Publishing Checklist

Before publishing a block to the AutoGPT marketplace or sharing with your team:

| Check | Why | How to Verify |
|---|---|---|
| **Schema completeness** | Consumers need to understand inputs and outputs without reading code | Every field has a description in the Pydantic model. No `dict`, `Any`, or `object` types |
| **Error handling** | Bad blocks crash graphs and waste user time | Run with invalid inputs, API failures, timeouts. Block should fail gracefully with meaningful error |
| **Cost transparency** | Users need to know what a block costs before using it | `cost_config` set for any block making paid API calls. Cost clearly documented |
| **Credential isolation** | Security requirement | No hardcoded keys. `credentials_required` lists all needed providers |
| **Idempotent execution** | Platform may retry. Side effects must be safe to repeat | Run execute() twice with same input. No duplicate records, double-sends, or state corruption |
| **Documentation** | Users need to know what the block does without reading source | Block `description` is clear. Input/output field descriptions explain expected values |
