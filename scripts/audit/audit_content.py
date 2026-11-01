#!/usr/bin/env python3
"""Task 1 — 全章內容比對引擎。

比對三個維度：
  1. 數值門檻（numeric thresholds）：網站出現的數值是否在原書同一主題附近也出現
  2. 原書未出現的關鍵醫學敘述：網站有、原書同頁找不到（僅列為 UNVERIFIED，不判定錯誤）
  3. 章內矛盾：同一概念在網站不同位置出現互相衝突的說法

沿用 PR #2 已驗證規則：書頁碼 = 影像檔名 - 9；書頁碼 -> PDF 頁序偏移 +8。
"""
import re, json, os, csv, sys
from collections import Counter, defaultdict

SRC = os.environ.get('CR_SOURCE_DIR', '/tmp/cr_source')
SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
IMG_OFFSET = 9

STOP = set('''the a an and or of to in is are be on for with that this these those by as at from
which when while can may also not no its their there here been being more most other than then
they them we you he she his her our your if but so such into over under between during'''.split())

# 數值 + 單位
NUM = re.compile(
    r'(?<![\w.])(\d+(?:\.\d+)?)\s*'
    r'(%|mm|cm|mL|ml|mg|kg|Hz|Gy|gy|days?|weeks?|months?|years?|hours?|minutes?|min|sec)',
    re.I)

# 醫學主題關鍵詞（用於主題定位）
TOPICS = {
    'atelectasis': r'atelectasis|collapse|luftsichel|golden',
    'pneumonia': r'pneumonia|pneumonitis|abscess|empyema|tuberculosis|koch',
    'ggo': r'ground.?glass|\bGGO\b|crazy paving|consolidation',
    'nodule': r'nodule|tree.in.bud|miliary|random nodule',
    'lungcancer': r'lung cancer|carcinoma|adenocarcinoma|squamous|small cell',
    'mediastinum': r'mediastin|thymoma|teratoma|lymphadenopathy',
    'pleura': r'pleura|effusion|pneumothorax|empyema necessitans',
    'aorta': r'aort|aneurysm|endoleak| dissection',
    'kidney': r'kidney|renal|nephro|adrenal',
    'liver': r'liver|hepat|cirrhos|biliary',
    'breast': r'breast|mammograph|calcification|BI-RADS',
    'neuro': r'brain|cerebr|stroke|aneurysm|hemorrhage',
    'msk': r'bone|fracture|arthritis|joint|osteomyelitis',
    'ultrasound': r'ultrasound|doppler|echograph|sonograph',
    'nuclear': r'PET|SPECT|thyroid scan|bone scan',
    'interventional': r'angiograph|angioplasty|stent|emboliz|catheter',
    'pediatric': r'child|infant|neonat|pediatric',
    'physics': r'contrast|radiation|dose|Hounsfield|attenuation',
    'contrast': r'contrast|reaction|renal|nephropathy|extravasation',
}


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


def site_sections(chapter):
    path = f'{SITE}/content/docs/{chapter}/_index.md'
    if not os.path.exists(path):
        return []
    lines = open(path, encoding='utf-8').read().split('\n')
    secs, cur = [], None
    for i, ln in enumerate(lines, 1):
        m2 = re.match(r'^##\s+(.*)', ln)
        m3 = re.match(r'^###\s+(.*)', ln)
        if m2 or m3:
            if cur:
                secs.append(cur)
            cur = {'h2': '', 'h3': '', 'lines': [], 'start': i}
            if m2:
                cur['h2'] = m2.group(1).strip(); cur['h3'] = ''
            else:
                cur['h3'] = m3.group(1).strip()
            continue
        if cur is None:
            continue
        cur['lines'].append((i, ln))
    if cur:
        secs.append(cur)
    return secs


def toks(s):
    s = re.sub(r'[^a-z0-9\s]', ' ', s.lower())
    return [w for w in s.split() if len(w) > 2 and w not in STOP]


def topic_of(text):
    tl = text.lower()
    best, bs = None, 0
    for t, pat in TOPICS.items():
        n = len(re.findall(pat, tl, re.I))
        if n > bs:
            best, bs = t, n
    return best or ''


def find_topic_pages(pages, topic):
    """在原書找出屬於某主題的頁碼集合"""
    pat = re.compile(TOPICS[topic], re.I)
    return {p for p, t in pages.items() if pat.search(t)}


def numbers_in(text):
    out = []
    for m in NUM.finditer(text):
        val = float(m.group(1))
        unit = m.group(2).lower().rstrip('s')
        # 排除明顯非醫學數值（年份、章節號）
        if unit in ('days', 'day') and val > 365:
            continue
        out.append((m.group(0).strip(), val, unit, text[max(0, m.start()-90):m.start()]))
    return out


def context_terms(text):
    """從數值所在句子抽出關鍵術語，用於上下文比對。"""
    t = re.sub(r'[^A-Za-z ]', ' ', text)
    words = [w.lower() for w in t.split() if len(w) > 3]
    return set(words)


def value_with_context_found(val, unit, ctx_words, book_pages, scope):
    """數值 + 單位 + 上下文術語是否在同一原書頁面出現。

    必要性：'300 mL' 在原書 p.702 存在，但講的是咯血；
    若只看數值會誤判「300 mL（肋膈角變鈍）」為已驗證。
    """
    for p in sorted(scope):
        pt = book_pages[p]
        for m in NUM.finditer(pt):
            if abs(float(m.group(1)) - val) > 1e-9:
                continue
            if m.group(2).lower().rstrip('s') != unit:
                continue
            # 同一句 / 鄰近 300 字元內需有上下文術語
            window = pt[max(0, m.start() - 300):m.start() + 300]
            if ctx_words & context_terms(window):
                return p, ' '.join(window.split())[:180]
    return None, ''


def analyse_numbers(chapter, pages, secs):
    """比對網站數值與原書同主題數值"""
    rows = []
    topic_pages = {t: find_topic_pages(pages, t) for t in TOPICS}
    all_book_text = '\n'.join(pages.values())

    for s in secs:
        title = s['h3'] or s['h2']
        body = '\n'.join(l for _, l in s['lines'])
        topic = topic_of(title + ' ' + body)
        # 該主題在原書的頁
        cand_pages = topic_pages.get(topic, set())
        if not cand_pages:
            scope_text = all_book_text
            scope_label = 'all'
        else:
            scope_text = '\n'.join(pages[p] for p in sorted(cand_pages))
            scope_label = f'topic:{topic}({len(cand_pages)}p)'
        scope_nums = set()
        for _, v, u, _ in numbers_in(scope_text):
            scope_nums.add((round(v, 4), u))

        for ln_no, ln in s['lines']:
            # 上下文術語：行內英文 + 區塊英文標題（中文行的英文多在標題裡）
            title_en = title.split('/')[-1].strip()
            title_words = set(toks(title_en))
            for raw, v, u, ctx in numbers_in(ln):
                ctx_words = context_terms(ctx) | title_words
                key = (round(v, 4), u)
                # 1) 同主題頁內，數值+單位+上下文術語是否一致
                cp, ctext = value_with_context_found(v, u, ctx_words,
                                                      pages, cand_pages or set(pages))
                if cp is not None:
                    rows.append({
                        'chapter': chapter,
                        'finding_type': 'numeric_threshold',
                        'severity': 'LOW',
                        'verification_status': 'VERIFIED',
                        'source_file': f'content/docs/{chapter}/_index.md',
                        'source_line': ln_no,
                        'section': title[:90],
                        'subject': '',
                        'value': raw,
                        'context': ' '.join(ctx.split())[-110:],
                        'book_evidence': f'book p.{cp}: {ctext}',
                        'book_page': cp,
                        'note': '',
                    })
                    continue
                # 2) 僅數值+單位在同主題頁出現（上下文未對上）
                val_only = None
                for p in sorted(cand_pages or set(pages)):
                    for m in NUM.finditer(pages[p]):
                        if (abs(float(m.group(1)) - v) < 1e-9
                                and m.group(2).lower().rstrip('s') == u):
                            val_only = p
                            break
                    if val_only:
                        break
                if val_only:
                    status, sev = 'VERIFIED_ELSEWHERE', 'LOW'
                    ev = f'value+unit present on book p.{val_only}, context not matched'
                else:
                    anywhere = any(abs(vv - v) < 1e-9 and uu == u
                                   for _, vv, uu, _ in numbers_in(all_book_text))
                    if anywhere:
                        status, sev = 'VERIFIED_ELSEWHERE', 'LOW'
                        ev = 'value+unit present elsewhere in book (context not matched)'
                    else:
                        status, sev = 'UNVERIFIED', 'MEDIUM'
                        ev = (f'value+unit not found in {scope_label}; '
                              f'no matching value anywhere in book')
                rows.append({
                    'chapter': chapter,
                    'finding_type': 'numeric_threshold',
                    'severity': sev,
                    'verification_status': status,
                    'source_file': f'content/docs/{chapter}/_index.md',
                    'source_line': ln_no,
                    'section': title[:90],
                    'subject': '',
                    'value': raw,
                    'context': ' '.join(ctx.split())[-110:],
                    'book_evidence': ev,
                    'book_page': val_only if val_only else '',
                    'note': '',
                })
    return rows


def subject_key(lines_before, idx):
    """取該行所屬的「主體」：向前找最近的實體標籤。

    必要性（兩層）：
      1. 分級標籤：Stage I / Stage II ... 「Two-year survival: 95%」（Stage I）
         與「90%」（Stage II）數值不同但並非矛盾 —— 主體不同。
      2. 疾病實體：Wilms tumor 的 Stage I（95%）與 Neuroblastoma 的
         Stage I（75%）同樣不矛盾。若只抓分級標籤，會把不同疾病的同級
         誤判為衝突 —— 因此必須再往上找疾病名稱。

    做法：先找最近的疾病實體（粗體標題或 "Name (ABBR)" 型態），
    再在其範圍內找分級標籤，兩者合成主體鍵。
    """
    # --- 第一層：疾病實體 ---
    entity = ''
    for j in range(idx, max(-1, idx - 80), -1):
        s = lines_before[j].strip()
        if not s:
            continue
        # 粗體疾病名（項目符號或行內）： **Wilms tumor**
        m2 = re.match(r'^[•\-*]?\s*\*{1,2}([A-Z][^*\n]{2,40}(?:\s*\([A-Z]{2,5}\))?)\*{1,2}', s)
        if m2:
            entity = m2.group(1).strip().lower()[:40]
            break
        # "Name (ABBR)" 型態： Neuroblastoma / Wilms tumor (WT)
        m3 = re.match(r'^([A-Z][A-Za-z ]{2,28}(?:\s*\((?:[A-Z]{2,5})\))?)\s*$', s)
        if m3 and len(m3.group(1).split()) <= 5:
            entity = m3.group(1).strip().lower()[:40]
            break
        # 句首的疾病名（散文型）： "Wilms tumor is the most common ... "
        m4 = re.match(r'^([A-Z][A-Za-z ]{2,30}(?: tumor| disease| syndrome| carcinoma| '
                      r'sarcoma| cyst| stone| fracture| pneumonia| nephritis))\b', s)
        if m4:
            entity = m4.group(1).strip().lower()[:40]
            break
        # H3/H2 層級的章節標題
        if s.startswith('#'):
            entity = s.lstrip('# ').strip().lower()[:40]
            break

    # --- 第二層：分級標籤（限於同一實體範圍內）---
    stage = ''
    for j in range(idx, max(-1, idx - 12), -1):
        s = lines_before[j].strip()
        if not s:
            continue
        m = re.match(r'^(Stage\s+[IVX0-9]+[A-Z]?)\s*:', s)
        if m:
            stage = m.group(1).strip().lower()
            break
    if entity and stage:
        return f'{entity}@{stage}'
    return entity or stage


def analyse_contradictions(chapter, secs):
    """偵測章內矛盾：同一「主體 + 片語」出現不同數值。"""
    rows = []
    PHRASE = re.compile(r'([A-Za-z][A-Za-z \-/]{6,55}?)\s*[:：]?\s*'
                        r'(\d+(?:\.\d+)?)\s*(%|mm|cm|mL|days?|weeks?|years?)', re.I)
    seen = defaultdict(list)
    for s in secs:
        title = s['h3'] or s['h2']
        lines_before = [l for _, l in s['lines']]
        for k, (ln_no, ln) in enumerate(s['lines']):
            subj = subject_key(lines_before, k)
            for m in PHRASE.finditer(ln):
                ph = ' '.join(m.group(1).split()).lower()
                ph = re.sub(r'^(the|a|an|of|in|on|for|and|is|are|with|to|by)\s+', '', ph).strip()
                if len(ph) < 8:
                    continue
                seen[(subj, ph)].append((ln_no, title, m.group(0).strip(), m.group(2), m.group(3)))

    for (subj, ph), occ in seen.items():
        vals = set(f'{v}{u.lower()}' for _, _, _, v, u in occ)
        if len(vals) > 1 and len(occ) >= 2:
            for ln_no, title, raw, v, u in occ:
                others = [f'{vv}{uu.lower()}' for _, _, _, vv, uu in occ
                          if f'{vv}{uu.lower()}' != f'{v}{u.lower()}']
                rows.append({
                    'chapter': chapter,
                    'finding_type': 'internal_contradiction',
                    'severity': 'HIGH',
                    'verification_status': 'PROBABLE',
                    'source_file': f'content/docs/{chapter}/_index.md',
                    'source_line': ln_no,
                    'section': title[:90],
                    'subject': subj[:40],
                    'value': raw,
                    'context': ph[:110],
                    'book_evidence': 'conflicting values for same subject within one chapter',
                    'book_page': '',
                    'note': f'subject="{subj}" conflicts with: {", ".join(sorted(set(others)))}',
                })
    return rows


def main():
    chapters = sys.argv[1:] or ['thoracic', 'gi', 'genitourinary', 'neuro', 'msk',
                                 'ultrasound', 'nuclear', 'breast', 'cardiovascular',
                                 'interventional', 'pediatric', 'physics']
    all_rows = []
    for ch in chapters:
        pages = load_pages(ch)
        secs = site_sections(ch)
        r1 = analyse_numbers(ch, pages, secs)
        r2 = analyse_contradictions(ch, secs)
        all_rows.extend(r1); all_rows.extend(r2)
        nv = sum(1 for r in r1 if r['verification_status'] == 'VERIFIED_ELSEWHERE')
        print(f'{ch:16s} numeric_unverified={len(r1)-nv:4d} numeric_elsewhere={nv:4d} '
              f'contradictions={len(r2):3d}')
    out = f'{SITE}/docs/audit/content_findings_raw.csv'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cols = ['chapter', 'finding_type', 'severity', 'verification_status', 'source_file',
            'source_line', 'section', 'subject', 'value', 'context', 'book_evidence',
            'book_page', 'note']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(all_rows)
    print(f'\nwrote {out}  ({len(all_rows)} rows)')


if __name__ == '__main__':
    main()
