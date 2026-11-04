"""Focused behavioral tests. Standard library only; disposable fixtures, no installs.

Run: python3 -B -m unittest discover -s <skill-dir>/tests -p test_contract.py -v
Keep this file and the shared scripts byte-identical in both skills.
"""
from __future__ import annotations
import hashlib
import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
PAIR = SKILL.parent
SIBLINGS = ('plan-and-challenge', 'implement-plan')
GATE = SKILL / 'scripts/fingerprint.py'
HYGIENE = SKILL / 'scripts/artifacts.py'
# Exercise the literal agents actually copy, rather than a second expected constant.
# Read this skill's own copy so the suite still runs when the sibling is not installed.
def documented_stamp(skill=SKILL):
    text = (skill / 'references/strict-workflow.md').read_text()
    blocks = re.findall(r'```markdown\n(.*?)\n```', text, re.S)
    candidates = [block.split('\n> **Review:**', 1)[0] for block in blocks
                  if block.startswith('> **Execution gate:**')]
    if len(candidates) != 1:
        raise ValueError(f'expected one documented execution stamp in {skill}')
    return candidates[0]


STAMP = documented_stamp()
# A filled-in Protocol State: the gate requires the approved run to declare its own budget.
PROTOCOL = {'Mode': 'full', 'Challenge venue': 'fresh subagent', 'Current owner': 'controller',
            'Next action': 'none; approval recorded', 'Required review lens': 'general',
            'Round': '1 of 2', 'Review dispatches used': '2 of 4',
            'Reviser dispatches used': '1 of 2', 'Delegation': 'usable and authorized'}


def run(*args, cwd=None):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_NOSYSTEM='1')
    return subprocess.run([str(a) for a in args], cwd=cwd, env=env,
                          capture_output=True, text=True, check=False)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fields(heading, values):
    return heading + '\n' + ''.join(f'- {k}: {v}\n' for k, v in values.items())


def run_block(run_id, decisions, mode='full', state=None):
    values = dict(PROTOCOL, Mode=mode) if state is None else state
    return (f'## Run {run_id}\n\n' + fields('## Protocol State', values) + '\n' +
            '\n'.join(fields('## Final Decision', decision) for decision in decisions))


class Fixture(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='plan-contract-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
        return path


class GateContract(Fixture):
    def setUp(self):
        super().setUp()
        self.task = self.write('task.md', 'Return the original value.\n')
        self.spec = self.write('spec.md', 'Do not change whitespace.\n')
        self.plan = self.write('plan.md', STAMP + '\n> **Review:** `./review.md`\n'
                               '> **Specification:** `./spec.md`\nT1: Return the original value.\n')
        self.review = self.root / 'review.md'
        self.evidence = self.root / 'verdict.md'
        self.record()

    def record(self, *, mode='full', role='verifier', verdict='CLEAR', reviewer='agent-v',
               specification=True):
        artifacts = {'Task snapshot': 'task.md', 'Task fingerprint': digest(self.task),
                     'Plan': 'plan.md', 'Plan fingerprint': digest(self.plan),
                     'Specification': 'spec.md' if specification else 'none',
                     'Specification fingerprint': digest(self.spec) if specification else 'none'}
        self.ev = {'Run ID': '1', 'Role': role, 'Reviewer': reviewer, 'Verdict': verdict,
                   **artifacts}
        if role == 'user':
            self.ev['User approval'] = 'Explicit message: I approve these reviewed bytes.'
        self.save_evidence()
        self.fd = {'Status': 'APPROVED', 'Approval schema': 'plan-approval-v2',
                   'Fingerprint algorithm': 'sha256-exact-bytes-v1', 'Run ID': '1',
                   'Review mode': mode, **artifacts,
                   'Evidence': 'verdict.md', 'Evidence fingerprint': digest(self.evidence),
                   'Open minor findings': '0', 'Verdict by': reviewer, 'Recorded by': 'controller'}
        self.save_review()

    def save_evidence(self):
        self.evidence.write_text('Coverage and constraint evidence from the reviewer.\n\n' +
                                 fields('## Review Evidence', self.ev))

    def save_review(self):
        self.review.write_text(run_block(self.fd['Run ID'], [self.fd],
                                         mode=self.fd['Review mode']))

    def verify(self, expected=0, supplied=None):
        result = run(sys.executable, '-B', GATE, '--verify', self.review,
                     '--plan', supplied or self.plan)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_complete_approval_passes(self):
        self.verify()

    def test_minor_task_must_be_a_declaration(self):
        original = self.plan.read_text()
        for extra in ('T99 is not planned.', 'T990: Another task.'):
            with self.subTest(extra=extra):
                self.plan.write_text(original + '\n' + extra)
                self.record()
                self.fd['Open minor findings'] = '1; PLAN-001: address in task T99'
                self.save_review()
                self.verify(1)

    def test_minor_task_declaration_formats_pass(self):
        original = self.plan.read_text()
        for declaration in ('### T99 — Follow up', '### Task T99: Follow up',
                            '| T99 | Follow up |', '- **T99**: Follow up'):
            with self.subTest(declaration=declaration):
                self.plan.write_text(original + '\n' + declaration)
                self.record()
                self.fd['Open minor findings'] = '1; PLAN-001: address in task T99'
                self.save_review()
                self.verify()

    def test_protocol_placeholder_words_are_rejected(self):
        for value in ('pending', 'none', 'unknown', 'n/a'):
            with self.subTest(value=value):
                self.review.write_text(run_block('1', [self.fd], state=dict(
                    PROTOCOL, **{'Current owner': value})))
                self.verify(1)

    def test_mode_specific_review_limits(self):
        for mode, updates in (
            ('full', {'Round': '2 of 2', 'Review dispatches used': '2 of 4'}),
            ('lightweight', {'Review dispatches used': '3 of 4'}),
            ('lightweight', {'Reviser dispatches used': '2 of 2'}),
            ('lightweight', {'Round': '2 of 2'}),
        ):
            with self.subTest(mode=mode, updates=updates):
                self.record(mode=mode, role='verifier' if mode == 'full' else 'lightweight-challenger')
                state = dict(PROTOCOL, Mode=mode, **updates)
                self.review.write_text(run_block('1', [self.fd], state=state))
                self.verify(1)

    def append_decisions(self, statuses):
        self.review.write_text(run_block('1', [dict(self.fd, Status=status) for status in statuses],
                                         mode=self.fd['Review mode']))

    def test_pending_to_approval_passes(self):
        self.append_decisions(['Pending', 'APPROVED'])
        self.verify()

    def test_blocked_round_report_before_final_approval_passes(self):
        self.review.write_text(run_block('1', [dict(self.fd, Status='Pending')]) +
                               '\n## Round 1\nChallenger: BLOCKED; revision and verifier: CLEAR.\n' +
                               fields('## Final Decision', self.fd))
        self.verify()

    def test_blocked_run_can_be_followed_by_new_approved_run(self):
        self.append_decisions(['BLOCKED'])
        old = self.review.read_text()
        self.ev['Run ID'] = self.fd['Run ID'] = '2'
        self.save_evidence()
        self.fd['Evidence fingerprint'] = digest(self.evidence)
        self.review.write_text(old + '\n' + run_block('2', [self.fd]))
        self.verify()

    def test_ready_to_explicit_user_approval_passes(self):
        self.record(mode='local-fallback', role='user', verdict='APPROVED', reviewer='user')
        self.append_decisions(['Pending', 'READY_FOR_USER_APPROVAL', 'APPROVED'])
        self.verify()

    def test_terminal_decisions_cannot_be_reopened_in_same_run(self):
        for status in ('BLOCKED', 'APPROVED'):
            with self.subTest(status=status):
                self.append_decisions(['Pending', status, 'APPROVED'])
                self.verify(1)

    def test_ready_cannot_bypass_user_approval(self):
        self.append_decisions(['READY_FOR_USER_APPROVAL', 'APPROVED'])
        self.verify(1)

    def test_ready_cannot_reset_to_pending(self):
        self.append_decisions(['READY_FOR_USER_APPROVAL', 'Pending', 'APPROVED'])
        self.verify(1)

    def test_earlier_decision_must_match_current_run(self):
        earlier = dict(self.fd, Status='Pending')
        earlier['Run ID'] = 'old'
        self.review.write_text(run_block('1', [earlier, self.fd]))
        self.verify(1)

    def test_postapproval_activity_in_all_visible_forms_is_rejected(self):
        for activity in ('## Later round: BLOCKED', 'Later round was BLOCKED.',
                         '**Later round: BLOCKED**', '- Later round: BLOCKED',
                         '> Later round: BLOCKED', '    Later round: BLOCKED'):
            with self.subTest(activity=activity):
                self.save_review()
                self.review.write_text(self.review.read_text() + '\n' + activity + '\n')
                self.verify(1)

    def test_blank_lines_comments_and_fenced_examples_after_approval_pass(self):
        self.review.write_text(self.review.read_text() +
                               '\n<!-- explanatory comment -->\n```markdown\nexample\n```\n')
        self.verify()

    def test_external_task_symlink_is_rejected(self):
        outside = tempfile.TemporaryDirectory(prefix='external-task-')
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / 'snapshot.md'
        target.write_bytes(self.task.read_bytes())
        self.task.unlink()
        self.task.symlink_to(target)
        self.verify(1)

    def test_internal_task_symlink_is_rejected(self):
        target = self.write('snapshot.md', self.task.read_text())
        self.task.unlink()
        self.task.symlink_to(target)
        self.verify(1)

    def test_zero_minor_phrasings_pass(self):
        for value in ('0', 'none', 'None'):
            with self.subTest(value=value):
                self.fd['Open minor findings'] = value
                self.save_review()
                self.verify()

    def test_minor_ids_and_dispositions_pass(self):
        self.fd['Open minor findings'] = ('2; PLAN-001: address in task T1; '
                                         'PLAN-002: leave because naming follows local convention')
        self.save_review()
        self.verify()

    def test_malformed_minor_dispositions_fail(self):
        for value in ('banana', '1', '-1', '0; PLAN-001: leave because harmless',
                      '2; PLAN-001: address in task T1',
                      '2; PLAN-001: address in task T1; PLAN-001: address in task T2',
                      '1; PLAN-001: Pending', '1; PLAN-001: leave because',
                      '1; PLAN-001: address in task <task>',
                      '1; PLAN-001: address in task Pending'):
            with self.subTest(value=value):
                self.fd['Open minor findings'] = value
                self.save_review()
                self.verify(1)

    def test_minor_assigned_to_a_missing_task_is_rejected(self):
        self.fd['Open minor findings'] = '1; PLAN-001: address in task T99'
        self.save_review()
        self.verify(1)

    def test_minor_assigned_to_a_named_task_without_an_id_passes(self):
        self.fd['Open minor findings'] = '1; PLAN-001: address in task renaming the helper'
        self.save_review()
        self.verify()

    def test_no_specification_is_explicit_and_passes(self):
        self.plan.write_text(self.plan.read_text().replace('`./spec.md`', '`none`'))
        self.record(specification=False)
        self.verify()

    def test_missing_task_is_rejected(self):
        del self.fd['Task snapshot']
        del self.fd['Task fingerprint']
        self.save_review()
        self.verify(1)

    def test_none_task_is_rejected(self):
        self.fd['Task snapshot'] = self.fd['Task fingerprint'] = 'none'
        self.save_review()
        self.verify(1)

    def test_unfinished_artifacts_are_rejected(self):
        for key in ('Task', 'Specification'):
            for placeholder in ('Pending', '<path>', ''):
                with self.subTest(key=key, placeholder=placeholder):
                    self.record()
                    self.fd['Task snapshot' if key == 'Task' else key] = placeholder
                    self.fd[key + ' fingerprint'] = placeholder
                    self.save_review()
                    self.verify(1)

    def test_changed_approved_inputs_are_rejected(self):
        for path in (self.task, self.spec, self.plan):
            with self.subTest(path=path.name):
                before = path.read_bytes()
                path.write_bytes(before + b'\n')
                self.verify(1)
                path.write_bytes(before)

    def test_missing_artifact_file_is_rejected(self):
        self.task.unlink()
        self.verify(1)

    def test_wrong_task_identity_is_rejected(self):
        self.write('other-task.md', self.task.read_text())
        self.fd['Task snapshot'] = self.ev['Task snapshot'] = 'other-task.md'
        self.save_evidence()
        self.fd['Evidence fingerprint'] = digest(self.evidence)
        self.save_review()
        self.verify(1)

    def test_wrong_plan_identity_is_rejected(self):
        self.verify(1, supplied=self.write('other.md', self.plan.read_text()))

    def test_nonapproved_statuses_are_rejected(self):
        for status in ('BLOCKED', 'Pending', 'READY_FOR_USER_APPROVAL'):
            with self.subTest(status=status):
                self.fd['Status'] = status
                self.save_review()
                self.verify(1)

    def test_legacy_schema_is_rejected(self):
        del self.fd['Approval schema']
        self.save_review()
        self.verify(1)

    def test_wrong_algorithm_is_rejected(self):
        self.fd['Fingerprint algorithm'] = 'md5'
        self.save_review()
        self.verify(1)

    def test_bad_digest_is_rejected(self):
        for value in ('0' * 64, '<digest>', 'abcd'):
            self.fd['Plan fingerprint'] = value
            self.save_review()
            self.verify(1)

    def test_conflicting_duplicate_fields_are_rejected(self):
        self.review.write_text(self.review.read_text().replace('- Status: APPROVED',
                                '- Status: BLOCKED\n- Status: APPROVED'))
        self.verify(1)

    def test_fenced_approval_cannot_override_blocked_decision(self):
        approved = fields('## Final Decision', self.fd)
        for fence in ('```', '~~~', '````'):
            with self.subTest(fence=fence):
                self.fd['Status'] = 'BLOCKED'
                self.save_review()
                self.review.write_text(self.review.read_text() + '\n' + fence + 'markdown\n' +
                                       approved + fence + '\n')
                self.verify(1)

    def test_commented_example_is_not_a_decision(self):
        approved = fields('## Final Decision', self.fd)
        self.fd['Status'] = 'BLOCKED'
        self.save_review()
        self.review.write_text(self.review.read_text() + '\n<!--\n' + approved + '-->\n')
        self.verify(1)

    def test_reopening_without_new_decision_revokes_approval(self):
        self.review.write_text(self.review.read_text() + '\n## Run 2\nPending challenge.\n')
        self.verify(1)

    def test_new_run_cannot_reuse_old_run_decision(self):
        self.review.write_text(self.review.read_text() + '\n' + run_block('2', [self.fd]))
        self.verify(1)

    def test_approved_new_run_with_new_evidence_passes(self):
        old = self.review.read_text()
        self.ev['Run ID'] = self.fd['Run ID'] = '2'
        self.save_evidence()
        self.fd['Evidence fingerprint'] = digest(self.evidence)
        self.review.write_text(old + '\n' + run_block('2', [self.fd]))
        self.verify()

    def test_missing_verdict_metadata_is_rejected(self):
        for key in ('Verdict by', 'Recorded by', 'Evidence', 'Evidence fingerprint'):
            with self.subTest(key=key):
                self.record()
                del self.fd[key]
                self.save_review()
                self.verify(1)

    def test_changed_evidence_is_rejected(self):
        self.evidence.write_text(self.evidence.read_text() + 'edited\n')
        self.verify(1)

    def test_post_verdict_change_cannot_be_approved_by_rehashing(self):
        self.plan.write_text(self.plan.read_text() + 'Unreviewed step.\n')
        self.fd['Plan fingerprint'] = digest(self.plan)
        self.save_review()
        self.verify(1)

    def test_full_review_requires_a_clear_verifier(self):
        self.record(role='challenger')
        self.verify(1)
        self.record(verdict='BLOCKED')
        self.verify(1)

    def test_lightweight_clear_challenger_passes(self):
        self.record(mode='lightweight', role='lightweight-challenger')
        self.verify()

    def test_explicit_user_approval_of_local_fallback_passes(self):
        self.record(mode='local-fallback', role='user', verdict='APPROVED', reviewer='user')
        self.verify()

    def test_local_fallback_needs_explicit_user_evidence(self):
        self.record(mode='local-fallback', role='user', verdict='APPROVED', reviewer='user')
        del self.ev['User approval']
        self.save_evidence()
        self.fd['Evidence fingerprint'] = digest(self.evidence)
        self.save_review()
        self.verify(1)

    def test_reviewer_identity_must_match(self):
        self.fd['Verdict by'] = 'some-other-agent'
        self.save_review()
        self.verify(1)

    def test_controller_cannot_clear_its_own_plan(self):
        for mode, role in (('full', 'verifier'), ('lightweight', 'lightweight-challenger')):
            with self.subTest(mode=mode):
                self.record(mode=mode, role=role, reviewer='controller')
                self.verify(1)

    def test_missing_protocol_state_is_rejected(self):
        self.review.write_text('## Run 1\n\n' + fields('## Final Decision', self.fd))
        self.verify(1)

    def test_unfinished_protocol_state_is_rejected(self):
        for key in PROTOCOL:
            for value in (None, '', '<unfilled template value>'):
                with self.subTest(key=key, value=value):
                    state = dict(PROTOCOL)
                    if value is None:
                        del state[key]
                    else:
                        state[key] = value
                    self.review.write_text(run_block('1', [self.fd], state=state))
                    self.verify(1)

    def test_protocol_state_mode_must_match_the_decision(self):
        self.record(mode='lightweight', role='lightweight-challenger')
        self.review.write_text(run_block('1', [self.fd], mode='full'))
        self.verify(1)

    def test_review_budget_overrun_is_rejected(self):
        for key, value in (('Round', '3 of 2'), ('Round', '0 of 2'),
                           ('Review dispatches used', '5 of 4'),
                           ('Review dispatches used', '2 of 9'),
                           ('Reviser dispatches used', '3 of 2'),
                           ('Review dispatches used', 'several')):
            with self.subTest(key=key, value=value):
                self.review.write_text(run_block('1', [self.fd],
                                                 state=dict(PROTOCOL, **{key: value})))
                self.verify(1)

    def test_full_mode_needs_a_challenger_and_a_fresh_verifier(self):
        state = dict(PROTOCOL, **{'Review dispatches used': '1 of 4'})
        self.review.write_text(run_block('1', [self.fd], state=state))
        self.verify(1)
        self.record(mode='lightweight', role='lightweight-challenger')
        self.review.write_text(run_block('1', [self.fd], state=dict(state, Mode='lightweight')))
        self.verify()

    def test_plan_review_link_is_enforced(self):
        original = self.plan.read_text()
        for replacement in ('', '> **Review:** `missing.md`',
                            '> **Review:** `review.md`\n> **Review:** `review.md`',
                            '> **Review:** [review](review.md)'):
            with self.subTest(replacement=replacement):
                self.plan.write_text(original.replace('> **Review:** `./review.md`', replacement))
                self.record()
                self.verify(1)

    def test_gate_stamp_is_enforced(self):
        self.plan.write_text(self.plan.read_text().replace(STAMP, 'Execute directly.'))
        self.record()
        self.verify(1)

    def test_specification_cannot_be_omitted_from_approval(self):
        self.record(specification=False)
        self.verify(1)

    def test_specification_can_live_outside_task_folder(self):
        outside = tempfile.TemporaryDirectory(prefix='external-spec-')
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / 'external.md'
        target.write_text(self.spec.read_text())
        self.plan.write_text(self.plan.read_text().replace('./spec.md', str(target)))
        self.record()
        self.fd['Specification'] = self.ev['Specification'] = str(target)
        self.save_evidence()
        self.fd['Evidence fingerprint'] = digest(self.evidence)
        self.save_review()
        self.verify()

    def test_paths_with_spaces_work_from_another_directory(self):
        target = self.root / 'task with spaces'
        target.mkdir()
        for path in (self.task, self.spec, self.plan, self.evidence, self.review):
            shutil.copyfile(path, target / path.name)
        result = run(sys.executable, '-B', GATE, '--verify', target / 'review.md',
                     '--plan', target / 'plan.md', cwd=self.root.parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_print_mode_hashes_saved_bytes(self):
        result = run(sys.executable, '-B', GATE, self.task, self.plan)
        self.assertEqual(result.returncode, 0)
        self.assertEqual([line.split('\t')[1] for line in result.stdout.splitlines()],
                         [digest(self.task), digest(self.plan)])

    def test_missing_review_fails_without_traceback(self):
        self.review.unlink()
        result = run(sys.executable, '-B', GATE, '--verify', self.review, '--plan', self.plan)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('Traceback', result.stderr)


@unittest.skipUnless(shutil.which('git'), 'Git unavailable')
class GitHygiene(Fixture):
    def setUp(self):
        super().setUp()
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.assertEqual(run('git', 'init', '-q', self.repo).returncode, 0)
        self.task = self.repo / 'docs/agent-plans/TASK'
        self.task.mkdir(parents=True)
        self.exclude = self.repo / '.git/info/exclude'
        self.exclude.write_text('# existing rule without newline')
        (self.repo / '.gitignore').write_text('unrelated.log\n')

    def prepare(self, expected=0):
        result = run(sys.executable, '-B', HYGIENE, self.task)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_folder_gitignore_ignores_itself_and_artifacts(self):
        self.prepare()
        self.assertEqual((self.task / '.gitignore').read_text(), '*\n')
        for name in ('.gitignore', 'task.md', 'plan.md', 'review.md', 'implementation.md', 'nested/verdict.md'):
            target = self.task / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if name != '.gitignore':
                target.write_text('artifact\n')
            self.assertEqual(run('git', 'check-ignore', '-q', '--', target,
                                 cwd=self.repo).returncode, 0, name)

    def test_parent_gitignore_and_exclude_remain_unchanged(self):
        before = self.exclude.read_bytes(), (self.repo / '.gitignore').read_bytes()
        self.prepare()
        self.assertEqual(before, (self.exclude.read_bytes(), (self.repo / '.gitignore').read_bytes()))

    def test_add_all_does_not_stage_artifacts(self):
        self.prepare()
        (self.task / 'plan.md').write_text('private artifact\n')
        (self.repo / 'source.py').write_text('value = 1\n')
        self.assertEqual(run('git', 'add', '-A', cwd=self.repo).returncode, 0)
        staged = run('git', 'diff', '--cached', '--name-only', cwd=self.repo).stdout.splitlines()
        self.assertIn('source.py', staged)
        self.assertFalse(any('agent-plans' in name for name in staged), staged)

    def test_existing_ignore_rules_preserved_without_trailing_newline(self):
        (self.task / '.gitignore').write_text('old-rule')
        self.prepare()
        self.assertEqual((self.task / '.gitignore').read_text(), 'old-rule\n*\n')

    def test_prepare_is_idempotent(self):
        self.prepare()
        before = (self.task / '.gitignore').read_bytes()
        self.prepare()
        self.assertEqual(before, (self.task / '.gitignore').read_bytes())

    def test_tracked_artifacts_block_without_modifying_index(self):
        (self.task / 'plan.md').write_text('existing tracked plan\n')
        self.assertEqual(run('git', 'add', '--', self.task / 'plan.md', cwd=self.repo).returncode, 0)
        index = (self.repo / '.git/index').read_bytes()
        self.prepare(1)
        self.assertEqual(index, (self.repo / '.git/index').read_bytes())
        self.assertFalse((self.task / '.gitignore').exists())

    def test_repository_root_is_rejected(self):
        before = (self.repo / '.gitignore').read_bytes()
        self.task = self.repo
        self.prepare(1)
        self.assertEqual(before, (self.repo / '.gitignore').read_bytes())

    def test_non_git_folder_is_supported(self):
        self.task = self.root / 'outside-git/task'
        self.prepare()
        self.assertTrue(self.task.is_dir())

    def test_linked_worktree_uses_folder_local_ignore(self):
        result = run('git', '-c', 'user.email=test@example.invalid', '-c', 'user.name=Test',
                     '-c', 'core.hooksPath=/dev/null', 'commit', '--allow-empty', '-qm', 'fixture', cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        linked = self.root / 'linked'
        result = run('git', 'worktree', 'add', '-b', 'fixture-linked', linked, cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.task = linked / 'docs/agent-plans/TASK'
        self.prepare()
        self.assertEqual((self.task / '.gitignore').read_text(), '*\n')


class PairStructure(unittest.TestCase):
    """Cross-skill checks. Each half is testable alone; both halves are checked when installed."""

    def installed(self):
        return [PAIR / name for name in SIBLINGS if (PAIR / name / 'SKILL.md').is_file()]

    def test_documented_stamp_matches_each_gate(self):
        for skill in self.installed():
            with self.subTest(skill=skill.name):
                spec = importlib.util.spec_from_file_location('stamp_gate', skill / 'scripts/fingerprint.py')
                gate = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(gate)
                self.assertEqual(documented_stamp(skill), gate.STAMP, skill.name)
                self.assertEqual(documented_stamp(skill), STAMP, 'documented stamps drifted apart')

    def test_shared_scripts_and_tests_are_identical(self):
        skills = self.installed()
        if len(skills) < len(SIBLINGS):
            self.skipTest('the sibling skill is not installed beside this one')
        for relative in ('scripts/fingerprint.py', 'scripts/artifacts.py', 'tests/test_contract.py'):
            with self.subTest(relative=relative):
                self.assertEqual(*[(skill / relative).read_bytes() for skill in skills])

    def test_review_templates_carry_every_field_the_gate_requires(self):
        # The gate reads Protocol State, so a template missing a field ships an unapprovable run.
        planning = PAIR / 'plan-and-challenge'
        if not (planning / 'SKILL.md').is_file():
            self.skipTest('plan-and-challenge is not installed beside this skill')
        spec = importlib.util.spec_from_file_location('gate_fields', GATE)
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        for name in ('review-template.md', 'light-review-template.md'):
            with self.subTest(template=name):
                text = (planning / 'assets' / name).read_text()
                block = text.split('## Protocol State', 1)[1].split('\n## ', 1)[0]
                present = {key.lower() for key in re.findall(r'^- ([^:]+):', block, re.M)}
                self.assertLessEqual(set(gate.PROTOCOL_FIELDS), present, name)

    def test_support_references_resolve(self):
        # Backticked paths and Markdown links both break silently when a file is renamed.
        pattern = (r'`((?:agents|references|assets|scripts|tests)/[a-z0-9._/-]+)`'
                   r'|\]\(((?:agents|references|assets|scripts|tests)/[a-z0-9._/-]+)\)')
        for skill in self.installed():
            for path in skill.rglob('*.md'):
                for backticked, linked in re.findall(pattern, path.read_text()):
                    reference = backticked or linked
                    self.assertTrue((skill / reference).is_file(), f'{path}: {reference}')


if __name__ == '__main__':
    unittest.main()
