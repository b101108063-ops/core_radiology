#!/usr/bin/env python3
"""Task 3 — 非原書來源（Learning Radiology 等）全站盤點與 A/B/C/D 分類。

原則：
  * 暫時保留全部內容，只做盤點與分類。
  * 不刪除、不改寫。
  * 分類需有可追溯的證據欄位。
  * 「原書未提及」不等於「錯誤」—— C 類僅表示需臨床覆核。
"""
import re, json, os, csv, sys

SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')

# 非 Core Radiology 的來源標註樣式
ATTRIB = re.compile(
    r'\*\*Source:\s*Learning Radiology[^*]*\*\*|'
    r'\*\*Source:\s*(?!Core Radiology)[^*]{3,120}\*\*|'
    r'Learning Radiology[,\s]*Chapter\s*\d+', re.I)

# 常見的非原書來源關鍵字
OTHER_SOURCE = re.compile(
    r'Learning Radiology|William Herring|Radiopaedia(?!\s*is)|'
    r'St\. ?John ?Radiology|RadPrimer|e-Anatomy|StatPearls|'
    r'Radiology Assistant|UpToDate|AMBOSS', re.I)


def section_of(lines, idx):
    """回傳該行所屬的最近標題（H2 / H3）"""
    h2 = h3 = ''
    for i in range(idx, -1, -1):
        l = lines[i]
        if h3 == '' and l.startswith('### '):
            h3 = l[4:].strip()
        elif h2 == '' and l.startswith('## '):
            h2 = l[3:].strip()
        if h2 and h3:
            break
    return h2, h3


def main():
    chapters = sys.argv[1:] or ['thoracic', 'gi', 'genitourinary', 'neuro', 'msk',
                                 'ultrasound', 'nuclear', 'breast', 'cardiovascular',
                                 'interventional', 'pediatric', 'physics']
    rows = []
    for ch in chapters:
        path = f'{SITE}/content/docs/{ch}/_index.md'
        if not os.path.exists(path):
            continue
        lines = open(path, encoding='utf-8').read().split('\n')
        # 找出所有明確出處標註
        for i, l in enumerate(lines):
            if ATTRIB.search(l):
                h2, h3 = section_of(lines, i)
                src = re.sub(r'\*+', '', ATTRIB.search(l).group(0)).strip()
                rows.append({
                    'chapter': ch,
                    'kind': 'explicit_attribution',
                    'source_file': f'content/docs/{ch}/_index.md',
                    'source_line': i + 1,
                    'section_h2': h2[:80],
                    'section_h3': h3[:80],
                    'attribution': src[:160],
                    'classification': '',
                    'rationale': '',
                })
        # 找出非原書來源的關鍵字（但沒有明確出處標註）
        for i, l in enumerate(lines):
            if ATTRIB.search(l):
                continue
            if OTHER_SOURCE.search(l):
                h2, h3 = section_of(lines, i)
                rows.append({
                    'chapter': ch,
                    'kind': 'other_source_keyword',
                    'source_file': f'content/docs/{ch}/_index.md',
                    'source_line': i + 1,
                    'section_h2': h2[:80],
                    'section_h3': h3[:80],
                    'attribution': l.strip()[:160],
                    'classification': '',
                    'rationale': '',
                })

    out = f'{SITE}/docs/audit/other_sources.csv'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cols = ['chapter', 'kind', 'source_file', 'source_line', 'section_h2',
            'section_h3', 'attribution', 'classification', 'rationale']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    c = Counter(r['chapter'] for r in rows)
    print(f'{len(rows)} hits')
    for k, v in sorted(c.items()):
        print(f'  {k:16s} {v}')
    print(f'\nwrote {out}')


if __name__ == '__main__':
    main()
