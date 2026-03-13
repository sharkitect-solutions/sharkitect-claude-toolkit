# Voice & IVR Implementation Patterns

Load when building voice features with Twilio Programmable Voice, designing IVR flows, implementing call recording, or troubleshooting voice call issues.

## IVR Architecture Patterns

### Pattern 1: Simple Auto-Attendant

```
Incoming Call -> Welcome Message -> Gather Input -> Route to Department
                                                 -> 1: Sales (queue or forward)
                                                 -> 2: Support (queue or forward)
                                                 -> 3: Billing (queue or forward)
                                                 -> No input: Repeat or operator
```

| Design Rule | Why |
|---|---|
| Maximum 4 menu options per level | Each additional option after 4 reduces completion rate by 10% (Genesys research) |
| Announce the action before the number | "For sales, press 1" not "Press 1 for sales" -- callers hear the option before the action |
| Include "press 0 for operator" on every level | Callers who can't navigate IVR will hang up if there's no escape hatch |
| Set `<Gather>` timeout to 5 seconds | Shorter timeout frustrates slow callers. Longer timeout wastes everyone's time. |
| Play a brief hold message before queueing | Silence after selection makes callers think the call dropped |

### Pattern 2: Conversational IVR (Speech Recognition)

| Setting | Recommended Value | Why |
|---|---|---|
| `input` attribute | `dtmf speech` | Accept both keypad and voice for accessibility |
| `speechTimeout` | `auto` | Twilio detects end of speech automatically -- better than fixed timeout |
| `speechModel` | `phone_call` for IVR, `default` for general | `phone_call` is optimized for telephony audio quality |
| `language` | Match caller locale | Mismatched language model drastically reduces recognition accuracy |
| `hints` | Comma-separated expected phrases | "sales, support, billing, cancel, representative" -- dramatically improves accuracy for known intents |

**Speech recognition gotcha**: Twilio's speech recognition is NOT a substitute for NLU. It transcribes speech to text but doesn't understand intent. For complex conversational IVR, pipe the transcription to your own NLU (Dialogflow, Lex, or custom) and return TwiML based on the interpreted intent.

### Pattern 3: Queue-Based Call Center

| Component | TwiML / API | Key Configuration |
|---|---|---|
| Place caller in queue | `<Enqueue>` with queue name | Set `waitUrl` for hold music/messages. Don't use silence -- callers hang up. |
| Agent connects | `<Dial><Queue>` to dequeue next caller | Agent's phone or client receives the dequeued call |
| Queue position announcement | `waitUrl` TwiML with `<Say>` | "You are caller number 3. Estimated wait: 4 minutes." Update every 30 seconds. |
| Queue overflow | Check queue size via REST API | If queue depth > 15, offer callback option instead of wait |
| Callback implementation | Record number + position, hang up, call back when agent available | Use TaskRouter for sophisticated routing; simple callback = `<Record>` + scheduled outbound call |

**Queue hold music rule**: Silence causes 50% of callers to hang up within 60 seconds. Music with periodic position updates retains callers 3x longer (Genesys). Update queue position every 30 seconds.

## TwiML Deep Patterns

### Gather with Fallback Chain

| Attempt | TwiML Behavior | After Timeout/Invalid |
|---|---|---|
| 1st attempt | Normal prompt: "Press 1 for sales, 2 for support" | Repeat with simpler wording |
| 2nd attempt | Simplified: "Press 1 or 2" | Offer operator |
| 3rd attempt | "Please hold for a representative" | Route to default agent |

**Implementation**: Use the `action` URL on `<Gather>` to track attempt count via URL parameter: `/ivr/menu?attempt=1`, `/ivr/menu?attempt=2`, etc. Remember: TwiML is stateless -- you must pass state through URLs or external storage.

### Conference Call Patterns

| Feature | TwiML | Gotchas |
|---|---|---|
| Basic conference | `<Dial><Conference>room-name</Conference></Dial>` | Conference name is global to your account -- use unique names (UUID or user-scoped) |
| Moderator controls | `startConferenceOnEnter="true"` on moderator, `"false"` on participants | Participants hear hold music until moderator joins |
| Recording | `record="record-from-start"` on the `<Conference>` tag | Recording starts when conference starts, not when first participant joins. Announce recording for legal compliance. |
| Max participants | `maxParticipants="10"` (default 250) | Set a limit to prevent accidental large conferences. Billing is per-participant-per-minute. |
| Mute on entry | `muted="true"` on participant `<Dial>` | For webinar-style calls where only moderator speaks |
| Coaching/whisper | `coach="call-sid-of-agent"` | Supervisor can speak to agent without caller hearing -- useful for training |

**Conference billing gotcha**: Twilio bills per participant per minute, not per conference per minute. A 10-person, 30-minute conference = 300 participant-minutes billed, not 30 minutes.

### Call Recording

| Recording Type | How | Storage | Access |
|---|---|---|---|
| Full call recording | `record="true"` on `<Dial>` | Twilio cloud (30-day default retention) | Via REST API or Console |
| Conference recording | `record="record-from-start"` on `<Conference>` | Same | Same |
| Voicemail recording | `<Record maxLength="120" action="/handle-recording">` | Same | Callback to `action` URL with recording URL |
| Dual-channel recording | `recordingChannels="dual"` on `<Dial>` | Same | Each participant on separate audio channel -- critical for analytics |

| Recording Compliance | Requirement |
|---|---|
| One-party consent states (most US states) | One party (your agent) knowing is sufficient |
| Two-party consent states (CA, FL, IL, PA, WA, +8 more) | MUST announce recording. "This call may be recorded for quality assurance." |
| GDPR (EU) | Explicit consent required. Purpose must be stated. Right to request deletion. |
| PCI DSS | Pause recording during credit card number entry. Use `<Pause>` to stop recording or Twilio's "pause" REST API. |

**Recording announcement gotcha**: "This call may be recorded" is NOT sufficient for two-party consent states. The announcement must occur BEFORE any conversation starts. Place the `<Say>` announcement as the first TwiML verb, before `<Dial>` or `<Gather>`.

## Voice Quality Troubleshooting

| Issue | Diagnosis | Fix |
|---|---|---|
| One-way audio (caller hears, agent doesn't or vice versa) | NAT/firewall blocking UDP traffic | Ensure ports 10000-60000 UDP are open for Twilio media. Use TURN relay if behind strict firewall. |
| Echo on calls | Audio feedback loop between speaker and microphone | Enable acoustic echo cancellation on client. Reduce speaker volume. Use headset instead of speakerphone. |
| Choppy/robotic audio | Packet loss or jitter on network | Check network quality: jitter <30ms, packet loss <1%, latency <150ms one-way. Use wired connection over WiFi. |
| Long silence before connection | DNS resolution or TLS handshake delay | Pre-warm connections. Use Twilio edge locations closest to your server. Check `<Dial>` timeout setting. |
| TTS sounds unnatural | Default voice is basic | Use Amazon Polly voices via `<Say voice="Polly.Joanna">` for more natural speech. Or use `<Play>` with pre-recorded audio for critical messages. |
| Background noise on calls | Microphone picking up ambient sound | Enable noise suppression on Twilio Client SDK. Use `<Stream>` with server-side noise cancellation for critical applications. |

## Outbound Call Patterns

### Click-to-Call Architecture

```
User clicks "Call" in your app
  -> Your server calls Twilio REST API to create outbound call to user's phone
  -> User answers, TwiML plays greeting
  -> TwiML <Dial>s the business number
  -> Both parties connected
```

| Design Decision | Recommendation | Why |
|---|---|---|
| Who calls whom | Server calls the customer first, then dials the business | Customer experiences a normal incoming call. Business line is only connected after customer answers. |
| Caller ID on outbound | Use your verified Twilio number | Unverified caller IDs are blocked by carriers. STIR/SHAKEN attestation requires verified numbers. |
| No-answer handling | Set `timeout="30"` and `action="/no-answer"` | After 30 seconds, trigger voicemail or callback scheduling |
| Busy signal | Check `CallStatus` in status callback | `busy` = retry in 5 minutes. `no-answer` = try alternate number or offer callback. |

### Call Status Tracking

| CallStatus | Meaning | Action |
|---|---|---|
| `initiated` | Twilio is placing the call | No action |
| `ringing` | Destination phone is ringing | Start timeout counter |
| `in-progress` | Call connected and active | Log start time for duration tracking |
| `completed` | Call ended normally | Log duration and outcome |
| `busy` | Destination busy | Retry once after 5 minutes |
| `no-answer` | No answer after timeout | Offer callback or try alternate number |
| `failed` | Call failed (wrong number, carrier error) | Check ErrorCode; suppress if invalid number |
| `canceled` | Caller hung up before connection | Log as abandoned call |

## STIR/SHAKEN and Call Authentication

| Concept | What It Means | Impact |
|---|---|---|
| STIR/SHAKEN | Caller ID authentication framework mandated by FCC (2021) | Calls without attestation are flagged as "Spam Likely" or blocked by carriers |
| Attestation levels | A (full): you own the number. B (partial): you're authorized. C (gateway): no verification. | A-level gets through. C-level is frequently blocked. Twilio numbers get A attestation. |
| Branded calling | Your business name appears on caller ID instead of number | Register with Twilio's Branded Calls (currently invite-only) for higher answer rates |

**STIR/SHAKEN gotcha**: If you use `callerId` parameter with a number you don't own on Twilio, attestation drops to C level (gateway). Carriers increasingly block C-level calls. Always use a Twilio number you own as the caller ID.
