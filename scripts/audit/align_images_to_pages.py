#!/usr/bin/env python3
"""最終影像比對器：**保序**對齊（書頁單調不減，允許多段共用同一頁）。

為什麼 v9 是對的
----------------
把兩邊的段落/書頁清單攤開後可以看見一個非常規律的事實（以 thoracic 為例）：

    站台含圖段落     88 個
    原書含圖書頁     47 頁（總書頁 86）
    偏移量隨段落遞增  +0 → +6 → +8 → +10 → … → +53 → 之後歸零

也就是說：**網站原本是「照著書頁順序」鋪段的，但鋪到某個點之後整段往後滑**，
滑動量隨書頁增長。這是典型的「插入/刪除一頁沒同步」造成的累積位移。

由於書頁與段落在書中同序，正確答案必然滿足：

    目標書頁序列對段落序列 **單調不減**（可多段共用同一頁）

v8 放棄單調性 → 噪音暴增；v7 加上單調性但要求「一頁配一段、段落不可跳過」
→ 讓真正對應的段落分不到頁。v9 兩點都修：
  - 書頁序列單調不減
  - 允許多個相鄰段落共用同一頁（站台把一個書頁拆成多個小節是常事）
  - 段落可「不配頁」（KEEP），不影響其他段落

評分
----
  score(section, page) = W_TITLE * F1(段落英文標題, 書頁標題∪圖說標題)
                        + W_BODY  * idf_cosine(段落內文, 書頁內文)

套用門檻
--------
  - 錨點命中率（對照 image_segment_offsets.csv 內已確認的錨點）必須達標
  - 單筆建議的 F1 必須達門檻，否則標為 KEEP
  - 位移 < MIN_MOVE 不動

輸出
----
  docs/audit/image_reassignment.csv
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

# 人工判定為錯誤配對的錨點（比對雜訊），不納入驗證
KNOWN_BAD = {('thoracic', 4524)}

# 退化錨點叢集：同一書頁被 >=3 筆指向，代表該處比對已崩壞（段落匹配退化），
# 這些錨點不能當驗證基準，否則會把錯誤當成正確來衡量命中率。
DEGENERATE_MIN_CLUSTER = 3

MIN_MOVE = 2
F1_APPLY = 0.55          # 套用所需的標題 F1 門檻
MIN_ANCHOR_HITRATE = 0.85


def toks(s):
    s = re.sub(r'[^a-z0-9\s]', ' ', (s or '').lower())
    return [w for w in s.split() if len(w) >= 3 and w not in STOP]


def en_title_variants(sec):
    """回傳英文標題的所有候選字串。

    為什麼不能只取括號內文字：站台標題常見
        「毛玻璃樣浸潤 / Ground Glass Opacification (GGO)」
    只取括號會得到 "GGO"，與原書 "Ground glass opacification (GGO)"
    的 F1 極低，害 GGO 段落配不到書頁 p10。
    因此同時保留：主體、完整原串、以及多詞的括號內容。
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
    """相容舊介面：回傳主要英文標題。"""
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
    path = f'{SITE}/content/docs/{ch}/_index.md'
    lines = open(path, encoding='utf-8').read().split('\n')
    blocks, cur = [], None
    for i, ln in enumerate(lines, 1):
        m = re.match(r'^(#{2,3})\s+(.*)', ln)
        if m:
            if cur:
                blocks.append(cur)
            cur = {'h2': '', 'h3': '', 'text': [], 'images': [], 'line': i}
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
                cur = {'h2': '(preamble)', 'h3': '', 'text': [], 'images': [], 'line': i}
            cur['images'].append({'file': int(mi.group(3)), 'line': i, 'alt': mi.group(1)})
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
        }
    return out


def load_anchors():
    """讀取已確認的錨點，並剔除退化叢集。"""
    p = f'{SITE}/docs/audit/image_segment_offsets.csv'
    if not os.path.exists(p):
        return {}
    raw = []
    for r in csv.DictReader(open(p, encoding='utf-8')):
        if r['status'] == 'MATCHED' and r['source_book_page']:
            raw.append((r['chapter'], int(r['source_line']), int(r['source_book_page'])))
    # 統計 (chapter, book_page) 的叢集大小，>= MIN 者視為退化
    cnt = Counter((c, pg) for c, _, pg in raw)
    degenerate = {k for k, v in cnt.items() if v >= DEGENERATE_MIN_CLUSTER}
    out = {}
    for c, ln, pg in raw:
        if (c, ln) in KNOWN_BAD:
            continue
        if (c, pg) in degenerate:
            continue
        out[(c, ln)] = pg
    return out


def run(ch, verbose=False, w_title=5.0, w_body=1.0):
    pages, caps = load_chapter(ch)
    pgc = page_candidates(pages, caps)
    blocks = site_blocks(ch)
    img_blocks = [b for b in blocks if b['images']]

    df = Counter()
    for p in pgc:
        df.update(pgc[p]['body_words'])
    N = len(pgc)
    idf = {w: math.log(N / (1 + c)) + 1.0 for w, c in df.items()}

    # 預先算好每段 vs 每頁的分數
    S = len(img_blocks)
    P = len(pgc)
    plist = sorted(pgc)
    tf = [[0.0] * P for _ in range(S)]
    bs = [[0.0] * P for _ in range(S)]
    tot = [[0.0] * P for _ in range(S)]
    for si, b in enumerate(img_blocks):
        variants = en_title_variants(b['h2']) + en_title_variants(b['h3'])
        sec_toks = [toks(v) for v in variants]
        sec_t = [w for tv in sec_toks for w in tv]
        sec_w = set(toks(' '.join(b['text'])))
        sec_norm = math.sqrt(sum(idf.get(w, 1.0) for w in sec_w)) or 1.0
        for pi, p in enumerate(plist):
            t = max((f1(stv, tt) for stv in sec_toks for tt in pgc[p]['title_toks']),
                    default=0.0)
            inter = sec_w & pgc[p]['body_words']
            body = (sum(idf.get(w, 1.0) for w in inter) / sec_norm) if inter else 0.0
            tf[si][pi] = t
            bs[si][pi] = body
            tot[si][pi] = w_title * t + w_body * body

    # DP：段落 i -> 書頁 j，書頁序列單調不減（允許多段共用同一頁）
    NEG = -1e18
    # f[i][j] = 前 i+1 段的最大總分，第 i 段配到第 j 頁
    f = [row[:] for row in tot]
    ptr = [[-1] * P for _ in range(S)]
    for i in range(1, S):
        # prefix max over k <= j of f[i-1][k]
        run_max, run_arg = NEG, 0
        for j in range(P):
            if f[i - 1][j] > run_max:
                run_max, run_arg = f[i - 1][j], j
            v = run_max + tot[i][j]
            if v > f[i][j]:
                f[i][j] = v
                ptr[i][j] = run_arg
    j = max(range(P), key=lambda x: f[S - 1][x])
    assign = [0] * S
    for i in range(S - 1, -1, -1):
        assign[i] = j
        j = ptr[i][j]
        if j < 0:
            for k in range(i - 1, -1, -1):
                assign[k] = j
            break

    anc = {ln: pg for (c, ln), pg in load_anchors().items() if c == ch}

    rows = []
    hit = miss = 0
    for si, b in enumerate(img_blocks):
        im = b['images'][0]
        ln = im['line']
        cur_pg = im['file'] - IMG_OFFSET
        pi = assign[si]
        sugg_pg = plist[pi]
        t = tf[si][pi]
        body = bs[si][pi]

        if t >= 0.80:
            conf = 'HIGH'
        elif t >= F1_APPLY:
            conf = 'MEDIUM'
        else:
            conf = 'LOW'

        if conf == 'LOW' or abs(sugg_pg - cur_pg) < MIN_MOVE:
            status = 'KEEP'
        else:
            status = 'REASSIGN'

        tag = ''
        if ln in anc:
            if sugg_pg == anc[ln]:
                hit += 1
                tag = 'HIT'
            else:
                miss += 1
                tag = f'MISS(exp p{anc[ln]})'

        rows.append({
            'chapter': ch,
            'source_line': ln,
            'section': (b['h2'] or b['h3'])[:70],
            'current_image': f'page-{im["file"]:03d}.png',
            'current_book_page': cur_pg,
            'suggested_book_page': sugg_pg,
            'suggested_image': f'page-{sugg_pg + IMG_OFFSET:03d}.png',
            'offset': sugg_pg - cur_pg,
            'title_f1': round(t, 3),
            'body_score': round(body, 3),
            'confidence': conf,
            'suggested_page_heading': pgc[sugg_pg]['heading'][:70],
            'status': status,
            'anchor_expected_page': anc.get(ln, ''),
            'anchor_check': tag,
        })
        if verbose:
            print(f'{tag:14s} L{ln:>5} p{cur_pg:>3} -> p{sugg_pg:<3} '
                  f'F1={t:.2f} body={body:.2f} {conf:6s} {status:8s} | '
                  f'{(b["h2"] or b["h3"])[:36]:36s} | {pgc[sugg_pg]["heading"][:34]}')
    return rows, hit, miss, len(blocks), len(img_blocks), len(pgc)


ALL_CHAPTERS = ['thoracic', 'gi', 'genitourinary', 'neuro', 'msk', 'ultrasound',
                'nuclear', 'breast', 'cardiovascular', 'interventional',
                'pediatric', 'physics']


def main():
    chs = sys.argv[1:] or ALL_CHAPTERS
    allrows = []
    summary = []
    for ch in chs:
        rows, hit, miss, nb, nimg, npg = run(ch, verbose=False)
        total = hit + miss
        rate = (hit / total) if total else 1.0
        nre = sum(1 for r in rows if r['status'] == 'REASSIGN')
        ok = 'PASS' if rate >= MIN_ANCHOR_HITRATE else 'FAIL'
        summary.append((ch, hit, total, rate, ok, nb, nimg, npg, nre))
        allrows += rows
    print(f'{"章節":16s} {"錨點":>10s} {"命中率":>7s}  {"狀態":5s} '
          f'{"含圖段落":>8s} {"書頁":>5s} {"建議重指派":>10s}')
    print('-' * 72)
    for ch, hit, total, rate, ok, nb, nimg, npg, nre in summary:
        print(f'{ch:16s} {hit:>4d}/{total:<5d} {rate:>6.0%}  {ok:5s} '
              f'{nimg:>8d} {npg:>5d} {nre:>10d}')
    print('-' * 72)
    print(f'合計建議重指派：{sum(s[8] for s in summary)}')
    out = f'{SITE}/docs/audit/image_reassignment.csv'
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(allrows[0].keys()), lineterminator='\n')
        w.writeheader()
        w.writerows(allrows)
    print(f'wrote {out}')


if __name__ == '__main__':
    main()
