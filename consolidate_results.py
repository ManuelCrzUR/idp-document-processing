# -*- coding: utf-8 -*-
"""
Consolidate OCR results: Extract text to TXT and generate metrics JSON.
"""
import json
from pathlib import Path
from collections import Counter


def consolidate_ocr_results(ocr_json_path, output_dir):
    """
    Consolidate OCR results into TXT and metrics JSON.

    Args:
        ocr_json_path: Path to ocr_results.json from Phase 4
        output_dir: Output directory for consolidated results
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 100)
    print("CONSOLIDATING OCR RESULTS")
    print("=" * 100 + "\n")

    # Load OCR results
    print(f"[*] Loading OCR results: {ocr_json_path}")
    with open(ocr_json_path, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)

    # Extract text
    full_text = ocr_data.get('texto_completo', '')
    bloques = ocr_data.get('bloques', [])
    metricas = ocr_data.get('metricas', {})

    print(f"[OK] Loaded {len(bloques)} text blocks")

    # ========================================================================
    # 1. SAVE OCR TEXT TO TXT FILE
    # ========================================================================
    txt_output_path = output_dir / "ocr_extracted_text.txt"
    with open(txt_output_path, 'w', encoding='utf-8') as f:
        f.write("OCR EXTRACTED TEXT\n")
        f.write("=" * 100 + "\n\n")
        f.write(full_text)
        f.write("\n\n" + "=" * 100 + "\n")
        f.write(f"Total characters: {len(full_text):,}\n")
        f.write(f"Total words: {len(full_text.split()):,}\n")
        f.write(f"Total blocks: {len(bloques)}\n")

    print(f"[OK] OCR text saved to: {txt_output_path}")

    # ========================================================================
    # 2. CALCULATE METRICS
    # ========================================================================
    print("\n[CALCULATING METRICS]")
    print("-" * 100)

    # Basic metrics
    words = full_text.split()
    lines = full_text.split('\n')
    chars = len(full_text)
    total_words = len(words)

    # Confidence metrics
    confidences = [b.get('confianza', 0) for b in bloques if isinstance(b, dict)]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    min_confidence = min(confidences) if confidences else 0
    max_confidence = max(confidences) if confidences else 0

    # Text properties
    unique_words = len(set(word.lower() for word in words))
    avg_word_length = chars / total_words if total_words > 0 else 0

    # Orthographic metrics
    words_corrected = metricas.get('palabras_corregidas', 0)
    entities_detected = metricas.get('entidades_detectadas', 0)

    # Confidence distribution
    confidence_bins = {
        '0.0-0.2': len([c for c in confidences if 0 <= c < 0.2]),
        '0.2-0.4': len([c for c in confidences if 0.2 <= c < 0.4]),
        '0.4-0.6': len([c for c in confidences if 0.4 <= c < 0.6]),
        '0.6-0.8': len([c for c in confidences if 0.6 <= c < 0.8]),
        '0.8-1.0': len([c for c in confidences if 0.8 <= c <= 1.0]),
    }

    print(f"  Total characters:     {chars:,}")
    print(f"  Total words:          {total_words:,}")
    print(f"  Total lines:          {len(lines):,}")
    print(f"  Total blocks:         {len(bloques)}")
    print(f"  Unique words:         {unique_words:,}")
    print(f"  Average word length:  {avg_word_length:.2f}")
    print(f"  Average confidence:   {avg_confidence:.4f} ({avg_confidence*100:.2f}%)")
    print(f"  Min confidence:       {min_confidence:.4f} ({min_confidence*100:.2f}%)")
    print(f"  Max confidence:       {max_confidence:.4f} ({max_confidence*100:.2f}%)")
    print(f"  Words corrected:      {words_corrected}")
    print(f"  Entities detected:    {entities_detected}")

    # ========================================================================
    # 3. CREATE METRICS JSON
    # ========================================================================
    metrics_json = {
        'pipeline_phase': 'Phase 4 (OCR)',
        'timestamp': str(Path(ocr_json_path).stat().st_mtime),

        'text_metrics': {
            'total_characters': chars,
            'total_words': total_words,
            'total_lines': len(lines),
            'total_blocks': len(bloques),
            'unique_words': unique_words,
            'average_word_length': round(avg_word_length, 4),
            'character_per_block': round(chars / len(bloques), 2) if len(bloques) > 0 else 0,
        },

        'ocr_confidence_metrics': {
            'average': round(avg_confidence, 4),
            'average_percent': round(avg_confidence * 100, 2),
            'min': round(min_confidence, 4),
            'max': round(max_confidence, 4),
            'distribution': confidence_bins,
            'blocks_with_high_confidence': len([c for c in confidences if c >= 0.8]),
            'blocks_with_medium_confidence': len([c for c in confidences if 0.5 <= c < 0.8]),
            'blocks_with_low_confidence': len([c for c in confidences if c < 0.5]),
        },

        'post_processing_metrics': {
            'words_corrected': words_corrected,
            'entities_detected': entities_detected,
            'correction_rate': round(words_corrected / total_words * 100, 2) if total_words > 0 else 0,
            'entity_rate': round(entities_detected / len(bloques) * 100, 2) if len(bloques) > 0 else 0,
        },

        'engines_and_processors': {
            'ocr_engines': metricas.get('motores_usados', []),
            'processors': metricas.get('procesadores_usados', []),
        },

        'file_paths': {
            'ocr_results_json': str(ocr_json_path),
            'extracted_text_txt': str(txt_output_path),
            'metrics_json': str(output_dir / 'ocr_metrics.json'),
        }
    }

    # Save metrics JSON
    metrics_json_path = output_dir / "ocr_metrics.json"
    with open(metrics_json_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_json, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Metrics saved to: {metrics_json_path}")

    # ========================================================================
    # 4. DISPLAY TEXT SAMPLE
    # ========================================================================
    print("\n[TEXT SAMPLE]")
    print("-" * 100)
    sample = full_text[:500]
    print(f"{sample}...\n")

    # ========================================================================
    # 5. PRINT SUMMARY
    # ========================================================================
    print("=" * 100)
    print("CONSOLIDATION SUMMARY")
    print("=" * 100)
    print(f"\nGenerated files:")
    print(f"  1. {txt_output_path}")
    print(f"     Extracted OCR text in plain text format")
    print(f"\n  2. {metrics_json_path}")
    print(f"     Comprehensive metrics (characters, words, confidence, etc.)")
    print(f"\nKey Metrics:")
    print(f"  - Text: {chars:,} characters, {total_words:,} words, {len(bloques)} blocks")
    print(f"  - Confidence: {avg_confidence*100:.2f}% average")
    print(f"  - Corrections: {words_corrected} words corrected")
    print(f"  - Entities: {entities_detected} entities detected")

    print("\n" + "=" * 100 + "\n")

    return metrics_json


if __name__ == "__main__":
    # Paths
    ocr_json = "pipeline_results/phase_4/ocr_results.json"
    output_dir = "pipeline_results/consolidated"

    if not Path(ocr_json).exists():
        print(f"[ERROR] OCR results file not found: {ocr_json}")
        exit(1)

    metrics = consolidate_ocr_results(ocr_json, output_dir)
