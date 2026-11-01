#!/usr/bin/env python3
"""套用 image_reassignment.csv 的影像重指派建議。

只改三樣東西（都不碰醫學文字）：
  1. 影像檔名 `page-NNN.png` -> `page-MMM.png`
  2. alt 文字 `![Page NNN]` -> `![Page MMM]`
  3. 章節標題的 `Page NNN` 前綴（若該標題的數字等於舊檔名編號）

安全設計
--------
- 逐行校驗：目標行必須是預期的 image markdown，且檔名等於 CSV 的
  `current_image`，否則跳過並記錄。
- 目標檔必須實際存在於 static/images/<chapter>/，否則跳過。
- 產生 unified diff 備份，可用 git checkout 還原。
- 支援 --dry-run。

用法
----
  python3 scripts/audit/apply_reassign.py --dry-run
  python3 scripts/audit/apply_reassign.py
"""
import re
import os
import csv
import sys
import argparse
import difflib
from collections import defaultdict

SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
CSV_PATH = f'{SITE}/docs/audit/image_reassignment.csv'
DIFF_PATH = f'{SITE}/docs/audit/applied_reassignment.diff'

IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)]*?page-(\d+)\.png)\)')
ALT_NUM_RE = re.compile(r'(?<=Page )(\d+)')
HEAD_LABEL_RE = re.compile(r'(###\s+Page )(\d+)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--only', default='', help='只套用指定章節（逗號分隔）')
    args = ap.parse_args()

    only = {c.strip() for c in args.only.split(',') if c.strip()}

    rows = [r for r in csv.DictReader(open(CSV_PATH, encoding='utf-8'))
            if r['status'] == 'REASSIGN']
    if only:
        rows = [r for r in rows if r['chapter'] in only]

    by_file = defaultdict(list)
    for r in rows:
        by_file[r['chapter']].append(r)

    applied, skipped, diffs = [], [], []
    for ch in sorted(by_file):
        path = f'{SITE}/content/docs/{ch}/_index.md'
        lines = open(path, encoding='utf-8').read().split('\n')

        for r in sorted(by_file[ch], key=lambda x: int(x['source_line'])):
            idx = int(r['source_line']) - 1
            if idx < 0 or idx >= len(lines):
                skipped.append((ch, r['source_line'], 'line out of range'))
                continue
            old_line = lines[idx]
            old_file = r['current_image']
            new_file = r['suggested_image']

            m = IMG_RE.search(old_line)
            if not m:
                skipped.append((ch, r['source_line'], 'no image markdown'))
                continue
            if f'page-{m.group(3)}.png' != old_file:
                skipped.append((ch, r['source_line'],
                                f'file mismatch: line={m.group(3)}.png csv={old_file}'))
                continue

            target = f'{SITE}/static/images/{ch}/{new_file}'
            if not os.path.exists(target):
                skipped.append((ch, r['source_line'], f'target image missing: {new_file}'))
                continue

            new_line = old_line.replace(old_file, new_file)
            # alt 數字同步
            am = ALT_NUM_RE.search(m.group(1))
            if am:
                new_line = new_line.replace(m.group(1),
                                           m.group(1)[:am.start(1)] + new_file[5:8] +
                                           m.group(1)[am.end(1):], 1)

            # 章節標題的 Page NNN 前綴：僅當標題數字等於舊檔名編號時才更新
            hi = next((i for i in range(idx - 1, -1, -1)
                       if lines[i].startswith('### ')), None)
            if hi is not None:
                hm = HEAD_LABEL_RE.search(lines[hi])
                if hm and hm.group(2) == old_file[5:8]:
                    new_head = lines[hi][:hm.start(2)] + new_file[5:8] + lines[hi][hm.end(2):]
                    if new_head != lines[hi]:
                        diffs.extend(difflib.unified_diff(
                            [lines[hi]], [new_head], fromfile=f'a/{ch}',
                            tofile=f'b/{ch}', lineterm='', n=0))
                        lines[hi] = new_head

            if new_line != old_line:
                lines[idx] = new_line
                applied.append((ch, r['source_line'], old_file, new_file))
                diffs.extend(difflib.unified_diff(
                    [old_line], [new_line], fromfile=f'a/{ch}',
                    tofile=f'b/{ch}', lineterm='', n=0))

        if not args.dry_run:
            open(path, 'w', encoding='utf-8').write('\n'.join(lines))

    with open(DIFF_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(diffs) + ('\n' if diffs else ''))

    print(f'{"(dry-run) " if args.dry_run else ""}applied: {len(applied)}   '
          f'skipped: {len(skipped)}')
    for s in skipped:
        print('  skipped:', s)
    print(f'diff backup: {DIFF_PATH}')
    if applied:
        print('\n--- changes ---')
        for a in applied:
            print(f'  {a[0]:14s} L{a[1]:>5}  {a[2]} -> {a[3]}')


if __name__ == '__main__':
    main()
