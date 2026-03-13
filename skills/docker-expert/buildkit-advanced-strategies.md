# BuildKit Advanced Strategies

BuildKit is Docker's next-generation build engine (default since Docker 23.0). Understanding its internals unlocks build optimizations that standard Dockerfile tutorials don't cover.

## BuildKit vs Legacy Builder

| Feature | Legacy Builder | BuildKit |
|---|---|---|
| Parallelism | Sequential -- each instruction waits for the previous | Parallel -- independent stages build concurrently |
| Cache | Layer-based, invalidated by ANY change in a layer | Content-addressable, fine-grained per-file cache |
| Secrets | No native support (ENV/ARG leaks to history) | `--mount=type=secret` -- never written to any layer |
| SSH | No native support (copy keys into image, security risk) | `--mount=type=ssh` -- agent forwarding, no key exposure |
| Cache mounts | Not available | `--mount=type=cache` -- persistent package manager caches |
| Output | Always produces an image | Can output to local directory, tar, OCI layout, or skip output entirely |

**Enabling BuildKit**: Default on Docker 23.0+. On older versions: `DOCKER_BUILDKIT=1 docker build ...` or set `"features": {"buildkit": true}` in daemon.json.

## Cache Mount Patterns

Cache mounts persist package manager downloads ACROSS builds. Without them, every `RUN npm ci` re-downloads all packages even if only one changed.

### Package Manager Cache Locations

| Package Manager | Cache Path | Mount Syntax |
|---|---|---|
| npm | `/root/.npm` | `--mount=type=cache,target=/root/.npm` |
| yarn | `/usr/local/share/.cache/yarn` | `--mount=type=cache,target=/usr/local/share/.cache/yarn` |
| pnpm | `/root/.local/share/pnpm/store` | `--mount=type=cache,target=/root/.local/share/pnpm/store` |
| pip | `/root/.cache/pip` | `--mount=type=cache,target=/root/.cache/pip` |
| apt | `/var/cache/apt` + `/var/lib/apt/lists` | Both need separate mounts |
| Go modules | `/go/pkg/mod` | `--mount=type=cache,target=/go/pkg/mod` |
| Cargo (Rust) | `/usr/local/cargo/registry` | `--mount=type=cache,target=/usr/local/cargo/registry` |
| Maven | `/root/.m2/repository` | `--mount=type=cache,target=/root/.m2/repository` |
| Gradle | `/root/.gradle/caches` | `--mount=type=cache,target=/root/.gradle/caches` |

### Cache Mount Gotchas

1. **UID mismatch**: If your Dockerfile runs as non-root (`USER 1001`), the cache mount is owned by root by default. Fix: `--mount=type=cache,target=/path,uid=1001,gid=1001`

2. **CI environments**: Cache mounts persist on the Docker daemon, NOT in the build context. In ephemeral CI runners (GitHub Actions, GitLab CI), the cache is empty every run unless you use an external cache backend:
   ```bash
   docker build --cache-from type=registry,ref=ghcr.io/org/app:cache \
                --cache-to type=registry,ref=ghcr.io/org/app:cache ...
   ```

3. **Sharing modes**: Default is `shared` (concurrent reads). Use `locked` for package managers that don't support concurrent access: `--mount=type=cache,target=/path,sharing=locked`

4. **Cache invalidation**: Cache mounts are NOT invalidated when the Dockerfile changes. A corrupted cache persists until manually cleared: `docker builder prune --filter type=exec.cachemount`

5. **Size growth**: Cache mounts grow unbounded. Package managers don't auto-prune. Add periodic cleanup steps or set build pruning policies.

### Optimized apt Pattern

```dockerfile
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev
```

No `rm -rf /var/lib/apt/lists/*` needed -- the cache mount isn't in any layer, so it doesn't bloat the image. The `sharing=locked` prevents concurrent builds from corrupting the apt lock files.

## Build Secrets

Secrets needed during build (API keys for private registries, SSH keys for private repos) must NEVER be in `ENV`, `ARG`, or `COPY`'d files -- they persist in image layers visible via `docker history`.

### Secret Mount Pattern

```dockerfile
# syntax=docker/dockerfile:1
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) \
    npm ci --registry=https://registry.npmjs.org/
```

Build command:
```bash
docker build --secret id=npm_token,src=$HOME/.npmrc .
```

The secret is mounted at `/run/secrets/<id>` during that single `RUN` instruction only. It never appears in any layer, `docker history`, or the build cache.

### SSH Agent Forwarding

```dockerfile
# syntax=docker/dockerfile:1
RUN --mount=type=ssh \
    git clone git@github.com:org/private-repo.git
```

Build command:
```bash
eval $(ssh-agent) && ssh-add ~/.ssh/id_ed25519
docker build --ssh default .
```

The SSH agent socket is forwarded into the build. No key files are ever copied or exposed.

## Multi-Platform Builds (buildx)

BuildKit + buildx enables building for multiple architectures from a single machine.

### Architecture Decision

| Target Architecture | When | Method |
|---|---|---|
| Same as build host | Standard development | Normal `docker build` |
| linux/arm64 from amd64 host | Deploying to ARM servers (Graviton, Apple Silicon in CI) | QEMU emulation via buildx |
| linux/amd64 from arm64 host | Apple Silicon developer building for x86 servers | QEMU emulation via buildx |
| Both amd64 + arm64 | Publishing to registries for multi-arch consumption | Multi-platform manifest with buildx |

### QEMU Emulation Gotchas

| Issue | Detail |
|---|---|
| Speed | QEMU is 5-20x slower than native. A 2-minute native build can take 20-40 minutes emulated |
| Segfaults | Some packages segfault under QEMU (notably: `sharp`, `esbuild`, `grpc`). Workaround: cross-compile in a native stage, copy binary to emulated stage |
| Node.js native modules | `npm ci` under QEMU emulation for arm64 on amd64 often fails on `node-gyp` builds. Fix: use `--platform` on the install stage only and cross-compile |
| Go cross-compilation | Go natively cross-compiles (`GOOS=linux GOARCH=arm64`). Don't use QEMU for Go -- use native cross-compilation, it's faster and more reliable |
| Rust cross-compilation | Use `cross` crate or `cargo-zigbuild` for cross-compiling. QEMU for Rust builds is extremely slow |

### Multi-Platform Build Pattern

```bash
# Create a builder with multi-platform support
docker buildx create --name multiarch --driver docker-container --use

# Build and push multi-platform image
docker buildx build --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/org/app:latest \
  --push .
```

**Key constraint**: Multi-platform builds MUST push to a registry (`--push`) or output to a tar/OCI directory. You cannot `--load` a multi-platform image into the local Docker daemon -- the daemon only holds one platform at a time.

## Dockerfile Frontend Syntax

The `# syntax=` directive at the top of a Dockerfile selects which BuildKit frontend parses it. This enables features before they ship in Docker releases.

```dockerfile
# syntax=docker/dockerfile:1
```

| Syntax | What It Enables |
|---|---|
| `docker/dockerfile:1` | Latest stable features (cache mounts, secrets, SSH, heredocs) |
| `docker/dockerfile:1.7-labs` | Experimental features (currently: `COPY --parents`, `COPY --exclude`) |
| `docker/dockerfile:1-labs` | Same as above, auto-updating |

### Heredoc Syntax (1.4+)

Run multi-line scripts without `&&` chains:

```dockerfile
# syntax=docker/dockerfile:1
RUN <<EOF
  apt-get update
  apt-get install -y curl
  rm -rf /var/lib/apt/lists/*
EOF
```

**Gotcha**: Each heredoc `RUN` is still a single layer. The benefit is readability, not layer optimization. Shell errors inside the heredoc will still fail the build (set -e is implicit).

### COPY --exclude (labs)

```dockerfile
# syntax=docker/dockerfile:1-labs
COPY --exclude=*.test.js --exclude=__tests__ ./src ./app/src
```

Eliminates the need for `.dockerignore` entries that only apply to specific COPY instructions.

## Build Cache Optimization

### Cache Invalidation Rules

BuildKit invalidates cache when:

| Trigger | What's Invalidated |
|---|---|
| File content changes (by checksum, not timestamp) | The COPY/ADD instruction and ALL subsequent instructions |
| Instruction text changes | That instruction and everything after it |
| Build arg value changes | Instructions that reference that ARG and everything after |
| Base image changes | Everything (FROM pulls new image, invalidates all layers) |
| Parent stage rebuild | COPY --from=stage instructions that reference the rebuilt stage |

### Cache-Friendly Ordering (Beyond Basics)

Most guides say "copy package.json first, then source code." The principle extends further:

```dockerfile
# Layer 1: System deps (change yearly)
RUN apt-get update && apt-get install -y libpq-dev

# Layer 2: Language version lockfile (change monthly)
COPY .tool-versions ./
RUN asdf install

# Layer 3: Dependency lockfile (change weekly)
COPY package-lock.json ./
RUN npm ci

# Layer 4: Generated code (change weekly)
COPY prisma/schema.prisma ./prisma/
RUN npx prisma generate

# Layer 5: Source code (change daily)
COPY . .
RUN npm run build
```

**Principle**: Order by change frequency (least -> most). Each layer invalidates everything below it.

### Inline Cache Export

For CI where builds don't share a local daemon:

```bash
docker build \
  --cache-from ghcr.io/org/app:cache \
  --cache-to type=inline \
  --tag ghcr.io/org/app:latest \
  --push .
```

`type=inline` embeds cache metadata in the image itself. Simpler than maintaining a separate cache image, but limited: only caches the final stage, not intermediate stages. For multi-stage builds, use `type=registry` with a separate cache ref.

## Build Contexts and Named Contexts

BuildKit supports multiple build contexts -- useful for monorepos and shared libraries.

```bash
docker build \
  --build-context shared=../shared-lib \
  --build-context configs=../deploy/configs \
  -f services/api/Dockerfile .
```

```dockerfile
COPY --from=shared /utils ./shared-utils
COPY --from=configs /production.yaml ./config/
```

**Gotcha**: Named contexts override `FROM` stage names. If you have `FROM alpine AS shared` and also `--build-context shared=../lib`, the build context wins. Name your contexts distinctly from your stages.

## Debugging Build Failures

| Technique | When | How |
|---|---|---|
| Build with `--progress=plain` | Need full output of RUN commands | `docker build --progress=plain .` (default is `auto` which collapses output) |
| Target a specific stage | Build hangs or fails in a later stage | `docker build --target=deps .` to build only up to the `deps` stage |
| Interactive debugging | Need a shell at the point of failure | `docker build --target=failing-stage .` then `docker run -it <image> sh` |
| Build history | Inspecting what's cached vs rebuilt | `docker buildx du` shows build cache usage by type |
| Cache miss diagnosis | Build is slower than expected | `--progress=plain` output shows `CACHED` or `sha256:...` for each step. If a step isn't cached, check what changed upstream |
