#!/usr/bin/env python3
"""
Rebuild data/index.json by scanning the worksheet JSON files on disk.

Run from the repo root:    python3 tools/rebuild_index.py

Use this after adding, removing, or renumbering worksheets. Set-level
descriptions live in data/sets.json so they survive a rebuild; any set folder
missing from that file gets a placeholder you can edit afterwards.
"""

import json
import os
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
LETTERS = ['A', 'B', 'C', 'D']


def answer_key(doc):
    out = ''
    for q in doc['questions']:
        out += LETTERS[q['order'].index('c')]
    return out


def main():
    meta_path = os.path.join(DATA, 'sets.json')
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    order = meta.get('order', [])
    info = meta.get('sets', {})

    folders = sorted(
        d for d in os.listdir(DATA)
        if os.path.isdir(os.path.join(DATA, d)) and not d.startswith('_')
    )

    # honour the explicit ordering in sets.json, then anything new, alphabetically
    ordered = [f for f in order if f in folders] + [f for f in folders if f not in order]

    manifest = {'sets': []}
    total = 0

    for set_id in ordered:
        folder = os.path.join(DATA, set_id)
        files = sorted(
            f for f in os.listdir(folder)
            if f.endswith('.json') and not f.startswith('_')
        )
        if not files:
            continue

        entries = []
        for name in files:
            path = os.path.join(folder, name)
            try:
                doc = json.load(open(path))
            except json.JSONDecodeError as e:
                print('SKIPPED %s/%s — invalid JSON: %s' % (set_id, name, e))
                continue

            entries.append({
                'id': doc['id'],
                'number': doc['number'],
                'topic': doc['topic'],
                'title': doc['title'],
                'file': 'data/%s/%s' % (set_id, name),
                'answerKey': answer_key(doc),
            })

        entries.sort(key=lambda e: e['number'])

        si = info.get(set_id, {})
        first = json.load(open(os.path.join(folder, files[0])))

        manifest['sets'].append({
            'id': set_id,
            'title': si.get('title', first.get('setTitle', set_id)),
            'description': si.get('description', 'TODO: add a description in data/sets.json'),
            'readingLevel': si.get('readingLevel', first.get('readingLevel', 'Standard (grades 6-8)')),
            'tiered': si.get('tiered', bool(first.get('tiered', False))),
            'count': len(entries),
            'worksheets': entries,
        })
        total += len(entries)

    manifest['generated'] = datetime.date.today().isoformat()
    manifest['totalSets'] = len(manifest['sets'])
    manifest['totalWorksheets'] = total

    with open(os.path.join(DATA, 'index.json'), 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print('Rebuilt data/index.json — %d worksheets across %d sets.'
          % (total, len(manifest['sets'])))
    for s in manifest['sets']:
        flag = '  <-- needs a description in data/sets.json' if s['description'].startswith('TODO') else ''
        print('  %-18s %2d worksheets%s' % (s['id'], s['count'], flag))
    return 0


if __name__ == '__main__':
    sys.exit(main())
