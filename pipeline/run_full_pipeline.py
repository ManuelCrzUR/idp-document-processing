# -*- coding: utf-8 -*-
"""
Full Pipeline Runner: Orchestrates Phases 3A, 4, and 5
Complete stamp removal → OCR → evaluation workflow.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from run_phase_3a import run_phase_3a
from run_phase_4 import run_phase_4
from run_evaluation import run_evaluation


def run_full_pipeline(
    input_image: str,
    output_dir: str,
    ground_truth_dir: str = None,
    skip_phase_3a: bool = False,
    skip_phase_4: bool = False,
    skip_phase_5: bool = False,
    block_size: int = 20,
    inpainting_method: str = "hybrid",
    language: str = "es",
    confidence_threshold: float = 0.6,
) -> dict:
    """
    Run complete pipeline: Phase 3A → Phase 4 → Phase 5.

    Args:
        input_image: Path to input image
        output_dir: Base output directory
        ground_truth_dir: Optional ground truth directory for Phase 5
        skip_phase_3a: Skip Phase 3A (stamp removal)
        skip_phase_4: Skip Phase 4 (OCR)
        skip_phase_5: Skip Phase 5 (evaluation)
        block_size: Block size for Phase 3A
        inpainting_method: Inpainting method for Phase 3A
        language: OCR language for Phase 4
        confidence_threshold: Confidence threshold for Phase 4

    Returns:
        Dictionary with complete pipeline results
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pipeline_results = {
        'start_time': None,
        'phases': {},
        'success': True,
    }

    print("\n" + "=" * 80)
    print("RUNNING FULL OCR PIPELINE")
    print("=" * 80 + "\n")

    # Phase 3A: Stamp Removal
    if not skip_phase_3a:
        print("[PHASE 3A] Stamp Removal")
        print("-" * 80)

        phase_3a_output = output_dir / "phase_3a"
        try:
            result_3a = run_phase_3a(
                input_image_path=input_image,
                output_dir=str(phase_3a_output),
                block_size=block_size,
                inpainting_method=inpainting_method,
            )
            pipeline_results['phases']['phase_3a'] = result_3a

            if result_3a['success']:
                print("[OK] Phase 3A completed\n")
                phase_3a_image = result_3a['output_image']
            else:
                print(f"[ERROR] Phase 3A failed: {result_3a.get('error')}\n")
                pipeline_results['success'] = False
                return pipeline_results
        except Exception as e:
            print(f"[ERROR] Phase 3A exception: {e}\n")
            pipeline_results['phases']['phase_3a'] = {'success': False, 'error': str(e)}
            pipeline_results['success'] = False
            return pipeline_results
    else:
        print("[SKIPPED] Phase 3A\n")
        phase_3a_image = input_image

    # Phase 4: OCR and Post-Correction
    if not skip_phase_4:
        print("[PHASE 4] OCR and Post-Correction")
        print("-" * 80)

        phase_4_output = output_dir / "phase_4"
        try:
            result_4 = run_phase_4(
                input_image_path=phase_3a_image,
                output_dir=str(phase_4_output),
                language=language,
                confidence_threshold=confidence_threshold,
            )
            pipeline_results['phases']['phase_4'] = result_4

            if result_4['success']:
                print("[OK] Phase 4 completed\n")
                phase_4_ocr_json = result_4['output_json']
            else:
                print(f"[ERROR] Phase 4 failed: {result_4.get('error')}\n")
                pipeline_results['success'] = False
                if not skip_phase_5:
                    return pipeline_results
        except Exception as e:
            print(f"[ERROR] Phase 4 exception: {e}\n")
            pipeline_results['phases']['phase_4'] = {'success': False, 'error': str(e)}
            pipeline_results['success'] = False
            if not skip_phase_5:
                return pipeline_results
    else:
        print("[SKIPPED] Phase 4\n")

    # Phase 5: Evaluation
    if not skip_phase_5 and ground_truth_dir:
        print("[PHASE 5] CER/WER Evaluation")
        print("-" * 80)

        phase_5_output = output_dir / "phase_5"
        try:
            result_5 = run_evaluation(
                ocr_results_dir=str(Path(phase_4_ocr_json).parent),
                ground_truth_dir=str(ground_truth_dir),
                output_dir=str(phase_5_output),
            )
            pipeline_results['phases']['phase_5'] = result_5

            if result_5['success']:
                print("[OK] Phase 5 completed\n")
            else:
                print(f"[ERROR] Phase 5 failed: {result_5.get('error')}\n")
                pipeline_results['success'] = False
        except Exception as e:
            print(f"[ERROR] Phase 5 exception: {e}\n")
            pipeline_results['phases']['phase_5'] = {'success': False, 'error': str(e)}
            pipeline_results['success'] = False
    elif skip_phase_5 or not ground_truth_dir:
        print("[SKIPPED] Phase 5 (evaluation requires ground truth)\n")

    # Summary
    print("=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)

    for phase_name, phase_result in pipeline_results['phases'].items():
        status = "[OK]" if phase_result.get('success', False) else "[FAILED]"
        print(f"{phase_name}: {status}")

    if pipeline_results['success']:
        print("\n[OK] Pipeline completed successfully!")
    else:
        print("\n[ERROR] Pipeline had errors. Check output above.")

    print("=" * 80 + "\n")

    # Save pipeline summary
    summary_file = output_dir / "pipeline_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(pipeline_results, f, indent=2)
    print(f"[OK] Summary saved to: {summary_file}\n")

    return pipeline_results


def main():
    parser = argparse.ArgumentParser(
        description="Full OCR Pipeline: Phase 3A + Phase 4 + Phase 5"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input image path"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output base directory"
    )
    parser.add_argument(
        "--ground_truth",
        help="Optional ground truth directory for evaluation"
    )
    parser.add_argument(
        "--skip_phase_3a",
        action="store_true",
        help="Skip Phase 3A (stamp removal)"
    )
    parser.add_argument(
        "--skip_phase_4",
        action="store_true",
        help="Skip Phase 4 (OCR)"
    )
    parser.add_argument(
        "--skip_phase_5",
        action="store_true",
        help="Skip Phase 5 (evaluation)"
    )
    parser.add_argument(
        "--block_size",
        type=int,
        default=20,
        help="Block size for Phase 3A (default 20)"
    )
    parser.add_argument(
        "--inpainting_method",
        choices=["lama", "opencv", "hybrid"],
        default="hybrid",
        help="Inpainting method (default hybrid)"
    )
    parser.add_argument(
        "--language",
        default="es",
        help="OCR language (default 'es')"
    )
    parser.add_argument(
        "--confidence_threshold",
        type=float,
        default=0.6,
        help="OCR confidence threshold (default 0.6)"
    )

    args = parser.parse_args()

    result = run_full_pipeline(
        input_image=args.input,
        output_dir=args.output,
        ground_truth_dir=args.ground_truth,
        skip_phase_3a=args.skip_phase_3a,
        skip_phase_4=args.skip_phase_4,
        skip_phase_5=args.skip_phase_5,
        block_size=args.block_size,
        inpainting_method=args.inpainting_method,
        language=args.language,
        confidence_threshold=args.confidence_threshold,
    )

    if result['success']:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
