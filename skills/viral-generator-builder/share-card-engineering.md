# Share Card Engineering for Viral Generators

## OG Image Specifications by Platform

Each social platform renders share cards differently. Design for the platform where most of your shares happen.

| Platform | OG Image Size | Display Behavior | Design Priority |
|---|---|---|---|
| **Twitter/X** | 1200x628px (1.91:1) | Large card: full-width image above title/description. Summary card: small square thumbnail | Large card is essential for generators. Small card = invisible in timeline. Set `twitter:card` to `summary_large_image` |
| **Facebook** | 1200x630px (1.91:1) | Image above title/description. Rounded corners (8px crop). Dark mode inverts background | Test in dark mode. White backgrounds become dark gray. Ensure text has enough contrast in both modes |
| **LinkedIn** | 1200x627px (1.92:1) | Image above title/description. Professional audience = cleaner design expectations | LinkedIn crops more aggressively on mobile. Keep key content in center 80% of image |
| **iMessage** | 1200x630px | Rich link preview: image + title + description. Small format in conversation bubbles | Mobile-only viewing. Text must be readable at thumbnail size. This is where most direct shares happen |
| **WhatsApp** | 1200x630px | Square crop for thumbnail, full image on click. Title + description below | The thumbnail crop is SQUARE (center-crop). Your result text must survive a square crop of the center |
| **Discord** | 1200x630px | Embedded card with image, title, description. Side color bar matches embed color | Discord users are tech-savvy. Low-effort share cards get mocked. Higher quality bar than other platforms |

## Dynamic OG Image Generation

Static OG images show the same preview for every share. Dynamic OG images show the USER'S specific result -- dramatically increasing click-through.

| Approach | How It Works | Latency | Cost | Best For |
|---|---|---|---|---|
| **Server-side rendering** (Puppeteer/Playwright) | Render HTML template to image on the server. Cache aggressively | 500-2000ms first render, <50ms cached | $5-20/month hosting (Vercel/Railway) | Full control over design. Best quality. Most common approach |
| **Cloudinary/imgix text overlays** | Use image transformation API to overlay text on a base template | 100-300ms (CDN-cached) | Free tier: 25K transformations/month. Paid: $89+/month | Simple text-on-image results. No complex layouts. Fast and reliable |
| **Vercel OG** (@vercel/og) | React components rendered to images at the edge. JSX-based templating | 50-200ms at edge | Free on Vercel (included in hosting) | Vercel-hosted generators. React developers. Excellent DX |
| **Pre-generated + stored** | Generate all possible result images at build time. Store in CDN | <10ms (static file) | Storage cost only ($0.01-1/month for most generators) | Generators with <100 possible results. Name generators with fixed output sets |

**Dynamic OG meta tag pattern**:
```
<meta property="og:image" content="https://yourgenerator.com/api/og?result=midnight-architect&name=John" />
```

Each unique result URL generates a unique OG image. Social platforms cache aggressively (Facebook: 24-48 hours, Twitter: 7 days). Use the Facebook Sharing Debugger and Twitter Card Validator to test and refresh cache.

## Screenshot Optimization

40-60% of generator shares happen via screenshot, NOT share buttons. Design the result page for screenshot-ability.

| Principle | Implementation | Why |
|---|---|---|
| **Result fits in one screen** | No scrolling required to see full result. Mobile viewport (375x667px logical) is the constraint | If the result requires scrolling, the screenshot will be incomplete. Users won't take multiple screenshots |
| **Branding visible but subtle** | Logo or domain name in corner of result area. NOT a watermark -- a natural part of the design | When screenshots are shared without the link, your brand is still visible. But aggressive watermarks make users AVOID sharing |
| **High contrast text** | Result text is the largest element. Minimum 24px on mobile. Dark text on light background OR light on dark. No medium contrast | Screenshots are often viewed at small sizes in social feeds. Low-contrast text becomes unreadable |
| **Clean background** | Solid or simple gradient background. No busy patterns that compress poorly in screenshots | JPEG/WebP compression artifacts are worse on complex backgrounds. Screenshots shared via messaging apps get compressed aggressively |
| **No UI chrome in result area** | Share buttons, navigation, and other UI elements are BELOW the result area, not inside it | Users crop screenshots to just the result. If share buttons are inside the result area, they look weird in the crop |

## Share Button UX

| Pattern | How It Works | Share Rate Impact |
|---|---|---|
| **Share buttons at eye level** | Place share buttons immediately below the result, above any other content | Baseline. This is the minimum viable share UX |
| **Pre-written share text** | "I got [Result Name]! What are you? [link]" auto-filled in share dialog | +30-50% share rate vs empty share dialog. Users don't want to write share text |
| **Copy link button** | Dedicated "Copy my result link" button with animated confirmation | +15-25% share rate. Many users prefer copying links to using platform-specific share buttons |
| **Native share API** | `navigator.share()` on mobile. Shows system share sheet with all installed apps | +20-40% share rate on mobile (not available on desktop). The share sheet includes messaging apps that don't have dedicated buttons |
| **"Compare with friends" CTA** | "Send to a friend to compare results" button that generates a unique comparison link | +10-20% share rate. Changes sharing from "look at me" to "let's do this together" |

**Share button hierarchy** (test for your audience, but this order works for most generators):
1. Copy Link (universal, no platform friction)
2. Native Share (mobile only, catches messaging apps)
3. Twitter/X (public sharing, highest viral reach per share)
4. WhatsApp (private sharing, highest in non-US markets)
5. Facebook (declining but still large for 35+ audience)

## Share Card A/B Testing

| What to Test | Variants | Metric | Minimum Sample |
|---|---|---|---|
| **Image style** | Photo-realistic vs illustrated vs typographic | Share-to-click rate | 500 shares per variant |
| **Text size on OG image** | Large result text vs result + description | Click-through rate from social | 500 impressions per variant |
| **Share text phrasing** | "I got [X]!" vs "My result: [X]" vs "Find out what you are:" | Share rate from result page | 1,000 result views per variant |
| **CTA placement** | Share above fold vs below result | Share rate | 1,000 result views per variant |
| **Curiosity vs reveal** | OG image shows full result vs partial (blurred/hidden) | Click-through from share to generator | 500 shares per variant. Curiosity gap usually wins by 30-50% |

## Platform-Specific Share Gotchas

| Platform | Gotcha | Solution |
|---|---|---|
| **Twitter/X** | Cards are cached for 7 days. Can't update OG image after first share | Use unique URLs per result so each result gets its own card. Append `?r=result-id` to base URL |
| **Facebook** | OG image must be >200x200px or Facebook ignores it entirely. Caches 24-48 hours | Use Facebook Sharing Debugger to pre-cache images before launch. Test with `og:image:width` and `og:image:height` tags |
| **LinkedIn** | Doesn't support `twitter:card` tags. Only reads OpenGraph tags | Always include both `og:image` AND `twitter:image` tags. Don't rely on fallback behavior |
| **iMessage** | Rich link previews only generate if server responds in <3 seconds | OG image generation must be FAST. Pre-generate or cache. Timeout = plain text link (ugly, no preview) |
| **WhatsApp** | Caches link previews device-side. No way to force refresh | Use versioned URLs (`?v=2`) if you need to update share cards after deployment |
| **Slack** | Unfurls links with OG data. Shows full description unlike most platforms | Your `og:description` actually gets read on Slack. Make it compelling, not just SEO filler |
