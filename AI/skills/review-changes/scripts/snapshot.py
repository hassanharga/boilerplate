#!/usr/bin/env python3
"""Exact Git blob export and evidence manifests, without checkout filters.

Usage: snapshot.py export <revision|index|local> <destination>
       snapshot.py fingerprint <index|local>
       snapshot.py seal <packet> | verify <packet>
Run from the repository root. Standard library only. Submodules are recorded as
coverage gaps, never represented as if their contents had been exported.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def git(*args):
    return subprocess.check_output(['git', *args])


def entries(source):
    if source == 'index':
        records = git('ls-files', '--stage', '-z').split(b'\0')
    else:
        records = git('ls-tree', '-rz', source).split(b'\0')
    result = []
    for raw in filter(None, records):
        meta, path = raw.split(b'\t', 1)
        mode, value, last = meta.split()
        if source == 'index':
            if last != b'0':
                raise ValueError('unmerged index; resolve the review target explicitly')
            oid = value
        else:
            oid = last
        result.append((mode.decode(), oid.decode(), os.fsdecode(path)))
    return result


def local_paths():
    return sorted(set(os.fsdecode(p) for p in
        git('ls-files', '--cached', '--others', '--exclude-standard', '-z').split(b'\0') if p))


def digest_file(path):
    # A tracked directory can be replaced by a symlink in local work. Its old
    # child paths are deletions, never permission to follow the link externally.
    if any(parent.is_symlink() for parent in path.parents if str(parent) != '.'):
        return {'kind': 'obscured_by_symlink'}
    if path.is_symlink():
        return {'kind': 'symlink', 'sha256': hashlib.sha256(os.fsencode(os.readlink(path))).hexdigest()}
    if path.is_file():
        return {'kind': 'file', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'executable': bool(path.stat().st_mode & 0o111)}
    return {'kind': 'missing' if not path.exists() else 'directory'}


def fingerprint(source):
    index = entries('index')
    if source == 'index':
        data = index
    else:
        data = {'index': index, 'files': {p: digest_file(Path(p)) for p in local_paths()}}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def safe_target(dest, name):
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('unsafe repository path')
    path = dest / relative
    for parent in path.parents:
        if parent == dest:
            break
        if parent.is_symlink():
            raise ValueError('symlink parent in snapshot')
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def export(source, dest):
    dest.mkdir()  # Never merge into or replace an existing snapshot.
    gaps = []
    if source == 'local':
        submodules = {p for mode, _, p in entries('index') if mode == '160000'}
        for name in local_paths():
            src = Path(name)
            if name in submodules:
                gaps.append({'path': name, 'reason': 'submodule contents not captured'})
            elif any(parent.is_symlink() for parent in src.parents if str(parent) != '.'):
                continue
            elif src.is_symlink():
                os.symlink(os.readlink(src), safe_target(dest, name))
            elif src.is_file():
                shutil.copy2(src, safe_target(dest, name), follow_symlinks=False)
            elif src.exists():
                raise ValueError('unsupported working-tree entry: ' + name)
            # Absent tracked files are deletions, not copy failures.
    else:
        with subprocess.Popen(['git', 'cat-file', '--batch'], stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE) as proc:
            for mode, oid, name in entries(source):
                if mode == '160000':
                    gaps.append({'path': name, 'reason': 'submodule contents not captured', 'oid': oid})
                    continue
                proc.stdin.write((oid+'\n').encode())
                proc.stdin.flush()
                header = proc.stdout.readline().split()
                if len(header) != 3 or header[1] != b'blob':
                    raise ValueError('cannot read blob ' + oid)
                data = proc.stdout.read(int(header[2]))
                if len(data) != int(header[2]) or proc.stdout.read(1) != b'\n':
                    raise ValueError('truncated blob ' + oid)
                path = safe_target(dest, name)
                if mode == '120000':
                    os.symlink(os.fsdecode(data), path)
                else:
                    path.write_bytes(data)
                    path.chmod(0o755 if mode == '100755' else 0o644)
            proc.stdin.close()
            if proc.wait() != 0:
                raise ValueError('blob export failed')
    dest.with_name(dest.name+'-gaps.json').write_text(json.dumps(gaps, indent=2)+'\n')


def packet_manifest(packet):
    files = {}
    for name in ('snapshot', 'base-snapshot'):
        for parent, dirs, names in os.walk(packet/name, followlinks=False):
            # Include directory symlinks themselves, without following them.
            names += [d for d in dirs if (Path(parent)/d).is_symlink()]
            dirs[:] = [d for d in dirs if not (Path(parent)/d).is_symlink()]
            for item in names:
                path = Path(parent)/item
                files[str(path.relative_to(packet))] = digest_file(path)
    for name in ('diff.patch', 'files.txt', 'meta.json', 'snapshot-gaps.json',
                 'base-snapshot-gaps.json', 'pr.json', 'checks.json', 'existing-feedback.json'):
        path = packet/name
        if path.is_file():
            files[name] = digest_file(path)
    return files


def main():
    try:
        action, *args = sys.argv[1:]
        if action == 'export':
            export(args[0], Path(args[1]))
        elif action == 'fingerprint':
            print(fingerprint(args[0]))
        elif action == 'seal':
            packet = Path(args[0])
            (packet/'manifest.json').write_text(json.dumps(packet_manifest(packet), sort_keys=True, indent=2)+'\n')
        elif action == 'verify':
            packet = Path(args[0])
            if json.loads((packet/'manifest.json').read_text()) != packet_manifest(packet):
                raise ValueError('packet changed; recollect or revalidate the affected evidence')
            print('packet integrity: PASS')
        else:
            raise ValueError(__doc__)
    except (ValueError, OSError, IndexError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
