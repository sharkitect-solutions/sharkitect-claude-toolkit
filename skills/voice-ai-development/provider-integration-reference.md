# Voice AI Provider Integration Reference

Load when connecting to a specific voice AI provider or troubleshooting provider-specific issues.

## Provider Connection Patterns

### OpenAI Realtime API

| Parameter | Value | Gotcha |
|-----------|-------|--------|
| Endpoint | `wss://api.openai.com/v1/realtime` | WebSocket only -- no HTTP REST for streaming audio |
| Auth | `Authorization: Bearer sk-...` header on WebSocket upgrade | Token exposed in browser WebSocket -- use server-side proxy in production |
| Audio input format | PCM16, 24kHz, mono | Sending 16kHz audio works but quality degrades. Resample UP before sending. |
| Audio output format | PCM16, 24kHz, mono | Must downsample if your playback chain expects 16kHz (Deepgram default) |
| Session config | Send `session.update` event after connection | Must configure voice, modalities, tools BEFORE sending audio. Late config causes session reset. |
| Turn detection | Server VAD (default) or manual `input_audio_buffer.commit` | Server VAD adds 200-300ms to detect end-of-speech. Manual commit gives faster turns but requires client-side VAD. |
| Interruption handling | Send `response.cancel` then `input_audio_buffer.clear` | Order matters: cancel first, then clear. Reversed order causes stale audio in buffer. |
| Cost model | $0.06/min audio input, $0.24/min audio output (as of 2025) | Audio output 4x more expensive than input. Long TTS responses cost significantly more than STT. |
| Session timeout | 15 minutes idle, 30 minutes max | No keepalive mechanism. Reconnect and restore conversation context on timeout. |
| Transcription | Set `input_audio_transcription` in session config | Transcription is optional and adds latency. Only enable if you need text logs of audio input. |

### Deepgram

| Feature | STT (Nova-2) | TTS (Aura) |
|---------|-------------|------------|
| Protocol | WebSocket streaming or REST batch | WebSocket streaming or REST |
| Auth | `Authorization: Token dg-...` header | Same token for both services |
| Input format (STT) | Linear16/PCM16 at 8/16/24/48kHz, or Opus, FLAC, MP3 | N/A |
| Output format (TTS) | N/A | Linear16 at 24kHz (default), MP3, Opus, FLAC, AAC, Mulaw |
| Streaming latency | 100-200ms for interim results, 200-400ms for final | 80-150ms first byte |
| Key parameters | `model=nova-2`, `language=en`, `smart_format=true`, `utterances=true` | `model=aura-asteria-en` (female), `aura-orion-en` (male) |
| Endpointing | `endpointing=300` (ms of silence before utterance end) | N/A |
| Interim results | `interim_results=true` for real-time partial transcripts | N/A |
| Diarization | `diarize=true` -- adds 100-200ms latency, max 4 speakers | N/A |
| Keepalive | Send `{"type": "KeepAlive"}` JSON every 8 seconds | Same keepalive pattern |
| Reconnection | WebSocket drops after 1 hour. Must reconnect and re-send config. | Same behavior |

**Deepgram-specific gotcha**: `smart_format=true` converts numbers, currency, and dates to written form ("twenty dollars" -> "$20"). This is usually desired for display but can confuse LLMs that expect the spoken form. Disable for LLM-consumed transcripts.

### ElevenLabs

| Parameter | Value | Gotcha |
|-----------|-------|--------|
| Streaming endpoint | `wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input` | voice_id is NOT the voice name. Lookup via `/v1/voices` API first. |
| Auth | `xi-api-key` header on WebSocket upgrade | API key scoping: some keys are org-wide, others per-project. Check key permissions if 403. |
| Input | Text chunks (JSON with `text` field) | Send text in sentence-sized chunks. Sending word-by-word produces choppy prosody. |
| Output format | PCM16/MP3/Opus, configurable `output_format` parameter | Default is MP3. For real-time pipelines, use `pcm_24000` (PCM16 at 24kHz) to avoid decode overhead. |
| Flush signal | Send `{"text": ""}` empty text to flush remaining audio | Without flush, last sentence may stay buffered on server until timeout. |
| Close signal | Send `{"text": ""}` with empty string, then close WebSocket | Closing WebSocket without flush loses the final audio chunk. |
| Latency modes | `optimize_streaming_latency=4` (max speed, slight quality loss) | Values 0-4. Default 0 = best quality but 200-300ms first byte. Value 4 = ~100ms but noticeable quality drop on long sentences. |
| Voice cloning | Professional cloning needs 30+ min clean audio. Instant cloning needs 30 seconds. | Instant clones degrade on emotional range and long-form. Professional clones are worth the effort for production. |
| Pronunciation | Use `<phoneme>` SSML tags or pronunciation dictionaries | Global pronunciation dictionaries apply across all requests -- test carefully before deploying org-wide. |

### LiveKit

| Aspect | Detail | Gotcha |
|--------|--------|--------|
| Architecture | Open-source SFU server + agent framework | Server must be self-hosted or use LiveKit Cloud. No serverless option. |
| Agent SDK | Python (`livekit-agents`) and Node.js | Python SDK is more mature. Node.js SDK has fewer built-in plugins. |
| Audio transport | WebRTC (browser) or direct track subscription (server) | WebRTC handles echo cancellation, jitter buffer automatically. Server-side agents skip these -- add manually if needed. |
| STT plugin | `livekit-plugins-deepgram`, `livekit-plugins-google` | Plugin wraps provider API. Still need provider API key. |
| TTS plugin | `livekit-plugins-elevenlabs`, `livekit-plugins-cartesia` | Cartesia plugin has lower latency than ElevenLabs plugin due to streaming differences. |
| LLM plugin | `livekit-plugins-openai` | Wraps OpenAI API. Does NOT use Realtime API -- pipes text through chat completions. |
| Room topology | One room per conversation. Agent joins as participant. | Multiple agents in one room cause echo. Use separate tracks or mute non-speaking agents. |
| Deployment | Docker container + Redis for multi-instance | Redis required for agent dispatch across multiple server instances. Single instance works without Redis. |

### Vapi

| Aspect | Detail | Gotcha |
|--------|--------|--------|
| Architecture | Fully hosted. Configure via API, receive events via webhook. | Zero infrastructure to manage. Trade-off: limited pipeline control. |
| Pricing | Per-minute. Includes STT + LLM + TTS + infrastructure. | More expensive per minute than self-hosted at scale (>5K min/month). Cheaper below that. |
| Custom LLM | Point `serverUrl` to your endpoint. Vapi sends transcripts, expects LLM response. | Your endpoint must respond within 5 seconds or Vapi falls back to configured default. |
| Phone integration | Built-in Twilio/Vonage integration. Assign phone numbers in dashboard. | Phone audio is narrowband (8kHz). STT accuracy drops vs wideband (16kHz+). Adjust VAD sensitivity. |
| Function calling | Vapi handles tool/function calls. Define tools in assistant config. | Async tool calls (database lookups, API calls) must return within 20 seconds. Vapi plays filler audio while waiting. |
| Interruption | Configured per assistant: `backchannelingEnabled`, `silenceTimeoutSeconds` | `silenceTimeoutSeconds` too low (< 5) causes premature hangup on users who pause to think. Default 30 is too high for most cases. Set to 10-15. |

## Cost Comparison Matrix

| Provider | STT Cost | TTS Cost | Total (1K min/mo) | Total (50K min/mo) | Best For |
|----------|----------|----------|--------------------|--------------------|----------|
| OpenAI Realtime | Included | Included | ~$300 | ~$15,000 | Prototypes, single-provider simplicity |
| Deepgram Nova-2 + Aura | $0.0043/min | $0.015/min | ~$20 | ~$1,000 | Cost-sensitive, high volume |
| Deepgram + ElevenLabs | $0.0043/min | $0.30/1K chars (~$0.09/min) | ~$95 | ~$4,700 | Best voice quality at moderate cost |
| Vapi (hosted) | Included | Included | ~$150 | ~$6,000 | Zero infrastructure, phone bots |
| LiveKit (self-hosted) + providers | Provider costs only | Provider costs only | Compute + ~$20 | Compute + ~$1,000 | Full control, custom pipelines |

**Cost gotcha**: ElevenLabs charges per character, not per minute. Verbose LLM responses cost significantly more. Constrain LLM output length (max_tokens or system prompt instruction) to control TTS costs.

## Authentication Patterns by Provider

| Provider | Auth Method | Token Rotation | Rate Limit Headers |
|----------|------------|----------------|-------------------|
| OpenAI | Bearer token in WS upgrade header | Manual. Rotate via dashboard. | `x-ratelimit-remaining-requests`, `x-ratelimit-remaining-tokens` |
| Deepgram | `Authorization: Token dg-...` | API key management via console. Scoped keys available. | `x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-reset` |
| ElevenLabs | `xi-api-key` header | Manual rotation. Per-project keys available on Pro plan. | `xi-ratelimit-limit`, `xi-ratelimit-remaining`, `xi-ratelimit-reset` |
| LiveKit | Server-side API key + secret for room management. Client gets short-lived JWT. | JWT expiry controls access. Rotate API key/secret pair via dashboard. | N/A (self-hosted, you control limits) |
| Vapi | Bearer token for API calls. Webhook secret for event verification. | API key rotation in dashboard. Webhook secret separate. | Standard HTTP 429 with retry-after header |

**Security rule**: Never expose provider API keys to browser clients. All provider connections should go through your server. The only exception is LiveKit client SDK which uses short-lived JWTs (not the API key itself).
