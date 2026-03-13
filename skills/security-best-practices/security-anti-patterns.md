# Security Anti-Patterns Catalog

Load when reviewing code for security issues, when a security review finds vulnerabilities, or when educating developers on secure coding practices. These anti-patterns go beyond OWASP Top 10 to cover real-world failures.

## Authentication Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|---|---|---|
| Client-side only role checks | Attacker inspects frontend, finds admin routes, accesses directly | Every API endpoint verifies role server-side. Frontend checks are UX only. |
| JWT stored in localStorage | XSS can read localStorage -- any script injection steals the token | httpOnly, Secure, SameSite=Strict cookie. If SPA requires header-based auth, use in-memory + refresh token in httpOnly cookie. |
| Long-lived access tokens (>1 hour) | Stolen token is valid for the entire lifetime | Short-lived access (15min) + long-lived refresh (7-30 days). Refresh token rotation with reuse detection. |
| Password reset via security questions | Answers are guessable, publicly available (mother's maiden name), or phishable | Email/SMS token with expiry. TOTP or WebAuthn for high-security. |
| Rolling your own password hashing | Custom hashing algorithms have unknown vulnerabilities | Use bcrypt (cost 12+), scrypt, or Argon2id. NEVER MD5, SHA-1, or SHA-256 without salt+stretching. |
| Same secret for signing and encryption | Compromise of one operation compromises both | Separate keys for signing (JWT) and encryption (data at rest). Different rotation schedules. |
| Session fixation on login | Attacker sets a session ID before victim authenticates, then hijacks the authenticated session | Regenerate session ID on every authentication state change (login, logout, privilege escalation). |

## Authorization Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|---|---|---|
| IDOR (Insecure Direct Object Reference) | `/api/user/123/profile` returns any user's profile by changing the ID | Verify requesting user owns/has permission to the resource. Use UUIDs (not sequential IDs) AND ownership checks. |
| Mass assignment | `user.update(req.body)` allows attacker to set `role: "admin"` | Whitelist updateable fields explicitly. Never pass raw request body to ORM update. |
| Path traversal on file operations | `readFile(userInput)` allows `../../etc/passwd` | Resolve path, then verify it starts with the expected base directory. Don't just strip `../` (double-encoding bypasses). |
| Frontend route guards as authorization | React/Vue router guards prevent navigation but API is unprotected | All authorization logic on the server. Frontend guards are navigation UX, not security. |
| Implicit deny failure | New API endpoints default to "open" until someone remembers to add auth | Default-deny middleware. New routes must explicitly declare their auth requirements or they return 401. |
| Over-scoped API keys | Single API key with full account access used everywhere | Create scoped keys per service/function. Read-only keys for read operations. Time-limited keys for CI/CD. |
| Authorization check only at entry point | Middleware checks auth on route, but internal functions called by that route don't verify | Defense in depth: check permissions at each layer (controller, service, data access). Especially on shared functions called by multiple routes. |

## Data Handling Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|---|---|---|
| Logging sensitive data | Passwords, tokens, credit cards, SSNs in log files -- accessible to anyone with log access | Structured logging with explicit field allowlists. Sanitize PII before logging. Regex-scan logs for credit card patterns. |
| Returning full database objects in API responses | Response includes `password_hash`, `internal_notes`, `deleted_at`, etc. | Use DTOs/serializers that explicitly declare which fields to include. Never return raw ORM objects. |
| Soft delete without access control update | Record marked `deleted_at` but still returned by queries, still accessible via API | Soft delete must also revoke all access. Add `WHERE deleted_at IS NULL` to every query, or use database views. |
| Caching authenticated responses | CDN or browser caches a response containing user-specific data, serves it to other users | `Cache-Control: private, no-store` on all authenticated responses. Never cache responses that vary by user. |
| Email/notification content with sensitive data | Password reset link in email body, full credit card number in SMS notification | Emails: link to a page that requires authentication. Notifications: mask all but last 4 digits. Never include passwords in any notification. |
| Trusting client-supplied content type | Server processes file based on `Content-Type` header, which attacker controls | Verify file content by magic bytes, not headers. A `.jpg` with `Content-Type: image/jpeg` can contain embedded JavaScript. |
| Deserializing untrusted data | `JSON.parse()` is safe, but `pickle.load()`, `unserialize()`, `ObjectInputStream` are arbitrary code execution | NEVER deserialize untrusted data with language-native deserializers. Use JSON or Protocol Buffers. If you must: validate schema strictly before deserializing. |

## Infrastructure Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|---|---|---|
| Running as root in containers | Compromised container has full host access | `USER nonroot` in Dockerfile. Rootless containers (Podman). Read-only filesystem where possible. |
| Default database credentials | `postgres:postgres`, `root:root`, `admin:admin` -- the first thing attackers try | Unique, randomly generated credentials per environment. Secrets manager, not config files. |
| Debug mode in production | Exposes stack traces, environment variables, internal paths, and sometimes a code execution shell | `DEBUG=false` in production, enforced by deployment pipeline. Health check endpoint that verifies debug is off. |
| Unrestricted CORS | `Access-Control-Allow-Origin: *` on authenticated endpoints | Whitelist specific origins. Never use `*` with `credentials: true` (browsers already block this, but misconfigurations happen). |
| No network segmentation | All services can talk to all other services | Service mesh with explicit allow rules. Database only accepts connections from application server, not from the internet. |
| Secrets in environment variables visible to all processes | `env` command or `/proc/*/environ` leaks secrets to any process | Use secrets manager with per-service access. If env vars are unavoidable, ensure only the application process can read them. |
| Build artifacts containing source code | Docker image includes `.git/`, `node_modules` with dev dependencies, source maps | Multi-stage builds. `.dockerignore` for `.git`, `.env`, tests, docs. Verify final image with `docker history` and `dive`. |

## Error Handling Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|---|---|---|
| Stack traces in API responses | Reveals framework version, file structure, library versions, SQL queries | Generic error response in production (RFC 7807 format). Log the full error server-side with a correlation ID. Return only the correlation ID to the client. |
| Different error messages for different auth failures | "User not found" vs "Incorrect password" confirms which usernames exist | Identical message for all auth failures: "Invalid credentials." Identical response time (add artificial delay to faster path). |
| Catching and ignoring exceptions silently | `catch (e) {}` hides security-relevant failures (auth bypass, injection detection) | Log every caught exception. If you can't handle it properly, let it propagate. Silent catches mask attacks. |
| Error messages containing user input | `"Invalid email: " + userInput` in response -- if rendered in HTML, it's reflected XSS | Never reflect user input in error messages without output encoding. Use templated error messages with encoded placeholders. |
| Retry on authentication failure | Auto-retry on 401/403 with same credentials enables credential stuffing acceleration | No automatic retry on auth failures. Log the failure. Implement progressive delays (1s, 2s, 4s) on repeated failures from same source. |

## Dependency and Supply Chain Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Pattern |
|---|---|---|
| No lock file committed | `npm install` or `pip install` pulls latest versions, which may include compromised updates | Always commit `package-lock.json`, `yarn.lock`, `poetry.lock`, or equivalent. CI should use `--frozen-lockfile`. |
| Wildcard version ranges | `"lodash": "*"` or `"requests": ">=2.0"` allows any future version, including compromised ones | Pin to exact versions or use tight ranges (`^` for minor, `~` for patch). Audit before updating. |
| No dependency audit in CI | Vulnerable dependencies merged without detection | `npm audit`, `pip-audit`, or `cargo audit` in CI pipeline. Fail build on critical/high severity. |
| Installing from untrusted registries | Private packages from mirrors, or typosquatted package names | Use official registries only. Enable scope locking for private packages. Verify package ownership before first install. |
| Vendored dependencies never updated | Dependencies copied into repo and forgotten for years | If vendoring: schedule quarterly audits. Track vendored versions in a manifest. Better: use a package manager with lock files. |
| Running arbitrary install scripts | `postinstall` scripts in npm can execute anything during `npm install` | Use `--ignore-scripts` for untrusted packages. Review install scripts before allowing. Consider `npm ci` over `npm install`. |
