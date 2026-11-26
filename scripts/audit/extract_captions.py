#!/usr/bin/env python3
"""從教科書文字層抽取「圖說（figure caption）」與「頁首標題」，供影像語意交叉驗證。

沿用 PR #2 已驗證的規則：
  - 書頁碼 -> PDF 頁序偏移固定 +8
  - 影像檔名 page-NNN.png 的 NNN = 書頁碼 + 9

圖說的三種真實形態（皆由實際文字層觀察歸納，非臆測）：
  A. 影像描述 + 冒號 + 詳細說明      例：「Amorphous calcifications: Numerous ...」
  B. 直接以說明開頭（無標題）        例：「Round atelectasis: Noncontrast CT shows ...」
  C. 含 "Case courtesy" 的病例行

信心分級（避免把一般條列誤判為圖說）：
  high   明確含影像字樣 / Case courtesy
  medium 冒號型，且前段像標題、後段夠長
  low    僅靠冒號型態推得 —— 需人工覆核
"""
import re, json, os, sys

SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
OFF = 8

FOOT = re.compile(r'Downloaded from Cambridge Books Online|Cambridge Books Online ©|http://dx\.doi\.org')

IMG_WORDS = (r'Case\s+courtesy|radiograph|\bfrontal\b|\blateral\b|\baxial\b|\bcoronal\b|'
             r'\bsagittal\b|\boblique\b|\bCT\b|\bMR\b|MRI|angiogram|ultrasound|'
             r'scintigraph|\bschematic\b|\bplain\s+film\b|\bimage\b|\bview\b|'
             r'\bphotograph\b|\bphotograph|\bspecimen\b|\bpathology\b|'
             r'\bcalcification|\bmass\b|\bnodule|\bopacity|\bconsolidation|'
             r'\bmetastasis|\bfracture|\bstenosis|\bdilatation|\bembolus|'
             r'\babscess|\beffusion|\bpneumothorax|\bhernia|\bforeign body')

CAPTION_IMG = re.compile(IMG_WORDS, re.I)
CAPTION_COLON = re.compile(r'^([A-Z][^:]{6,90}):\s+(\S.*)$')
CASE_COURTESY = re.compile(r'Case\s+courtesy', re.I)


def load_pages(chapter):
    path = f'{SRC}/ch/{chapter}.txt'
    pages, cur, buf = {}, None, []
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^===== BOOK PAGE (\d+) =====$', line.rstrip())
        if m:
            if cur is not None:
                pages[cur] = buf
            cur = int(m.group(1)); buf = []
        else:
            buf.append(line.rstrip())
    if cur is not None:
        pages[cur] = buf
    return pages


def clean_lines(lines):
    return [l.strip() for l in lines if l.strip() and not FOOT.search(l)]


FIG_PAIR = re.compile(
    r'\b(frontal|lateral|axial|coronal|sagittal|oblique|AP|PA|anteroposterior|posteroanterior)\b'
    r'[^.]{0,50}?\b(radiograph|film|image|view|projection|CT|MR|MRI|angiogram|ultrasound|scintigraph)\b',
    re.I)
FIG_LEFT_RIGHT = re.compile(r'\b(left|right)\s+(image|panel)\b', re.I)


def count_figures(text):
    """估算該圖說涵蓋的影像數量。"""
    n = len(FIG_PAIR.findall(text))
    if len(FIG_LEFT_RIGHT.findall(text)) >= 2:
        n = max(n, 2)
    return max(1, n)


def extract_captions(lines):
    ls = clean_lines(lines)
    caps = []
    i = 0
    while i < len(ls):
        l = ls[i]
        m = CAPTION_COLON.match(l)
        if not m:
            i += 1
            continue
        title, body = m.group(1).strip(), m.group(2).strip()
        # 前段須像標題（非完整敘述句）
        title_like = (not title.endswith('.') and len(title.split()) <= 12
                      and not title.lower().startswith(('the ', 'this ', 'in ')))
        if not title_like:
            i += 1
            continue
        # 往後接續行屬同一圖說
        j = i + 1
        cont = []
        while j < len(ls):
            nxt = ls[j]
            if nxt.startswith('•'):
                break
            if CAPTION_COLON.match(nxt) and title_like:
                break
            if len(nxt) < 3:
                break
            cont.append(nxt)
            j += 1
            if len(cont) > 10:
                break
        full = ' '.join([title, body] + cont)
        has_img = bool(CAPTION_IMG.search(full))
        has_case = bool(CASE_COURTESY.search(full))
        if has_case:
            conf = 'high'
        elif has_img:
            conf = 'high'
        elif len(body) > 60:
            conf = 'medium'
        else:
            conf = 'low'
        caps.append({
            'title': title,
            'body': ' '.join([body] + cont),
            'figures': count_figures(full),
            'confidence': conf,
        })
        i = j
    return caps


def page_heading(lines):
    for l in clean_lines(lines):
        if l.startswith('•'):
            continue
        if len(l) <= 70 and re.match(r'^[A-Z0-9]', l):
            return l
    return ''


def main():
    chapters = sys.argv[1:] or ['thoracic', 'gi', 'genitourinary', 'neuro', 'msk',
                                 'ultrasound', 'nuclear', 'breast', 'cardiovascular',
                                 'interventional', 'pediatric', 'physics']
    out = {}
    for ch in chapters:
        pages = load_pages(ch)
        rec = {}
        for p, lines in pages.items():
            caps = extract_captions(lines)
            rec[p] = {
                'heading': page_heading(lines),
                'captions': caps,
                'n_captions': len(caps),
                'n_figures': sum(c['figures'] for c in caps),
                'n_confident': sum(1 for c in caps if c['confidence'] == 'high'),
            }
        out[ch] = rec
        tot_c = sum(v['n_captions'] for v in rec.values())
        tot_h = sum(v['n_confident'] for v in rec.values())
        pages_with = sum(1 for v in rec.values() if v['n_confident'])
        print(f'{ch:16s} pages={len(rec):3d}  pages_with_high_conf={pages_with:3d}  '
              f'captions={tot_c:3d} (high={tot_h:3d})')
    with open(f'{SRC}/captions.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'\nwrote {SRC}/captions.json')


if __name__ == '__main__':
    main()
