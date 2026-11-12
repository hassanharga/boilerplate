#!/usr/bin/env python3
"""Enrich profile JSON on stdin with package-local routing and instruction chains.

Usage: workspace-profile.py <root> [changed-files.txt]
Changed files accept collector name-status output or one repository-relative path
per line. Without a list, discover packages and instruction files, pruning tool
and dependency directories. Commands are suggestions to inspect, never executed.
"""
import json
import importlib.util
import os
from pathlib import Path
import re
import sys

spec = importlib.util.spec_from_file_location('diff_anchors',Path(__file__).with_name('diff-anchors.py'))
path_helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(path_helpers)

PRUNE = {'.git', 'node_modules', 'vendor', 'dist', 'build', '.venv', 'venv', 'target', '.next', '__pycache__'}
FRAMEWORKS = {'@nestjs/core':'nestjs', 'next':'nextjs', 'react':'react', '@angular/core':'angular',
              'vue':'vue', 'express':'express', 'fastify':'fastify', 'jest':'jest', 'vitest':'vitest',
              '@playwright/test':'playwright', 'cypress':'cypress'}
RULES = ('AGENTS.md', 'CLAUDE.md', 'learnings.md', 'CONTRIBUTING.md')


def main():
    root = Path(sys.argv[1]).resolve()
    profile = json.load(sys.stdin)
    paths, manifests, discovered_rules, gaps = set(), set(), set(), []
    if len(sys.argv) > 2:
        for line in Path(sys.argv[2]).read_text().splitlines():
            fields = line.split('\t')
            for name in fields[1:] if len(fields)>1 else fields:
                # Git quotes paths containing tabs/newlines. Decode C-style quoting.
                name = path_helpers.decode_path(name)
                p = root/name
                if Path(name).is_absolute() or '..' in Path(name).parts:
                    raise ValueError('changed file outside permitted project paths: '+name)
                paths.add(p)
                for parent in [p.parent, *p.parent.parents]:
                    if not parent.is_relative_to(root): break
                    if (parent/'package.json').is_file(): manifests.add(parent/'package.json')
    else:
        def onerror(exc): gaps.append(str(exc))
        for parent, dirs, names in os.walk(root, onerror=onerror, followlinks=False):
            dirs[:] = [d for d in dirs if d not in PRUNE and not (Path(parent)/d).is_symlink()]
            if 'package.json' in names: manifests.add(Path(parent)/'package.json')
            discovered_rules.update(Path(parent)/n for n in names if n in RULES)
        paths.update(p.parent/'package.json' for p in manifests)
    if (root/'package.json').is_file(): manifests.add(root/'package.json')

    def label(p): return str(p.relative_to(root)) if p.is_relative_to(root) else str(p)

    def rules_for(p):
        # Read order is broad to specific. Ancestors can be outside the repository.
        return [parent/n for parent in reversed([p.parent, *p.parent.parents])
                for n in RULES if (parent/n).is_file()]

    scopes = {label(p):[label(r) for r in rules_for(p)] for p in sorted(paths)}
    rules = set(profile['instruction_files']) | {label(r) for r in discovered_rules}
    rules.update(label(r) for r in rules_for(root/'placeholder'))
    rules.update(r for chain in scopes.values() for r in chain)
    packages = []
    refs = set(profile['stack_references'])
    frameworks = set(profile['frameworks'])
    for manifest in sorted(manifests):
        try:
            if not manifest.resolve().is_relative_to(root):
                gaps.append(label(manifest)+': manifest points outside repository'); continue
            pkg = json.loads(manifest.read_text())
        except (OSError, ValueError) as exc:
            gaps.append(label(manifest)+': '+str(exc)); continue
        deps = {**pkg.get('dependencies',{}), **pkg.get('devDependencies',{})}
        fw = {name for dep,name in FRAMEWORKS.items() if dep in deps}
        if any(d.startswith('@yatechnologies/') for d in deps): fw.add('yassir-mobility-chassis')
        frameworks.update(fw)
        if fw & {'react','nextjs','angular','vue'}: refs.add('frontend.md')
        if {'nestjs','yassir-mobility-chassis'} <= fw: refs.add('yassir-nestjs-ddd.md')
        manager = None
        for parent in [manifest.parent,*manifest.parent.parents]:
            if not parent.is_relative_to(root): break
            parent_manifest = parent/'package.json'
            if parent_manifest.is_file():
                try: manager = json.loads(parent_manifest.read_text()).get('packageManager','').split('@')[0] or None
                except (OSError,ValueError): pass
            if manager: break
            for lock,pm in [('pnpm-lock.yaml','pnpm'),('yarn.lock','yarn'),('package-lock.json','npm'),('bun.lock','bun'),('bun.lockb','bun')]:
                if (parent/lock).is_file(): manager=pm; break
            if manager: break
        manager = manager or 'npm'
        run = 'npm run' if manager == 'npm' else manager
        commands = {key:{'command':run+' '+key,'runs':value} for key,value in pkg.get('scripts',{}).items()
                    if re.fullmatch(r'lint|typecheck|type-check|tsc|check|build|test|test:(?:unit|integration|e2e|component)|format:check',key)}
        packages.append({'path':label(manifest.parent), 'frameworks':sorted(fw),
                         'package_manager':manager, 'commands':commands})
    profile.update(packages=packages, frameworks=sorted(frameworks), stack_references=sorted(refs),
                   instruction_files=sorted(rules), instruction_scopes=scopes,
                   discovery={'scope':'changed paths' if len(sys.argv)>2 else 'repository excluding dependency/build directories',
                              'complete':not gaps,'gaps':gaps})
    root_package = next((p for p in packages if p['path']=='.'), None)
    if root_package:
        profile['commands']['scripts'] = root_package['commands']
    if packages:
        profile['languages'] = sorted(set(profile['languages']) | {'javascript'})
    print(json.dumps(profile,indent=2))


if __name__ == '__main__':
    main()
