#!/usr/bin/env python3
"""全站影像對應審計：建立 image_mapping.csv。

沿用 PR #2 已驗證的規則：
  - 書頁碼 -> PDF 頁序偏移固定 +8
  - 影像檔名 page-NNN.png 的 NNN = 書頁碼 + 9

核心方法：單調對齊（monotonic alignment / DP）
  網站各章節的區塊是依原書順序撰寫的，因此「區塊 -> 原書頁碼」必然是
  非遞減序列。放棄逐段獨立比對，改以動態規劃在整條序列上做最佳對齊，
  這同時消除了低分候選頁（如 p.59 "Iatrogenic lung disease"）誤中為
  「肺部解剖」這類錯誤。

  比分三訊號加權：
    heading  (0.45)  區塊英文標題 vs 原書頁首標題
    caption  (0.30)  區塊英文標題 vs 該頁圖說標題
    text     (0.25)  區塊內文 vs 該頁內文（cosine）

信心分級：
  VERIFIED    對齊分數高且與目前影像頁碼相符
  PROBABLE    對齊分數足夠但與目前影像頁碼不符 -> 需人工覆核
  UNVERIFIED  證據不足，不給建議值（依指示：不因未找到出處就判定錯誤）
"""
import re, json, os, csv, sys
from collections import Counter

SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
IMG_OFFSET = 9

STOP = set('''the a an and or of to in is are be on for with that this these those by as at from
which when while can may also not no its their there here been being more most other than then
they them we you he she his her our your if but so such into over under between during
image images figure fig table see shown shows show used using use including include includes
e.g i.e vs versus per each any all less also only both same different new old'''.split())

# 區塊標題中的通用詞，比對時降權
WEAK = set('''approach overview patterns introduction basic basics clinical features note notes
key points diagnosis differential imaging findings management treatment imaging'''.split())


def toks(s):
    s = re.sub(r'[^a-z0-9\s]', ' ', s.lower())
    return [w for w in s.split() if len(w) > 2 and w not in STOP]


def strong(s):
    return [w for w in toks(s) if w not in WEAK]


def cosine(q, p):
    if not q or not p:
        return 0.0
    inter = sum(min(c, p.get(t, 0)) for t, c in q.items())
    if not inter:
        return 0.0
    return inter / ((sum(q.values()) ** 0.5) * (sum(p.values()) ** 0.5))


def load_pages(chapter):
    path = f'{SRC}/ch/{chapter}.txt'
    pages, cur, buf = {}, None, []
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^===== BOOK PAGE (\d+) =====$', line.rstrip())
        if m:
            if cur is not None:
                pages[cur] = '\n'.join(buf)
            cur = int(m.group(1)); buf = []
        else:
            buf.append(line.rstrip())
    if cur is not None:
        pages[cur] = '\n'.join(buf)
    return pages


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
        mi = re.search(r'!\[([^\]]*)\]\([^)]*page-(\d+)\.png\)', ln)
        if cur is None and mi:
            cur = {'h2': '(章節前言)', 'h3': '', 'imgs': [], 'text': [], 'line': i}
        if cur is None:
            continue
        if mi:
            cur['imgs'].append({'file': int(mi.group(2)), 'alt': mi.group(1), 'line': i})
        s = ln.strip()
        if not s or s.startswith(('|', '>', '#')):
            continue
        cur['text'].append(s)
    if cur:
        blocks.append(cur)
    return blocks


def page_meta(captions, ch):
    """{book_page: {heading, caption_tokset, body_tokset}}"""
    meta = {}
    capdata = captions.get(ch, {})
    for p, v in capdata.items():
        p = int(p)
        ctoks = set()
        for c in v.get('captions', []):
            ctoks |= set(strong(c['title'])) | set(strong(c['body'])[:120])
        meta[p] = {'heading': v.get('heading', ''), 'caption_tokset': ctoks}
    return meta


def align(sections, pages, meta):
    """DP 單調對齊。sections: list of (title_en, body_text)；回傳每段最佳頁碼與分數。"""
    bpages = sorted(pages)
    n, m = len(sections), len(bpages)
    if n == 0 or m == 0:
        return []

    # 預先算分數矩陣
    S = [[0.0] * m for _ in range(n)]
    for i, (title, body) in enumerate(sections):
        qt = set(strong(title))
        qb = Counter(toks(body))
        for j, p in enumerate(bpages):
            md = meta.get(p, {})
            hset = set(strong(md.get('heading', '')))
            hsc = (len(qt & hset) / len(qt)) if qt and hset else 0.0
            csc = (len(qt & md.get('caption_tokset', set())) / len(qt)) if qt else 0.0
            tsc = cosine(qb, Counter(toks(pages[p])))
            S[i][j] = 0.45 * hsc + 0.30 * csc + 0.25 * tsc

    # DP：dp[i][j] = 前 i 段、最後落在 j 或之前的最大總分
    NEG = -1e9
    dp = [[NEG] * m for _ in range(n)]
    back = [[-1] * m for _ in range(n)]
    for j in range(m):
        dp[0][j] = S[0][j]
    for i in range(1, n):
        run = NEG
        runj = -1
        for j in range(m):
            # 允許停留（同一頁可對應多段）
            if dp[i - 1][j] > run:
                run = dp[i - 1][j]; runj = j
            cand = run + S[i][j]
            if cand > dp[i][j]:
                dp[i][j] = cand
                back[i][j] = runj
    # 回溯
    path = []
    j = m - 1
    for i in range(n - 1, -1, -1):
        # 找回溯起點
        while j > 0 and back[i][j] == -1:
            j -= 1
        path.append(j)
        j = back[i][j] if back[i][j] >= 0 else j
    path.reverse()
    out = []
    for i, j in enumerate(path):
        out.append((bpages[j], S[i][j]))
    return out


def analyse_chapter(chapter, captions):
    pages = load_pages(chapter)
    meta = page_meta(captions, chapter)
    blocks = site_blocks(chapter)

    # 只取含影像的區塊參與對齊；但對齊序列必須保留所有區塊的順序。
    # 做法：用所有區塊做對齊，再取含影像者。
    secs = []
    for b in blocks:
        title = b['h3'] or b['h2']
        secs.append((title.split('/')[-1].strip(), ' '.join(b['text'])))
    aligned = align(secs, pages, meta)
    amap = {}
    for b, (bp, sc) in zip(blocks, aligned):
        amap[id(b)] = (bp, sc)

    rows = []
    for b in blocks:
        if not b['imgs']:
            continue
        exp, score = amap.get(id(b), (None, 0.0))
        title = b['h3'] or b['h2']
        for img in b['imgs']:
            cur_bp = img['file'] - IMG_OFFSET
            md = meta.get(exp, {}) if exp else {}
            # 信心：分數 + 標題/圖說命中 + 與第二名的差距
            hsc = csc = 0.0
            if exp is not None:
                qt = set(strong(title.split('/')[-1].strip()))
                hset = set(strong(md.get('heading', '')))
                hsc = (len(qt & hset) / len(qt)) if qt and hset else 0.0
                csc = (len(qt & md.get('caption_tokset', set())) / len(qt)) if qt else 0.0
            strong_evidence = (hsc >= 0.5) or (csc >= 0.6)
            if score >= 0.30 and strong_evidence:
                conf = 'high'
            elif score >= 0.18 and (hsc > 0 or csc > 0):
                conf = 'medium'
            else:
                conf = 'low'

            if exp is None or conf == 'low':
                status = 'UNVERIFIED'
                proposed = ''
                mtype = 'indeterminate'
            elif abs(cur_bp - exp) <= 1:
                status = 'VERIFIED'
                proposed = ''
                mtype = 'none'
            else:
                status = 'PROBABLE'
                proposed = f'page-{exp + IMG_OFFSET:03d}.png'
                mtype = 'image_ahead_of_text' if cur_bp > exp else 'image_behind_text'

            ev = (f'align_score={score:.3f} heading_match={hsc:.2f} caption_match={csc:.2f} | '
                  f'expected book p.{exp} heading="{md.get("heading","")[:55]}"')

            rows.append({
                'chapter': chapter,
                'section': title[:90],
                'section_h2': b['h2'][:60],
                'source_file': f'content/docs/{chapter}/_index.md',
                'source_line': img['line'],
                'current_image': f'page-{img["file"]:03d}.png',
                'current_book_page': cur_bp,
                'expected_book_page': exp if exp is not None else '',
                'proposed_image': proposed,
                'confidence': conf,
                'verification_status': status,
                'mismatch_type': mtype,
                'evidence': ev,
            })
    return rows


def main():
    chapters = sys.argv[1:] or ['thoracic', 'gi', 'genitourinary', 'neuro', 'msk',
                                 'ultrasound', 'nuclear', 'breast', 'cardiovascular',
                                 'interventional', 'pediatric', 'physics']
    with open(f'{SRC}/captions.json', encoding='utf-8') as f:
        captions = json.load(f)
    all_rows = []
    for ch in chapters:
        rows = analyse_chapter(ch, captions)
        all_rows.extend(rows)
        v = sum(1 for r in rows if r['verification_status'] == 'VERIFIED')
        p = sum(1 for r in rows if r['verification_status'] == 'PROBABLE')
        u = sum(1 for r in rows if r['verification_status'] == 'UNVERIFIED')
        hi = sum(1 for r in rows if r['confidence'] == 'high')
        print(f'{ch:16s} imgs={len(rows):3d} verified={v:3d} probable={p:3d} unverified={u:3d} '
              f'(high_conf={hi})')
    out = f'{SITE}/docs/audit/image_mapping.csv'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cols = ['chapter', 'section', 'section_h2', 'source_file', 'source_line',
            'current_image', 'current_book_page', 'expected_book_page',
            'proposed_image', 'confidence', 'verification_status', 'mismatch_type', 'evidence']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(all_rows)
    print(f'\nwrote {out}  ({len(all_rows)} rows)')


if __name__ == '__main__':
    main()
