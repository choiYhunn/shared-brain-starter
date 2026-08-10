# Deterministic Bootstrap Export Format

The importer accepts one UTF-8 text/Markdown file containing one or more file blocks.

## Syntax

```text
<!-- FILE: brain/00_CURRENT.md -->
# Current State
...
<!-- END FILE -->

<!-- FILE: brain/projects/example-project.md -->
# Example Project
...
<!-- END FILE -->
```

Rules:

- `<!-- FILE: ... -->` must be on its own line.
- `<!-- END FILE -->` must be on its own line.
- Paths are repository-relative and use `/` separators.
- Allowed roots are `brain/` and `sources/` only.
- Markdown files only (`.md`).
- Absolute paths and `..` traversal are rejected.
- Sensitive roots such as `archive/`, `vault/`, `raw/`, `.git/`, `inbox/`, and secret/config files are not accepted by the importer.
- Existing files are not overwritten unless `--overwrite` is explicitly passed.

The format is intentionally boring so that NotebookLM, another LLM, or a human can produce it and a small deterministic script can validate it.