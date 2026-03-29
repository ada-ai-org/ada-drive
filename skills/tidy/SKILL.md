---
name: tidy
description: Review Ada Drive contents and suggest organisation improvements. Updates README.md with a fresh overview of what's in the drive. Run on-demand when the drive feels cluttered or out of date.
version: 1.0.0
---

The user wants to tidy up their Ada Drive.

## Steps

1. **Survey the drive** — call `drive_read` with an empty path to list top-level contents. Then read into any subdirectories that look active or cluttered.

2. **Read AGENTS.md and README.md** — call `drive_read` for each. Note whether they're still accurate.

3. **Identify issues** — look for:
   - Files or folders in unexpected locations (should they be under `projects/`? `notes/`?)
   - Duplicate or redundant files
   - Stale content (old session notes that could be archived or deleted)
   - README.md that doesn't reflect what's actually in the drive

4. **Suggest and apply improvements** — for each issue:
   - Describe the problem briefly
   - Ask the user if they want you to fix it, or just do it if it's clearly safe (e.g. updating README.md)
   - Use `drive_write` to make changes

5. **Update README.md** — rewrite the overview section to reflect the current drive structure. Keep it short: a sentence per section or top-level folder.

6. **Sync** — once done, call `drive_sync` with a message like `"Tidy: update README and reorganise"` to commit and push all changes.

Be pragmatic — this is a quick tidy, not a deep reorganisation. If the drive is already well-organised, just update README.md and tell the user it looks good.
