# Core Radiology image-fidelity verification

Verified on 2026-11-01 against the supplied textbook page images and OCR text.

## Result

- Body image references: 872
- Missing image files: 0
- Uncovered textbook figure pages: 0
- Visually verified OCR false positives excluded: 12
- Hugo build: 0.166.0, exit 0
- `git diff --check`: clean

## Corrected chapters

- thoracic: GGO and atypical mycobacteria / MAI
- gi: benign cystic splenic lesions and esophagus
- breast: breast metastasis
- nuclear: continuous page alignment from `page-562.png` through `page-600.png`
- neuro: acute stroke and orbit / globe / neck-space block
- ultrasound: XGP / pyonephrosis, fetal abdominal-wall defects, fetal GU tract
- physics: MRI physics page alignment

## False-positive handling

`captions.json` is extracted from the text layer and can mistake lists, table entries, or references for figure captions. Pages visually confirmed to contain no figure are recorded in `verified_no_figure_pages.csv`; `audit_image_coverage.py` excludes only those explicit records.

## Reproduction

```bash
export CR_SOURCE_DIR=/tmp/cr_source
export CR_SITE_DIR="$PWD"
python3 scripts/audit/audit_image_coverage.py
python3 scripts/audit/plan_missing_images.py
python3 scripts/audit/apply_missing_images.py --dry-run
/usr/local/bin/hugo166 --quiet
```
