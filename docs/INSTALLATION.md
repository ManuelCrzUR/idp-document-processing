# Installation & Setup Guide

**Document Stamp Removal + OCR Pipeline**

---

## 📋 System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 8GB
- **Disk**: ~2GB for dependencies + models
- **GPU**: Optional (significantly speeds up EasyOCR on first run)
- **OS**: Windows, macOS, or Linux

No GPU is required — the pipeline works perfectly on CPU.

---

## 🚀 Option 1: Google Colab (Recommended for First Time)

**Fastest way to get started — no installation needed.**

1. **Open the notebook**: 
   - Click the badge in the README, OR
   - [Open directly in Colab](https://colab.research.google.com/github/YOUR_USERNAME/final_vision/blob/main/notebooks/pipeline_colab.ipynb)

2. **Run cells top-to-bottom**:
   - Cell 1: Install dependencies (~5 min, first time only)
   - Cells 2+: Upload document → Process → Download results

3. **First run notes**:
   - EasyOCR downloads Spanish model on first Phase 4 run (~100MB, ~5 min)
   - Subsequent runs are much faster
   - Colab may restart between cells — it's normal

**No further setup needed.**

---

## 💻 Option 2: Local Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/final_vision.git
cd final_vision
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Core: numpy, opencv-python-headless, PIL, matplotlib
- OCR: easyocr
- Text processing: spacy, textdistance
- Config: PyYAML, tqdm, tabulate

### Step 4: Download Optional spaCy Model (for NER)

```bash
python -m spacy download es_core_news_sm
```

This enables Named Entity Recognition (optional but recommended).

### Step 5: Verify Installation

```bash
python -c "from pipeline import run_phase_3a, run_phase_4, consolidate_ocr_results; print('[OK] Pipeline ready')"
```

Expected output: `[OK] Pipeline ready`

---

## 📖 How to Run

### Option A: CLI (Command Line)

Process a single document:

```bash
python execute_full_pipeline.py --input path/to/document.png
```

With ground truth for evaluation:
```bash
python execute_full_pipeline.py --input path/to/document.png --ground_truth /path/to/ground_truth_dir
```

Or via environment variable:
```bash
export GT_DIR=/path/to/ground_truth_dir
python execute_full_pipeline.py --input path/to/document.png
```

### Option B: Jupyter Notebook (Local)

**Start Jupyter:**
```bash
jupyter notebook
```

**Open:** `notebooks/pipeline_local.ipynb`

**Configure:** 
- Line 1 of first cell: `INPUT_IMAGE = "path/to/your/document.png"`
- Run all cells

### Option C: Python API

```python
import sys
sys.path.insert(0, '/path/to/final_vision')

from pipeline import run_phase_3a, run_phase_4, consolidate_ocr_results

# Phase 3A: Stamp Removal
result_3a = run_phase_3a(
    input_image_path="document.png",
    output_dir="output/phase_3a/",
    block_size=20,
    inpainting_method="hybrid",
    save_intermediate=True
)

# Phase 4: OCR Extraction
result_4 = run_phase_4(
    input_image_path=result_3a["output_image"],
    output_dir="output/phase_4/",
    language="es"
)

# Consolidate: Text to TXT + Metrics to JSON
metrics = consolidate_ocr_results(
    ocr_json_path=result_4["output_json"],
    output_dir="output/consolidated/"
)
```

---

## 🔍 Verify Each Component

### Check Python installation:
```bash
python --version
# Should be 3.8+
```

### Check OpenCV:
```bash
python -c "import cv2; print(f'OpenCV {cv2.__version__}')"
```

### Check EasyOCR:
```bash
python -c "import easyocr; print('[OK] EasyOCR ready')"
```

### Check spaCy (optional):
```bash
python -m spacy download es_core_news_sm
python -c "import spacy; nlp = spacy.load('es_core_news_sm'); print('[OK] spaCy ready')"
```

### Full pipeline test:
```bash
python -c "from pipeline import *; print('[OK] All imports successful')"
```

---

## ⚠️ Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'cv2'`

**Solution:**
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python-headless>=4.5.0
```

Note: Never install both `opencv-python` and `opencv-python-headless` together.

---

### Issue: EasyOCR takes forever to download models

**Cause:** First run downloads Spanish language model (~100MB)

**Solution:** This is normal. Wait 5-10 minutes. Models cache for future runs.

To pre-download manually:
```bash
python -c "import easyocr; reader = easyocr.Reader(['es'])"
```

---

### Issue: spaCy model not found error

**Solution:**
```bash
python -m spacy download es_core_news_sm
```

If you skip this, the pipeline still works — NER features just disabled.

---

### Issue: `Cannot import name 'run_phase_3a'` when using pipeline API

**Cause:** Python path not configured correctly

**Solution:** Ensure this is in your script BEFORE imports:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))  # Adjust path to repo root
from pipeline import run_phase_3a, run_phase_4
```

---

### Issue: Permission denied on Linux/Mac

**Solution:** Add execute permission:
```bash
chmod +x notebooks/pipeline_colab.ipynb
```

---

### Issue: `CUDA out of memory` (if you have GPU)

**Solution:** The pipeline uses CPU by default. No action needed.

To explicitly disable CUDA in EasyOCR:
```python
result = run_phase_4(input_image, output_dir, gpu=False)
```

---

## 📦 Uninstall / Clean Up

**Remove virtual environment:**
```bash
# Windows
rmdir venv /s /q

# macOS/Linux  
rm -rf venv/
```

**Clean cached models:**
```bash
# EasyOCR cache
rm -rf ~/.EasyOCR/

# spaCy cache
python -m spacy download es_core_news_sm --force-all
```

---

## 🆘 Still Having Issues?

1. **Check Python version:** `python --version` must be 3.8+
2. **Verify venv is activated:** Prompt should show `(venv)` prefix
3. **Re-install dependencies:** `pip install -r requirements.txt --force-reinstall`
4. **Check GPU drivers** (if using GPU): `nvidia-smi`
5. **Open GitHub issues** with: Python version, OS, error message, and steps to reproduce

---

## 📋 Minimal Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt` completed without errors
- [ ] `python -m spacy download es_core_news_sm` completed (optional)
- [ ] `python -c "from pipeline import run_phase_3a, run_phase_4; print('OK')"` works
- [ ] Sample test document available
- [ ] Output directory writable

✅ **If all checks pass, you're ready to go!**

---

## Next Steps

- **First time?** Open `notebooks/pipeline_colab.ipynb` and run all cells
- **Want more details?** Read `docs/PIPELINE_DOCUMENTATION.md`
- **Have a document to process?** Use the Jupyter notebook or CLI as shown above

---

**Questions?** Check the docs or open an issue on GitHub.
