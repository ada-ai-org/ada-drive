---
name: setup
description: Set up your Ada Drive — pick a local folder, connect or create a GitHub repo, choose a template, and get everything wired up. Run this once after installing the plugin.
version: 1.0.0
---

Help the user set up their Ada Drive. This is an interactive conversation — ask one thing at a time, wait for their answer, then proceed. Never skip a step, even if a previous step had an issue.

---

## Step 1: Ask for drive location

Ask:

**"Where should your AdaDrive live locally?**

**1.** `~/AdaDrive` (default)
**2.** Enter a custom path

**Reply with 1, or type a path like `/Users/you/MyDrive`."**

If they reply `1` or anything that isn't a path, use `~/AdaDrive`. Otherwise use what they typed.

Use their answer as `DRIVE_PATH` for the rest of setup. Expand `~` to the full home directory path when running commands.

---

## Step 2: GitHub authentication

Check if the user is already authenticated using the Bash tool (not `!`):

```bash
gh auth status 2>&1
```

- **If authenticated**: tell them "GitHub is already connected." and continue to Step 3.
- **If not authenticated or gh not found**: ask them: **"How would you like to connect to GitHub? Options:
  1. `gh auth login` — interactive login via browser (recommended)
  2. Personal access token — paste a GitHub token with `repo` scope
  3. Skip — set up GitHub sync later"**

**If they choose option 1 (gh login):**
Tell them to run this in their terminal:
```
! gh auth login
```
Wait for them to confirm it worked, then continue.

**If they choose option 2 (token):**
Ask for the token, then run:
```bash
gh auth login --with-token <<< "<their-token>"
```
Confirm with `gh auth status 2>&1`.

**If they choose option 3 (skip):**
Note that `drive_sync` won't work until GitHub is set up, then continue.

---

## Step 3: Ask for GitHub repo

Ask: **"Do you want to (1) create a new private GitHub repo, or (2) connect to an existing repo?"**

**If new repo:**
- Ask: "What should it be called? Default is `AdaDrive`."
- Create it using the Bash tool:
  ```bash
  gh repo create <repo-name> --private --description "My AdaDrive — personal AI memory, synced to GitHub"
  ```
- Get their GitHub username:
  ```bash
  gh api user --jq '.login'
  ```
- Set `GITHUB_REPO` = `<owner>/<repo-name>`

**If existing repo:**
- Ask: "What's the repo? (format: `owner/repo`, or paste the full GitHub URL)"
- Extract `owner/repo` from their answer — strip any `https://github.com/` prefix and trailing `.git` if present.
- Set `GITHUB_REPO` = the extracted `owner/repo`.

**If GitHub was skipped in Step 2:**
- Set `GITHUB_REPO` = empty, skip repo creation.

---

## Step 4: Set up the local drive folder

**First**, check whether the directory already exists and is a git repo:
```bash
git -C <DRIVE_PATH> rev-parse --is-inside-work-tree 2>/dev/null && echo "IS_GIT" || echo "NOT_GIT"
```

**Case A — directory is already a git repo (`IS_GIT`):**
Just verify the remote is correct and pull latest:
```bash
git -C <DRIVE_PATH> remote get-url origin 2>/dev/null || echo "no remote"
git -C <DRIVE_PATH> pull 2>&1 || true
```
Tell the user: "Found an existing git repo at `<DRIVE_PATH>` — using it as-is."
Skip the clone steps below and continue to Step 5.

**Case B — directory does not exist or is not a git repo (`NOT_GIT`):**

Create the directory:
```bash
mkdir -p <DRIVE_PATH>
```

**If a GitHub repo was chosen**, clone using the gh CLI (uses the authenticated user's credentials):
```bash
gh repo clone <GITHUB_REPO> <DRIVE_PATH> 2>&1
```
If that fails, fall back to HTTPS:
```bash
git clone https://github.com/<GITHUB_REPO>.git <DRIVE_PATH> 2>&1
```

**After cloning a brand-new empty repo** (no commits yet), explicitly create the main branch:
```bash
git -C <DRIVE_PATH> checkout -b main 2>/dev/null || git -C <DRIVE_PATH> checkout main
```

**If GitHub was skipped:** the directory is already created above, continue.

---

## Step 5: Ask for use case

Ask: **"How do you want to set up your AdaDrive?

1. **AI memory** (default) — AI agents will remember you across conversations and projects
2. **Blank** — just the basics, you decide the structure later"**

---

## Step 6: Write AGENTS.md and README.md

Write both files using the Write tool. Do NOT create any folders — only these two files.

### Option 1: AI memory

**`AGENTS.md`** (`<DRIVE_PATH>/AGENTS.md`):
```markdown
# AdaDrive — AI Memory

This is my personal AI memory. You have read and write access here.

## Your job

You are the keeper of this memory. Use it to remember things about me across conversations and projects — my preferences, context, decisions, and anything else that would help you work better with me over time.

**At the start of every conversation:**
- Read this file
- Read any files here that seem relevant to the current task or conversation

**During and after conversations:**
- Write down what you learn about me: preferences, working style, personal context, project decisions, tools I use
- If something already exists that's related, update it rather than creating a duplicate
- Use your judgment on how to organise the files — create and structure them in whatever way makes most sense given what you know about me

**The goal:** someone reading these files cold should be able to understand who I am, how I work, and what's important to me — well enough to pick up any conversation or project mid-stream.
```

**`README.md`** (`<DRIVE_PATH>/README.md`):
```markdown
# AdaDrive

My personal AI memory — context and preferences that persist across conversations and projects.

AI agents read and write here automatically. You can also edit files directly.
```

---

### Option 2: Blank

**`AGENTS.md`** (`<DRIVE_PATH>/AGENTS.md`):
```markdown
# AdaDrive

This is my AdaDrive. AI agents can read and write here.
```

**`README.md`** (`<DRIVE_PATH>/README.md`):
```markdown
# AdaDrive
```

---

### Commit and push

After writing the files:

```bash
git -C <DRIVE_PATH> add AGENTS.md README.md
git -C <DRIVE_PATH> commit -m "Initialize AdaDrive"
git -C <DRIVE_PATH> push --set-upstream origin main 2>&1 || git -C <DRIVE_PATH> push 2>&1
```

If there is no GitHub remote (GitHub was skipped), omit the push — just commit locally.

---

## Step 7: Import from another AI assistant (optional)

Ask: **"Do you want to import your memory from another AI assistant (ChatGPT, Claude, Gemini, etc.)? I can generate an export prompt for you to run there."**

If yes:

Tell them:

---

Run this prompt on ChatGPT, Claude.ai, or whichever assistant you want to import from:

```
Export all of my stored memories and any context you've learned about me and all activities from past conversations. Preserve my words verbatim where possible, especially for instructions and preferences.

## Categories (output in this order):

1. **Instructions**: Rules I've explicitly asked you to follow going forward — tone, format, style, "always do X", "never do Y", and corrections to your behavior. Only include rules from stored memories, not from conversations.

2. **Identity**: Name, age, location, education, family, relationships, languages, and personal interests.

3. **Career**: Current and past roles, companies, and general skill areas.

4. **Projects**: Projects I meaningfully built or committed to. Ideally ONE entry per project. Include what it does, current status, and any key decisions. Use the project name or a short descriptor as the first words of the entry.

5. **Preferences**: Opinions, tastes, and working-style preferences that apply broadly.

6. **Other**: Things that don't fall into any of the previous categories but are noteworthy due to their frequency, repetition, and/or importance.

## Format:

Use section headers for each category. Within each category, list one entry per line, sorted by oldest date first. Format each line as:

[YYYY-MM-DD] - Entry content here.

If no date is known, use [unknown] instead.

## Output:
- Wrap the entire export in a single code block for easy copying.
- After the code block, state whether this is the complete set or if more remains.
```

---

**Paste the result here and I'll save it to your AdaDrive.**

When they paste the result:
- Save it to `<DRIVE_PATH>/imported-memory.md` using the Write tool, with a header:
  ```markdown
  # Imported Memory

  Imported on <today's date>. Source: <ask which assistant if not obvious from context>.

  ---

  <their pasted content>
  ```
- Commit it:
  ```bash
  git -C <DRIVE_PATH> add imported-memory.md
  git -C <DRIVE_PATH> commit -m "Import memory from <source>"
  git -C <DRIVE_PATH> push 2>&1 || true
  ```

If they say no or skip: continue to Step 8.

---

## Step 8: Update global CLAUDE.md

Ask: **"Can I add a line to your global `~/.claude/CLAUDE.md` so Claude Code always reads your memory before starting work?"**

If they say yes:
```bash
mkdir -p ~/.claude
echo "" >> ~/.claude/CLAUDE.md
echo "Personal AI memory: <DRIVE_PATH> — read AGENTS.md there before starting work." >> ~/.claude/CLAUDE.md
```

---

## Step 9: Register in Claude Desktop (optional)

Ask: **"Do you use Claude Desktop (the desktop app)? I can register the AdaDrive MCP server there so Claude Chat also has access to your memory."**

If yes — run the install script (it auto-detects Claude Desktop and registers if found):
```bash
bash ${CLAUDE_PLUGIN_ROOT}/hooks/install-deps.sh
```

Then tell them: **"Restart Claude Desktop to pick up the new connection."**

If no or unsure — skip, no action needed. Registration happens automatically on the next Claude Code session start anyway.

---

## Step 10: Print summary

Tell the user:

```
✓ AdaDrive is ready!

  Local path:  <DRIVE_PATH>
  GitHub repo: https://github.com/<GITHUB_REPO>   (or "not connected" if skipped)
  Setup:       <AI memory / Blank>

What's set up:
  - AGENTS.md — instructions for AI agents
  - README.md — overview for humans
  [if memory was imported]
  - imported-memory.md — your imported context from <source>
  [if CLAUDE.md was updated]
  - ~/.claude/CLAUDE.md — Claude Code will read your memory automatically
  [if Claude Desktop registered]
  - Claude Desktop — restart the app to activate

Next steps:
  - Start a conversation anywhere — Claude will now remember you across sessions
  - Run /ada-drive:status to see what's in your drive
  - Run /ada-drive:sync to push changes to GitHub
```
