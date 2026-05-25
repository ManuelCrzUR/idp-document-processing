# Pipeline Technical Documentation

**Complete reference for all phases, parameters, and outputs**

---

## 📐 Architecture Overview

```
INPUT IMAGE (PNG/JPG)
    ↓
[PHASE 3A] Stamp Removal
├─ Chromatic pixel classification → 5 categories
├─ Horizontal sweep filter → rows without text cleared
├─ Block sweep filter (20×20) → blocks without text cleared  
├─ Intelligent inpainting → OpenCV or LaMa
└─ Output: cleaned_image.png + 10 evidence images

    ↓
[PHASE 4] OCR & Text Extraction
├─ EasyOCR: detect text blocks with bounding boxes
├─ Spell correction: Levenshtein-based word fixing
├─ NER: Named Entity Recognition (spaCy)
└─ Output: ocr_results.json with full text + metrics

    ↓
[CONSOLIDATE] Extract & Metrics
├─ Extract plain text to .txt
└─ Generate comprehensive metrics JSON

    ↓
[PHASE 5] Evaluation (Optional)
├─ Compare OCR output vs. ground truth
├─ Calculate CER (Character Error Rate)
├─ Calculate WER (Word Error Rate)
└─ Output: evaluation_results.json with metrics
```

---

## Phase 3A: Stamp Removal & Inpainting

### Purpose

Identifies and removes translucent stamps from document images using intelligent inpainting.

### Function Signature

```python
def run_phase_3a(
    input_image_path: str,           # Path to document with stamp
    output_dir: str,                 # Where to save results
    stamp_bbox: tuple = None,        # (xc_norm, yc_norm, w_norm, h_norm) or (x1,y1,x2,y2)
    block_size: int = 20,            # Block size for filtering (pixels)
    inpainting_method: str = "hybrid", # "lama", "opencv", or "hybrid"
    save_intermediate: bool = True,  # Save all 10 evidence images
) -> dict
```

### Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `input_image_path` | str | required | Full path to document (PNG/JPG) |
| `output_dir` | str | required | Directory for all outputs |
| `stamp_bbox` | tuple | None | Stamp region. If None, processes whole image. Format: `(xc_norm, yc_norm, w_norm, h_norm)` (0–1 normalized) or `(x1, y1, x2, y2)` (absolute pixels) |
| `block_size` | int | 20 | Size of blocks for filtering. Larger = coarser filtering. Range: 10–50 |
| `inpainting_method` | str | "hybrid" | "opencv" (fast, basic), "lama" (slower, better, needs torch), or "hybrid" (opencv fallback) |
| `save_intermediate` | bool | True | Save all 10 intermediate images for debugging/visualization |

### How It Works

**Step 1: Pixel Classification**

Each pixel is classified into one of 5 categories based on RGB values:

| Category | Color | Meaning | Example |
|----------|-------|---------|---------|
| TEXTO (0) | Black | Text pixels | Document text, black ink |
| SELLO_SATURADO (1) | Red | Saturated seal pixels | Stamp core, bright red seal |
| MIXTO (2) | Yellow | Mixed text + seal | Stamp edge over text |
| FONDO (3) | White | Background | Paper, white space |
| SELLO_TRANSLUCIDO (4) | Blue | Translucent seal | Faint stamp overlay |

Thresholds in `config/pipeline_config.yaml`:
- `chromatic_threshold`: Default 50 (pixel intensity for TEXTO classification)
- `dominance_threshold`: Default 0.3 (RGB channel dominance for classification)

**Step 2: Horizontal Sweep Filter**

- Scans each row of the stamp ROI
- If row has NO TEXTO pixels → mark entire row for removal
- Removes: SELLO_SATURATED, MIXTO, SELLO_TRANSLUCIDO
- Keeps: TEXTO and FONDO

Result: removes large stamp areas while preserving text.

**Step 3: Block Sweep Filter**

- Divides remaining region into 20×20 blocks
- If block has NO TEXTO pixels → mark entire block for removal
- More aggressive cleanup of remaining stamp fragments
- Configurable: change `block_size` parameter for finer/coarser filtering

**Step 4: Final Inpainting**

Reconstructs pixels marked for removal using context from surrounding pixels.

- **`inpainting_method="opencv"`**: Uses OpenCV Telea/NL Means algorithm. Fast (~1 sec), good for small stamps.
- **`inpainting_method="lama"`**: Uses Meta LaMa (state-of-art). Slow (~30 sec) but preserves text better. Requires torch.
- **`inpainting_method="hybrid"`** (default): Tries LaMa, falls back to OpenCV if torch unavailable.

### Output Files

When `save_intermediate=True`, saves 10 images to `output_dir/`:

| File # | Name | Visual | Purpose |
|--------|------|--------|---------|
| 1a | `01_pixel_classification.png` | RGB overlay: colors per category | Verify pixel classification accuracy |
| 1b | `01_initial_mask.png` | Red (inpaint) vs white (keep) | Initial mask before filtering |
| 2a | `02_after_hsweep_classification.png` | RGB overlay after horizontal filter | Verify row-level filtering |
| 2b | `02_after_hsweep_mask.png` | Red/white after hsweep | Pixels cleared by hsweep |
| 3a | `03_after_bsweep_classification.png` | RGB overlay after block filter | Verify block-level filtering |
| 3b | `03_after_bsweep_mask.png` | Red/white after bsweep | Pixels cleared by bsweep |
| 3c | `03_block_grid_overlay.png` | Grid with green (kept) + red (removed) blocks | Block-level decision visualization |
| 4 | `04_final_inpaint_mask.png` | Final red/white mask | Exact pixels sent to inpainting |
| 5a | `cleaned_image.png` | **Main output** | Document with stamp removed |
| 5b | `05_comparison_before_after.png` | Side-by-side: original | before/cleaned | after | Visual verification |

### Return Dictionary

```python
{
    "success": bool,                 # True if Phase 3A completed
    "output_image": str,             # Path to cleaned_image.png
    "blocks_processed": int,         # Total pixels in ROI
    "pixels_inpainted": int,         # Pixels reconstructed
    "inpainting_method": str,        # "lama", "opencv", or "hybrid"
    "summary": {
        "input_image": str,
        "output_image": str,
        "stamp_roi": {               # Stamp bounding box
            "x1": int, "y1": int, "x2": int, "y2": int
        },
        "block_size": int,
        "inpainting_method": str,
        "pixel_classification": {
            "initial": {             # Before any filtering
                "TEXTO": int,
                "SELLO_SATURADO": int,
                "MIXTO": int,
                "FONDO": int,
                "SELLO_TRANSLUCIDO": int
            },
            "after_horizontal_sweep": {  # After hsweep
                ...
            },
            "after_block_sweep": {       # After bsweep
                ...
            }
        },
        "block_filtering": {
            "total_blocks": int,
            "blocks_kept": int,
            "blocks_removed": int
        },
        "final_mask": {
            "inpaint_pixels": int,
            "percentage": str       # % of ROI inpainted
        }
    }
}
```

### Usage Examples

**Basic usage:**
```python
from pipeline import run_phase_3a

result = run_phase_3a(
    input_image_path="documents/contract.png",
    output_dir="output/phase_3a/"
)

if result["success"]:
    cleaned = result["output_image"]
    print(f"Pixels inpainted: {result['pixels_inpainted']}")
```

**Fine-tuning parameters:**
```python
# For heavy stamp coverage, use larger blocks
result = run_phase_3a(
    input_image_path="doc.png",
    output_dir="output/",
    block_size=30,  # Coarser filtering
    inpainting_method="lama"  # Better quality
)
```

**Without visual evidence:**
```python
# For faster execution, skip intermediate images
result = run_phase_3a(
    input_image_path="doc.png",
    output_dir="output/",
    save_intermediate=False  # No 10 images, just cleaned_image.png
)
```

---

## Phase 4: OCR & Text Extraction

### Purpose

Extract text from document images using EasyOCR, then apply spell correction and Named Entity Recognition.

### Function Signature

```python
def run_phase_4(
    input_image_path: str,           # Path to document (from Phase 3A or original)
    output_dir: str,                 # Where to save ocr_results.json
    language: str = "es",            # OCR language code ("es" = Spanish)
    confidence_threshold: float = 0.6, # Min confidence to include block
    levenshtein_threshold: int = 2,  # Max edit distance for spell correction
    seal_bbox: tuple = None,         # (xc_norm, yc_norm, w_norm, h_norm)
) -> dict
```

### Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `input_image_path` | str | required | Document image path |
| `output_dir` | str | required | Output directory for ocr_results.json |
| `language` | str | "es" | Language code: "es" (Spanish), "en" (English), etc. |
| `confidence_threshold` | float | 0.6 | Blocks below this confidence are marked `baja_confianza`. Range: 0–1 |
| `levenshtein_threshold` | int | 2 | Max character edits for spell correction. Higher = more corrections |
| `seal_bbox` | tuple | None | Seal region (normalized coords). Blocks here marked `en_zona_sello=True` |

### How It Works

**Step 1: EasyOCR Detection**

- Reads image and detects text regions
- Returns: bounding box coordinates (4 corner points) + confidence score + detected text
- Supports 80+ languages out of the box

**Step 2: Confidence Filtering**

Blocks are marked:
- `baja_confianza = True` if confidence < threshold
- `baja_confianza = False` if confidence ≥ threshold

Low-confidence blocks are still kept in output but flagged for review.

**Step 3: Spell Correction**

Uses Levenshtein distance to fix OCR errors:
- Compares detected words against Spanish vocabulary
- If edit distance ≤ `levenshtein_threshold`, suggests correction
- Automatically applies if correction is high-confidence
- Disabled if textdistance package unavailable (graceful fallback)

**Step 4: Named Entity Recognition (NER)**

Uses spaCy's Spanish model to identify:
- **PERSON**: Names of people
- **ORG**: Organizations, companies
- **DATE**: Dates and time expressions
- **MONEY**: Currency amounts
- **GPE**: Geographic locations

Entidades are attached to each block + tallied in metrics.

Disabled if spacy unavailable (graceful fallback).

### Output Files

Phase 4 generates exactly one file: `ocr_results.json`

**Full structure:**

```json
{
  "timestamp": "2026-05-25T14:30:00.000Z",
  "imagen_size": {
    "width": 2550,
    "height": 3300
  },
  "seal_bbox": null,
  "texto_completo": "Full extracted text...\nMulti-line string with all blocks concatenated.",
  
  "bloques": [
    {
      "id": 1,
      "texto_raw": "Original OCR detection",
      "texto_corregido": "Original OCR detection",  // After spelling
      "confianza": 0.92,
      "baja_confianza": false,
      "motor": "EasyOCR",
      "coordenadas": [
        [100, 50],    // Top-left
        [500, 50],    // Top-right
        [500, 80],    // Bottom-right
        [100, 80]     // Bottom-left
      ],
      "en_zona_sello": false,
      "overlap_sello": 0.0,
      "palabras_parciales": [],
      "fue_corregido": false,
      "distancia_correccion": 0,
      "entidades": []  // NER results
    },
    // ... more blocks
  ],
  
  "metricas": {
    "total_bloques": 152,
    "confianza_promedio": 0.8312,
    "palabras_corregidas": 55,
    "entidades_detectadas": 17,
    "confianza_threshold": 0.6,
    "motores_usados": ["EasyOCR"],
    "procesadores_usados": ["Levenshtein", "spaCy"]
  }
}
```

### Coordinate System

Each block has `coordenadas` = list of 4 points (x, y) in image pixel coordinates:

```
[Top-Left, Top-Right, Bottom-Right, Bottom-Left]
```

Example: `[[100, 50], [500, 50], [500, 80], [100, 80]]`
- Top-left corner: (100, 50)
- Width: 500 - 100 = 400px
- Height: 80 - 50 = 30px

### Return Dictionary

```python
{
    "success": bool,                 # True if OCR completed
    "output_json": str,              # Path to ocr_results.json
    "text_blocks": int,              # Count of detected blocks
    "confidence": float,             # Average confidence (0–1)
    "words_corrected": int,          # Words fixed by spell check
    "entities": int,                 # Entities detected by NER
    "text_length": int,              # Characters in texto_completo
}
```

### Usage Examples

**Default Spanish OCR:**
```python
from pipeline import run_phase_4

result = run_phase_4(
    input_image_path="cleaned.png",
    output_dir="output/phase_4/"
)

# Access full JSON
with open(result["output_json"]) as f:
    ocr_data = json.load(f)
    print(f"Extracted {result['text_blocks']} blocks")
    print(f"Confidence: {result['confidence']:.2%}")
```

**English documents:**
```python
result = run_phase_4(
    input_image_path="doc.png",
    output_dir="output/",
    language="en"
)
```

**Stricter confidence filtering:**
```python
result = run_phase_4(
    input_image_path="doc.png",
    output_dir="output/",
    confidence_threshold=0.75  # Only high-confidence blocks included
)
```

---

## Consolidate: Extract Text & Generate Metrics

### Purpose

Converts OCR JSON to plain text file and generates comprehensive metrics report.

### Function Signature

```python
def consolidate_ocr_results(
    ocr_json_path: str,    # Path to ocr_results.json from Phase 4
    output_dir: str        # Where to save .txt and metrics.json
) -> dict                  # Returns metrics dictionary
```

### Output Files

**1. `ocr_extracted_text.txt`**

Plain text file with:
- Full extracted text (texto_completo)
- Footer with character/word/block counts

```
OCR EXTRACTED TEXT
====================================================================================================

<Full text from OCR...>

====================================================================================================
Total characters: 3,546
Total words: 534
Total blocks: 152
```

**2. `ocr_metrics.json`**

Comprehensive metrics:

```json
{
  "text_metrics": {
    "total_characters": 3546,
    "total_words": 534,
    "total_lines": 42,
    "total_blocks": 152,
    "unique_words": 378,
    "average_word_length": 6.64,
    "character_per_block": 23.33
  },
  
  "ocr_confidence_metrics": {
    "average": 0.8312,
    "average_percent": 83.12,
    "min": 0.42,
    "max": 0.99,
    "distribution": {
      "0.0-0.2": 0,
      "0.2-0.4": 3,
      "0.4-0.6": 12,
      "0.6-0.8": 45,
      "0.8-1.0": 92
    },
    "blocks_with_high_confidence": 92,       // ≥ 0.8
    "blocks_with_medium_confidence": 45,     // 0.5–0.8
    "blocks_with_low_confidence": 15         // < 0.5
  },
  
  "post_processing_metrics": {
    "words_corrected": 55,
    "entities_detected": 17,
    "correction_rate": 10.30,     // % of words corrected
    "entity_rate": 11.18          // entities per block
  },
  
  "engines_and_processors": {
    "ocr_engines": ["EasyOCR"],
    "processors": ["Levenshtein", "spaCy"]
  }
}
```

### Return Value

The function returns the `ocr_metrics_json` dictionary (same as in .json file).

### Usage

```python
from pipeline import consolidate_ocr_results

metrics = consolidate_ocr_results(
    ocr_json_path="output/phase_4/ocr_results.json",
    output_dir="output/consolidated/"
)

# Access metrics
print(f"Words: {metrics['text_metrics']['total_words']}")
print(f"Confidence: {metrics['ocr_confidence_metrics']['average_percent']:.1f}%")
```

---

## Phase 5: Evaluation (Optional)

### Purpose

Compare OCR output against ground truth to calculate accuracy metrics (CER, WER).

### CER (Character Error Rate)

Measures character-level accuracy using Levenshtein distance:

```
CER = (Insertions + Deletions + Substitutions) / Reference Characters × 100%
```

**Examples:**
- `CER = 5%` → 95% of characters are correct (Excellent)
- `CER = 10%` → 90% correct (Very Good)
- `CER = 20%` → 80% correct (Good)
- `CER > 30%` → Needs improvement

### WER (Word Error Rate)

Measures word-level accuracy (same formula as CER, applied to words):

```
WER = (Word edits) / Reference Words × 100%
```

Higher than CER because a single character mistake can break an entire word.

### Function Signature

```python
def run_evaluation(
    ocr_results_dir: str,        # Directory with ocr_results.json files
    ground_truth_dir: str,       # Directory with .txt ground truth files
    output_dir: str,             # Where to save evaluation results
    doc_mapping: dict = None     # Mapping {doc_id: (ocr_json, gt_txt)}
) -> dict
```

### Usage

```python
from pipeline import run_evaluation

result = run_evaluation(
    ocr_results_dir="output/phase_4/",
    ground_truth_dir="/data/ground_truth/",
    output_dir="output/phase_5/"
)

# Access results
eval_data = json.load(open(result["output_json"]))
for doc_id, metrics in eval_data.items():
    print(f"{doc_id}: CER={metrics['cer']:.2%}, WER={metrics['wer']:.2%}")
```

### Output

- `evaluation_results.json`: CER/WER for each document
- `evaluation_results.csv`: Same in spreadsheet format

---

## 🎯 Quick Reference: CLI Commands

### Phase 3A only:
```bash
python pipeline/run_phase_3a.py --input doc.png --output output/3a/
```

### Phase 4 only:
```bash
python pipeline/run_phase_4.py --input doc.png --output output/4/
```

### All phases (full pipeline):
```bash
python execute_full_pipeline.py --input doc.png
```

With ground truth:
```bash
python execute_full_pipeline.py --input doc.png --ground_truth /path/to/gt/
```

### See all options:
```bash
python execute_full_pipeline.py --help
```

---

## 📊 Configuration

Edit `config/pipeline_config.yaml` to tune Phase 3A thresholds:

```yaml
phase_3a:
  chromatic_threshold: 50          # Brightness threshold for TEXTO
  dominance_threshold: 0.3         # RGB channel dominance
  horizontal_sweep:
    enabled: true
  block_sweep:
    enabled: true
    block_size: 20                 # Configurable here too
  inpainting:
    method: hybrid                 # lama, opencv, hybrid
```

---

## 🔗 Related Files

- **Entry points**: `pipeline/run_phase_3a.py`, `run_phase_4.py`, `run_evaluation.py`, `run_full_pipeline.py`
- **Core modules**: `src/phase_3a/`, `src/phase_4/`, `src/phase_5/`
- **Visualization**: `create_comparison_image.py` (draw OCR blocks on image)
- **Configuration**: `config/pipeline_config.yaml`

---

## 💡 Tips & Tricks

1. **Processing large batches**: Use `run_full_pipeline()` API for automation
2. **Debugging Phase 3A**: Check intermediate images to tune parameters
3. **Low OCR confidence**: Try increasing `block_size` in Phase 3A (less aggressive)
4. **Slow performance**: Use `save_intermediate=False` to skip image saves
5. **Better OCR results**: Increase image resolution before Phase 4 (300+ DPI recommended)

---

**For more examples, see `notebooks/pipeline_colab.ipynb` and `notebooks/pipeline_local.ipynb`**
