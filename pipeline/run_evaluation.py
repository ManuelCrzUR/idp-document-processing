# -*- coding: utf-8 -*-
"""
Phase 5 Runner: CER/WER Evaluation
Measures OCR quality using Character and Word Error Rates.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.phase_5 import CERWEREvaluator


def run_evaluation(
    ocr_results_dir: str,
    ground_truth_dir: str,
    output_dir: str,
    doc_mapping_file: str = None,
) -> dict:
    """
    Run Phase 5: Evaluation metrics.

    Args:
        ocr_results_dir: Directory with OCR JSON files
        ground_truth_dir: Directory with ground truth text files
        output_dir: Output directory for results
        doc_mapping_file: Optional JSON file with document mapping

    Returns:
        Dictionary with evaluation results
    """
    ocr_results_dir = Path(ocr_results_dir)
    ground_truth_dir = Path(ground_truth_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] OCR Results Dir: {ocr_results_dir}")
    print(f"[*] Ground Truth Dir: {ground_truth_dir}")
    print(f"[*] Output Dir: {output_dir}")

    # Load document mapping
    if doc_mapping_file and Path(doc_mapping_file).exists():
        with open(doc_mapping_file, 'r') as f:
            doc_mapping = json.load(f)
        print(f"[*] Loaded document mapping from: {doc_mapping_file}")
    else:
        # Auto-discover mapping
        doc_mapping = {}
        ocr_files = list(ocr_results_dir.glob("*_ocr*.json"))
        print(f"[*] Auto-discovering document mapping ({len(ocr_files)} files found)...")

    if not doc_mapping:
        print("[ERROR] No document mapping found")
        return {"success": False, "error": "No documents to evaluate"}

    # Run evaluation
    print(f"[*] Evaluating {len(doc_mapping)} documents...")
    evaluator = CERWEREvaluator(hypothesis_threshold=5.0)

    results = evaluator.evaluate_batch(
        ocr_results_dir=ocr_results_dir,
        ground_truth_dir=ground_truth_dir,
        doc_mapping=doc_mapping,
    )

    if not results:
        print("[ERROR] No successful evaluations")
        return {"success": False, "error": "No successful evaluations"}

    print(f"[OK] Evaluated {len(results)} documents")

    # Save results
    evaluator.save_results(output_dir)

    # Print summary
    evaluator.print_summary()

    # Calculate statistics
    cer_values = [r['cer'] for r in results]
    wer_values = [r['wer'] for r in results]

    stats = {
        'documents_evaluated': len(results),
        'cer_average': float(sum(cer_values) / len(cer_values)),
        'cer_min': float(min(cer_values)),
        'cer_max': float(max(cer_values)),
        'wer_average': float(sum(wer_values) / len(wer_values)),
        'wer_min': float(min(wer_values)),
        'wer_max': float(max(wer_values)),
    }

    print("STATISTICS")
    print("-" * 80)
    print(f"CER Average: {stats['cer_average']:.2f}%")
    print(f"CER Range: {stats['cer_min']:.2f}% - {stats['cer_max']:.2f}%")
    print(f"WER Average: {stats['wer_average']:.2f}%")
    print(f"WER Range: {stats['wer_min']:.2f}% - {stats['wer_max']:.2f}%")
    print("-" * 80 + "\n")

    return {
        "success": True,
        "documents_evaluated": len(results),
        "statistics": stats,
        "results_json": str(output_dir / "evaluation_results.json"),
        "results_csv": str(output_dir / "evaluation_results.csv"),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Phase 5: CER/WER Evaluation"
    )
    parser.add_argument(
        "--ocr_results",
        required=True,
        help="Directory with OCR JSON results"
    )
    parser.add_argument(
        "--ground_truth",
        required=True,
        help="Directory with ground truth text files"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory"
    )
    parser.add_argument(
        "--mapping",
        help="Optional JSON file with document mapping"
    )

    args = parser.parse_args()

    result = run_evaluation(
        ocr_results_dir=args.ocr_results,
        ground_truth_dir=args.ground_truth,
        output_dir=args.output,
        doc_mapping_file=args.mapping,
    )

    if result["success"]:
        print("[OK] Phase 5 completed successfully")
        return 0
    else:
        print(f"[ERROR] {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
