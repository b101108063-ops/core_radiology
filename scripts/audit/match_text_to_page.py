#!/usr/bin/env python3
"""對照引擎：把網站章節的每一段文字配對到教科書頁碼。

用途：找出「網站段落實際來自哪一頁」，再與該段落所嵌入的圖檔（book page = 檔名 - 9）
比較，量化影像配對錯誤。
"""
import re, json, sys, os
from collections import Counter

# 教科書來源工作目錄。可用環境變數 CR_SOURCE_DIR 覆蓋。
# 預設 /tmp/cr_source，內含：
#   textbook.pdf            原始 PDF（Core Radiology, Cambridge 2013）
#   text_all.txt            pdftotext -layout 產生的全書文字層
#   ch/<chapter>.txt        各章依書頁碼切分的文字
#   bookhead.json           書頁 → 頁標題
#   p2i.json                書頁碼 → PDF 頁序（偏移固定 +8）
SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
IMG_OFFSET = 9   # 影像檔名編號 = 書頁碼 + 9

FOOT = re.compile(r'Downloaded from Cambridge Books Online|Cambridge Books Online ©|http://dx\.doi\.org')

STOP = set('''the a an and or of to in is are be on for with that this these those by as at from
which when while can may also not no its their there here been being more most other than then
they them we you he she his her our your if but so such into over under between during
patient patients image images figure fig table see shown shows show used using use
including include includes included e.g i.e vs versus per'''.split())


def tokens(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    return [w for w in s.split() if len(w) > 2 and w not in STOP]


def load_book_pages(chapter):
    """回傳 {book_page: text}"""
    path = f'{SRC}/ch/{chapter}.txt'
    out = {}
    cur = None
    buf = []
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^===== BOOK PAGE (\d+) =====$', line.rstrip())
        if m:
            if cur is not None:
                out[cur] = '\n'.join(buf)
            cur = int(m.group(1)); buf = []
        else:
            buf.append(line.rstrip())
    if cur is not None:
        out[cur] = '\n'.join(buf)
    return out


def parse_site(chapter):
    """把網站 _index.md 切成段落區塊，回傳 list of dict"""
    path = f'{SITE}/content/docs/{chapter}/_index.md'
    lines = open(path, encoding='utf-8').read().split('\n')
    blocks = []
    cur = None
    for ln in lines:
        m2 = re.match(r'^##\s+(.*)', ln)
        m3 = re.match(r'^###\s+(.*)', ln)
        if m2 or m3:
            if cur:
                blocks.append(cur)
            cur = {'h2': '', 'h3': '', 'imgs': [], 'text': []}
            if m2:
                cur['h2'] = m2.group(1).strip(); cur['h3'] = ''
            else:
                cur['h3'] = m3.group(1).strip()
            continue
        if cur is None:
            continue
        mi = re.search(r'!\[([^\]]*)\]\([^)]*page-(\d+)\.png\)', ln)
        if mi:
            cur['imgs'].append(int(mi.group(2)))
        # 收集可比對的英文散文（去掉表格行與引用標記）
        s = ln.strip()
        if not s or s.startswith('|') or s.startswith('>') or s.startswith('#'):
            continue
        cur['text'].append(s)
    if cur:
        blocks.append(cur)
    return blocks


def best_pages(text, bookpages, topk=3):
    """以詞重疊找出最可能的教科書頁"""
    q = Counter(tokens(text))
    if not q:
        return []
    scored = []
    for p, bt in bookpages.items():
        bt_toks = Counter(tokens(bt))
        inter = sum(min(c, bt_toks.get(t, 0)) for t, c in q.items())
        if inter == 0:
            continue
        denom = (sum(q.values()) ** 0.5) * (sum(bt_toks.values()) ** 0.5)
        scored.append((inter / denom, inter, p))
    scored.sort(reverse=True)
    return scored[:topk]


def main():
    chapter = sys.argv[1]
    bookpages = load_book_pages(chapter)
    blocks = parse_site(chapter)
    rows = []
    for b in blocks:
        text = ' '.join(b['text'])
        if len(tokens(text)) < 12:
            continue
        cand = best_pages(text, bookpages)
        if not cand:
            continue
        score, inter, p = cand[0]
        img_bp = [i - IMG_OFFSET for i in b['imgs']]
        rows.append({
            'h2': b['h2'], 'h3': b['h3'],
            'img_bp': img_bp,
            'text_bp': p, 'score': round(score, 4), 'inter': inter,
            'alt': cand[1][2] if len(cand) > 1 else None,
            'altscore': round(cand[1][0], 4) if len(cand) > 1 else 0,
            'cand': [(c[2], round(c[0], 4)) for c in cand],
        })
    json.dump(rows, open(f'/tmp/cr_source/match_{chapter}.json', 'w'), ensure_ascii=False, indent=1)
    print(f'{"text→book p.":>10} {"score":>6} {"img→book p.":>16} {"Δ":>4}  section')
    mism = 0; tot = 0
    for r in rows:
        tb = r['text_bp']
        ibs = r['img_bp']
        if not ibs:
            continue
        tot += 1
        # 圖片應落在文字所屬頁的附近（±3）
        d = min(abs(i - tb) for i in ibs)
        flag = 'OK' if d <= 3 else f'{d:+d}'
        if d > 3:
            mism += 1
        sec = (r['h2'] or r['h3'])[:46]
        print(f'{tb:10d} {r["score"]:6.3f} {str(ibs[:3]):>16} {flag:>4}  {sec}')
    print(f'\n影像與文字頁碼落差 >3 頁的段落: {mism}/{tot}')


if __name__ == '__main__':
    main()
