#!/usr/bin/env python3
"""為缺圖書頁插入影像引用。

插入規則（保守）
----------------
只有同時滿足下列條件才自動插入：
  1. 目標區段**目前沒有任何影像** —— 純新增，不動到既有引用
  2. 標題 F1 >= 0.5（區段標題與書頁標題／圖說標題有實質重疊）

其餘情形（區段已有圖、或標題對不上）標為 MANUAL，輸出到 CSV 供人工判定，
因為那代表「該替換」或「需找別的段落」，不能自動決定。

插入位置
--------
插在區塊標題行之後（該區塊第一段內文之前），格式與既有一致：

    ![Page NNN](/core_radiology/images/<chapter>/page-NNN.png)

其中 NNN 是檔名編號（書頁 + 9），與站台既有 alt 慣例相同。

輸出
----
  docs/audit/missing_image_insertions.csv
  docs/audit/applied_missing_images.diff
"""
import re
import os
import csv
import sys
import difflib
import argparse

SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
CSV_PATH = f'{SITE}/docs/audit/missing_image_insertions.csv'
DIFF_PATH = f'{SITE}/docs/audit/applied_missing_images.diff'

MIN_TITLE_F1 = 0.50


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true',
                    help='report planned insertions without modifying files')
    args = ap.parse_args()
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
    applied, manual = [], []

    by_ch = {}
    for r in rows:
        by_ch.setdefault(r['chapter'], []).append(r)

    for ch, items in sorted(by_ch.items()):
        path = f'{SITE}/content/docs/{ch}/_index.md'
        lines = open(path, encoding='utf-8').read().split('\n')
        # 由後往前插入，避免行號位移
        for r in sorted(items, key=lambda x: int(x['target_line']), reverse=True):
            ln = int(r['target_line'])
            f1 = float(r['title_f1'])
            img = r['image_file']
            num = img[len('page-'):-len('.png')]

            # 找區塊範圍（到下一個 h2/h3 或檔案結尾）
            end = len(lines)
            for j in range(ln, len(lines)):
                if j > ln and re.match(r'^#{2,3}\s', lines[j]):
                    end = j
                    break
            has_img = any(re.search(r'!\[[^\]]*\]\([^)]*page-\d+\.png\)', lines[j])
                          for j in range(ln, end))

            if has_img or f1 < MIN_TITLE_F1:
                manual.append({**r, 'reason': 'section already has an image'
                               if has_img else f'title F1 {f1} < {MIN_TITLE_F1}'})
                continue

            new_line = f'![Page {num}](/core_radiology/images/{ch}/{img})'
            lines.insert(ln, new_line)
            applied.append({**r, 'inserted_at': ln + 1, 'image_line': new_line})

        if not args.dry_run:
            open(path, 'w', encoding='utf-8').write('\n'.join(lines))

    diffs = []
    for a in applied:
        diffs.append(f"+{a['image_line']}   "
                     f"({a['chapter']} book p{a['book_page']} "
                     f"-> {a['target_section'][:40]})")
    if not args.dry_run:
        with open(DIFF_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(diffs) + ('\n' if diffs else ''))

    print(f'{"(dry-run) " if args.dry_run else ""}inserted: {len(applied)}   '
          f'manual: {len(manual)}')
    if not args.dry_run:
        print(f'wrote {DIFF_PATH}')
    print()
    print('--- inserted ---')
    for a in applied:
        print(f"  {a['chapter']:12s} p{a['book_page']:>3} {a['image_file']} "
              f"-> L{a['inserted_at']:>5} | {a['target_section'][:44]}")
    print()
    print('--- manual ---')
    for m in manual:
        print(f"  {m['chapter']:12s} p{m['book_page']:>3} {m['image_file']} "
              f"F1={m['title_f1']:>5} | {m['book_heading'][:34]:34s} | "
              f"{m['reason']}")


if __name__ == '__main__':
    main()
