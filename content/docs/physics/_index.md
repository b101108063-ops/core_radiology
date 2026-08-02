---
title: "Physics of Imaging"
weight: 12
---

# Physics

# Physics of Imaging - Page 853

![Page 853](/core_radiology/images/physics/page-853.png)

## 輻射劑量學基礎 / Radiation Dosimetry Fundamentals

### 劑量類型 / Dose Types

#### 曝露量 / Exposure

- 定義：游離電子在單位質量空氣中釋放的電荷量
- 單位：庫侖/公斤 (C/kg)
- 僅用於描述空氣中 X/γ 射線的能量沉積

#### 空氣比釋動能 / Air Kerma

- **Kerma** = Kinetic Energy Released per Mass
- 描述入射 X 射線束強度：光子將能量轉移至帶電粒子（電子）
- 單位：Gray (Gy)，1 Gy = 1 J/kg
- **組織吸收劑量轉換**：空氣比釋動能 (Gy) × R 因子 = 吸收劑量
- R 因子取決於 kV 與吸收組織的原子序數 (Z)
- **骨頭 (Z=12) 吸收能量遠高於軟組織 (Z≈7.6)**
- 範例：10 mGy 空氣比釋動能 → 骨頭吸收 40 Gy，軟組織吸收 11 Gy

#### 等效劑量 / Equivalent Dose

- 單位：Sievert (Sv)
- 公式：等效劑量 (Sv) = 吸收劑量 (Gy) × 輻射加權因子 (WR)
- **WR 取決於線能量轉移 (LET)**
- X 射線診斷：WR = 1
- α 粒子具有高 LET，生物效應更強

#### 有效劑量 / Effective Dose

- 單位：Sievert (Sv)
- 考量所有受照器官的等效劑量及各器官的輻射敏感度
- **公式**：有效劑量 = Σ (吸收劑量 × WR × WT)，針對所有受照器官
- **WT（組織加權因子）**：
  - 高敏感器官 (WT=0.12)：骨髓、結腸、肺、乳房
  - 低敏感器官 (WT=0.01)：骨頭、腦、皮膚

### 輻射單位 / Radiation Units

| 類型 Type | SI 單位 SI Unit | 傳統單位 Legacy Unit | 換算 Conversion |
|-----------|----------------|---------------------|----------------|
| 吸收劑量 Absorbed dose / 空氣比釋動能 Air kerma | **Gray (Gy)** = J/kg | Rad | 1 Gy = 100 Rad |
| 等效劑量 Equivalent dose / 有效劑量 Effective dose | **Sievert (Sv)** | Rem | 1 Sv = 100 Rem |
| 放射性活度 Radioactivity | **Becquerel (Bq)** = 1 衰變/秒 | Curie (Ci) | 1 Ci = 3.7×10¹⁰ Bq |

- **Curie（居禮）**仍廣泛用於核醫學，典型給藥劑量為毫居里等級

---

## 臨床要點 / Clinical Key Points

- **有效劑量**是評估診斷影像輻射風險的最佳指標，單位為 Sv
- 骨頭比軟組織吸收更多能量（Z 效應）：相同空氣比釋動能下，骨頭吸收劑量可達軟組織的 3-4 倍
- **組織加權因子 WT**：高敏感組織（骨髓、肺、乳房）WT=0.12，診斷檢查時應優先屏蔽
- 核醫學仍使用 Curie 為單位；SI 單位 Gray/Sievert 已幾乎全面取代 Rad/Rem

---

# Physics of Imaging - Page 854

![Page 854](/core_radiology/images/physics/page-854.png)

## X 射線產生 / X-ray Production

### X 射線發電機 / X-ray Generator

- 高能電子撞擊陽極靶材 → 產生 X 射線光子
- **陽極靶材**：一般放射學與 CT 使用**鎢 (Tungsten, W)**，原子量 74
- **能量分配**：電子動能 99% 轉化為熱，僅 1% 轉化為 X 射線

### X 射線光譜組成 / X-ray Spectrum Components

| 類型 Type | 佔比 Proportion | 機制 Mechanism |
|-----------|----------------|----------------|
| **制動輻射 Bremsstrahlung** | **90%** | 電子在原子核電場中減速產生 |
| **特性輻射 Characteristic radiation** | **10%** | 高能電子撞出 K 層電子，外層電子填補空位產生 |

#### 特性輻射產生條件 / Characteristic X-ray Generation

- **必需條件**：電子能量 (keV) > K 層束縛能
- 鎢的 K-edge = **70 keV**，特性 X 射線能量 **< 70 keV**
- 當 kV < K-edge 時：**無特性 X 射線產生**
- 公式：E = E(K-shell) − E(transition shell)

#### X 射線能譜 / X-ray Spectrum

- **最大能量**：等於發電機 kV（例：80 kVp → 最大 80 keV）
- **平均能量**：≈ 最大能量的 **1/3**（對特性輻射不適用）

### kV 對管輸出影響 / Effect of kV on Tube Output

- **X 射線產量 ∝ (kV)²**
- kV 增加 15% → 光子數量增加約 **100%**
- 臨床影響：
  - 增加 kV → **降低劑量**
  - 增加 kV → **降低對比度**（自動曝曬控制條件下）

### 足跟效應 / Heel Effect

- **成因**：陽極對 X 射線的衰減，導致陽極側光子數減少
- **主要影響因素**：陽極角度（典型約 **15 度**）
- 陽極角越大，足跟效應越明顯

---

## 臨床要點 / Clinical Key Points

- **鎢靶**是常規放射學與 CT 的標準靶材；特性 X 射線能量低於 K-edge 70 keV
- X 射線產生效率極低（僅 1%），散熱是陽極設計的首要考量
- kV 對產量影響巨大（平方關係）：臨床調整 kV 時需同時考慮對比度與劑量的權衡
- **足跟效應**使 X 射線束在陽極側強度較低，曝曬時需考慮均勻性

---

# Physics of Imaging - Page 855

![Page 855](/core_radiology/images/physics/page-855.png)

## X 射線與物質交互作用 / X-ray Interactions with Matter

### 總覽 / Overview

X 射線光子與物質的交互作用可分為四種類型：

| 交互作用 Interaction | 能量變化 Energy Change | 對患者劑量的貢獻 Patient Dose Contribution |
|---------------------|----------------------|-------------------------------------------|
| **相干散射 Coherent scatter** | 無能量交換 | **無貢獻**（<5% 交互作用）|
| **康普頓散射 Compton scatter** | 能量降低 | 主要貢獻 |
| **光電效應 Photoelectric effect** | 能量被完全吸收 | 主要貢獻 |
| **配對產生 Pair production** | ≥1.02 MeV | 診斷能量範圍不顯著 |

### 相干散射 / Coherent (Classical) Scatter

- 無能量交換、無頻率變化
- **不貢獻患者劑量**
- 僅佔所有 X 射線交互作用的 **<5%**

### 康普頓散射 / Compton Scatter

- **與電子密度成正比**，與光子能量 E 成反比：∝ (電子密度)/E
- 散射光子**向各方向射出**
- **主導能量範圍**：
  - 軟組織：> **25 keV**
  - 骨骼：> **40 keV**
- 臨床意義：散射光子降低影像對比度

### 光電效應 / Photoelectric Effect

- **與原子序數 Z³ 成正比**，與能量 E³ 成反比：∝ **Z³/E³**
- **主導能量範圍**：
  - 軟組織：< **25 keV**
  - 骨骼：< **40 keV**
- 機制：
  1. 入射光子能量完全被吸收
  2. 內層（K 層）電子被擊出
  3. 外層電子填補空位 → 特性 X 射線或俄歇電子
- **臨床意義**：Z³ 效應使骨骼在影像中顯示高對比度

### 能量沉積 / Energy Deposition

- 內層電子攜帶的能量在局部被吸收（高能電子游離徑短）
- 30 keV 電子約造成 **1,000 次游離**（每次約 30 eV）

---

## 臨床要點 / Clinical Key Points

- **康普頓散射**主宰中高能量（>25 keV 軟組織），是影像霧化與對比度下降的主因
- **光電效應**主宰低能量（<25 keV），解釋了為何骨骼在 X 光片上如此明顯（Z³效應）
- **散射與吸收的平衡**：臨床操作中常透過調整 kV 來控制兩者比例
- 25-40 keV 是軟組織與骨骼在康普頓/光電效應主導切換的關鍵區間

---

# Physics of Imaging - Page 856

![Page 856](/core_radiology/images/physics/page-856.png)

## 衰減與半值層 / Attenuation and Half-Value Layer

### 線性衰減定律 / Linear Attenuation Law

$$N = N_0 \cdot e^{-\mu t}$$

- **N₀**：初始光子數
- **µ**：線性衰減係數（cm⁻¹）
- **t**：物質厚度（cm）
- **分數穿透率**：e^(-µt)

| µ 值 Condition | 公式應用 Formula | 臨床意義 |
|----------------|-----------------|---------|
| µ < 0.1/cm（弱衰減材料）| µ ≈ 與物質交互作用的光子比例 | 近似線性關係 |
| µ > 0.1/cm（強衰減材料）| 需使用完整指數公式 | 不可線性近似 |

- **範例**：µ = 0.5/cm，則 e^(-µt) = 61% 穿透

### 質量衰減係數 / Mass Attenuation Coefficient

- **公式**：µ/ρ（ρ = 密度）
- **特點**：與密度無關，僅取決於物質的原子組成與光子能量

### 散射與濾線柵 / Scatter and Grids

- **典型散射：主射線比**：**5-10:1**
- **濾線柵比** (Grid ratio) = 高度/寬度
- 典型濾線柵比：**8:1 ~ 12:1**
- 主射線穿透率：約 **70%**
- **Bucky 因子** =  incident dose / transmitted dose（≠ 濾線柵比！）
- 典型 Bucky 因子：**5–10**（例：40 → 200 mAs）
- **kV 升高增加散射**（康普頓效應主宰）
- **四肢檢查不使用濾線柵**（骨骼 Z 高、厚度小）

### 射束品質與半值層 / Beam Quality and Half-Value Layer (HVL)

- **高品質射束**：低能光子已被過濾
- **HVL（半值層）**：使入射能量衰減 **50%** 所需的材料厚度
- HVL 隨光子能量增加而增加
- **標準材料**：鋁 (Al)
- **典型 HVL 值**：

| 檢查類型 | 典型 HVL |
|---------|---------|
| 乳房攝影 Mammography | **0.3 mm Al** |
| 一般放射學 Radiography | **3 mm Al** |
| CT | **8–9 mm Al** |

- 法規要求：80 kVp 時 HVL **> 2.5 mm Al**

---

## 臨床要點 / Clinical Key Points

- 衰減遵循指數定律：µ 值越大，射線衰減越快
- **質量衰減係數 (µ/ρ)** 與密度無關，更適合不同組織間的比較
- 濾線柵提升對比度代價：患者劑量增加 5-10 倍（Bucky 因子）
- **HVL 是射束品質的核心指標**：HVL 越大，射束平均能量越高，穿透力越強
- 法規要求 80 kVp 時 HVL > 2.5 mm Al，確保射束足以穿透患者

---

# Physics of Imaging - Page 857

![Page 857](/core_radiology/images/physics/page-857.png)

## film光學密度與特性曲線 / Film Optical Density and Characteristic Curves

### 光學密度定義 / Film Optical Density (OD)

- **公式**：OD = log₁₀(I₀/Iₜ) = log₁₀(入射光強/透射光強)
- OD 值對照：

| OD 值 | 穿透率 Transmission | 臨床意義 |
|-------|-------------------|---------|
| **1.0** | 10% 光子穿透 | 典型診斷密度 |
| **2.0** | 1% 光子穿透 | 高密度區域 |
| **3.0** | 0.1% 光子穿透 | 極高密度 |

- **理想平均 OD ≈ 1.5**（約 5 µGy 光子撞擊菲林/螢光屏時達成）
- 霧化 (Fog)：無輻射曝曬時菲林的基準暗化（≈ 0.2 OD）

### 特性曲線（Hurter–Driffield 曲線）/ Characteristic Curve

特性曲線：對數繪製輻射曝曬（空氣比釋動能）與 film 光學密度的關係

| 曲線區域 Region | 特徵 Characteristics |
|---------------|---------------------|
| **趾部 Toe** | 低曝曬區；密度上升緩慢 |
| **線性區段 Linear portion** | 正常工作範圍 |
| **肩部 Shoulder** | 高曝曬區；密度趨於飽和 |

- **伽瑪值 (Gamma)** = 曲線最陡部分的斜率（對比度指標）
- **梯度 (Gradient)** = 平均斜率

### 寬容度與對比度 / Latitude and Contrast

| 類型 | 特性 | 適用場景 |
|------|------|---------|
| **高寬容度 (High-latitude) 菲林** | 密度變化範圍大，對比度較低 | 胸部 X 光（高低透射差異大）|
| **低寬容度 (Low-latitude) 高對比菲林** | 密度變化範圍窄，對比度極高 | 乳房攝影（組織對比度低）|

### 數位偵測器 / Digital Detectors

| 偵測器類型 | 材料 | 機制 | 優勢 | 劣勢 |
|-----------|------|------|------|------|
| **電離室 Ionization chamber** | 高壓 Xe (K-edge 35 keV) | 氣體電離 | 精確劑量測量 | 不能成像 |
| **光刺激磷光體 Photostimulable phosphor** | BaFBr | 紅色雷射讀取（發射藍光）| 動態範圍 10,000:1（film 僅 40:1），可用劑量範圍 0.1–1,000 µGy | 讀出速度慢 |
| **閃爍體 Scintillator** | CsI | 間接：X 射線→光→電荷 | K-edge 30 keV，X 射線吸收佳 | 光子擴散導致模糊 |
| **光導體 Photoconductor** | Selenium (Se) | 直接：X 射線→電荷 | 無光擴散，影像銳利 | K-edge 13 keV，標準能量吸收差（僅用於**乳房攝影**）|

- **動態範圍**：數位偵測器 >> 傳統 film（10,000:1 vs 40:1）

---

## 臨床要點 / Clinical Key Points

- OD = log₁₀(I₀/Iₜ)：菲林密度每增加 1，透射光減少 10 倍
- 特性曲線的**趾部**與**肩部**代表非正常工作區域，應避免曝曬落在這些區段
- **寬容度與對比度成反比**：高寬容度菲林對比度低（胸部），低寬容度菲林對比度高（乳房攝影）
- 數位偵測器**動態範圍極寬**，可在單次曝曬中同時捕捉極亮與極暗區域
- **硒光導體**僅用於乳房攝影（低 K-edge 13 keV 配合低能乳房 X 射線）

---

# Physics of Imaging - Page 858

![Page 858](/core_radiology/images/physics/page-858.png)

## 乳房攝影物理學 / Mammography Physics

### 技術參數對照 / Technique Comparison

| 參數 Parameter | 接觸式乳房攝影 Contact | 放大乳房攝影 Magnification |
|---------------|----------------------|--------------------------|
| **kV** | **25 kV** | 25 kV |
| **mA** | 100 mA | 25 mA |
| **焦點大小 Focal spot** | 0.3 mm | **0.1 mm** |
| **曝曬時間 Exposure time** | ~1 秒 | ~3 秒 |
| **mAs** | ~100 mAs | ~70 mAs |
| **劑量 Dose** | 5 µGy | **200 µGy** |
| **濾線柵 Grid ratio** | 5:1 (Bucky factor ~2) | 不使用（氣隙替代）|
| **平均能量 Average energy** | ~17 keV | ~17 keV |

### 乳房攝影影像品質提升因素 / Image Quality Improvement Factors

| 提升面向 | 機制 | 具體方法 |
|---------|------|---------|
| **對比度 Contrast ↑** | 降低 kV、增加壓迫、film 伽瑪值 | 25 kV；使用高對比菲林 |
| **解析度 Resolution ↑** | 薄螢光屏、小焦點、壓迫 | 單層薄螢光屏；0.1 mm 焦點 |
| **雜訊（斑點）Noise ↓** | 增加光子抵達偵測器 | 200 µGy（vs 一般 5 µGy）|

### 乳房攝影 X 射線發電機與濾片 / Mammography X-ray Generator and Filters

| 靶材/濾片 Target/Filter | 特性 X 射線能量 | 臨床應用 |
|------------------------|----------------|---------|
| **Mo 靶 Mo target** (K-edge 20 keV) | **17 keV 與 19 keV** | 標準乳房攝影 |
| **Mo 濾片** | 去除低能（增加劑量無貢獻）及高能（降低對比度）X 射線 | 僅讓特性 X 射線通過 |
| **Rh 濾片 Rh filter** | 光譜右移（能量更高）| **緻密乳房（較厚/較高密度）** |
| **Rh 靶/Rh 濾片** | 最高能量 | **極緻密乳房** |

- **Mo 靶平均能量 ≈ 17 keV**（不適用「平均能量≈1/3~1/2最大值」規則）

### 乳房壓迫 / Breast Compression

| 優勢 Advantages | 劣勢 Disadvantages |
|----------------|---------------------|
| 增加 X 射線穿透性 | 可能造成不舒服 |
| 密度均勻性 ↑ | |
| 散射 ↓ | |
| 劑量 ↓ | |
| 組織重疊 ↓ | |
| 焦點模糊 ↓ | |

---

## 臨床要點 / Clinical Key Points

- 乳房攝影**降低 kV（25 kV）**是增加對比度的關鍵：低能光子更易被組織差異吸收
- **Mo 靶/Mo 濾片组合**專為乳房組織設計：K-edge 20 keV 產生 17/19 keV 特性 X 射線
- **Rh 濾片**用於緻密乳房（光譜右移），確保足夠穿透力
- **壓迫**是乳房攝影最重要的步驟之一：同時改善對比度、解析度、均勻性並降低劑量
- 放大乳房攝影使用 0.1 mm 焦點代價：曝曬時間延長、劑量增加（不使用濾線柵以部分補償）

---

# Physics of Imaging - Page 859

![Page 859](/core_radiology/images/physics/page-859.png)

## 數位乳房攝影與放大技術 / Digital Mammography and Magnification

### 數位乳房攝影規格 / Digital Mammography Specifications

- **像素大小**：約 **80 µm**
- **最小可見微鈣化**：約 **150 µm**
- **解析度**：3,000 × 4,000 像素 ≈ **24 MB**（每像素 2 byte）
- **顯示器需求**：**5 百萬像素**監視器

### 放大乳房攝影幾何 / Magnification Mammography Geometry

$$M = \frac{SID}{SOD}$$

| 縮寫 | 定義 | 典型值 |
|------|------|--------|
| **SID** | Source-Image Distance（源-像距）| 65 cm |
| **SOD** | Source-Object Distance（源-物距）| 35 cm |
| **OID** | Object-Image Distance（物-像距）| 30 cm |

- **放大倍率**：65/35 = **1.85×**
- **不使用濾線柵**（以氣隙替代散射控制）
- **焦點大小**：0.1 mm
- **技術總結**：

| 參數 | 數值 |
|------|------|
| mA | 25 mA |
| 曝曬時間 | 3 秒 |
| mAs | 70 mAs |

- **為何不使用濾線柵**：氣隙引入使散射光子偏離偵測器，低總 mAs 可補償

### MQSA 規範 / Mammography Quality Standards Act (MQSA)

| 項目 | 要求 |
|------|------|
| **判讀醫師資歷** | 過去 24 個月內判讀 **960 例**乳房攝影 |
| **品管計畫** | 必須建立 |
| **假體測試** | 每週一次；平均腺體劑量 < **3 mGy** |

### 平均腺體劑量 / Average Glandular Dose (AGD)

- **聯邦標準**：每側乳房每體位 AGD < **3 mGy**
- 典型 AGD：**1.5–1.8 mGy/視圖/側乳房**（數位略低）
- **聯邦唯一其他劑量規範**：透視劑量率限制 **100 或 200 mGy/分鐘**

---

## 臨床要點 / Clinical Key Points

- 數位乳房攝影像素 80 µm，可偵測 **150 µm 以上**微鈣化（乳癌早期指標）
- **放大乳房攝影**：SID 65 cm / SOD 35 cm = 1.85× 放大，0.1 mm 焦點維持解析度
- 氣隙代替濾線柵：散射光子離開光路，減少約 70% 散射，同時降低總劑量
- **MQSA**強制要求判讀醫師最低量 960 例/24 個月，保障品質與經驗
- **AGD < 3 mGy**：是乳房攝影最重要的劑量安全指標

---

# Physics of Imaging - Page 860

![Page 860](/core_radiology/images/physics/page-860.png)

## 透視與 CT 物理學 / Fluoroscopy and CT Physics

### 透視物理學 / Fluoroscopy Physics

#### 電子放大 / Electronic Magnification

- 視野 (FOV) 縮小 2 倍（如 10 cm → 5 cm）：
  - 縮小的視野投射至整個輸出螢光屏 → **亮度降至 1/4**
  - 自動曝曬控制使**皮膚劑量增加 4 倍**
- FOV 10 cm → 7 cm：患者入射空氣比釋動能增加 **2 倍**

#### 透視技術參數 / Fluoroscopy Technique

- **連續透視**：電流 1–5 mA（典型 **3 mA**）
- **空氣比釋動能/幀**：約 **0.01 µGy**（標準胸部 X 光 5 µGy，透視每幀光子少 **500 倍**）
- **聯邦法規限制**：
  - 標準透視：**< 100 mGy/分鐘** 入射空氣比釋動能
  - 高劑量模式（含聲音/視覺警示）：**< 200 mGy/分鐘**（大型患者用）

#### 劑量影響因素 / Effects on Dose

| 因素 | 對劑量的影響 | 說明 |
|------|------------|------|
| **增加源-皮距離** | **↓ 劑量** | 反平方定律 |
| **增加濾片** | **↓ 劑量** | 去除低能 X 射線 |
| **移除濾線柵** | **↓ 劑量** | 兒科使用 |
| **劑量分散**（移動射束）| **↓ 最大皮膚劑量** | 避免單點過度曝曬 |
| **放大** | **↑ 劑量** | 如上所述 |

- **連續透視皮膚劑量率**：約 **10–30 mGy/分鐘**
- 高級模式最大：100 或 200 mGy/分鐘
- **2 Gy 可在 10 分鐘內達成**（高劑量模式下）
- **大型患者皮膚傷害風險更高**

### CT 概覽 / Overview of CT

- CT 旋轉扇形射束圍繞患者，透過重建演算法計算每個像素的**線性衰減係數**
- 斷層切片排除重疊結構，提供横截面影像

### Hounsfield 單位 / Hounsfield Units (HU)

$$HU = 1{,}000 \times \frac{\mu_x - \mu_{water}}{\mu_{water}}$$

| 物質 | HU 值 | 臨床意義 |
|------|-------|---------|
| 水 | **0** | 參考標準 |
| 空氣 | **-1,000** | |
| 脂肪 | **-30 ~ -100** | |
| 灰質 | **~40** | |
| 白質 | **~30** | 灰白質差異僅 **0.5%** HU |
| 對比劑強化組織 | **> 100** | 取決於增強程度 |
| 骨頭 | **> 400**（密質骨可達 +1,000）| |

- **10 HU ≈ 1% 對比度差異**
- HU 與線性衰減係數 µ 直接相關

---

## 臨床要點 / Clinical Key Points

- 透視 FOV 縮小需付出劑量代價（4 倍），操作時應權衡診斷需求
- **透視 2 Gy 可在 10 分鐘內達成**（高劑量模式），需警惕長時間透視的皮膚損傷風險
- **CT HU 值**標準化使不同設備間可比較；灰白質差異極小（0.5%），對 CT 軟體解析力要求高
- 增加源-皮距離是減少透視劑量的最簡單有效方法（反平方定律）

---

# Physics of Imaging - Page 861

![Page 861](/core_radiology/images/physics/page-861.png)

## CT 劑量學 / CT Dosimetry

### CT 劑量指數 / CT Dose Index (CTDI)

- **CTDI 定義**：單次軸向切片（完整旋轉，無床面移動）的平均 phantom 劑量，含散射，單位 Gy
- **CTDI 測量 phantom**：16 cm 與 32 cm（16 cm 劑量恆较高）

**CTDIw（加權 CTDI）**：
$$CTDI_w = \frac{2}{3} CTDI_p + \frac{1}{3} CTDI_c$$

- CTDIp = 周邊劑量
- CTDIc = 中央劑量

**CTDIvol（容積 CTDI）**：
$$CTDI_{vol} = \frac{CTDI_w}{pitch}$$

- **Pitch** 與床面移動速度相關
  - Pitch < 1：過度掃描 → 劑量增加
  - Pitch > 1：跳過區域 → 劑量減少
- CTDIvol 與掃描長度無關

**CTDIvol 參考值**：

| 檢查類型 | CTDIvol 參考值 | Phantom |
|---------|--------------|--------|
| 成人頭部 | **75 mGy** | 16 cm |
| 成人腹部 | **25 mGy** | 32 cm |
| 兒科腹部 | **20 mGy** | 16 cm |

### 劑量-長度乘積與有效劑量 / DLP and Effective Dose

$$DLP = CTDI_{vol} \times scan\ length\ (mGy \cdot cm)$$

**有效劑量估算**：
$$Effective\ dose\ (mSv) = DLP \times conversion\ factor$$

**身體部位轉換因子**：

| 部位 | 轉換因子 (mSv/mGy·cm) |
|------|---------------------|
| 頭部 Head | 0.0023 |
| 頸部 Neck | 0.0054 |
| 胸部 Chest | 0.019 |
| 腹部 Abdomen | 0.017 |
| 盆腔 Pelvis | 0.017 |
| 四肢 Legs | 0.0008 |

- **範例**：腹部 CT DLP = 900 mGy·cm → 有效劑量 = 900 × 0.017 = **15.4 mSv**

### 常見診斷檢查有效劑量 / Effective Doses of Common Diagnostic Exams

| 檢查類型 | 有效劑量 (mSv) |
|---------|--------------|
| **放射學 Radiography** | |
| PA 與側位胸部 | 0.1 |
| 頸椎 | 0.2 |
| 腰椎 | 1.5 |
| 腹部 | 0.7 |
| 盆腔 | 0.6 |
| 乳房攝影 | 0.4 |
| 膝蓋 | 0.005 |
| **透視 Fluoroscopy** | |
| 上腸胃道檢查 | 6 |
| 鋇劑灌腸 | 8 |
| **介入放射學 Interventional** | |
| 腦血管造影 | 1–10 |
| 周邊血管造影 | 5 |
| 心導管（診斷）| 7 |
| TIPS | 100 |
| **CT** | |
| 頭部 CT | 2 |
| 頸部 CT | 3 |
| 胸部 CT | 7 |
| 腹部 CT | 8 |
| 盆腔 CT | 6 |

---

## 臨床要點 / Clinical Key Points

- **DLP**是估計 CT 輻射風險的最佳單一指標（考量掃描長度）
- **CTDIvol**用於劑量監控但不直接等於患者劑量（需結合掃描範圍）
- Pitch < 1 會增加劑量（過度掃描），臨床應根據診斷需求權衡
- **腹部 CT 典型有效劑量 ≈ 8 mSv ≈ 400 張胸部 X 光**，合理 ALARA 原則下應有明確臨床適應症
- 介入檢查（心導管、TIPS）劑量可達數十至數百 mSv，需特別注意

---

# Physics of Imaging - Page 862

![Page 862](/core_radiology/images/physics/page-862.png)

## 影像品質 / Image Quality

### 對比度 / Contrast

- **對比度優化最關鍵因素**：增加抵達菲林的光子數（film 密度）
- **散射降低對比度** → 使用濾線柵或氣隙技術控制
- **準直 (Collimation)**：減少散射的同時**降低劑量**（少數「影像品質↑且劑量↓」的例外）
- **kV 降低對比度**（自動曝曬控制條件下）
- **Screen-film 系統**：對比度與螢光屏寬容度/梯度相關

### 解析度與模糊 / Resolution and Blur

**僅有三個因素影響模糊（解析度），皆不影響影像對比度**：

| 因素 | 相關參數 | 臨床控制 |
|------|---------|---------|
| **焦點模糊** | 焦點大小幾何 | 小焦點（如 0.1 mm 放大攝影）|
| **運動模糊** | 曝曬時間 | 短曝曬時間；固定患者 |
| **偵測器模糊** | 螢光屏厚度 | 快屏增厚→模糊↑（速度與解析度的權衡）|

### 統計學基礎 / Statistics Fundamentals

| 指標 | 公式 | 意義 |
|------|------|------|
| **敏感度 Sensitivity** | TP/(TP+FN) | 正確識別有病者的比例 |
| **特異度 Specificity** | TN/(TN+FP) | 正確識別無病者的比例 |
| **陽性預測值 PPV** | TP/(TP+FP) | 陽性結果為真的機率 |
| **陰性預測值 NPV** | TN/(TN+FN) | 陰性結果為真的機率 |

> TP = True Positive（真陽）；TN = True Negative（真陰）
> FP = False Positive（假陽）；FN = False Negative（假陰）

### ROC 曲線 / Receiver Operator Characteristic (ROC) Curve

- ROC 曲線比較診斷測試在不同決策信心閾值下的表現

**閾值設定與曲線移動**：

| 閾值設定 | 對敏感度的影響 | 對特異度的影響 |
|---------|--------------|--------------|
| **Threshold 1**（平衡設定）| 適中 | 適中 |
| **Threshold 2**（閾值降低）| **↑ 敏感度** | **↓ 特異度**（FP 增加）|

- 閾值降低 → 曲線上點向右移動 → 真陽率↑且假陽率↑
- ROC 曲線越靠近左上角，測試診斷效能越好

---

## 臨床要點 / Clinical Key Points

- **準直是少數同時改善影像品質又降低劑量的措施**：應常規使用
- 解析度三要素（焦點、運動、偵測器）與對比度因素完全獨立，可分開優化
- **敏感度與特異度成反向關係**：提高閾值犧牲敏感度以提升特異度
- **PPV 受疾病盛行率影響**：低盛行率環境中即使特異度高的測試 PPV 也可能低
- ROC 曲線視覺化敏感度/特異度權衡，是評估診斷測試客觀效能的標準工具

---

# Physics of Imaging - Page 863

![Page 863](/core_radiology/images/physics/page-863.png)

## 輻射生物學 / Radiation Biology

### DNA 損傷 / DNA Damage

- 輻射生物損傷大多數由**自由基**（游離子）介導
- DNA 雙鏈斷裂是最嚴重的損傷形式，修復失敗可導致細胞死亡或突變

### 決定性效應 / Deterministic Effects

**定義**：超過特定**閾值劑量**才會發生的效應，低於閾值不會發生

| 效應 | 閾值劑量 | 備註 |
|------|---------|------|
| **淋巴球減少** Lymphocyte decrease | ≥ **0.5 Gy** | 最敏感的血液學指標 |
| **白內障** Cataracts | ≥ **2 Gy**（眼部）| 後極優先受影響；高 LET 輻射（neutrons, α）更易誘發 |
| **早期紅斑** Early erythema | **2 Gy** | 短暫 |
| **強烈紅斑** Robust erythema | **6 Gy** | |
| **暫時性脫毛** Temporary epilation | **3 Gy** | 約 3 週後出現 |
| **永久性脫毛** Permanent epilation | **7 Gy** | |
| **濕性脫屑** Moist desquamation | **15 Gy** | 曝曬後約 4 週 |
| **血管損傷** Vascular damage | > **20 Gy** | |
| **潰爛/色素脫失** Ulceration/depigmentation | 晚期效應 | 真皮損傷 |
| **男性暫時性不孕** Male temporary sterility | > **0.15 Gy** | |
| **女性永久性不孕/早發更年期** Female permanent sterility | > **3.5 Gy** | |

### 遺傳效應 / Hereditary Effects

- **加倍劑量 (Doubling dose)**：使族群自發性突變率加倍的劑量，約 **1 Gy**（適用於整體人口）
- **遺傳效應風險**：約 **0.2%/Sv**（個人風險）
- 範例：性腺劑量 100 mSv → 風險 = 0.2% × 0.1 Sv = **0.02%**

### 致死劑量 / Lethal Doses (Whole-body Radiation)

| 劑量 | 終點 | 機制 |
|------|------|------|
| **3–4 Gy** | **LD₅₀/₆₀**（60 天內 50% 死亡）| 造血系統衰竭 |
| **10 Gy** | **LD₅₀/₅**（5 天內 50% 死亡）| 腸道黏膜剝脫（小腸最敏感）|
| **100 Gy** | **LD₅₀/₂**（2 天內 50% 死亡）| 腦血管症候群 |

- **LD₅₀/ₓ**：使 X 天內 50% 人口致死的劑量

---

## 臨床要點 / Clinical Key Points

- **決定性效應有明確閾值**：低於閾值不發生，ALARA 原則可完全避免
- **白內障閾值 2 Gy**（舊標準為 5 Gy，2011 年 ICRP 修訂下調）
- **造血系統**（3-4 Gy）和**腸道**（10 Gy）是全身致死劑量的兩大主要機制
- 遺傳效應風險極低（0.2%/Sv），但性腺劑量仍應盡量降低
- **皮膚劑量 20 Gy 以上**可能造成不可逆血管與真皮損傷，是介入手術皮膚管理的依據

---

# Physics of Imaging - Page 864

![Page 864](/core_radiology/images/physics/page-864.png)

## 隨機性效應與胎兒效應 / Stochastic Effects and Fetal Effects

### 隨機性效應 / Stochastic Effects

**特點**：
- **隨機發生**，無閾值
- 效應嚴重程度與劑量無關（單光子即可誘發）
- **潛伏期數年**（固體腫瘤可達 25 年）
- 劑量、劑量率與組織類型影響發生風險

### 劑量效應模型 / Dose-Effect Models

| 模型 | 適用腫瘤類型 | 潛伏期 | 特點 |
|------|-----------|--------|------|
| **線性無閾模型 Linear no-threshold (LNT)** | 固體腫瘤 | ~25 年 | 最廣泛接受的風險評估模型 |
| **線性-二次函數 Linear-quadratic** | **白血病** | **5–7 年** | 低劑量線性，高劑量趨於平坦 |

- **急性劑量癌症風險**：約 **8%/Gy**（日本原子彈存活者數據）
- 範例：4 Gy 急性暴露 → 癌症風險增加 **24%**（8 × 4）

### 輻射誘發癌症 / Radiation-Induced Cancer

| 癌症類型 | 風險 |
|---------|------|
| **白血病**（急慢性）| 約 **1%/Sv**（急性劑量）|
| **實體癌**（慢性暴露如輻射工作人員）| 約 **4%/Gy**（慢性）|

### 甲狀腺敏感性 / Thyroid Radiosensitivity

- **甲狀腺是人體輻射最敏感組織**
- 電離輻射誘發甲狀腺癌是已確定的風險

### 職業/醫源性暴露案例 / Occupational/Iatrogenic Exposure Cases

| 暴露情境 | 誘發腫瘤 |
|---------|---------|
| **僵直性脊椎炎**（X 射線治療）| 白血病 |
| **結核病透視篩檢**（歷史性螢光透視）| 乳癌 |
| **馬紹爾群島居民**（核試驗落塵）| 甲狀腺腫瘤 |
| **礦工**（尤其鈾礦，含氡氣）| 肺癌 |
| **鐘錶工人**（以唇舔取含 Ra 顏料）| 骨骼肉瘤、鼻咽癌 |

### 胎兒輻射效應 / Radiation Effects on the Fetus

| 妊娠週數 | 主要效應 |
|---------|---------|
| **0–2 週**（著床前期）| 「全有或全無」：顯著暴露可能導致流產 |
| **2–6 週** | 器官畸形、新生兒死亡↑ |
| **8–15 週** | **中樞神經畸形最關鍵期**：智能障礙 **40%/Sv**、頭徑縮小↑、兒童癌症↑ |
| **15–25 週** | 智能障礙 **10%/Sv**、兒童癌症↑ |

> 以上為**顯著暴露（例如 2 Gy）**的效應

### 妊娠輻射工作者胎兒劑量 / Fetal Dose for Pregnant Radiation Workers

- **劑量限值**：**0.5 mSv/月**（孕期全程約 5 mSv）
- **鉛圍裙**：外部測量劑量衰減 **20 倍**
- 胎兒實際劑量更低（母親覆蓋組織額外衰減約 2 倍）

---

## 臨床要點 / Clinical Key Points

- **線性無閾模型 (LNT)**是輻射防護的基礎：即使最低劑量也有理論風險
- 急性全體暴露 4 Gy 致癌風險 24%——解釋為何核事故如此致命
- **白血病潛伏期短（5-7 年）**，固體腫瘤可長達 25 年
- **胎兒中樞神經系統 8-15 週最敏感**：智能障礙風險達 40%/Sv，孕期應盡量避免高劑量影像檢查
- **孕婦影像檢查決策**：需評估臨床必要性，優先選擇非電離輻射替代方案（如超聲、MRI）

---

# 醫學影像物理學 — Learning Radiology 整合 / Medical Imaging Physics

> **来源 / Source:** Learning Radiology (5th Ed.) — Chapter 1: Recognizing Anything: Past, Present, and Future

---

## 影像模態概述 / Overview of Imaging Modalities

### 傳統 X 光（Conventional Radiography / Plain Films）

**原理：** X 光穿透人體，不同密度組織對 X 光有不同吸收率。

**五大基本密度（Five Basic Densities）：**

| 密度 | 吸收率 | X 光表現 |
|------|--------|----------|
| **空氣（Air）** | 最低 | 最黑 |
| **脂肪（Fat）** | 較低 | 灰（比軟組織稍黑）|
| **液體/軟組織（Fluid/Soft Tissue）** | 中等 | 灰白 |
| **鈣化（Calcium）** | 較高 | 白 |
| **金屬（Metal）** | 最高 | 最白 |

**優點：**
- 取得快速、價格便宜
- 可攜帶（Portable）
- 應用最廣

**缺點：**
- 密度解析範圍有限
- 使用游離輻射

**常見用途：**
- 胸部 X 光
- 腹部 X 光
- 骨折、關節炎評估

---

## 電腦斷層掃描 / Computed Tomography (CT)

### 原理
- 旋轉 X 光束配合多排偵檢器
- 螺旋（Helical/Spiral）掃描
- 電腦演算法重建三維影像

### Hounsfield 單位（Hounsfield Units, HU）

| 物質 | HU 範圍 |
|------|---------|
| 空氣 | -1000 |
| 脂肪 | -40 ~ -120 |
| 水 | 0 |
| 軟組織 | +20 ~ +100 |
| 骨骼 | +400 ~ +600 |
| 金屬 | +1000+ |

### 視窗技術（Windowing）
- **肺視窗（Lung Windows）**：顯示肺實質、支氣管
- **縱隔視窗（Mediastinal Windows）**：顯示縱隔結構、淋巴結
- **骨骼視窗（Bone Windows）**：顯示骨頭

### 多排偵檢器 CT 的優勢
- 超快速掃描（頭到腳 < 10 秒）
- 任意平面重建（軸向、矢狀、冠狀）
- 3D 容積重建（Volume Rendering）
- 新應用：虛擬大腸鏡、虛擬支氣管鏡、心臟鈣化積分、CT 冠狀动脉血管攝影

---

## 超音波 / Ultrasound (US)

### 原理
- 使用**高頻聲波（超聲波）**成像
- 探頭同時發射及接收訊號
- 不使用游離輻射

### 優點
- 價格便宜、廣泛可及
- 可攜帶（甚至手持式）
- **無游離輻射** → 孕婦、兒童安全
- 即時成像
- 可導引切片及引流

### 缺點
- 無法穿透骨骼
- 氣體阻擋聲波
- 肥胖者深部組織顯像困難
- **操作者依賴性（Operator-Dependent）**

### 常見用途
- 婦科（Pelvis）首選
- 囊腫 vs. 實心病灶鑑別
- 胎兒、胎盤評估
- 非侵入性血管成像
- 乳房的囊腫/實心鑑別
- 甲狀腺結節
- 肌腱、肌肉、韌帶

---

## 磁振造影 / Magnetic Resonance Imaging (MRI)

### 原理
- 利用體內**氫原子（主要在水分中）**的磁特性
- 強磁場 + 射頻脈衝 → 釋放訊號 → 電腦重建影像
- 可使用**釓（Gadolinium）**對比劑增強

### Hounsfield 單位等價（MRI 信號）
- T1 加權：脂肪高信號（白），水低信號（黑）
- T2 加權：水高信號（白），脂肪稍低
- igrations：不同組織有不同訊號特性

### 優點
- **無游離輻射**
- 軟組織對比極佳
- 可區分脂肪、水、肌肉、鐵等
- 鈣化無訊號（所以被骨頭包圍的組織如後顱窩可清楚顯像）
- 可任意平面成像
- 功能性成像：血流、擴散（Diffusion）、灌注（Perfusion）

### 缺點
- 價格高、取得不易
- 需要專用場地
- 安全考量：金屬物品、子宮內裝置、植入心律調節器可能禁忌
- 幽閉恐懼

### 常見用途
- 神經系統（最優勢領域）
- 肌肉、肌腱、韌帶
- 心臟結構及功能
- 肝臟、胰臟、攝護腺等

---

## 透視檢查 / Fluoroscopy

### 原理
- 实时 X 光透視
- 可見運動及裝置位置
- 可注射碘對比劑追蹤管道

### 優點
- 可導引裝置放置（如心律調節器）
- 实时確認位置
- 可做 spot film

### 缺點
- 辐射剂量較高（实时連續曝光）
- 需尽量缩短透視時間

### 常見用途
- 腸胃道鋇劑檢查
- 泌尿系統成像
- 血管、心導管
- 介入性 Radiologist 的實时導引

---

## 核子醫學 / Nuclear Medicine

### 原理
- 注射**放射性同位素製劑（Radiopharmaceutical）**
- 同位素選擇性聚集於特定器官
- **伽瑪相機（Gamma Camera）**偵測輻射成像

### 常用同位素製劑

| 器官 | 同位素 | 載體 |
|------|--------|------|
| 腦 | Tc-99m, I-123 |  |
| 心臟 | Tl-201, Tc-99m |  |
| 骨骼 | Tc-99m | 磷酸鹽（MDP）|
| 甲狀腺 | I-131, I-123 |  |
| 肺 | Tc-99m | MAA（粒子）|
| 腎 | Tc-99m | 馬尿酸（Hippuran）|

### SPECT（單光子發射電腦斷層）
- 多角度二維影像 → 電腦重建三維切片

### PET（正子發射電腦斷層）
- 使用正子同位素（+電子）
- 最常用：**FDG（一種葡萄糖類似物）**
- 90% 用於**癌症**分期及治療追蹤
- PET/CT 融合：CT 提供解剖定位，PET 提供代谢/生化資訊

### 優點
- **功能/代谢成像**領先所有其他模態
- 偵測功能性異常（可用於早期發現）
- CT/fluoroscopy 辐射劑量較低（多數核醫檢查）

### 缺點
- 空間解析較差
- 費用較高
- 患者本身成為輻射源（對其他人有暫時性暴露）

---

## 影像存檔與傳輸系統 / PACS

**PACS = Picture Archiving and Communication System**
- 所有影像電子化存檔
- 各地可即時調閱
- 幾乎完全取代傳統底片

---

## 人工智慧在放射科 / Artificial Intelligence in Radiology

### 監督式學習（Supervised Learning）
- 由人類教學電腦（如 radiologist 標註）
- 電腦學習规则並類化

### 深度學習（Deep Learning）
- 類神經網路自我學習
- 近年快速進展

### 臨床應用
- 輔助偵測病變（如肺結節、骨折）
- 自動量化（如钙化積分）
- 協助 triage
- 工作流程優化

---

## 各模態綜合比較 / Comparison

| 模態 | 輻射 | 優勢 | 劣勢 |
|------|------|------|------|
| **X 光** | 有（低）| 快速、便宜、可攜 | 密度解析有限 |
| **CT** | 有（中-高）| 任意平面、3D | 辐射、費用 |
| **US** | 無 | 安全、可攜、即時 | 操作者依賴、氣/骨阻擋 |
| **MRI** | 無 | 軟組織對比最佳 | 費用、禁忌、幽閉 |
| **透視** | 有（高）| 实时、導引 | 辐射 |
| **核醫** | 有 | 功能成像 | 解析差、費用 |

---

## 臨床要點 / Clinical Key Points

- 五大基本密度：空氣、脂肪、液體/軟組織、鈣化、金屬
- CT 利用 Hounsfield 單位擴大密度解析範圍，並可任意視窗化
- 超音波無輻射，是孕婦、兒童首選；但穿透力受限於骨骼及氣體
- MRI 無游離輻射，軟組織對比最佳；但有金屬禁忌及幽閉問題
- 核子醫學提供功能性/代谢成像，PET/CT 結合解剖與功能
- 人工智慧正在改變放射科的診斷及工作流程

---

> **參考文獻 / Reference:** Herring W. Learning Radiology (5th Ed.) — Recognizing Anything: Past, Present, and Future (Ch. 1). Elsevier.

---

## 圖片出處 / Image References

