#!/usr/bin/env python3
"""Prepare one task artifact directory with a folder-local .gitignore containing *.

Usage: python3 artifacts.py TASK_DIRECTORY
Preserve existing ignore rules. Reject repository roots and tracked artifact folders.
Never change a parent .gitignore, Git's exclusion configuration, or the index.
Outside Git, create only the directory. Keep both installed copies byte-identical.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['git', '-C', str(cwd), *args], capture_output=True,
                          text=True, check=False)


def prepare(raw: str) -> int:
    try:
        folder = Path(raw).resolve()
        existing = folder
        while not existing.exists():
            existing = existing.parent
        if not existing.is_dir():
            raise ValueError(f'not a directory: {existing}')
        if not shutil.which('git'):
            folder.mkdir(parents=True, exist_ok=True)
            print(f'Created {folder}; Git unavailable, exclusion unverified.')
            return 0
        location = git(existing, 'rev-parse', '--show-toplevel')
        if location.returncode:
            if 'not a git repository' not in location.stderr.lower():
                raise ValueError(location.stderr.strip() or 'cannot determine Git root')
            folder.mkdir(parents=True, exist_ok=True)
            print(f'Created {folder}; outside Git, exclusion not applicable.')
            return 0
        root = Path(location.stdout.strip()).resolve()
        if folder == root or not folder.is_relative_to(root):
            raise ValueError('choose a task folder inside the repository, never its root')
        relative = folder.relative_to(root).as_posix()
        tracked = git(root, 'ls-files', '--', relative)
        if tracked.returncode or tracked.stdout.strip():
            raise ValueError('task folder contains tracked/staged files; preserve them and resolve ownership first')
        folder.mkdir(parents=True, exist_ok=True)
        ignore = folder / '.gitignore'
        if ignore.is_symlink():
            raise ValueError('refusing to follow a .gitignore symlink')
        data = ignore.read_bytes() if ignore.exists() else b''
        # Append last so earlier negations cannot cancel the task-folder rule.
        if not data.splitlines() or data.splitlines()[-1] != b'*':
            data += (b'\n' if data and not data.endswith(b'\n') else b'') + b'*\n'
            ignore.write_bytes(data)
        for name in ('.gitignore', 'task.md', 'plan.md', 'review.md', 'implementation.md'):
            result = git(root, 'check-ignore', '-q', '--', f'{relative}/{name}')
            if result.returncode:
                raise ValueError(f'Git did not confirm exclusion of {folder / name}')
        print(f'Artifacts ignored by {ignore}')
        return 0
    except (OSError, ValueError) as exc:
        print(f'Artifact setup blocked: {exc}', file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task_directory')
    args = parser.parse_args()
    return prepare(args.task_directory)


if __name__ == '__main__':
    raise SystemExit(main())
