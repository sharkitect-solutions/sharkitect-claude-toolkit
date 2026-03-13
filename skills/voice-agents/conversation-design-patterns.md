# Conversation Design Patterns for Voice Agents

Load when designing multi-turn voice conversations, implementing turn-taking strategies, or building dialogue flows for voice agents.

## Turn-Taking Architecture

### Turn State Machine

Every voice conversation is a state machine with these states:

| State | Description | Transitions |
|---|---|---|
| LISTENING | Agent microphone open, waiting for user speech | -> PROCESSING (on utterance end) or -> INTERRUPTED (on timeout) |
| PROCESSING | STT complete, LLM generating response | -> SPEAKING (on first TTS chunk) or -> LISTENING (on empty response) |
| SPEAKING | Agent TTS playing audio to user | -> LISTENING (on TTS complete) or -> BARGE_IN (on user speech detected) |
| BARGE_IN | User interrupted agent speech | -> LISTENING (TTS cancelled, agent yields) |
| INTERRUPTED | Timeout or error during any state | -> LISTENING (with recovery prompt) or -> ENDED (on max retries) |
| ENDED | Conversation terminated | Terminal state |

### Turn-Taking Failure Modes

| Failure | What Happens | Root Cause | Fix |
|---|---|---|---|
| Agent talks over user | Agent starts responding before user finishes | VAD end-of-turn trigger too aggressive (short silence threshold) | Increase silence threshold to 1.2-2.0s. Add semantic completeness check. |
| Double-response | Agent responds, then responds again to silence | TTS audio picked up by microphone, processed as new utterance | Enable AEC. If AEC is on, check that the agent mutes input during TTS playback. |
| Infinite silence | Neither agent nor user speaks, conversation stalls | Missing silence timeout handler | Implement 5-8 second silence prompt: "Are you still there?" Max 2 prompts before graceful end. |
| Conversation ping-pong | Agent gives one-word responses, user gives one-word responses | LLM not prompted for conversational depth | System prompt: "Ask follow-up questions. Don't just acknowledge." |
| Premature handoff | Agent transfers to human too quickly | Confidence threshold too low or handoff triggers too broad | Require 2+ failed attempts before handoff. Log the trigger for tuning. |

## Multi-Turn Context Management

### Context Window Strategy for Voice

| Approach | When to Use | Tradeoff |
|---|---|---|
| Full transcript in context | <10 turns, low token budget | Simple but context grows linearly. LLM slows as context grows. |
| Rolling window (last N turns) | 10-30 turns, general conversation | Loses early context. User says "go back to what you said earlier" and agent can't. |
| Summary + recent turns | >30 turns or long sessions | Add a summary of turns 1-N every 10 turns. Keep last 5 turns verbatim. Best balance. |
| Slot-filling (structured state) | Form-fill or data collection tasks | Extract named slots (name, date, amount) from each turn. Discard raw transcript. Most token-efficient. |

### Slot-Filling Pattern

For conversations that collect structured data (booking, intake forms, customer service):

| Component | What It Does | Implementation Detail |
|---|---|---|
| Slot schema | Defines what data needs to be collected | JSON schema with required/optional fields, types, validation rules |
| Extraction prompt | LLM extracts slot values from user utterance | "Given the user said: '{utterance}', extract values for these fields: {unfilled_slots}" |
| Confirmation strategy | Verify extracted values before proceeding | Implicit confirmation (repeat back naturally) for low-stakes. Explicit confirmation ("Is that correct?") for high-stakes (payments, medical). |
| Correction handling | User says "no, I said Tuesday not Thursday" | Re-extract the corrected slot. Don't re-ask the entire form. |
| Completion check | Are all required slots filled? | Check after each turn. When complete, summarize all values and confirm before action. |

### Context Injection Points

Where to inject external data into the voice conversation:

| Injection Point | What to Inject | Timing |
|---|---|---|
| System prompt (static) | Agent persona, business rules, compliance requirements | Before conversation starts |
| System prompt (dynamic) | Customer profile, order history, account status | After caller identified (ANI lookup, account number) |
| Mid-conversation retrieval | Knowledge base articles, product details, policy documents | When user asks a question the LLM can't answer from context alone |
| Tool call results | API responses, database lookups, calculations | After LLM decides to call a tool |

**Latency rule**: Dynamic context injection adds latency. Pre-fetch likely-needed context (customer profile, recent orders) during the greeting. Don't wait until the user asks.

## Voice Agent Persona Design

### Persona Calibration Matrix

| Dimension | Formal (Bank, Healthcare) | Professional (B2B Support) | Friendly (Consumer App) | Casual (Entertainment, Social) |
|---|---|---|---|---|
| Greeting | "Thank you for calling [Company]. How may I assist you?" | "Hi, this is [Agent] from [Company]. How can I help?" | "Hey! What can I help you with?" | "What's up? What do we want to do?" |
| Sentence length | 15-25 words max per sentence | 10-20 words | 8-15 words | 5-12 words |
| Filler words | Never | Rarely | Occasionally ("Sure", "Got it") | Frequently ("Cool", "Awesome", "No worries") |
| Error recovery | "I apologize. Could you please repeat that?" | "Sorry, I didn't catch that. Could you say that again?" | "Oops, I missed that. Say again?" | "My bad, one more time?" |
| Thinking time | "One moment please" (silence acceptable) | "Let me check on that" (brief pause OK) | "Hmm, let me look..." (filler preferred over silence) | "Hold on..." (filler required, silence feels broken) |
| Escalation | "I'll transfer you to a specialist" | "Let me connect you with someone who can help" | "I'm going to get you to a real person who can sort this out" | "Gonna get you to someone, hang tight" |

### Voice Prompt Engineering

| Rule | Why | Bad Example | Good Example |
|---|---|---|---|
| Constrain response length | Voice responses over 3 sentences feel like lectures | "Respond helpfully" | "Respond in 1-2 sentences. Be concise. This will be spoken aloud." |
| Forbid visual formatting | LLM will output lists, markdown, URLs that can't be spoken | No instruction about format | "Never use bullet points, numbered lists, URLs, or markdown. Speak in natural sentences." |
| Specify pronunciation | Names, acronyms, and numbers need spoken forms | No instruction | "Say phone numbers digit by digit with pauses. Spell out acronyms unless commonly spoken (e.g., 'NASA' is fine, 'API' should be 'A-P-I')." |
| Handle "I don't know" | LLM will hallucinate rather than admit ignorance | No instruction | "If you don't know the answer, say so. Never guess at specific numbers, dates, or policy details." |
| Prohibit self-reference | LLM references being an AI, which breaks immersion | No instruction | "Never say 'As an AI' or reference your nature. You are [Agent Name], a [role] at [Company]." |

## Tool Calling in Voice Context

### Voice-Specific Tool Calling Challenges

| Challenge | Why It's Worse in Voice | Solution |
|---|---|---|
| Tool execution latency | User hears silence during tool calls. >2s silence = "is this thing broken?" | Play a filler phrase before tool execution: "Let me check that for you." Stream filler TTS while tool runs. |
| Parallel tool calls | Multiple sequential API calls compound latency | Batch-resolve: identify all needed tools from the utterance, call in parallel, respond with combined result. |
| Tool call failure | User can't see error messages or retry buttons | Agent must verbally recover: "I'm having trouble looking that up. Can you give me a moment?" Retry once silently. If still failing, offer alternative or escalation. |
| Confirmation before action | Destructive actions (cancel order, delete account) need verbal confirmation | Two-step: "I'm going to cancel order #4521. That's $49.99 back to your card ending in 3456. Should I go ahead?" Wait for explicit "yes." |
| Result presentation | Can't show a table or list of 10 items verbally | Summarize: "I found 3 upcoming appointments. The next one is Tuesday at 2pm with Dr. Smith. Want to hear the others?" |

### Tool Call Filler Strategy

| Tool Expected Duration | Filler Strategy | Example |
|---|---|---|
| <500ms | No filler (silence acceptable) | -- |
| 500ms - 2s | Brief acknowledgment before tool call | "Let me pull that up." |
| 2s - 5s | Acknowledgment + context | "I'm looking up your order history. Just a moment." |
| >5s | Acknowledgment + progress update + music/hold | "This might take a moment. I'm checking across our systems..." (then humming/hold music if available) |

## Conversation Recovery Patterns

| Scenario | Detection | Recovery |
|---|---|---|
| STT returns garbage | Transcript is nonsensical or very short (<3 words) with low confidence | "I didn't quite catch that. Could you say that again?" (max 2 retries, then offer text fallback) |
| User goes off-topic | LLM classifies utterance as unrelated to agent's scope | "I can help with [scope]. For [off-topic thing], you'd want to [redirect]. Back to your question about [last topic]..." |
| User is frustrated | Sentiment detection: raised voice, profanity, "talk to a human" | Acknowledge emotion first: "I understand this is frustrating." Then offer: handoff to human, or one more attempt with a different approach. |
| User provides partial info | Slot-filling has incomplete data after 2 attempts | "I have your name and email. I still need your order number. You can find it in your confirmation email." |
| Connection quality degrades | High STT error rate, frequent retranscription | "It sounds like we have a bad connection. Let me try to work with what I've got." Increase VAD sensitivity, repeat back more often. |
| User wants to restart | "Start over", "Never mind", "Go back to the beginning" | Clear all slot data. Return to initial greeting state. "No problem, let's start fresh." |
