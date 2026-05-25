# -*- coding: utf-8 -*-
"""
Public API for the stamp-removal + OCR pipeline.
Functions are importable from any environment (local, Colab, CI/CD).
"""
from .run_phase_3a import run_phase_3a
from .run_phase_4 import run_phase_4
from .consolidate_results import consolidate_ocr_results
from .run_evaluation import run_evaluation
from .run_full_pipeline import run_full_pipeline

__all__ = [
    "run_phase_3a",
    "run_phase_4",
    "consolidate_ocr_results",
    "run_evaluation",
    "run_full_pipeline",
]
