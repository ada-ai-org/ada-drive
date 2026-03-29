---
name: sync
description: Sync Ada Drive with GitHub — pull latest changes, commit everything local, and push. Run this after writing files to the drive, or to pull updates from other agents or teammates.
version: 1.0.0
---

The user wants to sync their Ada Drive with GitHub.

Ask: **"What changed? I'll use your answer as the commit message."**

If they don't have anything specific, suggest: `"Update Ada Drive"`.

Then call `drive_sync` with their message.

Report the result back to the user — either confirmation that it synced, or the error if something went wrong (e.g. push rejected because of upstream changes).
