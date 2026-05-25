# Document Processing Pipeline - Stamp Removal & OCR

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/final_vision/blob/main/notebooks/pipeline_colab.ipynb)

A comprehensive pipeline for processing document images that removes translucent stamps and extracts high-quality text through intelligent inpainting and OCR post-processing.

## Quick Start

### Google Colab (Recommended)
Click the badge above or [open the Colab notebook](https://colab.research.google.com/github/YOUR_USERNAME/final_vision/blob/main/notebooks/pipeline_colab.ipynb). Run cells top-to-bottom:
1. Install dependencies
2. Clone repository  
3. Upload your document
4. Watch the pipeline execute (stamp removal → OCR → metrics)
5. Download results as ZIP

No local setup required.

### Local Installation
```bash
git clone <repository-url>
cd final_vision
pip install -r requirements.txt
python -m spacy download es_core_news_sm  # Optional, for NER

# Process a document
python execute_full_pipeline.py --input path/to/document.png
```

### Python API
```python
from pipeline import run_phase_3a, run_phase_4, consolidate_ocr_results

# 1. Remove stamp
result_3a = run_phase_3a("doc.png", "output/phase_3a/")
cleaned = result_3a["output_image"]

# 2. Extract text
result_4 = run_phase_4(cleaned, "output/phase_4/")
ocr_json = result_4["output_json"]

# 3. Consolidate to TXT + metrics JSON
metrics = consolidate_ocr_results(ocr_json, "output/consolidated/")
```

## Overview

This project implements a multi-phase document processing system:

- **Phase 3A**: Stamp Detection & Removal using chromatic separation and intelligent inpainting
- **Phase 4**: Text Extraction & Correction via EasyOCR and Levenshtein-based spell correction
- **Phase 5**: Quality Evaluation with CER/WER metrics and entity validation

## Project Structure

```
src/
├── classification/                    # Stamp classification
│   └── stamp_classifier.py           # RGB-based stamp detection
├── data_generation/                   # Dataset preparation
│   ├── generate_synthetic_dataset.py  # Synthetic document generation
│   └── prepare_yolo_dataset.py       # YOLO annotation format
├── data_utils/                        # Data utilities
│   ├── data_registry.py              # Dataset catalog
│   └── extract_samples.py            # Sample extraction
├── phase_3a/                          # Stamp removal
│   ├── chromatic_separator.py        # Chromatic-based separation
│   └── inpainter.py                  # LaMa/OpenCV inpainting
├── phase_4/                           # OCR & post-processing
│   ├── ocr_engine.py                 # EasyOCR integration
│   ├── spell_corrector.py            # Levenshtein-based correction
│   └── entity_validator.py           # spaCy NER validation
├── phase_5/                           # Evaluation metrics
│   ├── cer_wer_evaluator.py          # CER/WER metrics
│   ├── levenshtein_calculator.py     # Levenshtein distance
│   └── text_normalizer.py            # Text preprocessing
├── pipeline/                          # Main pipeline modules
│   ├── chromatic_separator.py        # Chromatic separation
│   ├── lama_inpainter.py             # LaMa inpainting
│   ├── phase_3a_complete.py          # Phase 3A orchestrator
│   ├── phase_4_ocr_complete.py       # Phase 4 orchestrator
│   └── phase_5a_evaluation.py        # Phase 5A evaluator
└── training/                          # Model training utilities
    └── test_train_speed.py           # Training benchmarks

config/
└── pipeline_config.yaml              # Configuration parameters
```

## Installation

### Requirements
- Python 3.8+
- CUDA 11.8+ (for GPU acceleration)

### Setup

```bash
# Clone repository
git clone <repository-url>
cd final_vision

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Configuration

Edit `config/pipeline_config.yaml` to adjust parameters:
- Chromatic thresholds for stamp detection
- Inpainting method (LaMa or OpenCV)
- OCR confidence thresholds
- Entity validation rules

### Running Phases

**Phase 3A - Stamp Removal:**
```bash
python src/pipeline/phase_3a_complete.py --input document.png --output output/
```

**Phase 4 - OCR & Correction:**
```bash
python src/pipeline/phase_4_ocr_complete.py --input cleaned.png --output output/
```

**Phase 5A - Evaluation:**
```bash
python src/pipeline/phase_5a_evaluation.py --ocr_results results.json --ground_truth ground_truth/
```

## Key Features

- **Chromatic-based Stamp Detection**: Identifies stamp pixels using RGB/HSV color spaces
- **Intelligent Inpainting**: Removes stamps with minimal text degradation
- **Post-OCR Correction**: Character and word-level error correction using Levenshtein distance
- **Entity Validation**: Validates extracted entities (names, dates, amounts) using spaCy NER
- **Production-Ready**: Clean, modular, well-documented code
- **Configuration-Driven**: Easy parameter tuning via YAML

## Configuration Reference

Key parameters in `config/pipeline_config.yaml`:

```yaml
chromatic_separation:
  magenta_threshold: 200      # Magenta detection threshold
  cyan_threshold: 150         # Cyan detection threshold

inpainting:
  method: lama                # 'lama' or 'opencv'
  lama_model: lama2.pt        # LaMa model path

ocr:
  languages: ['es']           # OCR languages
  confidence_threshold: 0.5   # Confidence cutoff

spell_correction:
  max_distance: 2             # Max Levenshtein distance

evaluation:
  cer_weight: 0.6            # CER metric weight
  wer_weight: 0.4            # WER metric weight
```

## Documentation

- `SETUP.md` - Detailed setup instructions
- `docs/plan_desarrollo.md` - Development roadmap
- `docs/metodologia_tecnica.md` - Technical methodology

## Author

Manuel Cruz Garrote - Universidad del Rosario

---

**Status**: Production | **Version**: 1.0
