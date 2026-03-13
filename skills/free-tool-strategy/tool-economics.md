# Tool Economics for Engineering-as-Marketing

## Build Cost Estimation

### Development Cost by Tool Type

| Tool Type | MVP Scope | Typical Dev Time | Typical Cost (contractor/agency) | Ongoing Maintenance (year 1) |
|---|---|---|---|---|
| **Simple calculator** (input form + math + output) | 1-3 inputs, 1 output page, no database | 2-5 days | $1K-3K | $500-1K (minimal -- logic rarely changes) |
| **Complex calculator** (multi-step, personalized report) | 5-10 inputs, multi-page output, PDF export, email delivery | 2-4 weeks | $5K-15K | $2K-5K (data updates, PDF template fixes) |
| **Analyzer/auditor** (URL or file input, automated analysis) | URL input, API calls, scoring algorithm, output report | 3-6 weeks | $10K-25K | $5K-10K (API changes, scoring model updates, error handling) |
| **Generator** (input -> customized output) | Input form, template engine, output preview, copy/download | 1-3 weeks | $3K-10K | $2K-4K (template updates, edge cases) |
| **Interactive library/directory** | Database, search, filtering, individual item pages | 4-8 weeks | $10K-30K | $5K-15K (content updates, SEO, database maintenance) |
| **Interactive educational** (playground, simulator) | Custom UI, real-time feedback, state management | 4-12 weeks | $15K-50K | $5K-15K (browser compatibility, content updates) |

### Hidden Costs That Blow Budgets

| Hidden Cost | Why It's Missed | Typical Impact |
|---|---|---|
| **Mobile optimization** | MVP scoped for desktop only. But 50-70% of tool traffic is mobile | +30-50% of initial build. Non-negotiable for any marketing tool |
| **Edge case handling** | "What if they enter a negative number?" "What if the URL is malformed?" "What if the API times out?" | +20-40% of initial build. Unhandled edge cases = broken tool = brand damage |
| **OG image / share card** | Nobody thinks about social sharing preview until after launch | 1-3 days. Critical for tools where results are shared (analyzers, generators, quizzes) |
| **Email integration** | CRM sync, welcome email, result delivery, nurture trigger | 1-2 days for basic. 1 week for proper CRM integration with lead scoring |
| **Analytics setup** | Tracking funnel (land -> start -> complete -> share -> convert) beyond basic page views | 1-2 days. Without this, you can't measure ROI |
| **Accessibility** | WCAG compliance often scoped out of MVP. Then legal requires it | +10-20% of build. Input labels, keyboard navigation, screen reader, color contrast |
| **Data refresh** | Calculator uses 2024 tax rates. It's now 2026. Who updates the data? | Ongoing. Some tools need monthly data updates. Budget for it or automate it |

---

## Lead Value Calculation

### Formula

```
Monthly Tool Value = Monthly Tool Visitors x Completion Rate x Email Capture Rate x Lead-to-MQL Rate x MQL-to-Customer Rate x Customer LTV

Example:
5,000 visitors/mo x 60% completion x 15% email capture x 20% MQL x 5% customer x $5,000 LTV
= 5,000 x 0.60 x 0.15 x 0.20 x 0.05 x $5,000
= $2,250/month

Payback = Build Cost / Monthly Value
= $15,000 / $2,250
= 6.7 months
```

### Benchmarks by Tool Type

| Tool Type | Avg Completion Rate | Avg Email Capture Rate | Avg Lead Quality (MQL Rate) | Typical Monthly Value per 1K Visitors |
|---|---|---|---|---|
| **Calculator** (simple) | 70-85% | 10-20% (soft gate) | 15-25% | $150-500 (depends on ACV) |
| **Calculator** (complex) | 40-60% | 20-35% (partial gate) | 25-40% | $300-1,200 |
| **Analyzer/auditor** | 30-50% | 25-40% (gate for full report) | 30-50% | $500-2,000 |
| **Generator** | 60-80% | 8-15% (save/share gate) | 10-20% | $100-400 |
| **Library/directory** | N/A (browse, not complete) | 3-8% (newsletter, download) | 5-15% | $50-200 |
| **Quiz/assessment** | 50-70% | 15-30% (gate results) | 20-35% | $200-800 |

**Note**: These assume soft/partial gating. Fully gated tools have higher capture rates (30-60%) but much lower completion rates (10-30%). Net lead volume is usually LOWER with full gating.

---

## ROI Benchmarks by Category

### What "Good" ROI Looks Like

| Metric | Target | Excellent | Warning |
|---|---|---|---|
| **Payback period** | <12 months | <6 months | >18 months -- reconsider scope or promotion strategy |
| **Cost per lead (from tool)** | <50% of paid channel CPL | <25% of paid CPL | >75% of paid CPL -- tool isn't providing cost advantage |
| **Organic traffic growth** (month 6+) | 10-20% month-over-month | >30% MoM (compounding, backlinks working) | Flat after 6 months -- SEO strategy failing |
| **Lead quality** (vs paid leads) | Similar MQL-to-customer rate | Higher than paid (tool users are more educated) | Significantly lower -- tool attracting wrong audience (fit problem) |
| **Attribution clarity** | >60% of tool leads have clear source attribution | >80% attribution | <40% -- tracking setup is broken |

### Case Study Economics (Anonymized Benchmarks)

| Company Type | Tool Built | Build Cost | Monthly Leads | Monthly Value | Payback |
|---|---|---|---|---|---|
| B2B SaaS ($50K ACV) | ROI calculator | $8K | 40 MQLs | $10K pipeline | 1 month |
| Agency ($5K project avg) | Website grader | $20K | 150 leads | $7.5K | 3 months |
| E-commerce platform | Store profitability calculator | $12K | 200 emails | $2K direct revenue | 6 months |
| Developer tools | Code playground | $30K | 50 leads + 500 brand impressions | Hard to attribute | 12-18 months (brand play) |
| HR SaaS ($20K ACV) | Salary benchmarking tool | $25K | 80 MQLs | $16K pipeline | 2 months |

**Pattern**: B2B tools with high ACV payback fastest because each converted lead is worth thousands. Consumer/low-ACV tools need high volume to justify build cost.

---

## When to Kill a Free Tool

### Kill Criteria Decision

| Signal | Severity | Action |
|---|---|---|
| <50 monthly visitors after 9+ months, with SEO effort applied | CRITICAL | Kill. SEO had enough time. The demand isn't there |
| Negative brand feedback ("your tool gave wrong results," "it's broken") | CRITICAL | Fix immediately or take offline. Broken tools cause more harm than no tool |
| Lead-to-MQL rate <5% (tool leads never convert) | HIGH | Tool-product fit is broken. Kill or reposition |
| Maintenance cost exceeds lead value for 3 consecutive months | HIGH | Tool is a net negative. Kill or reduce maintenance to zero-effort mode |
| Security vulnerability in tool dependencies with no patch available | CRITICAL | Take offline immediately. A compromised tool is a brand and legal disaster |
| Core product pivot made tool irrelevant | MEDIUM | Sunset gracefully (redirect, archive notice) within 60 days |

### Graceful Sunset Procedure

| Step | Action | Why |
|---|---|---|
| 1 | Set a sunset date 30-60 days out | Gives time for SEO value capture and user communication |
| 2 | Add a banner: "This tool will be retired on [date]. [Alternative]" | Transparency. Don't just break links |
| 3 | Export and archive any user data | GDPR/CCPA compliance. Don't lose data you might need |
| 4 | Set up 301 redirect to nearest relevant page | Preserve SEO value. 301s pass ~90% of link equity |
| 5 | Update any blog posts, emails, or landing pages that link to the tool | Avoid sending users to a dead end |
| 6 | Monitor 404s for 90 days after redirect | Catch any missed internal links |

---

## Maintenance Budgeting

### Annual Maintenance by Complexity

| Tool Complexity | Year 1 Maintenance | Year 2+ Maintenance | What's Included |
|---|---|---|---|
| **Simple** (calculator, generator) | 10-15% of build cost | 5-10% of build cost | Dependency updates, occasional bug fix, data refresh |
| **Medium** (analyzer, quiz, library) | 15-25% of build cost | 10-15% of build cost | API updates, content refresh, performance optimization, security patches |
| **Complex** (interactive app, playground) | 25-40% of build cost | 15-25% of build cost | Feature additions, major dependency updates, browser compatibility, scale handling |

### Zero-Maintenance Mode

For tools that should keep running but don't justify active development:

| Action | How | Impact |
|---|---|---|
| Remove external API dependencies | Cache or inline any data from external APIs | Eliminates the #1 cause of tool breakage (API changes, rate limits, deprecation) |
| Static-generate everything possible | Pre-compute results for common inputs. Serve as static HTML | Reduces hosting cost to near-zero. Eliminates server-side failure modes |
| Remove analytics tracking | If you're not analyzing the data, stop collecting it | Reduces page load, eliminates tracking script maintenance |
| Set calendar reminder for 6-month check | Review if tool is still live, relevant, and non-embarrassing | Prevents the "ghost tool" anti-pattern |
