# Source Priority / Conflict Rules

When sources conflict, prefer:

1. the user's explicit current correction;
2. current canonical state and the relevant canonical dossier;
3. the more recent explicit decision/status statement;
4. original project artifacts, code, test results, logs, or official course/work sources;
5. recent conversation context;
6. model-native memory snapshots;
7. old conversations and early brainstorming.

Rules:

- Preserve useful old states as `SUPERSEDED` instead of silently rewriting history.
- Do not promote model advice or inference into a user decision.
- Keep unresolved conflicts explicit as `UNKNOWN`, `SOURCE_CONFLICT`, or `NEEDS_VERIFICATION`.
- The actual project repository is authoritative for current code/config/tests/logs; Shared Brain stores durable meaning, decisions, constraints, and provenance pointers.
