# Phase 4: OCR and Post-Correction Module
from .ocr_engine import EasyOCREngine

# Legacy imports (for compatibility)
try:
    from .spell_corrector import SpellCorrector
    from .entity_validator import EntityValidator
except ImportError:
    # These are now integrated into EasyOCREngine
    pass

__all__ = [
    "EasyOCREngine",
]
