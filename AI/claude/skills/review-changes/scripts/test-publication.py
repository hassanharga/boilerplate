"""Offline publisher recovery and identity regressions. No GitHub calls.

Run: python3 -B scripts/test-publication.py
"""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('publisher', SCRIPTS/'publish.py')
pub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pub)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'plan.json'
        self.head = 'a'*40
        self.plan = {'repo':'o/r', 'pr':1, 'commit':self.head, 'event':'COMMENT',
            'opener':'Reviewed the changed flow.', 'comments':[
            {'path':'a.ts','line':3,'side':'RIGHT','body':'x'*180+' first'}]}
        self.reviews = []
        self.comments = []
        self.writes = []
        self.fail_after = None
        self.fail_reads = False
        self.reject_write = None

    def gh(self, *args, payload=None):
        path = args[-1]
        if '-X' in args:
            kind = 'reviews' if path.endswith('/reviews') else 'comments'
            self.writes.append(kind)
            if self.reject_write:
                raise RuntimeError(self.reject_write)
            item = {'id':len(self.writes), 'user':{'login':'me'}, 'html_url':'https://example.invalid/result'}
            if kind == 'reviews':
                item.update(commit_id=payload['commit_id'], body=payload['body'],
                            state='COMMENTED' if payload['event']=='COMMENT' else 'CHANGES_REQUESTED')
                self.reviews.append(item)
            else:
                item.update(payload)
                self.comments.append(item)
            if self.fail_after == kind:
                self.fail_after = None
                raise RuntimeError('response lost after acceptance')
            return copy.deepcopy(item)
        if path == 'user': return {'login':'me'}
        if path.endswith('/reviews'):
            if self.fail_reads and self.writes: raise RuntimeError('read unavailable')
            return copy.deepcopy(self.reviews)
        if path.endswith('/comments'):
            if self.fail_reads and self.writes: raise RuntimeError('read unavailable')
            return copy.deepcopy(self.comments)
        return {'head':{'sha':self.head}, 'state':'open', 'merged':False, 'locked':False}

    def run_plan(self, yes=True):
        self.path.write_text(json.dumps(self.plan))
        out = io.StringIO()
        with patch.object(pub,'gh',self.gh), patch.object(sys,'argv',
            ['publish.py',str(self.path),'--json']+(['--yes'] if yes else [])), contextlib.redirect_stdout(out):
            code = pub.main()
        return code, json.loads(out.getvalue())

    def existing_review(self, state='COMMENTED'):
        self.reviews.append({'id':90,'user':{'login':'me'},'commit_id':self.head,
                             'body':self.plan['opener'],'state':state})

    def existing_comment(self, **changes):
        c = {'id':91,'user':{'login':'me'},'commit_id':self.head,**self.plan['comments'][0]}
        c.update(changes)
        self.comments.append(c)

    def test_action_is_part_of_review_identity(self):
        self.existing_review()
        self.plan['event']='REQUEST_CHANGES'
        code, _ = self.run_plan()
        self.assertEqual(code,0)
        self.assertEqual(self.writes,['reviews','comments'])
        self.assertEqual(self.reviews[-1]['state'],'CHANGES_REQUESTED')

    def test_comment_identity_uses_full_body_revision_side_and_range(self):
        self.existing_review()
        for index, changes in enumerate(({'body':'x'*180+' second'}, {'commit_id':'b'*40},
                        {'side':'LEFT'}, {'start_line':2,'start_side':'RIGHT'})):
            with self.subTest(changes=changes):
                self.path = Path(self.temp.name)/f"plan-{index}.json"
                self.comments=[]
                self.writes=[]
                self.existing_comment(**changes)
                code,_ = self.run_plan()
                self.assertEqual(code,0)
                self.assertEqual(self.writes,['comments'])

    def test_lost_review_response_reconciles_then_resumes(self):
        self.fail_after='reviews'
        code, report = self.run_plan()
        self.assertEqual(code,0,report)
        self.assertEqual(self.writes,['reviews','comments'])
        code,_ = self.run_plan()
        self.assertEqual(code,0)
        self.assertEqual(len(self.writes),2)
        self.assertTrue(self.path.with_suffix('.journal.json').is_file())

    def test_lost_comment_response_is_verified_without_duplicate(self):
        self.fail_after='comments'
        code,report = self.run_plan()
        self.assertEqual(code,0,report)
        self.assertEqual(len(self.comments),1)
        self.assertEqual(self.run_plan()[0],0)
        self.assertEqual(len(self.comments),1)

    def test_unresolved_ambiguous_write_stops_and_persists_evidence(self):
        self.fail_after='reviews'
        self.fail_reads=True
        code,report = self.run_plan()
        self.assertEqual(code,1)
        self.assertIsNotNone(report['stopped'])
        self.assertEqual(self.writes,['reviews'])
        journal=json.loads(self.path.with_suffix('.journal.json').read_text())
        self.assertIn('ambiguous',str(journal))
        self.fail_reads=False
        self.assertEqual(self.run_plan()[0],0)
        self.assertEqual(self.writes,['reviews','comments'])

    def test_same_prefix_comments_in_plan_are_both_posted(self):
        second={**self.plan['comments'][0],'body':'x'*180+' second'}
        self.plan['comments'].append(second)
        self.assertEqual(self.run_plan()[0],0)
        self.assertEqual(len(self.comments),2)
        self.assertEqual(self.run_plan()[0],0)
        self.assertEqual(len(self.comments),2)

    def test_dry_run_shows_exact_content_and_creates_no_journal(self):
        code,report=self.run_plan(False)
        self.assertEqual(code,0)
        self.assertEqual(self.writes,[])
        self.assertEqual(report['plan']['comments'],self.plan['comments'])
        self.assertFalse(self.path.with_suffix('.journal.json').exists())

    def test_absent_response_does_not_retry_in_run_and_caps_resume(self):
        self.reject_write='response lost before acceptance'
        self.assertEqual(self.run_plan()[0],1)
        self.assertEqual(len(self.writes),1)
        self.assertEqual(self.run_plan()[0],1)
        self.assertEqual(len(self.writes),2)
        self.assertEqual(self.run_plan()[0],1)
        self.assertEqual(len(self.writes),2)

    def test_permanent_failure_is_not_retried_on_resume(self):
        self.reject_write='HTTP 422 invalid anchor'
        self.assertEqual(self.run_plan()[0],1)
        self.assertEqual(self.run_plan()[0],1)
        self.assertEqual(len(self.writes),1)

    def test_changed_plan_is_rejected_by_existing_journal(self):
        self.assertEqual(self.run_plan()[0],0)
        self.plan['comments'][0]['body']='different authorized content'
        code,report=self.run_plan()
        self.assertEqual(code,1)
        self.assertIn('another plan',report['stopped'])
        self.assertEqual(len(self.writes),2)

    def test_corrupted_remote_body_does_not_count_as_verified(self):
        original=self.gh
        def changing_gh(*args,payload=None):
            value=original(*args,payload=payload)
            if payload and args[-1].endswith('/comments'):
                self.comments[-1]['body']='different body'
            return value
        with patch.object(self,'gh',changing_gh):
            code,report=self.run_plan()
        self.assertEqual(code,1)
        self.assertIsNotNone(report['stopped'])


if __name__=='__main__':
    unittest.main(verbosity=2)
