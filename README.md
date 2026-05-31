# Document Processing Pipeline - Stamp Removal & OCR

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/manuelcruzg78/final_vision/blob/main/notebooks/pipeline_colab.ipynb)

A comprehensive pipeline for processing document images that removes translucent stamps and extracts high-quality text through chromatic pixel classification, intelligent inpainting, and OCR post-processing. Achieves **CER = 10.63%** and **89.37% character accuracy** without GPU requirements.

## Quick Start — 3 Ways

### 1. Command Line (RECOMMENDED — Fastest)

Process any document image with a single command:

```bash
# Clone and setup (once)
git clone <repository-url>
cd final_vision
pip install -r requirements.txt
python -m spacy download es_core_news_sm

# Process your document
python procesar_documento.py ruta/a/tu/imagen.png
```

**Output**: `output/IMAGEN_NAME/` with:
- `evidencias_fase3a.png` — Grid showing stamp detection process
- `detecciones_ocr.png` — Bounding boxes color-coded by confidence (green ≥80%, yellow 50-80%, red <50%)
- `dashboard_metricas.png` — Histogram + metrics table + quality assessment
- `fase_3a/` — Cleaned image without stamp
- `fase_4/` — OCR JSON with text blocks and coordinates
- `consolidated/` — Extracted text (plain) + metrics JSON

**Example**:
```bash
python procesar_documento.py "C:\Documentos\factura.png"
# Creates: output/factura/evidencias_fase3a.png, detecciones_ocr.png, ...
```

### 2. Local Jupyter Notebook

For interactive exploration and fine-tuning parameters:

```bash
jupyter notebook notebooks/pipeline_demo_real.ipynb
```

Then upload your document in Cell 3 (FileUpload widget). See all phases with visualizations.

### 3. Google Colab

Click the badge above. No setup required — ideal for GPU acceleration.

---

### Python API (For Integration)

```python
from pipeline import run_phase_3a, run_phase_4, consolidate_ocr_results

# 1. Remove stamp
result_3a = run_phase_3a("doc.png", "output/phase_3a/")
cleaned = result_3a["output_image"]

# 2. Extract text
result_4 = run_phase_4(cleaned, "output/phase_4/", language="es")
ocr_json = result_4["output_json"]

# 3. Consolidate to TXT + metrics
metrics = consolidate_ocr_results(ocr_json, "output/consolidated/")
print(f"CER: {metrics['text_metrics']['total_characters']}, Confidence: {metrics['ocr_confidence_metrics']['average_percent']:.2f}%")
```

## How It Works

### Phase 3A: Chromatic Stamp Detection + Hybrid Inpainting
Detects stamp pixels by analyzing RGB/HSV properties without neural networks:
- **Chromatic classification**: Categories = TEXTO, SELLO_SATURADO, SELLO_TRANSLUCIDO, MIXTO, FONDO
- **H-Sweep & Block-Sweep**: Spatial filtering to isolate stamp regions
- **Hybrid inpainting**: TELEA for small areas (<5000px), Navier-Stokes for larger areas

**Result**: Cleaned image ready for OCR (~8 seconds per image)

### Phase 4: EasyOCR + Spell Correction + NER
Extracts text from cleaned images using deep learning OCR:
- **EasyOCR** (Spanish): Detects text blocks with confidence scores
- **Levenshtein correction**: Fixes typos by distance ≤2 against dictionary
- **spaCy NER**: Identifies entities (names, dates, organizations)

**Result**: JSON with text blocks, coordinates, and confidence (~9 seconds per image)

### Phase 5: Quality Metrics
Evaluates OCR accuracy against ground truth:
- **CER** (Character Error Rate) = (Substitutions + Deletions + Insertions) / N
- **WER** (Word Error Rate) = same but for words
- Character accuracy = 1 - CER

**Benchmark**: CER = 10.63%, Character Accuracy = 89.37%

## Project Structure

```
final_vision/
├── procesar_documento.py              # Main entry point — process single document
├── pipeline/                          # Public API (importable)
│   ├── __init__.py                   # Exports: run_phase_3a, run_phase_4, consolidate_ocr_results
│   ├── run_phase_3a.py               # Phase 3A orchestrator
│   ├── run_phase_4.py                # Phase 4 orchestrator
│   ├── consolidate_results.py        # Consolidation & metrics
│   ├── run_evaluation.py             # Phase 5 evaluation
│   └── run_full_pipeline.py          # End-to-end pipeline
│
├── src/                               # Implementation modules
│   ├── phase_3a/
│   │   ├── chromatic_separator.py    # RGB/HSV pixel classification
│   │   └── inpainter.py              # TELEA & Navier-Stokes inpainting
│   ├── phase_4/
│   │   ├── ocr_engine.py             # EasyOCR integration
│   │   ├── spell_corrector.py        # Levenshtein correction
│   │   └── entity_validator.py       # spaCy NER
│   ├── phase_5/
│   │   ├── levenshtein_calculator.py # Distance metrics
│   │   ├── cer_wer_evaluator.py      # CER/WER computation
│   │   └── text_normalizer.py        # Text preprocessing
│   ├── data_generation/              # Dataset tools
│   ├── data_utils/                   # Data utilities
│   └── classification/               # Classification helpers
│
├── notebooks/                        # Jupyter notebooks
│   ├── pipeline_colab.ipynb          # Google Colab version (with file upload)
│   ├── pipeline_local.ipynb          # Local Jupyter (file path input)
│   └── pipeline_demo_real.ipynb      # Interactive demo (ipywidgets)
│
├── docs/                             # Documentation
│   ├── INSTALLATION.md               # Setup guide
│   ├── PIPELINE_DOCUMENTATION.md     # Technical details
│   ├── presentacion_resultados.tex   # Beamer presentation (18 slides)
│   ├── plan_desarrollo.md            # Development roadmap
│   └── metodologia_tecnica.md        # Methodology details
│
└── requirements.txt                  # Dependencies
```

## Installation

### Requirements
- **Python 3.8+** 
- **No GPU required** (runs on CPU, slower but works fine)
- **8GB RAM minimum** for EasyOCR model

### One-Time Setup

```bash
git clone <repository-url>
cd final_vision

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy Spanish model (optional, for NER)
python -m spacy download es_core_news_sm
```

The first time you run the pipeline, EasyOCR will download its model (~100MB) automatically.

## Usage

### Process a Document

```bash
python procesar_documento.py "ruta/a/tu/documento.png"
```

**Parameters:**
```bash
python procesar_documento.py imagen.png --salida carpeta/personalizada/
```

### Fine-Tune Parameters

Edit these in `procesar_documento.py` (lines ~130-150):
```python
run_phase_3a(
    input_image_path=...,
    block_size=20,              # Stamp detection block size
    inpainting_method="hybrid", # "hybrid", "telea", or "navier_stokes"
)

run_phase_4(
    input_image_path=...,
    language="es",
    confidence_threshold=0.6,   # OCR confidence cutoff
    levenshtein_threshold=2,    # Max spelling correction distance
)
```

### Batch Processing (50+ images)

```bash
python batch_process_50_images.py
```
Processes 50 random synthetic images with 8 parallel workers. Output: `batch_results/batch_50_images_TIMESTAMP/`

## Key Features

✅ **No GPU Required** — Runs on CPU, ~17s per image  
✅ **Unsupervised Stamp Detection** — No manual annotations needed  
✅ **High Accuracy** — CER = 10.63%, Character Accuracy = 89.37%  
✅ **Visual Evidence** — Grid of detection steps + color-coded confidence boxes  
✅ **Clean Modular Code** — Easy to integrate, extend, or modify  
✅ **Production-Ready** — Error handling, logging, incremental saves  
✅ **Multiple Interfaces** — CLI, Jupyter, Colab, Python API  

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Time per image | 16-20 seconds |
| Phase 3A (stamp removal) | ~8s |
| Phase 4 (OCR) | ~9s |
| Character Error Rate (CER) | 10.63% |
| Character Accuracy | 89.37% |
| Word Error Rate (WER) | 28.76% |
| Avg OCR Confidence | 85.2% |
| Blocks detected per image | 42 |
| GPU required | No |

*Benchmark: 50 synthetic document images, Intel CPU (no GPU)*

## Documentation

- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** — Step-by-step setup for Windows/Mac/Linux and Colab
- **[docs/PIPELINE_DOCUMENTATION.md](docs/PIPELINE_DOCUMENTATION.md)** — Technical deep-dive: architecture, phases, API reference
- **[docs/presentacion_resultados.tex](docs/presentacion_resultados.tex)** — Beamer presentation contrasting methodologies
- **[docs/plan_desarrollo.md](docs/plan_desarrollo.md)** — Development roadmap and milestones
- **[docs/metodologia_tecnica.md](docs/metodologia_tecnica.md)** — Detailed methodology and implementation notes

## Examples

### Example 1: Process a single document

```bash
python procesar_documento.py "C:\Users\manue\Documentos\factura.png"
```

Output files in `output/factura/`:
- `evidencias_fase3a.png` — Shows 6 intermediate steps of stamp detection
- `detecciones_ocr.png` — Text boxes colored by confidence
- `dashboard_metricas.png` — Metrics visualization
- `consolidated/ocr_extracted_text.txt` — Plain extracted text
- `consolidated/ocr_metrics.json` — Detailed metrics

### Example 2: Use in your Python code

```python
from pipeline import run_full_pipeline
from pathlib import Path

# Process document
result = run_full_pipeline(
    image_path="documento.png",
    output_dir="resultados/",
    language="es"
)

# Access results
print(f"Extracted {result['text_blocks']} blocks")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Cleaned image: {result['cleaned_image']}")
```

### Example 3: Jupyter with visualization

See `notebooks/pipeline_demo_real.ipynb` — upload documents interactively and view:
- Phase 3A detection grid
- OCR bounding boxes with confidence colors
- Metrics dashboard
- Extracted text preview

## Common Issues

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError: No module named 'easyocr'" | `pip install easyocr` |
| "NumPy 2.x incompatibility" | `pip install "numpy<2"` |
| "No module named 'spacy'" | `pip install spacy && python -m spacy download es_core_news_sm` |
| Widget not showing in Jupyter | `pip install ipywidgets && jupyter nbextension enable --py widgetsnbextension` |
| First run takes 5 minutes | EasyOCR is downloading model (~100MB), wait for completion |

## Contributing

This project is developed as part of a graduate research thesis at Universidad del Rosario. Fork, modify, and submit pull requests!

## Citation

If you use this pipeline in academic work, cite:

```bibtex
@thesis{cruz2025ocr,
  author = {Cruz Garrote, Manuel},
  title = {Automatic Stamp Detection and Removal in Document Images},
  school = {Universidad del Rosario},
  year = {2025}
}
```

## Author

**Manuel Cruz Garrote**  
Universidad del Rosario  
Email: manuelcruzg78@gmail.com  

---

**Status**: Production | **Version**: 1.1 | **Last Updated**: May 2025
