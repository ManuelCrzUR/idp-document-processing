# Phase 3A: Stamp Removal Module
from .chromatic_separator import ChromaticSeparator
from .inpainter import LaMaInpainter, OpenCVInpainter, HybridInpainter

__all__ = [
    "ChromaticSeparator",
    "LaMaInpainter",
    "OpenCVInpainter",
    "HybridInpainter",
]
