# 數值 flag 重新驗證（2026-11-25 每週任務）

對象：`docs/audit/findings.csv` 中 59 筆 `numeric_threshold_not_in_book`（N-001 – N-059，狀態原為 UNVERIFIED）。
基準：`main` @ `4a18d3f`。原書來源：Google Drive 各章 PDF 的文字層。
明細：[`numeric_reverification_2026-11-25.csv`](numeric_reverification_2026-11-25.csv)

本次**沒有修改任何網站醫學內容**，只更新稽核紀錄。

## 為什麼要重驗

舊稽核的比對程式有三個系統性誤判來源：

1. **單位寫法不同**：書寫 `minutes`、`mg/dl`、`three days`，網站寫 `min`、`mg/dL`、`3 days`，因此被判為「書中找不到」。
2. **範圍被截斷解析**：例如 `15–30 mmHg` 被拆成 `15 mm`，`eGFR 30–45 ml/min` 被拆成 `45 ml`，`20 mL/s 共 30 mL` 被拆成 `30 mL`。
3. **內容已更動**：PR #3 和 Learning Radiology 段落清理之後，許多被 flag 的段落已經不存在。

## 結果

| 新狀態 | 筆數 | 意義 |
|---|---|---|
| VERIFIED_IN_BOOK | 20 | 原書有此數值，網站忠實 → 可關閉 |
| STALE | 28 | 該數值或段落已不在目前的 main → 可關閉 |
| NOT_IN_BOOK | 5 | 章節文字完整可查，但原書沒有此數值 → 需人工決定 |
| MISMATCH | 1 | 網站數值與原書敘述不符 → 需人工決定 |
| INCONCLUSIVE | 5 | 該頁超出可取得的文字範圍 → 下次補查 |

## 需要人工決定的項目（未自動修改）

| ID | 章節 / 位置 | 網站內容 | 原書 | 分類 |
|---|---|---|---|---|
| N-041 | cardiovascular `_index.md` L330 | 「約 5% 鈍性主動脈創傷患者存活」 | "In the small percentage of patients who survive blunt aortic trauma, injury occurs at the isthmus in 95% of cases." 書中沒有 5% 這個數字 | site-conversion |
| N-002 | thoracic L1899 | NSCLC 85% / SCLC 15% | pp.1–80（含 lung cancer 段落）沒有這個比例 | site-conversion（網站補充） |
| N-005, N-006 | thoracic L3111, L3151 | AIP organizing phase "After 1 week" | p.54 只說 early (exudative) 與 chronic (organizing) 兩期，沒有時間界線 | site-conversion（網站補充） |
| N-038 | nuclear L378 | HIDA "small bowel by 30–60 min" | 書只寫 "Tracer should be seen in the small bowel to ensure a patent CBD"；唯一時間來自病例圖（25 min）。Liver 5 min / GB 15 min 有出處 | site-conversion（網站補充） |
| N-052 | interventional L63, L65 | Persistent left SVC 盛行率 0.3–0.5% | 書有胚胎學與引流說明，但沒有盛行率 | site-conversion（網站補充） |

建議處理方式由使用者決定：改回書中敘述、標註「網站補充，非本教科書內容」，或刪除。

## 順帶發現

- **physics L305（source-book）**：書中 magnification mammography 寫 "25 mA current, 3 second exposure, 70 mAs"，但 25 × 3 = 75 mAs。這是原書內部的不一致，網站照書轉錄，屬忠實轉錄，**不建議修改**，可考慮加註。
- **physics L305（site-conversion，minor）**：書寫 "A typical AGD is ~1.8–1.5 mGy per view per breast"，網站只寫「典型值約 1.5 mGy」，範圍被縮成單一數值。

## 未完成 / 限制

- Drive 的文字表示對大檔會截斷：thoracic 到 p.80/86、MSK 到 p.425/463、neuro 到 p.280/345、ultrasound 到 p.543/552、pediatric 到 p.820/837。INCONCLUSIVE 的 5 筆都落在截斷之後，需要用完整 PDF（`pdftotext`）補查。
- STALE 僅確認該數值已不在原段落或原章節；沒有重新稽核改寫後的新段落。

## 章節轉檔狀態

12 章（Ch 1–12）都已轉成網站內容，`data/image_index.json` 每一頁都有對應的影像與段落，沒有「尚未轉檔」的章節。之後的每週任務建議改成**逐章 fidelity 稽核**。下一個建議目標：**Ch 9 Cardiovascular 全章數值比對**（PDF 小、文字層完整、且有 N-041）。
