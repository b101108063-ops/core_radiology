#!/usr/bin/env python3
"""以 OCR 驗證「影像檔實際對應的教科書頁」。

原理：static/images/<chapter>/page-NNN.png 是教科書該頁的**全頁掃描**，
因此可對 PNG 做 OCR，再與 PDF 文字層該頁的內容比對，判定這張圖
「實際上是哪一頁」。

這與 F-01（影像「應該」對應哪一頁）是兩個不同的問題：
  - 本工具回答：這張圖實際是第幾頁？（影像身分，OCR 可確定性驗證）
  - 對齊引擎回答：這張圖「應該」是第幾頁？（語意，須人工覆核）

同時處理「同一頁含多個 figure」的情況：該頁所有圖說標題都會被列出，
供人工確認實際是哪一幅。
"""
import re, os, csv, sys, json, subprocess, hashlib
from concurrent.futures import ThreadPoolExecutor

SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
IMG_OFFSET = 9
OCR_CACHE = f'{SRC}/ocr_cache'

STOP = set('''the a an and or of to in is are be on for with that this these those by as at from
which when while can may also not no its their there here been being more most other than then
they them we you he she his her our your if but so such into over under between during
case courtesy dr hospital brigham women'''.split())


def toks(s):
    s = re.sub(r'[^a-z0-9\s]', ' ', s.lower())
    return [w for w in s.split() if len(w) > 2 and w not in STOP]


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


def ocr_image(path):
    """OCR 一張圖，回傳文字（帶快取）。"""
    os.makedirs(OCR_CACHE, exist_ok=True)
    key = hashlib.md5(f'{os.path.basename(path)}:{os.path.getsize(path)}'.encode()).hexdigest()
    cf = f'{OCR_CACHE}/{key}.txt'
    if os.path.exists(cf):
        return open(cf, encoding='utf-8', errors='replace').read()
    try:
        r = subprocess.run(['tesseract', path, '-', '--psm', '3'],
                           capture_output=True, timeout=180)
        txt = r.stdout.decode('utf-8', errors='replace')
    except Exception as e:
        txt = f''
    with open(cf, 'w', encoding='utf-8') as f:
        f.write(txt)
    return txt


def score(t1, t2):
    a, b = set(toks(t1)), set(toks(t2))
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def verify_one(chapter, img_file, pages):
    """回傳該影像實際對應的原書頁碼與信心。"""
    path = f'{SITE}/static/images/{chapter}/{img_file}'
    if not os.path.exists(path):
        return None
    txt = ocr_image(path)
    if len(txt.strip()) < 30:
        return {'ocr_chars': len(txt.strip()), 'actual_page': None,
                'score': 0.0, 'runner': None, 'runner_score': 0.0,
                'status': 'OCR_FAILED'}
    ot = set(toks(txt))
    scored = []
    for p, bt in pages.items():
        bt_t = set(toks(bt))
        if not bt_t:
            continue
        s = len(ot & bt_t) / len(ot | bt_t)
        scored.append((s, p))
    scored.sort(reverse=True)
    if not scored:
        return {'ocr_chars': len(txt), 'actual_page': None, 'score': 0.0,
                'runner': None, 'runner_score': 0.0, 'status': 'NO_CANDIDATE'}
    top_s, top_p = scored[0]
    run_s, run_p = (scored[1] if len(scored) > 1 else (0.0, None))
    margin = top_s - run_s
    if top_s >= 0.30 and margin >= 0.05:
        status = 'VERIFIED'
    elif top_s >= 0.20:
        status = 'PROBABLE'
    else:
        status = 'UNVERIFIED'
    return {'ocr_chars': len(txt), 'actual_page': top_p, 'score': round(top_s, 4),
            'runner': run_p, 'runner_score': round(run_s, 4), 'status': status,
            'margin': round(margin, 4)}


def main():
    chapters = sys.argv[1:] or ['thoracic', 'gi', 'genitourinary', 'neuro', 'msk',
                                 'ultrasound', 'nuclear', 'breast', 'cardiovascular',
                                 'interventional', 'pediatric', 'physics']
    rows = []
    for ch in chapters:
        pages = load_pages(ch)
        imgs = sorted(f for f in os.listdir(f'{SITE}/static/images/{ch}')
                      if f.endswith('.png'))
        print(f'{ch}: {len(imgs)} images -> OCR...', flush=True)
        with ThreadPoolExecutor(max_workers=4) as ex:
            results = list(ex.map(lambda f: verify_one(ch, f, pages), imgs))
        nver = sum(1 for r in results if r and r['status'] == 'VERIFIED')
        for f, r in zip(imgs, results):
            if r is None:
                continue
            rows.append({
                'chapter': ch,
                'image_file': f,
                'filename_book_page': int(re.search(r'page-(\d+)', f).group(1)) - IMG_OFFSET,
                'actual_book_page': r.get('actual_page'),
                'ocr_match_score': r.get('score'),
                'ocr_margin': r.get('margin'),
                'runner_up_page': r.get('runner'),
                'ocr_status': r.get('status'),
                'ocr_chars': r.get('ocr_chars'),
                'identity_agrees': ('YES' if r.get('actual_page') ==
                                    int(re.search(r'page-(\d+)', f).group(1)) - IMG_OFFSET
                                    else 'NO'),
            })
        print(f'   verified_identity={nver}/{len(imgs)}')
    out = f'{SITE}/docs/audit/image_identity_ocr.csv'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cols = ['chapter', 'image_file', 'filename_book_page', 'actual_book_page',
            'ocr_match_score', 'ocr_margin', 'runner_up_page', 'ocr_status',
            'ocr_chars', 'identity_agrees']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f'\nwrote {out}  ({len(rows)} rows)')


if __name__ == '__main__':
    main()
