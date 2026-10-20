# Shared Brain Starter

A privacy-first bootstrap kit for building a **private, Git-backed personal knowledge brain** that multiple AI clients can reuse without loading your entire history every time.

This public starter is intentionally separated from any real person's private brain. It ships templates, a NotebookLM bootstrap workflow, import/validation scripts, and a publishing helper. It does **not** contain private memories, chat archives, telemetry, credentials, or personal project data.

## Core idea

```text
raw personal sources
      ↓
NotebookLM / manual curation
      ↓
structured Markdown candidates
      ↓
local validator
      ↓
private Git repository
      ↓
AI clients retrieve only the smallest relevant slice
```

The operating principles are:

- one canonical durable fact, not duplicated summaries everywhere;
- current corrections beat old notes;
- project repositories remain the source of truth for current code/config/logs;
- archives are historical evidence, not canonical truth;
- unknown or disputed claims stay explicit;
- retrieval should be narrow and skipped entirely when personal memory cannot change the answer.

## What this starter includes

- `bootstrap/NOTEBOOKLM_BOOTSTRAP_PROMPT.md` — prompt to turn a private NotebookLM notebook into structured Shared Brain Markdown candidates.
- `bootstrap/EXPORT_FORMAT.md` — deterministic multi-file text format for import.
- `templates/brain/` — minimal canonical brain skeleton.
- `scripts/init-personal-brain.ps1` — creates a new local private-brain workspace from the templates.
- `scripts/import_notebooklm.py` — safely splits a NotebookLM/LLM export into allowlisted Markdown files.
- `scripts/validate_brain.py` — checks required files, path policy, obvious secret patterns, and file-size limits.
- `scripts/publish-public-repo.ps1` — maintainer helper for publishing this starter as a separate public GitHub repository.

## Quick start

### 1. Create your private brain locally

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-personal-brain.ps1 -TargetDir "$HOME\my-shared-brain"
```

On Linux or macOS (no PowerShell), the same skeleton can be created by hand. The PowerShell script additionally writes a private `README.md` and a `.gitignore` that excludes `raw/`, `vault/`, `secrets/`, `exports/`, and `.env*`; add an equivalent `.gitignore` before your first commit.

```bash
BRAIN="$HOME/my-shared-brain"
mkdir -p "$BRAIN/brain"
cp -R templates/brain/. "$BRAIN/brain/"
mkdir -p "$BRAIN"/{brain/knowledge,brain/academics,brain/career,brain/memory,sources,inbox/pending}
python3 scripts/validate_brain.py "$BRAIN"
```

### 2. Build a private NotebookLM notebook

Upload only sources you are allowed to process. Keep the notebook private. Then use the prompt in `bootstrap/NOTEBOOKLM_BOOTSTRAP_PROMPT.md`.

NotebookLM should produce one text export using the markers documented in `bootstrap/EXPORT_FORMAT.md`.

### 3. Import the generated candidates

```powershell
python .\scripts\import_notebooklm.py .\notebooklm-export.md --root "$HOME\my-shared-brain"
python .\scripts\validate_brain.py "$HOME\my-shared-brain"
```

Review every generated file before committing it. AI-produced text is a **candidate**, not automatically canonical truth.

### 4. Put your brain in a private Git repository

```powershell
cd "$HOME\my-shared-brain"
git init
git add .
git commit -m "Initialize private Shared Brain"
```

If you use GitHub CLI:

```powershell
gh repo create my-shared-brain --private --source . --remote origin --push
```

## Verify this starter

These are the same checks the GitHub Actions workflow runs (`.github/workflows/validate.yml`); they need only Python 3 and no network access.

```bash
python3 -m py_compile scripts/import_notebooklm.py scripts/validate_brain.py
python3 -m unittest discover -s tests -p 'test_*.py'          # importer safety tests
python3 scripts/import_notebooklm.py examples/notebooklm-export.example.md --root .tmp/example-brain
python3 scripts/validate_brain.py .tmp/example-brain           # expected: PASS: 0 blocking issues
```

The example export is synthetic. The importer refuses path traversal, duplicate paths, and text outside the documented file blocks; the validator checks required files, path policy, obvious secret patterns, and file sizes. A PASS does not prove that the content is factually correct.

## Recommended hierarchy

```text
brain/
  00_CURRENT.md          # small, current global state
  01_PROFILE.md          # durable profile facts only
  02_SOURCE_PRIORITY.md  # conflict/source rules
  DECISIONS.md           # durable decisions and superseded plans
  projects/
    INDEX.md
    *.md
  knowledge/
    *.md
  academics/
    *.md
  career/
    *.md
  memory/
    *.md
inbox/pending/           # reviewed-before-promotion candidates
sources/                 # source pointers/hashes, not necessarily raw files
```

## Privacy boundary

Do not commit raw exports, credentials, tokens, private chat dumps, student/employee IDs, addresses, medical data, or other sensitive material unless you deliberately accept the risk of storing it in that repository. Prefer source pointers/hashes and sanitized summaries.

The public starter and each user's private brain should remain separate repositories.

## Status

**Alpha / bootstrap layer.** This starter focuses on safe ingestion and canonical structure. A generalized runtime MCP/retrieval package should be extracted only after real-world usage proves which parts of the current private implementation are actually reusable. See `ROADMAP.md`.

## 한국어 요약

이 저장소는 개인 메모리를 공개하는 프로젝트가 아니라, 각 사용자가 **자기 private Git repo에 자기 Shared Brain을 만들기 위한 배포용 뼈대**입니다. NotebookLM은 초기 Markdown 후보를 만드는 도구로만 사용하고, 실제 canonical 반영 전에는 반드시 사람이 검토하도록 설계되어 있습니다.

## License

MIT. See `LICENSE`.