---
name: file-organizer
description: "Use when organizing files and directories, cleaning up cluttered folders, establishing filing conventions, detecting and handling duplicate files, or designing folder taxonomy for projects. Do NOT use for invoice/financial document organization (use invoice-organizer), source code project structure (use senior-architect), or database file management."
---

# File Organization & Directory Architecture

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/platform-commands.md` | Executing file operations, writing scripts for moves/copies/deletes, detecting platform, handling path differences | Designing folder taxonomy, choosing organizational patterns, dedup strategy selection |
| `references/dedup-strategies.md` | Detecting duplicate files, choosing hash algorithms, handling near-duplicate images or documents, fuzzy filename matching | Folder taxonomy design, platform commands, automation setup |
| `references/organization-archetypes.md` | Designing folder structures for specific user profiles, choosing naming conventions, setting up project templates | Duplicate detection, platform-specific commands, hash algorithm selection |

## Scope Boundary

| In Scope | Out of Scope |
|----------|-------------|
| Folder taxonomy design and restructuring | Invoice/receipt/financial document filing (use invoice-organizer) |
| File naming conventions and enforcement | Source code project structure (use senior-architect) |
| Duplicate detection and resolution | Database file management and storage engines |
| Cross-platform file operations (Windows/macOS/Linux) | Cloud storage sync configuration (Dropbox, OneDrive admin) |
| Batch file moves with rollback capability | File recovery from corrupted/deleted media |
| Watched folder automation patterns | Disk partitioning or filesystem formatting |
| Archive aging and retention policies | Backup strategy and disaster recovery planning |
| File metadata preservation during operations | Digital asset management (DAM) platform administration |
| Conflict resolution for name collisions | Version control systems (use git-commit-helper) |
| Directory depth and cognitive load optimization | File encryption and security classification |

---

## Organizational Pattern Selection

Five named patterns cover the full spectrum of file organization needs. Selection depends on three factors: file volume, access frequency, and user profile.

### Decision Matrix

| Pattern | Best For | Volume | Access Pattern | Weakness |
|---------|----------|--------|---------------|----------|
| **Chronological** | Photos, logs, meeting notes | Any | Time-based retrieval | Cross-project search is slow |
| **Categorical** | Downloads, reference materials | <1,000 | Type-based retrieval | Categories multiply without governance |
| **Project-Based** | Active work with deadlines | 100-10,000 | Project context retrieval | Shared assets duplicated across projects |
| **Hybrid** | Business users, mixed content | 1,000-50,000 | Mixed retrieval patterns | Requires clear routing rules |
| **Activity-Based** | Creative professionals, pipelines | Any | Workflow-stage retrieval | Stage definitions drift without enforcement |

**Chronological** organizes by date (YYYY/YYYY-MM or YYYY/YYYY-Q#). Works when "when did I create this?" is the natural retrieval question. Fails when the same topic spans months -- a project folder with dates inside it is Project-Based, not Chronological.

**Categorical** groups by type or domain (documents/, images/, spreadsheets/). Natural for small collections. Breaks down past 1,000 files because categories either become too broad (100+ files per folder) or too specific (The Infinite Nest).

**Project-Based** groups by project or deliverable. Each project is self-contained with its own docs, assets, and output. Best when work has defined start/end dates. Fails when assets are shared across projects (logos, templates, brand guidelines) -- use a shared `_assets/` root folder alongside project folders.

**Hybrid** combines two patterns: typically Project-Based for active work with Categorical for reference materials. Requires explicit routing rules: "new files go to the active project folder; reference materials go to the library." Without routing rules, Hybrid degrades into The Flat Dump.

**Activity-Based** organizes by workflow stage (inbox/, in-progress/, review/, complete/, archive/). Natural for creative pipelines, editorial workflows, and processing queues. Files move through stages. Requires discipline to advance files -- stale items in "in-progress" for months signal a broken pipeline.

### Volume Thresholds

- **Under 100 files**: Any pattern works. Do not over-engineer. A single well-named folder may suffice.
- **100-1,000 files**: Two-level hierarchy is sufficient. One pattern handles this range.
- **1,000-10,000 files**: Hybrid pattern required. Pure Categorical or Chronological becomes unnavigable. Add search-friendly naming conventions.
- **10,000+ files**: Automation is mandatory. Manual organization is unsustainable at this scale. Implement watched folders with auto-routing rules.

---

## Folder Taxonomy Design

### Depth Limits

Cognitive load research (Miller, 1956: 7 plus-or-minus 2 items) applies to folder navigation. Each level of nesting requires a decision. Practical limits:

- **Maximum 4 levels deep** for any manually-navigated hierarchy. Beyond 4, users lose mental context of where they are.
- **3 levels is ideal** for most personal and small business use cases.
- **Exception**: Automated systems (build output, log archives) can go deeper because humans rarely navigate them manually.

Count: if a path exceeds `root/level1/level2/level3/level4/`, the taxonomy needs restructuring.

### Naming Conventions

| Convention | Example | Platform Implications |
|-----------|---------|----------------------|
| snake_case | `project_files` | Safe everywhere. Most portable. |
| kebab-case | `project-files` | Safe everywhere. Common in web/dev contexts. |
| Title Case | `Project Files` | Works on all platforms but spaces require quoting in CLI. |
| SCREAMING_SNAKE | `ARCHIVE_2024` | Use sparingly for top-level special directories. |

**Rules that prevent cross-platform failures:**
- No spaces in paths used by scripts or automation (spaces break unquoted shell variables)
- No characters from `< > : " / \ | ? *` -- these are reserved on Windows
- Keep path components under 255 characters (NTFS and ext4 per-component limit)
- Total path under 260 characters on Windows unless long path support is enabled (registry key `LongPathsEnabled`). Linux allows 4,096 characters.
- Avoid leading dots on Windows (`.hidden` files are a Unix convention; Windows Explorer struggles with them)
- Avoid trailing dots or spaces (Windows silently strips them, causing phantom mismatches)

### Case Sensitivity

This is the single most common cross-platform failure.

- **Windows and macOS**: Case-insensitive but case-preserving. `Report.pdf` and `report.pdf` are the same file. Creating both silently overwrites one.
- **Linux**: Case-sensitive. `Report.pdf` and `report.pdf` are two distinct files.
- **Consequence**: A folder organized on Linux with case-variant filenames will lose files when copied to Windows or macOS. Always enforce a single casing convention (lowercase recommended) when cross-platform use is possible.

---

## Duplicate Detection Architecture

Duplicate detection is a performance problem disguised as a correctness problem. Naive approaches hash every file -- on a 500GB drive with 200,000 files, this takes hours. Smart approaches eliminate 95% of candidates before computing a single hash.

### The Size-First Pipeline

1. **Group by file size.** Files with unique sizes cannot be duplicates. This eliminates 70-85% of files with zero I/O beyond a stat call.
2. **Hash the first 4KB** of remaining candidates. Files with different first-4KB hashes are not duplicates. This eliminates another 50-70% of candidates with minimal read I/O.
3. **Full-content hash** only the remaining candidates.

This pipeline reduces hash computation by 95%+ compared to hashing everything.

### Hash Algorithm Selection

| Algorithm | Speed | Collision Resistance | Use Case |
|-----------|-------|---------------------|----------|
| xxHash (xxh64) | Fastest (10+ GB/s) | Low | Pre-filter, non-security |
| MD5 | Fast (700 MB/s) | Broken for security | File dedup (collisions irrelevant at file scale) |
| SHA-256 | Moderate (300 MB/s) | High | When legal/compliance proof of identity is needed |

For file dedup, MD5 is sufficient. The birthday paradox collision probability for MD5 at 1 million files is approximately 1 in 10^26. Use SHA-256 only when you need cryptographic proof of file identity (legal discovery, compliance auditing).

### Beyond Exact Duplicates

Exact hashing misses near-duplicates: resized images, re-encoded videos, documents saved in different formats. See `references/dedup-strategies.md` for perceptual hashing, text similarity, and fuzzy filename matching techniques.

---

## Cross-Platform File Operations

### Metadata Preservation

Moving files naively destroys metadata. Each platform stores different metadata, and each copy/move tool preserves different subsets.

**What gets lost and how to prevent it:**
- **Timestamps** (created, modified, accessed): Use platform-aware copy commands. Python `shutil.copy2()` preserves timestamps cross-platform. Raw `shutil.copy()` does not.
- **Extended attributes** (macOS): `cp -a` preserves them; `cp` alone does not. Python `shutil.copytree()` does not preserve xattrs by default.
- **NTFS alternate data streams** (Windows): Lost on copy to non-NTFS filesystems. Lost with most cross-platform tools. Use `robocopy /COPY:DATSOU` to preserve on Windows-to-Windows moves.
- **Unix permissions**: Meaningless on Windows. When moving from Linux to Windows, permission bits are lost. When moving from Windows to Linux, files may get overly permissive defaults.

### Symlink and Junction Handling

- **Symlinks** (all platforms): Point to a target path. If the target moves, the symlink breaks. During cleanup, deleting a symlink does NOT delete the target. Following symlinks during recursive operations creates duplicates or infinite loops.
- **NTFS junctions** (Windows): Similar to symlinks but for directories only. Junction targets must be on the same volume. `dir /AL` lists junctions. Treat junctions like symlinks: never follow during recursive cleanup.
- **Detection before action**: Always check whether a path is a symlink before moving or deleting. Python: `os.path.islink()`. PowerShell: `(Get-Item path).Attributes -match 'ReparsePoint'`.

### Unicode Normalization

macOS normalizes filenames to NFD (decomposed). Linux and Windows use NFC (composed). The characters look identical but have different byte sequences. A file named "resume.pdf" (with an accented e) may appear as two different files when transferring between macOS and Linux. Normalize to NFC before comparison to avoid false-positive duplicates.

---

## Automation Patterns

### Watched Folder Automation

Automate organization for high-volume directories (Downloads, inbox folders, scan output).

**Architecture**: A watcher process monitors a directory for new files. When a file appears, routing rules determine the destination based on extension, name pattern, or content type. The file is moved (not copied) to the destination.

**Implementation options:**
- Python `watchdog` library: Cross-platform, event-driven, production-grade
- `fswatch` (macOS/Linux): Command-line, lightweight, good for simple rules
- Windows Task Scheduler + PowerShell: No dependencies, runs on schedule rather than events
- `inotifywait` (Linux): Kernel-level file events, lowest latency

**Routing rule design**: Rules must be ordered by specificity. More specific patterns match first. A catch-all "other" rule handles unmatched files. Example priority order: (1) invoices matching `INV-*.pdf` go to `finances/invoices/`, (2) any `.pdf` goes to `documents/`, (3) everything else goes to `unsorted/`.

### File Aging Rules

Files have a lifecycle. Aging rules enforce it automatically.

| Age | Action | Applies To |
|-----|--------|-----------|
| 0-30 days | Active. No action. | All files |
| 30-90 days | Flag for review. Move to `_review/` if in inbox-type folders. | Downloads, temp, inbox |
| 90-365 days | Archive. Compress and move to `archive/YYYY/`. | Completed projects, old exports |
| 365+ days | Archive or delete. Prompt for decision on first occurrence, then apply rule. | Everything except explicitly preserved |

**Archive vs Delete decision**: Archive when the file might be needed for legal, reference, or sentimental reasons. Delete when the file is easily re-downloadable, is a duplicate, or is a byproduct of a process (build artifacts, temp exports, installer packages).

---

## Large-Scale Organization

### Dry-Run Mode

Every bulk operation must support a preview-before-execute pattern. Generate a manifest of planned operations (source, destination, action) and present it for approval before executing any file system changes. This is non-negotiable for operations touching more than 10 files.

### Rollback Strategy

Maintain an operation log during batch processing. Each entry records: timestamp, action (move/rename/delete), source path, destination path. If something goes wrong mid-batch, the log enables reversal. For deletes, move to a staging directory (`.trash/` or `_deleted/YYYY-MM-DD/`) rather than permanent deletion. Purge the staging directory only after explicit confirmation.

### Conflict Resolution

When a destination already contains a file with the same name:

| Strategy | When to Use |
|----------|------------|
| **Rename** (append `-1`, `-2`, etc.) | Default for batch operations. Preserves both files. |
| **Skip** | When destination is known-good (authoritative copy already exists). |
| **Overwrite if newer** | Sync scenarios where the most recent version should win. |
| **Overwrite if larger** | Media files where larger usually means higher quality. |
| **Prompt** | Interactive cleanup where user judgment is needed per file. |

Never overwrite without explicit strategy selection. The default should always be rename or skip -- never silent overwrite.

---

## Named Anti-Patterns

### The Flat Dump
Everything in one folder with descriptive names but no hierarchy. Works until file count exceeds 200. File explorer and `ls` output become unusable. Alphabetical sorting forces naming gymnastics ("AAA-important-file"). **Detect:** Any folder with 200+ files at a single level. **Fix:** Apply Categorical or Project-Based pattern. Create 5-8 top-level folders and route files by type or purpose.

### The Infinite Nest
8+ levels of nested folders with 1-2 files at each leaf. Created by someone who mistakes folder creation for organization. **Detect:** Average files-per-folder below 3. Path lengths exceeding 200 characters. **Fix:** Flatten to 3 levels maximum. Move leaf files up. Encode former folder names into filenames if needed.

### The Metadata Destroyer
Moving files with tools that strip timestamps, extended attributes, or alternate data streams. Original creation dates lost forever. **Detect:** All files in a directory showing the same "created" date (the date they were moved). **Fix:** Use metadata-preserving tools. Python `shutil.copy2()`, `robocopy /COPY:DAT`, `cp -a`. Verify timestamps after bulk moves.

### The Case Sensitivity Trap
Folder works on Linux with `Report.pdf` and `report.pdf` as separate files. Copied to Windows, one silently overwrites the other. **Detect:** Find case-variant filenames: group files by lowercased name and flag groups with count >1. **Fix:** Enforce single casing convention (lowercase). Rename case-variant files before cross-platform transfer.

### The Symlink Surprise
Following symlinks during recursive cleanup. Deleting the symlink target thinking it was a regular file. Duplicating symlinked content into the cleanup output. **Detect:** Check for symlinks before any recursive operation. Python `os.path.islink()`. **Fix:** Skip symlinks during cleanup by default. Resolve symlink targets only when explicitly requested.

### The Desktop Purgatory
Desktop surface used as permanent workspace. Hundreds of files on the desktop, never organized because they are "right there." Desktop becomes the operating system's junk drawer. **Detect:** Desktop folder containing 50+ files. **Fix:** Create an inbox workflow: items stay on desktop for max 7 days. Weekly sweep moves them to proper locations. Automate with a scheduled script.

---

## Rationalization Table

| Temptation | Why It Fails | Do This Instead |
|------------|-------------|-----------------|
| "I'll organize it later" | Later never comes. The pile grows. Every day of delay increases the sorting effort by the new files added plus the increased difficulty of remembering what older files are. | Organize immediately using routing rules. Spend 2 minutes now instead of 2 hours later. |
| "I know where everything is" | You do today. You will not in 6 months. A colleague, replacement, or future-you cannot navigate a system that exists only in current-you's memory. | Design for a stranger. If someone unfamiliar with your work could find a file in under 30 seconds, the system works. |
| "Folders are enough, naming doesn't matter" | `Document1.pdf` in the right folder is still unfindable among 50 other documents. Naming carries retrieval context that hierarchy alone cannot provide. | Combine hierarchy with descriptive naming. `clients/acme/2025-03-proposal.pdf` gives three retrieval dimensions: who, when, what. |
| "I'll just search for it" | Search requires remembering keywords. Unnamed screenshots, generic document titles, and binary files defeat search entirely. Search is a backup, not a strategy. | Make files findable by both browse and search. Naming conventions ensure search works. Hierarchy ensures browsing works. |
| "Duplicates don't matter, storage is cheap" | Storage is cheap. The cost is not disk space -- it is ambiguity. Which copy is the current one? Which has the edits? Duplicates create decision paralysis and version divergence. | Deduplicate regularly. Designate one canonical location per file. Use symlinks or shortcuts for secondary access points. |

---

## Red Flags Checklist

Stop and reassess the organizational approach when any of these appear:

- [ ] **Any folder contains 500+ files at a single level** -- The Flat Dump is forming. Split by category, date, or project immediately.
- [ ] **Path depth exceeds 5 levels** -- The Infinite Nest is growing. Flatten hierarchy, encode context into filenames instead.
- [ ] **Desktop has 50+ files** -- Desktop Purgatory. Implement an inbox sweep rule (weekly automated or manual).
- [ ] **More than 10% of files are named generically** (Document1, Screenshot, IMG_XXXX, Untitled) -- Files are unfindable by search. Batch-rename using date + content description.
- [ ] **Cross-platform file transfers lose timestamps** -- The Metadata Destroyer is active. Switch to metadata-preserving tools immediately.
- [ ] **Duplicate files detected across 3+ locations** -- Canonical source is undefined. Designate one source of truth per file, replace duplicates with shortcuts or symlinks.
- [ ] **Organization attempts abandoned mid-process** -- Scope was too large. Break into smaller batches: one folder at a time, one category at a time.
- [ ] **Automation rules have not been reviewed in 6+ months** -- Routing rules drift as file types and projects change. Audit and update rules quarterly.
