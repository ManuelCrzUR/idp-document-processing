# Setup and Installation Guide

Complete guide for setting up the OCR Pipeline project.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ocr-stamp-removal.git
cd ocr-stamp-removal
```

### 2. Create Virtual Environment

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy Models (Required)

For Spanish NER support:
```bash
python -m spacy download es_core_news_sm
```

For English NER support:
```bash
python -m spacy download en_core_web_sm
```

### 5. Optional: Install LaMa Inpainting

If you want to use LaMa for advanced inpainting:

```bash
# Uncomment lama-cleaner and torch in requirements.txt, then:
pip install lama-cleaner
# Note: This installs PyTorch (~2GB), which may take time
```

## Project Structure

```
final_vision/
├── README.md                          # Project overview
├── SETUP.md                          # This file
├── LICENSE                           # MIT License
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore rules
├── config/
│   └── pipeline_config.yaml         # Configuration parameters
├── src/
│   ├── __init__.py
│   ├── classification/              # Stamp classification
│   │   └── stamp_classifier.py      # RGB-based classifier
│   ├── data_generation/             # Dataset generation
│   ├── data_utils/                  # Data utilities
│   ├── phase_3a/                    # Stamp removal
│   │   ├── chromatic_separator.py   # Chromatic separation
│   │   └── inpainter.py             # LaMa/OpenCV inpainting
│   ├── phase_4/                     # OCR and correction
│   │   ├── ocr_engine.py            # EasyOCR wrapper
│   │   ├── spell_corrector.py       # Levenshtein correction
│   │   └── entity_validator.py      # spaCy NER
│   ├── phase_5/                     # Evaluation
│   │   ├── levenshtein_calculator.py # Levenshtein distance
│   │   ├── text_normalizer.py       # Text preprocessing
│   │   └── cer_wer_evaluator.py     # CER/WER calculation
│   ├── pipeline/                    # Main pipeline modules
│   │   ├── phase_3a_complete.py     # Phase 3A orchestrator
│   │   ├── phase_4_ocr_complete.py  # Phase 4 orchestrator
│   │   └── phase_5a_evaluation.py   # Phase 5A evaluator
│   └── training/                    # Training utilities
├── docs/
│   ├── plan_desarrollo.md           # Development roadmap
│   └── metodologia_tecnica.md       # Technical methodology
└── config/
    └── pipeline_config.yaml         # Configuration file
```

## Usage

### Quick Test

Run a single image through the full pipeline:

```bash
python pipeline/run_full_pipeline.py \
    --input /path/to/document.png \
    --output ./results/ \
    --language es
```

### Individual Phases

**Phase 3A Only (Stamp Removal):**
```bash
python pipeline/run_phase_3a.py \
    --input document.png \
    --output ./results/phase_3a/
```

**Phase 4 Only (OCR):**
```bash
python pipeline/run_phase_4.py \
    --input cleaned_document.png \
    --output ./results/phase_4/ \
    --language es
```

**Phase 5 Only (Evaluation):**
```bash
python pipeline/run_evaluation.py \
    --ocr_results ./results/phase_4/ \
    --ground_truth ./data/ground_truth/ \
    --output ./results/phase_5/
```

### Configuration

Edit `config/pipeline_config.yaml` to customize:
- Block size for Phase 3A
- OCR language for Phase 4
- Spelling correction threshold
- CER/WER evaluation parameters

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'easyocr'"

**Solution**: Install EasyOCR
```bash
pip install easyocr
```

### Issue: "No model named 'es_core_news_sm'"

**Solution**: Download the spaCy model
```bash
python -m spacy download es_core_news_sm
```

### Issue: "CUDA out of memory" when using EasyOCR

**Solution**: The pipeline uses CPU by default. If you have GPU:
1. Install CUDA-compatible versions
2. Modify `src/phase_4/ocr_engine.py` to use GPU

### Issue: LaMa inpainting not working

**Solution**: LaMa requires PyTorch. Install it:
```bash
pip install torch torchvision torchaudio
pip install lama-cleaner
```

The pipeline will automatically fall back to OpenCV inpainting if LaMa fails.

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_phase_4.py

# Run with coverage
pytest --cov=src --cov-report=html
```

## Performance Notes

- **Phase 3A**: ~30-60 seconds per image (depends on size and inpainting method)
- **Phase 4**: ~10-20 seconds per image (EasyOCR with CPU)
- **Phase 5**: ~1 second per document (evaluation only)

Total for full pipeline: ~1-2 minutes per document

## System Requirements

- **Minimum**: 4GB RAM, 2GB disk space
- **Recommended**: 8GB RAM, 10GB disk space (for models and cache)
- **With LaMa**: 16GB RAM, 20GB disk space

## Development

### Setting up for development:

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Format code
black src/ pipeline/

# Lint code
flake8 src/ pipeline/

# Run tests with coverage
pytest --cov=src tests/
```

### Before committing:

1. Run tests: `pytest`
2. Format code: `black src/ pipeline/`
3. Lint code: `flake8 src/ pipeline/`
4. Check coverage: `pytest --cov=src tests/`

## Next Steps

1. Read `README.md` for project overview
2. Review `config/pipeline_config.yaml` for available parameters
3. Check `docs/metodologia_tecnica.md` for technical details
4. Review `docs/plan_desarrollo.md` for development roadmap

## Support

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## License

This project is licensed under the MIT License - see `LICENSE` file for details.
