---
name: interactive-portfolio
description: "Use when building developer portfolios, designer portfolios, creative showcases, or personal websites meant to convert visitors into job offers or client inquiries. Also use when the user mentions portfolio architecture, case study presentation, project showcase, hiring manager psychology, or portfolio performance optimization. NEVER use for scroll animation implementation (scroll-experience), visual design direction and typography (frontend-design), portfolio copywriting and messaging (copywriting), or Figma-to-code translation (figma-implement-design)."
version: "2.0"
optimized: true
optimized_date: "2026-03-12"
---

# Interactive Portfolio

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Portfolio type decision, architecture, project selection, case study structure, hiring manager psychology, performance vs creativity, anti-patterns | Always (auto-loaded) |
| developer-portfolio-guide.md | GitHub profile optimization (pinned repos, contribution graph, README strategy), technical blog positioning (topics that get hired vs topics that don't), code showcase patterns (live demos vs screenshots vs embedded snippets), open source contribution presentation, developer-specific case study structure | When building a developer or engineering portfolio specifically |
| design-portfolio-guide.md | Case study depth calibration by audience (recruiter vs hiring manager vs design lead), process documentation strategy (showing thinking vs showing output), design system showcase techniques, tool proficiency demonstration without resume-listing, UX research presentation, multi-platform work display | When building a designer or UX portfolio specifically |
| portfolio-technical-implementation.md | Framework selection for portfolio sites (Next.js vs Astro vs SvelteKit vs vanilla, with tradeoffs), performance budgets specific to portfolios, hosting and deployment (Vercel vs Netlify vs GitHub Pages vs custom), SEO for personal sites (structured data, OG tags, sitemap), analytics setup (what to track and why), image optimization for project screenshots, accessibility requirements | When implementing the technical infrastructure of a portfolio site |

Do NOT load companion files for basic architecture decisions, project selection, or anti-pattern reference -- SKILL.md covers these fully.

## Scope Boundary

| Area | This Skill | Other Skill |
|---|---|---|
| Portfolio site architecture and information hierarchy | YES | -- |
| Project selection and case study structure | YES | -- |
| Hiring manager psychology and conversion optimization | YES | -- |
| Portfolio performance vs creativity tradeoffs | YES | -- |
| Portfolio type decision (dev/design/creative/agency) | YES | -- |
| Scroll animations and parallax effects | NO | scroll-experience |
| Typography, color, and visual design direction | NO | frontend-design |
| Portfolio copywriting and about page messaging | NO | copywriting |
| Translating Figma mockups to code | NO | figma-implement-design |
| SEO technical audits and optimization | NO | seo-optimizer |
| Page load performance optimization | NO | page-cro (for conversion), clean-code (for implementation) |
| Personal branding strategy | NO | marketing-strategy-pmm |

## Portfolio Type Decision

First match determines primary structure and emphasis.

| Signal | Portfolio Type | Architecture | Critical Section |
|---|---|---|---|
| Applying for developer/engineering roles | Developer portfolio | Hybrid (landing + separate case studies). GitHub integration essential | Technical depth: architecture decisions, code quality evidence, system design thinking |
| Applying for design/UX roles | Design portfolio | Multi-page (dedicated case study pages, 800-1500 words each). Visual-first navigation | Process showcase: research -> ideation -> iteration -> validation -> outcome. Recruiters check process, not just final output |
| Freelance/agency seeking clients | Client portfolio | Multi-page with industry/service filtering. Testimonials prominent. Clear pricing signals | Results and ROI: "Increased conversions 40%" beats "Redesigned the homepage." Clients buy outcomes, not craft |
| Creative (illustration, 3D, motion) | Creative portfolio | Grid gallery with filtering. Single-page scroll works. Minimal text, maximum visual impact | Visual quality speaks. Descriptions secondary. Loading performance critical (heavy assets) |
| Career transition (new field) | Transition portfolio | Hybrid. Transferable skills narrative + 3-5 targeted projects (even side projects count) | Story arc: why you're transitioning, what you bring from previous career, evidence of new skills |

## Architecture Decision

| Signal | Architecture | Why |
|---|---|---|
| <8 projects worth showing | Single-page scroll | Not enough content for multi-page. Better to show density than sparse pages |
| 8-15 quality projects across categories | Hybrid (landing page + case study subpages) | Landing gives overview, subpages give depth. Best balance for most portfolios |
| 15+ projects across different service types | Multi-page with filtering | Visitors need to self-select. Category/industry filters prevent overwhelm |
| Primarily visual work (illustration, photography) | Grid gallery | Words get in the way. Let the work speak. Quick scanning is the interaction model |
| Complex technical work (systems, architecture) | Blog-style with long-form case studies | Technical depth requires reading. 1500-3000 word case studies per project |

### The 30-Second Rule

Hiring managers and potential clients spend 6 seconds on a resume and 30 seconds on a portfolio (eye-tracking research, Ladders Inc. 2018). In 30 seconds, visitors must identify:

1. **Who you are** (name, role -- above fold, no scrolling)
2. **What you do** (one line, specific -- "Frontend engineer specializing in design systems" not "Creative problem solver")
3. **Your best work** (2-3 featured projects visible without scrolling)
4. **How to contact you** (CTA visible or reachable in one click)

If any of these requires scrolling or clicking to find, you're losing 60-70% of visitors.

## Project Selection Framework

**Quality threshold**: Only include projects where you can answer "What problem did this solve and what was the measurable result?" Projects without clear outcomes should be excluded regardless of technical complexity.

| Selection Criteria | Include | Exclude |
|---|---|---|
| Recency | Projects from last 2-3 years | Anything older unless it's exceptional and still relevant |
| Relevance | Projects matching your target role/client | Projects in a completely different domain (unless career transition portfolio) |
| Impact evidence | "Reduced load time 60%" or "Shipped to 50K users" | "Built a website" or "Designed the UI" with no outcome |
| Your contribution | Work you personally led or significantly contributed to | Team projects where your contribution was minor or unclear |
| Diversity | Different project types showing range | 5 variations of the same type (diminishing returns after 2 similar projects) |
| Completeness | Live, functional, or well-documented | "Coming soon," broken links, placeholder screenshots |

**The Magic Number**: 4-6 featured projects. Research shows that 3 feels thin, 8+ creates decision fatigue (Iyengar & Lepper, "jam study" 2000). Present your best 4-6 prominently, with additional work available via "See all projects" if needed.

## Case Study Structure Decision

| Audience | Depth | Structure | Length |
|---|---|---|---|
| Recruiter (initial screen) | Shallow -- they're checking boxes | Hero image + one-line summary + tech stack tags + result metric. They scan, they don't read | 100-200 words max per project |
| Hiring manager (detailed review) | Medium -- they're evaluating judgment | Problem -> Your role -> Key decisions -> Outcome. Show WHY you made choices, not just WHAT you built | 500-800 words per project |
| Design lead (portfolio review) | Deep -- they're evaluating process | Full case study: Research -> Ideation (show sketches/wireframes) -> Iteration (show evolution) -> User testing -> Final design -> Metrics | 800-1500 words + 10-15 images |
| Potential client (sales context) | Results-focused -- they're evaluating ROI | Challenge (their language) -> Solution (your approach) -> Results (quantified) -> Testimonial (social proof) | 300-500 words + testimonial |

### Case Study Elements That Actually Convert

| Element | Impact | Why | Gotcha |
|---|---|---|---|
| Before/after comparison | HIGH | Visual proof of improvement. Instantly communicable. Works for both design and development (before: 4s load time, after: 0.8s) | Must be genuine improvement, not staged. Fake before/after destroys trust |
| Specific metrics | VERY HIGH | "40% increase in signups" beats "improved the user experience" every time. Numbers create credibility | Don't fabricate metrics. If you don't have them, use qualitative outcomes: "Reduced support tickets from weekly to monthly" |
| Process artifacts | MEDIUM-HIGH (for designers) | Wireframes, sketches, user flows show thinking. Hiring managers want to see HOW you think, not just what you produced | Don't show every artifact. Curate 3-5 that show key decision points |
| Technical decisions documented | HIGH (for developers) | "Chose Redis over Memcached because of data persistence requirements and sorted sets for leaderboard feature" shows judgment | Avoid name-dropping technologies without explaining WHY. Tech lists without reasoning look like resume padding |
| Video walkthrough | MEDIUM | Great for interactive or complex products. Shows the experience better than screenshots | Keep under 60 seconds. Nobody watches a 5-minute portfolio video. If it requires explanation, the work isn't self-evident enough |
| Testimonial from stakeholder | VERY HIGH (for clients) | Third-party validation is more persuasive than your own claims. "Sarah increased our conversion rate 35%" > "I increased their conversion rate 35%" | Get permission. Attribute to real people with real titles. Anonymous testimonials have near-zero credibility |

## Performance vs Creativity Tradeoff

| Portfolio Type | Performance Budget | Creativity Budget | Why |
|---|---|---|---|
| Developer portfolio | Strict: LCP <1.5s, CLS <0.05, TBT <150ms | Low: clean, functional, well-typed. Code quality IS the portfolio | Your portfolio IS a code sample. Hiring managers WILL inspect your source. Slow, janky developer portfolio = immediate rejection |
| Designer portfolio | Moderate: LCP <2.5s, CLS <0.1 | High: custom layouts, transitions, hover states. Visual craft expected | Designers are expected to push visual boundaries. But: images must be optimized (WebP/AVIF, lazy loading, srcset). A beautiful portfolio that takes 8s to load is a failed UX portfolio |
| Creative portfolio | Relaxed: LCP <3s acceptable for heavy visual content | Very high: 3D, animation, experimental layouts acceptable | Creative portfolios can push performance boundaries IF the loading experience itself is designed (progress bars, skeleton screens, content-first loading) |
| Client-facing portfolio | Strict: LCP <2s, TBT <200ms | Low-medium: professional, not experimental. Clients don't appreciate avant-garde navigation | Clients equate portfolio performance with work quality. Slow portfolio = "they'll build me a slow website too" |

**The Performance Paradox**: The most impressive portfolio animations mean nothing if the visitor bounces before they load. Mobile visitors on 3G (still common globally) experience your 5MB portfolio as a 15-second blank screen. Core Web Vitals aren't just Google metrics -- they're user patience metrics.

## Anti-Patterns

| Anti-Pattern | What Happens | Why It Fails | Fix |
|---|---|---|---|
| **Template Clone** | Uses a popular template (e.g., top Dribbble shot recreation) with only content swapped | Hiring managers see 50 identical portfolios per week. Zero memorability. Actually hurts: shows you can't design/build your own site | Start from scratch or heavily customize. Your portfolio layout IS a portfolio piece |
| **Animation Carnival** | Every element animates, parallaxes, or transitions. Page feels like a tech demo | Animations distract from content. Hiring managers can't find information. Accessibility nightmare (motion sensitivity). Performance tanks on mobile | Max 3-5 meaningful animations on the entire site. Each animation should guide attention, not demand it |
| **Resume Website** | Chronological list of jobs, skills as percentage bars, no project depth | Doesn't use the medium. A PDF resume does this better. No evidence of work quality. Skills bars are meaningless (80% of JavaScript?) | Show work, don't list credentials. Replace job history with case studies. Delete skill percentage bars entirely |
| **Coming Soon Syndrome** | "Portfolio coming soon!" or 2 projects + 4 "coming soon" placeholders | Communicates that you don't have enough work to show AND that you don't finish what you start. Double negative signal | Launch with whatever you have (even 2-3 projects). A complete small portfolio beats an incomplete ambitious one |
| **Tutorial Showcase** | Projects are tutorial follow-alongs (Todo app, weather app, calculator, Spotify clone) | Proves you can follow instructions, not solve problems. Hiring managers recognize popular tutorial projects immediately | Replace with original projects solving real problems. Even small personal tools (budget tracker you actually use, script that automates your workflow) show initiative |
| **Kitchen Sink** | 20+ projects with no curation. Every project ever completed, regardless of quality | Decision fatigue. Visitor can't find your best work. Low-quality projects drag down perception of high-quality ones (averaging effect) | Curate ruthlessly. 4-6 featured projects. Archive the rest or put behind "View all" link. Quality over quantity always |

### Rationalizations That Signal Bad Decisions

| Rationalization | Reality |
|---|---|
| "I need more projects before I launch" | You don't. 3 quality projects > 10 mediocre ones. Launch with what you have and iterate |
| "The animations show I'm technically skilled" | They show you can copy CodePen demos. Technical skill is demonstrated through project case studies, not portfolio animations |
| "I'll add case studies later" | You won't. Projects without case studies are screenshots with no context. Write the case study before adding the project |
| "Skills percentage bars show my expertise" | They're meaningless. 80% React? Compared to what? Compared to whom? Replace with "Technologies I use regularly" -- a simple list |
| "Visitors will click through to see everything" | They won't. 70% of portfolio visitors never scroll past the fold. Put your best work above the fold |

### Red Flags

| Red Flag | Diagnosis |
|---|---|
| Average time on site <15 seconds | First impression fails. Hero section doesn't communicate identity or hook interest |
| High traffic but zero contact form submissions | Portfolio showcases work but doesn't convert. Missing or weak CTA. Contact buried too deep |
| Visitors view landing page but don't click any projects | Project thumbnails or titles don't create curiosity. "Project 1, Project 2" naming. No visual hooks |
| Mobile bounce rate >80% | Portfolio broken or slow on mobile. Test on actual devices, not just browser resize |
| Visitors spend time but only on one project | Rest of portfolio isn't compelling enough to explore. One strong project carrying a weak portfolio |
| Contact form asks too many questions | "Name, email, budget, timeline, project description, how did you find me" -- each field reduces submissions. Name + email + one textarea is enough |

### NEVER

- Never use skill percentage bars (80% JavaScript has no meaning)
- Never include tutorial follow-along projects as portfolio pieces
- Never launch with "coming soon" placeholders -- launch with what you have
- Never sacrifice content readability for animation effects
- Never hide the contact CTA behind navigation or scrolling
