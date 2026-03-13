# Framework-Specific Slop Patterns

Load when deslopping code written in a specific framework (React/Next.js, Express, Django, Rails, etc.) where generic language-level patterns miss framework-idiomatic issues.

## React / Next.js Slop

| Pattern | Example | Why It's Slop | Fix |
|---|---|---|---|
| Fragment wrapping a single child | `<>{singleElement}</>` | Fragment only needed for multiple siblings. Single child needs no wrapper. | Remove Fragment, return child directly |
| useEffect for derived state | `useEffect(() => setFullName(first + last), [first, last])` | Computed value doesn't need state + effect. Causes extra render. | `const fullName = first + last` (compute during render) |
| useCallback on non-memoized child | `useCallback(fn, [deps])` passed to a non-React.memo'd component | useCallback does nothing if the child rerenders regardless | Remove useCallback unless child is memoized or in a dependency array |
| State for form inputs with no validation | `const [name, setName] = useState('')` for a simple form with no real-time validation | Uncontrolled refs or form library handles this without per-keystroke rerenders | Use `useRef` or form library (react-hook-form) for simple forms |
| `'use client'` on every component | Every file starts with `'use client'` in Next.js App Router | Defeats the purpose of server components. AI defaults to client because it's "safer". | Remove `'use client'` unless the component uses hooks, event handlers, or browser APIs |
| Dynamic import of tiny components | `const Button = dynamic(() => import('./Button'))` | Code splitting a 2KB component adds loading complexity with no measurable benefit | Only dynamic import components > 50KB or those using heavy libraries |
| Prop spreading with no type narrowing | `<Component {...props} />` where props is `any` or untyped | Bypasses type checking, can pass invalid DOM attributes | Destructure needed props explicitly |
| Event handler as inline arrow in JSX | `onClick={() => handleClick(id)}` in a list of 500+ items | Creates new function reference per render per item. Causes unnecessary rerenders in memoized lists. | Define handler outside JSX with useCallback, or use data attributes + delegation |
| Redundant key on single static element | `<div key="container">...</div>` on a non-list element | key is only needed for list reconciliation | Remove key attribute |

### Next.js App Router Specific

| Pattern | Why It's Slop | Fix |
|---|---|---|
| `async` on client component functions | Client components cannot be async. AI adds it "just in case". | Remove async. Use useEffect or SWR/React Query for data fetching in client. |
| Fetching data in client component that could be server | `useEffect(() => fetch('/api/data'))` in a component with no interactivity | Server component with direct database/API call is simpler and faster | Move data fetching to server component, pass as props |
| Creating API routes for data the page could fetch directly | `/api/products` route called by the page that renders products | In App Router, server components can query the database directly | Fetch in server component, remove API route if only used internally |
| `export const dynamic = 'force-dynamic'` on static pages | AI adds this when it sees database queries, even if data changes rarely | Disables static generation for no reason. Forces every request to be dynamic. | Remove unless data genuinely changes per-request. Use `revalidate` for ISR instead. |

## Express / Fastify / Node.js Backend Slop

| Pattern | Example | Why It's Slop | Fix |
|---|---|---|---|
| Try/catch wrapping entire route handler | `try { ...all code... } catch(e) { res.status(500).json({error: 'Internal error'}) }` | Express error middleware already handles uncaught errors. Duplicated at every route. | Use express error middleware. Only try/catch specific operations that need custom error responses. |
| Validating req.body fields manually | `if (!req.body.name \|\| typeof req.body.name !== 'string')` repeated per field | Verbose, inconsistent, misses edge cases | Use Zod, Joi, or express-validator. Define schema once. |
| Wrapping res.json in a utility function | `function sendSuccess(res, data) { res.json({ success: true, data }) }` | Thin wrapper adds indirection with zero value | Call `res.json()` directly |
| Middleware for every trivial check | `const requireAdmin = (req, res, next) => { if (req.user.role === 'admin') next(); else res.status(403).json(...) }` duplicated across files | Same check repeated as middleware in multiple route files | Centralize auth middleware, compose with role parameter |
| Logging every request field | `console.log('Request:', JSON.stringify(req.body, null, 2))` | Debug logging left in production code | Use a structured logger (pino, winston) with log levels |
| Async handler wrapper on sync route | `asyncHandler(async (req, res) => { res.json({ status: 'ok' }) })` | No async operations in this handler | Remove async and wrapper |

## Django Slop

| Pattern | Example | Why It's Slop | Fix |
|---|---|---|---|
| Explicit `objects.all()` in queryset | `MyModel.objects.all().filter(active=True)` | `.all()` before `.filter()` is redundant -- filter already returns a queryset | `MyModel.objects.filter(active=True)` |
| Empty `class Meta: pass` | Model or form class with `class Meta: pass` | If Meta has no attributes, it does nothing | Remove entirely |
| `str()` on model returning `self.name` when field is already a string | `def __str__(self): return str(self.name)` | `self.name` is already a CharField (string). `str()` is redundant. | `return self.name` |
| Unnecessary `default=None` on nullable field | `models.CharField(null=True, blank=True, default=None)` | `None` is already the default for nullable fields | Remove `default=None` |
| Import of unused admin decorators | `from django.contrib.admin import register` but using `admin.site.register()` | Two registration methods imported, only one used | Remove unused import |
| View decorators repeated on class-based views | `@login_required` on every method of a view that already uses `LoginRequiredMixin` | Mixin already handles auth. Decorators are redundant. | Remove decorators, keep mixin |
| `get_queryset` that just returns `super().get_queryset()` | Override with no modification | Method override does nothing | Remove the method entirely |

## Rails Slop

| Pattern | Example | Why It's Slop | Fix |
|---|---|---|---|
| Explicit `self.` on reads inside model methods | `self.name` inside a model method | Ruby reads instance methods without `self.`. Only needed for assignment. | Remove `self.` on reads |
| `before_action` with single-method `only:` matching the method it's in | `before_action :set_user, only: [:show]` in a controller with only `show` | Only constraint is unnecessary when there's one action | Remove `only:` or move set_user logic inline |
| Wrapping `ActiveRecord::Base.transaction` around a single save | `transaction { record.save! }` | Single save is already atomic. Transaction is redundant. | Just call `record.save!` |
| `rescue => e` swallowing the exception | `rescue => e; Rails.logger.error(e); nil` | Silently returns nil, hiding the failure from callers | Let it raise, or rescue specific exceptions with meaningful handling |
| N+1 query pattern introduced by AI | Controller loads `@posts = Post.all`, view calls `post.author.name` | Classic N+1. AI doesn't add `includes` because it doesn't see the view. | `Post.includes(:author).all` |

## Style Conflict Resolution

When framework-specific slop overlaps with project conventions:

| Conflict | Resolution |
|---|---|
| Project uses inline arrows in JSX everywhere, but list has 500+ items | Fix only the performance-critical list. Leave other inline arrows. Note in report. |
| Project uses try/catch in every Express route (established pattern) | Leave it. This is local convention, not AI slop. Note: "project uses explicit try/catch per route, leaving in place." |
| Django project uses `objects.all().filter()` consistently | Leave it. Consistency > minor optimization. Only flag if inconsistent with surrounding code. |
| Project has no eslint/formatter but AI added consistent formatting | Leave formatting. Deslop targets artifacts, not style. AI-consistent formatting is an improvement over none. |
| Framework docs recommend one pattern, project uses another | Follow the project. Deslop aligns with the codebase, not with framework docs. |
