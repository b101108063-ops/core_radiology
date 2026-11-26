#!/usr/bin/env python3
"""套用「系統性偏移段」修正。

只處理**同一章內、同一偏移值出現 >= MIN_REPEAT 次**的連續區塊 ——
這是機械式 bug 的特徵（頁碼換算被重複套用或漏用），孤立的大偏移
多半是比對雜訊，一律不動。

修正內容
--------
1. 影像檔名 `page-NNN.png` -> `page-MMM.png`
2. alt 文字 `![Page NNN]` -> `![Page MMM]`
3. 若區塊標題本身帶 `Page NNN` 前綴（如 ultrasound 章），一併更新標籤
   —— 標籤若不同步，網站會顯示與影像不符的頁碼。

安全設計
--------
- 套用前逐行校驗：該行必須是預期的 image markdown，且檔名等於 CSV 記錄值。
- 只動檔名與頁碼標籤，不碰任何醫學文字內容。
- 輸出 unified diff 備份，可用 git checkout 還原。
"""
import re, os, csv, sys, difflib
from collections import Counter, defaultdict

SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
AUD = f'{SITE}/docs/audit'
CSV_PATH = f'{AUD}/image_segment_offsets.csv'
IMG_RE = re.compile(r'page-(\d+)\.png')
ALT_RE = re.compile(r'(!\[Page )(\d+)(\])')
LABEL_RE = re.compile(r'(###\s+Page )(\d+)')
MIN_REPEAT = 3


def main():
    rows = [r for r in csv.DictReader(open(CSV_PATH, encoding='utf-8'))
            if r['status'] == 'MATCHED' and int(r['offset']) != 0]

    # 只保留出現 >= MIN_REPEAT 次的 (chapter, offset)
    cnt = Counter((r['chapter'], int(r['offset'])) for r in rows)
    systematic = {k for k, v in cnt.items() if v >= MIN_REPEAT}
    if not systematic:
        print('no systematic offset segments found')
        return
    print('systematic (chapter, offset) segments:',
          {f'{c}:{o:+d}': cnt[(c, o)] for c, o in sorted(systematic)})

    targets = [r for r in rows if (r['chapter'], int(r['offset'])) in systematic]

    by_file = defaultdict(list)
    for r in targets:
        by_file[r['source_file']].append(r)

    applied, skipped = [], []
    diffs = []
    for rel, items in sorted(by_file.items()):
        path = f'{SITE}/{rel}'
        lines = open(path, encoding='utf-8').read().split('\n')
        for r in items:
            idx = int(r['source_line']) - 1
            old = lines[idx]
            want = r['current_image']
            m = IMG_RE.search(old)
            if not m:
                skipped.append((rel, r['source_line'], 'no image markdown'))
                continue
            if m.group(0) != want:
                skipped.append((rel, r['source_line'],
                                f'file mismatch: line={m.group(0)} csv={want}'))
                continue

            src_bp = int(r['source_book_page'])
            new_file = f'page-{src_bp + 9:03d}.png'
            new = old.replace(want, new_file)

            # alt 文字同步（用新檔名的數字）
            am = ALT_RE.search(new)
            if am:
                new = new[:am.start(2)] + new_file[5:8] + new[am.end(2):]

            # 章節標題的 Page NNN 標籤同步（往上找最近的 ### 標題行）
            hi = next((i for i in range(int(r['source_line']) - 2, -1, -1)
                       if lines[i].startswith('### ')), None)
            if hi is not None:
                old_head = lines[hi]
                lm = LABEL_RE.search(old_head)
                if lm:
                    new_head = old_head[:lm.start(2)] + new_file[5:8] + old_head[lm.end(2):]
                    lines[hi] = new_head
                    diffs.extend(difflib.unified_diff(
                        [old_head], [new_head], fromfile=f'a/{rel}', tofile=f'b/{rel}',
                        lineterm='', n=0))

            if new != old:
                lines[idx] = new
                applied.append(r)
                diffs.extend(difflib.unified_diff(
                    [old], [new], fromfile=f'a/{rel}', tofile=f'b/{rel}',
                    lineterm='', n=0))
        open(path, 'w', encoding='utf-8').write('\n'.join(lines))

    diff_path = f'{AUD}/applied_segment_offsets.diff'
    with open(diff_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(diffs) + ('\n' if diffs else ''))

    print(f'applied: {len(applied)}   skipped: {len(skipped)}')
    print(f'diff backup: {diff_path}')
    for s in skipped:
        print('  skipped:', s)


if __name__ == '__main__':
    main()
