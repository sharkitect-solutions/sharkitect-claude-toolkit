# Container Kernel Internals

What containers actually are at the Linux kernel level -- the primitives that Docker abstracts away but that explain every "weird" container behavior.

## Containers Are Not VMs

A container is a regular Linux process with three kernel restrictions applied: namespaces (what it can see), cgroups (what it can use), and seccomp (what it can call). There is no hypervisor, no separate kernel. The container shares the host kernel. This is why:
- A kernel exploit inside a container compromises the host
- `uname -r` inside a container returns the HOST kernel version
- A container built on kernel 5.15 can fail on kernel 4.19 if it uses newer syscalls
- `--privileged` doesn't just add capabilities -- it disables ALL isolation (namespaces, cgroups, seccomp, AppArmor/SELinux)

## Namespace Isolation (What the Container Sees)

Linux has 8 namespace types. Docker uses 6 by default. Each namespace creates an illusion of isolation for one resource class.

| Namespace | Isolates | Docker Default | Gotcha |
|---|---|---|---|
| PID | Process tree | Yes -- container sees PID 1 as its init | PID 1 doesn't get default signal handlers. `SIGTERM` is IGNORED unless your app handles it explicitly. This is why containers don't stop gracefully with `docker stop` -- the app never receives the signal. Fix: use `tini` or `--init` flag |
| Network | Network stack, interfaces, ports | Yes -- virtual eth pair + bridge | `localhost` inside container is the CONTAINER's loopback, not the host's. Two containers on the same bridge network reach each other by container name (Docker DNS), not localhost. Host networking (`--network host`) shares the host's stack entirely -- no port mapping needed but no isolation |
| Mount | Filesystem tree | Yes -- union filesystem (overlay2) | Container sees a merged view of image layers (read-only) + a thin writable layer on top. Writes go to the writable layer via copy-on-write. Writing to a 1GB file in an image layer copies the entire file to the writable layer first -- this is why writing to large existing files inside containers is slow and bloats the container |
| UTS | Hostname, domain name | Yes | `hostname` inside container returns the container ID by default. `--hostname` overrides but doesn't affect DNS resolution |
| IPC | Shared memory, semaphores, message queues | Yes | Containers on the same IPC namespace can use `shmget`/`shmat`. PostgreSQL uses shared memory -- if you hit "could not resize shared memory segment" it's because `--shm-size` defaults to 64MB. Set `shm_size: 256m` in compose |
| User | UID/GID mapping | No (disabled by default) | Without user namespaces, UID 0 in the container IS UID 0 on the host. Container escape + root = host root. Enable with `userns-remap` in daemon.json, but: many images break because they expect to run as real root during build |
| Cgroup | Cgroup root view | Yes (v2 only) | Container sees only its own cgroup hierarchy, not the host's. This means `/proc/meminfo` and `/proc/cpuinfo` still show HOST resources -- your app thinks it has 64GB RAM when it has 512MB. Use `lscgroup` or read from `/sys/fs/cgroup/` for real limits |
| Time | System clock | Kernel 5.6+ only | Not used by Docker yet. Containers share the host clock. Changing timezone requires `TZ` env var or bind-mounting `/etc/localtime`, NOT `timedatectl` |

### The PID 1 Problem in Detail

In Linux, PID 1 (init) has special behavior:
- Signals without an explicit handler are IGNORED (unlike other PIDs where `SIGTERM` default action is terminate)
- Orphaned child processes get reparented to PID 1, which must `wait()` on them or they become zombies

**Impact on containers**: If your app runs as PID 1 and doesn't handle `SIGTERM`:
1. `docker stop` sends `SIGTERM` -- app ignores it
2. Docker waits 10 seconds (default `--stop-timeout`)
3. Docker sends `SIGKILL` -- app is force-killed, no graceful shutdown
4. Database connections not closed, in-flight requests dropped, temp files not cleaned

**Solutions (pick one)**:
- `--init` flag or `init: true` in compose -- injects `tini` as PID 1, forwards signals, reaps zombies
- `ENTRYPOINT ["tini", "--"]` in Dockerfile -- same but baked into the image
- Handle signals in your application code -- Node.js: `process.on('SIGTERM', ...)`, Python: `signal.signal(signal.SIGTERM, ...)`
- Shell form `CMD node app.js` runs via `/bin/sh -c` which DOES handle signals -- but also prevents `docker stop` from reaching your app if the shell doesn't forward them (bash does, sh doesn't always)

## Cgroups v2 Resource Control

Cgroups (control groups) limit what resources a container can USE. Docker's `--memory`, `--cpus`, etc. map directly to cgroup knobs.

### Memory Cgroup

| Setting | What It Does | Non-Obvious Behavior |
|---|---|---|
| `memory.max` (--memory) | Hard limit -- OOM kill if exceeded | The OOM killer picks the process with the highest `oom_score_adj` + memory usage. In a container, this is almost always PID 1 (your app). The container exits with code 137 (128 + SIGKILL=9) |
| `memory.high` (--memory-reservation) | Soft limit -- kernel reclaims memory aggressively | Not a guarantee. Under host memory pressure, the kernel MAY let the container exceed this. Under no pressure, the kernel still throttles if you exceed it |
| `memory.swap.max` (--memory-swap) | Swap limit | Default: 2x memory limit. Set to same as memory limit to disable swap. Swap in containers is almost always wrong -- it hides memory leaks and degrades performance |

**The `/proc/meminfo` lie**: Applications reading `/proc/meminfo` see HOST memory, not container limits. This is why Java <= 8 without `-XX:+UseContainerSupport` allocates based on host RAM and gets OOM-killed. Modern runtimes read `/sys/fs/cgroup/memory.max` instead. Node.js `--max-old-space-size` must be set explicitly -- it doesn't auto-detect container limits.

### CPU Cgroup

| Setting | What It Does | Non-Obvious Behavior |
|---|---|---|
| `cpu.max` (--cpus) | CPU bandwidth limit (quota/period) | `--cpus 0.5` = 50ms of CPU per 100ms period. A multi-threaded app with 4 threads will consume 50ms of wall time in 12.5ms, then be THROTTLED for 87.5ms. This looks like random latency spikes, not CPU saturation |
| `cpuset.cpus` (--cpuset-cpus) | Pin to specific CPU cores | Useful for NUMA-aware workloads. But: pinned containers can't benefit from idle cores elsewhere. Don't pin unless you have a measured reason |

**CPU throttling vs CPU shares**: `--cpus` is a hard ceiling. `--cpu-shares` is relative weight (only matters when CPUs are contended). Most people want `--cpus` for predictable behavior. `--cpu-shares` alone doesn't prevent a single container from consuming all CPU when others are idle.

## Overlay2 Filesystem

Docker's default storage driver. Understanding it explains image layer caching, build performance, and container disk behavior.

### How Layers Work

```
Container writable layer (thin, copy-on-write)
  |
  v
Image layer N (FROM instruction or COPY/RUN result)
Image layer N-1
...
Image layer 1 (base image)
```

- Each Dockerfile instruction creates a new layer
- Layers are read-only after creation and content-addressable (SHA256)
- The container gets a thin writable layer on top via overlay2
- Reads: overlay2 walks down the stack until it finds the file (upperdir -> lowerdir)
- Writes: copy-on-write. The ENTIRE file is copied from the lower layer to the upper layer before modification, even if you change one byte

### Performance Implications

| Operation | What Happens | Impact |
|---|---|---|
| Read existing file | Served from layer cache | Fast -- similar to native filesystem |
| Write new file | Written to container layer | Fast -- no copy needed |
| Modify existing file from image layer | Full file copy-up then modify | Slow for large files. Modifying a 500MB SQLite database in the image = 500MB copy first. This is why databases must use volumes |
| Delete file from image layer | Whiteout file created in upper layer | Original file still exists in lower layer, consuming space. Images don't shrink by deleting files in later layers -- the space is still in previous layers |
| Many small files | Each needs separate overlay lookup | `node_modules` with 50,000 files is slower on overlay2 than native. Named volumes bypass overlay2 entirely |

### Why `RUN rm -rf` Doesn't Reduce Image Size

```dockerfile
RUN apt-get update && apt-get install -y build-essential  # Layer 1: +400MB
RUN make && make install                                   # Layer 2: +50MB
RUN apt-get purge -y build-essential && rm -rf /var/lib/apt/lists/*  # Layer 3: +0MB (whiteouts), Layer 1 still has 400MB
```

The `rm` creates whiteout entries in Layer 3 but Layer 1 still contains all 400MB. The image is 450MB, not 50MB. Fix: combine into one `RUN` layer, or use multi-stage builds where the final stage never had the build tools.

## Seccomp Profiles

Seccomp (Secure Computing) restricts which SYSTEM CALLS a container can make. Docker applies a default profile that blocks ~44 dangerous syscalls.

### Notable Blocked Syscalls

| Syscall | Why Blocked | Impact |
|---|---|---|
| `clone` with `CLONE_NEWUSER` | Prevents creating new user namespaces (escalation vector) | Can't run Docker-in-Docker without `--privileged` or custom seccomp |
| `mount` | Prevents filesystem manipulation | Can't mount filesystems inside containers. Affects FUSE-based tools |
| `reboot` | Prevents host reboot from container | Obvious safety measure |
| `keyctl` | Prevents kernel keyring access | Blocks access to host encryption keys |

**Custom profiles**: When the default profile blocks something legitimate, create a custom profile that allows ONLY the specific syscall needed, not `--privileged` which disables everything:
```bash
docker run --security-opt seccomp=custom-profile.json ...
```

## Capabilities vs Privileged

Linux capabilities break root power into ~41 discrete permissions. Docker drops all but 14 by default.

| Capability | What It Allows | When Actually Needed |
|---|---|---|
| `NET_BIND_SERVICE` | Bind ports below 1024 | Nginx/Apache on port 80 (kept by default) |
| `NET_RAW` | Raw sockets, packet crafting | Network debugging tools like `ping`, `tcpdump` (kept by default -- consider dropping if not needed) |
| `SYS_PTRACE` | Process tracing, debugging | Attaching debuggers. Required for `strace` inside containers. NOT needed for production |
| `SYS_ADMIN` | Mount, namespace creation, many others | The "almost root" capability. 90% of `--privileged` requests actually need this one capability. But it's dangerously broad -- find the specific capability needed instead |
| `NET_ADMIN` | Network configuration | Modifying iptables, network interfaces. Required for VPN containers, service mesh sidecars |

**The `--privileged` escalation**: `--privileged` gives ALL capabilities + disables seccomp + disables AppArmor + gives access to all host devices. It is root on the host in all but name. Never use it because "the container needs one thing that doesn't work" -- find which specific capability is missing and add only that.
