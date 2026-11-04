"""Parse old/new changed lines, retaining the correct paths across renames."""
import re
import json


def decode_path(text):
    if text.startswith('"'):
        # Untracked name-status entries are JSON strings; most Git C strings are
        # also valid JSON. Git's octal/vertical-tab escapes need the byte parser.
        try:
            return json.loads(text)
        except ValueError:
            pass
        data = text[1:-1].encode('utf-8', 'surrogateescape')
        escapes = {ord(k): bytes([v]) for k,v in
                   {'a':7,'b':8,'t':9,'n':10,'v':11,'f':12,'r':13,'"':34,'\\':92}.items()}
        def unescape(match):
            value = match.group(1)
            return bytes([int(value,8)]) if value[:1] in b'01234567' else escapes[value[0]]
        text = re.sub(rb'\\([0-7]{1,3}|.)',unescape,data).decode('utf-8','surrogateescape')
    return text


def parse_path(text):
    text = decode_path(text.split('\t',1)[0])
    if text == '/dev/null': return None
    return re.sub(r'^[ab]/','',text)


def changed_lines(diff_path):
    changed = {}
    old_path = new_path = None
    old_line = new_line = 0
    in_hunk = False
    for raw in diff_path.read_text(errors='replace').splitlines():
        if raw.startswith('diff --git '): in_hunk=False
        elif not in_hunk and raw.startswith('--- '): old_path=parse_path(raw[4:])
        elif not in_hunk and raw.startswith('+++ '): new_path=parse_path(raw[4:])
        elif raw.startswith('@@ '):
            m = re.match(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@',raw)
            if not m: continue
            old_line,new_line=map(int,m.groups()); in_hunk=True
        elif in_hunk:
            if raw.startswith('+'):
                if new_path: changed.setdefault(('RIGHT',new_path),set()).add(new_line)
                new_line+=1
            elif raw.startswith('-'):
                if old_path: changed.setdefault(('LEFT',old_path),set()).add(old_line)
                old_line+=1
            elif raw.startswith(' '): old_line+=1; new_line+=1
    return changed


