# Data Visualization Standards for Client Reports

## Chart Type Selection Guide

Choose the chart type based on the question being answered, not the data shape. Wrong chart types force clients to do mental translation, which means they stop reading.

### Decision Matrix

| Question Being Answered | Chart Type | Example |
|------------------------|-----------|---------|
| How does this compare across categories? | Horizontal bar chart | Revenue by service line, hours by project |
| How has this changed over time? | Line chart | Monthly revenue trend, weekly traffic |
| What is the composition/breakdown? | Stacked bar or donut (not pie) | Budget allocation, time by category |
| Where do we stand vs target? | Bullet chart or progress bar | KPI vs goal, budget consumed vs total |
| What is the relationship between two variables? | Scatter plot | Effort vs outcome, spend vs return |
| What is the distribution? | Histogram or box plot | Response time distribution, deal sizes |
| What is the current status? | Single number with context | Current MRR, this week's leads |

### Chart Type Anti-Rules

- **Never use pie charts with more than 5 slices.** Beyond 5, slices become indistinguishable. Use horizontal bar chart instead.
- **Never use 3D charts.** 3D effects distort proportions and add zero information. They exist to impress, not to inform.
- **Never use dual y-axes unless both metrics share a clear relationship.** Dual axes create false correlations. If the metrics are unrelated, use two separate charts.
- **Never use area charts for non-cumulative data.** Area charts imply volume/accumulation. Using them for discrete series misleads the reader about magnitude.

---

## Color Coding Standards

### Traffic Light System (universal across all reports)

| Color | Hex | Usage | Meaning |
|-------|-----|-------|---------|
| Green | #2E7D32 | On track, target met, positive change | No action needed |
| Yellow/Amber | #F9A825 | At risk, approaching threshold | Monitor, investigate |
| Red | #C62828 | Off track, target missed, negative change | Action required |
| Gray | #757575 | Baseline, prior period, neutral | Reference/comparison |
| Blue | #1565C0 | Primary brand/data, current period | Focus attention |

### Color Rules

1. **Maximum 5 colors per chart.** More than 5 forces legend lookups that break reading flow.
2. **Consistent color assignment across reports.** If "Project Alpha" is blue in the status report, it must be blue in the QBR deck. Inconsistency forces re-learning on every page.
3. **Color-blind safe palette.** 8% of men have color vision deficiency. Always pair color with a secondary encoding (pattern, label, icon). Never rely on red/green distinction alone -- add icons or text labels.
4. **Desaturation for less important data.** Use muted/lighter versions of colors for secondary series. The eye is drawn to saturated colors first.
5. **No pure red for general data.** Reserve red exclusively for negative/warning states. Using red as a general data color in a chart triggers false alarm responses.

---

## Data Density Rules for Client Audiences

### The 5-Second Rule

A client should understand the main message of any chart or dashboard panel within 5 seconds. If they cannot, the visualization is too complex.

**How to test:** Cover the chart title. Show the chart to someone unfamiliar with the project. If they cannot state the trend or comparison in one sentence within 5 seconds, simplify.

### Density Tiers by Audience

| Audience | Max Metrics per Page | Max Data Points per Chart | Annotation Level |
|----------|---------------------|--------------------------|-----------------|
| Executive (C-suite, owner) | 3-4 | 12 (monthly for a year) | Heavy -- explain every notable change |
| Manager (client PM, director) | 5-7 | 24 (weekly for 6 months) | Moderate -- explain deviations |
| Analyst (client ops team) | 8-12 | 52+ (weekly for a year) | Light -- they will explore the data |

### Data Reduction Techniques

- **Aggregate up:** If daily data creates noise, show weekly. If weekly is noisy, show monthly. Match time granularity to decision frequency.
- **Highlight the exception:** Show the full trend line but call out only the data points that deviate from expected. A flat line with one spike tells a clearer story than a labeled flat line.
- **Small multiples over complex overlays:** Instead of 5 lines on one chart, show 5 small identical charts with one line each. Easier to compare patterns than to untangle spaghetti.

---

## Dashboard Layout Principles

### Grid Structure

Use a consistent grid. The most effective client dashboard layout:

```
Row 1: [Status Banner -- overall health, one line]
Row 2: [KPI Card] [KPI Card] [KPI Card] [KPI Card]     <- 3-5 headline numbers
Row 3: [Primary Trend Chart -- full width]               <- the most important trend
Row 4: [Comparison Chart] [Composition Chart]             <- supporting detail
Row 5: [Data Table or Detail View]                        <- for those who dig deeper
```

### Information Flow

- **Top-left = most important.** Reading pattern is Z-shaped (left-to-right, top-to-bottom). Place the single most critical metric at top-left.
- **Above the fold = verdict.** Everything visible without scrolling should answer "how are we doing?" The scroll-below content answers "why?" and "what next?"
- **Progressive disclosure.** Dashboard is the summary. Clicking any element should drill down to detail. Never put detail on the main view.

### KPI Card Design

Each KPI card shows exactly four pieces of information:

```
[Metric Name]
[Current Value]     [Trend Arrow: up/down/flat]
[vs Target: X%]     [vs Prior Period: +/-Y%]
```

No sparklines inside KPI cards unless the dashboard tool renders them cleanly at small size. Poorly rendered sparklines add noise, not signal.

---

## Annotation and Callout Best Practices

### When to Annotate

Annotate any data point where:
- The metric crosses a threshold (green to yellow, yellow to red)
- An external event explains a change (holiday, campaign launch, client reorg)
- The trend reverses direction for the first time in 3+ periods
- The value hits an all-time high or low

### Annotation Format

Keep annotations to 10 words or fewer directly on the chart. Use a callout line pointing to the specific data point. If more context is needed, number the annotation and provide detail in a legend below the chart.

**Good annotation:** "Campaign launched Mar 3" pointing to a traffic spike.
**Bad annotation:** "We launched the new email campaign on March 3rd which resulted in a significant increase in web traffic from the targeted segments" -- this belongs in the narrative section, not on the chart.

---

## Mobile and Print Considerations

### Mobile Optimization

- Minimum font size: 14px for values, 12px for labels
- Charts must be legible at 375px width (standard mobile viewport)
- Replace hover-dependent interactions with tap-to-expand
- KPI cards stack vertically on mobile -- design for single-column reading
- Test every dashboard on an actual phone before sending the link to a client

### Print Optimization

- All charts must render clearly in grayscale (color should not be the only differentiator)
- Use patterns (hatching, dots, dashes) alongside colors for categorical distinction
- Headers and footers on every printed page: client name, report date, page number, confidentiality notice
- PDF export should maintain layout -- test export before establishing the template as standard

---

## Accessibility in Data Visualization

### Mandatory Accessibility Standards

1. **Color is never the sole encoding.** Pair color with shape, pattern, label, or position. A red/green traffic light must also include text labels ("On Track" / "At Risk" / "Off Track") or icons.
2. **Alt text for all charts.** When dashboards are shared as images or PDFs, include a text description: "Line chart showing monthly revenue from January to June 2026, trending upward from $45K to $78K with a dip in March."
3. **Minimum contrast ratio 4.5:1** for text on colored backgrounds. Use a contrast checker tool. Light gray text on white backgrounds fails accessibility standards and is hard to read on projectors.
4. **Data tables as fallback.** Every chart should have a corresponding data table available (hidden by default, accessible via toggle or screen reader). Charts communicate quickly; tables communicate precisely.
5. **Font choices.** Use sans-serif fonts (Inter, Helvetica, Arial) for data labels. Minimum 11pt for print, 14px for screen. Never use decorative fonts in data visualizations.
6. **Animation restraint.** Loading animations are acceptable. Data-encoding animations (bars growing, lines drawing) delay comprehension and can cause issues for users with vestibular disorders. Use sparingly and provide a "reduce motion" option.
