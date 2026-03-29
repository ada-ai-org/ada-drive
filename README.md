# Ada Drive

**A shared filesystem for humans and AI agents — local-first, GitHub-synced.**

You clone a GitHub repo to `~/AdaDrive`. Your AI agents read it for context, write notes and decisions back to it, and sync to GitHub. Every change is a git commit. No database, no embeddings, no magic — just files.

## Install

**1. Open a terminal and start Claude Code:**

```bash
claude
```

**2. Run these commands one at a time**, waiting for each to complete:

```
/plugin marketplace add ada-ai-org/ada-drive
```
```
/plugin install ada-drive@ada-ai
```

**3. Quit Claude Code and restart it** — press `Ctrl+C` twice in the terminal, then run `claude` again. This is required for skills to load after a fresh install.

**4. Run setup:**

```
/ada-drive:setup
```

> **After updating** (`/plugin update ada-drive`), also quit and restart Claude Code (`Ctrl+C` twice, then `claude`). Skills won't reload until you do.

`/ada-drive:setup` walks you through cloning a repo, picking a template, and wiring Claude Code to read the drive automatically.

## Setup modes

**AI memory** (default) — agents remember your preferences, context, and facts across all conversations and projects. They organize files as they learn — no fixed folder structure imposed.

**Blank** — minimal `AGENTS.md` and `README.md`. You define everything.

## How it works

Two files at the root define the contract:

- **`AGENTS.md`** — instructions for AI agents: what the drive is for, what to read and write
- **`README.md`** — overview for humans: what's in the drive

Everything else is plain markdown files in whatever layout makes sense to you.

```
~/AdaDrive/
  AGENTS.md
  README.md
  projects/
    my-app/
      decisions.md
      context.md
      sessions/
        2026-03-28.md
  notes/
```

### Claude Code (and Codex)

Local agents read files directly from the cloned folder — no MCP server needed. `/ada-drive:setup` adds this line to `~/.claude/CLAUDE.md`:

```
Shared agent workspace: ~/AdaDrive/ — read AGENTS.md there for instructions.
```

Claude Code picks this up at session start and reads the drive automatically.

### Chat agents (claude.ai, Claude Desktop)

Ada Drive ships an MCP server that exposes the drive over the MCP protocol:

| Tool | What it does |
|---|---|
| `drive_read` | Read a file or list a directory |
| `drive_write` | Write a file (then call `drive_sync` to push) |
| `drive_search` | grep for files matching a query |
| `drive_history` | Recent git log |
| `drive_sync` | `git pull` + `git add -A` + `git commit` + `git push` |

The MCP server reads from the local clone, so it works offline and is fast.

## Architecture

```
Claude Code ──── reads/writes files ──▶ ~/AdaDrive/  ◀──── git pull/push ────┐
Codex       ──── reads/writes files ──▶ ~/AdaDrive/                           │
                                             │                                 │
                                         git push                          GitHub repo
                                             │                             (your-user/AdaDrive)
claude.ai   ──── MCP tools ──────────▶ MCP server                            │
Claude Desktop ─ MCP tools ──────────▶ (reads local clone) ──── git sync ────┘
```

Both paths — direct files and MCP — read and write the same local clone, which syncs to GitHub.

## Skills

| Skill | What it does |
|---|---|
| `/ada-drive:setup` | Interactive setup: repo, location, template, CLAUDE.md |
| `/ada-drive:status` | Drive path, contents, sync state, recent commits |
| `/ada-drive:sync` | Commit all local changes and push to GitHub |
| `/ada-drive:tidy` | Review drive contents, suggest improvements, update README.md |

## CLI

```bash
ada-drive init       # create the GitHub repo
ada-drive sync -m "message"  # pull, commit, push
ada-drive status     # show drive state
ada-drive serve      # start MCP server (for chat agents)
```

## License

MIT
