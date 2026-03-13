# Authentication & Authorization Deep Dive

## OAuth2 Flow Selection

OAuth2 is not one protocol -- it is four grant types solving different trust relationships. Choosing the wrong flow creates security gaps or unnecessary complexity.

### Flow Comparison

| Flow | Client Type | User Present | Token Storage | Use Case |
|------|------------|-------------|---------------|----------|
| **Authorization Code + PKCE** | Public (SPA, mobile, CLI) | Yes | Memory only | Any user-facing app. PKCE prevents code interception. Always use PKCE -- the "confidential client" exception is not worth the risk. |
| **Authorization Code** | Confidential (server) | Yes | Server-side session | Traditional web apps with server rendering. Client secret never leaves the server. |
| **Client Credentials** | Machine (service-to-service) | No | Secure vault | Automated systems, cron jobs, microservice communication. No user context. |
| **Device Code** | Input-constrained (TV, IoT, CLI) | Yes (on separate device) | Polling loop | Smart TVs, CLI tools, embedded devices. User authenticates on phone/browser, device polls for token. |

**Deprecated flows to reject:** Implicit flow (tokens in URL fragments -- interceptable), Resource Owner Password Credentials (user gives password to client -- defeats the purpose of OAuth2). If existing systems use these, plan migration.

### PKCE Implementation Details

PKCE (Proof Key for Code Exchange) binds the authorization request to the token exchange, preventing interception attacks. The client generates a `code_verifier` (43-128 character random string), derives a `code_challenge` via SHA-256, sends the challenge with the auth request, and proves possession of the verifier at token exchange. The authorization server compares `SHA256(code_verifier) == code_challenge`. Failure to implement PKCE on public clients (SPAs, mobile) is a vulnerability, not a simplification.

---

## JWT Architecture

### Token Structure and Validation Checklist

A JWT has three parts: header (algorithm + type), payload (claims), signature (integrity proof). Validation is sequential -- stop at first failure:

1. **Decode header** -- Extract `alg`. Reject `none` algorithm unconditionally (CVE-2015-9235).
2. **Verify signature** -- Use the public key corresponding to the `kid` (key ID) in the header. Never use the key specified inside the JWT itself (algorithm confusion attack).
3. **Check `exp` claim** -- Token must not be expired. Allow 30-60 second clock skew tolerance for distributed systems.
4. **Check `nbf` claim** -- Token must not be used before this timestamp (if present).
5. **Check `iss` claim** -- Issuer must match your trusted authorization server.
6. **Check `aud` claim** -- Audience must include your service identifier. A token issued for Service A should not be accepted by Service B.
7. **Check custom claims** -- Scopes, roles, permissions relevant to the requested operation.

### Token Lifetime Strategy

| Token Type | Lifetime | Storage | Rotation |
|-----------|----------|---------|----------|
| Access token | 15 minutes | Memory (never localStorage) | Obtained via refresh token |
| Refresh token | 7-30 days | HttpOnly secure cookie or secure storage | Rotate on every use (one-time use) |
| ID token | Match access token | Memory | Not refreshed -- re-authenticate |

**Refresh token rotation:** Issue a new refresh token with every access token refresh. Invalidate the old refresh token. If a rotated-out refresh token is reused, it signals theft -- revoke the entire token family (all refresh tokens for that user/session). This is called refresh token replay detection.

**Why not localStorage for tokens:** localStorage is accessible to any JavaScript running on the page. A single XSS vulnerability (third-party script, CDN compromise, dependency injection) exposes every token. HttpOnly cookies are inaccessible to JavaScript. The CSRF risk from cookies is mitigable (SameSite=Strict, CSRF tokens); the XSS risk from localStorage is not.

---

## API Key Management

API keys authenticate applications, not users. They are appropriate for server-to-server communication, rate limit identification, and public API access tracking.

### Key Lifecycle

**Generation:** Generate keys using cryptographically secure random bytes (minimum 32 bytes, base64-encoded). Prefix keys with an identifier for the key type and environment: `sk_live_abc123` (secret, production), `pk_test_xyz789` (publishable, sandbox). The prefix aids debugging and prevents accidental cross-environment usage.

**Storage:** Hash API keys with SHA-256 before storing. Store only the hash. Display the full key exactly once at creation -- it cannot be recovered. Store a truncated identifier (last 4 characters) for customer support lookup. This mirrors credit card storage patterns.

**Rotation:** Support multiple active keys per application (minimum 2). Clients add the new key, verify functionality, then revoke the old key. Zero-downtime rotation requires overlapping validity windows. Set key expiration dates (90-365 days) and enforce rotation.

**Revocation:** Immediate revocation must propagate within seconds, not minutes. Cache key hashes in a fast lookup (Redis, in-memory) with short TTLs. On revocation, remove from cache and add to a blocklist that persists longer than the cache TTL.

**Scoping:** Keys should carry scope restrictions: which endpoints they can access, which HTTP methods, which IP ranges. A key scoped to `read:orders` cannot `write:payments`. Granular scoping limits blast radius on compromise.

---

## Webhook Signature Verification (HMAC)

Webhooks are server-to-server push notifications. The receiver must verify the sender's identity and message integrity.

**HMAC-SHA256 signing pattern:** The sender computes `HMAC-SHA256(webhook_secret, request_body)` and includes the signature in a header (typically `X-Signature-256` or `X-Hub-Signature-256`). The receiver recomputes the HMAC using the shared secret and compares. Use constant-time comparison to prevent timing attacks.

**Timestamp validation:** Include a timestamp header. Reject webhooks older than 5 minutes (replay attack prevention). The receiver checks: `current_time - webhook_timestamp < 300 seconds`. Include the timestamp in the HMAC computation so it cannot be tampered with independently.

**Idempotency:** Webhooks may be delivered multiple times (network retries). Include a unique event ID. Receivers must deduplicate by event ID before processing. Store processed event IDs for at least 24 hours.

---

## mTLS for Service-to-Service

Mutual TLS authenticates both client and server via X.509 certificates. Unlike API keys (which prove application identity via a shared secret), mTLS proves identity cryptographically without transmitting secrets over the wire.

**When to use mTLS:** Service mesh communication where both parties must prove identity. Zero-trust network architectures. Environments where API key management at scale becomes unwieldy (100+ services). Regulatory requirements mandating certificate-based authentication.

**When NOT to use mTLS:** Public APIs (certificate distribution to external consumers is impractical). Simple service-to-service with <10 services (API keys are simpler). Environments without certificate management infrastructure (the operational cost exceeds the security benefit).

**Certificate management:** Use short-lived certificates (24-72 hours) with automated renewal. Long-lived certificates (1+ year) become unrotatable in practice. Service meshes (Istio, Linkerd) automate certificate issuance and rotation via SPIFFE/SPIRE identity framework.
