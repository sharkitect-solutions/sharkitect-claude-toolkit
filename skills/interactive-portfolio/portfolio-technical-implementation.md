# Portfolio Technical Implementation

## Framework Selection for Portfolio Sites

| Signal | Recommended Framework | Why | Gotcha |
|---|---|---|---|
| Developer portfolio (code quality matters) | **Astro** or **Next.js (static export)** | Astro: zero JS by default, fastest possible load. Ships HTML. Your portfolio performance IS your resume. Next.js: if you want to showcase React skills, use static export (no server required) | Astro: limited interactivity without explicit islands. If you need complex client-side features, add React/Svelte islands. Next.js: don't use server-side rendering for a portfolio -- it adds hosting complexity for zero benefit |
| Designer portfolio (visual polish matters) | **Next.js** or **SvelteKit** | Both support smooth page transitions and image optimization (next/image, enhanced:img). Design portfolios need visual craft in the site itself | Don't over-engineer. A designer's portfolio that takes 6 months to build with a custom CMS is 6 months not designing. Ship fast, iterate later |
| Creative portfolio (experimental OK) | **SvelteKit** or **Three.js + vanilla** | SvelteKit: smaller bundle, smoother animations. Three.js: if 3D is part of your creative practice. WebGL portfolios are impressive when they work | 3D portfolios exclude visitors with older devices, slow connections, or accessibility needs. Always provide a fallback. Test on a 5-year-old phone |
| Freelancer/agency (speed to launch) | **Astro** with a CMS (Contentful, Sanity, or even Markdown) | Content-focused. Easy to update projects without code changes. Fast build times | Don't use WordPress for a developer/agency portfolio in 2026. It signals outdated technical skills regardless of the design quality |
| Minimal portfolio (just ship it) | **Plain HTML/CSS** or **Astro** with Markdown | Zero dependencies. Fastest possible. Never breaks. Never needs updating | If you're a frontend developer, "plain HTML" might signal lack of framework experience. Use your judgment based on target role |

**The meta-decision**: Your portfolio framework IS a technology choice that hiring managers evaluate. A React developer should probably use Next.js. A performance-obsessed developer should use Astro. A creative technologist can use whatever pushes boundaries. Match the framework to the story you're telling about yourself.

## Performance Budgets for Portfolios

Portfolio-specific budgets. These are stricter than general web performance because your portfolio IS a performance sample.

| Metric | Developer Portfolio | Designer Portfolio | Creative Portfolio | Why This Threshold |
|---|---|---|---|---|
| LCP (Largest Contentful Paint) | <1.5s | <2.0s | <2.5s | Developer portfolios are judged on performance. 1.5s is "excellent" in Core Web Vitals. Designer/creative portfolios get slightly more lenient because image-heavy content has higher LCP |
| CLS (Cumulative Layout Shift) | <0.05 | <0.1 | <0.1 | Layout shifts make portfolios feel janky. Developer portfolios: 0.05 shows attention to detail. Design portfolios: 0.1 is acceptable with hero image loading |
| TBT (Total Blocking Time) | <100ms | <200ms | <300ms | JavaScript blocking. Developer portfolios should be lean. Creative portfolios may need more JS for interactions |
| Total page weight | <500KB (first load) | <1MB | <2MB | Including all images above fold. Use lazy loading for below-fold content |
| Time to Interactive | <2s | <3s | <4s | How long until the portfolio is usable. Creative portfolios get more loading time IF the loading experience is designed |

### Image Optimization (the biggest performance lever)

| Technique | Implementation | Impact |
|---|---|---|
| Modern formats | WebP (95% browser support) or AVIF (85% support). Use `<picture>` with fallback. Astro/Next.js handle this automatically | 30-50% smaller than JPEG at same visual quality |
| Responsive images | `srcset` with 3-4 breakpoints: 400w, 800w, 1200w, 2400w. Serve appropriate size for device | Mobile devices loading desktop-size images is the #1 portfolio performance killer |
| Lazy loading | `loading="lazy"` on all images below the fold. Native browser lazy loading, no JS library needed | Reduces initial page weight by 50-80% for image-heavy portfolios |
| Blur placeholder | Low-resolution placeholder (20px wide, base64 encoded inline) while full image loads. next/image does this automatically | Eliminates layout shift and perceived loading time |
| Project thumbnails | 600-800px wide maximum for grid cards. JPEG quality 75-80 is visually identical to 100 at this size | Most portfolios serve 2000px thumbnails in 300px containers. Insane waste |

## Hosting and Deployment

| Platform | Best For | Free Tier | Custom Domain | Gotcha |
|---|---|---|---|---|
| **Vercel** | Next.js portfolios (native integration) | 100GB bandwidth, 100 deployments/day | Free (HTTPS automatic) | Free tier has "Powered by Vercel" unless you use a custom domain. Cold start on serverless functions if using SSR (don't use SSR for portfolios) |
| **Netlify** | Static sites, Astro, any JAMstack | 100GB bandwidth, 300 build minutes/month | Free (HTTPS automatic) | Build minutes limit can be tight if you rebuild frequently during development. Use `netlify dev` locally |
| **GitHub Pages** | Plain HTML, Jekyll, minimal sites | Unlimited for public repos | Free (with CNAME setup) | No server-side features. No redirects (client-side only). No form handling (use external service). Great for simplicity, limiting for features |
| **Cloudflare Pages** | Performance-critical portfolios | Unlimited bandwidth, 500 builds/month | Free (HTTPS automatic + CDN) | Best raw performance due to Cloudflare's edge network. Less ecosystem than Vercel/Netlify but faster globally |
| **Railway/Render** | Portfolios with backend features (contact form, CMS) | $5/month credit (Railway), 750 hours/month (Render) | Custom domain on paid plans | Overkill for static portfolios. Use only if you need a backend. Cold starts on free tiers |

**Deployment recommendation**: For 90% of portfolios, Vercel or Netlify free tier is correct. Don't self-host. Don't use a VPS. The time spent on infrastructure is time not spent on portfolio content.

## SEO for Personal Sites

Personal portfolio SEO matters for discoverability: "John Smith developer" should find your portfolio, not your LinkedIn.

| SEO Element | Implementation | Why It Matters for Portfolios |
|---|---|---|
| Title tag | `[Your Name] - [Role] | Portfolio`. Example: "Jane Doe - Senior Product Designer | Portfolio" | Hiring managers Google your name. Your portfolio should outrank LinkedIn and social profiles |
| Meta description | One sentence: what you do + what you're known for. 150-160 chars | Appears in search results. "Senior product designer specializing in fintech and design systems. Based in NYC." |
| OG tags (Open Graph) | `og:title`, `og:description`, `og:image` for every page. Create a custom OG image (1200x630px) with your name and role | When your portfolio link is shared on Slack, LinkedIn, or Twitter, the preview card matters. A portfolio with no OG image looks unprofessional |
| Structured data | `Person` schema: name, jobTitle, url, sameAs (social profiles). `WebSite` schema for the portfolio itself | Helps Google's Knowledge Panel. Your name + role may appear in branded search results |
| Sitemap | Generate automatically (Astro/Next.js plugins). Include all case study pages | Ensures Google indexes your case studies, not just your homepage |
| Canonical URLs | Self-referencing canonicals on all pages. If you cross-post case studies to Medium/dev.to, canonical should point to your portfolio | If your Medium article outranks your portfolio for a project name, you're giving SEO value to Medium instead of yourself |

## Analytics Setup

Track portfolio performance to understand what works and what doesn't.

| What to Track | Tool | Why | Gotcha |
|---|---|---|---|
| Page views by project | Plausible or Fathom (privacy-focused, no cookie banner needed) | Know which projects get attention. Invest in case studies for popular projects | Don't use Google Analytics. For a portfolio, you don't need the complexity, and the cookie banner hurts UX. Plausible: $9/month. Fathom: $14/month. Free alternative: Umami self-hosted |
| Contact form submissions | Your form provider (Formspree, Basin, or custom) | The only metric that truly matters: did the portfolio convert? | Track which page the visitor was on before submitting. This tells you which projects drive conversion |
| Scroll depth on case studies | Plausible or Fathom (built-in) | Know if people read your case studies or bounce at the hero image | If 80% bounce before the "results" section, your case study is too long or the middle section isn't engaging |
| Referral sources | Any analytics tool | Know where your visitors come from: LinkedIn, direct, Google, GitHub, Dribbble | If 90% is direct traffic, SEO isn't working. If 90% is LinkedIn, your portfolio depends on a single channel |
| Device breakdown | Any analytics tool | Know how visitors view your portfolio: mobile vs desktop | If 60%+ is mobile and your portfolio isn't mobile-optimized, you're losing the majority of visitors |

## Accessibility Requirements

Portfolio accessibility is both a moral imperative and a professional signal. An inaccessible developer portfolio signals inaccessible development practices.

| Requirement | Implementation | Why It Matters for Portfolios Specifically |
|---|---|---|
| Alt text on all images | Describe what's in the screenshot. "Dashboard showing user analytics with sidebar navigation" not "screenshot" | Project screenshots need meaningful alt text. Screen reader users should understand what the project looks like |
| Keyboard navigation | All interactive elements focusable. Tab order matches visual order. Focus indicators visible | Custom navigation, project filtering, and modals must be keyboard-accessible. Test with Tab key only |
| Color contrast | 4.5:1 for body text, 3:1 for large text (WCAG AA) | Light gray text on white background is the most common portfolio accessibility failure |
| Reduced motion | `prefers-reduced-motion` media query. Disable non-essential animations when set | Creative portfolios with heavy animation MUST respect this preference. It's not optional -- vestibular disorders affect 5-10% of adults |
| Semantic HTML | Use `<main>`, `<nav>`, `<article>`, `<section>`, `<header>`, `<footer>` | Semantic structure enables screen readers to navigate efficiently. `<div>` soup fails this |
| Focus management | When opening modals or project overlays, trap focus inside. Return focus when closed | Project detail modals that lose focus are navigation dead ends for keyboard users |
