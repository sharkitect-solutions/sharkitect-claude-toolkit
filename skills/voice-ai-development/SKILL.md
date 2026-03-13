---
name: voice-ai-development
description: "Use when implementing voice AI features: real-time voice agents, STT/TTS pipelines, WebRTC audio, voice provider integration (OpenAI Realtime, Deepgram, ElevenLabs, Vapi, LiveKit), latency optimization, barge-in detection, or voice-specific error handling. NEVER for voice agent architecture decisions without implementation (use voice-agents), general audio processing without voice AI context (use standard libraries), phone system configuration (use twilio-communications), transcription-only workflows (use transcribe)."
---

# Voice AI Development

## Scope Boundary

| Task | This skill | Other skill |
|------|-----------|-------------|
| Choose S2S vs pipeline architecture | Yes | voice-agents (strategy) |
| Implement STT/TTS streaming code | Yes | -- |
| Select voice provider for a project | Yes | voice-agents (broader evaluation) |
| Wire up WebRTC audio transport | Yes | -- |
| Optimize voice latency budget | Yes | -- |
| Design multi-agent voice system | No | voice-agents |
| Transcribe a recorded audio file | No | transcribe |
| Configure Twilio phone numbers/IVR | No | twilio-communications |
| Build non-voice audio processing | No | standard libraries |

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Pipeline architecture, provider selection, latency budgets, edge cases, debugging | Always (auto-loaded) |
| provider-integration-reference.md | Provider-specific API patterns (OpenAI Realtime, Deepgram, ElevenLabs, LiveKit, Vapi), auth, formats, cost comparison | When connecting to a specific provider or troubleshooting provider-specific issues |
| audio-pipeline-cookbook.md | Audio format specs, sample rate conversion, VAD tuning parameters, preprocessing chains, buffering strategies, codec selection | When implementing audio processing, format conversion, or VAD tuning |
| production-monitoring.md | Metrics dashboards, alerting rules, load testing, capacity planning, disaster recovery, session logging | When deploying to production or diagnosing production quality issues |

## Voice Pipeline Assembly Procedure

Follow this sequence for every voice AI implementation. The order matters -- later decisions depend on earlier ones.

1. **Determine if voice is justified**: Voice adds latency, cost, and complexity over text. Ask: Does this use case genuinely require real-time spoken interaction (hands-free, accessibility, phone-based), or would async audio messages or text chat serve the same need at 10x lower cost? If the answer is "text would work," stop here -- the voice pipeline is unnecessary complexity.
2. **Set the latency target**: Use the Latency Budget Framework to establish a target. If the target is >1200ms, use a hosted platform (Vapi) instead of building custom. If <600ms, you need S2S pipeline with co-located services. If the user already has a working pipeline with latency problems, skip to step 5 and debug the existing pipeline.
3. **Select providers per stage**: Use the Provider Selection Decision Matrix for each pipeline stage independently. Do not default to a single provider for all stages unless the user needs billing simplicity over performance. If the user's existing provider handles STT+TTS adequately, do not introduce multi-provider complexity.
4. **Wire the streaming pipeline**: Connect stages with streaming, not batch. Start TTS on first LLM sentence boundary, not full completion. This single optimization typically saves 500ms+. If using OpenAI Realtime (audio-in/audio-out), skip this step -- the model handles streaming internally.
5. **Implement barge-in before anything else**: Barge-in handling (stop TTS + clear queue + cancel LLM + restart STT) is the feature that separates demos from production. Build it first, not last. If total turn latency exceeds 1200ms after integration, go back to step 2 and re-evaluate the budget.
6. **Test on mobile networks**: WiFi demos hide jitter, packet loss, and variable latency. Test on 4G with 100ms+ jitter before declaring the pipeline "working." If STT accuracy drops below 85% on mobile, add audio preprocessing (noise gate, gain normalization, 80Hz high-pass filter). If browser deployment, verify against the Browser Audio Restrictions table before launch.

**Key mindset**: The difference between a voice AI demo and a production voice agent is latency discipline. Every architectural decision must be evaluated against the latency budget. If you cannot measure per-stage latency, you cannot optimize it.

## Provider Selection Decision Matrix

Evaluate top-down. Use the FIRST match.

| Signal | Provider | Tradeoff |
|--------|----------|----------|
| Need voice-to-voice with GPT intelligence, single provider | OpenAI Realtime API | Highest per-minute cost ($0.06/min audio). Audio-in audio-out only -- no text intermediary unless you enable transcription. 24kHz PCM16. |
| Need phone-based voice agent deployed in hours, not days | Vapi | Hosted platform, webhook-based. Fastest time-to-deploy. Less control over pipeline internals. Per-minute pricing includes infrastructure. |
| Need best STT accuracy with lowest transcription latency | Deepgram Nova-2 | ~100-200ms streaming latency. Best word error rate for English. 16kHz input. Volume pricing drops fast at scale. |
| Need highest quality synthetic voice (emotional range, cloning) | ElevenLabs | Best voice quality but 150-300ms first-byte latency (turbo model). Higher cost per character. 24kHz output. |
| Need self-hosted real-time infrastructure (WebRTC rooms) | LiveKit | Open-source server, agent framework for server-side bots. Most complex to deploy but full control. No per-minute API costs beyond compute. |
| Need cheapest unified STT+TTS at scale | Deepgram (STT + Aura TTS) | Single provider, single bill, volume discounts. TTS quality below ElevenLabs but adequate for most agents. Lowest total cost at >10K minutes/month. |
| Need browser-only prototype, no server | Web Speech API | Free, zero dependencies. Terrible accuracy, no streaming control, browser-only. Prototype use ONLY. |

**Override rule**: If the user has already committed to a specific provider (existing contract, integration, or team expertise), use it. Only suggest alternatives if the user reports a specific limitation that their current provider cannot address.

## Latency Budget Framework

Voice feels "real-time" when total perceived latency stays under 800ms. Natural human turn-taking gap is 200-500ms. Anything above 1200ms feels broken.

| Pipeline Stage | Typical Range | Where Time Goes |
|----------------|--------------|-----------------|
| Audio capture + VAD | 50-200ms | Microphone buffer + silence detection threshold. VAD silence_duration_ms is the main knob (shorter = faster but more false triggers). |
| STT processing | 100-300ms | Model inference + network. Streaming STT (Deepgram) gives interim results in ~100ms. Batch STT (Whisper) waits for full utterance. |
| STT -> LLM network | 10-50ms | Negligible if same cloud region. Add 50-100ms cross-region. |
| LLM first token | 200-800ms | Model size dependent. GPT-4o ~300ms. Claude ~400ms. Smaller models faster. Streaming essential -- do not wait for full completion. |
| LLM -> TTS handoff | 5-20ms | Start TTS on first sentence boundary, not full LLM completion. Sentence detection on streaming tokens saves 500ms+. |
| TTS first audio byte | 100-300ms | ElevenLabs turbo ~150ms. Deepgram Aura ~100ms. OpenAI Realtime ~80ms (integrated). Non-streaming TTS adds full synthesis time. |
| Audio playback buffer | 20-50ms | Jitter buffer + device output latency. Mostly fixed overhead. |

**Total budget example (optimized):** 50 + 100 + 20 + 300 + 10 + 120 + 30 = ~630ms (acceptable)
**Total budget example (naive):** 200 + 300 + 50 + 800 + 300 + 300 + 50 = ~2000ms (feels broken)

### Where to Cut Latency

1. Stream everything -- STT interim results, LLM token streaming, TTS chunk streaming
2. Start TTS before LLM finishes -- detect sentence boundaries in token stream, send completed sentences to TTS immediately
3. Use interim STT results -- start LLM processing on high-confidence interim transcripts, cancel if final differs
4. Co-locate services -- same cloud region for STT, LLM, TTS reduces 50-100ms per hop
5. Pre-warm connections -- keep WebSocket connections to providers open between turns, not per-utterance
6. Reduce VAD silence threshold -- default 500ms is conservative. 300ms works for most English conversations. Below 200ms causes false triggers.

## Pipeline Architecture Decision

| Factor | Server-to-Server (S2S) | Client-Server |
|--------|----------------------|---------------|
| Audio path | Provider -> your server -> provider (audio never touches browser) | Browser captures audio -> your server -> providers |
| Latency | Lower (server-to-server hops, no browser overhead) | Higher (extra browser-to-server hop for all audio) |
| Complexity | Higher (manage audio streams server-side, need media server or raw WebSocket handling) | Lower (browser Web Audio API handles capture/playback) |
| Control | Full control over pipeline, mixing, routing | Limited by browser APIs and permissions |
| Use case | Production voice agents, phone bots, high-volume | Prototypes, web demos, low-volume |
| Audio transport | WebSocket (simpler, unidirectional or bidirectional) or WebRTC (built-in echo cancellation, jitter buffer, NAT traversal) | WebRTC preferred (browser has native support) or WebSocket with manual audio handling |

**Decision rule:** If building a production voice agent that handles >100 concurrent calls or needs sub-600ms latency, use S2S. For everything else, start client-server and migrate if needed. If the user has an existing architecture, work within it -- do not propose a full pipeline migration unless they report a latency or scaling problem.

## Voice-Specific Edge Cases

These are the problems that separate working demos from production voice apps.

**Barge-in handling** -- User interrupts while TTS is playing. Must: (1) detect speech via VAD during playback, (2) immediately stop TTS audio output, (3) clear any queued audio chunks, (4) cancel pending LLM response if still generating, (5) restart STT listening. If you skip step 3 or 4, the bot "talks over" the user with stale content.

**VAD tuning** -- Default thresholds cause two failure modes. Too sensitive (threshold < 0.3): background noise, keyboard clicks, breathing trigger false speech detection. Too lax (threshold > 0.7): clips first syllables, misses quiet speakers. Start at 0.5, tune per environment. Also tune prefix_padding_ms (audio before speech trigger to capture) and silence_duration_ms (how long silence before end-of-turn).

**Audio format mismatches** -- OpenAI Realtime requires PCM16 at 24kHz mono. Deepgram expects PCM16 at 16kHz. ElevenLabs outputs at 22050Hz or 24000Hz depending on format. Browser MediaRecorder often outputs Opus in WebM. Resampling between sample rates adds 5-20ms latency. Worst case: accidental double-resampling in a mixed pipeline.

**Echo cancellation** -- WebRTC connections include built-in Acoustic Echo Cancellation (AEC). Raw WebSocket audio does not. Without AEC, the bot hears its own TTS output through the user's speakers, creating feedback loops or false barge-in triggers. Solutions: use WebRTC when possible, or implement software AEC (SpeexDSP, WebRTC AEC module), or use headphones-only constraint.

**Network jitter** -- Streaming audio over unreliable connections. Jitter buffer too small = choppy audio with gaps. Jitter buffer too large = added latency. Adaptive jitter buffers (WebRTC default) work well. For WebSocket audio: implement a 40-80ms playback buffer client-side. Mobile networks are worst -- 4G jitter can hit 100ms+.

**Silence and prosody** -- Most TTS providers output audio without natural pauses at sentence boundaries. Concatenated TTS chunks sound robotic. Insert 150-300ms silence between sentences. Also: TTS models handle punctuation differently -- commas, ellipses, and em-dashes produce inconsistent pause lengths across providers.

**Multi-language mid-conversation** -- User switches language mid-conversation. Most STT models do not auto-detect language switches within a stream. Deepgram multi-language mode helps but adds latency. Solution: detect language from STT output, switch STT model if confidence drops, restart TTS with matching language voice.

**Simultaneous speaker overlap** -- In multi-party voice scenarios, overlapping speakers degrade STT accuracy by 30-60%. Diarization helps identify who spoke but adds latency. For real-time multi-party: separate audio channels per participant when possible.

## Browser Audio Restrictions

Non-obvious browser policies that silently break voice AI in web deployments:

| Restriction | Impact | Workaround |
|---|---|---|
| Autoplay policy (all modern browsers) | TTS audio will not play until user has interacted with the page (click/tap). Bot appears completely silent on page load with no error in console. | Require a "Start conversation" button before initiating voice. Call `AudioContext.resume()` only after a user gesture event. |
| iOS Safari audio routing | Audio output routes to earpiece instead of speaker by default when no `<audio>` element is used. User can barely hear the bot. | Use an `<audio>` element for playback instead of raw AudioContext. Set `playsInline` attribute. Test on physical iOS devices -- simulators do not reproduce this. |
| MediaRecorder codec variance | Chrome outputs Opus in WebM container. Safari outputs AAC in MP4 container. Sending raw browser audio to STT providers without format detection causes silent transcription failures. | Check `MediaRecorder.isTypeSupported()` at startup and negotiate format. Send PCM16 (universally supported) when cross-browser compatibility is required. |
| getUserMedia permission persistence | Browser may revoke microphone permission after tab backgrounding (especially mobile Safari). Voice session breaks silently when user switches apps and returns. | Monitor `MediaStreamTrack.onended` event. Re-request permission and reinitialize audio capture when the track ends unexpectedly. |

## Common Integration Failures

| Failure | Symptom | Fix |
|---------|---------|-----|
| Non-streaming pipeline | 3-5 second delay per turn. User perceives bot as broken. | Stream all three stages (STT, LLM, TTS). Start TTS on first LLM sentence, not full completion. |
| Ignoring interruptions | Bot finishes old response after user interrupts. Feels like talking to a recording. | Implement barge-in: VAD during playback -> stop TTS -> clear queue -> cancel LLM -> restart STT. |
| Single provider for everything | Suboptimal quality per stage. Single point of failure. | Mix providers: Deepgram STT + your LLM + ElevenLabs TTS. Abstract behind interfaces for swapping. |
| No graceful degradation | TTS provider outage = complete silence. STT outage = bot stops responding. | Fallback chain: ElevenLabs TTS -> Deepgram Aura TTS -> cached "I'm having trouble, please wait" audio. |
| Blocking the audio thread | Synchronous database call or API request in the audio processing loop. Audio stutters or drops. | All I/O in the audio path must be async. Use queues between audio processing and business logic. |
| No WebSocket reconnection | Provider WebSocket drops (common after 10-30 min). Bot goes silent permanently. | Implement reconnect with exponential backoff. Buffer audio during reconnection gap. Resume STT session. |
| Missing audio preprocessing | Background noise, low gain, or clipping degrades STT accuracy by 20-40%. | Apply noise gate, gain normalization, and high-pass filter (remove below 80Hz) before STT. |
| Hardcoded sample rates | Pipeline assumes 16kHz everywhere. OpenAI sends 24kHz. Audio plays at wrong speed (chipmunk or slow-motion effect). | Negotiate format per provider. Resample explicitly at each boundary. Log actual sample rates. |

## Voice Quality Debugging Procedure

When voice quality degrades in production, diagnose systematically:

1. **Isolate the broken stage**: Record audio at each pipeline boundary (after capture, after STT text, LLM output text, TTS output audio). Compare to identify which stage introduces the problem. If all stages look fine individually, the problem is handoff timing or format conversion.
2. **Check the sample rate chain**: Log actual sample rates at every boundary. Mismatches cause chipmunk (too fast) or slow-motion (too slow) audio without explicit errors. Most common: sending 16kHz audio to a 24kHz endpoint or vice versa.
3. **Measure per-stage latency variance**: The stage with the highest variance (not highest average) is usually the bottleneck. A consistent 200ms is fine; a 200ms that spikes to 800ms every 5th call breaks the conversation flow.
4. **Test with known-good audio**: Send a pre-recorded clean audio file through the pipeline. If quality is fine with clean input but bad with live audio, the problem is capture or preprocessing, not the pipeline itself.

## Rationalization Table

Before implementing, verify the approach is justified.

| Impulse | Check First | Likely Better |
|---------|-------------|---------------|
| "Build custom voice pipeline from scratch" | Do you need sub-500ms latency or custom audio processing? | Use Vapi for standard voice agents. Build custom only when hosted platforms hit a wall. |
| "Use OpenAI Realtime for everything" | Are you willing to pay ~$0.06/min and accept audio-only interface? | Deepgram STT + your LLM + ElevenLabs TTS gives more control and often lower cost at scale. |
| "Add voice to the existing chatbot" | Does the use case genuinely benefit from voice vs text? Voice adds complexity, cost, and latency. | Text chat with optional audio messages (async) is 10x simpler and often sufficient. |
| "Implement WebRTC from scratch" | Do you need NAT traversal, SRTP, DTLS, STUN/TURN? | Use LiveKit or Daily.co. Raw WebRTC is thousands of lines of edge-case handling. |
| "Use Whisper for real-time STT" | Whisper is batch-only -- waits for full utterance. Adds 1-3 seconds per turn. | Use Deepgram Nova-2 or Deepgram streaming for real-time. Whisper is fine for post-call transcription. |
| "Run TTS on GPU locally" | Do you have reliable GPU infrastructure and model expertise? Latency often worse than API. | Use hosted TTS APIs until you hit >50K minutes/month where self-hosted ROI makes sense. |

## Red Flags

Stop and reassess if you encounter any of these.

1. Total turn latency exceeds 1200ms in testing -- something in the pipeline is not streaming
2. Bot responds to its own audio output -- missing echo cancellation
3. First word of user speech is consistently clipped -- VAD prefix_padding_ms too low or threshold too high
4. Audio sounds like chipmunks or slow motion -- sample rate mismatch between pipeline stages
5. Bot keeps talking after user interrupts -- barge-in not implemented or TTS queue not cleared
6. WebSocket connections drop every 10-30 minutes -- missing keepalive pings or reconnection logic
7. STT accuracy drops below 85% in production -- missing audio preprocessing (noise, gain, sample rate)
8. Voice agent works in dev but not production -- local machine has lower latency than cloud routing; test with realistic network conditions

## NEVER

1. NEVER wait for full LLM completion before starting TTS -- stream sentence-by-sentence or you add 1-3 seconds of dead air
2. NEVER use synchronous/blocking calls in the audio processing pipeline -- one slow database query kills the entire audio stream
3. NEVER hardcode a single provider without a fallback interface -- provider outages are common; abstract STT/LLM/TTS behind swappable interfaces
4. NEVER skip echo cancellation testing -- works fine with headphones in dev, creates feedback loops with speakers in production
5. NEVER deploy without testing on mobile networks -- WiFi demos hide jitter, packet loss, and variable latency that break voice on 4G/5G
