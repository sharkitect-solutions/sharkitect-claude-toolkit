# Question Bank by Dimension

Pre-crafted Socratic questions organized by clarity dimension. Use these as templates,
not scripts -- adapt the phrasing to the conversation context.

## Scope Questions

**Level 1 (Score 1-3) -- Identify the core:**
- "If this had to do ONE thing on day one, what would that be?"
- "Is this (a) a standalone tool, (b) an addition to an existing system, or (c) a platform with multiple parts?"
- "Paint me the 30-second version: a user opens this and does what exactly?"

**Level 2 (Score 4-6) -- Draw the boundaries:**
- "What is explicitly NOT part of this? What should I leave out?"
- "You mentioned [X] and [Y] -- are those one system or two separate things?"
- "Is there a phase 1 vs phase 2 here, or is everything equally important?"

**Level 3 (Score 7+) -- Validate:**
- "So the scope is: [summary]. In scope: [list]. Out of scope: [list]. Does that match your intent?"

## Success Criteria Questions

**Level 1 (Score 1-3) -- Establish any criteria:**
- "How will you personally test whether this works? What would you check?"
- "Imagine I hand you the finished product. What's the first thing you click/run/check?"
- "What would 'done' look like? Can you describe one concrete scenario?"

**Level 2 (Score 4-6) -- Make criteria measurable:**
- "You said it should be [fast/reliable/easy]. Can we put a number on that?"
- "Would it be: (a) returns correct data, (b) returns correct data within X ms, or (c) returns correct data within X ms with Y% uptime?"
- "What inputs go in, what outputs come out? Can you give me one example pair?"

**Level 3 (Score 7+) -- Validate:**
- "Here are the acceptance criteria I've captured: [list]. Are these the right pass/fail gates?"

## Constraints Questions

**Level 1 (Score 1-3) -- Surface any constraints:**
- "Are there any hard rules about technology? (Language, framework, no external dependencies, etc.)"
- "What environment does this run in? (Your laptop, a server, a cloud function, inside n8n, etc.)"
- "Is there a size/complexity budget? (Under 500 lines, single file, no database, etc.)"

**Level 2 (Score 4-6) -- Classify constraints:**
- "You mentioned [X constraint]. Is that non-negotiable, or flexible if there's a good reason?"
- "Any constraints from external systems? (API rate limits, auth requirements, data formats)"
- "Timeline constraint: is this needed by a specific date, or is quality more important than speed?"

**Level 3 (Score 7+) -- Validate:**
- "Constraints captured: [list with negotiability flags]. Any I'm missing?"

## Edge Case Questions

**Level 1 (Score 1-3) -- Introduce the concept:**
- "What happens when the input is empty or missing?"
- "What if the thing this depends on is unavailable? (API down, file missing, network timeout)"
- "What's the worst-case scenario? What should the system do when it happens?"

**Level 2 (Score 4-6) -- Enumerate specific cases:**
- "Walk me through: valid input, slightly wrong input, completely wrong input. What happens at each?"
- "Is there a volume/scale edge? (What if 1 item vs 10,000?)"
- "What about concurrent use? Can two users/processes hit this at the same time?"

**Level 3 (Score 7+) -- Validate:**
- "Edge cases captured: [list with expected behaviors]. Any scenarios I'm missing?"

## Dependencies Questions

**Level 1 (Score 1-3) -- Discover dependencies:**
- "What existing systems or data does this touch?"
- "Does this read from, write to, or call anything that already exists?"
- "Does anything need to exist FIRST before we can build this?"

**Level 2 (Score 4-6) -- Map interfaces:**
- "For [dependency X]: what's the interface? (API endpoint, database table, file format, function call)"
- "Is [dependency] something we control, or external? Can we change its interface if needed?"
- "What happens if [dependency] changes its interface? How brittle is this connection?"

**Level 3 (Score 7+) -- Validate:**
- "Dependencies mapped: [list with interface + status]. Ready to build against these?"

## User Context Questions

**Level 1 (Score 1-3) -- Identify the user:**
- "Who specifically uses this? (You, your team, customers, automated systems)"
- "How do they access it? (CLI, web UI, API call, Slack command, cron job)"
- "How often? (Once, daily, on-demand, triggered by an event)"

**Level 2 (Score 4-6) -- Understand the journey:**
- "What triggers the need? What just happened that makes someone reach for this tool?"
- "What do they do with the output? (Read it, feed it to another system, make a decision)"
- "Are there different user types with different needs, or one user type?"

**Level 3 (Score 7+) -- Validate:**
- "User context: [who, how, when, why]. Does this capture the actual usage?"

## Meta-Questions (Any Dimension)

These work when you're unsure which dimension to probe:

- "What's the riskiest assumption we're making right now?"
- "If this fails, what's the most likely reason?"
- "What would make you change your mind about how this should work?"
- "Is there anything you know about this domain that I probably don't?"
- "What's the thing you haven't said yet because it seemed obvious?"
