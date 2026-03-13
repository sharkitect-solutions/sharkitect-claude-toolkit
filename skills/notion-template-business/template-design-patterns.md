# Notion Template Design Patterns

## Database Architecture for Sellable Templates

The database structure IS the product. A template with poor database architecture creates support tickets and refund requests.

| Pattern | When to Use | Structure | Gotcha |
|---|---|---|---|
| **Single database + views** | Simple templates (task tracker, habit tracker) | 1 database, 4-6 views (table, board, calendar, gallery) | Users often don't know how to switch views. Add a "Views Guide" page with links to each view |
| **Hub-and-spoke** | Business templates (CRM, project management) | Central dashboard links to 3-5 related databases | Relations between databases are the #1 source of user confusion. Label every relation property clearly |
| **Linked databases** | Multi-area templates (life OS, second brain) | Master databases in a hidden "Backend" section, linked database views throughout | Users accidentally edit the linked view filters, breaking the template. Add "DO NOT EDIT" callouts on backend databases |
| **Template button pattern** | Templates with repeatable workflows | Databases with template buttons pre-configured for common entries | Template buttons don't copy over when users duplicate the template. Test the duplicate flow BEFORE listing |

## Formula Complexity Management

| Complexity Level | What's Appropriate | Example | Risk |
|---|---|---|---|
| **Level 1: Simple** (property references, basic math) | Any template | `prop("Price") * prop("Quantity")` | LOW -- users can modify these |
| **Level 2: Conditional** (if/else, format) | Pro templates | `if(prop("Status") == "Done", "Complete", "In Progress")` | MEDIUM -- users may break syntax when editing |
| **Level 3: Complex** (nested if, dateBetween, regex) | Premium templates only | Multi-condition formulas with date math and string manipulation | HIGH -- any edit breaks the formula. MUST document "DO NOT EDIT THIS FORMULA" with explanation of what it does |
| **Level 4: Rollup chains** (rollups of rollups) | Avoid unless necessary | Rollup that references a rollup in another database | VERY HIGH -- one broken link cascades through the entire template. Breaks are invisible to users |

**Formula documentation rule**: Every Level 3+ formula gets a callout block directly above or below it explaining: (1) what it calculates, (2) what inputs it depends on, (3) why the user should NOT edit it directly.

## Onboarding Flow Design

The first 5 minutes after template duplication determine whether the user keeps or refunds.

| Step | What to Include | Format | Why |
|---|---|---|---|
| 1. Welcome page | What this template does (1 sentence), who it's for, estimated setup time | Full-width page with banner image | Sets expectations. "This will take 10 minutes to set up" prevents "this is too complicated" abandonments |
| 2. Quick start | 3-5 numbered steps to get first value | Toggle blocks for each step with screenshots | Users need a WIN within 5 minutes. First win = first data entered and seeing it reflected in a view |
| 3. Sample data | Pre-populated example entries in every database | Real-looking data, not "Test 1, Test 2" | Sample data shows what the template looks like when actually used. Empty databases look broken. Include a "Delete sample data" button |
| 4. Customization guide | What to change (colors, names, categories) and what NOT to change (formulas, relations) | Clearly labeled sections: "Customize These" vs "Don't Touch These" | Prevents accidental breakage while encouraging personalization |
| 5. Feature deep-dives | Detailed walkthroughs of advanced features | Linked pages (not inline) -- optional reading | Users who want depth can find it. Users who want simplicity aren't overwhelmed |

## Template Visual Design Principles

| Principle | Implementation in Notion | Impact on Sales |
|---|---|---|
| **Consistent icon system** | Pick ONE icon style (outline, filled, or emoji) and use it everywhere. Never mix styles | Inconsistent icons signal amateur design. The #1 visual quality indicator reviewers check |
| **Color coding with purpose** | Max 3-4 colors. Each color means something (red=urgent, green=complete, blue=in-progress) | Random color usage makes templates feel chaotic. Purposeful color = "this person thought about the design" |
| **White space** | Use dividers, callout blocks, and empty space intentionally. Don't pack every page full | Cramped templates feel "cheap." White space increases perceived value and reduces cognitive load |
| **Header hierarchy** | H1 for page titles only. H2 for sections. H3 for subsections. Never skip levels | Clear hierarchy helps users navigate. Inconsistent headers make templates feel disorganized |
| **Cover images** | Custom cover images for every database page and key sections. NOT stock photos. | Custom covers signal premium quality. Canva templates for Notion covers work well (1500x600px) |

## Notion-Specific UX Patterns That Sell

| Pattern | How It Works | Why It Increases Sales |
|---|---|---|
| **Dashboard with linked databases** | Central page showing summary views of all databases. Status counts, recent items, upcoming deadlines | Dashboard is the "money shot" for preview images. First thing users see = first impression |
| **Status automations** | Notion automations that update status, send notifications, or create items automatically | "It does things for me" is the highest-value perception. Even simple automations feel premium |
| **Button actions** | Notion buttons that create pre-filled pages, change statuses, or trigger automations | Buttons reduce friction. "Click this button to add a new client" > "Create a new page in the Clients database" |
| **Template buttons in databases** | Pre-configured templates for common entry types (meeting notes, project briefs, client onboarding) | Users see "this template thinks of everything." Reduces blank page anxiety |
| **Synced blocks for repeated content** | Headers, navigation, or key metrics that appear on multiple pages via synced blocks | Users update once, changes everywhere. Feels "smart" and reduces maintenance |
| **Relation-powered filters** | Views that automatically filter based on related database selections | "Select a project and see only that project's tasks" -- feels like a real app, not a template |

## Template Testing Checklist (Before Listing)

| Test | How to Test | What Breaks |
|---|---|---|
| **Duplicate test** | Share template link, duplicate to a NEW workspace (not the same one) | Template buttons, some automations, API connections, and integrations do NOT survive duplication |
| **Empty state test** | Delete ALL sample data. Does the template still make sense? | Rollups showing errors, formulas returning #ERROR, views showing blank instead of helpful empty states |
| **Mobile test** | Open every page on Notion mobile app | Complex layouts with columns break on mobile. Multi-select properties overflow. Gallery views may not show images |
| **New user test** | Give template to someone unfamiliar with Notion. Watch them use it (no help) | Where they get stuck = where your documentation is inadequate. If they ask "what do I do next?" = onboarding flow is broken |
| **Scale test** | Add 50-100 entries to each database | Some views/formulas slow down with more data. Rollups across large databases can lag significantly |
| **Formula resilience test** | For each formula: delete the properties it references. What happens? | Formulas should degrade gracefully (show empty or fallback) not show cryptic errors |

## Template Versioning Strategy

| Scenario | How to Handle | Communication |
|---|---|---|
| Bug fix (broken formula, typo) | Fix in-place. Update template link. Email existing buyers | "We found and fixed [specific issue]. Re-duplicate using your original link for the updated version" |
| Feature addition (new view, new automation) | Add to existing template. Update listing. Email buyers about new feature | "We added [feature] to your template. Re-duplicate for the update, or add it manually: [instructions]" |
| Major version (v2 with restructured databases) | Create new listing. Offer existing buyers discount (50-75% off) | "Template v2 is here with [major changes]. As an existing owner, get 60% off. Your v1 still works perfectly" |
| Notion platform update (new features available) | Evaluate if new Notion features improve the template. If yes, update | Not every Notion update requires a template update. Only update if the new feature genuinely improves user experience |
