# Voice Agent Platform Integration Guide

Load when choosing a voice agent platform, integrating with telephony providers, or connecting voice agents to external systems.

## Platform Selection Decision Matrix

Evaluate in order. First match wins.

| Signal | Platform | Why |
|---|---|---|
| Need phone number (PSTN) with <1 week to deploy | Vapi or Retell AI | Hosted platforms handle telephony, STT, TTS, hosting. Phone number provisioning in minutes. |
| Need custom LLM + tool calling over phone | Twilio + custom pipeline | Twilio provides PSTN. You control STT/LLM/TTS stack. More work but full control. |
| Need WebRTC in-browser with real-time voice | LiveKit Agents | SFU handles WebRTC complexity. Agent framework runs server-side. Best for browser-based voice. |
| Need lowest possible latency (sub-500ms) | OpenAI Realtime API (S2S) | Audio-in/audio-out eliminates STT/TTS hops. Tradeoff: less control, higher per-minute cost. |
| Need multi-modal (voice + screen sharing + video) | LiveKit or Daily.co | Media servers handle multiple tracks. Voice-only platforms can't add video later. |
| Enterprise compliance (HIPAA, SOC 2, data residency) | Self-hosted pipeline on compliant infrastructure | Hosted platforms may not meet compliance requirements. Verify BAA availability before choosing hosted. |

## Telephony Integration Patterns

### PSTN (Phone Calls) Architecture Options

| Option | How It Works | Latency | Cost | Complexity |
|---|---|---|---|---|
| Vapi (fully hosted) | Vapi handles phone number, STT, LLM orchestration, TTS | Medium (800-1200ms) | $0.05-0.15/min + LLM costs | Low |
| Retell AI (fully hosted) | Similar to Vapi. Handles full pipeline. | Medium (800-1200ms) | $0.05-0.10/min + LLM costs | Low |
| Twilio Media Streams + custom | Twilio sends raw audio over WebSocket. You handle STT/LLM/TTS. | Low-medium (600-1000ms) | Twilio: $0.0085/min + your pipeline costs | High |
| Vonage + custom | Similar to Twilio approach. WebSocket audio streaming. | Low-medium | Vonage: $0.005-0.01/min + pipeline | High |
| SIP trunk + Asterisk + custom | Direct SIP connectivity. Full control. | Lowest | SIP: $0.005/min | Very high |

### Twilio Media Streams Integration

Key gotchas that aren't in the docs:

| Gotcha | What Happens | Fix |
|---|---|---|
| Audio format is mulaw 8kHz | Twilio sends 8kHz mulaw, not PCM16. STT expects 16kHz PCM. | Decode mulaw to PCM16 and upsample to 16kHz before sending to STT. |
| Bidirectional streaming has no AEC | Twilio doesn't provide echo cancellation on media streams | Implement server-side echo cancellation, or accept that agent's own audio may trigger STT |
| Media stream disconnects after 2 hours | Twilio enforces a 2-hour session limit on media streams | Implement session handoff: transfer call to new TwiML that reconnects media stream |
| Mark messages for sync | Twilio needs `mark` events to know when agent speech ends | Send `mark` event after each TTS chunk. Twilio fires `mark` callback when audio plays. Use this for barge-in timing. |
| Start event has call metadata | The `start` event contains `callSid`, `from`, `to` | Use `callSid` for session tracking. `from` for caller identification (ANI lookup). |

### Phone Number Provisioning

| Provider | Local Numbers | Toll-Free | International | A2P 10DLC Required |
|---|---|---|---|---|
| Twilio | $1/mo + usage | $2/mo + usage | Available in 100+ countries | Yes for US SMS (not required for voice-only) |
| Vapi | Included in plan or $2/mo | Available | Limited countries | Handled by Vapi |
| Retell AI | Included or pass-through | Available | Limited | Handled by Retell |
| Vonage | $1/mo + usage | $2/mo + usage | Available in 80+ countries | Yes for US SMS |

## WebRTC Integration Patterns

### Browser-Based Voice Agent

| Component | Options | Recommendation |
|---|---|---|
| Media capture | `getUserMedia` API | Always request `{ audio: { echoCancellation: true, noiseSuppression: true } }` |
| Transport | WebRTC (via LiveKit/Daily) or WebSocket | WebRTC if you need AEC. WebSocket if server-side only. |
| Client SDK | LiveKit JS SDK, Daily JS SDK, or custom WebSocket | LiveKit for complex (multi-participant). WebSocket for simple (1:1 agent). |
| Audio worklet | For custom audio processing in browser | Required for real-time audio manipulation (gain, noise gate) before sending |

### LiveKit Agents Framework

| Concept | What It Does | Key Detail |
|---|---|---|
| Agent | Server-side process that joins a LiveKit room | Written in Python. Receives audio tracks, sends audio tracks. |
| Room | Virtual space where participants connect | One room per conversation. Agent + user (+ optional observers). |
| STT plugin | Converts incoming audio track to text | Deepgram, Google, or OpenAI Whisper. Configured on agent. |
| LLM plugin | Generates response from transcript | OpenAI, Anthropic, or custom. Streaming required. |
| TTS plugin | Converts response text to audio track | ElevenLabs, Cartesia, or OpenAI TTS. Streaming required. |
| VAD plugin | Detects when user is speaking | Silero VAD (default). Configurable thresholds. |

**LiveKit gotcha**: Agent process runs on YOUR server, not LiveKit's. LiveKit handles only the media routing (SFU). Your server needs to run the agent process and connect to LiveKit Cloud or self-hosted LiveKit. Budget for agent server compute separately.

## External System Integration

### CRM Integration (During Calls)

| CRM | Integration Method | What to Fetch | Latency Impact |
|---|---|---|---|
| Salesforce | REST API with OAuth | Contact record, recent cases, opportunity stage | 200-500ms (pre-fetch on call start) |
| HubSpot | REST API with API key | Contact properties, deal stage, recent activities | 100-300ms |
| Zendesk | REST API | Ticket history, customer tier, CSAT score | 200-400ms |
| Custom CRM/DB | Direct database query or internal API | Whatever's relevant | 10-100ms (if co-located) |

**Pre-fetch rule**: Always fetch CRM data during the greeting/IVR phase, not when the user asks a question. By the time the user says "What's my order status?", you should already have their order history loaded.

### Knowledge Base Integration (RAG for Voice)

| Challenge | Why It's Harder in Voice | Solution |
|---|---|---|
| Retrieval latency | User hears silence while RAG queries run | Pre-fetch likely topics from first utterance. Cache top-5 relevant docs per caller intent category. |
| Long document results | Can't read a 500-word article aloud | Retrieve, then prompt LLM: "Using ONLY this context, answer in 1-2 spoken sentences: {context}" |
| Source attribution | Can't show footnotes in voice | "According to our [policy name], [brief answer]. Would you like me to send you the full details by email?" |
| Retrieval failure | RAG returns irrelevant results | Agent must say "I don't have specific information on that" rather than hallucinate from bad retrieval |

### Webhook and Event Integration

| Event | When to Fire | Payload |
|---|---|---|
| `call.started` | New voice session begins | session_id, caller_id, timestamp, channel (phone/web) |
| `call.ended` | Session terminates (any reason) | session_id, duration, end_reason (completed/timeout/error/transfer), turns_count |
| `intent.detected` | Agent classifies user intent | session_id, intent, confidence, utterance |
| `tool.called` | Agent invokes an external tool | session_id, tool_name, parameters, result_status |
| `escalation.triggered` | Agent hands off to human | session_id, reason, transcript_summary, unresolved_slots |
| `sentiment.negative` | Frustration detected | session_id, utterance, sentiment_score |

**Webhook reliability**: Use async webhook delivery with retry (3 attempts, exponential backoff). Voice sessions are real-time -- webhook delivery must not block the conversation. Fire-and-forget with a queue.

## Cost Estimation Framework

### Per-Minute Cost Breakdown

| Component | Typical Cost | Notes |
|---|---|---|
| Telephony (inbound) | $0.0085-0.02/min | Twilio, Vonage. Includes both legs. |
| STT (streaming) | $0.006-0.015/min | Deepgram Nova-2: $0.0059/min. Google: $0.012/min. |
| LLM (per turn) | $0.001-0.01/turn | Depends on model and context length. GPT-4o-mini: ~$0.001/turn. GPT-4o: ~$0.01/turn. |
| TTS (streaming) | $0.015-0.03/1K chars | ElevenLabs: $0.018/1K. OpenAI TTS: $0.015/1K. ~100 chars/sentence. |
| Platform hosting | $0-0.05/min | Vapi: $0.05/min. Self-hosted: compute cost only. |
| **Total (self-hosted pipeline)** | **$0.03-0.06/min** | Excludes compute. |
| **Total (hosted platform)** | **$0.08-0.20/min** | Includes platform markup. |

### Cost Optimization Strategies

| Strategy | Savings | Tradeoff |
|---|---|---|
| Use smaller LLM for simple tasks (GPT-4o-mini, Claude Haiku) | 5-10x LLM cost reduction | Slightly lower quality on complex reasoning |
| Cache common responses (greeting, hold messages, confirmations) | Eliminates TTS cost for cached audio | Only works for deterministic responses |
| Use Deepgram over Google/OpenAI for STT | 40-60% STT cost reduction | Slightly different accuracy profile |
| Reduce average call duration (better conversation design) | Linear cost reduction | Requires conversation optimization effort |
| Negotiate volume discounts (>100K min/month) | 20-40% across providers | Requires commitment |

### ROI Calculation for Voice Agent Deployment

| Metric | How to Calculate | Typical Range |
|---|---|---|
| Cost per resolved call (agent) | Total monthly voice agent cost / calls resolved without human | $0.50-3.00 |
| Cost per resolved call (human) | Agent salary + tools + overhead / calls handled per month | $5.00-15.00 |
| Containment rate | Calls resolved by agent / total calls | 40-70% for well-designed agents |
| Cost savings | (Human cost - Agent cost) * contained calls per month | 60-80% reduction on contained calls |
| Breakeven volume | Platform fixed costs / (human cost per call - agent cost per call) | Usually 500-2000 calls/month |
