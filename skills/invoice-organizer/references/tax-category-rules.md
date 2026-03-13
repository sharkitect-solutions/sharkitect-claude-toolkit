# Tax Category Rules and Expense Classification

## IRS Schedule C Expense Categories

These are the 13 standard expense categories for sole proprietors and single-member LLCs. Every business invoice should map to one of these (or "Other Expenses" as a catch-all). Correct categorization determines deduction eligibility and audit risk.

| Line | Category | Deductible | Common Invoice Types | Edge Cases |
|------|----------|-----------|---------------------|------------|
| 8 | Advertising | 100% | Google Ads, Facebook Ads, print ads, promotional materials, website costs | Business cards = advertising, not office supplies. Sponsorships = advertising if branding visible. |
| 9 | Car & Truck Expenses | Varies | Fuel, maintenance, insurance, lease payments | Must choose standard mileage OR actual expenses for the year, cannot mix. See vehicle section below. |
| 10 | Commissions & Fees | 100% | Contractor referral fees, platform fees, affiliate commissions | Stripe/PayPal processing fees go here, NOT bank charges. |
| 11 | Contract Labor | 100% | Freelancer invoices, 1099 contractors, subcontractors | Must issue 1099-NEC for payments >$600/year to any single contractor. |
| 13 | Depreciation | Varies | Equipment >$2,500, vehicles, furniture, machinery | Section 179 allows full first-year deduction up to $1,160,000 (2023). See CAPEX rules. |
| 15 | Insurance | 100% | Business liability, E&O, professional liability, property insurance | Health insurance for self-employed goes on Schedule 1 Line 17, NOT Schedule C. |
| 16a | Mortgage Interest | 100% | Mortgage interest on business property | Home office mortgage interest goes on Form 8829, not directly on Schedule C. |
| 17 | Legal & Professional Services | 100% | Attorney fees, CPA fees, bookkeeper, consultants | Tax preparation fees for business portion are deductible here. Personal tax prep is NOT. |
| 18 | Office Expenses | 100% | Software subscriptions, office supplies, printer ink, paper | SaaS tools used 100% for business = full deduction. Mixed-use tools = prorate by business %. |
| 20a | Rent - Vehicles/Equipment | 100% | Equipment leases, vehicle leases (business use %) | Copier lease = here. Office rent = Line 20b. |
| 20b | Rent - Other Business Property | 100% | Office rent, coworking membership, storage unit | Home office deduction uses Form 8829, not this line. |
| 25 | Utilities | 100% | Electric, gas, water, internet, phone (business portion) | Home internet/phone: deduct only the business-use percentage. 100% deduction only if separate business line. |
| 27 | Other Expenses | 100% | Education, training, books, bank fees, postage, shipping | Catch-all. If >5% of total deductions come from "Other", reclassify -- it signals lazy categorization to auditors. |

## Meals and Entertainment Rules (Post-2023)

This is the most commonly misclassified category and the most audited.

**Current rules (2023+):**
- Business meals: **50% deductible** (must have business purpose, not lavish/extravagant)
- Entertainment: **0% deductible** (concerts, sporting events, golf -- fully non-deductible since 2018 TCJA)
- Meals during travel: **50% deductible** (must be away from tax home overnight)
- Meals provided to employees for convenience of employer: **50% deductible**
- Company holiday party / team building meals: **100% deductible** (must include all employees)

**Documentation requirements for meals:**
Every meal receipt MUST record: (1) amount, (2) date, (3) place, (4) business purpose, (5) names of attendees and business relationship. Missing any of these = disallowed deduction under audit.

**Common misclassification traps:**
- Taking a client to a baseball game and buying food there: the tickets = entertainment (0%), the food = meal (50%) -- must split the receipt
- Coffee shop while working alone: deductible ONLY if you are traveling away from tax home. Working at a local coffee shop is NOT deductible.
- Team lunch at a restaurant: 50% deductible. Team lunch catered to the office: 50% deductible (was 100% in 2021-2022, reverted).

## Home Office Deduction

Two methods -- the choice affects how invoices are categorized:

**Simplified method:** $5 per square foot, max 300 sq ft ($1,500 max deduction). No need to categorize individual home expenses. Cannot carry over losses.

**Regular method (Form 8829):** Calculate business-use percentage (dedicated office sq ft / total home sq ft). Apply that percentage to:
- Mortgage interest or rent
- Property taxes
- Homeowner's insurance
- Utilities (electric, gas, water, internet)
- Repairs (whole-house repairs get prorated, office-only repairs get 100%)

**Invoice categorization impact:** Under regular method, every utility bill, insurance payment, and repair invoice needs the home office percentage applied. Tag these invoices with `[HOME-OFFICE-PRORATE]` during filing so the accountant can apply the correct percentage.

## Vehicle Expense Methods

**Standard mileage rate (2024):** $0.67/mile for business use. Simple, but requires a mileage log (date, destination, business purpose, miles driven). No invoice categorization needed beyond the log.

**Actual expense method:** Categorize every vehicle invoice:
- Gas/fuel -> Car & Truck (Line 9)
- Insurance -> Car & Truck (Line 9)
- Repairs/maintenance -> Car & Truck (Line 9)
- Lease payments -> Rent (Line 20a), prorated by business-use %
- Purchase/loan -> Depreciation (Line 13)

**Critical rule:** Once you choose a method for a vehicle, you MUST use the same method for the life of that vehicle (with limited exceptions for leased vehicles). This decision happens at tax filing, but the invoice filing system must preserve enough detail for either method.

## Receipt Retention Requirements

| Situation | Minimum Retention | Reason |
|-----------|------------------|--------|
| Standard business expenses | 3 years from filing date | IRS statute of limitations for standard audits |
| Income underreported by >25% | 6 years | Extended audit window |
| Suspected fraud or no return filed | Unlimited | No statute of limitations |
| Property/equipment (depreciation) | Life of asset + 3 years | Must substantiate basis through entire depreciation period |
| Employment tax records | 4 years after tax due/paid | Different from income tax schedule |

**Practical recommendation:** Keep all business receipts for 7 years. Storage is cheap. The cost of missing a receipt during an extended audit far exceeds the cost of storage.

**Digital receipt requirements:** The IRS accepts digital copies as substantiation IF: (1) the digital copy is legible and complete, (2) you can produce it on request, (3) the original was not altered. Scanned receipts saved as PDF satisfy these requirements. Phone photos are acceptable if legible.

**Thermal receipt warning:** Thermal paper (gas stations, restaurants, retail) fades within 6-18 months. Scan or photograph thermal receipts immediately. A blank piece of paper proves nothing during an audit.

## State-Specific Considerations

State tax rules add categories beyond federal Schedule C:

| State | Additional Requirement | Impact on Filing |
|-------|----------------------|-----------------|
| California | Franchise Tax Board requires separate tracking of CA-source income | Tag invoices with state of service delivery |
| New York | Unincorporated Business Tax on NYC residents | Separate city-level expense tracking |
| Texas | No state income tax, but franchise tax on gross receipts >$1.23M | Track gross receipts separately from net income categories |
| Florida | No state income tax | Federal categories sufficient |
| Washington | B&O tax on gross receipts (varies by classification) | Classify invoices by B&O category: retailing, service, manufacturing |

When filing invoices for multi-state businesses, add a state tag to each invoice to simplify state-specific reporting. Format: `[STATE:CA]` or `[STATE:MULTI]` for invoices that span multiple states.
