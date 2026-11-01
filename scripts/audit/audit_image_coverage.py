#!/usr/bin/env python3
"""影像覆蓋缺口盤點：原書有圖的書頁，站台是否完全沒有顯示。

背景
----
`static/images/<chapter>/page-NNN.png` 是原書的**整頁掃描**，
檔名編號 = 書頁碼 + 9（已像素級驗證）。

站台每個含圖段落掛一張整頁圖。若原書某頁有圖、但站台從未掛出該頁，
代表該頁的內容在網站上**沒有視覺佐證** —— 這是「內容缺口」而非「錯置」。

同時反向檢查：站台掛了某頁，但原書該頁沒有任何圖 → 該圖並非來自原書該頁。

輸出
----
  docs/audit/image_coverage_gaps.csv

人工覆核
--------
`captions.json` 由文字層抽取，可能把條列、表格或參考文獻誤判成圖說。
逐頁視覺確認為「無圖」的頁面記錄在：

  docs/audit/verified_no_figure_pages.csv

這些頁面會從缺口清單排除，但仍會在終端摘要顯示排除數量。
"""
import re
import os
import csv
import json
import sys
from collections import Counter

SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
IMG_OFFSET = 9

CHAPTERS = ['thoracic', 'gi', 'genitourinary', 'neuro', 'msk', 'ultrasound',
            'nuclear', 'breast', 'cardiovascular', 'interventional',
            'pediatric', 'physics']

VERIFIED_NO_FIGURE_CSV = f'{SITE}/docs/audit/verified_no_figure_pages.csv'


def site_used_pages(ch):
    path = f'{SITE}/content/docs/{ch}/_index.md'
    t = open(path, encoding='utf-8').read()
    return Counter(int(m.group(1)) - IMG_OFFSET
                   for m in re.finditer(r'!\[[^\]]*\]\([^)]*page-(\d+)\.png\)', t))


def book_fig_pages(ch):
    caps = json.load(open(f'{SRC}/captions.json', encoding='utf-8')).get(ch, {})
    out = {}
    for p, v in caps.items():
        n = v.get('n_figures') or 0
        if n > 0:
            out[int(p)] = {
                'heading': v.get('heading') or '',
                'n_fig': n,
                'captions': ' | '.join((c.get('title') or '')
                                       for c in (v.get('captions') or [])),
            }
    return out


def verified_no_figure_pages():
    """回傳人工視覺確認沒有 figure 的 {(chapter, book_page), ...}。"""
    if not os.path.exists(VERIFIED_NO_FIGURE_CSV):
        return set()
    out = set()
    with open(VERIFIED_NO_FIGURE_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if (row.get('verification') or '').strip().upper() != 'NO_FIGURE':
                continue
            out.add((row['chapter'].strip(), int(row['book_page'])))
    return out


def main():
    allgaps = []
    excluded = verified_no_figure_pages()
    excluded_count = 0
    print(f'{"章節":16s} {"書頁":>5s} {"站台用":>7s} {"有圖頁":>7s} {"缺圖頁":>7s} {"多餘頁":>7s}')
    print('-' * 62)
    for ch in CHAPTERS:
        used = site_used_pages(ch)
        figp = book_fig_pages(ch)
        raw_missing = sorted(p for p in figp if used[p] == 0)
        missing = [p for p in raw_missing if (ch, p) not in excluded]
        excluded_count += len(raw_missing) - len(missing)
        extra = sorted(p for p in used if figp.get(p, {}).get('n_fig', 0) == 0)
        print(f'{ch:16s} {len(used):>5d} {len(used):>7d} {len(figp):>7d} '
              f'{len(missing):>7d} {len(extra):>7d}')
        for p in missing:
            d = figp[p]
            allgaps.append({
                'chapter': ch,
                'book_page': p,
                'image_file': f'page-{p + IMG_OFFSET:03d}.png',
                'n_figures': d['n_fig'],
                'book_heading': d['heading'],
                'caption_titles': d['captions'][:150],
                'site_has_no_image_for_this_page': 'YES',
            })
    print('-' * 62)
    print(f'合計缺口書頁：{len(allgaps)}')
    print(f'人工覆核排除（無圖頁）：{excluded_count}')
    out = f'{SITE}/docs/audit/image_coverage_gaps.csv'
    fieldnames = [
        'chapter', 'book_page', 'image_file', 'n_figures', 'book_heading',
        'caption_titles', 'site_has_no_image_for_this_page',
    ]
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
        w.writeheader()
        w.writerows(allgaps)
    print(f'wrote {out}')
    print()
    for g in allgaps:
        print(f"{g['chapter']:14s} p{g['book_page']:>3} ({g['image_file']}) "
              f"nfig={g['n_figures']}  {g['book_heading'][:46]}")


if __name__ == '__main__':
    main()
