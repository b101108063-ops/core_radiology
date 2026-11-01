#!/usr/bin/env python3
"""以「頁首標題包含」判定影像錯位，並輸出**分段偏移表**。

改進（相對上一版）
------------------
1. 候選頁比對**只用頁首標題**（heading），不再混入圖說標題。
   圖說裡常出現大量相鄰頁都會提到的詞，會讓包含規則過鬆 ——
   上一版因此把 msk 的 9 個連續區塊（「Monteggia fracture-dislocation」
   等）全部誤配到同一頁，產生明顯的假陽性。
2. 只用**內容詞**比對（濾掉 imaging / diagnosis / overview 等泛用詞）。
3. 產出**每個區段的偏移量**統計：錯位若是機械式 bug，
   同一段落的偏移應該是常數（例如整段都是 +9）。

判定
----
  S = 區塊英文標題的內容詞集
  候選頁 P = 滿足 S ⊆ heading(P) 的頁（heading 為頁首標題）
  唯一候選 -> 該區塊的「來源書頁」
  實際書頁 = 影像檔名 - 9
  偏移 = 實際書頁 - 來源書頁

輸出
----
  docs/audit/image_segment_offsets.csv   逐區塊
  docs/audit/image_segment_summary.csv  分段偏移統計
"""
import re, json, os, csv, sys
from collections import Counter, defaultdict

SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
AUD = f'{SITE}/docs/audit'
IMG_OFFSET = 9

STOP = set('''the a an and or of to in is are be on for with that this these those by as at from
which when while can may also not no its their there here been being more most other than then
they them we you he she his her our your if but so such into over under between during
image images figure fig table see shown shows show used using use including include includes
e.g i.e vs versus per each any all less only both same different new old note notes'''.split())

GENERIC = set('''imaging diagnosis differential management treatment clinical overview
introduction patterns approach features types basic basics definition radiographic radiologic
computed plain sonographic nuclear pediatric general summary key point points disease
diseases imaging findings review concept'''.split())

NOT_SOURCE = re.compile(r'^(contents|references?\b.*|index$|chapter contents)', re.I)


def words(s):
    s = re.sub(r'[^a-z0-9\s]', ' ', (s or '').lower())
    return {w for w in s.split() if len(w) > 2 and w not in STOP and w not in GENERIC}


def en_title(sec):
    m = re.findall(r'\(([^)]*)\)', sec)
    if m:
        return m[-1].strip()
    parts = [p.strip() for p in sec.split('/')]
    return parts[-1] if parts else ''


def site_blocks(chapter):
    path = f'{SITE}/content/docs/{chapter}/_index.md'
    if not os.path.exists(path):
        return []
    lines = open(path, encoding='utf-8').read().split('\n')
    blocks, cur = [], None
    for i, ln in enumerate(lines, 1):
        m2 = re.match(r'^##\s+(.*)', ln)
        m3 = re.match(r'^###\s+(.*)', ln)
        if m2 or m3:
            if cur:
                blocks.append(cur)
            cur = {'h2': '', 'h3': '', 'imgs': [], 'text': [], 'line': i}
            if m2:
                cur['h2'] = m2.group(1).strip(); cur['h3'] = ''
            else:
                cur['h3'] = m3.group(1).strip()
            continue
        mi = re.search(r'!\[([^\]]*)\]\(([^)]*page-(\d+)\.png)\)', ln)
        if cur is None and mi:
            cur = {'h2': '(章節前言)', 'h3': '', 'imgs': [], 'text': [], 'line': i}
        if cur is None:
            continue
        if mi:
            cur['imgs'].append({'file': int(mi.group(3)), 'alt': mi.group(1),
                                 'line': i, 'url': mi.group(2)})
        s = ln.strip()
        if not s or s.startswith(('|', '>', '#')):
            continue
        cur['text'].append(s)
    if cur:
        blocks.append(cur)
    return blocks


def main():
    chapters = sys.argv[1:] or ['thoracic', 'gi', 'genitourinary', 'neuro', 'msk',
                                 'ultrasound', 'nuclear', 'breast', 'cardiovascular',
                                 'interventional', 'pediatric', 'physics']
    with open(f'{SRC}/captions.json', encoding='utf-8') as f:
        captions = json.load(f)

    rows = []
    for ch in chapters:
        blocks = site_blocks(ch)
        # heading(P) 的內容詞集；排除目次 / 參考文獻頁
        hset = {}
        for p, v in captions.get(ch, {}).items():
            head = (v.get('heading') or '').strip()
            if NOT_SOURCE.match(head):
                continue
            hset[int(p)] = words(head)
        # 反向索引：詞 -> 頁
        idx = defaultdict(set)
        for p, W in hset.items():
            for w in W:
                idx[w].add(p)

        for b in blocks:
            if not b['imgs']:
                continue
            sec = b['h3'] or b['h2']
            S = words(en_title(sec))
            if not S:
                continue
            # 候選頁 = 同時含所有詞的頁
            cand = None
            for w in S:
                pages_w = idx.get(w, set())
                cand = set(pages_w) if cand is None else (cand & pages_w)
                if not cand:
                    break
            cand = sorted(cand or [])

            for img in b['imgs']:
                cur_bp = img['file'] - IMG_OFFSET
                if len(cand) == 1:
                    src_bp = cand[0]
                    offset = cur_bp - src_bp
                    status = 'MATCHED'
                elif len(cand) > 1:
                    src_bp, offset = '', ''
                    status = 'AMBIGUOUS'
                else:
                    src_bp, offset = '', ''
                    status = 'NO_MATCH'
                rows.append({
                    'chapter': ch,
                    'status': status,
                    'source_file': f'content/docs/{ch}/_index.md',
                    'source_line': img['line'],
                    'section': sec[:110],
                    'current_image': f'page-{img["file"]:03d}.png',
                    'current_book_page': cur_bp,
                    'source_book_page': src_bp,
                    'offset': offset,
                    'current_page_heading': (captions.get(ch, {}).get(str(cur_bp), {})
                                            .get('heading', '') or '')[:60],
                    'source_page_heading': (captions.get(ch, {}).get(str(src_bp), {})
                                            .get('heading', '') or '')[:60] if src_bp != '' else '',
                    'candidate_count': len(cand),
                })

    os.makedirs(AUD, exist_ok=True)
    cols = list(rows[0].keys())
    with open(f'{AUD}/image_segment_offsets.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)

    # 分段偏移統計：把連續且偏移相同的區塊視為一段
    summary = []
    for ch in chapters:
        sub = sorted([r for r in rows if r['chapter'] == ch],
                     key=lambda r: int(r['source_line']))
        matched = [r for r in sub if r['status'] == 'MATCHED']
        if not matched:
            continue
        seg = []
        for r in matched:
            off = int(r['offset'])
            if seg and off == seg[-1][0] and r['source_line'] - seg[-1][2] <= 30:
                seg[-1][1].append(r); seg[-1][2] = int(r['source_line'])
            else:
                seg.append([off, [r], int(r['source_line'])])
        for off, items, lastline in seg:
            summary.append({
                'chapter': ch,
                'offset': off,
                'count': len(items),
                'first_line': items[0]['source_line'],
                'last_line': lastline,
                'first_book_page': items[0]['current_book_page'],
                'last_book_page': items[-1]['current_book_page'],
                'sample_section': items[0]['section'][:70],
                'correct_file': items[0]['current_image'],
                'proposed_file': f"page-{int(items[0]['source_book_page']) + IMG_OFFSET:03d}.png",
            })

    scols = list(summary[0].keys())
    with open(f'{AUD}/image_segment_summary.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=scols)
        w.writeheader(); w.writerows(summary)

    print('status:', dict(Counter(r['status'] for r in rows)))
    print()
    print(f"{'chapter':16s} {'matched':>7s} {'offset=0':>8s} {'nonzero':>8s}  分布")
    for ch in chapters:
        sub = [r for r in rows if r['chapter'] == ch]
        m = [r for r in sub if r['status'] == 'MATCHED']
        if not m:
            continue
        off = Counter(int(r['offset']) for r in m)
        nz = sum(v for k, v in off.items() if k != 0)
        print(f"{ch:16s} {len(m):7d} {off[0]:8d} {nz:8d}  {dict(off.most_common(6))}")
    print()
    print('--- 非零偏移分段（>=2 個連續區塊）---')
    for s in summary:
        if s['offset'] != 0 and s['count'] >= 2:
            print(f"{s['chapter']:16s} off={s['offset']:+4d} n={s['count']:3d} "
                  f"L{s['first_line']}-{s['last_line']} book {s['first_book_page']}-{s['last_book_page']} "
                  f"| {s['sample_section'][:45]}")


if __name__ == '__main__':
    main()
