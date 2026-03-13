---
name: meeting-insights-analyzer
description: >
  Use when analyzing meeting transcripts, recordings, or notes to diagnose dysfunction,
  power dynamics, facilitation failures, or whether the meeting should exist at all.
  Use when auditing an organization's meeting culture across multiple meetings.
  NEVER for scheduling, calendar management, or meeting invitation logistics.
  NEVER for transcription itself -- this analyzes already-transcribed content.
---

# Meeting Insights Analyzer

## Meeting Dysfunction Decision Tree

Start here for EVERY meeting analysis. Work top-down.

```
Should this meeting exist at all?
|
+--[Calculate ROI: attendees x avg hourly rate x duration]
|  Cost > value of decisions made? --> RECOMMEND: cancel, replace with async
|
+-- Does this meeting have a single clear TYPE? (see taxonomy below)
|   NO --> The meeting is trying to do too much. Split it.
|   YES --> proceed
|
+-- Is the stated purpose the ACTUAL purpose?
|   NO --> This is a theater meeting (see pre-wire detection below)
|   YES --> proceed
|
+-- Does the dysfunction live in the MEETING or the CULTURE?
|   CULTURE --> No amount of meeting optimization fixes org dysfunction
|   MEETING --> Diagnose: format, facilitation, cadence, or attendee list
|
+-- Is the facilitator the problem?
|   YES --> See facilitation failure patterns
|   NO --> Analyze participant dynamics
```

## Meeting Type Taxonomy

There are exactly 4 types of meetings. Mixing them is the #1 structural failure.

| Type | Purpose | Required Format | Failure When Mixed |
|------|---------|----------------|--------------------|
| Decision | Choose a path forward | Pre-read required, max 6 people, ends with documented decision | Adding "FYI updates" dilutes decision focus, 30 min of context-setting leaves 5 min to decide |
| Information | One-way broadcast | Could almost always be an email/doc, only justified when Q&A is expected | Adding a "quick decision" to an info meeting means uninformed people vote |
| Creative | Generate options | Divergent thinking, no evaluation during generation, psychological safety required | Status updates kill creative energy, boss speaking first anchors all ideas |
| Status | Progress reporting | Structured format (blockers only, not accomplishments), time-boxed per person | "Let's also brainstorm solutions" turns a 15-min standup into 90 min |

**Mixing test:** If a meeting agenda has items from 2+ types, flag it. "Team sync" meetings that combine status + decisions + brainstorming are the most common dysfunction and the hardest to kill because everyone thinks they are "efficient."

## Rationalization Table

When people describe their meeting problems, translate to the real issue:

| What They Say | What It Actually Means | Real Fix |
|---------------|----------------------|----------|
| "We need better agendas" | Meetings lack clear type/purpose | Classify meeting type, kill mixed-purpose meetings |
| "People don't come prepared" | No pre-read culture, no consequences for showing up cold | Cancel meetings when pre-reads are not done, enforce publicly |
| "Meetings run long" | No facilitator willing to cut people off, or the meeting is mistyped | Assign a facilitator with actual authority to enforce time |
| "We have too many meetings" | Decisions are not being made in meetings, so more meetings are scheduled to "follow up" | Require every meeting to end with a documented decision or be cancelled |
| "Nobody pays attention" | The meeting does not need these attendees, or it should be async | Cut attendee list to decision-makers only |
| "We need to be more collaborative" | One person dominates, others have learned silence is safer | This is a psychological safety problem, not a meeting format problem |
| "Our standups take too long" | Standups became status-reporting-to-manager instead of team coordination | Blockers only, no accomplishments, facilitator rotates, manager observes silently |
| "I spend all day in meetings" | Org uses synchronous communication as default instead of exception | Audit all recurring meetings, delete 40%, make async the default |

## NEVER List

1. NEVER report filler word counts ("um" appeared 47 times) -- this is shallow analysis that any word counter can do. Analyze WHY filler words spike (uncertainty, being challenged, talking about a topic they do not own).
2. NEVER provide a "speaking ratio" without analyzing WHO they spoke to, WHEN they spoke (first? last? after the boss?), and WHETHER their contributions were acknowledged.
3. NEVER recommend "better agendas" as a fix. Agendas are a symptom treatment. Diagnose the meeting type problem.
4. NEVER analyze a meeting in isolation when the user has access to multiple meetings. Patterns across meetings reveal culture; single meetings reveal noise.
5. NEVER treat all participants as equal. Analyze the power structure first -- who can interrupt without consequence, whose silence means disagreement vs disengagement.
6. NEVER suggest "meeting-free days" as a solution. This treats the symptom (too many meetings) without addressing why they exist (decisions not being made, async communication failure).
7. NEVER provide feedback without specific transcript evidence. "You tend to hedge" is useless. "At 14:32 you said 'maybe we could potentially consider' when you needed to say 'we need to change the timeline'" is useful.
8. NEVER score or rate a meeting without first establishing what TYPE of meeting it was supposed to be. A decision meeting with no decision is a failure. An information meeting with no decision is fine.
9. NEVER conflate someone being quiet with someone being disengaged. Quiet in the presence of a dominator is a rational survival strategy, not a participation problem.
10. NEVER recommend "go around the room" as an inclusion technique. It puts people on the spot and produces performative contributions. Recommend pre-submitted written input instead.

## Power Dynamics Analysis Framework

This is the most valuable and most overlooked layer of meeting analysis. Surface-level tools count words. Expert analysis reads power.

### Dominance Signals (in transcripts)

- **Interruption asymmetry:** Who interrupts whom, and who gets interrupted? When a senior person interrupts a junior person, does anyone notice? When a junior person interrupts a senior person, do they apologize?
- **Idea laundering:** Person A suggests X, it gets ignored. Person B (higher status) restates X five minutes later, it gets adopted. Track this explicitly -- it is a retention and equity problem.
- **Question direction:** Who gets ASKED for their opinion vs who VOLUNTEERS it? Being asked signals perceived authority. Only volunteering signals the person has to fight for airtime.
- **Post-boss anchoring:** After the highest-status person speaks, do others agree, elaborate, or challenge? If challenge rate drops to zero after the boss speaks, the meeting is not a discussion -- it is a ratification ceremony.
- **Silence mapping:** Who stops talking and when? If a person was active in the first 15 minutes and silent after a specific exchange, something happened in that exchange.
- **Hedge differential:** Senior people who hedge ("I think maybe we should...") are being diplomatic. Junior people who hedge are being protective. Same words, different meaning based on power position.

### Pre-Wire Detection

A "pre-wired" meeting is one where the decision was made before the meeting started. The meeting exists for optics. Signs:

- The proposal is presented as fully formed with no alternatives
- Questions are answered with "we already looked into that"
- The timeline is already set ("we need to decide today")
- One person has clearly rehearsed their pitch
- Dissent is acknowledged but not incorporated ("good point, but...")
- The meeting ends exactly where the organizer wanted it to

**When you detect a pre-wire:** Name it explicitly. "This meeting appears to have a predetermined outcome. The discussion format is performative. If the decision is already made, recommend the organizer communicate it directly and use meeting time for implementation planning instead."

## Facilitation Failure Patterns

| Pattern | What It Looks Like | Why It Fails |
|---------|-------------------|--------------|
| Self-answering | "Does anyone have concerns? I think it looks good, right?" | The facilitator answered their own question, signaling the expected response |
| "Any questions?" killer | Ending each topic with "any questions?" after a 2-second pause | This format rewards only people who can formulate questions instantly under social pressure |
| The non-enforcing timekeeper | "We're a bit over time but let's keep going" | If time limits are never enforced, they do not exist |
| Topic drift tolerance | Allowing conversation to wander because "it's all related" | Every minute of drift is stolen from the agenda items that will now be rushed |
| Loudest-voice routing | Calling on whoever raises their hand first or speaks loudest | Systematically excludes reflective thinkers and non-native speakers |
| Consensus without check | "So we're all agreed?" with no explicit dissent check | Silence is not agreement. It is often disagreement that does not feel safe |
| Note-taker as secretary | Assigning the most junior person (often a woman) to take notes | This person cannot fully participate while documenting, and the pattern reinforces status hierarchies |

## Meeting ROI Calculation

Use this to determine whether a meeting should exist:

```
Meeting cost = (number of attendees) x (avg hourly fully-loaded rate) x (duration in hours)
  + (15 min context-switch cost per attendee before and after)

Meeting value = decisions made x estimated value of timely decision
  + problems surfaced that would not have been found async
  + alignment created that prevents future rework

If cost > value for 3+ consecutive instances: recommend cancellation or async replacement
```

**Typical findings when applied:**
- A weekly 1-hour meeting with 8 people at $75/hr fully loaded = $800/week = $41,600/year
- If that meeting produces 0-1 decisions per month, it costs $41,600 to make 12 decisions
- The same decisions via a shared doc with async comments would cost near zero

## Before/After: Shallow vs Expert Meeting Analysis

**BEFORE (shallow analysis -- what basic tools produce):**

"In the March 5 product review meeting, you spoke for 38% of the time. You used 'um' 23 times and 'like' 15 times. You interrupted Sarah twice. You asked 4 questions. Recommendation: reduce filler words and be more mindful of interruptions."

**AFTER (expert analysis -- what this skill produces):**

"The March 5 product review was structured as a decision meeting but functioned as an information-sharing session. No decision was made despite 'finalize Q2 priorities' being the stated purpose.

Power dynamics: After VP Chen stated his preference at 12:04, zero alternatives were raised for the remaining 40 minutes. Sarah's proposal from 8:30 (restructure the mobile team) was restated by Chen at 12:04 without attribution. You interrupted Sarah twice -- both times to 'build on her point' -- but your additions redirected her proposal toward Chen's known preference. This may have been unconscious alignment with authority rather than intentional idea theft, but the effect was the same: Sarah's original proposal was absorbed and reframed.

Your filler word rate tripled between 8:00-12:00 (your section) and 12:04-12:45 (after Chen spoke), suggesting decreased confidence once senior leadership established a direction. You hedged your Q2 recommendation with 'maybe we could consider' when your pre-meeting notes show you had a firm position.

Core issue: This meeting is pre-wired. Chen's preference was communicated to you in a 1:1 on March 3 (referenced at 11:52). The 'product review' is ratification theater. Recommend either (a) making it an explicit announcement meeting, freeing 45 minutes, or (b) restructuring so Chen speaks last, not first, to allow genuine deliberation."

## Meeting Culture Audit Framework

When analyzing an organization's meetings (not just one meeting), evaluate these five dimensions:

1. **Decision velocity:** How many meetings does it take to make a decision? >1 means the meeting structure is broken.
2. **Async-first culture:** What percentage of "meetings" could be a document with comments? Target: convert 40%+ to async.
3. **Attendee discipline:** Average meeting size vs number of people who actually speak. If 8 attend and 3 speak, 5 people are wasting their time.
4. **Recurring meeting hygiene:** When was the last time each recurring meeting was evaluated for continued relevance? If "never," at least 30% can be killed.
5. **Psychological safety proxy:** Ratio of challenges-to-agreements after the highest-status person speaks. Below 0.2 suggests performative agreement culture.
