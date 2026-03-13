# Financial Modeling Guide

Load when projecting revenue, calculating unit economics, evaluating pricing changes, or planning financial milestones for a micro-SaaS.

## Revenue Projection Model

### Bottom-Up Estimation (Preferred)

Build projections from acquisition capacity, not market size. Micro-SaaS founders control acquisition, not TAM.

| Variable | How to Estimate | Common Range |
|---|---|---|
| Monthly new trials/signups | Channel capacity: content = 50-200/mo, Product Hunt = 500-2000 one-time, cold email = 20-50/mo, paid ads = budget / CPC * CTR | 30-200/month for solo founder |
| Trial-to-paid conversion rate | Depends on friction and price. Self-serve SaaS average 3-8%. With onboarding optimization: 8-15%. | 5-10% starting assumption |
| Average revenue per user (ARPU) | Pricing architecture * plan mix. If 70% pick $19/mo and 30% pick $49/mo: ARPU = $28 | $15-50 typical for micro-SaaS |
| Monthly churn rate | Industry avg 5-7% for SMB SaaS. Good: 3-5%. Excellent: <3%. | 5% starting assumption |
| Expansion revenue rate | Upgrades + seat additions as % of existing MRR. Rare in early micro-SaaS. | 0-3% monthly |

### Monthly MRR Projection Formula

```
Month N MRR = Month N-1 MRR * (1 - churn_rate) + new_customers * ARPU + expansion
```

| Month | New Customers | Churned | Net New MRR | Cumulative MRR |
|---|---|---|---|---|
| 1 | 10 | 0 | $280 | $280 |
| 2 | 12 | 1 ($28) | $308 | $588 |
| 3 | 15 | 2 ($56) | $364 | $952 |
| 6 | 20 | 5 ($140) | $420 | $2,800 |
| 12 | 25 | 10 ($280) | $420 | $7,200 |

**Reality check**: This assumes steady growth in new customer acquisition. Most micro-SaaS products see lumpy acquisition (spikes from launches, content hits, then plateaus). Plan for 3-month plateaus between growth spurts.

## Cost Structure Template

### Fixed Monthly Costs

| Category | Typical Items | Micro-SaaS Range | Optimization |
|---|---|---|---|
| Hosting/infrastructure | Vercel, Railway, Supabase, domain, DNS | $0-50 | Free tiers cover first 1000 users for most stacks |
| SaaS tools | Email (Resend), analytics (PostHog), error tracking (Sentry) | $0-50 | Free tiers exist for all of these at micro-SaaS scale |
| Payment processing | Stripe/Paddle/Lemon Squeezy fees | 2.9% + $0.30 per transaction | Negotiate volume discount above $50K/year |
| Domain + email | Custom domain, Google Workspace or Zoho | $6-12 | Non-negotiable. Professional email is baseline. |
| **Total fixed (pre-revenue)** | | **$10-100/month** | |

### Variable Costs (Scale with Usage)

| Category | Cost Model | Scaling Point |
|---|---|---|
| API costs (OpenAI, etc.) | Per-token or per-call | Becomes significant above 1K active users |
| Email sending | Per-email (Resend: $0.001/email after free tier) | Significant above 10K emails/month |
| File storage | Per-GB (S3: $0.023/GB/month) | Rarely significant for micro-SaaS |
| Support time (founder hours) | Opportunity cost: your hourly rate * hours spent | Significant above 100 customers |
| Bandwidth/CDN | Per-GB transferred | Rarely significant unless serving large files |

### Breakeven Calculation

```
Monthly breakeven = fixed_costs / (ARPU - variable_cost_per_customer)
```

| Scenario | Fixed Costs | ARPU | Variable Cost/Customer | Breakeven Customers |
|---|---|---|---|---|
| Lean (free tiers) | $50/mo | $29/mo | $2/mo | 2 customers |
| Moderate | $200/mo | $29/mo | $5/mo | 9 customers |
| With API costs | $200/mo | $29/mo | $10/mo | 11 customers |
| With paid tools | $500/mo | $29/mo | $5/mo | 21 customers |

**Key insight**: Micro-SaaS breakeven is almost always achievable with <25 customers. The real question is not "can I break even?" but "can I acquire 25 paying customers?"

## Pricing Change Impact Calculator

Before changing price, estimate the impact on each metric:

| Change | Expected Impact | Risk | Mitigate |
|---|---|---|---|
| Raise price 30% for new customers | ARPU up 30%, conversion rate may drop 10-20% | Net revenue likely increases (30% more per customer offsets 10-20% fewer customers) | Grandfather existing customers at old price for 6 months |
| Add annual billing (20% discount) | 10-20% of customers switch. LTV increases (lower churn on annual). Cash flow improves. | Monthly revenue per customer decreases 20% for annual switchers | Default the pricing toggle to annual. Show monthly as the comparison anchor. |
| Remove free tier | Trial-to-paid increases dramatically. Total signups decrease. | Lose viral/word-of-mouth from free users | Replace free tier with 14-day trial. Capture email before trial starts. |
| Add premium tier ($99/mo) | 5-10% of existing customers upgrade. ARPU increases. | Feature cannibalization -- users expect premium features to be added to basic tier eventually | Clear differentiation: premium = more usage/limits/support, not just more features |
| Introduce per-seat pricing | Revenue scales with team adoption. ARPU increases for multi-user accounts. | Single users feel punished. Solopreneurs churn. | Keep single-user plan flat-rate. Per-seat kicks in at 3+ users. |

## Milestone-Based Financial Planning

| MRR Milestone | What It Means | What to Do | What NOT to Do |
|---|---|---|---|
| $0 -> $100 | Product exists, someone paid | Validate: will 10 more people pay? Talk to your first customers obsessively. | Optimize pricing, build features, invest in growth. |
| $100 -> $1K | Product-market fit signal | Double down on the acquisition channel that got you here. Automate onboarding. | Diversify channels. Build features. Hire. |
| $1K -> $5K | Real business potential | Fix churn (it compounds). Set up dunning. Start content/SEO. | Quit your job (too early unless you have 12-month runway). |
| $5K -> $10K | Sustainable solo income | Consider quitting day job (with 6-month runway). Invest in support efficiency. | Hire a team. Enterprise pivots. Fundraising. |
| $10K -> $25K | Comfortable solo business | Hire first contractor (support or content). Explore expansion revenue. | Over-hire. Build a "platform." Chase enterprise. |
| $25K -> $50K | Decision point | Decide: stay solo (optimize profit) or grow (hire, scale, accept lower margins). Both are valid. | Drift without a conscious strategy. |

## Tax and Legal Essentials (Awareness, Not Advice)

| Topic | What Solo Founders Often Miss | Action |
|---|---|---|
| Sales tax / VAT | SaaS is taxable in most US states and all EU countries. Merchant of Record (Paddle, Lemon Squeezy) handles this. Stripe does NOT. | Use a Merchant of Record OR register for sales tax in nexus states. |
| Income classification | SaaS revenue is ordinary income (not capital gains). Self-employment tax applies in US. | Set aside 25-35% of revenue for taxes from day one. |
| Business entity | Sole proprietorship = personal liability. LLC = asset protection + tax flexibility. | Form an LLC before $5K MRR. Cost: $50-500 depending on state. |
| Terms of Service / Privacy Policy | Required by payment processors and app stores. GDPR requires specific disclosures. | Use Termly, Iubenda, or a template. Not optional, but doesn't need a lawyer at this stage. |
| Contractor payments | If you hire contractors, issue 1099s (US) or equivalent. Misclassification risk. | Use a payment platform (Deel, Gusto) that handles tax forms. |

**Disclaimer**: This is awareness-level guidance, not legal or tax advice. Consult a CPA and attorney when revenue exceeds $5K/month.
