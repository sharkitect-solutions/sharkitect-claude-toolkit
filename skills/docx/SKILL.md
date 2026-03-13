---
name: docx
description: "Use when creating, editing, analyzing, or reviewing .docx files, implementing tracked changes (redlining), extracting text from Word documents, or converting documents to images. NEVER use for .xlsx spreadsheets (use xlsx skill), .pptx presentations (use pptx skill), or PDF-only operations."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# DOCX creation, editing, and analysis

## Workflow Decision Tree

### Reading/Analyzing Content
Use "Text extraction" or "Raw XML access" sections below

### Creating New Document
Use "Creating a new Word document" workflow

### Editing Existing Document
- **Your own document + simple changes**
  Use "Editing an existing Word document" workflow

- **Someone else's document**
  Use **"Redlining workflow"** (recommended default)

- **Legal, academic, business, or government docs**
  Use **"Redlining workflow"** (required)

## Reading and analyzing content

### Text extraction
Convert the document to markdown using pandoc to read text contents:

```bash
pandoc --track-changes=all path-to-file.docx -o output.md
# Options: --track-changes=accept/reject/all
```

### Raw XML access
Required for: comments, complex formatting, document structure, embedded media, and metadata.

#### Unpacking a file
`python ooxml/scripts/unpack.py <office_file> <output_directory>`

#### Key file structures
* `word/document.xml` - Main document contents
* `word/comments.xml` - Comments referenced in document.xml
* `word/media/` - Embedded images and media files
* Tracked changes use `<w:ins>` (insertions) and `<w:del>` (deletions) tags

## Creating a new Word document

Use **docx-js** to create Word documents using JavaScript/TypeScript.

### Workflow
1. **MANDATORY - READ ENTIRE FILE**: Read [`docx-js.md`](docx-js.md) (~500 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for detailed syntax, critical formatting rules, and best practices before proceeding.
2. Create a JavaScript/TypeScript file using Document, Paragraph, TextRun components (assume dependencies are installed; if not, see Dependencies section below)
3. Export as .docx using Packer.toBuffer()

## Editing an existing Word document

Use the **Document library** (Python library for OOXML manipulation). The library handles infrastructure setup and provides methods for document manipulation. For complex scenarios, access the underlying DOM directly through the library.

### Workflow
1. **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~600 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for the Document library API and XML patterns.
2. Unpack the document: `python ooxml/scripts/unpack.py <office_file> <output_directory>`
3. Create and run a Python script using the Document library (see "Document Library" section in ooxml.md)
4. Pack the final document: `python ooxml/scripts/pack.py <input_directory> <office_file>`

## Redlining workflow for document review

This workflow plans comprehensive tracked changes using markdown before implementing them in OOXML. **CRITICAL**: Implement ALL changes systematically.

**Batching Strategy**: Group related changes into batches of 3-10 changes. Test each batch before moving to the next.

**Principle: Minimal, Precise Edits**
Only mark text that actually changes. Repeating unchanged text makes edits harder to review and appears unprofessional. Break replacements into: [unchanged text] + [deletion] + [insertion] + [unchanged text]. Preserve the original run's RSID for unchanged text by extracting the `<w:r>` element from the original and reusing it.

Example - Changing "30 days" to "60 days":
```python
# BAD - Replaces entire sentence
'<w:del><w:r><w:delText>The term is 30 days.</w:delText></w:r></w:del><w:ins><w:r><w:t>The term is 60 days.</w:t></w:r></w:ins>'

# GOOD - Only marks what changed, preserves original <w:r> for unchanged text
'<w:r w:rsidR="00AB12CD"><w:t>The term is </w:t></w:r><w:del><w:r><w:delText>30</w:delText></w:r></w:del><w:ins><w:r><w:t>60</w:t></w:r></w:ins><w:r w:rsidR="00AB12CD"><w:t> days.</w:t></w:r>'
```

### Tracked changes workflow

1. **Get markdown representation**:
   ```bash
   pandoc --track-changes=all path-to-file.docx -o current.md
   ```

2. **Identify and group changes**: Review the document and identify ALL changes needed, organizing into logical batches:

   **Location methods** (for finding changes in XML):
   - Section/heading numbers (e.g., "Section 3.2", "Article IV")
   - Paragraph identifiers if numbered
   - Grep patterns with unique surrounding text
   - Document structure (e.g., "first paragraph", "signature block")
   - **DO NOT use markdown line numbers** - they don't map to XML structure

   **Batch organization** (group 3-10 related changes per batch):
   - By section: "Batch 1: Section 2 amendments", "Batch 2: Section 5 updates"
   - By type: "Batch 1: Date corrections", "Batch 2: Party name changes"
   - By complexity: Start with simple text replacements, then tackle complex structural changes
   - Sequential: "Batch 1: Pages 1-3", "Batch 2: Pages 4-6"

3. **Read documentation and unpack**:
   - **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~600 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Pay special attention to "Document Library" and "Tracked Change Patterns" sections.
   - **Unpack the document**: `python ooxml/scripts/unpack.py <file.docx> <dir>`
   - **Note the suggested RSID**: The unpack script will suggest an RSID to use for your tracked changes. Copy it for use in step 4b.

4. **Implement changes in batches**:

   **Suggested batch groupings:**
   - By document section (e.g., "Section 3 changes", "Definitions", "Termination clause")
   - By change type (e.g., "Date changes", "Party name updates", "Legal term replacements")
   - By proximity (e.g., "Changes on pages 1-3", "Changes in first half of document")

   For each batch:

   **a. Map text to XML**: Grep for text in `word/document.xml` to verify how text is split across `<w:r>` elements.

   **b. Create and run script**: Use `get_node` to find nodes, implement changes, then `doc.save()`. See "Document Library" section in ooxml.md for patterns.

   **Note**: Always grep `word/document.xml` immediately before writing a script to get current line numbers. Line numbers change after each script run.

5. **Pack the document**:
   ```bash
   python ooxml/scripts/pack.py unpacked reviewed-document.docx
   ```

6. **Final verification**:
   ```bash
   pandoc --track-changes=all reviewed-document.docx -o verification.md
   grep "original phrase" verification.md   # Should NOT find it
   grep "replacement phrase" verification.md  # Should find it
   ```

## Converting Documents to Images

Two-step process: DOCX to PDF, then PDF to JPEG.

```bash
# Step 1: Convert DOCX to PDF
soffice --headless --convert-to pdf document.docx

# Step 2: Convert PDF pages to JPEG (creates page-1.jpg, page-2.jpg, etc.)
pdftoppm -jpeg -r 150 document.pdf page

# Specific page range example
pdftoppm -jpeg -r 150 -f 2 -l 5 document.pdf page
```

Key flags: `-r 150` = 150 DPI resolution, `-f N` = first page, `-l N` = last page, `-png` for PNG output.

## Code Style Guidelines

When generating code for DOCX operations:
- Write concise code
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements

## Dependencies

- **pandoc**: `sudo apt-get install pandoc` (text extraction)
- **docx**: `npm install -g docx` (creating new documents)
- **LibreOffice**: `sudo apt-get install libreoffice` (PDF conversion)
- **Poppler**: `sudo apt-get install poppler-utils` (PDF-to-image conversion)
- **defusedxml**: `pip install defusedxml` (secure XML parsing)

## Rationalization Table

| Excuse | Why It's Wrong |
|--------|----------------|
| "I'll edit the XML directly without the Document library" | The Document library handles namespace management, RSID generation, and XML integrity automatically. Direct XML edits cause malformed documents that Word refuses to open. |
| "Tracked changes aren't needed for internal documents" | Any document you didn't create yourself should use redlining. The document owner needs visibility into what changed -- internal docs are no exception. |
| "I'll skip reading ooxml.md -- I already know OOXML" | The Document library has a specific API and patterns that differ from generic OOXML knowledge. Skipping it causes API misuse, broken scripts, and wasted time debugging. |
| "The document is simple enough to create without reading docx-js.md" | docx-js has non-obvious syntax for tables, styles, and formatting. Even simple documents fail without the reference. The MANDATORY read takes less time than debugging. |
| "I'll replace entire paragraphs instead of doing minimal edits" | Whole-paragraph replacements appear unprofessional in review mode and destroy document history. Reviewers cannot see what specifically changed without precise del/ins marking. |
| "Pandoc conversion is good enough -- no need to verify XML" | Pandoc shows a flattened view. The XML may contain structural errors, duplicate runs, or malformed tags that pandoc hides. Verification catches silent failures before delivery. |
| "I'll implement all changes in one script instead of batching" | Large scripts are nearly impossible to debug when one change breaks another. Batches of 3-10 isolate failures and allow incremental progress without starting over. |
| "Line numbers from my last grep are still valid" | Line numbers shift after every script execution. Reusing stale line numbers inserts changes at the wrong location or throws index errors. Always re-grep before each script. |

## Red Flags Checklist

Signs this skill is being applied incorrectly:

- [ ] Editing `word/document.xml` directly without using the Document library
- [ ] Skipping the mandatory read of `ooxml.md` or `docx-js.md` before starting
- [ ] Using markdown line numbers to locate content in `word/document.xml`
- [ ] Replacing entire paragraphs when only a word or phrase changed
- [ ] Not running pandoc verification after implementing all changes
- [ ] Creating a new document without reading `docx-js.md` first
- [ ] Omitting RSID preservation on unchanged runs in tracked changes
- [ ] Implementing all changes in a single script without batching
- [ ] Reusing grep line numbers from a previous script run without re-grepping
- [ ] Attempting to unpack or pack without using the provided ooxml scripts

## NEVER List

- **NEVER edit XML without reading `ooxml.md` first** -- the Document library API is required; direct XML manipulation produces malformed files.
- **NEVER use markdown line numbers to locate content in XML** -- markdown structure does not map to XML structure; use grep patterns on unique surrounding text.
- **NEVER replace entire paragraphs when only specific text changed** -- surgical del/ins tracking is required; full replacements are unprofessional and obscure the actual change.
- **NEVER skip the final pandoc verification step** -- silent XML errors pass undetected without verification; always confirm every change landed correctly.
- **NEVER create documents without reading `docx-js.md` first** -- the library's syntax for styles, tables, and formatting is non-obvious and cannot be safely guessed.
- **NEVER modify companion files** (`ooxml.md`, `docx-js.md`, unpack/pack scripts) -- these are shared infrastructure; changes break all docx operations across every project.
