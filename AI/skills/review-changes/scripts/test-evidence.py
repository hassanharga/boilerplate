"""Focused offline regressions for collection, profiling, and report anchors.

Run: python3 -B scripts/test-evidence.py
Only disposable repositories are mutated; no downloads or service calls.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.hooksPath', '/dev/null')
        self.write('a.txt', 'base\n')
        self.commit()

    def call(self, *args, cwd=None, stdin=None):
        env = {**os.environ, 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'}
        return subprocess.run(args, cwd=cwd or self.repo, input=stdin,
                              capture_output=True, text=True, env=env)

    def git(self, *args):
        p = self.call('git', *args)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.strip()

    def write(self, name, body):
        f = self.repo / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(body)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        return self.git('rev-parse', 'HEAD')

    def collect(self, kind, *args, cwd=None):
        packet = self.root / ('packet-' + str(len(list(self.root.glob('packet-*')))))
        p = self.call('bash', str(SCRIPTS/'collect.sh'), str(packet), kind, *args, cwd=cwd)
        return packet, p

    def test_local_deletion_and_untracked_from_nested_directory(self):
        self.write('sub/new file.txt', 'untracked\n')
        (self.repo/'a.txt').unlink()
        packet, p = self.collect('local', cwd=self.repo/'sub')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertFalse((packet/'snapshot/a.txt').exists())
        self.assertEqual((packet/'snapshot/sub/new file.txt').read_text(), 'untracked\n')
        self.assertIn('sub/new file.txt', (packet/'diff.patch').read_text())
        self.assertTrue((packet/'base-snapshot/a.txt').is_file())
        self.assertTrue((packet/'manifest.json').is_file())

    def test_export_attributes_do_not_change_reviewed_content(self):
        self.write('.gitattributes', 'a.txt export-ignore\nb.txt export-subst\n')
        self.write('b.txt', '$Format:%H$\n')
        self.commit()
        packet, p = self.collect('commit', 'HEAD')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual((packet/'snapshot/a.txt').read_text(), 'base\n')
        self.assertEqual((packet/'snapshot/b.txt').read_text(), '$Format:%H$\n')

    def test_staged_snapshot_excludes_unstaged_content(self):
        self.write('a.txt', 'staged\n')
        self.git('add', 'a.txt')
        self.write('a.txt', 'unstaged\n')
        packet, p = self.collect('staged')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual((packet/'snapshot/a.txt').read_text(), 'staged\n')
        self.assertTrue((packet/'base-snapshot/a.txt').is_file())

    def test_merge_requires_explicit_parent(self):
        base = self.git('rev-parse', 'HEAD')
        self.git('checkout', '-qb', 'other')
        self.write('other.txt', 'other\n')
        self.commit()
        self.git('checkout', '-qb', 'main-fixture', base)
        self.write('main.txt', 'main\n')
        self.commit()
        self.git('merge', '--no-ff', '-qm', 'merge fixture', 'other')
        _, p = self.collect('commit', 'HEAD')
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('parent', p.stderr.lower())
        packet, p = self.collect('commit', 'HEAD', '--parent', '2')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads((packet/'meta.json').read_text())['base'], self.git('rev-parse', 'HEAD^2'))

    def test_existing_packet_is_never_destroyed_or_reused(self):
        packet, p = self.collect('commit', 'HEAD')
        self.assertEqual(p.returncode, 0, p.stderr)
        marker = packet/'keep.txt'
        marker.write_text('keep')
        p = self.call('bash', str(SCRIPTS/'collect.sh'), str(packet), 'local')
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(marker.read_text(), 'keep')

    def test_manifest_detects_content_and_extra_file_changes(self):
        packet, p = self.collect('commit', 'HEAD')
        self.assertEqual(p.returncode, 0, p.stderr)
        def verify():
            return self.call('python3', '-B', str(SCRIPTS/'snapshot.py'), 'verify', str(packet))
        self.assertEqual(verify().returncode, 0)
        (packet/'snapshot/a.txt').write_text('tampered\n')
        self.assertNotEqual(verify().returncode, 0)
        (packet/'snapshot/a.txt').write_text('base\n')
        (packet/'snapshot/extra.txt').write_text('extra')
        self.assertNotEqual(verify().returncode, 0)

    def test_exact_export_preserves_symlink_and_executable(self):
        self.write('run.sh', '#!/bin/sh\nexit 0\n')
        (self.repo/'run.sh').chmod(0o755)
        (self.repo/'link').symlink_to('a.txt')
        self.commit()
        packet,p = self.collect('commit','HEAD')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(os.readlink(packet/'snapshot/link'),'a.txt')
        self.assertTrue((packet/'snapshot/run.sh').stat().st_mode & 0o111)

    def test_submodule_gap_is_explicit_in_metadata(self):
        oid=self.git('rev-parse','HEAD')
        self.git('update-index','--add','--cacheinfo','160000,'+oid+',dependency')
        self.git('commit','-qm','gitlink fixture')
        packet,p=self.collect('commit','HEAD')
        self.assertEqual(p.returncode,0,p.stderr)
        meta=json.loads((packet/'meta.json').read_text())
        self.assertFalse(meta['snapshot_complete'])
        self.assertEqual(meta['snapshot_gaps'][0]['path'],'dependency')

    def test_source_fingerprint_is_saved_and_changes_with_working_tree(self):
        packet,p=self.collect('local')
        self.assertEqual(p.returncode,0,p.stderr)
        fingerprint=json.loads((packet/'meta.json').read_text())['source_fingerprint']
        self.assertEqual(len(fingerprint),64)
        self.write('a.txt','changed again\n')
        p=self.call('python3','-B',str(SCRIPTS/'snapshot.py'),'fingerprint','local')
        self.assertNotEqual(fingerprint,p.stdout.strip())

    def test_rewritten_range_retains_both_exact_snapshots(self):
        base=self.git('rev-parse','HEAD')
        self.write('a.txt','old review\n')
        previous=self.commit()
        self.git('checkout','-qb','rewritten',base)
        self.write('a.txt','new review\n')
        current=self.commit()
        packet,p=self.collect('range',previous,current)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('not an ancestor',p.stderr)
        self.assertEqual((packet/'base-snapshot/a.txt').read_text(),'old review\n')
        self.assertEqual((packet/'snapshot/a.txt').read_text(),'new review\n')

    def test_profile_changed_package_and_instruction_chain(self):
        ancestor = self.root/'AGENTS.md'
        ancestor.write_text('ancestor rules')
        self.write('package.json', '{"private":true,"workspaces":["apps/*"]}')
        self.write('apps/web/package.json', json.dumps({'dependencies':{'react':'19'},
                    'packageManager':'pnpm@10', 'scripts':{'test':'node --test'}}))
        self.write('apps/web/src/deep/AGENTS.md', 'path rules')
        self.write('apps/web/src/deep/page.js', 'export default 1;')
        paths = self.root/'paths.txt'
        paths.write_text('M\tapps/web/src/deep/page.js\n')
        p = self.call('bash', str(SCRIPTS/'profile.sh'), str(self.repo), '--files', str(paths))
        self.assertEqual(p.returncode, 0, p.stderr)
        profile = json.loads(p.stdout)
        self.assertIn('frontend.md', profile['stack_references'])
        self.assertIn(str(ancestor), profile['instruction_files'])
        self.assertIn('apps/web/src/deep/AGENTS.md', profile['instruction_files'])
        package = next(x for x in profile['packages'] if x['path'] == 'apps/web')
        self.assertEqual(package['commands']['test']['command'], 'pnpm test')

    def test_profile_accepts_changes_under_build_named_directories(self):
        self.write('package.json', json.dumps({'scripts':{'test':'node --test','test:unit':'node --test unit',
                    'test:watch':'node --test --watch','test:cov':'c8 node --test'}}))
        self.write('scripts/build/deploy.sh', 'echo old\n')
        self.commit()
        self.write('scripts/build/deploy.sh', 'echo new\n')
        paths = self.root/'paths.txt'
        paths.write_text('M\tscripts/build/deploy.sh\nM\tdist/out.js\n')
        p = self.call('bash', str(SCRIPTS/'profile.sh'), str(self.repo), '--files', str(paths))
        self.assertEqual(p.returncode, 0, p.stderr)
        commands = json.loads(p.stdout)['commands']['scripts']
        self.assertEqual(sorted(commands), ['test', 'test:unit'])

    def test_profile_output_is_relative_to_invocation_directory(self):
        p=self.call('bash',str(SCRIPTS/'profile.sh'),str(self.repo),'profile.json',cwd=self.root)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue((self.root/'profile.json').is_file())
        self.assertFalse((self.repo/'profile.json').exists())

    def test_quoted_unicode_paths_are_discovered_and_validated(self):
        name='café\tfile.txt'
        self.write(name,'old guard\n')
        self.commit()
        self.write(name,'new guard\n')
        packet,p=self.collect('local')
        self.assertEqual(p.returncode,0,p.stderr)
        p=self.call('bash',str(SCRIPTS/'profile.sh'),str(packet/'snapshot'),
                    '--files',str(packet/'files.txt'))
        self.assertEqual(p.returncode,0,p.stderr)
        # Directly test the diff parser; Markdown anchors cannot represent a tab.
        import importlib.util
        spec=importlib.util.spec_from_file_location('diff_anchors',SCRIPTS/'diff-anchors.py')
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        changed=module.changed_lines(packet/'diff.patch')
        self.assertEqual(changed[('RIGHT',name)],{1})

    def test_untracked_unicode_and_control_path_profile(self):
        for name in ('café.txt','café\tfile.txt','control\x1b.txt'):
            self.write(name,'untracked\n')
        packet,p=self.collect('local')
        self.assertEqual(p.returncode,0,p.stderr)
        p=self.call('bash',str(SCRIPTS/'profile.sh'),str(packet/'snapshot'),
                    '--files',str(packet/'files.txt'))
        self.assertEqual(p.returncode,0,p.stderr)

    def test_deleted_left_anchor_and_rename(self):
        self.write('gone.txt', 'required guard\n')
        self.write('old name.txt', 'old guard\n')
        self.commit()
        (self.repo/'gone.txt').unlink()
        self.git('mv', 'old name.txt', 'new name.txt')
        self.write('new name.txt', 'new guard\n')
        packet, p = self.collect('local')
        self.assertEqual(p.returncode, 0, p.stderr)
        for anchor in ('gone.txt:1 [LEFT]', 'old name.txt:1 [LEFT]', 'new name.txt:1 [RIGHT]'):
            report = '\n'.join(['## Summary','Changes guards.','## Review path','Read guards.',
                '## Findings',f'Guard changed: {anchor}', 'Type: Issue - Blocking',
                'Issue: Invalid input passes.', 'Impact: Bad state.', 'Fix: Restore guard.',
                '## Conflict notes','None.','## AC coverage','Inferred.','## Verdict','Blocking yes.'])
            p = self.call('python3', '-B', str(SCRIPTS/'check-report.py'), '-', '--publish',
                          '--snapshot', str(packet/'snapshot'), '--base-snapshot', str(packet/'base-snapshot'),
                          '--diff', str(packet/'diff.patch'), '--json', stdin=report)
            self.assertEqual(p.returncode, 0, anchor + ': ' + p.stdout + p.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
