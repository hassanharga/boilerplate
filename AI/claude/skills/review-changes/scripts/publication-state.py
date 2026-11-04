"""Exact artifact identities and a local recovery journal; no service calls."""
import hashlib
import json
import os
from pathlib import Path


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def comment_payload(comment, commit):
    payload = {key: comment[key] for key in ('path', 'line', 'body')}
    payload.update(commit_id=commit, side=comment.get('side', 'RIGHT'))
    if comment.get('start_line') is not None:
        payload.update(start_line=comment['start_line'], start_side=comment.get('start_side', payload['side']))
    return payload


def matches_comment(got, wanted, actor):
    return (got.get('user', {}).get('login') == actor
            and got.get('commit_id') == wanted['commit_id']
            and got.get('path') == wanted['path'] and got.get('body') == wanted['body']
            and got.get('side') == wanted['side']
            and (got.get('line') or got.get('original_line')) == wanted['line']
            and (got.get('start_line') or got.get('original_start_line')) == wanted.get('start_line')
            and got.get('start_side') == wanted.get('start_side'))


def matches_review(got, wanted, actor):
    return (got.get('user', {}).get('login') == actor
            and got.get('commit_id') == wanted['commit_id'] and got.get('body') == wanted['body']
            and got.get('state') == ('COMMENTED' if wanted['event'] == 'COMMENT' else 'CHANGES_REQUESTED'))


class Journal:
    def __init__(self, path, plan, actor):
        self.path = Path(path)
        self.key = identity({'plan': plan, 'actor': actor})
        self.data = {'plan_id': self.key, 'actor': actor, 'operations': {}}
        self.lock = self.path.with_name(self.path.name + '.lock')
        self.fd = None

    def __enter__(self):
        self.fd = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            if self.path.exists():
                self.data = json.loads(self.path.read_text())
                if self.data.get('plan_id') != self.key:
                    raise ValueError('journal belongs to another plan or actor; use a separate --journal path')
            self.save()
        except Exception:
            self.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, *_):
        if self.fd is not None:
            os.close(self.fd)
            self.lock.unlink()
            self.fd = None

    def save(self):
        temp = self.path.with_name(self.path.name + '.tmp')
        with open(temp, 'w', encoding='utf-8') as handle:
            json.dump(self.data, handle, indent=2)
            handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp, self.path)

    def operation(self, kind, payload):
        key = identity({'kind': kind, 'payload': payload})
        return self.data['operations'].setdefault(key, {'kind': kind, 'payload': payload,
                                                       'attempts': 0, 'status': 'pending'})

    def record(self, op, status, **details):
        op.update(status=status, **details)
        self.save()
