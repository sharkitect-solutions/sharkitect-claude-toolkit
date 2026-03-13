# Voice Agent Testing & Debugging Guide

Load when building test suites for voice agents, debugging conversation quality issues, or establishing QA processes for voice deployments.

## Testing Strategy

### Test Pyramid for Voice Agents

| Layer | What It Tests | How | Coverage Target |
|---|---|---|---|
| Unit tests | Individual components (VAD config, prompt templates, slot extraction, tool call formatting) | Standard unit test framework. Mock provider APIs. | 80%+ on business logic |
| Integration tests | Component-to-component (STT->LLM pipeline, LLM->TTS handoff, tool call execution) | Real provider calls with test audio. Measure latency at each boundary. | Every integration boundary |
| Conversation tests | Multi-turn dialogue flows (happy path, edge cases, error recovery) | Scripted conversations: synthetic audio in, verify transcript + agent response + actions taken | 20-30 critical scenarios |
| Load tests | Concurrent session handling, provider rate limits, resource scaling | Simulated concurrent sessions with pre-recorded audio | Peak expected load + 2x burst |
| Voice quality tests | End-user experience (latency, naturalness, accuracy, task completion) | Human evaluation with scoring rubric. 5 evaluators per scenario minimum. | Monthly or per-release |

### Conversation Test Scenarios (Must-Have)

| Category | Scenario | What to Verify |
|---|---|---|
| Happy path | User provides all info cleanly, task completes | Correct slot extraction, correct tool calls, correct response, <800ms turn latency |
| Barge-in | User interrupts mid-response | TTS stops within 200ms. Agent acknowledges new input. Context preserved. |
| Correction | User says "no, I said Tuesday" after agent confirms Thursday | Slot updated correctly. Agent doesn't re-ask already-confirmed slots. |
| Ambiguity | User gives vague answer ("sometime next week") | Agent asks clarifying question. Doesn't guess or hallucinate a specific date. |
| Out-of-scope | User asks something the agent can't handle | Agent clearly states limitation. Offers alternative or handoff. Doesn't hallucinate. |
| Silence timeout | User stops talking for 10+ seconds | Agent prompts "Are you still there?" after 5-8s. Ends gracefully after 2 prompts. |
| Background noise | Loud environment, TV, other speakers | VAD doesn't false-trigger on non-speech. STT accuracy degrades gracefully. |
| Long utterance | User speaks for 30+ seconds without pausing | Agent doesn't cut off. STT handles full utterance. LLM receives complete transcript. |
| Repeated failures | STT returns garbage 3+ times in a row | Agent offers text alternative or human handoff. Doesn't loop "I didn't catch that" forever. |
| Tool call failure | External API returns error during conversation | Agent recovers verbally. Offers retry or alternative. Doesn't expose error details. |

### Automated Conversation Testing

| Approach | Implementation | Tradeoff |
|---|---|---|
| Text-based simulation | Send transcript text directly to LLM (skip STT/TTS) | Fast, cheap, tests logic only. Misses audio pipeline bugs. |
| Synthetic audio | Generate test utterances with TTS, feed through full pipeline | Tests full pipeline. Cleaner than real speech -- may miss accent/noise edge cases. |
| Recorded audio replay | Record real user sessions (with consent), replay through pipeline | Most realistic. Fixed scenarios. Legal/consent requirements. |
| LLM-as-evaluator | Second LLM scores agent responses for correctness, tone, helpfulness | Scalable. Correlates ~80% with human evaluation. Misses voice-specific issues (latency, naturalness). |

## Debugging Methodology

### Latency Debugging Procedure

When end-to-end latency exceeds target:

| Step | Action | Tool/Method | What to Look For |
|---|---|---|---|
| 1 | Measure each pipeline stage independently | Timestamps at stage boundaries (VAD end, STT response, LLM first token, TTS first byte) | Which stage is the bottleneck? |
| 2 | Check if bottleneck is consistent or intermittent | Plot latency histogram per stage over 100+ turns | Consistent = architecture issue. Intermittent = provider or network issue. |
| 3 | Test provider latency in isolation | Direct API call to STT/LLM/TTS with test input. Measure response time. | If provider is slow in isolation, it's their issue. If fast in isolation but slow in pipeline, it's your integration. |
| 4 | Check for serialization | Are stages running sequentially that could overlap? | STT->LLM handoff: are you waiting for full STT transcript before sending to LLM? Use streaming. |
| 5 | Check network | Traceroute to provider endpoints. Check for DNS resolution delays. | DNS: cache resolver results. Network: deploy closer to provider endpoints. |
| 6 | Check resource contention | CPU/memory during active sessions. Are audio processing and API calls competing? | Separate audio processing (CPU-bound) from API calls (I/O-bound) onto different threads/processes. |

### STT Accuracy Debugging

| Symptom | Likely Cause | Diagnosis | Fix |
|---|---|---|---|
| Random word substitutions | Audio quality issue (noise, echo, compression) | Compare raw audio waveform to transcript. Listen to the audio. | Add preprocessing (noise gate, AEC). Check audio format matches provider expectation. |
| Consistent misrecognition of specific words | Domain vocabulary not in STT model | Test the specific word in isolation. Does it transcribe correctly with clean audio? | Add custom vocabulary/keywords list to STT config. Deepgram: `keywords` parameter. |
| First word always wrong | Prefix padding too short -- VAD clips first syllable | Check VAD `prefix_padding_ms` setting. | Increase to 300-400ms. |
| Transcript is empty | Audio not reaching STT, or format mismatch | Check WebSocket/API logs. Verify audio bytes are actually being sent. Check format. | Most common: sending WAV with header to endpoint expecting raw PCM, or sample rate mismatch. |
| Transcript appears after long delay | Not using streaming STT, waiting for full utterance | Check if STT client is configured for streaming or batch | Switch to streaming mode. Send audio chunks as they arrive, don't buffer the full utterance. |

### LLM Response Quality Debugging

| Issue | Diagnosis | Fix |
|---|---|---|
| Agent gives long verbose responses | System prompt missing length constraint | Add: "Respond in 1-2 sentences maximum. This will be spoken aloud." |
| Agent outputs markdown, lists, or URLs | System prompt missing format constraint | Add: "Never use bullet points, numbered lists, URLs, code blocks, or markdown formatting." |
| Agent hallucinates facts | Context doesn't contain the needed information, LLM fills in gaps | Add: "If you don't have the specific information, say you'll need to check on it. Never guess." Add retrieval (RAG) for factual queries. |
| Agent forgets earlier conversation | Context window overflow or missing conversation history | Check token count. Implement summary + recent turns strategy. Verify history is actually being passed. |
| Agent personality drifts | System prompt washed out by long conversation context | Move persona instructions to both system prompt AND periodic "reminder" injections every 10 turns. |
| Agent calls wrong tool | Tool descriptions ambiguous or overlapping | Make tool descriptions mutually exclusive. Add negative examples: "Do NOT use this tool for X." |

## Evaluation Rubrics

### Conversation Quality Scorecard

Rate each dimension 1-5 for every test conversation:

| Dimension | 1 (Failing) | 3 (Acceptable) | 5 (Excellent) |
|---|---|---|---|
| Task completion | Task not completed, wrong outcome | Task completed with minor friction | Task completed smoothly on first attempt |
| Turn latency | >2s average turn time | 800ms-1.2s average | <800ms consistently |
| Naturalness | Robotic, awkward phrasing, unnatural pauses | Mostly natural with occasional awkwardness | Indistinguishable from skilled human agent |
| Error recovery | Agent loops, crashes, or gives up on first error | Recovers from errors but awkwardly | Recovers gracefully, user barely notices |
| Conciseness | Agent gives paragraph-length spoken responses | Responses are right length but could be tighter | Every word earns its place |
| Persona consistency | Agent personality changes mid-conversation | Mostly consistent with occasional drift | Rock-solid personality throughout |

**Passing threshold**: Average 3.5+ across all dimensions with no dimension below 2.0.

### A/B Testing Voice Changes

| What to Test | How to Split | Sample Size | Metric |
|---|---|---|---|
| System prompt changes | Random session assignment | 100+ sessions per variant | Task completion rate + user satisfaction |
| TTS voice selection | Random session assignment | 200+ sessions per variant | User satisfaction + repeat usage |
| VAD threshold changes | Random session assignment | 100+ sessions per variant | False trigger rate + successful turn completion |
| Barge-in sensitivity | Random session assignment | 100+ sessions per variant | Successful barge-in rate + accidental barge-in rate |
| Persona tone (formal vs casual) | Segment by user demographic if available | 100+ sessions per variant | Task completion + NPS |

**A/B testing rule**: Only test ONE variable at a time. Voice interactions have so many variables that multi-variable tests are uninterpretable. Run for minimum 7 days to capture day-of-week effects.

## Production Monitoring Essentials

### Key Metrics to Track Per Session

| Metric | Why | Alert Threshold |
|---|---|---|
| Average turn latency (P50, P95) | User experience proxy | P95 > 1.5s for 5 minutes |
| Task completion rate | Is the agent actually helping? | <70% over rolling 24 hours |
| Barge-in success rate | Can users interrupt effectively? | <50% barge-in attempts result in clean interruption |
| Escalation rate | How often does agent hand off to human? | >30% sessions escalated (for customer service agents) |
| Average session duration | Efficiency proxy | >2x expected duration for task type |
| STT confidence (average per session) | Audio quality proxy | Average confidence <0.7 across 10+ sessions |
| Silence timeout triggers | User engagement proxy | >20% sessions end via silence timeout |
