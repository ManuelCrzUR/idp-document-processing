# -*- coding: utf-8 -*-
"""
Execute full OCR pipeline: Phase 3A → Phase 4 → Phase 5
Processes a document image, extracts OCR, and evaluates with ground truth.

Usage:
    python execute_full_pipeline.py --input path/to/image.png
    python execute_full_pipeline.py --input path/to/image.png --ground_truth path/to/gt_dir
    GT_DIR=path/to/gt python execute_full_pipeline.py --input path/to/image.png
"""
import sys
import os
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.run_full_pipeline import run_full_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Full OCR Pipeline: Phase 3A + Phase 4 + Phase 5"
    )
    parser.add_argument(
        "--input",
        default="output/prueba_completa/01_imagen_original.png",
        help="Input image path (default: output/prueba_completa/01_imagen_original.png)",
    )
    parser.add_argument(
        "--output",
        default="pipeline_results",
        help="Output base directory (default: pipeline_results)",
    )
    parser.add_argument(
        "--ground_truth",
        default=None,
        help="Ground truth directory for Phase 5 evaluation (optional). "
             "Also reads from GT_DIR environment variable.",
    )
    args = parser.parse_args()

    # Resolve ground truth: CLI arg takes priority, then env var, then None
    ground_truth_dir = args.ground_truth or os.environ.get("GT_DIR") or None
    input_image = args.input
    output_base_dir = args.output

    # Validate ground truth path
    if ground_truth_dir and not Path(ground_truth_dir).exists():
        print(f"[WARN] Ground truth dir not found: {ground_truth_dir} — skipping Phase 5")
        ground_truth_dir = None

    print("\n" + "=" * 100)
    print("FULL OCR PIPELINE EXECUTION")
    print("=" * 100)
    print(f"\nConfiguration:")
    print(f"  Input image:      {input_image}")
    print(f"  Output directory: {output_base_dir}")
    print(f"  Ground truth:     {ground_truth_dir or 'NOT PROVIDED (Phase 5 skipped)'}")
    print("\n" + "=" * 100 + "\n")

    # Verify input
    if not Path(input_image).exists():
        print(f"[ERROR] Input image not found: {input_image}")
        return 1

    # Execute full pipeline
    results = run_full_pipeline(
        input_image=input_image,
        output_dir=output_base_dir,
        ground_truth_dir=ground_truth_dir,
        skip_phase_3a=False,
        skip_phase_4=False,
        skip_phase_5=(ground_truth_dir is None),
        block_size=20,
        inpainting_method="hybrid",
        language="es",
        confidence_threshold=0.6,
    )

    # Display results
    print("\n" + "=" * 100)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 100)

    if results['success']:
        print("\n[OK] Pipeline completed successfully\n")

        # Save full results to JSON
        results_json_path = Path(output_base_dir) / "pipeline_results_final.json"
        with open(results_json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"[OK] Full results saved to: {results_json_path}\n")

        # Display phase results
        for phase_name, phase_result in results.get('phases', {}).items():
            print(f"\n{phase_name.upper()}:")
            print("-" * 100)
            if isinstance(phase_result, dict):
                for key, value in phase_result.items():
                    if key != 'bloques' and key != 'palabras':  # Skip large arrays
                        print(f"  {key}: {value}")

        print("\n" + "=" * 100)
        return 0
    else:
        print("\n[ERROR] Pipeline failed\n")
        error_msg = results.get('phases', {}).get('error', 'Unknown error')
        print(f"Error: {error_msg}\n")
        print("=" * 100)
        return 1


if __name__ == "__main__":
    sys.exit(main())
