# Architecture

The starter separates **public tooling** from **private user state**.

```text
                    PUBLIC
        shared-brain-starter repository
     templates / importer / validator / docs
                        |
                        | initialize
                        v
                    PRIVATE
              user's brain repository
        brain/* / sources/* / inbox/pending
                        |
          +-------------+-------------+
          |                           |
          v                           v
  AI retrieval client          actual project repos
  smallest useful slice        code/config/tests/logs
```

## Memory layers

- **L0 current state** — very small, current information that materially affects near-term answers.
- **L1 canonical dossiers** — projects, academics, career, durable profile/memory state.
- **Technical knowledge** — reusable source-grounded notes, separate from project status.
- **Decision history** — current and superseded durable decisions.
- **Archive fallback** — optional historical evidence only; not part of this public bootstrap kit.

## Retrieval policy

```text
Does the answer depend on durable personal state?
  no  -> skip memory retrieval
  yes -> authoritative state already in the current conversation/project repo?
           yes -> use the closer source
           no  -> read the narrowest relevant canonical file
```

Known project/current targets should use exact reads before broad search. Archives should be consulted only when canonical state is insufficient.

## Write policy

Generated or cross-model updates should enter as reviewed candidates first. A mature runtime may add optimistic concurrency/version checks and advisory edit-intent leases, but correctness should ultimately rely on immutable versions and non-force publication rather than pretending a lease is a hard distributed lock.

## Why the runtime is not bundled yet

The original private implementation includes user-specific repository/project routes and production Cloudflare/OAuth configuration. Shipping it unchanged would leak assumptions and create a false "one-click generic" claim. The public alpha therefore ships the reusable ingestion/canonicalization layer first. Runtime extraction is a roadmap item after real-use telemetry identifies the genuinely reusable surface.