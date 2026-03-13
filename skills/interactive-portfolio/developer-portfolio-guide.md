# Developer Portfolio Guide

## GitHub Profile Optimization

Your GitHub profile IS part of your portfolio. Hiring managers check it before or after your portfolio site.

| Element | Optimization | Common Mistake |
|---|---|---|
| Profile README | 2-3 sentences: who you are, what you build, what you're interested in. Link to portfolio site. Keep it simple -- avoid ASCII art walls and badge spam | README with 50 badges, animated GIFs, and GitHub stats widgets. Looks like you spent more time on your README than on actual code |
| Pinned repositories | Pin 4-6 repos that represent your best work. Mix: 1-2 substantial projects, 1 open source contribution, 1 utility/tool | Pinning tutorial follow-alongs (todo-app, weather-app). Or pinning repos with no README and 1 commit |
| Contribution graph | Green squares show consistency, not volume. 3-5 commits/week is healthy. Large gaps are fine (people have lives) | Force-pushing empty commits to fill the graph. Experienced developers recognize artificial contribution patterns instantly |
| Repository READMEs | Each pinned repo needs: what it does (1 sentence), why you built it, how to run it, screenshot/demo link, tech stack | No README at all. Or a README that's just the framework's auto-generated boilerplate |
| Commit messages | Clean, descriptive commits in your showcase repos. "Fix user authentication race condition" not "fix stuff" | Rebasing your entire history to clean up commits looks artificial. A few messy commits are fine -- they show real development |
| Issue/PR participation | Open source contributions (even small ones: docs fixes, bug reports) show collaboration skills | Don't claim open source contributions unless they're genuine. Hiring managers can see the PR diff |

**The GitHub paradox**: Some of the best developers have sparse GitHub profiles (they code all day at work, not in their free time). If your GitHub is sparse, compensate with deeper case studies on your portfolio site. If your GitHub is active, link specific repos from your case studies.

## Technical Blog Positioning

A blog on your portfolio site demonstrates communication skills and technical depth. But topic selection matters enormously.

| Blog Topic Type | Hiring Impact | Why | Example |
|---|---|---|---|
| "How I solved X" (debugging story) | VERY HIGH | Shows problem-solving process, debugging methodology, and ability to communicate technical concepts | "How I reduced our API response time from 3s to 200ms" with the actual investigation process |
| "Why I chose X over Y" (architecture decision) | HIGH | Shows engineering judgment, tradeoff analysis, and decision-making maturity | "Why we moved from REST to GraphQL (and what we'd do differently)" |
| Technical deep dive | HIGH (for senior roles) | Demonstrates depth of understanding beyond surface-level usage | "Understanding V8's garbage collector and how it affected our Node.js memory leak" |
| Tutorial / "How to build X" | LOW | There are 10,000 "How to build a React todo app" articles. You're competing with professional tech writers and AI-generated content | Avoid unless the tutorial covers a genuinely novel topic. "How to build X" has near-zero hiring signal |
| Opinion piece ("Why X framework is bad") | NEGATIVE | Comes across as contrarian without constructive alternative. Hiring managers worry about culture fit | "React considered harmful" type posts signal someone who argues about tools rather than shipping |
| Learning journey | MEDIUM (for junior roles) | Shows self-awareness and growth mindset. Less valuable for senior roles where depth is expected | "My first year learning Rust: what surprised me" -- genuine, not performative |

**Blog frequency**: Quality >> quantity. One excellent post per quarter beats weekly low-quality posts. A portfolio with 2-3 deep technical articles outperforms one with 50 shallow tutorials.

## Code Showcase Patterns

How to demonstrate code quality without requiring visitors to clone and run your repos.

| Pattern | Best For | Implementation | Gotcha |
|---|---|---|---|
| Live demo link | Interactive applications, tools, visualizations | Deploy to Vercel/Netlify/Railway. Include demo credentials if login required | Demo must WORK. A broken live demo is worse than no demo. Check monthly. Free tier apps may spin down |
| Embedded code snippets | Highlighting specific elegant solutions or architecture decisions | Use syntax-highlighted code blocks in case studies. Show 15-30 lines max, not entire files | Don't show boilerplate. Show the interesting part with 2-3 sentences explaining WHY it's interesting |
| Architecture diagrams | System design, complex backend work, microservices | Simple diagrams (Excalidraw, Mermaid) showing component relationships. Not UML -- hiring managers don't read UML | Keep diagrams to 5-8 components max. Complex diagrams without explanation are noise |
| Before/after metrics | Performance optimization, refactoring | Lighthouse scores, load times, bundle sizes, test coverage. Screenshots of dashboards | Metrics must be from YOUR work. Don't show metrics from features where you weren't the primary contributor |
| Video walkthrough | Complex interactions, mobile apps, CLI tools | 30-60 second Loom/screen recording. No narration needed for simple walkthroughs | Keep SHORT. 30 seconds > 5 minutes. Nobody watches long portfolio videos. Start with the most interesting interaction |

## Developer-Specific Case Study Structure

Developer case studies differ from design case studies. Hiring managers evaluate different things.

| Section | What to Write | What They're Evaluating | Common Mistake |
|---|---|---|---|
| Problem statement | "The API was handling 10K requests/minute but degrading at 15K. We needed to support 50K without infrastructure cost increase" | Can you identify and articulate technical problems clearly? | Vague problems: "The app was slow." How slow? For whom? Under what conditions? |
| Technical decisions | "Chose Redis for caching over Memcached because we needed sorted sets for the leaderboard feature and data persistence for cache warming" | Do you make decisions based on technical requirements, not hype? | Name-dropping: "Used React, Node, Docker, Kubernetes, GraphQL" without explaining why each technology was chosen |
| Architecture | Show the system diagram. Explain the data flow. Highlight where the interesting complexity lives | Can you think about systems, not just code? | Over-engineering: showing a microservices architecture for a project that could have been a monolith |
| Challenges encountered | "Discovered that our database queries were creating N+1 problems when loading nested comments. Solved with DataLoader batching" | How do you handle unexpected problems? Do you debug systematically? | Pretending everything went smoothly. Real projects have real problems. Showing how you solved them is more impressive than pretending they didn't exist |
| Results | Quantified: "Response time: 3s -> 200ms. Server costs: $500/month -> $200/month. Error rate: 2% -> 0.1%" | Did your work actually make a measurable difference? | Unquantified results: "Made the app faster." By how much? How did you measure it? |
| Your role | "I was the sole backend developer. Designed the caching layer, wrote the migration scripts, and coordinated with the frontend team on API changes" | What specifically did YOU do vs. what the team did? | Claiming team achievements. "We built a platform serving 1M users" -- but what was YOUR contribution? |

## Open Source Contribution Presentation

| Contribution Type | How to Present | Portfolio Impact |
|---|---|---|
| Feature PR to major project | Link to PR with brief description. "Contributed i18n support to [project], merged after 3 rounds of code review" | HIGH. Shows you can navigate large codebases, follow contribution guidelines, and respond to code review |
| Bug fix | Link to issue + PR. Briefly describe the debugging process | MEDIUM-HIGH. Bug fixes show diagnostic skills. Especially valuable if the bug was non-trivial |
| Documentation improvement | Link to PR. Describe what was unclear and how you improved it | MEDIUM. Shows communication skills and attention to developer experience. Underrated by candidates, noticed by senior engineers |
| Created and maintained OSS tool | GitHub repo with stars/forks/downloads stats. Describe the problem it solves and who uses it | VERY HIGH. Building something others use is the strongest signal of engineering capability |
| Trivial contributions (typo fixes, minor formatting) | Don't feature these prominently | LOW. One or two are fine in a list. Making them a centerpiece looks like padding |
