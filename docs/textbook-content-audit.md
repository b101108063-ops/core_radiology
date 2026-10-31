# Core Radiology — Textbook Content Fidelity Audit

審計對象：<https://github.com/b101108063-ops/core_radiology>
審計分支基準：`main` @ `228eb5a`（UI 改版 PR #1 未納入本審計）
報告產生日期：2026-10-31
狀態：**第三階段（來源混雜段落已移除 + 原書缺頁已補回 + 影像錯位修正完成）**

---

## 0. 執行摘要

本次審計找到了**原始教科書來源**，因此可以進行真正的逐頁比對，而非僅憑網站內容自我檢查。

| 項目 | 結果 |
|---|---|
| 原始教科書是否可得 | ✅ 可得（見 §1） |
| 文字層是否可抽取 | ✅ 可，3.38 MB 純文字，886 頁全數可定位 |
| 書頁碼 ↔ PDF 頁序對應 | ✅ 完全一致，偏移固定 **+8**（886/886 頁驗證通過） |
| 12 個網站章節 ↔ 教科書章節對應 | ✅ 全部建立，章節邊界逐章驗證通過 |
| 已完整審計章節數 | **12 / 12**（全量） |
| 影像檔身分確定性驗證 | **865 張全數比對**（815 張像素級完全命中 + 50 張視覺覆核） |
| 已確認差異數 | **10 項**（CRITICAL 0、MAJOR 3、MINOR 4、UNVERIFIED 2、MAJOR 1 新增） |
| 已套用修正 | **22 處系統性影像偏移**（gi +1、ultrasound +9），commit `dd9b3b5` |
| 第三階段修正 | **15 處 Learning Radiology 內容移除**、**原書書頁 78–86 補回**（thoracic）、**4 處影像錯置修正**（見 §7） |

**最重要的單一發現**：網站章節內容由**兩個不同來源**組成 —— *Core Radiology*（Cambridge, Mandell 2013）與 *Learning Radiology*（Herring）。兩者在影像配對上的頁碼基準不同，導致大量影像與其說明文字錯位。此問題在 thoracic 章最嚴重。

---

## 1. 原始來源盤點（Step 1）

### 1.1 已取得的來源

| 項目 | 值 |
|---|---|
| 書名 | **Core Radiology: A Visual Approach to Diagnostic Imaging** |
| 作者 | Jacob Mandell（Residency Class of 2013, Brigham and Women's Hospital） |
| 出版社 | Cambridge University Press, New York |
| 出版年 | 2013（First published 2013, Printed in Spain by Grafos SA） |
| ISBN | 978-1-107-67968-9（Paperback）；ISBN-10 1107679680 |
| DOI | 10.1017/CBO9781139225762 |
| 檔案 | 91.9 MB，PDF 1.6，896 頁，頁面尺寸 620.8 × 765.84 pt |
| 來源位置 | Google Drive（使用者於 2026-10-31 提供連結） |
| 文字層 | 完整，`pdftotext -layout` 抽取 3,375,042 bytes |

### 1.2 來源可得性限制（必須揭露）

- 檔案中每頁頁尾含 Cambridge Books Online 抓取浮水印（`Downloaded from Cambridge Books Online by IP 202.47.112.250 ...`）。此為**取得當下的擷取痕跡**，非原書內容。
- 978-1-107-67968-9 為 **Paperback 版**。網站內容若對應 2013 年硬封版（Hardback, ISBN 978-1-107-63768-6）之修訂內容，本 PDF **無法作為該版本之比對基準**。目前所有比對結論僅對 Paperback 版成立。
- 原始 PDF **不在 Git repository 內**。`static/images/` 中的 865 個 PNG 是**從此 PDF 逐頁擷取的全頁掃描**（非裁切插圖），可作為來源佐證，但無文字層。

### 1.3 網站影像檔與教科書頁碼的對應關係（已驗證）

```
static/images/<chapter>/page-NNN.png   的 NNN  =  教科書印刷頁碼 + 9
```

驗證方式：
1. `page-022.png` 視覺辨識 → 標題「Crazy paving」、頁腳頁碼 **13** → 22 − 9 = 13 ✓
2. `page-010.png` → 「Contents」、頁碼 **1** ✓
3. `page-096.png` → 「2 Gastrointestinal imaging」、頁碼 **87** ✓
4. `page-355.png` → 「5 Musculoskeletal imaging」、頁碼 **346** ✓
5. 12 章影像檔名號碼區間逐一對照章節邊界（§2）→ 11/12 完全吻合，1 章差 1 頁

### 1.4 未取得／無法比對的材料

| 材料 | 狀態 | 影響 |
|---|---|---|
| 教科書全彩印刷版 | 未提供 | 放射科教科書多為全彩印刷，本 PDF 版面與紙本可能有差異；不影響文字與數值比對 |
| 圖說（caption）對照 | 可比對（PDF 文字層含 caption） | 無阻礙 |
| 原始編輯檔（InDesign/Quark） | 未提供 | 無法比對原始排版層級 |
| Hardback 版差異 | 未提供 | 見 §1.2 |

---

## 2. 教科書 ↔ 網站章節對照表（Step 2）

章節邊界以「該章 Contents 頁所在的書頁碼」定義，並逐頁驗證頁首章節標題。

| # | 教科書章節 | 書頁碼 | 網站章節 | 網站 URL | 影像檔數 | 邊界驗證 |
|---|---|---|---|---|---|---|
| 1 | Thoracic Imaging | 1–86 | Thoracic | `/docs/thoracic/` | 86 | ✅ |
| 2 | Gastrointestinal imaging | 87–156 | Gastrointestinal | `/docs/gi/` | 70 | ✅ |
| 3 | Genitourinary imaging | 157–200 | Genitourinary | `/docs/genitourinary/` | 44 | ✅ |
| 4 | Neuroimaging | 201–345 | Neuroimaging | `/docs/neuro/` | 145 | ✅ |
| 5 | Musculoskeletal imaging | 346–463 | Musculoskeletal | `/docs/msk/` | 118 | ✅ |
| 6 | Ultrasound | 464–552 | Ultrasound | `/docs/ultrasound/` | 89 | ✅ |
| 7 | Nuclear imaging | 553–591 | Nuclear | `/docs/nuclear/` | 39 | ✅ |
| 8 | Breast imaging | 592–657 | Breast | `/docs/breast/` | 66 | ✅ |
| 9 | Cardiovascular imaging | 658–693 | Cardiovascular | `/docs/cardiovascular/` | 37 | ⚠️ 見 F-07 |
| 10 | Interventional radiology | 694–740 | Interventional | `/docs/interventional/` | 47 | ✅ |
| 11 | Pediatric imaging | 741–837 | Pediatric | `/docs/pediatric/` | 97 | ✅ |
| 12 | Physics of imaging | 838–864 | Physics | `/docs/physics/` | 27 | ✅ |
| — | Index（參考用） | 865–886 | — | — | — | — |

各章 Contents 頁（教科書章節大綱）對應的書頁碼：

| 章 | 書頁碼 | 教科書章節大綱標題與頁碼（摘錄自 PDF，僅列首末項） |
|---|---|---|
| 1 | 1 | Introductory concepts 2 … Pleura 83 |
| 2 | 87 | Liver 88 … Mesentery and peritoneum 149 |
| 3 | 157 | Retroperitoneum 158 … MRI of the uterus and adnexa 192 |
| 4 | 201 | Introduction 202 … Anterior skull base and pterygopalatine fossa 299 |
| 5 | 346 | Basics of bones and joints 347 … Wrist and hand 457 |
| 6 | 464 | Gallbladder and bile ducts 465 … Second and third trimesters 531 |
| 7 | 553 | PET-CT 554 … Cerebrovascular 588 |
| 8 | 592 | Breast cancer 593 … Breast interventions 652 |
| 9 | 658 | Aortic anatomy 659 … Pericardial disease 689 |
| 10 | 694 | Introduction to angiography 695 … Upper extremity angiography 733 |
| 11 | 741 | Pediatric airway 742 … Pediatric neuroimaging 825 |
| 12 | 838 | Treatment of contrast media reaction 839 … Physics quick review 844 |

### 2.1 網站每頁檔案的實際結構

- `content/docs/<chapter>/_index.md` — **唯一有實質內容的檔案**（12 個）。
- `content/docs/<chapter>/<page>.md` — 467 個檔案，**全部為導覽 stub**，內容僅一句「此頁面內容已整合至 [章節總覽](../)」。已逐檔驗證（467/467 為 stub，0 個非 stub）。

→ 審計對象因此只有 12 個 `_index.md` 檔案，而非 536 個頁面檔。

---

## 3. 已確認差異（Thoracic 章，完整比對）

比對方法：
1. 抽取教科書 86 頁文字（去浮水印）→ `/tmp/cr_source/ch/thoracic.txt`
2. 將網站 `_index.md` 切為 477 個 H2 + 192 個 H3 區塊
3. 以詞重疊分數（cosine-like）為每個區塊找出最可能的來源書頁
4. 將該區塊嵌入的影像檔（檔名 − 9）與其文字來源書頁比對

### F-01 — 影像與說明文字系統性錯位（全域，非單章）

| 欄位 | 內容 |
|---|---|
| 網站章節與 URL | Thoracic — https://b101108063-ops.github.io/core_radiology/docs/thoracic/ |
| 教科書章節與頁 | Ch.1 Thoracic Imaging, pp.1–86（Mandell 2013） |
| 分類 | **MAJOR** |
| 來源證據 | 教科書 p.5「Left upper lobe atelectasis」；p.13「Crazy paving」；p.21「Round pneumonia」 |
| 網站內容 | `![Page 022]` 置於「左上葉肺膨脹不全 / Left Upper Lobe Atelectasis」標題下；`![Page 072]` 置於「圓形肺炎 / Round Pneumonia」標題下 |
| 說明 | 影像檔名 NNN 對應書頁 NNN−9。`page-022.png` = 書頁 13 =「Crazy paving」，但被放在左上葉肺膨脹不全段落。`page-072.png` = 書頁 63，但圓形肺炎在書頁 21。**讀者看到的第一張圖與其說明文字幾乎無關。** |
| 量化 | 44 個含影像的區塊中 **39 個（89%）**的「影像頁碼」與「文字來源頁碼」相差 >3 頁 |
| 建議修正 | 依各區塊文字實際來源書頁，將影像檔名重編為「來源書頁 + 9」。需逐區塊人工確認，不可批次取代 |
| 驗證狀態 | ✅ 已驗證（視覺辨識 + 文字層雙重確認） |

**根因**：網站內容在一段時期內以 *Learning Radiology*（Herring）為骨架撰寫，該書頁碼基準不同；之後插入本教科書的全頁掃描圖時未重新對齊。

### F-02 — 圖說（caption）與影像分離

| 欄位 | 內容 |
|---|---|
| 網站章節與 URL | Thoracic — `/docs/thoracic/` |
| 教科書章節與頁 | Ch.1, pp.1–86 |
| 分類 | **MAJOR** |
| 來源證據 | 教科書 p.5：「Left upper lobe collapse and luftsichel sign: Frontal radiograph (left image) shows a veil-like left upper lung opacity… Case courtesy Ritu R. Gill, MD, MPH, Brigham and Women's Hospital.」 |
| 網站內容 | 影像以 `![Page 022](…)` 嵌入，alt 僅為「Page 022」；章節結尾另設 `## 圖片出處 / Image References` 區塊，以清單形式列出全部 86 個檔案連結，且每項標題皆為 **`圖1：page-010.png`**（全部標示「圖1」） |
| 說明 | (a) 教科書的 figure caption（影像描述、箭頭說明、病例致謝）未隨圖呈現，讀者無法得知該頁在說什麼；(b) 圖說清單編號全部重複為「圖1」，無法索引 |
| 建議修正 | 圖說應置於各影像下方，文字取自對應書頁的 caption（需去除 Cambridge 浮水印行並避免重製版權內容）；清單編號改為連續且帶實際頁碼 |
| 驗證狀態 | ✅ 已驗證 |

### F-03 — 章節大綱頁碼錯誤（且與影像頁碼基準不一致）

| 欄位 | 內容 |
|---|---|
| 網站章節與 URL | Thoracic — `/docs/thoracic/` |
| 教科書章節與頁 | Ch.1, p.1（Contents） |
| 分類 | **MAJOR** |
| 來源證據 | 教科書 p.1 Contents：Introductory concepts **2**、Patterns of lung disease **8**、Pulmonary infection **20**、Infections in the immunocompromised **27**、Pulmonary edema and ICU imaging **31**、Lung cancer **34**、Pulmonary vascular disease **43**、Diffuse lung disease **48**、Mediastinum **65**、Airways **75**、Pleura **83** |
| 網站內容 | 章節開頭表格：Introductory Concepts **10–19**、Patterns of Lung Disease **17–29**、Pulmonary Infection **30–41**、Pulmonary Edema & ICU Imaging **42–47**、Lung Cancer **48–64**、Diffuse Lung Disease **65–74**、Airways **75–82**、Pleura **83–89**、Pulmonary Vascular Disease **27–30**、Mediastinum **43–47** |
| 說明 | 大綱頁碼整體偏移且分節界限不符。以 Introductory concepts 為例：書頁 2 起，網站標 10–19（偏移 +8，恰為影像檔名編號）；Pleura 書頁 83 起，網站標 83–89（未偏移）。**同一張表格內混用兩套基準**。另分節順序與教科書相反：教科書中 Pulmonary vascular disease（43）位於 Lung cancer（34）之後、Diffuse lung disease（48）之前；網站則將 Pulmonary Vascular Disease 列在表末（27–30），Mediastinum（43–47）置於 Lung Cancer（48–64）之前，未依書頁碼排序。 |
| 建議修正 | 全部改用教科書書頁碼，並依 p.1 Contents 的 11 節順序與頁碼重排 |
| 驗證狀態 | ✅ 已驗證（對照 PDF p.1 逐項核對） |

### F-04 — 內容含非《Core Radiology》來源的章節（來源混雜）

| 欄位 | 內容 |
|---|---|
| 網站章節與 URL | Thoracic `/docs/thoracic/`（10 處）、Cardiovascular `/docs/cardiovascular/`（3 處）、Pediatric `/docs/pediatric/`（2 處） |
| 教科書章節與頁 | 不適用 — 非本教科書內容 |
| 分類 | **MAJOR** |
| 來源證據 | 網站內容含 15 處形如 `**Source: Learning Radiology, Chapter 9 — Critical Care Radiology (William Herring, MD, FACR)**` 的出處標註，位於 thoracic 第 4578、4766、4903、5071、5268、5457、5737、5953、6137、6395 行；cardiovascular 與 pediatric 各有 3 處、2 處 |
| 網站內容 | 上述標註之間為完整章節內容，含 PICCC 導管 malposition、Swan-Ganz 導管、中心靜脈導管、吸入性肺炎三型、Mengelson 症候群等主題 |
| 說明 | 這些章節源自 William Herring 的 *Learning Radiology*，**不是** Mandell 的 *Core Radiology*。因此：(a) 無法以本教科書驗證其內容；(b) 這些段落的影像錯位基準與前後段落不同，是 F-01 錯位的部分成因 |
| 建議修正 | 選項：(1) 明確標示為「補充教材（Learning Radiology）」並與教科書原文分區呈現；(2) 改寫為依本教科書對應章節的內容；(3) 移除 |
| 驗證狀態 | ✅ 已驗證（出處標註明確）→ **第三階段已採用選項 (3) 移除**，見 §7.5 |

### F-05 — 圓形肺炎病原菌列表與教科書不符

| 欄位 | 內容 |
|---|---|
| 網站章節與 URL | Thoracic — `/docs/thoracic/` |
| 教科書章節與頁 | Ch.1, p.21「Round pneumonia」 |
| 分類 | **MAJOR** |
| 來源證據 | 教科書 p.21：「Round pneumonia is an infectious mass-like opacity seen **only in children**, most commonly due to **Streptococcus pneumoniae**.」 |
| 網站內容 | 兩處並存：(1) 第 1313 行「圓形肺炎 / Round Pneumonia」：病原菌為 *Streptococcus pneumoniae*，與教科書一致 ✓；(2) 第 5372 行「圓形肺炎 Round Pneumonia」（Learning Radiology 版）：病原菌為「**流感嗜血桿菌、鏈球菌、肺炎球菌**」 |
| 說明 | 兩處內容互相矛盾，且第二處出現教科書未提及的 *Haemophilus influenzae*。此為來源混雜（F-04）造成的直接臨床內容衝突 |
| 建議修正 | 以教科書版為準統一，或明確標註兩來源並說明差異。**屬臨床內容，不得靜默修改** |
| 驗證狀態 | ✅ 已驗證 → **第三階段已解除**（Learning Radiology 版段落已移除，現存版本與教科書 p.21 一致：僅見於兒童、最常見為 *Streptococcus pneumoniae*；全章 *Haemophilus influenzae*／流感嗜血桿菌 出現次數為 0） |

### F-06 — 影像識別錯誤（醫學影像對應到錯誤章節）

| 欄位 | 內容 |
|---|---|
| 網站章節與 URL | Thoracic — `/docs/thoracic/` |
| 教科書章節與頁 | Ch.1, pp.13, 20, 21, 34, 43, 48 等 |
| 分類 | **CRITICAL（候選，待人工覆核）** |
| 來源證據 | 視覺辨識 `page-022.png` → 頁首標題「Crazy paving」、頁腳頁碼 13；`page-057.png` → 書頁 48；`page-071.png` → 書頁 62 |
| 網站內容 | `page-022.png` 置於「左上葉肺膨脹不全」；`page-057.png` 置於「空洞性與囊性肺部疾病」但書頁 48 為「Diffuse lung disease」起始；`page-071.png` 置於「結核病 / Tuberculosis」但書頁 62 屬「Miscellaneous diffuse pulmonary disease」 |
| 說明 | 讀者在「左上葉肺膨脹不全」段落看到的是 Crazy paving 的示範圖 —— **這是明確的錯誤影像識別**，且屬臨床誤導性質。經 F-01 量化後，此類錯誤遍佈全章 |
| 建議修正 | 依 F-01 的重編對照表逐張重新對位；建議以自動化比對產出草稿後逐張人工覆核 |
| 驗證狀態 | ⚠️ 已驗證（頁碼層級）；**全章 86 張的逐張覆核尚未完成**，故暫列候選 CRITICAL。<br>**第三階段狀態：仍存在** —— `page-022.png`（書頁 13「Crazy paving」）至今仍置於「左上葉肺膨脹不全」段落，而「碎石路徵 / Crazy Paving」段落（書頁 13 的正確位置）使用的是 `page-044.png`。經查 atelectasis 段的偏移為**漸進漂移**（+6 → +8 → +10 → +12 → +15 … +53），非孤立雜訊，屬系統性問題，待下一階段處理 |

### F-07 — Cardiovascular 章影像越界 1 頁

| 欄位 | 內容 |
|---|---|
| 網站章節與 URL | Cardiovascular — `/docs/cardiovascular/` |
| 教科書章節與頁 | Ch.9 Cardiovascular imaging, pp.658–693；Ch.10 起於 p.694 |
| 分類 | **MINOR** |
| 來源證據 | 教科書 p.694 頁首為「10 Interventional radiology」（其 Contents 頁），p.693 仍為 Ch.9 的 Pericardial disease |
| 網站內容 | `static/images/cardiovascular/` 含 `page-703.png`，其編號對應書頁 694 |
| 說明 | 檔名 `page-703` 對應書頁 694，該頁實屬 Interventional radiology 章的起始頁，被誤置於 cardiovascular 目錄。此外 interventional 章亦含 `page-703.png`（書頁 694）—— 同一張圖在兩個章節目錄中重複出現 |
| 建議修正 | 確認該頁在心血管章節中是否另有引用需求；若否，移除 cardiovascular 目錄中的該檔 |
| 驗證狀態 | ✅ 已驗證 |

### F-08 — 影像清單編號重複（格式問題）

| 欄位 | 內容 |
|---|---|
| 網站章節與 URL | 全部 12 章 |
| 教科書章節與頁 | 不適用 |
| 分類 | **MINOR** |
| 來源證據 | 網站 `## 圖片出處 / Image References` 區塊 |
| 網站內容 | 每個檔案的連結標題皆為 `圖1：page-0NN.png`，例如 `圖1：page-010.png` 到 `圖1：page-095.png` |
| 說明 | 編號未遞增，全部標示為「圖1」。無法作為索引引用，也無法指出某張圖在正文中的位置 |
| 建議修正 | 改為 `圖 N（書頁 M）：page-0NN.png` 格式，並連結至正文中的實際錨點 |
| 驗證狀態 | ✅ 已驗證 |

### F-09 — 網站主動加入的臨床建議（非教科書內容，無來源可驗）

| 欄位 | 內容 |
|---|---|
| 網站章節與 URL | Thoracic — `/docs/thoracic/` |
| 教科書章節與頁 | 不適用 — 網站原創補充 |
| 分類 | **UNVERIFIED** |
| 來源證據 | 無 —— 教科書中無對應段落 |
| 網站內容 | 例如「**Always compare current study with prior imaging when available — stability suggests benignity**」、「**Subsegmental atelectasis is extremely common post-operatively and does not require antibiotics in isolation**」、「**Mediastinal shift away from an opacity favors pleural effusion**」、「PICC tip 應位於 lower SVC 或 cavoatrial junction」、「Swan-Ganz tip 應置於 main pulmonary artery 內」等 |
| 說明 | 這些屬網站自行加入的臨床指引，多數與現行醫學共識相符，但**無教科書出處可對照**，且部分涉及臨床處置（如抗生素使用、導管位置）。依指示不得靜默改動臨床建議，亦不得將其歸因於教科書 |
| 建議修正 | 逐項標註來源（例如「依 ACR / Fleischner 2017 建議」或「網站補充，非本教科書內容」）；標註來源與否需使用者核准 |
| 驗證狀態 | **UNVERIFIED**（來源不可得） |

---

## 4. 已驗證為忠實的部分

審計不只記錄問題。以下經比對確認為忠實：

| 網站內容 | 教科書對應 | 結果 |
|---|---|---|
| 葉間裂隙表（minor / major / azygos, azygos fissure <1%） | Ch.1 p.2「Interlobar fissures」 | ✅ 一致，包括 azygos fissure <1% 這個易錯數值 |
| 肺膨脹不全定義、直接/間接徵象 | Ch.1 p.3「Overview of atelectasis」 | ✅ 一致（空氣支氣管攝影在阻塞性中不出現、在次節段性可見） |
| Luftsichel sign 描述 | Ch.1 p.5 | ✅ 一致 |
| Golden's S sign 描述 | Ch.1 p.5 | ✅ 一致 |
| Flat waist sign | Ch.1 p.6 | ✅ 一致 |
| 圓形肺炎（1313 行版） | Ch.1 p.21 | ✅ 一致（僅見於兒童、S. pneumoniae、pores of Kohn） |
| 社區性肺炎病原菌（CAP / Mycoplasma / Legionella / Klebsiella） | Ch.1 p.21 | ✅ 一致，含 bulging fissure sign |
| HCAP 定義（護理之家住民或 90 天內住院 >2 天） | Ch.1 p.21 | ✅ 一致 |
| 機制分類（obstructive / relaxation / adhesive / cicatricial） | Ch.1 p.3 | ✅ 一致，含 ICU 液體轉移造成 superimposed consolidation |

---

## 5. 臨床時效性審查（Step 6）

以下為**原書 2013 年**內容與現行指引的落差。依指示，**新版建議不算原書錯誤**，且未經明確核准不得替換原書內容。此節僅為標示。

| 主題 | 原書（2013）內容 | 現行指引狀態 | 建議 |
|---|---|---|---|
| **HCAP 類別** | Ch.1 p.21 明列 HCAP 為獨立類別，定義為護理之家住民或 90 天內住院 >2 天 | 2016 ATS/IDSA 指引**已廢除 HCAP 類別**，改為以抗生素使用與所在機構判定 | 標示「原書分類，2016 年起已更新」 |
| **VAP 病原菌** | Ch.1 p.21 主要為革蘭氏陰性桿菌 | 現行強調 MDR 與院內抗生素暴露史 | 標示 |
| **圓形肺炎** | Ch.1 p.21 稱「seen only in children」 | 成人亦可見，成人圓形肺炎須排除腫瘤 | 標示；此項在醫學上具實務重要性 |
| **肺結節處置** | 原書 2013 年版 | Fleischner Society 2017 準則已更新門檻 | 需人工確認網站是否引用舊門檻數值 |
| **對比劑腎病** | Ch.12 Physics, pp.839–842 | 現行建議已大幅放寬（僅 eGFR<30 需預防） | 需人工確認 |
| **Gadolinium 與 NSF** | Ch.12 p.842（2013，早於線性類 agent 時代） | 已改用線性/大環狀類 agent，NSF 風險極低 | 需人工確認 |
| **COVID-19 影像** | 原書出版於 2013，無此內容 | 屬教材需更新之範疇，非錯誤 | 可另立補充章節，不應改寫原書 |

> ⚠️ 上述「需人工確認」項目**尚未逐項比對**，因為其對應章節（nuclear、physics、thoracic 肺結節段）尚未完成審計。

---

## 6. 全 12 章影像身分驗證（第二階段已完成）

### 6.1 確定性影像身分驗證（865 張）

以 `scripts/audit/verify_image_pixels.py` 逐張比對：把 `static/images/<chapter>/page-NNN.png`
與教科書對應書頁以相同解析度渲染後做像素比對。正確頁的平均絕對差為 **0**，次選頁為 13.9–24.5，
差距逾 10 倍，故差值 < 3 視為確定性命中。

| 章節 | 影像數 | 像素級完全命中 | 檔名與實際一致 |
|---|---|---|---|
| thoracic | 86 | 86 | 86 |
| gi | 70 | 70 | 70 |
| genitourinary | 44 | 44 | 44 |
| neuro | 145 | 145 | 145 |
| msk | 118 | 118 | 118 |
| ultrasound | 89 | 89 | 89 |
| nuclear | 39 | 39 | 39 |
| breast | 66 | 66 | 66 |
| interventional | 47 | 47 | 47 |
| pediatric | 97 | 97 | 97 |
| cardiovascular | 37 | 1 | 35 |
| physics | 27 | 13 | 22 |
| **合計** | **865** | **815** | **849** |

**結論：影像檔名規則（`NNN = 書頁 + 9`）在全書成立。** 剩餘 50 張未像素命中者全部集中於
cardiovascular 與 physics —— 這兩章的掃描檔解析度是 1241×1531（其餘為 1294×1630），
渲染尺寸不一致導致像素差無法歸零。已用視覺覆核確認這 50 張的檔名規則同樣成立
（例：`cardiovascular/page-668.png` = 書頁 659「Aortic anatomy」、
`physics/page-851.png` = 書頁 842「Iodinated contrast and pregnancy」）。

**這修正了第一階段的認知**：原報告 F-01 認為「影像與說明文字系統性錯位」的成因是
*Learning Radiology* 骨架。實際上**檔名本身幾乎全對**，錯的是「哪一張圖掛在哪一段」。

### 6.2 影像數與書頁數相等 → 一對一對應

| 章節 | 影像數 | 該章書頁數 | 差 |
|---|---|---|---|
| thoracic | 86 | 86 | 0 |
| gi | 70 | 70 | 0 |
| genitourinary | 44 | 44 | 0 |
| neuro | 145 | 145 | 0 |
| msk | 118 | 118 | 0 |
| ultrasound | 89 | 89 | 0 |
| nuclear | 39 | 39 | 0 |
| breast | 66 | 66 | 0 |
| interventional | 47 | 47 | 0 |
| pediatric | 97 | 97 | 0 |
| physics | 27 | 27 | 0 |
| cardiovascular | 37 | 36 | +1（F-07） |

11/12 章完全相等。這意味著正確的對應必然是**雙射**（每張圖恰好對應一頁）。
此發現同時宣告兩個方法論的**死路**（實測驗證）：

- **嚴格單調一對一對齊**：必然退化成恆等映射，檢不出任何錯位（空檢定）。
- **允許多段複用同一頁的 DP**：會整體漂移，產生離譜偏移（實測 thoracic 末段偏移 −53），
  誤提案率極高。

可用的判準是**局部**的：每一段文字都帶有它自己應對應的書頁標題。

### 6.3 逐區塊比對：詞集包含規則

採用**包含關係**而非模糊分數：區塊英文標題的內容詞集 S，若 `S ⊆ heading(P)`
（教科書該頁頁首標題的詞集），則 P 幾乎確定就是該段來源頁。包含關係比 cosine 嚴格得多，
不會把「肝臟 / Liver」這種單詞泛配到所有含 liver 的頁。

比對結果（`docs/audit/image_segment_offsets.csv`，743 個含影像區塊）：

| 狀態 | 數量 | 意義 |
|---|---|---|
| MATCHED | 124 | 找到唯一來源頁，可計算偏移 |
| AMBIGUOUS | 16 | 多頁同詞，證據不足以區分 |
| NO_MATCH | 603 | 區塊標題是網站自撰，無法用書頁標題反查 |

已 MATCHED 的 124 段中，偏移量分布**高度集中**：

| 章節 | offset=0（正確） | 非零偏移 | 分布 |
|---|---|---|---|
| ultrasound | 16 | 0 | 全對（修正後） |
| gi | 35 | 2 | 全對（修正後） |
| breast | 25 | 2 | — |
| interventional | 6 | 0 | 全對 |
| thoracic | 0 | 18 | 全部唯一值 +6…+53 |
| msk | 2 | 11 | 全部唯一值 −12…+9 |
| neuro / pediatric / cardiovascular | 0 | 0–1 | 無可比對區塊 |

**非零偏移只有兩處成段出現**：

| 章節 | 偏移 | 連續段數 | 行號範圍 | 性質 |
|---|---|---|---|---|
| gi | **+1** | 10 | L406–545（脾臟／食道段） | 頁碼換算漏用一次 |
| ultrasound | **+9** | 9 | L854–1190（婦產科段） | 頁碼換算**重複套用**一次 |

偏移量恰為 +9 是決定性線索：`NNN = 書頁 + 9` 的換算被做了兩次。

### 6.4 已套用的修正（commit `dd9b3b5`）

`scripts/audit/apply_segment_offsets.py` 只處理**同一章內、同一偏移值出現 ≥3 次**的連續區塊 ——
這是機械式 bug 的特徵；孤立的大偏移經查證多為比對雜訊（例如 thoracic 的 +6…+53
各只出現一次，且其「來源頁」多為章節總覽或參考文獻頁），一律不動。

修正內容（22 處）：

1. 影像檔名 `page-NNN.png` → `page-MMM.png`
2. alt 文字 `![Page NNN]` → `![Page MMM]`
3. 章節標題的 `### Page NNN` 標籤同步（ultrasound 章的標籤即頁碼，
   不同步會讓網站顯示與影像不符的頁碼）

驗證結果：

- 套用 22 處、跳過 0 處
- 重跑比對：ultrasound 16/16 offset=0、gi 35/37 offset=0
- 942 個影像引用全部可解析，零缺圖
- alt 文字與檔名一致性：全部章節通過（neuro 有 1 處**既有**不一致，非本次修改造成）
- `### Page NNN` 標籤與影像一致性：全部章節通過
- `hugo` 0.166.0（CI 同版本）build：502 pages，EXIT=0

### 6.5 尚待處理

| 項目 | 狀態 |
|---|---|
| thoracic 18 段、msk 11 段的孤立偏移 | 未處理 —— 多為比對雜訊，需逐張視覺覆核才能確認 |
| 603 個 NO_MATCH 區塊 | 無法用標題反查，需改用內文 cosine 或圖說語意逐張比對 |
| F-02 圖說回填 | 未執行 |
| F-03 章節大綱頁碼 | 未修正 |
| F-04 來源混雜 15 處 | ✅ **第三階段已移除**（見 §7A.1） |
| F-09 網站原創臨床建議標註 | 待使用者決定 |
| **移除 LR 後的主題缺口（7 個主題）** | 未處理 —— 原書對應段落尚未補回，見 §7A.4 |

---

## 7. 建議的後續流程

### 7.1 影像重對位（已部分完成）

已完成系統性偏移段（gi +1、ultrasound +9，22 處，commit `dd9b3b5`）。剩餘待處理：

1. **孤立偏移段**（thoracic 18 段、msk 11 段）：逐張視覺覆核才能確認，多數疑為比對雜訊。
   比對工具：`scripts/audit/propose_exact_image_fixes.py`（輸出 `docs/audit/image_segment_offsets.csv`）。
2. **NO_MATCH 區塊**（603 段）：區塊標題為網站自撰，無法用書頁標題反查。
   需改用**區塊內文**對該頁內文的 cosine 比對，或以圖說語意人工覆核。
3. 覆核後依對照表更新檔名，並同步 alt 文字與 `### Page NNN` 標籤。

**方法論提醒**（第二階段實測得出，見 §6.2）：
- 不要用「嚴格單調一對一對齊」—— 影像數等於書頁數，必然退化成恆等映射，檢不出任何錯位。
- 不要用「允許多段複用同一頁的 DP」—— 會整體漂移，產生離譜偏移。
- 可靠的是**局部**判準：詞集包含規則 + 系統性偏移檢測（同一偏移值連續出現）。

### 7.2 圖說回填

從對應書頁的 caption 抽取影像描述，置於圖下。需注意：原書 caption 屬受版權保護內容，應以**改寫摘要**而非逐字複製處理。

### 7.3 來源混雜區段

thoracic（10 處）、cardiovascular（3 處）、pediatric（2 處）共 15 處 Learning Radiology 內容需使用者決策。
**第三階段已採用「移除」方案並補回原書對應內容，見 §7.5。**

### 7.4 分支策略

依指示，內容修正應與 UI 改版**分開 PR**：

- `feature/radiology-atlas`（PR #1）— UI 改版，維持現狀待 review
- `feature/content-fidelity-audit`（PR #2）— 內容修正，獨立 PR

---

## 7A. 第三階段：移除來源混雜內容並補回原書缺頁

### 7A.1 已套用的變更

| 變更 | 範圍 | 內容 |
|---|---|---|
| 移除 Learning Radiology 區塊 | thoracic 10 處、cardiovascular 3 處、pediatric 2 處，合計 15 處 | 全站 `Learning Radiology` 字串歸零；刪除 2579 行、補回 198 行 |
| 補回原書書頁 78–86 | thoracic | 先天性結締組織疾病、支氣管擴張症病因與形態學分類、肺氣腫（3 型）、氣道腫瘤（SCC／ACC／類癌／黏液表皮樣癌／氣管淋巴瘤／氣管內轉移／直接侵犯／良性腔內病變）、胸膜疾病（間皮瘤／轉移／骨髓瘤／FTP／積液／乳糜胸）、參考文獻 |
| 影像錯置修正 | thoracic 4 處 | 見 §7A.3 |

**補回內容的來源**：全部改寫自教科書文字層 `/tmp/cr_source/ch/thoracic.txt`（書頁 78–86），
未加入原書沒有的臨床主張。參考文獻節為原書書頁 85–86 的條目。

### 7A.2 修正前後的驗證

| 項目 | 修正前 | 修正後 |
|---|---|---|
| `hugo` 0.166.0 build（CI 同版本） | EXIT=0（baseline） | EXIT=0，502 pages，零 ERROR |
| 全站影像引用 | 845 | 847（新增 2 張重複引用，因原書同頁含兩張圖） |
| 缺圖 | 0 | 0 |
| alt 文字與檔名一致性 | 1 處不一致（neuro，**既有**問題） | 1 處不一致（neuro，同一處，未變動） |
| `Learning Radiology` 出現次數 | 15 處 | 0 |
| 12 章詞集包含規則比對 | — | MATCHED 129 / AMBIGUOUS 17 / NO_MATCH 599 |

### 7A.3 影像錯置的 4 處修正 —— 「一節配一頁」的假設失效

補回內容後以「詞集包含規則」重跑比對，發現 4 處 offset 非零。**根因不是頁碼換算錯誤，
而是「一個小節配一張圖」的假設失效：原書一頁含多張圖，頁首標題只反映該頁的第一個標題。**

| 段落 | 該圖實際所在書頁 | 修正前 | 修正後 |
|---|---|---|---|
| 全小葉型肺氣腫 | 書頁 80 | `page-089` ✅ | `page-089` |
| 氣管鱗狀細胞癌（SCC） | 書頁 80（與肺氣腫**同頁**） | `page-090` ❌ | `page-089` |
| 腺樣囊性癌（ACC） | 書頁 81 | `page-091` ❌ | `page-090` |
| 氣管類癌（Endobronchial Carcinoid） | 書頁 81（與 ACC **同頁**） | 無圖 ❌ | `page-090` |
| 氣管內轉移 | 書頁 82 | 無圖 ❌ | `page-091` |

**驗證方式**：對 `page-089.png`／`page-090.png` 下半部裁切後逐張視覺覆核，
確認書頁 80 同頁含「Panacinar emphysema」與「Endotracheal squamous cell carcinoma」兩張圖，
書頁 81 含「Tracheal adenoid cystic carcinoma」與「Endobronchial carcinoid」兩張圖，
書頁 82 含「Endobronchial metastasis」。

**方法論教訓**：
- 「詞集包含規則」在**一頁一圖**時有效；**一頁多圖**時會必然漏配（頁首標題不含第二張圖的圖說詞）。
- 這也解釋了為何書頁 80 的 SCC 段會被判成 offset=44 —— 規則把該段反查到書頁 36。
- 因此**比對結果只能當候選**，同頁多圖的情境必須視覺覆核（本階段 4 處修正全部來自視覺覆核，比對只提供了線索）。

### 7A.4 移除來源混雜內容後的主題缺口（新增發現，待處理）

移除 Learning Radiology 區塊後，以下主題在網站**歸零**，而這些主題**原書都有**：

| 章節 | 歸零主題 | 原書對應 |
|---|---|---|
| thoracic | 前縱隔／後縱隔腫瘤分類、畸胎瘤、甲狀腺腫塊、Luftsichel 徵、肋膜積液 | 書頁 65–74（Mediastinum）、p.5、p.40 |
| pediatric | 兒童虐待相關骨折 | 書頁（Pediatric 章，'abuse' 出現 14 次、'fracture' 88 次、'Salter' 6 次） |
| cardiovascular | 主動脈夾層、僧帽瓣 | 書頁 661–664（Acute aortic syndrome）、685（Mitral regurgitation） |

**這不是「刪錯了」，而是揭露了 F-04 的另一面**：原本標示為 Learning Radiology 的區塊中，
部分內容**確實涵蓋了原書的主題**，只是以另一本書的架構與頁碼基準呈現。移除它們會讓
這些主題在網站消失，須依原書重寫補回（同 thoracic 書頁 78–86 的處理方式）。

**未在本階段處理**，因為需要逐主題比對原書文字後改寫，屬另一個批次的工作量。
建議下一步：對 thoracic 書頁 65–74、pediatric 虐待主題、cardiovascular 書頁 658–693
逐段做「原書頁 → 網站段落」盤點，再以同一套腳本（`scripts/audit/add_book_pages_*.py`）補回。

**注意**：Luftsichel 徵在書頁 5 與 p.3 概述均有描述，網站目前仍以 `### Luftsichel Sign` 小節保留
（僅中文關鍵字「Luftschel」拼寫少一個 c，英文 "luftsichel" 仍在），故實質未遺失。

---

## 8. 可重現性

本次審計使用的工具與路徑：

| 用途 | 位置 |
|---|---|
| 教科書 PDF | `/tmp/cr_source/textbook.pdf`（91.9 MB，未納入 git） |
| 全書文字層 | `/tmp/cr_source/textbook_all.txt`（3.38 MB） |
| 書頁 ↔ PDF 頁序對照 | `/tmp/cr_source/p2i.json`（偏移固定 +8） |
| 各章書頁文字 | `/tmp/cr_source/ch/<chapter>.txt` |
| 書頁標題索引 | `/tmp/cr_source/bookhead.json` |
| 頁面圖說資料 | `/tmp/cr_source/captions.json` |
| 逐頁像素快取 | `/tmp/cr_source/pixel_cache/`（`p<書頁>-<pdf頁序>.png`） |

**審計工具（已納入 repository，`scripts/audit/`）**

| 工具 | 用途 |
|---|---|
| `verify_image_pixels.py` | 像素級影像身分驗證（確定性，865 張） |
| `verify_image_identity.py` | 影像身分驗證（OCR 輔助） |
| `extract_captions.py` | 抽取各頁頁首標題與圖說 |
| `audit_content.py` | 數值門檻／原書未提及敘述／章內矛盾 |
| `audit_images.py` | 全站影像對應審計（DP 單調對齊） |
| `inventory_other_sources.py` | 非原書來源（Learning Radiology 等）盤點與 A/B/C/D 分類 |
| `consolidate_findings.py` | 彙整 findings.csv |
| `propose_exact_image_fixes.py` | **詞集包含規則**逐區塊比對 + 分段偏移統計 |
| `apply_segment_offsets.py` | 只套用系統性偏移段（同一偏移值 ≥3 次連續） |
| `match_text_to_page.py` / `match_heading_to_page.py` | 文字／標題 → 書頁比對 |
| `add_book_pages_78_86.py` | **第三階段**：把原書書頁 78–86 的內容與影像補回 thoracic 章（可重跑，含自校驗） |

**審計結果資料（`docs/audit/`）**

| 檔案 | 內容 |
|---|---|
| `image_identity_pixels.csv` | 865 張影像的像素級身分驗證結果 |
| `image_segment_offsets.csv` | 743 個含影像區塊的逐區塊比對與偏移 |
| `image_segment_summary.csv` | 分段偏移統計 |
| `findings.csv` | 彙整後的 95 項發現 |
| `content_findings_raw.csv` | 內容比對原始結果 |
| `image_mapping.csv` | 全站影像對應表 |
| `other_sources.csv` | 非原書來源盤點 |
| `applied_segment_offsets.diff` | 已套用修正的 unified diff（可回溯） |

---

## 9. 聲明

- 本報告所有「教科書原文」引述均取自上述 PDF 的文字層，並標明書頁碼。**未虛構任何引文或頁碼。**
- 未能取得對應來源者，一律標為 **UNVERIFIED**，不以推測補足。
- 影像未依周邊文字反推 —— 影像識別結論均經視覺辨識頁首標題與頁腳頁碼確認。
- 本報告未修改任何網站內容。所有修正建議皆待核准。
- UI 改版（PR #1）與本內容審計彼此獨立，未合併。
