---
name: status
description: Show Ada Drive contents, sync status, and recent git history.
version: 1.0.0
---

Show the user the current state of their Ada Drive.

## Steps

1. Call `drive_read` with path `''` (empty string, lists the root) to show top-level contents.

2. Call `drive_history` with `limit=5` to show recent commits.

3. Check for uncommitted changes by running via Bash:
   ```bash
   git -C ~/AdaDrive status --short
   ```
   (Use the actual drive path if it differs from `~/AdaDrive`.)

## Present results

Show a clean summary — no headers needed for each section, just the facts:

```
Ada Drive: <drive path>
GitHub: <remote URL from git remote get-url origin>

Contents:
  [dir] projects/
  [file] AGENTS.md
  [file] README.md
  ...

Recent commits:
  abc1234 2026-03-28 — Add auth decisions for my-app
  ...

<if uncommitted changes>
Uncommitted changes:
  M notes/2026-03-28.md
  ...
<else>
Working tree is clean.
```

If `drive_read` returns "Drive not found", tell the user to run `/drive:setup` to initialise their drive.
