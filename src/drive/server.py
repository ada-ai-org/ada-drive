"""
ada-drive — a shared filesystem for humans and AI agents.

MCP server that reads/writes the local git-cloned drive folder.
Drive path is inferred from ~/.claude/CLAUDE.md or defaults to ~/AdaDrive/.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

# ── drive path ───────────────────────────────────────────────────


def _find_drive_path() -> Path:
    """Infer the local drive path.

    Checks ~/.claude/CLAUDE.md for a line like:
        Shared agent workspace: ~/AdaDrive/ — read AGENTS.md ...
    Falls back to ~/AdaDrive/.
    """
    claude_md = Path.home() / ".claude" / "CLAUDE.md"
    if claude_md.exists():
        for line in claude_md.read_text().splitlines():
            if line.startswith("Shared agent workspace:"):
                raw = line.split(":", 1)[1].strip()
                raw = raw.split("—")[0].strip().rstrip("/")
                if raw:
                    return Path(raw).expanduser()
    return Path.home() / "AdaDrive"


def _resolve(drive: Path, rel: str) -> Path:
    """Resolve a relative path inside the drive, blocking traversal."""
    target = (drive / rel).resolve()
    if not str(target).startswith(str(drive.resolve())):
        raise ValueError(f"Path '{rel}' escapes the drive directory")
    return target


# ── server setup ─────────────────────────────────────────────────

mcp = FastMCP(
    "ada-drive",
    instructions="""
You are connected to the user's Ada Drive — a shared workspace for humans and AI agents.
Read AGENTS.md to understand how to use this drive. Check relevant files for context before starting work.
""",
)


# ── tools ────────────────────────────────────────────────────────


@mcp.tool(
    description=(
        "Read a file or list a directory from the Ada Drive. "
        "Start by reading 'AGENTS.md' to understand how this drive is organised. "
        "End the path with '/' to list a directory."
    ),
    annotations={"readOnlyHint": True},
)
def drive_read(
    path: Annotated[
        str,
        Field(description="Path relative to drive root. E.g. 'AGENTS.md', 'projects/my-app/', 'notes/2026-03-28.md'"),
    ],
) -> str:
    """Read a file or list a directory."""
    drive = _find_drive_path()
    if not drive.exists():
        return f"Drive not found at {drive}. Run /drive:setup to initialise."

    if path.endswith("/") or (drive / path).is_dir():
        target = _resolve(drive, path.rstrip("/") or ".")
        entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name))
        if not entries:
            return "(empty directory)"
        return "\n".join(
            f"[{'dir' if e.is_dir() else 'file'}] {e.relative_to(drive)}"
            for e in entries
        )

    target = _resolve(drive, path)
    if not target.exists():
        return f"File not found: {path}"
    return target.read_text()


@mcp.tool(
    description=(
        "Write or update a file in the Ada Drive. "
        "Use this to save notes, decisions, session summaries, or any context worth keeping. "
        "After writing, call drive_sync to commit and push to GitHub."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
)
def drive_write(
    path: Annotated[
        str,
        Field(description="File path relative to drive root. E.g. 'projects/my-app/decisions.md'"),
    ],
    content: Annotated[
        str,
        Field(description="Full file content (plain markdown)."),
    ],
) -> str:
    """Write a file to the drive (does not commit — call drive_sync to push)."""
    drive = _find_drive_path()
    if not drive.exists():
        return f"Drive not found at {drive}. Run /drive:setup to initialise."

    target = _resolve(drive, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return f"Written: {path} (call drive_sync to commit and push)"


@mcp.tool(
    description=(
        "Search the Ada Drive for files whose content matches a query. "
        "Returns matching file paths — follow up with drive_read to see the content."
    ),
    annotations={"readOnlyHint": True},
)
def drive_search(
    query: Annotated[
        str,
        Field(description="Search terms. E.g. 'auth architecture', 'deployment', 'AGENTS'"),
    ],
) -> str:
    """Search file contents in the drive."""
    drive = _find_drive_path()
    if not drive.exists():
        return f"Drive not found at {drive}. Run /drive:setup to initialise."

    result = subprocess.run(
        ["grep", "-rl", "--include=*.md", query, str(drive)],
        capture_output=True,
        text=True,
    )
    if not result.stdout.strip():
        return f"No results for '{query}'."
    paths = [
        str(Path(p).relative_to(drive))
        for p in result.stdout.strip().splitlines()
    ]
    return f"Found {len(paths)} file(s):\n" + "\n".join(f"- {p}" for p in paths[:10])


@mcp.tool(
    description="Show recent git commits on the drive. Useful for seeing what changed and when.",
    annotations={"readOnlyHint": True},
)
def drive_history(
    path: Annotated[
        str | None,
        Field(description="Optional: filter to a specific file or subdirectory. Leave empty for all changes."),
    ] = None,
    limit: Annotated[
        int,
        Field(description="Number of recent commits to show. Default 10."),
    ] = 10,
) -> str:
    """Show recent git history for the drive."""
    drive = _find_drive_path()
    if not drive.exists():
        return f"Drive not found at {drive}. Run /drive:setup to initialise."

    cmd = [
        "git", "-C", str(drive),
        "log", f"--max-count={limit}",
        "--format=%h %as — %s",
    ]
    if path:
        cmd += ["--", path]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() or "No commits found."


@mcp.tool(
    description=(
        "Sync the Ada Drive with GitHub: pull latest changes, commit everything, and push. "
        "Call this after writing files to persist changes to GitHub."
    ),
    annotations={"readOnlyHint": False},
)
def drive_sync(
    message: Annotated[
        str,
        Field(description="Commit message describing what was changed. E.g. 'Add auth decisions for my-app'"),
    ],
) -> str:
    """Pull, commit all changes, and push to GitHub."""
    drive = _find_drive_path()
    if not drive.exists():
        return f"Drive not found at {drive}. Run /drive:setup to initialise."

    def _git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(drive), *args],
            capture_output=True,
            text=True,
        )

    _git("pull", "--rebase")
    _git("add", "-A")

    commit = _git("commit", "-m", message)
    if "nothing to commit" in commit.stdout + commit.stderr:
        _git("push")
        return "Nothing to commit. Drive is already up to date."

    push = _git("push")
    if push.returncode != 0:
        return f"Committed locally but push failed: {push.stderr.strip()}"

    return f"Synced: {message}"


# ── run ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
