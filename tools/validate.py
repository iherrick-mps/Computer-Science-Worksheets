#!/usr/bin/env python3
"""
Validate every worksheet JSON file and the manifest.

Run from the repo root:      python3 tools/validate.py
Exits with status 1 if anything is wrong, so it can be used in CI.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LETTERS = ['A', 'B', 'C', 'D']

REQUIRED_FIELDS = ['id', 'set', 'setTitle', 'number', 'title', 'topic',
                   'directions', 'paragraph', 'questions']

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def render_choices(q):
    """Rebuild display order from correct + distractors + order."""
    out = []
    for tok in q['order']:
        if tok == 'c':
            out.append(q['correct'])
        elif tok.startswith('d'):
            out.append(q['distractors'][int(tok[1:])])
        else:
            raise ValueError('bad order token %r' % tok)
    return out


def check_worksheet(path, doc, manifest_entry=None):
    where = os.path.relpath(path, ROOT)

    for f in REQUIRED_FIELDS:
        if f not in doc:
            err('%s: missing field "%s"' % (where, f))
            return

    if not doc['paragraph'].strip():
        err('%s: empty paragraph' % where)
    if '\n' in doc['paragraph']:
        warn('%s: paragraph contains a line break (prints as one block anyway)' % where)

    words = len(doc['paragraph'].split())
    if words < 60:
        warn('%s: paragraph is short (%d words)' % (where, words))
    if words > 260:
        warn('%s: paragraph is long (%d words) and may not fit one page' % (where, words))

    qs = doc['questions']
    if len(qs) != 5:
        err('%s: has %d questions, expected 5' % (where, len(qs)))

    key = ''
    for i, q in enumerate(qs, 1):
        tag = '%s q%d' % (where, i)

        for f in ['text', 'correct', 'distractors', 'order']:
            if f not in q:
                err('%s: missing field "%s"' % (tag, f))
                return

        if len(q['distractors']) != 3:
            err('%s: has %d distractors, expected 3' % (tag, len(q['distractors'])))
            continue
        if len(q['order']) != 4:
            err('%s: order has %d entries, expected 4' % (tag, len(q['order'])))
            continue
        if sorted(q['order']) != ['c', 'd0', 'd1', 'd2']:
            err('%s: order must be a permutation of c, d0, d1, d2 (got %s)'
                % (tag, q['order']))
            continue

        choices = render_choices(q)
        if len(set(choices)) != 4:
            err('%s: duplicate answer choices' % tag)

        letter = LETTERS[q['order'].index('c')]
        key += letter

        if 'correctLetter' in q and q['correctLetter'] != letter:
            err('%s: correctLetter is "%s" but order puts the answer at "%s"'
                % (tag, q['correctLetter'], letter))

        if not q['text'].strip():
            err('%s: empty question text' % tag)
        for d in q['distractors']:
            if not str(d).strip():
                err('%s: empty distractor' % tag)

    if len(set(key)) == 1 and len(key) == 5:
        warn('%s: every answer is "%s" — vary the position of "c"' % (where, key[0]))

    if manifest_entry is not None:
        if manifest_entry.get('answerKey') != key:
            err('%s: manifest answerKey "%s" does not match file ("%s")'
                % (where, manifest_entry.get('answerKey'), key))
        if manifest_entry.get('id') != doc['id']:
            err('%s: manifest id "%s" != file id "%s"'
                % (where, manifest_entry.get('id'), doc['id']))

    return key


def main():
    manifest_path = os.path.join(ROOT, 'data', 'index.json')
    if not os.path.exists(manifest_path):
        print('FAIL: data/index.json not found')
        return 1

    manifest = json.load(open(manifest_path))
    seen_files = set()
    seen_ids = set()
    total = 0

    for s in manifest['sets']:
        if s['count'] != len(s['worksheets']):
            err('manifest set "%s": count %d != %d listed worksheets'
                % (s['id'], s['count'], len(s['worksheets'])))

        for entry in s['worksheets']:
            path = os.path.join(ROOT, entry['file'])
            seen_files.add(os.path.normpath(path))

            if entry['id'] in seen_ids:
                err('duplicate worksheet id "%s"' % entry['id'])
            seen_ids.add(entry['id'])

            if not os.path.exists(path):
                err('manifest points at missing file: %s' % entry['file'])
                continue

            try:
                doc = json.load(open(path))
            except json.JSONDecodeError as e:
                err('%s: invalid JSON — %s' % (entry['file'], e))
                continue

            if doc.get('set') != s['id']:
                err('%s: set is "%s" but it is listed under "%s"'
                    % (entry['file'], doc.get('set'), s['id']))

            check_worksheet(path, doc, entry)
            total += 1

    declared = manifest.get('totalWorksheets')
    if declared is not None and declared != total:
        err('manifest totalWorksheets is %s but %d were found' % (declared, total))

    # any JSON on disk that the manifest doesn't know about
    data_root = os.path.join(ROOT, 'data')
    config_files = {'index.json', 'sets.json'}
    for dirpath, _dirs, files in os.walk(data_root):
        # config and template files live at the data root, not inside a set folder
        if os.path.normpath(dirpath) == os.path.normpath(data_root):
            continue
        for name in files:
            if not name.endswith('.json') or name.startswith('_') or name in config_files:
                continue
            full = os.path.normpath(os.path.join(dirpath, name))
            if full not in seen_files:
                warn('%s exists on disk but is not listed in data/index.json'
                     % os.path.relpath(full, ROOT))

    print('Checked %d worksheets (%d questions).' % (total, total * 5))

    if warnings:
        print('\n%d warning(s):' % len(warnings))
        for w in warnings:
            print('  ! ' + w)

    if errors:
        print('\n%d error(s):' % len(errors))
        for e in errors:
            print('  x ' + e)
        print('\nFAIL')
        return 1

    print('\nAll good.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
