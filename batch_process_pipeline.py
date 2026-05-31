#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch Pipeline Processor: Process 200+ synthetic images in parallel
with incremental saving, memory management, and detailed metrics.

Usage:
    python batch_process_pipeline.py

Configuration:
    - IMAGES_DIR: Source directory (201 synthetic images)
    - OUTPUT_ROOT: Results directory
    - NUM_WORKERS: Parallel processes (adjust for RAM: 3-5 recommended)
    - BATCH_SIZE: Images processed before cleanup (5-10 recommended)
"""

import os
import sys
import json
import time
import gc
import psutil
import traceback
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import multiprocessing as mp
from functools import partial
from tqdm import tqdm
import cv2
import numpy as np

# Add repo to path
REPO_ROOT = Path(__file__).parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline import run_phase_3a, run_phase_4, consolidate_ocr_results

# ============================================================================
# CONFIGURATION
# ============================================================================

IMAGES_DIR = Path(r"C:\Users\manue\Documents\Desktop_Archive_2026-03-14\Folders\PR_COMPUTER_VISION\idp-project\datos\synthetic_dataset\images")
OUTPUT_ROOT = Path(REPO_ROOT) / "batch_results" / datetime.now().strftime("%Y%m%d_%H%M%S")
NUM_WORKERS = 4  # Parallel processes (adjust 3-5 based on RAM)
BATCH_SIZE = 5   # Images per cleanup cycle

# Create output directories
(OUTPUT_ROOT / "phase_3a").mkdir(parents=True, exist_ok=True)
(OUTPUT_ROOT / "phase_4").mkdir(parents=True, exist_ok=True)
(OUTPUT_ROOT / "consolidated").mkdir(parents=True, exist_ok=True)
(OUTPUT_ROOT / "logs").mkdir(parents=True, exist_ok=True)

# ============================================================================
# WORKER FUNCTION (runs in separate process)
# ============================================================================

def process_single_image(image_path, output_root, image_index, total_images):
    """
    Process a single image through the full pipeline.
    Returns dict with results and timing info.
    """
    result = {
        "image_name": image_path.name,
        "image_index": image_index,
        "success": False,
        "phases_completed": [],
        "timing": {},
        "errors": [],
    }

    try:
        # Get file size
        image_size_mb = image_path.stat().st_size / (1024 * 1024)

        start_total = time.time()
        start_mem = psutil.Process().memory_info().rss / (1024 * 1024)

        # ====== PHASE 3A: Stamp Removal ======
        try:
            phase_3a_output = str(output_root / "phase_3a" / image_path.stem)
            Path(phase_3a_output).mkdir(parents=True, exist_ok=True)

            start = time.time()
            result_3a = run_phase_3a(
                input_image_path=str(image_path),
                output_dir=phase_3a_output,
                block_size=20,
                inpainting_method="hybrid",
                save_intermediate=False,  # Don't save intermediate to save space
            )
            result["timing"]["phase_3a"] = time.time() - start

            if result_3a["success"]:
                result["phases_completed"].append("3a")
                cleaned_image = result_3a["output_image"]
            else:
                result["errors"].append(f"Phase 3A failed: {result_3a.get('error', 'Unknown')}")
                cleaned_image = str(image_path)  # Fallback to original

        except Exception as e:
            result["errors"].append(f"Phase 3A exception: {str(e)}")
            cleaned_image = str(image_path)
            result["timing"]["phase_3a"] = time.time() - start

        # ====== PHASE 4: OCR Extraction ======
        try:
            phase_4_output = str(output_root / "phase_4" / image_path.stem)
            Path(phase_4_output).mkdir(parents=True, exist_ok=True)

            start = time.time()
            result_4 = run_phase_4(
                input_image_path=cleaned_image,
                output_dir=phase_4_output,
                language="es",
                confidence_threshold=0.6,
                levenshtein_threshold=2,
            )
            result["timing"]["phase_4"] = time.time() - start

            if result_4["success"]:
                result["phases_completed"].append("4")
                ocr_json = result_4["output_json"]
                result["ocr_blocks"] = result_4.get("text_blocks", 0)
                result["ocr_confidence"] = result_4.get("confidence", 0)
                result["ocr_text_length"] = result_4.get("text_length", 0)
            else:
                result["errors"].append(f"Phase 4 failed: {result_4.get('error', 'Unknown')}")
                ocr_json = None

        except Exception as e:
            result["errors"].append(f"Phase 4 exception: {str(e)}")
            ocr_json = None
            result["timing"]["phase_4"] = time.time() - start

        # ====== Consolidate Results ======
        try:
            if ocr_json and Path(ocr_json).exists():
                consolidated_output = str(output_root / "consolidated" / image_path.stem)
                Path(consolidated_output).mkdir(parents=True, exist_ok=True)

                start = time.time()
                metrics = consolidate_ocr_results(
                    ocr_json_path=ocr_json,
                    output_dir=consolidated_output,
                )
                result["timing"]["consolidate"] = time.time() - start
                result["phases_completed"].append("consolidate")

                # Store key metrics
                tm = metrics.get("text_metrics", {})
                cm = metrics.get("ocr_confidence_metrics", {})
                pm = metrics.get("post_processing_metrics", {})

                result["metrics"] = {
                    "total_characters": tm.get("total_characters", 0),
                    "total_words": tm.get("total_words", 0),
                    "total_blocks": tm.get("total_blocks", 0),
                    "avg_confidence": cm.get("average_percent", 0),
                    "words_corrected": pm.get("words_corrected", 0),
                    "entities_detected": pm.get("entities_detected", 0),
                }
        except Exception as e:
            result["errors"].append(f"Consolidation exception: {str(e)}")
            result["timing"]["consolidate"] = time.time() - start

        # ====== Finalize ======
        end_mem = psutil.Process().memory_info().rss / (1024 * 1024)
        result["timing"]["total"] = time.time() - start_total
        result["timing"]["image_size_mb"] = image_size_mb
        result["memory_delta_mb"] = end_mem - start_mem
        result["success"] = len(result["errors"]) == 0

    except Exception as e:
        result["errors"].append(f"Overall exception: {str(e)}\n{traceback.format_exc()}")

    return result


# ============================================================================
# MAIN BATCH PROCESSOR
# ============================================================================

def main():
    """Main batch processing pipeline."""

    print("="*80)
    print("BATCH PIPELINE PROCESSOR - 200+ Synthetic Images")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Images directory: {IMAGES_DIR}")
    print(f"  Output directory: {OUTPUT_ROOT}")
    print(f"  Parallel workers: {NUM_WORKERS}")
    print(f"  Batch size (cleanup cycle): {BATCH_SIZE}")

    # ====== DISCOVER IMAGES ======
    image_files = sorted([
        f for f in IMAGES_DIR.glob("*")
        if f.suffix.lower() in [".png", ".jpg", ".jpeg"]
    ])

    print(f"\nFound {len(image_files)} images")
    if len(image_files) == 0:
        print("[ERROR] No images found!")
        return

    # ====== METRICS ======
    metrics_summary = {
        "start_time": datetime.now().isoformat(),
        "total_images": len(image_files),
        "images_processed": 0,
        "images_failed": 0,
        "phases_timing": defaultdict(float),
        "image_timings": [],
        "errors_log": [],
    }

    # ====== PROCESS IN BATCHES WITH PARALLELIZATION ======
    print(f"\n{'='*80}")
    print("Starting batch processing...")
    print(f"{'='*80}\n")

    process_func = partial(process_single_image, output_root=OUTPUT_ROOT)

    with mp.Pool(processes=NUM_WORKERS) as pool:
        # Process images with progress bar
        batch_idx = 0
        for batch_start in range(0, len(image_files), BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, len(image_files))
            batch_images = image_files[batch_start:batch_end]
            batch_idx += 1

            print(f"\n[BATCH {batch_idx}] Processing images {batch_start+1}-{batch_end}/{len(image_files)}")

            # Process batch in parallel
            batch_results = list(tqdm(
                pool.starmap(
                    process_func,
                    [(img, idx+1, len(image_files)) for idx, img in enumerate(batch_images, start=batch_start)]
                ),
                total=len(batch_images),
                desc="  Progress",
                unit="img"
            ))

            # ====== SAVE BATCH RESULTS INCREMENTALLY ======
            for result in batch_results:
                # Save individual image result
                result_file = OUTPUT_ROOT / "logs" / f"{Path(result['image_name']).stem}_result.json"
                with open(result_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)

                # Update metrics
                if result["success"]:
                    metrics_summary["images_processed"] += 1
                    metrics_summary["image_timings"].append({
                        "image": result["image_name"],
                        "total_seconds": result["timing"]["total"],
                        "size_mb": result["timing"]["image_size_mb"],
                        "throughput_mb_per_sec": result["timing"]["image_size_mb"] / max(result["timing"]["total"], 0.1),
                    })
                    # Accumulate phase timings
                    for phase, timing in result["timing"].items():
                        if phase != "image_size_mb":
                            metrics_summary["phases_timing"][phase] += timing
                else:
                    metrics_summary["images_failed"] += 1
                    metrics_summary["errors_log"].append({
                        "image": result["image_name"],
                        "errors": result["errors"],
                    })

                # Print result summary
                status = "[OK]" if result["success"] else "[FAIL]"
                timing = result["timing"]["total"]
                print(f"  {status} {result['image_name']:50} {timing:6.2f}s", end="")
                if result.get("metrics"):
                    m = result["metrics"]
                    print(f" | Conf: {m['avg_confidence']:.1f}% | Blocks: {m['total_blocks']}", end="")
                print()

            # ====== CLEANUP AFTER BATCH ======
            gc.collect()
            mem = psutil.virtual_memory()
            print(f"  [Memory] After batch: {mem.percent:.1f}% used ({mem.available/(1024**3):.1f}GB available)")

    # ====== FINAL METRICS ======
    metrics_summary["end_time"] = datetime.now().isoformat()

    total_time = sum(t["total_seconds"] for t in metrics_summary["image_timings"])
    avg_time_per_image = total_time / max(metrics_summary["images_processed"], 1)

    metrics_summary["summary"] = {
        "total_time_seconds": total_time,
        "avg_time_per_image_seconds": avg_time_per_image,
        "throughput_images_per_minute": 60 / max(avg_time_per_image, 0.1),
        "success_rate_percent": 100 * metrics_summary["images_processed"] / max(metrics_summary["total_images"], 1),
        "avg_phase_timing": {
            phase: timing / max(metrics_summary["images_processed"], 1)
            for phase, timing in metrics_summary["phases_timing"].items()
        }
    }

    # ====== SAVE SUMMARY ======
    summary_file = OUTPUT_ROOT / "summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        # Convert defaultdict to regular dict for JSON serialization
        data = {k: v for k, v in metrics_summary.items()}
        data["phases_timing"] = dict(data["phases_timing"])
        json.dump(data, f, indent=2)

    # ====== PRINT FINAL REPORT ======
    print(f"\n{'='*80}")
    print("BATCH PROCESSING COMPLETE")
    print(f"{'='*80}\n")

    print(f"[RESULTS]")
    print(f"  Total images: {metrics_summary['total_images']}")
    print(f"  Processed: {metrics_summary['images_processed']}")
    print(f"  Failed: {metrics_summary['images_failed']}")
    print(f"  Success rate: {metrics_summary['summary']['success_rate_percent']:.1f}%")

    print(f"\n[TIMING]")
    print(f"  Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"  Avg per image: {avg_time_per_image:.2f}s")
    print(f"  Throughput: {metrics_summary['summary']['throughput_images_per_minute']:.1f} images/min")

    print(f"\n[PHASE TIMINGS (average)]")
    for phase, timing in metrics_summary["summary"]["avg_phase_timing"].items():
        print(f"  {phase:20} {timing:6.2f}s")

    print(f"\n[OUTPUT DIRECTORY]")
    print(f"  {OUTPUT_ROOT}")
    print(f"\n[FILES GENERATED]")
    print(f"  - phase_3a/          (cleaned images)")
    print(f"  - phase_4/           (OCR JSON per image)")
    print(f"  - consolidated/      (extracted text + metrics per image)")
    print(f"  - logs/              (individual result JSON + errors)")
    print(f"  - summary.json       (batch statistics and timing)")

    print(f"\n[SUMMARY FILE]")
    print(f"  {summary_file}")

    # ====== ERROR REPORT ======
    if metrics_summary["errors_log"]:
        print(f"\n[ERRORS]")
        print(f"  Failed images: {len(metrics_summary['errors_log'])}")
        errors_file = OUTPUT_ROOT / "ERRORS.txt"
        with open(errors_file, "w", encoding="utf-8") as f:
            for err in metrics_summary["errors_log"]:
                f.write(f"\n{err['image']}\n")
                for e in err["errors"]:
                    f.write(f"  - {e}\n")
        print(f"  Error log: {errors_file}")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
