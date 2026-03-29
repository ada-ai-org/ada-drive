"""CLI for ada-drive — init, sync, status, serve."""

from __future__ import annotations

import argparse
import subprocess
import sys


def _git(drive: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", drive, *args], capture_output=True, text=True)


# ── init ─────────────────────────────────────────────────────────

def cmd_init(args: argparse.Namespace) -> None:
    """Create a new private GitHub repo for the drive."""
    repo_name = args.repo or "ada-drive"
    result = subprocess.run(
        [
            "gh", "repo", "create", repo_name,
            "--private",
            "--description", "My Ada Drive — a shared filesystem for humans and AI agents",
        ],
        text=True,
    )
    if result.returncode != 0:
        sys.exit(result.returncode)
    print()
    print("GitHub repo created. Run /drive:setup in Claude Code to clone and initialise it.")


# ── sync ─────────────────────────────────────────────────────────

def cmd_sync(args: argparse.Namespace) -> None:
    """Pull, commit all local changes, and push."""
    from drive.server import _find_drive_path

    drive = str(_find_drive_path())
    message = args.message or "Update Ada Drive"

    _git(drive, "pull", "--rebase")
    _git(drive, "add", "-A")

    commit = _git(drive, "commit", "-m", message)
    if "nothing to commit" in commit.stdout + commit.stderr:
        print("Nothing to commit. Drive is already up to date.")
        _git(drive, "push")
        return

    push = _git(drive, "push")
    if push.returncode != 0:
        print(f"Committed locally but push failed:\n{push.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    print(f"Synced: {message}")


# ── status ───────────────────────────────────────────────────────

def cmd_status(args: argparse.Namespace) -> None:
    """Show local drive path, remote, working tree state, and recent commits."""
    from drive.server import _find_drive_path

    drive = _find_drive_path()
    print(f"Ada Drive: {drive}")

    if not drive.exists():
        print("Drive not found. Run /drive:setup to initialise.")
        return

    remote = _git(str(drive), "remote", "get-url", "origin")
    if remote.returncode == 0:
        print(f"GitHub:    {remote.stdout.strip()}")

    status = _git(str(drive), "status", "--short")
    if status.stdout.strip():
        print(f"\nUncommitted changes:\n{status.stdout.rstrip()}")
    else:
        print("\nWorking tree clean.")

    log = _git(str(drive), "log", "--max-count=5", "--format=%h %as — %s")
    if log.stdout.strip():
        print("\nRecent commits:")
        for line in log.stdout.strip().splitlines():
            print(f"  {line}")


# ── serve ────────────────────────────────────────────────────────

def cmd_serve(args: argparse.Namespace) -> None:
    """Start the MCP server (for chat agents)."""
    from drive.server import mcp

    if args.stdio:
        mcp.run(transport="stdio")
    else:
        port = args.port or 8000
        print(f"Starting ada-drive MCP server on http://localhost:{port}/mcp")
        mcp.run(transport="streamable-http", port=port)


# ── main ─────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ada-drive",
        description="A shared filesystem for humans and AI agents.",
    )
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Create the Ada Drive GitHub repo")
    p_init.add_argument("--repo", default="ada-drive", help="Repo name (default: ada-drive)")

    p_sync = sub.add_parser("sync", help="Pull, commit all changes, and push")
    p_sync.add_argument("--message", "-m", default="Update Ada Drive", help="Commit message")

    sub.add_parser("status", help="Show drive path, sync state, and recent commits")

    p_serve = sub.add_parser("serve", help="Start the MCP server")
    p_serve.add_argument("--stdio", action="store_true", help="Use stdio transport")
    p_serve.add_argument("--port", type=int, default=8000, help="HTTP port (default: 8000)")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
