---
name: voice-agents
description: "Use when building voice AI agents, implementing speech-to-speech or pipeline (STT->LLM->TTS) architectures, optimizing voice latency, integrating voice activity detection, or designing turn-taking and barge-in handling. NEVER use for text-only chatbots, pre-recorded IVR menu trees, or music/audio processing pipelines."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Voice Agents

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Architecture decisions (S2S vs Pipeline), latency budget, voice edge cases, turn-taking principles | Always (auto-loaded) |
| conversation-design-patterns.md | Turn state machine, multi-turn context management, slot-filling, persona design, voice prompt engineering, tool calling in voice, recovery patterns | When designing conversation flows, implementing turn-taking, or building dialogue systems |
| testing-debugging-guide.md | Test pyramid for voice, conversation test scenarios, latency debugging procedure, STT/LLM quality debugging, evaluation rubrics, A/B testing | When building test suites, debugging quality issues, or establishing QA processes |
| platform-integration-guide.md | Platform selection (Vapi/Retell/LiveKit/Twilio), telephony integration, WebRTC patterns, CRM integration, knowledge base (RAG) for voice, cost estimation | When choosing a platform, integrating telephony, or connecting voice agents to external systems |

## Architecture Decision Table

| Factor | Speech-to-Speech (S2S) | Pipeline (STT->LLM->TTS) |
|---|---|---|
| Latency | Lowest (~300-500ms) | Higher (~600-1200ms) |
| Emotional nuance | Preserved end-to-end | Lost between components |
| Debuggability | Opaque (audio in/out) | Each step inspectable |
| Cost | Higher per minute | Lower, pay-per-component |
| Controllability | Limited (model decides) | Full (inject, filter, route) |
| Best for | Conversational assistants, therapy bots, empathic agents | Customer service, compliance-heavy, tool-calling flows |
| Primary option | OpenAI Realtime API, Gemini Live | Deepgram STT + GPT-4o + ElevenLabs TTS |

**Decision rule:** Default to Pipeline unless emotional fidelity is the primary product differentiator. S2S sacrifices control for naturalness.

## Latency Budget

Sub-800ms end-to-end is the threshold for natural conversation. Budget each component.

| Component | Typical Range (ms) | Optimization Target | Primary Lever |
|---|---|---|---|
| Network round-trip (client -> server) | 20-80 | <50ms | Deploy regionally, WebSocket |
| Voice Activity Detection (VAD) | 0-300 | <100ms | Semantic VAD, not silence-only |
| STT (streaming) | 100-400 | <200ms | Streaming transcription, no wait-for-silence |
| LLM first token | 150-600 | <300ms | Streaming, smaller models for fast tasks |
| TTS first audio chunk | 80-300 | <150ms | Streaming TTS, pre-buffer |
| Audio playback start | 20-50 | <30ms | Pre-buffer 50ms before streaming |
| **Total target** | **<800ms** | **<600ms ideal** | Parallelize STT->LLM handoff |

**Critical path:** STT completion -> LLM first token -> TTS first chunk. Parallelize everything outside this path.

## Voice-Specific Edge Cases

| Scenario | Naive Handling | Correct Handling |
|---|---|---|
| Background noise triggers VAD | False turn start, garbled STT | Use semantic VAD (checks for speech content, not just audio energy) |
| User barges in mid-response | Agent keeps talking, frustrating user | Monitor input channel during output; interrupt and yield on VAD trigger |
| Silence mid-sentence (user thinking) | Premature end-of-turn detection | Set silence threshold to 1.2-2s, not 0.5s; use semantic completeness check |
| Heavy accent or non-native speaker | High STT word error rate | Add STT confidence scoring; fallback to "I didn't catch that" if WER risk is high |
| Phone/PSTN audio quality (8kHz) | STT trained on 16kHz degrades | Use STT model with phone-band support (Deepgram Nova-2 Phone model) |
| User speaks before TTS finishes | Audio collision, echo feedback | AEC (Acoustic Echo Cancellation) at client layer; server-side input muting during playback |
| Short backchannels ("uh-huh", "yeah") | Full LLM round-trip for 200ms filler | Classify short utterances pre-LLM; emit canned acknowledgment tokens without full inference |

## Rationalization Table

| Excuse | Why It's Wrong |
|---|---|
| "Users will wait a bit longer if the answer is good" | No they won't. >800ms feels like lag. >1200ms feels broken. Latency is UX, not just performance. |
| "We'll add barge-in later once the core works" | Barge-in is architecture, not a feature. Adding it retrofit requires redesigning the audio pipeline. Build it day one. |
| "Speech-to-speech is always better because it's more natural" | S2S removes your ability to inspect, filter, or route mid-conversation. For any regulated or tool-calling use case, pipeline is the right choice. |
| "We can use silence detection for turn-taking" | Silence-only VAD fires on pauses, filler words, and thinking time. Semantic VAD (checking for sentence completeness) cuts false positives by 60-80%. |
| "TTS voice quality doesn't matter that much" | Voice is the entire interface. Low-quality TTS destroys trust faster than a visual bug. Use streaming TTS with a tested voice from day one. |
| "We'll handle noise in post-processing" | Noise must be handled before STT, not after. AEC and noise suppression are client-layer concerns. Post-processing is too late. |

## Red Flags Checklist

- [ ] Latency is not being measured end-to-end per component - you cannot optimize what you do not measure
- [ ] Turn detection is silence-only (no semantic VAD) - will misfire on thinking pauses and filler words
- [ ] No barge-in detection - users cannot interrupt the agent, which feels unnatural and frustrating
- [ ] LLM responses are not length-constrained for voice - 3-sentence spoken answers feel like essays
- [ ] TTS is not streaming - entire response must generate before playback begins, adding 200-800ms
- [ ] No AEC or noise suppression at the client layer - echo and background noise corrupt STT
- [ ] S2S chosen for a compliance or tool-calling use case - you cannot inspect or intercept audio tokens mid-stream
- [ ] STT confidence scores are not monitored - silent degradation on accents or poor audio quality goes undetected

## NEVER List

- NEVER use silence-only turn detection in production. Semantic VAD is required. Silence thresholds alone fire on every thinking pause and "um".
- NEVER wait for full LLM response before starting TTS. Stream LLM tokens to TTS in real time. First-chunk latency is what users perceive.
- NEVER allow unconstrained LLM response length in voice contexts. Prompt explicitly: "Respond in 1-2 sentences. Be concise. This will be spoken aloud."
- NEVER skip AEC (Acoustic Echo Cancellation). Without it, the agent's own TTS audio feeds back into the microphone and corrupts subsequent STT turns.
- NEVER treat voice quality as a polish item. Voice is the entire interface. Placeholder TTS voices in demos set wrong expectations and erode stakeholder trust.

## Related Skills

Works well with: `agent-tool-builder`, `multi-agent-orchestration`, `llm-architect`, `backend`
