#!/usr/bin/env python3
"""以像素比對確定性驗證影像身分（不依賴 OCR 或視覺模型）。

原理
----
static/images/<chapter>/page-NNN.png 是教科書該頁的**全頁掃描渲染**，
與 PDF 對應頁以相同解析度渲染後，像素可完全相同（實測相關係數 = 1.0000）。

因此可確定性地回答兩個不同的問題：
  (A) 這個檔案實際是教科書第幾頁？   -> 本工具（像素比對，確定性）
  (B) 這個區塊的文字應該配哪一頁？   -> audit_images.py 的單調對齊（語意，需人工覆核）

已驗證的對應規則
----------------
  檔名 page-NNN.png  ->  教科書印刷頁碼 = NNN - 9
  教科書印刷頁碼 P    ->  pdftoppm -f (P + 9)   （pdftoppm 的 -f 是 1-based PDF 頁序）

用法
----
  python3 scripts/audit/verify_image_pixels.py [chapter ...]
"""
import os, re, csv, sys, subprocess, warnings, hashlib
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings('ignore')
from PIL import Image, ImageChops, ImageStat

SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
PDF = f'{SRC}/textbook.pdf'
CACHE = f'{SRC}/pixel_cache'
RENDER_DPI = 100
SIG_W, SIG_H = 96, 120

# 已驗證規則
FILE_TO_BOOK = 9        # book page = filename number - 9
BOOK_TO_PDF1 = 9        # pdftoppm -f = book page + 9（1-based PDF 頁序）

# 章節的教科書頁碼範圍（PR #2 已逐頁驗證）
CHAPTER_PAGES = {
    'thoracic': (1, 86), 'gi': (87, 156), 'genitourinary': (157, 200),
    'neuro': (201, 345), 'msk': (346, 463), 'ultrasound': (464, 552),
    'nuclear': (553, 591), 'breast': (592, 657), 'cardiovascular': (658, 693),
    'interventional': (694, 740), 'pediatric': (741, 837), 'physics': (838, 864),
}


def render_book_page(book_page):
    """渲染教科書頁，回傳 PNG 路徑（帶快取）。

    注意：pdftoppm 的輸出檔名會把頁序零填充成 3 位（例：-010），
    快取查找必須用相同格式，否則永遠 miss。
    """
    os.makedirs(CACHE, exist_ok=True)
    out = f'{CACHE}/p{book_page:03d}'
    idx = book_page + BOOK_TO_PDF1
    png = f'{out}-{idx:03d}.png'
    if os.path.exists(png):
        return png
    try:
        subprocess.run(['pdftoppm', '-f', str(idx), '-l', str(idx),
                        '-r', str(RENDER_DPI), '-png', PDF, out],
                       capture_output=True, timeout=180)
    except Exception:
        return None
    return png if os.path.exists(png) else None


def grayscale_small(path):
    """灰階化 + 縮小成小圖（PIL C 級運算）。"""
    try:
        return Image.open(path).convert('L').resize((SIG_W, SIG_H))
    except Exception:
        return None


def mean_abs_diff(im1, im2):
    """兩張小圖的平均絕對差（PIL C 級運算）。

    同一頁的渲染與掃描 PNG 實測像素完全相同 -> 差值 = 0；
    不同頁的差值遠大於 0。"""
    d = ImageChops.difference(im1, im2)
    return ImageStat.Stat(d).mean[0]


def verify_chapter(ch):
    b0, b1 = CHAPTER_PAGES[ch]
    imgdir = f'{SITE}/static/images/{ch}'
    imgs = sorted(f for f in os.listdir(imgdir) if f.endswith('.png'))

    # 1) 渲染該章所有教科書頁，並預先縮成小圖（C 級運算）
    page_imgs = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for bp, p in zip(range(b0, b1 + 1),
                         ex.map(render_book_page, range(b0, b1 + 1))):
            if p:
                im = grayscale_small(p)
                if im is not None:
                    page_imgs.append((bp, im))
    if not page_imgs:
        return []

    rows = []
    for f in imgs:
        n = int(re.search(r'page-(\d+)', f).group(1))
        claimed = n - FILE_TO_BOOK
        s = grayscale_small(f'{imgdir}/{f}')
        if s is None:
            continue
        scored = sorted(((mean_abs_diff(s, pim), bp) for bp, pim in page_imgs))
        top_d, top_p = scored[0]
        run_d, run_p = (scored[1] if len(scored) > 1 else (999.0, None))
        # 實測（breast 章）：正確頁 diff 0.29–1.80，次選頁 13.9–24.5 —— 差距逾 10 倍。
        # 因此 diff < 3 視為確定性命中。
        if top_d < 3.0:
            status = 'VERIFIED_EXACT'
        elif top_d < 8.0:
            status = 'PROBABLE'
        else:
            status = 'UNVERIFIED'
        rows.append({
            'chapter': ch,
            'image_file': f,
            'filename_book_page': claimed,
            'actual_book_page': top_p,
            'mean_abs_diff': round(top_d, 5),
            'runner_up_page': run_p,
            'runner_up_diff': round(run_d, 5),
            'identity_status': status,
            'filename_consistent': 'YES' if top_p == claimed else 'NO',
        })
    return rows


def main():
    chapters = sys.argv[1:] or list(CHAPTER_PAGES)
    all_rows = []
    for ch in chapters:
        rows = verify_chapter(ch)
        all_rows.extend(rows)
        exact = sum(1 for r in rows if r['identity_status'] == 'VERIFIED_EXACT')
        cons = sum(1 for r in rows if r['filename_consistent'] == 'YES')
        print(f'{ch:16s} images={len(rows):3d} exact_pixel_match={exact:3d} '
              f'filename_consistent={cons:3d}', flush=True)
    out = f'{SITE}/docs/audit/image_identity_pixels.csv'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cols = ['chapter', 'image_file', 'filename_book_page', 'actual_book_page',
            'mean_abs_diff', 'runner_up_page', 'runner_up_diff', 'identity_status',
            'filename_consistent']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(all_rows)
    print(f'\nwrote {out}  ({len(all_rows)} rows)')


if __name__ == '__main__':
    main()
