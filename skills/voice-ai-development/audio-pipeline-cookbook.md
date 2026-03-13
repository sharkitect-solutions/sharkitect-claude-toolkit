# Audio Pipeline Cookbook

Load when implementing audio processing, format conversion, VAD tuning, or buffering in a voice pipeline.

## Audio Format Reference

### Sample Rate Compatibility Matrix

| Source/Destination | 8kHz | 16kHz | 22.05kHz | 24kHz | 44.1kHz | 48kHz |
|-------------------|------|-------|----------|-------|---------|-------|
| Telephone (PSTN) | Native | -- | -- | -- | -- | -- |
| Deepgram STT input | Supported | Optimal | Supported | Supported | Supported | Supported |
| Deepgram Aura TTS output | -- | Available | -- | Default | -- | Available |
| OpenAI Realtime | -- | -- | -- | Required | -- | -- |
| ElevenLabs TTS output | -- | Available | Legacy | Available | Available | -- |
| Browser MediaRecorder | -- | -- | -- | -- | -- | Default (Opus) |
| WebRTC (default) | -- | -- | -- | -- | -- | Default |

### Resampling Decision

| Scenario | Action | Latency Cost | Quality Impact |
|----------|--------|-------------|----------------|
| 16kHz -> 24kHz (Deepgram to OpenAI) | Upsample with linear interpolation | 2-5ms | Minimal -- no new information, but compatible |
| 24kHz -> 16kHz (OpenAI to Deepgram) | Downsample with anti-alias filter | 2-5ms | Slight high-frequency loss. Acceptable for speech. |
| 48kHz -> 16kHz (WebRTC to Deepgram) | Downsample with proper anti-alias | 3-8ms | Good. Removes unnecessary bandwidth for speech. |
| 8kHz -> 16kHz (phone to Deepgram) | Upsample | 1-3ms | No quality improvement. Phone audio stays narrowband. |
| Any -> any without anti-alias filter | DON'T | -- | Aliasing artifacts. Metallic/distorted sound. |

**Rule**: Always apply a low-pass filter before downsampling. Without it, frequencies above the Nyquist limit fold back as audible artifacts. For speech, a 4th-order Butterworth at 0.45x target sample rate works well.

### PCM16 Format Specification

The universal interchange format for voice AI pipelines:
- Encoding: signed 16-bit integer, little-endian
- Range: -32768 to 32767
- Channels: mono (single channel)
- No header (raw bytes) -- container format (WAV) adds 44-byte header
- Byte rate: sample_rate * 2 bytes/sample (16kHz = 32KB/sec, 24kHz = 48KB/sec)

**Common mistake**: Sending WAV-wrapped PCM to APIs expecting raw PCM. The 44-byte WAV header gets interpreted as audio, producing a click/pop at the start. Strip the header or use the provider's WAV-aware endpoint.

## VAD (Voice Activity Detection) Tuning Guide

### Parameter Reference

| Parameter | Range | Default | Effect |
|-----------|-------|---------|--------|
| `threshold` (speech probability) | 0.0 - 1.0 | 0.5 | Higher = more confident speech detection. Lower = more sensitive but more false triggers. |
| `min_speech_duration_ms` | 50 - 500 | 250 | Minimum speech segment length. Filters very short sounds (clicks, pops). |
| `min_silence_duration_ms` (silence_duration_ms) | 100 - 2000 | 500 | Silence required to end an utterance. THE most impactful parameter for turn-taking speed. |
| `prefix_padding_ms` | 0 - 500 | 300 | Audio retained BEFORE speech detection trigger. Captures the first syllable. |
| `max_speech_duration_s` | 5 - 300 | 30 | Maximum single utterance length. Safety limit to prevent infinite speech detection. |

### Tuning by Environment

| Environment | threshold | min_silence_ms | prefix_padding_ms | Notes |
|-------------|-----------|---------------|-------------------|-------|
| Quiet room (headset) | 0.5 | 300 | 200 | Standard settings. Reliable performance. |
| Quiet room (speaker) | 0.6 | 400 | 300 | Higher threshold avoids echo-triggered false starts |
| Office (open plan) | 0.7 | 400 | 300 | Background voices cause false triggers at lower thresholds |
| Car (hands-free) | 0.75 | 500 | 400 | Road noise + engine. Need aggressive filtering. |
| Phone (narrowband) | 0.5 | 400 | 300 | Compression artifacts make VAD less reliable. Longer silence prevents mid-word cutoffs. |
| Mobile (outdoor) | 0.7 | 500 | 400 | Wind noise is the primary enemy. Consider noise gate before VAD. |

### VAD Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| First syllable clipped ("ello" instead of "Hello") | `prefix_padding_ms` too low | Increase to 300-400ms |
| Bot responds mid-sentence (user still talking) | `min_silence_ms` too low | Increase to 500-700ms. Trade-off: slower turn-taking. |
| Bot never responds (thinks user is still talking) | `min_silence_ms` too high, or threshold too low (background noise reads as speech) | Decrease `min_silence_ms` or increase `threshold` |
| Double triggers (responds, then responds again) | Utterance split by brief pause | Increase `min_silence_ms` to bridge natural pauses |
| Triggered by keyboard typing | `threshold` too low | Increase to 0.7+. Add noise gate as preprocessing. |
| Triggered by bot's own audio (echo) | Missing echo cancellation | Use WebRTC (built-in AEC) or add software AEC before VAD |

## Audio Preprocessing Chain

Apply these in order before sending audio to STT. Each step is optional but cumulative quality improvement is significant.

| Step | What It Does | When to Apply | Implementation |
|------|-------------|---------------|----------------|
| 1. Noise gate | Silence audio below amplitude threshold | Always (especially non-headset) | Threshold: -40dB. Attack: 1ms. Release: 50ms. |
| 2. High-pass filter | Remove low-frequency rumble (AC hum, traffic) | Always | Cutoff: 80Hz. 2nd order Butterworth. |
| 3. Gain normalization | Bring audio to consistent level | When users have varying mic volumes | Target: -3dBFS peak. Compressor ratio 3:1. |
| 4. Noise reduction | Spectral subtraction of stationary noise | Noisy environments only | Sample 500ms of "silence" at start for noise profile. |
| 5. Resample | Convert to target sample rate | When source != target rate | Always with anti-alias filter. Never truncate. |

**Preprocessing latency budget**: Steps 1-3 add <5ms total (simple DSP). Step 4 adds 10-30ms (FFT-based). Step 5 adds 2-8ms. Total: 17-43ms. Worth it if STT accuracy improves by >5%.

## Buffering Strategies

### Jitter Buffer for Audio Playback

| Network Type | Buffer Size | Trade-off |
|-------------|-------------|-----------|
| Local/LAN | 20ms | Minimal latency, no protection against jitter |
| WiFi (stable) | 40ms | Good balance for typical home/office WiFi |
| WiFi (congested) | 80ms | Handles packet reordering and brief drops |
| 4G mobile | 100ms | Mobile networks have 50-100ms jitter baseline |
| 3G / poor connection | 200ms | Maximum recommended. Beyond this, latency is worse than occasional glitches. |

### Audio Chunk Sizing

| Pipeline Stage | Chunk Size | Why |
|---------------|------------|-----|
| Microphone capture | 20ms (320 samples at 16kHz) | WebRTC standard. Matches Opus frame size. |
| STT streaming | 100ms (1600 samples at 16kHz) | Most STT APIs process in 100ms windows. Smaller chunks waste HTTP overhead. |
| TTS streaming output | Variable (sentence-aligned) | TTS outputs variable-length chunks at sentence boundaries. Buffer and play smoothly. |
| WebSocket send | 20-40ms chunks | Balance between latency (small chunks) and overhead (large chunks). |

### Buffer Underrun Recovery

When playback buffer empties (network stall or slow TTS):
1. Play silence (not noise) to maintain audio stream continuity
2. Log the underrun event with timestamp and duration
3. When audio resumes, do NOT speed up to "catch up" -- this sounds unnatural
4. If underruns happen >3 times per minute, increase jitter buffer size
5. If persistent, the pipeline stage before playback is the bottleneck -- investigate TTS latency or network

## Echo Cancellation Decision

| Setup | AEC Strategy | Implementation |
|-------|-------------|----------------|
| WebRTC connection (browser) | Built-in. Enable `echoCancellation: true` in getUserMedia constraints. | Automatic. Do nothing extra. |
| WebRTC connection (mobile app) | Platform AEC (iOS/Android handle this). | Enable in audio session config. Test on physical devices. |
| WebSocket audio (browser speakers) | No built-in AEC. Bot hears its own output. | Option A: Use WebRTC for transport instead. Option B: Software AEC (SpeexDSP). Option C: Headphones-only constraint. |
| WebSocket audio (server-side agent) | No AEC needed -- server doesn't have speakers. | N/A. But if agent plays audio back through the same channel, cancel it in software. |
| Phone (PSTN via Twilio/Vapi) | Carrier handles AEC. | Automatic. Twilio's media stream has AEC applied. |

**Critical rule**: If using WebSocket transport with speaker playback and no AEC, the bot WILL trigger on its own voice. This is the #1 cause of "bot talks to itself" loops. There is no software workaround as reliable as WebRTC's built-in AEC. Switch transport if possible.

## Codec Decision Guide

| Codec | Use Case | Bitrate | Latency | Browser Support |
|-------|----------|---------|---------|-----------------|
| PCM16 (raw) | Provider APIs, server-to-server | 256kbps (16kHz) | Zero (uncompressed) | Via AudioWorklet only |
| Opus | WebRTC, browser capture, low bandwidth | 16-128kbps (variable) | 5-20ms encode/decode | All modern browsers |
| MP3 | Cached audio, non-realtime playback | 128-320kbps | 50-100ms encode | All browsers |
| AAC | iOS Safari MediaRecorder default | 64-256kbps | 20-40ms | Safari, Chrome |
| Mulaw/Alaw | Telephone (PSTN) | 64kbps (8kHz) | Zero (simple transform) | Not natively |

**Codec rule for real-time voice**: Use Opus for browser-to-server. Use PCM16 for server-to-provider. Never use MP3 for real-time -- the encode latency alone exceeds your budget. If you see MP3 in a real-time pipeline, it's a design error.
