#!/usr/bin/env python3
"""Fix cardiovascular sub-items: demote 疾病名稱/臨床特點/診斷要點/鑑別診斷/etc to H3 under each disease H2."""

import re
import sys

# Sub-item patterns that should be H3 (under each disease H2)
SUB_ITEM_PATTERNS = [
    '疾病名稱',
    'Disease Name',
    '臨床特點',
    'Clinical Features',
    '臨床特徵',
    'Clinical Features',
    '診斷要點',
    'Diagnostic Key Points',
    '鑑別診斷',
    'Differential Diagnosis',
    '治療',
    'Treatment',
    '治療原則',
    'Treatment Principles',
    '病理特點',
    'Pathologic Features',
    '病理學',
    'Pathology',
    '病理機制',
    'Pathophysiology',
    '病因學',
    'Etiology',
    '概述',
    'Overview',
    '總覽',
    'Chapter Overview',
    '學習目標',
    'Learning Objectives',
    '鑑別診斷要點',
    'Differential Diagnosis Key Points',
    '適應症',
    'Indications',
    '技術要點',
    'Technical Points',
    '預後',
    'Prognosis',
    '術後處置',
    'Post-Procedure',
    '併發症',
    'Complications',
    '重要提醒',
    'Important Note',
    '囊腫液評估',
    'Cyst Aspirate Evaluation',
    '品質控制',
    'Quality Control',
    '不一致發現範例',
    'Discordant Finding Example',
    '核心原則',
    'Core Principle',
    '臨床注意',
    'Clinical Note',
    '疾病概述',
    'Disease Overview',
    'MRI 對比劑使用原則',
]

SUB_ITEM_RE = re.compile(r'^## (' + '|'.join(re.escape(p) for p in SUB_ITEM_PATTERNS) + r')\s*(?:/.*)?$')

def is_sub_item(s):
    return bool(SUB_ITEM_RE.search(s))

def count_hash(s):
    n = 0
    for c in s.lstrip():
        if c == '#': n += 1
        else: break
    return n

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        lvl = count_hash(s) if s.startswith('#') else 0

        if lvl == 2 and is_sub_item(s):
            # Demote H2 sub-item to H3
            newline = re.sub(r'^## ', '### ', line, 1)
            result.append(newline)
        else:
            result.append(line)
        i += 1

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(result)
    print(f"Processed: {path}")

if __name__ == '__main__':
    for p in sys.argv[1:]:
        process_file(p)
