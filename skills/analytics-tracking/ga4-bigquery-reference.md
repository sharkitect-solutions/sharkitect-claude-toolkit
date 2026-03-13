# GA4 BigQuery Export Reference

## Export Configuration

| Setting | Recommended | Why | Gotcha |
|---|---|---|---|
| Export type | Daily + Streaming | Daily for batch analysis (free). Streaming for real-time dashboards ($0.05/GB) | Streaming export has 10-15 minute delay despite the name. For true real-time, use GA4 Realtime API (which has its own 2-minute delay and limited dimensions) |
| Dataset location | Match your BigQuery region to GA4 property region | Cross-region queries add latency and can incur data transfer charges | Once set, dataset location CANNOT be changed. You must delete and recreate to move regions |
| Export includes | events_*, users_*, pseudonymous_users_* | events_* contains all event-level data. users_* and pseudonymous_users_* contain user-scoped properties | users_* table only contains users who triggered events in that export day. It is NOT a user master table -- it's an event-day snapshot |
| Table structure | events_YYYYMMDD (daily), events_intraday_YYYYMMDD (streaming) | Intraday tables are overwritten continuously. Daily tables are immutable after creation | Intraday tables are deleted when the daily table is created (~24-48 hours after the day ends). Never build pipelines that depend on intraday tables persisting |
| BigQuery sandbox | Free tier: 1TB queries/month, 10GB storage | Sufficient for small-medium sites (<1M events/day) | Sandbox tables auto-expire after 60 days. Must upgrade to standard project for persistent storage |

## Event Data Schema

The `events_*` table uses a nested/repeated schema. Every row is one event.

| Column | Type | Use | Query Gotcha |
|---|---|---|---|
| event_name | STRING | Event identifier | Case-sensitive. "page_view" != "Page_View". Filter with LOWER() if your implementation has inconsistencies |
| event_date | STRING (YYYYMMDD) | Partition key | STRING not DATE. Must cast for date operations: `PARSE_DATE('%Y%m%d', event_date)` |
| event_timestamp | INTEGER (microseconds) | Event time | Microseconds since epoch, not milliseconds. Divide by 1000000 for seconds: `TIMESTAMP_MICROS(event_timestamp)` |
| event_params | RECORD (REPEATED) | Custom parameters | Nested array. Must UNNEST to query: `UNNEST(event_params) AS param WHERE param.key = 'page_location'`. Each param has .string_value, .int_value, .float_value, .double_value -- only ONE is populated per param |
| user_properties | RECORD (REPEATED) | User-scoped dimensions | Same UNNEST pattern as event_params. Properties persist across events for the same user |
| user_pseudo_id | STRING | Client-side cookie ID | NOT the same as user_id. Changes when cookies are cleared. One person can have multiple pseudo IDs across devices/browsers |
| user_id | STRING | Your authentication ID | NULL for anonymous users. Only populated after you set it via gtag('set', 'user_id', ...) or GTM |
| traffic_source | RECORD | First-touch attribution | Contains source, medium, name. This is FIRST touch only -- not session-level. For session-level, query the session_start event's params |
| device | RECORD | Device info | Contains category (mobile/desktop/tablet), browser, operating_system, language. mobile_brand_name and mobile_model_name are NULL for web |
| geo | RECORD | Location | Country, city, region. Accuracy varies: country is ~95% accurate, city is ~70-80%. Metro/DMA is US-only |

## Essential Query Patterns

### Session-level metrics
GA4 BigQuery has no session table. You must reconstruct sessions from events.

Session definition: group events by `user_pseudo_id` + `ga_session_id` (from event_params). A session ends after 30 minutes of inactivity (default GA4 setting).

Key gotcha: `ga_session_id` is a Unix timestamp (seconds) of session start, not a sequential counter. Two sessions from the same user on the same day will have different `ga_session_id` values.

### Conversion attribution
GA4 BigQuery export does NOT include the attribution model calculations shown in the GA4 UI. You get raw events. To replicate:
- Last-click: straightforward -- attribute to the last non-direct source before conversion
- Data-driven: NOT replicable in BigQuery without Google's ML model. Must use GA4 API or Ads Data Hub
- First-click: attribute to first `session_start` event's traffic source for that user

### User counting
GA4 BigQuery uses `user_pseudo_id` for user counting, which is cookie-based. To match GA4 UI "Active Users" metric, count distinct `user_pseudo_id` values with at least one `session_start` event + `engagement_time_msec > 0`.

## Cost Optimization

| Technique | Savings | Implementation |
|---|---|---|
| Partition by event_date | 70-90% query cost reduction | Tables are auto-partitioned. Always filter with `_TABLE_SUFFIX` or `event_date` to avoid scanning all partitions |
| Cluster by event_name | 30-50% for filtered queries | Create clustered table: `CLUSTER BY event_name`. Effective when queries filter on specific events |
| Materialized views | 50-80% for repeated queries | Pre-aggregate common metrics (daily sessions, conversions by source). Auto-refreshes. First 1TB/month of materialized view queries free |
| SELECT only needed columns | 20-40% | BigQuery charges by column data scanned. Never `SELECT *` on GA4 tables -- nested columns like event_params are expensive |
| Schedule queries during off-peak | 0% (but reliability) | BigQuery has on-demand and flat-rate pricing. On-demand has no time-of-day discount. Flat-rate (slots) benefits from off-peak scheduling |

**Monthly cost estimate by scale**:
- 100K events/day: ~$5-10/month (well within free tier for queries)
- 1M events/day: ~$20-50/month (queries start exceeding 1TB/month)
- 10M events/day: ~$200-500/month (consider flat-rate pricing at 500 slots)

## Common BigQuery + GA4 Mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Querying without date filter | Scans ALL historical data. One query can cost $50+ for a year of data | Always include `WHERE event_date BETWEEN '20260101' AND '20260301'` or `WHERE _TABLE_SUFFIX BETWEEN '20260101' AND '20260301'` |
| Using `COUNT(DISTINCT user_id)` for total users | Excludes anonymous users (user_id is NULL until login). Undercounts by 40-80% for most sites | Use `COUNT(DISTINCT user_pseudo_id)` for total users. Use user_id only for logged-in user analysis |
| Treating traffic_source as session-level | traffic_source in the export is FIRST-TOUCH attribution for the user's lifetime, not the current session | For session-level source/medium, extract from the `session_start` event's `page_referrer` parameter or use collected_traffic_source (GA4 v2 export) |
| Not handling UNNEST for event_params | Queries return zero rows or incorrect results when filtering nested fields without UNNEST | Every query on event_params or user_properties must UNNEST. Use subquery pattern: `SELECT * FROM events, UNNEST(event_params) AS p WHERE p.key = 'value'` |
| Joining events_* to users_* incorrectly | users_* table is a daily snapshot, not a master table. Joining on wrong date produces NULL user properties | Join on both user_pseudo_id AND _TABLE_SUFFIX to get same-day user properties |
