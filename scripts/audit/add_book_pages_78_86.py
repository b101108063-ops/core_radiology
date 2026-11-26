#!/usr/bin/env python3
"""把《Core Radiology》書頁 78–86 的原書內容補進 thoracic 章節。

背景
----
刪除 Learning Radiology 區塊後，thoracic 章有兩個問題：

1. 原書書頁 78–86（Emphysema、Airway tumors、Pleura、References）在網站
   **完全沒有對應段落** —— 這些是原書有、網站缺的內容。
2. 對應的 9 張全頁掃描（page-087..page-095.png）只出現在檔尾的「圖片出處」
   清單裡，沒有任何內文段落承接，等於讀者只看到清單看不到內容。

本腳本：
- 在支氣管擴張症之後插入書頁 78（先天性結締組織疾病 / Broncholithiasis）
- 新增「肺氣腫」「氣道腫瘤」「胸膜疾病」「參考文獻」四節，對應書頁 79–86
- 讓 9 張圖各自落在正確的段落
- 補進「圖片出處」清單，並移除檔尾那 9 個裸影像（否則會重複）

所有內容均改寫自原書文字層（/tmp/cr_source/ch/thoracic.txt），未加入書上沒有的臨床主張。
"""
import re, os, shutil

SITE = os.environ.get('CR_SITE_DIR', '/home/node/.openclaw/workspace/core_radiology_hugo')
F = f'{SITE}/content/docs/thoracic/_index.md'
IMG = '/core_radiology/images/thoracic'

# ---------------------------------------------------------------- 內容區塊

BRONCHIECTASIS_ADD = f"""
### 先天性結締組織疾病 / Congenital Connective Tissue Disorders

- **Mounier–Kuhn**：結締組織疾病，造成**氣管支氣管擴張**（tracheobronchomegaly），導致反覆肺炎

- **Williams–Campbell**：遠端支氣管軟骨罕見疾病，可為先天性，或為病毒感染後的後遺症

![Page 087]({IMG}/page-087.png)

*Mounier–Kuhn：胸部 X 光（左）顯示嚴重瀰漫性支氣管擴張；CT 顯示氣管擴張（卡尺量測）與嚴重囊狀支氣管擴張。*

### 支氣管擴張症的原因 / Causes of Bronchiectasis

**CAPTAin Kangaroo has Mounier–Kuhn** — 記憶支氣管擴張症常見病因的口訣：

| 病因 / Cause | 備註 |
|---|---|
| **Cystic fibrosis** | 最常見原因之一 |
| **Allergic bronchopulmonary aspergillosis (ABPA)** | — |
| **Post infectious** | 感染後 |
| **TB / atypical mycobacteria** | — |
| **Agammaglobulinemia** | — |
| **Immunodeficiency** | — |
| **Kartagener** | 原發性纖毛運動不能 |
| **Mounier–Kuhn** | 先天性氣管支氣管擴張 |

- **Cystic fibrosis** 傾向**上葉為主**；相對地，**感染後**支氣管擴張症傾向**下葉為主**

### 形態學分類 / Morphologic Classification

形態學分類最適合作為**嚴重程度的粗略指標**：

| 型別 / Type | 嚴重度 | 描述 |
|---|---|---|
| **Cylindrical** | 最輕 | 輕度支氣管擴張 |
| **Varicose** | 中度 | 支氣管可變成串珠狀、不規則 |
| **Cystic** | 最嚴重 | 支氣管明顯擴大並氣球化，形成多發囊腫，可能與氣道不相通 |

### 影像表現 / Radiographic and CT Findings

- **X 光**：取決於嚴重程度。輕度案例可能只看到 **tram tracks**（電車軌徵）—— 支氣管壁增厚形成平行的放射不透線，狀似電車軌；較嚴重時可見廣泛囊狀變化

- **CT — signet ring sign（指環徵）**：擴張的支氣管**鄰鄰正常的肺動脈分支**。正常每條支氣管的大小應約等於相鄰的肺動脈分支

- 其他 CT 所見：**支氣管失去逐漸變細（lack of bronchial tapering）**、**支氣管壁增厚**、**黏液充填的支氣管**；常伴隨鄰近的 **tree-in-bud 結節**，很可能代表相關的小氣道感染

### 支氣管結石症 / Broncholithiasis

- 支氣管結石症是**支氣管腔內鈣化／骨化物質**的罕見疾病，最常由鄰近**鈣化肉芽腫淋巴結侵蝕**造成

- 臨床表現為**無痰咳嗽（nonproductive cough）、咯血（hemoptysis）與空氣滯留（air trapping）**
"""

EMPHYSEMA = f"""
## 肺氣腫 / Emphysema

![Page 088]({IMG}/page-088.png)

*小葉中心型與旁隔型肺氣腫：冠狀面（左）與軸位 CT 顯示小葉中心型與旁隔型肺氣腫。小葉中心型肺氣腫以上葉為主（黃箭頭），旁隔型肺氣腫見於前內側（藍箭頭）。冠狀面可見橫膈變平（紅箭頭）。*

### 定義與機轉 / Definition and Pathophysiology

- **肺氣腫** 是**肺泡壁的破壞**，導致**遠端氣腔不可逆擴大**。雖然肺氣腫初期不涉及纖維化，但**末期肺氣腫可能引發修復反應，最終導致肺纖維化**

- **Elastase（胰彈性蛋白酶）** 由**肺泡巨噬細胞與中性球**產生，兩者在吸菸者中皆增加。Elastase 是強大的破壞性酵素，在宿主防禦機制中發揮功能，但**過量的 elastase 對原生組織極為有害**

- **Alpha-1-antitrypsin（α1-抗胰蛋白酶）** 正常情況下中和 elastase。**elastase 過量**（吸菸相關肺氣腫）或**中和酵素不足**（α1-antitrypsin 缺乏）任一者都可造成肺組織破壞與肺氣腫

### 小葉中心型肺氣腫 / Centrilobular Emphysema

- **小葉中心型肺氣腫是吸菸相關的肺疾病**

- **以上葉為主**。與另一種吸菸相關肺疾病 **RB-ILD** 相同，小葉中心型肺氣腫**主要影響次級肺小葉的中心**

- 所有吸菸相關肺病（**RB、RB-ILD、DIP、PLCH 與 emphysema**）都可能屬於**同一發病譜系** —— 由巨噬細胞介導、對吸入顆粒與毒素的發炎反應所造成

### 旁隔型肺氣腫 / Paraseptal Emphysema

- 旁隔型肺氣腫**通常與其他形式的肺氣腫合併出現**，通常也與吸菸有關

- **位於胸膜下（subpleural）**，易導致**氣胸**

### 全小葉型肺氣腫 / Panacinar (Panlobular) Emphysema

![Page 089]({IMG}/page-089.png)

*全小葉型肺氣腫（α1-抗胰蛋白酶缺乏所致）：胸部 X 光與冠狀面 CT 顯示瀰漫性肺氣腫變化，以**下葉**最嚴重，並可見橫膈變平（箭頭）。*

- **全小葉型（又稱 panlobular）肺氣腫** 影響**整個腺泡（acinus）**，在肺內瀰漫分布；肺氣腫變化通常在**肺底部更嚴重**

- **Alpha-1-antitrypsin 缺乏是全小葉型肺氣腫的重要病因**
"""

AIRWAY_TUMORS = f"""
## 氣道腫瘤 / Airway Tumors

- **氣管與中央支氣管的原發腫瘤很少見**。**成人**而言絕大多數為**惡性**；**兒童**則**大多為良性**

- **鱗狀細胞癌（SCC）與腺樣囊性癌（ACC）** 是成人最常見的兩種中央氣道原發腫瘤

### 氣管鱗狀細胞癌 / Tracheal Squamous Cell Carcinoma (SCC)

![Page 089]({IMG}/page-089.png)

*氣管鱗狀細胞癌：胸部 X 光顯示細微的氣管充盈缺損（箭頭）。CT 可見異質性強化、界限清晰、顯著狹窄氣管腔的腫塊（箭頭）。*

- **鱗狀細胞癌是最常見的原發氣管惡性腫瘤**，與**吸菸**強烈相關

- 典型的 CT 表現為**息肉樣的腔內腫塊（polypoid intraluminal mass）**。腫塊輪廓可為**不規則、平滑或分葉狀**。腫瘤偶爾可**侵犯食道，造成氣管食道瘻（tracheoesophageal fistula）**

### 腺樣囊性癌 / Adenoid Cystic Carcinoma (ACC)

![Page 090]({IMG}/page-090.png)

*氣管腺樣囊性癌：CT（左）顯示不規則的環形氣管壁增厚（箭頭）。對比增強冠狀面 T1 加權 MRI（右）顯示伸入氣管腔的強化結節狀腫塊（箭頭）。*

- **腺樣囊性癌是相對低度惡性的腫瘤**，通常影響**四十歲左右**的病人，比典型的 SCC 病人**早一二十年**

- **與吸菸無關**

- **ACC 有沿神經周圍與黏膜下擴散（perineural and submucosal spread）的傾向**。雖然生長緩慢（indolent），**轉移病灶在 PET 上常呈現強烈 FDG uptake**

- 典型的 CT 表現為**黏膜下腫塊，浸潤氣管壁與周圍縱隔脂肪**。ACC 也可能表現為**環形的氣管或支氣管壁增厚，造成氣道狹窄**

### 氣管類癌 / Endobronchial Carcinoid

![Page 090]({IMG}/page-090.png)

*氣管內類癌：胸部 X 光顯示右下葉肺膨脹不全（箭頭）與容積減少。軸位對比增強 CT 顯示右主支氣管內、隆突稍遠端有一個輕度強化的界限清楚腔內支氣管腫塊（箭頭）。*

- **類癌是神經內分泌腫瘤的一個譜系**，包含**低度惡性類癌、侵襲性類癌與小細胞癌**，其生物學行為範圍廣

- 類癌腫瘤**極少分泌荷爾蒙**（例如 ACTH）

- 雖然**成人**的腔內支氣管類癌很少見，但**類癌是兒童最常見的支氣管腫瘤**

- **類癌幾乎總是發生在隆突（carina）遠端**

- **CT 顯示腔內支氣管腫塊，具均勻的動脈期強化**

- 強化的腔內支氣管腫塊之**鑑別診斷**還包括**黏液表皮樣癌（mucoepidermoid carcinoma）**，以及極罕見的**血管瘤與球瘤（glomus tumor）**

### 黏液表皮樣癌 / Mucoepidermoid Carcinoma

- 罕見腫瘤，起源於**氣管支氣管樹襯 lining 的細小唾液腺**

- 傾向影響**比腺樣囊性癌更年輕**的病人

- CT 表現為**圓形或卵形的腔內支氣管腫塊**，與**類癌無法區分**

### 氣管淋巴瘤 / Tracheal Lymphoma

- 氣管淋巴瘤罕見，通常與**黏膜相關淋巴組織（MALT）**相關，屬**低度惡性**

### 氣管內轉移 / Endobronchial Metastasis

![Page 091]({IMG}/page-091.png)

*氣管內轉移：冠狀面對比增強 CT 顯示一個異質性強化的腫塊，侵犯右主支氣管（箭頭）。此例為梭形細胞癌，但影像表現並無特異性。*

- **最常見會轉移至中央氣道的惡性腫瘤**：**乳癌、腎細胞癌、甲狀腺癌、肺癌、黑色素瘤與肉瘤**

- **BReTh Lung** 是記憶四種最常見氣道轉移（乳癌、腎細胞癌、甲狀腺癌、肺癌）的口訣

### 相鄰惡性腫瘤直接侵犯 / Direct Invasion of the Central Airways

- **直接侵犯中央氣道比氣管內轉移更常見**

- **侵襲性的喉癌、甲狀腺癌、食道癌與肺癌** 可造成直接的氣道侵犯

### 良性腔內病變 / Benign Endobronchial Lesions

- **乳突狀瘤（papilloma）** 是良性但**具有潛在癌變可能**的病變，可能轉化為癌。疑似乳突狀瘤通常需密切追蹤。**單一乳突狀瘤**通常由慢性刺激造成；**多發乳突狀瘤（喉氣管乳突狀瘤病）**由 **HPV** 造成，可於出生時獲得。**罕見**（<1% 的病例）乳突狀瘤會散播至肺部，形成**多發空洞性結節**

- **軟骨瘤（chondroma）** 是罕見的良性軟骨性腫瘤，極少發生於氣道

- 其他良性腔內病變包括**神經鞘瘤、腺瘤、錯構瘤、血管瘤、脂肪瘤與平滑肌瘤**
"""

PLEURA = f"""
## 胸膜疾病 / Pleura

### 惡性胸膜腫瘤 / Pleural Malignancy

![Page 092]({IMG}/page-092.png)

*間皮瘤：胸部對比增強 CT（左）顯示左側胸腔廣泛結節性胸膜增厚（箭頭）。上腹部影像顯示廣泛軟組織異常並侵犯胸壁（箭頭）。*

#### 間皮瘤 / Mesothelioma

- **間皮瘤是起源於胸膜的高度侵襲性腫瘤**。多數病例與**既往石棉暴露**有關，**潛伏期 >20 年**

- **上皮型（epithelial subtype）較常見**，預後略佳；**肉瘤樣與混合型更具侵襲性**

- **間皮瘤的 CT 典型表現為結節性同心胸膜增厚**，常伴隨胸腔積液

- **手術的角色仍在演進**，目標是切除所有可見的腫瘤

- **局部侵襲性疾病** 執行**胸膜外全肺切除（extrapleural pneumonectomy）**

- **較不進展的疾病**偏好**胸膜剝除術與剝除皮質（pleurectomy and decortication）**，可保留肺與葉間裂。對侵襲性較低的**上皮型**，其預後與胸膜剝除術或肺切除相當

- 結合**手術、術中 heated chemotherapy 與放射治療的三模式治療（trimodality therapy）**，已證實對部分病人有益

### 胸膜轉移 / Metastases

- **肺癌、胃腸道與泌尿生殖道腺癌，以及侵襲性胸腺瘤** 皆可轉移至胸膜

### 多發性骨髓瘤／漿細胞瘤 / Multiple Myeloma / Plasmacytoma

- **肋骨起源的病灶可能外觀上像是胸膜起源**，但**起源於肋骨的病灶其中心會落在肋骨上**

### 纖維性胸膜腫瘤 / Fibrous Tumor of the Pleura (FTP)

![Page 093]({IMG}/page-093.png)

*胸膜纖維性腫瘤：CT topogram（左）顯示一個圓形不透亮區（箭頭），內側緣銳利、外側緣不清，提示胸膜為來源的腫塊。CT 確認該腫塊（箭頭）源自胸膜，與胸膜呈寬基底相連。*

- **胸膜纖維性腫瘤是不與石棉沉著或間皮瘤相關的局灶性胸膜腫塊**，**並非間皮來源**

- **約 20–30% 的 FTP 為惡性，因此所有病例皆切除**。惡性潛力由**病理上的有絲分裂數**決定

- FTP 可伴隨**低血糖或肥大性肺性骨關節病**，但這些合併症**罕見（5%）**

- **FTP 可為帶蒂（pedunculated）**。**胸膜為主的腫塊若位置會改變，提示 FTP**。FTP 在 PET 上**FDG uptake 低**

### 胸腔積液：漏出液與滲出液 / Pleural Effusion: Transudate and Exudate

#### 漏出液 / Transudate

- **漏出性積液**源於**全身或局部的液體靜力學與血漿膠體滲透壓的不平衡**。常見原因包括**全身性低蛋白狀態、心臟衰竭與腎病症候群**

#### 滲出液 / Exudate

- **滲出性積液與漏出液的區分靠胸腔穿刺（thoracentesis）**。**沒有可靠的影像特徵**可以區分漏出液與滲出液

- 以 **Light's criteria** 分析胸腔穿刺液是**最可靠的區分方法**。若以下任一項存在，即歸類為**滲出液**：

| Light's criteria | 閾值 |
|---|---|
| 胸腔液蛋白 / 血清蛋白比值 | **>0.5** |
| 胸腔液 LDH / 血清 LDH 比值 | **>0.6** |
| 胸腔液 LDH | **> 血清正常上限的 2/3** |

- **滲出液的存在意味著胸膜疾病造成微血管通透性增加**，可能的原因包括：

- **肺炎**伴旁支氣管積液、**膿胸（empyema）** 或**結核性胸膜炎**

- **間皮瘤或胸膜轉移**

- **類風濕性關節炎或其他膠原血管疾病**

### 乳糜胸 / Chylothorax

![Page 094]({IMG}/page-094.png)

- **乳糜胸是含有腸淋巴液的胸腔積液**，最常由**胸導管的腫瘤性阻塞**造成。乳糜胸也與**淋巴管平滑肌瘤症（LAM）** 相關

- **胸導管起源於上腹部的乳糜池（cisterna chyli）**，並**注入左頭臂靜脈或左鎖骨下靜脈**
"""

REFERENCES = f"""
## 參考文獻 / References, Resources, and Further Reading

![Page 095]({IMG}/page-095.png)

以下為原書所列參考文獻。

### 一般參考文獻 / General References

- Webb, W.R. & Higgins, C.B. *Thoracic Imaging — Pulmonary and Cardiovascular Radiology*. Lung. Lippincott Williams & Williams. (2005).

- Hansell, D.M., Lynch, D., McAdams, H.P. & Bankier, A.A. *Imaging of Diseases of the Chest* (5th ed.). Mosby. (2010).

### 解剖與基本概念 / Anatomy and Basic Concepts

- Eisenhuber, E. Signs in imaging — the tree in bud sign. *Radiology* 222, 771–2 (2002).

- Engoren, M. Lack of association between atelectasis and fever. *Chest* 107, 81–84 (1995).

- Gibbs, J.M. et al. Lines and stripes: where did they go? — From conventional radiography to CT. *Radiographics* 27, 33–48 (2007).

- Marshall, G.B. et al. Signs in thoracic imaging. *Journal of Thoracic Imaging* 21, 76–90 (2006).

### 肺部感染 / Pulmonary Infection

- Franquet, T. et al. Spectrum of Pulmonary Aspergillosis: Histologic, Clinical, and Radiologic Findings. *Radiographics* 21, 825 (2001).

- Gotway, M.B. et al. The radiologic spectrum of pulmonary Aspergillus infections. *Journal of Computer Assisted Tomography* 26, 159–73 (2002).

- Systrom, D.M. & Wittram, C. Case 9-2005-A 67-Year-Old Man with Acute Respiratory Failure. *New England Journal of Medicine* 352, 1238 (2005).

- Tarver, R.D. et al. Radiology of community-acquired pneumonia. *Radiologic Clinics of North America* 43, 497–512, viii (2005).

- Waite, S., Jeudy, J. & White, C.S. Acute lung infections in normal and immunocompromised hosts. *Radiologic Clinics of North America* 44, 295–315, ix (2006).

### 肺水腫與 ICU 影像 / Pulmonary Edema and ICU Imaging

- Ely, E.W. Using the Chest Radiograph To Determine Intravascular Volume Status: The Role of Vascular Pedicle Width. *Chest* 121, 942–50 (2002).

- Martin, G.S. Findings on the Portable Chest Radiograph Correlate With Fluid Balance in Critically Ill Patients. *Chest* 122, 2087–2095 (2002).

### 肺癌 / Lung Cancer

- Hartman, T.E. Radiologic evaluation of the solitary pulmonary nodule. *Radiologic Clinics of North America* 43, 459–65, vii (2005).

- MacMahon, H. et al. Guidelines for management of small pulmonary nodules detected on CT scans: a statement from the Fleischner Society. *Radiology* 237, 395–400 (2005).

- Travis, W.D. et al. International association for the Study of Lung Cancer/American Thoracic Society/European Respiratory Society international multidisciplinary classification of lung adenocarcinoma. *Journal of Thoracic Oncology* 6, 244–85 (2011).

- UyBico, S.J. et al. Lung cancer staging essentials: the new TNM staging system and potential imaging pitfalls. *Radiographics* 30, 1163–81 (2010).

### 肺血管疾病 / Pulmonary Vascular Disease

- Agnelli, G. & Becattini, C. Acute Pulmonary Embolism. *New England Journal of Medicine* 363, 266–74 (2010).

- Durán-Mendicuti, A. & Sodickson, A. Imaging evaluation of the pregnant patient with suspected pulmonary embolism. *International Journal of Obstetric Anesthesia* 20, 51–9 (2011).

- Frazier, A. et al. From the Archives of the AFIP: Pulmonary Veno-occlusive Disease and Pulmonary Capillary Hemangiomatosis. *Radiographics* 27, 867–83 (2007).

- Kuriakose, J. & Patel, S. Acute pulmonary embolism. *Radiologic Clinics of North America* 48, 31–50 (2010).

- Patel, N.M. et al. Pulmonary hypertension in idiopathic pulmonary fibrosis. *Chest* 132, 998–1006 (2007).

- Wittram, C. et al. CT angiography of pulmonary embolism: diagnostic criteria and causes of misdiagnosis. *Radiographics* 24, 1219–38 (2004).

### 瀰漫性肺疾病 / Diffuse Lung Disease

- Attili, A.K. et al. Smoking-related interstitial lung disease: radiologic-clinical-pathologic correlation. *Radiographics* 28, 1383–96 (2008).

- Gill, R., Matsusoka, S. & Hatabu, H. Cavities in the lung in oncology patients: imaging overview and differential diagnoses. *Applied Radiology* (June), 10–21 (2010).

- Gotway, M.B. et al. High-resolution CT of the lung: patterns of disease and differential diagnoses. *Radiologic Clinics of North America* 43, 513–42, viii (2005).

- Kligerman, S.J. et al. Nonspecific interstitial pneumonia: radiologic, clinical, and pathologic considerations. *Radiographics* 29, 73–87 (2009).

- Medoff, B.D., Abbott, G.F. & Louissaint Jr, A. Case 16-2010 — A 48-Year-Old Man with a Cough and Pain in the Left Shoulder. *New England Journal of Medicine* 362, 2013 (2010).

- Mueller-Mang, C., Grosse, C. & Schmid, K. What Every Radiologist Should Know about Idiopathic Interstitial Pneumonias. *Radiographics* 27, 595–616 (2007).

- Rossi, S.E. et al. "Crazy-Paving" Pattern at Thin-Section CT of the Lungs: Radiologic-Pathologic Overview. *Radiographics* 23, 1509–519 (2003).

- Webb, W.R. Thin-section CT of the secondary pulmonary lobule: anatomy and the image — the 2004 Fleischner lecture. *Radiology* 239, 322–38 (2006).

### 縱隔 / Mediastinum

- Quint, L.E. Imaging of anterior mediastinal masses. *Cancer Imaging* 7 Spec No, S56–62 (2007).

- Tecce, P.M., Fishman, E.K. & Kuhlman, J.E. CT evaluation of the anterior mediastinum: spectrum of disease. *Radiographics* 14, 973 (1994).

- Whitten, C., Khan, S. & Munneke, G. A Diagnostic Approach to Mediastinal Abnormalities. *Radiographics* 27, 657–71 (2007).

### 氣道 / Airways

- Ferretti, G.R. et al. Imaging of tumors of the trachea and central bronchi. *Radiologic Clinics of North America* 47, 227–41 (2009).

- Javidan-Nejad, C. & Bhalla, S. Bronchiectasis. *Radiologic Clinics of North America* 47, 289–306 (2009).

- Martinez, S. et al. Mucoid impactions: finger-in-glove sign and other CT and radiographic features. *Radiographics* 28, 1369–82 (2008).

### 胸膜 / Pleura

- Qureshi, N.R. & Gleeson, F.V. Imaging of pleural disease. *Clinics in Chest Medicine* 27, 193–213 (2006).

- Sugarbaker, D. & Wolf, A. Surgery for malignant pleural mesothelioma. *Expert Review of Respiratory Medicine* 4, 363–72 (2010).

- Wang, Z.J. et al. Malignant Pleural Mesothelioma: Evaluation with CT, MR Imaging, and PET. *Radiographics* 24, 105 (2004).
"""

# ---------------------------------------------------------------- 執行

def main():
    shutil.copy(F, '/tmp/f04_backup/thoracic_before_bookpages.md')
    lines = open(F, encoding='utf-8').read().split('\n')

    # 1) 移除檔尾那 9 個裸影像（它們會被放進內文段落）
    tail_imgs = [i for i, l in enumerate(lines)
                 if re.match(r'^!\[Page (8[7-9]|9[0-5])\]', l)]
    assert len(tail_imgs) == 9, f'expected 9 trailing bare images, got {len(tail_imgs)}'
    for i in reversed(tail_imgs):
        del lines[i]
    while lines and lines[-1].strip() == '':
        lines.pop()

    # 2) 在「圖片出處」之前的分隔線前插入新內容
    refi = next(i for i, l in enumerate(lines) if l.startswith('## 圖片出處'))
    # refi 前是 '---' 分隔線，再前是空行
    anchor = refi
    while anchor > 0 and lines[anchor - 1].strip() in ('', '---'):
        anchor -= 1

    new_block = (BRONCHIECTASIS_ADD + EMPHYSEMA + AIRWAY_TUMORS
                 + PLEURA + REFERENCES).strip('\n').split('\n')
    lines[anchor:anchor] = new_block + ['', '---', '']

    # 3) 補「圖片出處」清單的 9 筆
    refi = next(i for i, l in enumerate(lines) if l.startswith('## 圖片出處'))
    last_link = max(i for i, l in enumerate(lines)
                    if i > refi and re.match(r'^- \[圖', l))
    entries = []
    for n in range(87, 96):
        entries.append(f'- [圖1：page-{n:03d}.png]({IMG}/page-{n:03d}.png)'
                       f'{{target="_blank"}}')
        entries.append('')
    lines[last_link + 1:last_link + 1] = entries

    open(F, 'w', encoding='utf-8').write('\n'.join(lines))
    print(f'inserted {len(new_block)} lines of book content before line {anchor+1}')
    print(f'added {len(entries)//2} image-reference entries')


if __name__ == '__main__':
    main()
