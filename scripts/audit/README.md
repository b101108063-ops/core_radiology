# Textbook Content Audit Tools

比對《Core Radiology》教科書原文與網站章節內容的工具。

## 來源

- 教科書 PDF：**Core Radiology: A Visual Approach to Diagnostic Imaging**，Jacob Mandell，
  Cambridge University Press, 2013，ISBN 978-1-107-67968-9，896 頁。
- 來源由維護者提供（Google Drive）。**PDF 本身不納入 git**（版權），需另行取得。

## 準備來源工作目錄

```bash
export CR_SOURCE_DIR=/tmp/cr_source
mkdir -p "$CR_SOURCE_DIR/ch"

cp /path/to/textbook.pdf "$CR_SOURCE_DIR/"

# 抽取全書文字層
pdftotext -layout "$CR_SOURCE_DIR/textbook.pdf" "$CR_SOURCE_DIR/text_all.txt"

# 依章節切分（章節邊界為教科書各章 Contents 頁的書頁碼）
python3 - <<'PY'
import re, os
src = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
raw = open(f'{src}/text_all.txt', encoding='utf-8', errors='replace').read()
pages = raw.split('\x0c')
OFF = 8                      # 書頁碼 -> PDF 頁序的固定偏移（已對 886 頁驗證）
FOOT = re.compile(r'Downloaded from Cambridge Books Online|Cambridge Books Online ©|http://dx\.doi\.org')
clean = lambda p: [l.strip() for l in p.split('\n') if l.strip() and not FOOT.search(l)]
ranges = {
    'thoracic': (1, 86), 'gi': (87, 156), 'genitourinary': (157, 200),
    'neuro': (201, 345), 'msk': (346, 463), 'ultrasound': (464, 552),
    'nuclear': (553, 591), 'breast': (592, 657), 'cardiovascular': (658, 693),
    'interventional': (694, 740), 'pediatric': (741, 837), 'physics': (838, 864),
}
for d, (b0, b1) in ranges.items():
    with open(f'{src}/ch/{d}.txt', 'w', encoding='utf-8') as f:
        for n in range(b0, b1 + 1):
            f.write(f'\n===== BOOK PAGE {n} =====\n')
            f.write('\n'.join(clean(pages[n + OFF])) + '\n')
PY
```

## 影像與書頁碼的對應關係

```
static/images/<chapter>/page-NNN.png   的 NNN  =  教科書印刷頁碼 + 9
```

此關係已由視覺辨識（頁首標題 + 頁腳頁碼）與 12 章影像檔名區間雙重驗證。

## 執行比對

```bash
export CR_SOURCE_DIR=/tmp/cr_source
export CR_SITE_DIR=/path/to/core_radiology_hugo

# 逐段落的「文字 → 書頁碼」比對，並檢查該段落的影像頁碼是否對得上
python3 scripts/audit/match_text_to_page.py thoracic

# 以英文標題對到教科書頁標題，判定每個區塊「應該」用哪一張圖
python3 scripts/audit/match_heading_to_page.py thoracic
```

兩個工具都會把結果寫成 JSON（`$CR_SOURCE_DIR/match_<chapter>.json`、
`hdrmatch_<chapter>.json`），供人工覆核。

## 影像對齊與覆蓋驗收

```bash
# 產生保序對齊候選；只寫 CSV，不直接修改正文
python3 scripts/audit/align_images_to_pages.py

# 盤點原書有圖、站台尚未引用的書頁
python3 scripts/audit/audit_image_coverage.py

# 產生缺頁補圖計畫；人工覆核 CSV 後再套用
python3 scripts/audit/plan_missing_images.py
python3 scripts/audit/apply_missing_images.py --dry-run

# 人工覆核重指派 CSV 後再套用
python3 scripts/audit/apply_reassign.py --dry-run
```

最終輸出：

- `docs/audit/image_reassignment.csv`：保序對齊候選
- `docs/audit/image_coverage_gaps.csv`：尚未覆蓋的真缺口
- `docs/audit/verified_no_figure_pages.csv`：人工視覺確認無圖、須排除的 OCR 假陽性
- `docs/audit/missing_image_insertions.csv`：補圖計畫

`align_images_to_pages.py` 的 FAIL 表示人工錨點命中率不足，結果只能盤點，不能套用。
兩個 apply 工具一律先跑 `--dry-run`，再檢查 diff、Hugo build 與缺檔。

## 重要限制

文字比對只能產生**候選**書頁，不能取代人工視覺覆核 —— 圖說語意需逐張確認。
工具本身不會修改任何 content 檔案。
