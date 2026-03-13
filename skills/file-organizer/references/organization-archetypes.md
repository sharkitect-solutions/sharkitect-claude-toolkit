# Organization Archetypes

Named organizational profiles for common user types. Each archetype defines a folder structure, naming convention, automation rules, and pitfalls specific to that profile.

---

## Developer Workspace

```
~/dev/
  projects/           # Active code repositories (git-managed)
  experiments/        # Throwaway code, POCs, learning exercises
  tools/              # Scripts, utilities, dotfile backups
  docs/               # Technical notes, architecture decisions
  downloads-dev/      # SDKs, installers, binary tools
```

**Naming:** All lowercase, kebab-case. No spaces (breaks shell scripts, Makefiles). Prefix experiments with date: `2025-03-try-rust-wasm/`. Never nest repos inside other repos.

**Automation:** `experiments/` older than 90 days -> archive. `downloads-dev/` older than 30 days -> delete (re-downloadable). Symlink tools scripts to `~/bin/`.

**Pitfalls:** Cloning repos into Desktop or Documents. Keeping stale branches as separate folder clones. Storing secrets in project folders without `.gitignore`.

---

## Creative Professional

```
~/creative/
  projects/                    # Active client or personal projects
    YYYY-MM-client-project/    # Date prefix for chronological sorting
      assets/                  # Source files (PSD, AI, RAW)
      exports/                 # Deliverables (PNG, PDF, MP4)
      briefs/                  # Client requirements, mood boards
  assets-library/              # Reusable assets NOT tied to projects
    fonts/
    stock-photos/
    templates/
    brand-kits/
  archive/YYYY/                # Completed projects (compressed)
  inbox/                       # New files to sort
```

**Naming:** Projects: `YYYY-MM-clientname-description`. Deliverables: `projectname-variant-WxH.ext`. Versions: use folders (`v1/`, `v2/`, `final/`), never filename suffixes.

**Automation:** Inbox scanned daily (images to current project assets/, docs to briefs/). Projects untouched 6 months -> prompt to archive. RAW photos auto-organized by EXIF date.

**Pitfalls:** Final deliverables only in email attachments. Assets-library as flat dump without subcategories. Missing exports/ subfolder (deliverables mixed with working files).

---

## Business User

```
~/business/
  clients/                     # Client-specific folders
    client-name/
      contracts/
      deliverables/
      correspondence/
  finances/                    # Financial documents (see invoice-organizer)
    invoices/
    receipts/
    tax/YYYY/
  hr/                          # Policies, templates, onboarding
  operations/                  # SOPs, vendor docs, licenses
  templates/                   # Reusable document templates
  archive/YYYY/                # Closed engagements, old fiscal years
```

**Naming:** Client folders: `company-name` (kebab-case). Documents: `YYYY-MM-DD-type-description.ext`. Contracts: `YYYY-MM-DD-contract-clientname-description.pdf`.

**Automation:** Receipts older than 7 years + current -> archive (tax retention). Clients with no activity 12 months -> prompt to archive. Quarterly SOP review for staleness.

**Pitfalls:** Client folders mixing all document types at one level. Tax documents scattered instead of centralized. Email as the filing system. No archive policy (5-year-old clients at same level as active).

---

## Personal / Home User

```
~/personal/
  documents/                   # Personal documents
    medical/
    financial/
    legal/
    education/
  photos/YYYY/                 # Event-based: YYYY-MM-event-name/
  media/                       # Music, videos, ebooks
  downloads-sorted/            # Categorized downloads
    installers/
    reference/
  archive/                     # Old files, previous computer backups
```

**Naming:** Photos: keep camera names inside dated event folders. Documents: `type-description.ext` (passport-scan.pdf, lease-2025.pdf). Keep it simple -- personal files rarely need date prefixes unless the date is meaningful.

**Automation:** Downloads older than 7 days -> `_review/`. Installers (.exe, .msi, .dmg) older than 30 days -> delete. Photos auto-organized by EXIF date on import. Medical and legal -> never auto-archive (permanent retention).

**Pitfalls:** Everything in Downloads permanently. Photos organized by device instead of date/event. No separation between personal and work files. Keeping installers "just in case."

---

## Archetype Selection Guide

| Question | Developer | Creative | Business | Personal |
|----------|-----------|----------|----------|----------|
| Primary file types? | Code, config | PSD, RAW, video | PDFs, DOCX, XLS | Photos, docs, media |
| How do you find files? | By project name | By client + date | By client or category | By date or event |
| What gets archived? | Stale experiments | Completed projects | Closed engagements | Old backups |
| Automation priority? | Downloads cleanup | Camera import sort | Receipt filing | Downloads cleanup |

Most users blend two archetypes. Keep them physically separated (different root folders) so naming conventions and lifecycle rules do not conflict.
