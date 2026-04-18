# Supabase Storage Patterns

Expert-only Storage knowledge. Generic "how to upload a file" tutorials are skipped. This file covers the RLS interaction with `storage.objects`, the upsert permission trap, signed URL gotchas, image transformations, and the common ways uploads silently fail.

---

## How Storage Actually Works

Supabase Storage is **NOT** an opaque file service. It's:
- Files stored in S3-compatible object storage (managed S3 on Supabase Cloud)
- Metadata in the `storage.objects` Postgres table — **subject to RLS**
- Bucket configuration in `storage.buckets` table

Every Storage operation = a database operation against `storage.objects`. RLS policies on `storage.objects` are what gate access. There is no second authorization layer.

This means:
- "Public bucket" = bucket with RLS policies that allow `public` role to SELECT
- "Private bucket" = bucket with no public policy
- Misconfigured RLS = silent file leakage or impossible-to-debug 403s

---

## The Upsert Permission Trap (THE Most Common Bug)

> Granting only INSERT lets new uploads succeed but file replacement (`upsert: true`) silently returns success while doing nothing — or returns a confusing 403 that doesn't say "you need UPDATE."

A storage upsert performs:
1. SELECT (to check if the file exists)
2. INSERT (if not present)
3. UPDATE (if present, to replace it)

If your RLS only grants INSERT, the SELECT or UPDATE silently fails.

**Required policy set for full upload + replace functionality:**

```sql
-- 1. SELECT — required for upsert path resolution AND for client to download own files
CREATE POLICY "users select own files" ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'user-uploads'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- 2. INSERT — for first-time uploads
CREATE POLICY "users upload own files" ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'user-uploads'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- 3. UPDATE — for upserts that replace existing files
CREATE POLICY "users update own files" ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'user-uploads'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- 4. DELETE — only if users should remove their own files
CREATE POLICY "users delete own files" ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'user-uploads'
  AND (storage.foldername(name))[1] = auth.uid()::text
);
```

### `storage.foldername()` and path conventions

`storage.foldername(name)` parses the object path into segments. The convention is to put `auth.uid()` as the first segment so RLS can match:

```
user-uploads/
  └── 7e8a... (user UUID)/
       ├── avatar.png
       └── documents/
            └── invoice.pdf
```

`(storage.foldername(name))[1]` extracts the first segment. Use `auth.uid()::text` (cast to text — UUID type comparison fails silently against text path).

---

## Public vs Private Buckets

### Truly public bucket (anyone can read)

```sql
-- Bucket marked public AND policy allowing public role
UPDATE storage.buckets SET public = true WHERE id = 'public-assets';

CREATE POLICY "public read" ON storage.objects FOR SELECT
USING (bucket_id = 'public-assets');
```

A public bucket exposes files via:
```
https://<project>.supabase.co/storage/v1/object/public/<bucket>/<path>
```

**Caching note:** Public bucket files are aggressively CDN-cached (default `cache-control: max-age=3600`). After replacing a file, users may see the old version for up to an hour. Workaround: append a cache-busting query string (`?v=<hash>`) or set custom `cacheControl` on upload.

### Private bucket (RLS-gated, requires signed URLs or auth headers)

```sql
UPDATE storage.buckets SET public = false WHERE id = 'user-files';
-- + RLS policies as above
```

Access via:
- `supabase.storage.from('user-files').download(path)` — uses session JWT, RLS-gated
- `supabase.storage.from('user-files').createSignedUrl(path, expirySeconds)` — pre-signed URL, bypasses RLS

---

## Signed URLs: Three Modes, Different Use Cases

| Method | Direction | Auth model | Use when |
|--------|-----------|-----------|----------|
| `createSignedUrl(path, expiry)` | Download | Pre-signed, no JWT needed | Email link to a private file, share with non-authenticated user |
| `createSignedUploadUrl(path)` | Upload | Pre-signed, single-use | Direct browser upload bypassing your backend |
| Public URL | Download | None | Truly public assets only |

### `createSignedUploadUrl` (the underused pattern)

```ts
// Server: generate a one-time upload URL, return to client
const { data } = await supabase.storage
  .from('user-uploads')
  .createSignedUploadUrl(`${userId}/avatar.png`)
// data.signedUrl, data.token, data.path

// Client: upload directly using the signed URL — your backend doesn't proxy bytes
await supabase.storage.from('user-uploads').uploadToSignedUrl(
  data.path, data.token, file
)
```

This pattern is critical for large file uploads (>6MB) where your backend can't accept the body within Edge Function limits. The signed upload URL is single-use and short-lived (configurable, default 2 hours).

### Signed URL gotchas

- `createSignedUrl` generates a URL but **does NOT validate the file exists** at generation time. A 404 surfaces only when the URL is accessed.
- The URL contains the JWT signature in a query param. **It is shareable** — anyone with the URL can access until expiry. Treat as a bearer token.
- For images you'll embed in emails, use longer expiry (24-72h) since email clients cache and re-render later. For UI tile thumbnails, 1h is fine.

---

## Image Transformations (Pro Tier)

Supabase Storage has on-the-fly image resizing/format conversion via query params.

```
/storage/v1/render/image/public/<bucket>/<path>?width=400&height=400&resize=cover&format=webp&quality=80
```

**Available transformations:**
- `width`, `height` — pixel dimensions
- `resize` — `cover` (crop to fill), `contain` (fit inside), `fill` (stretch)
- `format` — `origin`, `webp`, `avif` (browsers that support modern formats benefit; `origin` is fallback)
- `quality` — 0-100 (default 80)

### When to use transformations vs pre-resized variants

| Approach | When | Trade-off |
|----------|------|-----------|
| On-the-fly transformations | Few sizes, low traffic, dynamic dimensions | First-request latency (~500-2000ms), cached after; counted toward image transformation quota |
| Pre-resized variants stored as separate objects | High traffic, fixed sizes, hot path performance | More storage, more upload-time work, but zero transformation cost |

**Critical:** transformations only work on the SOURCE bucket, not on already-transformed URLs. Don't chain transformations.

### Transformations don't work on signed URLs by default

`createSignedUrl` generates a URL pointing to `/object/`, not `/render/image/`. To get a signed transformed URL:

```ts
const { data } = await supabase.storage
  .from('avatars')
  .createSignedUrl(`${userId}/photo.jpg`, 3600, {
    transform: { width: 200, height: 200, resize: 'cover' }
  })
```

The `transform` option is what flips the URL to the render endpoint.

---

## CORS for Direct Browser Uploads

Default CORS allows requests from any origin to all buckets. To lock down:

Dashboard → Storage → Configuration → CORS settings (or via management API):
```json
{
  "allowedOrigins": ["https://yourapp.com"],
  "allowedMethods": ["GET", "POST", "PUT"],
  "allowedHeaders": ["authorization", "content-type", "x-upsert"],
  "maxAgeSeconds": 3000
}
```

**`x-upsert` header note:** the `upsert: true` option in `supabase-js` sets the `x-upsert: true` request header. If your CORS config doesn't include it in `allowedHeaders`, browser uploads with upsert silently fail with CORS errors that mention OTHER headers (browser only reports the first missing header).

---

## File Size and MIME Type Limits

### Size limits

- Default per-file limit: **50 MB** (free tier, configurable on paid)
- Hard maximum: **500 GB** per file (paid)
- For files > 6MB, use **resumable uploads** via `tus-js-client` — Edge Functions / API routes can't proxy bodies > 6MB

```ts
import * as tus from 'npm:tus-js-client'
const upload = new tus.Upload(file, {
  endpoint: `${SUPABASE_URL}/storage/v1/upload/resumable`,
  headers: { authorization: `Bearer ${session.access_token}`, 'x-upsert': 'true' },
  metadata: { bucketName: 'large-files', objectName: `${userId}/video.mp4` },
  chunkSize: 6 * 1024 * 1024,  // 6MB chunks
})
upload.start()
```

### MIME type restriction

Set per-bucket allowed MIME types to prevent abuse:

```sql
UPDATE storage.buckets
SET allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp']
WHERE id = 'user-avatars';
```

Uploads with disallowed MIME types fail at the API layer with a 400 — RLS doesn't even evaluate.

**Spoofing note:** the MIME type is read from the `Content-Type` header sent by the client, NOT inspected from file magic bytes. A malicious client can claim `image/png` for a `.exe`. For genuine validation, run an Edge Function that downloads the uploaded file, inspects magic bytes, and deletes invalid uploads.

---

## Listing Files Efficiently

```ts
const { data, error } = await supabase.storage
  .from('user-files')
  .list(folder, {
    limit: 100,        // max 1000
    offset: 0,
    sortBy: { column: 'created_at', order: 'desc' }
  })
```

### The list() RLS gotcha

`list()` returns objects matching SELECT policy. If a user has SELECT only for files where path starts with their UUID, calling `list('')` (root) returns ONLY their UUID folder. Calling `list('other-user-id/')` returns an empty array (not an error).

### Pagination is offset-based, NOT cursor

For large folders (10K+ files), offset pagination becomes slow as offset grows (Postgres scans+skips). For high-cardinality folders, design path scheme to keep folders small (e.g., shard by date: `2026/04/`).

---

## Deleting and Cleanup

### Bulk delete by path prefix is NOT a single API call

```ts
// Storage API only supports deleting an explicit list of paths
await supabase.storage.from('user-files').remove([
  'user-id/file1.png',
  'user-id/file2.png'
])
```

To delete an entire folder, list first then remove:
```ts
const { data: files } = await supabase.storage.from('bucket').list('user-id/')
const paths = files.map(f => `user-id/${f.name}`)
await supabase.storage.from('bucket').remove(paths)
```

For deep recursive deletion, you must list each subfolder.

### Orphaned objects after user deletion

`auth.users` deletion does NOT cascade to `storage.objects`. After user deletion:
- Files in user's folder remain in S3 (cost continues)
- RLS may now block all access (no one matches `auth.uid() = old_user_id`)

Implement cleanup via:
1. Trigger on `auth.users` DELETE → enqueue cleanup job
2. Edge Function processes the queue, deletes Storage objects via service_role

```sql
CREATE FUNCTION queue_user_cleanup() RETURNS trigger AS $$
BEGIN
  INSERT INTO user_cleanup_queue (user_id) VALUES (OLD.id);
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_user_delete
  AFTER DELETE ON auth.users
  FOR EACH ROW EXECUTE FUNCTION queue_user_cleanup();
```

---

## Common Failure Modes

| Symptom | Likely cause |
|---------|-------------|
| `new row violates row-level security` on upload | Missing INSERT policy or `auth.uid()` != path's first segment |
| Upload succeeds but `upsert: true` doesn't replace | Missing UPDATE or SELECT policy |
| `403 Unauthorized` on download with valid session | Missing SELECT policy on `storage.objects` |
| Image transformation returns 404 | Source file doesn't exist, OR transformation params malformed (e.g., `width=0`) |
| Public bucket files showing stale | CDN cache, append `?v=hash` or set `cacheControl` on upload |
| Large file upload fails at 6MB | Used standard `upload()`, must use resumable `tus` for >6MB |
| `cors error` on browser upload with upsert | `x-upsert` not in CORS `allowedHeaders` |
| `list()` returns empty for known-existing files | RLS SELECT policy doesn't match path pattern |
| Signed URL works locally but not in email | Expiry too short (default 60s in some examples) |

---

## When This Skill Has Failed in the Past

- INSERT-only policy → upserts silently no-op
- Forgetting `(storage.foldername(name))[1] = auth.uid()::text` cast → string-vs-uuid mismatch, RLS denies
- Public bucket without `public = true` flag set → 403 even with permissive policy
- Direct backend proxy of multi-MB uploads → Edge Function 413/504 → migrate to signed upload URLs
- `createSignedUrl` without `transform` option → unstyled images
- Forgetting `x-upsert` in CORS allowedHeaders → opaque browser CORS errors
- Trusting Content-Type header for MIME validation → executable upload as fake image
