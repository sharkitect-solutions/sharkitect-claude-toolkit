# Duplicate Detection Strategies

## The Size-First Pipeline (Detailed)

Full-content hashing of every file is wasteful. The size-first pipeline eliminates candidates progressively, reducing total I/O by 95%+.

### Stage 1: Group by File Size

Query the filesystem for file sizes (a stat call, no content reading). Files with unique sizes cannot be duplicates. Discard them immediately.

**Typical elimination rate:** 70-85% of files have unique sizes. On a drive with 200,000 files, this reduces the candidate set to 30,000-60,000 files with zero content I/O.

**Edge case:** Zero-byte files all share size 0. Group them separately. They are "duplicates" by content but may serve different purposes (placeholder files, lock files). Flag but do not auto-delete.

### Stage 2: Partial Hash (First 4KB)

For remaining same-size groups, read and hash only the first 4,096 bytes of each file. Files with different first-4KB hashes are not duplicates -- different headers guarantee different content.

**Typical elimination rate:** 50-70% of same-size candidates have different first-4KB hashes. Particularly effective for media files where headers contain unique metadata (EXIF data, codec info, creation timestamps).

**Hash choice for partial:** xxHash (xxh64) for maximum speed. This is a pre-filter, not a final determination. False positives are acceptable because Stage 3 catches them.

### Stage 3: Full-Content Hash

Hash the full content of remaining candidates. Files with identical full hashes are exact duplicates with near-certainty.

**By this stage:** Only 1-5% of the original file set requires full-content hashing. On the 200,000-file example, this means 2,000-10,000 full hashes instead of 200,000.

---

## Hash Algorithm Comparison

| Algorithm | Speed (SSD) | Collision Risk at 1M Files | Best For |
|-----------|-------------|---------------------------|----------|
| xxHash (xxh64) | 10+ GB/s | ~1 in 10^13 | Pre-filter (Stage 2) |
| MD5 | 700 MB/s | ~1 in 10^26 | File dedup (Stage 3) |
| SHA-256 | 300 MB/s | ~1 in 10^53 | Legal/compliance proof |
| CRC32 | 2+ GB/s | ~1 in 10^4 | Never use alone for dedup |

**Why MD5 is fine for dedup:** MD5's cryptographic weaknesses (crafted collisions) are irrelevant for file dedup. Nobody is crafting collision files in your Documents folder. The birthday paradox probability at practical file counts is negligible. Use SHA-256 only when you need to prove file identity in a legal, audit, or compliance context.

**Large file handling:** For files over 1GB, use chunk hashing: read 64KB blocks at regular intervals (every 10MB), hash the concatenation. This produces a fingerprint in seconds rather than minutes. Full hash only the final candidates.

---

## Near-Duplicate Detection

### Perceptual Hashing for Images

Exact hashing misses images that are resized, re-compressed, cropped, or color-adjusted. Perceptual hashes produce similar values for visually similar images.

**Average Hash (aHash):**
1. Resize image to 8x8 pixels (64 pixels total)
2. Convert to grayscale
3. Compute mean pixel value
4. Each pixel becomes 1 (above mean) or 0 (below mean)
5. Result: 64-bit hash

Two images with Hamming distance <= 5 between their aHash values are likely perceptual duplicates.

**Difference Hash (dHash):**
1. Resize image to 9x8 pixels (72 pixels)
2. Convert to grayscale
3. Compare each pixel to its right neighbor
4. Each comparison becomes 1 (left > right) or 0
5. Result: 64-bit hash

dHash is more robust than aHash against brightness/contrast changes. Hamming distance <= 10 indicates likely duplicates.

**False positive handling:** Perceptual hashing produces false positives on images with similar structure but different content (two different headshots, two similar product photos). Always present perceptual duplicates for human review rather than auto-deleting.

**Python implementation:**
```python
from PIL import Image
def dhash(image_path, hash_size=8):
    img = Image.open(image_path).resize((hash_size + 1, hash_size), Image.LANCZOS).convert('L')
    pixels = list(img.getdata())
    diff = []
    for row in range(hash_size):
        for col in range(hash_size):
            left = pixels[row * (hash_size + 1) + col]
            right = pixels[row * (hash_size + 1) + col + 1]
            diff.append(1 if left > right else 0)
    return int(''.join(map(str, diff)), 2)

def hamming_distance(h1, h2):
    return bin(h1 ^ h2).count('1')
```

### Text Similarity for Documents

Documents saved in different formats (.docx vs .pdf vs .txt) or with minor edits are not exact duplicates but may be functionally identical.

**Approach:**
1. Extract plain text from each document (use python-docx, PyPDF2, or similar)
2. Normalize: lowercase, strip whitespace, remove punctuation
3. Compare using one of:
   - **Jaccard similarity** on word sets: |intersection| / |union|. Threshold >= 0.85 indicates near-duplicate.
   - **Simhash** for large documents: locality-sensitive hash that produces similar hashes for similar text. Hamming distance <= 3 on a 64-bit simhash indicates near-duplicate.

**When to skip text comparison:** If documents share the same filename stem but different extensions (`report.docx` and `report.pdf`), they are almost certainly versions of the same document. Flag by name match first; content comparison is confirmation, not discovery.

### Fuzzy Filename Matching

Files renamed with minor variations: `report-final.pdf`, `report-final-v2.pdf`, `report_final_v2 (1).pdf`, `report-final-v2-copy.pdf`.

**Levenshtein distance** measures the minimum edits (insert, delete, substitute) to transform one string into another. For filenames:
- Distance <= 3: Likely variants of the same file. Flag for review.
- Distance 4-8: Possible variants. Lower priority.
- Distance > 8: Unlikely to be related.

**Pre-processing before comparison:**
1. Strip extensions (compare stems only)
2. Remove common suffixes: `-copy`, `(1)`, `(2)`, `-v2`, `-final`, `-draft`
3. Normalize separators: replace `_`, `.`, spaces with `-`
4. Lowercase everything

After normalization, many fuzzy matches become exact matches, reducing false positives significantly.

---

## Duplicate Resolution Decision Framework

After detecting duplicates, deciding which to keep:

| Criterion | Keep This One | Rationale |
|-----------|--------------|-----------|
| **Most recent modified date** | Newer file | Likely has latest edits |
| **Longer path (deeper in hierarchy)** | Shallower path | The filed copy is canonical; the deep copy is a working copy |
| **Filename without suffixes** | `report.pdf` over `report (1).pdf` | The original, not the browser download variant |
| **Larger file size** (images/video) | Larger file | Higher resolution or less compression |
| **In a project folder** | Project copy | It was intentionally placed there |

When criteria conflict, present both files to the user with metadata comparison (size, dates, paths) and let them decide. Automated bulk dedup should default to keeping the canonical copy and moving (not deleting) duplicates to a `_duplicates/` staging folder for manual review.
