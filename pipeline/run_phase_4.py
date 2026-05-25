# -*- coding: utf-8 -*-
"""
Phase 4 Runner: OCR and Post-Correction
Extracts text, corrects spelling, validates entities.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
from src.phase_4 import EasyOCREngine, SpellCorrector, EntityValidator


def run_phase_4(
    input_image_path: str,
    output_dir: str,
    language: str = "es",
    confidence_threshold: float = 0.6,
    levenshtein_threshold: int = 2,
    seal_bbox: tuple = None,
) -> dict:
    """
    Run Phase 4: OCR and post-correction.

    Args:
        input_image_path: Path to input image
        output_dir: Output directory for results
        language: OCR language code (default "es" for Spanish)
        confidence_threshold: Minimum confidence for OCR results
        levenshtein_threshold: Levenshtein distance threshold for spell correction
        seal_bbox: Optional seal bbox (xc, yc, w, h) normalized

    Returns:
        Dictionary with processing results
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load input image
    print(f"[*] Loading image: {input_image_path}")
    image = cv2.imread(input_image_path)
    if image is None:
        print(f"[ERROR] Could not load image: {input_image_path}")
        return {"success": False, "error": "Could not load image"}

    print(f"[*] Image size: {image.shape[1]}x{image.shape[0]}")

    # Initialize OCR engine (with complete functionality)
    print(f"[*] Initializing OCR engine (language={language})...")
    ocr_engine = EasyOCREngine(
        language=language,
        confidence_threshold=confidence_threshold,
        max_levenshtein=levenshtein_threshold,
    )

    # Extract and correct text
    print(f"[*] Extracting text with OCR (with spell correction & NER)...")
    result = ocr_engine.extract_text(image, seal_bbox=seal_bbox)

    print(f"[*] Extracted {result['metricas']['total_bloques']} text blocks")
    print(f"[*] Average confidence: {result['metricas']['confianza_promedio']:.2%}")
    print(f"[*] Words corrected: {result['metricas']['palabras_corregidas']}")
    print(f"[*] Entities detected: {result['metricas']['entidades_detectadas']}")

    # Save results
    json_path = output_dir / "ocr_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved OCR results: {json_path}")

    # Print summary
    print("\n" + "=" * 80)
    print("OCR EXTRACTION SUMMARY")
    print("=" * 80)
    metricas = result['metricas']
    print(f"Total text blocks: {metricas['total_bloques']}")
    print(f"Average confidence: {metricas['confianza_promedio']:.4f}")
    print(f"Words corrected: {metricas['palabras_corregidas']}")
    print(f"Entities detected: {metricas['entidades_detectadas']}")
    print(f"Total text length: {len(result['texto_completo']):,} characters")
    print(f"Engines used: {', '.join(metricas['motores_usados'])}")
    print(f"Processors: {', '.join(metricas['procesadores_usados'])}")
    print("=" * 80 + "\n")

    # Show extracted text (first 500 chars)
    print("EXTRACTED TEXT (first 500 characters):")
    print("-" * 80)
    texto = result['texto_completo']
    print(texto[:500] + "..." if len(texto) > 500 else texto)
    print("-" * 80 + "\n")

    return {
        "success": True,
        "output_json": str(json_path),
        "text_blocks": metricas['total_bloques'],
        "confidence": metricas['confianza_promedio'],
        "words_corrected": metricas['palabras_corregidas'],
        "entities": metricas['entidades_detectadas'],
        "text_length": len(result['texto_completo']),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Phase 4: OCR and Post-Correction"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input image path"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory"
    )
    parser.add_argument(
        "--language",
        default="es",
        help="OCR language code (default 'es')"
    )
    parser.add_argument(
        "--confidence_threshold",
        type=float,
        default=0.6,
        help="Minimum confidence threshold (default 0.6)"
    )
    parser.add_argument(
        "--levenshtein_threshold",
        type=int,
        default=2,
        help="Levenshtein distance threshold for correction (default 2)"
    )

    args = parser.parse_args()

    result = run_phase_4(
        input_image_path=args.input,
        output_dir=args.output,
        language=args.language,
        confidence_threshold=args.confidence_threshold,
        levenshtein_threshold=args.levenshtein_threshold,
    )

    if result["success"]:
        print("[OK] Phase 4 completed successfully")
        return 0
    else:
        print(f"[ERROR] {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
