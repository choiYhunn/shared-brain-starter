# Roadmap

## v0.1 — Bootstrap kit (this release)

- private-brain directory skeleton;
- source/conflict rules;
- NotebookLM bootstrap prompt;
- deterministic multi-file export format;
- safe importer with path and overwrite guards;
- validator with required-file, size, secret-pattern, and privacy warnings;
- Windows PowerShell initializer;
- maintainer publishing helper;
- no real personal brain data.

## v0.2 — Generic retrieval runtime

Extract the reusable subset of the private MCP runtime without user-specific assumptions:

- `BRAIN_GITHUB_OWNER`, `BRAIN_GITHUB_REPO`, and branch as configuration;
- project routes generated from the private brain's own index/config instead of hard-coded aliases;
- exact current/project reads;
- bounded search over allowlisted Markdown;
- explicit failure rather than silent partial retrieval;
- small context router;
- tests using synthetic example brains only.

Do not ship production credentials, private repository IDs, or personal route names.

## v0.3 — Safe cross-client updates

- pending-only write path;
- immutable base commit/blob provenance;
- optimistic validation;
- non-force publication;
- optional advisory edit-intent lease;
- review-before-canonical promotion.

## v0.4 — Optional privacy-safe usage telemetry

Only after users explicitly opt in:

- tool/route usage metadata;
- no prompt/query/answer text;
- no raw User-Agent or credentials;
- frequency + recency evidence for optional hot-route pointers.

## Not planned by default

- uploading everyone's brain into one maintainer-controlled database;
- public NotebookLM notebooks containing private source material;
- automatic promotion of LLM output to canonical truth;
- copying canonical facts into multiple hot-cache Markdown files;
- vector databases or additional storage tiers without measured retrieval need.
