# Voice AI Production Monitoring

Load when deploying voice pipelines to production or diagnosing production quality issues.

## Metrics Dashboard

### Core Voice Metrics

| Metric | How to Measure | Good | Warning | Critical |
|--------|---------------|------|---------|----------|
| End-to-end turn latency | Timestamp delta: user stops speaking -> bot audio starts playing | <800ms | 800-1200ms | >1200ms |
| STT latency (per utterance) | Timestamp delta: audio chunk sent -> final transcript received | <300ms | 300-500ms | >500ms |
| LLM time-to-first-token | Timestamp delta: prompt sent -> first token received | <400ms | 400-800ms | >800ms |
| TTS time-to-first-byte | Timestamp delta: text sent -> first audio chunk received | <200ms | 200-400ms | >400ms |
| STT word error rate (WER) | Compare STT output to reference transcripts (sample 1% of calls) | <10% | 10-20% | >20% |
| Barge-in response time | Timestamp delta: user speech detected during TTS -> TTS audio stopped | <100ms | 100-300ms | >300ms |
| Audio quality (MOS estimate) | PESQ/POLQA score or user ratings | >4.0 | 3.0-4.0 | <3.0 |
| Concurrent sessions | Active WebSocket/WebRTC connections | <80% capacity | 80-95% | >95% |

### Infrastructure Metrics

| Metric | How to Measure | Good | Warning | Critical |
|--------|---------------|------|---------|----------|
| WebSocket reconnection rate | Reconnections per hour across all sessions | <1/hr per 100 sessions | 1-5/hr | >5/hr |
| Provider API error rate | 4xx/5xx responses from STT/TTS/LLM providers | <0.5% | 0.5-2% | >2% |
| Provider API latency P99 | 99th percentile response time per provider | <2x median | 2-5x median | >5x median |
| Memory usage per session | RSS delta per active voice session | <50MB | 50-100MB | >100MB (likely leak) |
| CPU usage (audio processing) | CPU time in audio encode/decode/resample | <30% per core | 30-60% | >60% (buffer underruns likely) |
| Buffer underrun rate | Playback buffer empty events per minute per session | 0 | 1-2/min | >2/min |

## Alerting Rules

### Immediate Response (Page)

| Condition | Action |
|-----------|--------|
| End-to-end latency P95 > 1500ms for 5 minutes | Check provider status pages. If provider healthy, check server CPU/memory. If both healthy, check network (traceroute to provider endpoints). |
| WebSocket connection failure rate > 10% for 2 minutes | Likely server-side issue. Check max connection limits, file descriptor limits, memory. |
| STT returning empty transcripts > 20% of utterances | Audio pipeline broken. Check: audio format mismatch, microphone permissions revoked, preprocessing chain error. |
| TTS producing silence > 10% of responses | TTS provider issue or text encoding problem. Check: provider status, input text for unprintable characters, output format config. |
| Provider 429 rate limit errors sustained 1 minute | Implement backoff. If already backed off, check if concurrent session count exceeds plan limits. |

### Investigate (Ticket)

| Condition | Action |
|-----------|--------|
| WER increases >5 points over 7-day rolling average | Check: audio quality degradation, user demographic shift, provider model update, preprocessing chain drift. |
| Average session duration drops >20% week-over-week | Users abandoning conversations. Check: latency spikes, error rates, conversation quality logs. |
| Memory usage per session trending upward over 24 hours | Memory leak. Profile: audio buffer accumulation, unclosed WebSocket connections, event listener growth. |
| Cost per minute increasing without traffic increase | Provider pricing change or inefficiency introduced. Check: LLM response length growth, unnecessary API calls, retry storms. |

## Load Testing Voice Pipelines

### Test Scenarios

| Scenario | What It Tests | Tool Approach |
|----------|--------------|---------------|
| Ramp-up (0 to max sessions over 10 min) | Connection handling, resource allocation | Script: open N WebSocket connections per second, send pre-recorded audio |
| Sustained load (max sessions for 30 min) | Memory leaks, connection stability, provider rate limits | Hold connections open, send periodic audio, monitor resource growth |
| Burst (2x normal in 30 seconds) | Auto-scaling response, queue depth, rejection handling | Rapid connection burst, measure time-to-first-response |
| Barge-in storm (all sessions interrupt simultaneously) | Queue clearing, state management under concurrent cancel | Send interrupt signals to all active sessions within 1-second window |
| Provider failover | Fallback chain activation, recovery time | Block provider endpoint with firewall rule, measure time to fallback |

### Synthetic Audio for Load Tests

| Approach | Pros | Cons |
|----------|------|------|
| Pre-recorded audio clips (real speech) | Most realistic. Tests actual STT accuracy under load. | Fixed scenarios. Need diverse clips for meaningful test. |
| TTS-generated audio (synthetic speech) | Unlimited variety. Script generates test utterances. | Cleaner than real speech. May not expose noise/accent edge cases. |
| Silence with periodic speech | Tests VAD under sustained load without transcript processing | Does not test STT or LLM paths. Useful for connection-only tests. |
| Noise-injected recordings | Tests preprocessing and STT robustness | Need calibrated noise levels. Too much noise = 100% failure (not useful). |

**Load test rule**: Always load test with the SAME provider plan you use in production. Dev/test API keys often have different rate limits than production keys. A test that passes on dev may hit rate limits immediately in production.

## Capacity Planning

### Resource Estimation Per Concurrent Session

| Component | CPU | Memory | Network Bandwidth |
|-----------|-----|--------|-------------------|
| WebSocket connection management | ~0.5% core | ~2MB | Negligible (control frames) |
| Audio receive + preprocessing | ~2% core | ~5MB (buffers) | 32KB/s in (16kHz PCM16) |
| STT API call (streaming) | ~0.1% core (HTTP client) | ~1MB | 32KB/s out + transcript response |
| LLM API call (streaming) | ~0.1% core (HTTP client) | ~2MB (context buffer) | ~1KB/s out, ~5KB/s in |
| TTS API call (streaming) | ~0.1% core (HTTP client) | ~3MB (audio buffer) | ~48KB/s in (24kHz PCM16) |
| Audio send + playback management | ~1% core | ~5MB (jitter buffer) | 48KB/s out |
| **Total per session** | **~4% core** | **~18MB** | **~160KB/s bidirectional** |

**Scaling estimate**: A 4-core, 8GB server handles ~50 concurrent voice sessions (CPU-limited, not memory). At 100+ sessions, use multiple servers with a load balancer that supports WebSocket sticky sessions.

### Scaling Patterns

| Scale | Architecture | Key Consideration |
|-------|-------------|-------------------|
| 1-50 concurrent | Single server, all components | Simple. Monitor CPU and memory. |
| 50-200 concurrent | 2-4 servers behind WebSocket-aware load balancer | Sticky sessions required (voice state is per-connection). |
| 200-1000 concurrent | Dedicated audio servers + separate LLM/API servers | Separate compute-heavy (audio processing) from I/O-heavy (API calls). |
| 1000+ concurrent | LiveKit SFU cluster or equivalent media server | Roll-your-own WebSocket management doesn't scale. Use purpose-built media infrastructure. |

## Disaster Recovery

### Provider Outage Playbook

| Provider Down | Impact | Mitigation |
|---------------|--------|------------|
| STT provider | Bot cannot understand user | Fallback: secondary STT provider. If none: play "I'm having trouble hearing you. Please try again in a moment." and retry every 30 seconds. |
| LLM provider | Bot cannot generate responses | Fallback: secondary LLM (even a smaller model). If none: play cached "I'm experiencing technical difficulties" and offer callback. |
| TTS provider | Bot cannot speak | Fallback: secondary TTS. If none: fall back to text chat. Send text transcript to user's screen/app. |
| WebRTC/media server | No audio transport | Switch to WebSocket audio transport (degraded AEC). If impossible: disconnect gracefully with status message. |
| All providers | Complete voice failure | Degrade to text chat immediately. Queue voice sessions for retry. Notify operations team. |

### Recovery Procedures

| Event | Recovery Steps | Expected Recovery Time |
|-------|---------------|----------------------|
| WebSocket disconnect (single session) | Auto-reconnect with exponential backoff (1s, 2s, 4s, max 30s). Resume from last known state. | 2-10 seconds |
| Provider rate limit (429) | Back off per retry-after header. Queue audio. Resume when limit clears. | 10-60 seconds |
| Server restart (rolling) | Drain existing connections (30s grace). New connections to new instance. Lost sessions reconnect. | 30-60 seconds |
| Full server crash | Load balancer detects health check failure. Routes new connections to healthy instances. Crashed sessions lost. | 5-15 seconds (detection) + reconnect time |
| Database failure (session state) | Voice continues (stateless for audio). Context/history unavailable. Log warning, continue with fresh context. | Depends on DB recovery |

## Session Logging Best Practices

### What to Log Per Session

| Field | Why | Privacy Note |
|-------|-----|-------------|
| session_id | Correlate all events in a session | Safe |
| user_id (hashed) | Track per-user quality patterns | Hash to anonymize |
| start_time, end_time, duration | Session analytics and billing | Safe |
| per_stage_latency (array) | Identify bottleneck stages | Safe |
| stt_transcript | Debug conversation quality | PII risk. Redact or encrypt at rest. Retention policy required. |
| llm_prompt_tokens, completion_tokens | Cost tracking | Safe |
| tts_characters | Cost tracking | Safe |
| error_events (array) | Diagnose failures | Safe |
| audio_quality_score | Track quality trends | Safe |
| barge_in_count | Measure conversation naturalness | Safe |
| reconnection_count | Track connection stability | Safe |

### What NOT to Log

- Raw audio bytes in application logs (storage explosion, privacy risk)
- Provider API keys (appears in connection URLs -- redact)
- Full user audio recordings without consent disclosure (legal risk in many jurisdictions -- GDPR, CCPA, BIPA)
- STT interim/partial results (noise, storage waste -- log final transcripts only)

**Consent rule**: If recording or logging voice data for quality improvement, users must be informed BEFORE the conversation starts. Many jurisdictions require explicit opt-in consent for voice recording. "This call may be recorded for quality assurance" is legally required, not optional.
