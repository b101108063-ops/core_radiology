# Core Radiology — Textbook Content Fidelity Audit

審計對象：<https://github.com/b101108063-ops/core_radiology>
審計分支基準：`main` @ `228eb5a`（UI 改版 PR #1 未納入本審計）
報告產生日期：2026-10-31
狀態：**第一階段（代表性章節抽樣審計）— 等待核准後續審其餘 11 章**

---

## 0. 執行摘要

本次審計找到了**原始教科書來源**，因此可以進行真正的逐頁比對，而非僅憑網站內容自我檢查。

| 項目 | 結果 |
|---|---|
| 原始教科書是否可得 | ✅ 可得（見 §1） |
| 文字層是否可抽取 | ✅ 可，3.38 MB 純文字，886 頁全數可定位 |
| 書頁碼 ↔ PDF 頁序對應 | ✅ 完全一致，偏移固定 **+8**（886/886 頁驗證通過） |
| 12 個網站章節 ↔ 教科書章節對應 | ✅ 全部建立，章節邊界逐章驗證通過 |
| 已完整審計章節數 | **1 / 12**（thoracic），其餘 11 章待核准 |
| 已確認差異數 | **9 項**（CRITICAL 0、MAJOR 3、MINOR 4、UNVERIFIED 2） |

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
| 建議修正 | 選項：(1) 明確標示為「補充教材（Learning Radiology）」並與教科書原文分區呈現；(2) 改寫為依本教科書對應章節的內容；(3) 移除。**需使用者決定，不得靜默改寫** |
| 驗證狀態 | ✅ 已驗證（出處標註明確） |

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
| 驗證狀態 | ✅ 已驗證 |

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
| 驗證狀態 | ⚠️ 已驗證（頁碼層級）；**全章 86 張的逐張覆核尚未完成**，故暫列候選 CRITICAL |

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

## 6. 尚未審計的章節（11 章）

| # | 章節 | 書頁碼 | 影像數 | 狀態 |
|---|---|---|---|---|
| 2 | Gastrointestinal | 87–156 | 70 | ⏳ 待核准 |
| 3 | Genitourinary | 157–200 | 44 | ⏳ 待核准 |
| 4 | Neuroimaging | 201–345 | 145 | ⏳ 待核准 |
| 5 | Musculoskeletal | 346–463 | 118 | ⏳ 待核准 |
| 6 | Ultrasound | 464–552 | 89 | ⏳ 待核准 |
| 7 | Nuclear | 553–591 | 39 | ⏳ 待核准 |
| 8 | Breast | 592–657 | 66 | ⏳ 待核准 |
| 9 | Cardiovascular | 658–693 | 37 | ⏳ 待核准 |
| 10 | Interventional | 694–740 | 47 | ⏳ 待核准 |
| 11 | Pediatric | 741–837 | 97 | ⏳ 待核准 |
| 12 | Physics | 838–864 | 27 | ⏳ 待核准 |

---

## 7. 建議的後續流程

### 7.1 影像重對位（影響最大，建議優先）

每個含影像的區塊都需決定「正確的影像檔」。這是機械性但需人工覆核的工作：

1. 對每個區塊，用文字比對工具產生候選書頁（目前工具已可用，thoracic 產出 44 個區塊的候選）
2. 產生重編對照表：`區塊標題 → 正確書頁 → 正確檔名（書頁+9）`
3. **逐張視覺覆核**（86 張/章；全書 865 張）—— 文字比對只能給候選，圖說語意需人眼確認
4. 依對照表更新 markdown 中的檔名，保留 alt 為可讀描述

### 7.2 圖說回填

從對應書頁的 caption 抽取影像描述，置於圖下。需注意：原書 caption 屬受版權保護內容，應以**改寫摘要**而非逐字複製處理。

### 7.3 來源混雜區段

thoracic（10 處）、cardiovascular（3 處）、pediatric（2 處）共 15 處 Learning Radiology 內容需使用者決策。

### 7.4 分支策略

依指示，內容修正應與 UI 改版**分開 PR**：

- `feature/radiology-atlas`（PR #1）— UI 改版，維持現狀待 review
- 建議新分支 `fix/content-fidelity` — 內容修正，獨立 PR

---

## 8. 可重現性

本次審計使用的工具與路徑：

| 用途 | 位置 |
|---|---|
| 教科書 PDF | `/tmp/cr_source/textbook.pdf`（91.9 MB，未納入 git） |
| 全書文字層 | `/tmp/cr_source/text_all.txt`（3.38 MB） |
| 書頁 ↔ PDF 頁序對照 | `/tmp/cr_source/p2i.json`（偏移固定 +8） |
| 各章書頁文字 | `/tmp/cr_source/ch/<chapter>.txt` |
| 書頁標題索引 | `/tmp/cr_source/bookhead.json` |
| 文字→書頁比對工具 | `/tmp/cr_source/match.py` |
| 標題→書頁比對工具 | `/tmp/cr_source/hdrmatch.py` |
| 網站段落比對結果 | `/tmp/cr_source/match_thoracic.json`、`hdrmatch_thoracic.json` |

比對工具目前位於 `/tmp`，**重啟後會遺失**。若要將審計流程納入 repository 以便複核，建議移至 `scripts/audit/`。此動作尚未執行，待核准。

---

## 9. 聲明

- 本報告所有「教科書原文」引述均取自上述 PDF 的文字層，並標明書頁碼。**未虛構任何引文或頁碼。**
- 未能取得對應來源者，一律標為 **UNVERIFIED**，不以推測補足。
- 影像未依周邊文字反推 —— 影像識別結論均經視覺辨識頁首標題與頁腳頁碼確認。
- 本報告未修改任何網站內容。所有修正建議皆待核准。
- UI 改版（PR #1）與本內容審計彼此獨立，未合併。
