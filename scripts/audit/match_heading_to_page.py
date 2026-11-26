#!/usr/bin/env python3
"""標題層級比對：把網站每個 section 的英文標題對到教科書頁標題，
再檢查該 section 所嵌入的影像檔是否就是正確的教科書頁。

規則：
  image file page-NNN  ->  book printed page = NNN - 9
  正確的影像 = 教科書該 section 所在頁 + 9
"""
import re, json, sys, os

# 見 match_text_to_page.py 的路徑說明。
SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
IMG_OFFSET = 9

def norm(s):
    s = s.lower()
    s = re.sub(r'\b(overview|patterns?|approach|introduction|basic|basics|of|the|and|for|in|to|a|an|imaging|radiology|radiographic|key|points?|clinical|features?|notes?)\b', ' ', s)
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    return ' '.join(w for w in s.split() if len(w) > 2)

def load_book_headings(chapter):
    """{book_page: heading}"""
    path = f'{SRC}/ch/{chapter}.txt'
    heads = {}
    cur = None
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^===== BOOK PAGE (\d+) =====$', line.rstrip())
        if m:
            cur = int(m.group(1)); heads.setdefault(cur, [])
            continue
        if cur is None:
            continue
        s = line.strip()
        if not s or len(s) > 70:
            continue
        if s.startswith(('•', 'Downloaded', 'http')):
            continue
        heads[cur].append(s)
    return heads

def site_sections(chapter):
    path = f'{SITE}/content/docs/{chapter}/_index.md'
    lines = open(path, encoding='utf-8').read().split('\n')
    secs = []
    cur = None
    for ln in lines:
        m2 = re.match(r'^##\s+(.*)', ln)
        m3 = re.match(r'^###\s+(.*)', ln)
        if m2 or m3:
            if cur and (cur['h2'] or cur['h3']):
                secs.append(cur)
            cur = {'h2': '', 'h3': '', 'imgs': []}
            if m2:
                cur['h2'] = m2.group(1).strip(); cur['h3'] = ''
            else:
                cur['h3'] = m3.group(1).strip()
            continue
        if cur is None:
            continue
        mi = re.search(r'page-(\d+)\.png', ln)
        if mi:
            cur['imgs'].append(int(mi.group(1)))
    if cur and (cur['h2'] or cur['h3']):
        secs.append(cur)
    return secs

def main():
    chapter = sys.argv[1]
    bh = load_book_headings(chapter)
    # 建立 教科書頁 -> 該頁所有標題的正規化 token 集合
    page_norm = {}
    for p, hs in bh.items():
        page_norm[p] = {norm(h) for h in hs if norm(h)}
    # 反向：token -> 頁碼
    tok2page = {}
    for p, ns in page_norm.items():
        for n in ns:
            tok2page.setdefault(n, set()).add(p)

    secs = site_sections(chapter)
    rows = []
    for s in secs:
        title = s['h3'] or s['h2']
        if not s['imgs']:
            continue
        en = title.split('/')[-1].strip()
        n = norm(en)
        cand = tok2page.get(n, set())
        if not cand:
            # 退而求其次：用部分 token
            toks = set(n.split())
            best = None
            for p, ns in page_norm.items():
                for pn in ns:
                    pt = set(pn.split())
                    if toks and len(toks & pt) / max(len(toks), 1) >= 0.6:
                        if best is None or p < best[0]:
                            best = (p, len(toks & pt))
            cand = {best[0]} if best else set()
        want = sorted(cand)[:1]
        got_bp = sorted(set(i - IMG_OFFSET for i in s['imgs']))
        rows.append({
            'title': title, 'img_files': s['imgs'],
            'want_bp': want[0] if want else None,
            'got_bp': got_bp,
            'correct_file': (want[0] + IMG_OFFSET) if want else None,
        })

    print(f'=== {chapter} ===')
    print(f'{"site section":50s} {"img":>6} {"book p(img)":>11} {"book p(txt)":>11} {"should be":>10}  ok')
    ok = wrong = unk = 0
    for r in rows:
        f = r['img_files'][0]
        gb = f - IMG_OFFSET
        wb = r['want_bp']
        if wb is None:
            print(f'{r["title"][:50]:50s} {f:6d} {gb:11d} {"?":>11s} {"?":>10s}  ?')
            unk += 1
        else:
            good = abs(gb - wb) <= 1
            ok += good; wrong += (not good)
            should = r['correct_file']
            print(f'{r["title"][:50]:50s} {f:6d} {gb:11d} {wb:11d} {str(should):>10}  {"OK" if good else "X"}')
    print(f'\n圖像與內容頁碼相符(±1): {ok} / 不符: {wrong} / 無法對應: {unk}  (共 {len(rows)})')
    json.dump(rows, open(f'/tmp/cr_source/hdrmatch_{chapter}.json', 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
