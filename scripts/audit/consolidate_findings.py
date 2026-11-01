#!/usr/bin/env python3
"""把各引擎的原始結果整合成 findings.csv（去重、分級、附建議）。

分級：
  CRITICAL 可能造成臨床危害的錯誤（錯誤影像識別、錯誤診斷標準）
  HIGH     遺失重要教學重點、數值/分類錯誤、內容矛盾
  MEDIUM   非必要遺漏、術語不一致、格式問題
  LOW      需人工覆核的線索或低影響差異

不變更網站內容；本腳本只產生報告。
"""
import csv, os, re, json, sys
from collections import defaultdict, Counter

SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
AUD = f'{SITE}/docs/audit'

# Phase 1 已人工確認的差異（沿用 PR #2 的編號與證據）
PHASE1 = [
    dict(id='F-01', chapter='thoracic', severity='HIGH', status='VERIFIED',
         type='image_misalignment',
         title='影像與其說明文字系統性錯位',
         location='content/docs/thoracic/_index.md',
         book='Ch.1 pp.1–86',
         evidence='44 個含影像區塊中 39 個（89%）的影像頁碼與其文字來源書頁相差 >3 頁；'
                  'page-022.png（書頁 13 Crazy paving）置於「左上葉肺膨脹不全」段落',
         proposed='依各區塊文字來源書頁重編檔名（書頁+9），逐張人工覆核後套用',
         auto_apply='NO'),
    dict(id='F-02', chapter='thoracic', severity='MEDIUM', status='VERIFIED',
         type='caption_separation',
         title='圖說與影像分離；影像清單編號全部重複為「圖1」',
         location='content/docs/thoracic/_index.md (## 圖片出處 / Image References)',
         book='Ch.1 pp.1–86',
         evidence='教科書 p.5 含完整 figure caption（影像描述、箭頭說明、Case courtesy）；'
                  '網站 alt 僅為「Page 022」，參考清單每項皆標為「圖1」',
         proposed='圖說置於圖下（改寫摘要而非逐字複製版權內容）；清單改連續編號並帶書頁碼',
         auto_apply='NO'),
    dict(id='F-03', chapter='thoracic', severity='HIGH', status='VERIFIED',
         type='contents_page_error',
         title='章節大綱頁碼混用兩套基準且順序與教科書相反',
         location='content/docs/thoracic/_index.md (章節開頭表格)',
         book='Ch.1 p.1 (Contents)',
         evidence='書頁 Introductory concepts 2 / Patterns of lung disease 8 / Mediastinum 65 / Pleura 83；'
                  '網站標 10–19 / 17–29 / 43–47 / 83–89',
         proposed='全表改用教科書書頁碼，並依 p.1 Contents 的 11 節順序重排',
         auto_apply='NO'),
    dict(id='F-04', chapter='thoracic;cardiovascular;pediatric', severity='HIGH', status='VERIFIED',
         type='mixed_source',
         title='15 處內容源自 Learning Radiology (Herring) 而非本教科書',
         location='content/docs/{thoracic,cardiovascular,pediatric}/_index.md',
         book='不適用',
         evidence='明確出處標註 **Source: Learning Radiology, Chapter N (William Herring, MD, FACR)**',
         proposed='由使用者決定：標示為補充教材並分區 / 改寫為依本教科書 / 移除',
         auto_apply='NO'),
    dict(id='F-05', chapter='thoracic', severity='HIGH', status='VERIFIED',
         type='internal_contradiction',
         title='圓形肺炎病原菌兩處說法互相矛盾',
         location='content/docs/thoracic/_index.md:1313 與 :5372',
         book='Ch.1 p.21',
         evidence='書頁：Round pneumonia ... seen only in children, most commonly due to Streptococcus '
                  'pneumoniae；網站 5372 行版另列「流感嗜血桿菌」',
         proposed='以教科書版為準統一；屬臨床內容，不得靜默修改',
         auto_apply='NO'),
    dict(id='F-06', chapter='thoracic', severity='CRITICAL', status='PROBABLE',
         type='wrong_image_identification',
         title='錯誤影像識別：Crazy paving 示範圖置於左上葉肺膨脹不全段落',
         location='content/docs/thoracic/_index.md:22 (區塊 左上葉肺膨脹不全)',
         book='Ch.1 p.13 (Crazy paving) 與 p.5 (Left upper lobe atelectasis)',
         evidence='view_image 辨識 page-022.png 頁首標題「Crazy paving」、頁腳頁碼 13',
         proposed='依 F-01 對照表重編；全章 86 張逐張視覺覆核',
         auto_apply='NO'),
    dict(id='F-07', chapter='cardiovascular', severity='MEDIUM', status='VERIFIED',
         type='duplicate_image_file',
         title='page-703.png 同時存在於 cardiovascular 與 interventional 目錄',
         location='static/images/cardiovascular/page-703.png, static/images/interventional/page-703.png',
         book='Ch.10 p.694 (Interventional 起頁)',
         evidence='書頁 694 頁首為「10 Interventional radiology」；cardiovascular 章節範圍為 658–693',
         proposed='確認心血管章是否需引用；否則移除 cardiovascular 目錄中的該檔',
         auto_apply='NO'),
    dict(id='F-08', chapter='all', severity='LOW', status='VERIFIED',
         type='formatting',
         title='影像參考清單編號未遞增（全部標為「圖1」）',
         location='content/docs/*/_index.md (## 圖片出處)',
         book='不適用',
         evidence='每個檔案的連結標題皆為 `圖1：page-0NN.png`',
         proposed='改為 `圖 N（書頁 M）：page-0NN.png` 並連結至正文錨點',
         auto_apply='NO'),
    dict(id='F-09', chapter='thoracic;cardiovascular;pediatric', severity='MEDIUM', status='UNVERIFIED',
         type='unsourced_clinical_advice',
         title='網站原創臨床建議無教科書出處',
         location='content/docs/*/_index.md',
         book='不適用',
         evidence='例如「Subsegmental atelectasis ... does not require antibiotics in isolation」、'
                  '「Swan-Ganz tip 應置於 main pulmonary artery 內」——教科書無對應段落',
         proposed='逐項標註來源或標為「網站補充，非本教科書內容」；需使用者核准',
         auto_apply='NO'),
]


def load_raw():
    p = f'{AUD}/content_findings_raw.csv'
    if not os.path.exists(p):
        return []
    return list(csv.DictReader(open(p)))


def load_images():
    p = f'{AUD}/image_mapping.csv'
    if not os.path.exists(p):
        return []
    return list(csv.DictReader(open(p)))


def main():
    rows = []
    # --- Phase 1 人工確認項 ---
    for f in PHASE1:
        rows.append({
            'finding_id': f['id'],
            'chapter': f['chapter'],
            'severity': f['severity'],
            'finding_type': f['type'],
            'verification_status': f['status'],
            'source_file': f['location'],
            'source_line': '',
            'section': f['title'],
            'value': '',
            'book_page': f['book'],
            'evidence': f['evidence'],
            'proposed_correction': f['proposed'],
            'auto_applicable': f['auto_apply'],
            'requires_human_review': 'YES',
        })

    # --- 數值門檻（去重：同章 + 同值 + 同 section）---
    seen = set()
    for r in load_raw():
        if r['verification_status'] != 'UNVERIFIED':
            continue
        key = (r['chapter'], r['value'], r['section'])
        if key in seen:
            continue
        seen.add(key)
        rows.append({
            'finding_id': f"N-{len(seen):03d}",
            'chapter': r['chapter'],
            'severity': 'MEDIUM',
            'finding_type': 'numeric_threshold_not_in_book',
            'verification_status': 'UNVERIFIED',
            'source_file': r['source_file'],
            'source_line': r['source_line'],
            'section': r['section'][:90],
            'value': r['value'],
            'book_page': '',
            'evidence': f"{r['book_evidence']} | site context: {r['context'][:80]}",
            'proposed_correction': '人工比對原書同主題段落後決定：補上出處或修正數值',
            'auto_applicable': 'NO',
            'requires_human_review': 'YES',
        })

    # --- 影像錯位（每章彙整成一筆，含統計）---
    imgs = load_images()
    bych = defaultdict(list)
    for r in imgs:
        bych[r['chapter']].append(r)
    for ch, lst in sorted(bych.items()):
        prob = [r for r in lst if r['verification_status'] == 'PROBABLE']
        unver = [r for r in lst if r['verification_status'] == 'UNVERIFIED']
        if not prob and not unver:
            continue
        sev = 'HIGH' if prob else 'MEDIUM'
        rows.append({
            'finding_id': f'IMG-{ch.upper()[:4]}',
            'chapter': ch,
            'severity': sev,
            'finding_type': 'image_section_misalignment',
            'verification_status': 'PROBABLE' if prob else 'UNVERIFIED',
            'source_file': f'content/docs/{ch}/_index.md',
            'source_line': ';'.join(str(r['source_line']) for r in (prob + unver)[:12]),
            'section': f'{len(lst)} 張含影像區塊',
            'value': '',
            'book_page': '',
            'evidence': (f'PROBABLE 錯位 {len(prob)} 張、UNVERIFIED {len(unver)} 張、'
                         f'VERIFIED {len([r for r in lst if r["verification_status"]=="VERIFIED"])} 張；'
                         f'對齊方法見 docs/audit/README.md。例：'
                         + (prob[0]['evidence'][:150] if prob else unver[0]['evidence'][:150])),
            'proposed_correction': '依 image_mapping.csv 的 proposed_image 逐張人工覆核後套用；不得批次改名',
            'auto_applicable': 'NO',
            'requires_human_review': 'YES',
        })

    # --- 非原書來源 ---
    p = f'{AUD}/other_sources.csv'
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            rows.append({
                'finding_id': f'LS-{r["chapter"][:4].upper()}-{r["source_line"]}',
                'chapter': r['chapter'],
                'severity': 'MEDIUM',
                'finding_type': 'non_textbook_source',
                'verification_status': 'PROBABLE',
                'source_file': r['source_file'],
                'source_line': r['source_line'],
                'section': (r['section_h3'] or r['section_h2'])[:90],
                'value': '',
                'book_page': '',
                'evidence': r['attribution'][:200],
                'proposed_correction': '分類為 A/B/C/D 並標示；內容暫時保留，不得刪除或靜默改寫',
                'auto_applicable': 'NO',
                'requires_human_review': 'YES',
            })

    out = f'{AUD}/findings.csv'
    os.makedirs(AUD, exist_ok=True)
    cols = ['finding_id', 'chapter', 'severity', 'finding_type', 'verification_status',
            'source_file', 'source_line', 'section', 'value', 'book_page', 'evidence',
            'proposed_correction', 'auto_applicable', 'requires_human_review']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f'wrote {out}  ({len(rows)} findings)')
    print('severity:', dict(Counter(r['severity'] for r in rows)))
    print('status :', dict(Counter(r['verification_status'] for r in rows)))
    print('type   :', dict(Counter(r['finding_type'] for r in rows)))


if __name__ == '__main__':
    main()
