# Security and Privacy

Shared Brain is designed around private personal context. Treat every generated brain repository as sensitive by default.

## Do not commit

- passwords, API keys, OAuth tokens, PATs, private keys;
- raw browser/account exports unless explicitly reviewed;
- unnecessary phone numbers, addresses, student/employee IDs, government IDs;
- confidential employer/customer material you do not have permission to store;
- third-party personal information that is not needed for the brain's purpose.

## Recommended model

```text
public starter repository
        ↓ copied templates/tools
private personal brain repository
        ↓ pointers only when possible
actual private project/source repositories
```

A public starter must never contain a real user's `brain/`, raw chat archive, production telemetry, tokens, or private source files.

## AI-generated bootstrap content

NotebookLM or another LLM output is untrusted candidate data. The importer only enforces path/format safety; it cannot prove factual correctness. Run the validator, review every file, and correct unsupported claims before commit.

## Reporting security issues

For a future public release, use GitHub private vulnerability reporting if enabled. Do not post credentials or sensitive personal examples in a public issue.