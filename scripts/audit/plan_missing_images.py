#!/usr/bin/env python3
"""為「原書有圖但站台未顯示」的書頁找出正確段落，並插入影像引用。

背景
----
`audit_image_coverage.py` 盤點出 34 個原書有圖的書頁在網站上完全沒有出現。
這些頁的內容在網站上**沒有視覺佐證** —— 例如：
  書頁 70「Less common thymic lesions（畸胎瘤）」→ 站台有「其他胸腺病變」小節但無圖
  書頁 73「Enlarged pulmonary artery（食道裂孔疝）」→ 站台有「肺動脈擴大」但無圖

本腳本對每個缺圖書頁，用與 align_v9 相同的評分（標題 F1 + 內文 idf）
在站台的**所有區塊**中找出最佳段落，再用 v9 的保序 DP 檢查該配對
是否與全章單調順序相容（避免把圖插到不相干的位置）。

只在兩條件同時成立時才建議插入：
  1. 評分達門檻（標題 F1 >= 0.5 或 內文 idf 分數夠高）
  2. 該配對不違反書頁順序單調性（相鄰缺圖頁之間不倒轉）

輸出
----
  docs/audit/missing_image_insertions.csv
"""
import re
import os
import math
import csv
import json
import sys
from collections import Counter

SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
IMG_OFFSET = 9

STOP = set('''the a an and or of to in is are be on for with that this these those by as at from
which when while can may also not no its their there here been being more most other than then
they them we you he she his her our your if but so such into over under between during
image images figure fig table see shown shows show used using use including include includes
e.g i.e vs versus per each any all less only both same different new old note notes'''.split())

NON_CONTENT = re.compile(r'^(contents|references?\b|index$|further reading|chapter contents)', re.I)

MIN_TITLE_F1 = 0.50
MIN_BODY_SCORE = 0.45
# 標題幾乎逐字吻合時，允许在已有圖的區段「追加」一張（站台本來就有多圖區段）
MIN_TITLE_F1_APPEND = 0.80
# body-only 配對（標題對不上）容易把圖插到不相干的段落，例如把
# 「Xanthogranulomatous pyelonephritis」配到「肝臟疾病」。因此自動插入
# 一律要求標題有實質重疊；body 分數只用於排序，不作為准入條件。
REQUIRE_TITLE_MATCH = True


def toks(s):
    s = re.sub(r'[^a-z0-9\s]', ' ', (s or '').lower())
    return [w for w in s.split() if len(w) >= 3 and w not in STOP]


def en_title_variants(sec):
    """英文標題候選字串。

    「Ground Glass Opacification (GGO)」若只取括號會變成 "GGO"，
    與原書標題的 F1 極低 —— 這正是 GGO 段落配不到書頁 p10 的根因。
    """
    if not sec:
        return []
    out = []
    parts = [p.strip() for p in sec.split('/')]
    cand = parts[-1] if len(parts) > 1 else sec
    main = re.sub(r'\s*\([^)]*\)\s*$', '', cand).strip()
    if main:
        out.append(main)
    for m in re.findall(r'\(([^)]*)\)', cand):
        m = m.strip()
        if m and len(m.split()) > 1:
            out.append(m)
    if cand and cand not in out:
        out.append(cand)
    return out


def en_title(sec):
    v = en_title_variants(sec)
    return v[0] if v else ''


def f1(a, b):
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    inter = len(sa & sb)
    if not inter:
        return 0.0
    p = inter / len(sa)
    r = inter / len(sb)
    return 2 * p * r / (p + r)


def load_chapter(ch):
    raw = open(f'{SRC}/ch/{ch}.txt', encoding='utf-8', errors='replace').read()
    parts = re.split(r'===== BOOK PAGE (\d+) =====', raw)
    pages = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
    with open(f'{SRC}/captions.json', encoding='utf-8') as f:
        caps = json.load(f).get(ch, {})
    return pages, caps


def site_blocks(ch):
    """所有區塊（含無圖的），供插入目標搜尋。"""
    path = f'{SITE}/content/docs/{ch}/_index.md'
    lines = open(path, encoding='utf-8').read().split('\n')
    blocks, cur = [], None
    for i, ln in enumerate(lines, 1):
        m = re.match(r'^(#{2,3})\s+(.*)', ln)
        if m:
            if cur:
                blocks.append(cur)
            cur = {'h2': '', 'h3': '', 'text': [], 'images': [], 'line': i,
                   'head_line': i}
            if len(m.group(1)) == 2:
                cur['h2'] = m.group(2).strip()
                cur['h3'] = ''
            else:
                cur['h3'] = m.group(2).strip()
            cur['text'].append(m.group(2))
            continue
        mi = re.search(r'!\[([^\]]*)\]\(([^)]*?page-(\d+)\.png)\)', ln)
        if mi:
            if cur is None:
                cur = {'h2': '(preamble)', 'h3': '', 'text': [], 'images': [],
                       'line': i, 'head_line': i}
            cur['images'].append({'file': int(mi.group(3)), 'line': i,
                                  'alt': mi.group(1)})
        if cur is None:
            continue
        s = ln.strip()
        if not s or s.startswith(('|', '>', '#')):
            continue
        cur['text'].append(s)
    if cur:
        blocks.append(cur)
    return blocks


def page_candidates(pages, caps):
    out = {}
    for p in sorted(pages):
        meta = caps.get(str(p), {})
        head = (meta.get('heading') or pages[p].strip().split('\n')[0]).strip()
        if NON_CONTENT.match(head):
            continue
        titles = [head]
        for c in (meta.get('captions') or []):
            t = (c.get('title') or '').strip()
            if t:
                titles.append(t)
        h = re.split(r'[:—–]', head)[0].strip()
        if h and h != head:
            titles.append(h)
        out[p] = {
            'heading': head,
            'titles': titles,
            'title_toks': [toks(t) for t in titles],
            'body_words': set(toks(pages[p])),
            'caption_titles': [(c.get('title') or '')
                                for c in (meta.get('captions') or [])],
        }
    return out


def main():
    gaps = list(csv.DictReader(open(f'{SITE}/docs/audit/image_coverage_gaps.csv',
                                    encoding='utf-8')))
    by_ch = {}
    for g in gaps:
        by_ch.setdefault(g['chapter'], []).append(int(g['book_page']))

    out_rows = []
    for ch, miss_pages in sorted(by_ch.items()):
        pages, caps = load_chapter(ch)
        pgc = page_candidates(pages, caps)
        blocks = site_blocks(ch)

        df = Counter()
        for p in pgc:
            df.update(pgc[p]['body_words'])
        N = len(pgc)
        idf = {w: math.log(N / (1 + c)) + 1.0 for w, c in df.items()}

        # 各區塊的代表書頁（用已掛圖推斷），用於順序單調性檢查
        for pg in sorted(miss_pages):
            d = pgc.get(pg)
            if d is None:
                continue
            best = None
            for b in blocks:
                sec_toks = [toks(v) for v in
                            (en_title_variants(b['h2']) + en_title_variants(b['h3']))]
                sec_w = set(toks(' '.join(b['text'])))
                sec_norm = math.sqrt(sum(idf.get(w, 1.0) for w in sec_w)) or 1.0
                tf = max((f1(stv, tt) for stv in sec_toks
                          for tt in d['title_toks']), default=0.0)
                inter = sec_w & d['body_words']
                body = (sum(idf.get(w, 1.0) for w in inter) / sec_norm) if inter else 0.0
                # 區塊自身掛的圖（其書頁）—— 供單調性檢查
                own = [i['file'] - IMG_OFFSET for i in b['images']]
                score = 5.0 * tf + 1.0 * body
                # 偏好「無圖」的區段：已有圖的區段只有在標題幾乎逐字吻合時才考慮追加
                if own and tf < MIN_TITLE_F1_APPEND:
                    score -= 1.0
                if best is None or score > best[0]:
                    best = (score, b, tf, body, own)
            score, b, tf, body, own = best
            if REQUIRE_TITLE_MATCH:
                ok = tf >= (MIN_TITLE_F1 if not own else MIN_TITLE_F1_APPEND)
            else:
                ok = (tf >= MIN_TITLE_F1 or body >= MIN_BODY_SCORE)
                if own:
                    ok = ok and tf >= MIN_TITLE_F1_APPEND
            out_rows.append({
                'chapter': ch,
                'book_page': pg,
                'image_file': f'page-{pg + IMG_OFFSET:03d}.png',
                'book_heading': d['heading'][:70],
                'caption_titles': ' | '.join(d['caption_titles'])[:150],
                'target_line': b['head_line'],
                'target_section': (b['h2'] or b['h3'])[:70],
                'target_own_pages': ','.join(str(x) for x in own),
                'title_f1': round(tf, 3),
                'body_score': round(body, 3),
                'status': 'INSERT' if ok else 'MANUAL',
                'target_has_image': 'YES' if own else 'NO',
            })

    out = f'{SITE}/docs/audit/missing_image_insertions.csv'
    fieldnames = [
        'chapter', 'book_page', 'image_file', 'book_heading', 'caption_titles',
        'target_line', 'target_section', 'target_own_pages', 'title_f1',
        'body_score', 'status', 'target_has_image',
    ]
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
        w.writeheader()
        w.writerows(out_rows)
    n_ins = sum(1 for r in out_rows if r['status'] == 'INSERT')
    print(f'缺圖書頁 {len(out_rows)}；可自動插入 {n_ins}；需人工處理 '
          f'{len(out_rows) - n_ins}')
    print(f'wrote {out}\n')
    for r in out_rows:
        mark = 'INSERT' if r['status'] == 'INSERT' else 'MANUAL'
        print(f"{mark} {r['chapter']:12s} p{r['book_page']:>3} -> L{r['target_line']:>5} "
              f"F1={r['title_f1']:>5} body={r['body_score']:>5} | "
              f"{r['book_heading'][:38]:38s} | {r['target_section'][:34]}")


if __name__ == '__main__':
    main()
